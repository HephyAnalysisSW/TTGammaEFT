#!/usr/bin/env python

# standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import sys
import os
import subprocess
import shutil
import uuid

from math                                        import sqrt, cos, sin, atan2, cosh
from operator                                    import mul

# RootTools
from RootTools.core.standard                     import *

# DeepCheck RootFiles
from Analysis.Tools.helpers                      import checkRootFile, deepCheckRootFile, deepCheckWeight

# Tools for systematics
from Analysis.Tools.helpers                      import checkRootFile, bestDRMatchInCollection, deltaR, deltaPhi, mT
from TTGammaEFT.Tools.user                       import cache_directory

from TTGammaEFT.Tools.objectSelection            import *
from TTGammaEFT.Tools.Variables                  import NanoVariables

from TTGammaEFT.Tools.overlapRemovalTTG          import *
from TTGammaEFT.Tools.puProfileCache             import puProfile

# environment
hostname   = os.getenv("HOSTNAME").lower()

# central configuration
targetLumi = 1000 #pb-1 Which lumi to normalize to

logChoices      = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET', 'SYNC']

def get_parser():
    ''' Argument parser for post-processing module.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser for nanoPostProcessing")

    argParser.add_argument('--logLevel',                    action='store',         nargs='?',              choices=logChoices,     default='INFO',                     help="Log level for logging")
    argParser.add_argument('--overwrite',                   action='store_true',                                                                                        help="Overwrite existing output files, bool flag set to True  if used")
    argParser.add_argument('--samples',                     action='store',         nargs='*',  type=str,                           default=['WZTo3LNu'],               help="List of samples to be post-processed, given as CMG component name")
    argParser.add_argument('--eventsPerJob',                action='store',         nargs='?',  type=int,                           default=300000000,                  help="Maximum number of events per job (Approximate!).") # mul by 100
    argParser.add_argument('--nJobs',                       action='store',         nargs='?',  type=int,                           default=1,                          help="Maximum number of simultaneous jobs.")
    argParser.add_argument('--job',                         action='store',                     type=int,                           default=0,                          help="Run only job i")
    argParser.add_argument('--minNJobs',                    action='store',         nargs='?',  type=int,                           default=1,                          help="Minimum number of simultaneous jobs.")
    argParser.add_argument('--fileBasedSplitting',          action='store_true',                                                                                        help="Split njobs according to files")
    argParser.add_argument('--processingEra',               action='store',         nargs='?',  type=str,                           default='TTGammaEFT_PP_v1',         help="Name of the processing era")
    argParser.add_argument('--small',                       action='store_true',                                                                                        help="Run the file on a small sample (for test purpose), bool flag set to True if used")
    argParser.add_argument('--year',                        action='store',                     type=int,   choices=[2016,2017,2018],  required = True,                    help="Which year?")
    argParser.add_argument('--interpolationOrder',          action='store',         nargs='?',  type=int,                           default=2,                          help="Interpolation order for EFT weights.")
    argParser.add_argument('--checkOnly',                   action='store_true',                                                                                        help="Check files at target and remove corrupt ones without reprocessing? Not possible with overwrite!")
    argParser.add_argument('--flagTTGamma',                 action='store_true',                                                                                        help="Check overlap removal for ttgamma")
    argParser.add_argument('--flagTTBar',                   action='store_true',                                                                                        help="Check overlap removal for ttbar")
    argParser.add_argument('--flagZWGamma',                 action='store_true',                                                                                        help="Check overlap removal for Zgamma/Wgamma")
    argParser.add_argument('--flagDYWJets',                 action='store_true',                                                                                        help="Check overlap removal for DY/WJets")
    argParser.add_argument('--flagTGamma',                  action='store_true',                                                                                        help="Check overlap removal for TGamma")
    argParser.add_argument('--flagSingleTopTch',            action='store_true',                                                                                        help="Check overlap removal for singleTop t-channel")
    argParser.add_argument('--flagGJets',                   action='store_true',                                                                                        help="Check overlap removal for GJets")
    argParser.add_argument('--flagQCD',                     action='store_true',                                                                                        help="Check overlap removal for QCD")
    argParser.add_argument('--reduceSizeBy',                action='store',                     type=int,                           default=1,                          help="Reduce the size of the sample by a factor of...")
    return argParser

options = get_parser().parse_args()

stitching = False
# combine ttg samples is they are nominal
if "TTG" in options.samples[0] and not "Tune" in options.samples[0] and not "erd" in options.samples[0] and not "QCDbased" in options.samples[0] and not "GluonMove" in options.samples[0] and not "ptG" in options.samples[0]:
    stitching = True

print stitching
# B-Tagger
tagger = 'DeepCSV'
#tagger = 'CSVv2'

if len( filter( lambda x: x, [options.flagTTGamma, options.flagTTBar, options.flagZWGamma, options.flagDYWJets, options.flagTGamma, options.flagSingleTopTch, options.flagGJets, options.flagQCD] ) ) > 1:
    raise Exception("Overlap removal flag can only be True for ONE flag!" )

# Logging
import Analysis.Tools.logger as logger
logdir  = "/tmp/lukas.lechner/%s/"%str(uuid.uuid4())
logFile = '%s/%s_%s_njob%s.txt'%(logdir, '_'.join(options.samples), os.environ['USER'], str(0 if options.nJobs==1 else options.job) )
if not os.path.exists( logdir ):
    try: os.makedirs( logdir )
    except: pass
logger  = logger.get_logger(options.logLevel, logFile = logFile)


import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(options.logLevel, logFile = None )

import Samples.Tools.logger as logger_samples
logger_samples = logger_samples.get_logger(options.logLevel, logFile = None )

# Flags 
diMuCond               = "(Sum$(Muon_pt>=20&&abs(Muon_eta)<=2.40&&Muon_tightId)>=1)&&(Sum$(Muon_pt>=10&&abs(Muon_eta)<=2.40&&Muon_tightId)>=2)"
if options.year == 2016:
    diMuGammaCond          = "(Sum$(Photon_pt>=10&&abs(Photon_eta)<=2.5&&Photon_cutBased>=2)>=1)"
else:
    diMuGammaCond          = "(Sum$(Photon_pt>=10&&abs(Photon_eta)<=2.5&&Photon_cutBasedBitmap>=2)>=1)"

# additional conditions for testing
addCond                = "(1)"

skimConds = [diMuCond, diMuGammaCond, addCond]

#Samples: Load samples
maxNFiles = None
if options.small:
    maxNFiles = 1
    maxNEvents = 10000
    options.job = 0
    options.nJobs = 1 # set high to just run over 1 input file

if options.year == 2016:
    from TTGammaEFT.Samples.Summer16_nanoAODv6      import *
    from Samples.nanoAOD.Run2016_nanoAODv6          import *
elif options.year == 2017:
    from TTGammaEFT.Samples.Fall17_nanoAODv6        import *
    from Samples.nanoAOD.Run2017_nanoAODv6          import *
elif options.year == 2018:
    from TTGammaEFT.Samples.Autumn18_nanoAODv6      import *
    from Samples.nanoAOD.Run2018_nanoAODv6          import *

# Load all samples to be post processed
samples = map( eval, options.samples ) 

if len(samples)==0:
    logger.info( "No samples found. Was looking for %s. Exiting" % options.samples )
    sys.exit(0)

isData = False not in [s.isData for s in samples]
isMC   = True  not in [s.isData for s in samples]

# Check that all samples which are concatenated have the same x-section.
assert isData or len(set([s.xSection for s in samples]))==1, "Not all samples have the same xSection: %s !"%( ", ".join( [s.name for s in samples] ) )
assert isMC   or len(samples)==1,                            "Don't concatenate data samples"

# Trigger selection
if options.year == 2016:
    triggers = ["HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ", "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ"]
elif options.year == 2017:
    triggers = ["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL", "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ","HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8","HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8"]
elif options.year == 2018:
    triggers = ["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8", "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8", "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL", "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ"]
skimConds.append( "("+"||".join(triggers)+")" )

#Samples: combine if more than one
if len(samples)>1:
    sample_name =  samples[0].name+"_comb"
    logger.info( "Combining samples %s to %s.", ",".join(s.name for s in samples), sample_name )
    sample      = Sample.combine(sample_name, samples, maxN=maxNFiles)
    sampleForPU = Sample.combine(sample_name, samples, maxN=-1)
elif len(samples)==1:
    sample      = samples[0]
    sampleForPU = samples[0]

    if options.small:
        sample.files = sample.files[:maxNFiles]

if options.reduceSizeBy > 1:
    if isData:
        raise NotImplementedError( "Data samples shouldn't be reduced in size!!" )
    logger.info("Sample size will be reduced by a factor of %s", options.reduceSizeBy)
    logger.info("Recalculating the normalization of the sample. Before: %s", sample.normalization)
    sample.reduceFiles( factor = options.reduceSizeBy )
    # recompute the normalization
    sample.clear()
    sample.name += "_redBy%s"%options.reduceSizeBy
    sample.normalization = sample.getYieldFromDraw(weightString="genWeight")['val']
    sample.isData = isData
    logger.info("New normalization: %s", sample.normalization)

postfix       = '_small' if options.small else ''
sampleDir     = sample.name #sample name changes after split

# User specific
from TTGammaEFT.Tools.user import postprocessing_output_directory as user_directory
directory        = os.path.join( user_directory, options.processingEra ) 
output_directory = os.path.join( '/tmp/%s'%os.environ['USER'], str(uuid.uuid4()) )
targetPath       = os.path.join( directory, "diMuGamma"+postfix, sampleDir )
if not os.path.exists( targetPath ):
    try:    os.makedirs( targetPath )
    except: pass
nExistingFiles    = len(os.listdir(targetPath))
if nExistingFiles > options.nJobs:
    raise Exception("Error: More files exist in target directory as should be processed! Check your nJobs input! Got nJobs %i, existing files: %i"%(options.nJobs, nExistingFiles))
logger.info("%i files exist in target directory! Processing %i files."%(nExistingFiles, options.nJobs))

# Single file post processing
if options.fileBasedSplitting or options.nJobs > 1:
    len_orig = len(sample.files)
    sample = sample.split( n=options.nJobs, nSub=options.job)
    if sample is None:  
        logger.info( "No such sample. nJobs %i, job %i numer of files %i", options.nJobs, options.job, len_orig )
        sys.exit(0)
    logger.info(  "fileBasedSplitting: Run over %i/%i files for job %i/%i."%(len(sample.files), len_orig, options.job, options.nJobs))
    logger.debug( "fileBasedSplitting: Files to be run over:\n%s", "\n".join(sample.files) )

# Directories
outputFilePath    = os.path.join( output_directory, sample.name + '.root' )
targetFilePath    = os.path.join( targetPath, sample.name + '.root' )
filename, ext = os.path.splitext( outputFilePath )

if os.path.exists( output_directory ) and options.overwrite:
    if options.nJobs > 1:
        logger.warning( "NOT removing directory %s because nJobs = %i", output_directory, options.nJobs )
    else:
        logger.info( "Output directory %s exists. Deleting.", outputFilePath )
        shutil.rmtree( outputFilePath, ignore_errors=True )

if not os.path.exists( output_directory ):
    try:
        os.makedirs( output_directory )
        logger.info( "Created output directory %s.", output_directory )
    except:
        logger.info( "Directory %s already exists.", output_directory )
        pass

# checking overwrite or file exists
sel = "&&".join(skimConds)
nEvents = sample.getYieldFromDraw(weightString="1", selectionString=sel)['val']
if not options.overwrite:
    if os.path.isfile(targetFilePath):
        logger.info( "Output file %s found.", targetFilePath)
        if checkRootFile( targetFilePath, checkForObjects=["Events"] ) and deepCheckRootFile( targetFilePath ) and deepCheckWeight( targetFilePath ):
            logger.info( "File already processed. Source: File check ok!" ) # Everything is fine, no overwriting
            logger.info( "Checking the normalization of the sample." )
            existingSample = Sample.fromFiles( "existing", targetFilePath, treeName = "Events" )
            nEventsExist = existingSample.getYieldFromDraw(weightString="1")['val']
            if nEvents == nEventsExist:
                logger.info( "File already processed. Normalization file check ok! Skipping." ) # Everything is fine, no overwriting
                sys.exit(0)
            else:
                logger.info( "Target events not equal to processing sample events! Is: %s, should be: %s!"%(nEventsExist, nEvents) )
                logger.info( "Removing file from target." )
                os.remove( targetFilePath )
                logger.info( "Reprocessing." )
        else:
            logger.info( "File corrupt. Removing file from target." )
            os.remove( targetFilePath )
            logger.info( "Reprocessing." )
    else:
        logger.info( "Sample not processed yet." )
        logger.info( "Processing." )

else:
    logger.info( "Overwriting.")

if options.checkOnly: sys.exit(0)

# Cross section for postprocessed sample
xSection = samples[0].xSection if isMC else None

if isMC:
        from Analysis.Tools.puReweighting import getReweightingFunction
        puProfiles          = puProfile( source_sample=sampleForPU, year=options.year )
        mcHist              = puProfiles.cachedTemplate( selection="( 1 )", weight='genWeight', overwrite=False ) # use genWeight for amc@NLO samples. No problems encountered so far
        if options.year == 2016:
            nTrueInt_puRW       = getReweightingFunction(data="PU_2016_35920_XSecCentral",  mc=mcHist)
            nTrueInt_puRWDown   = getReweightingFunction(data="PU_2016_35920_XSecDown",     mc=mcHist)
            nTrueInt_puRWUp     = getReweightingFunction(data="PU_2016_35920_XSecUp",       mc=mcHist)
        elif options.year == 2017:
            nTrueInt_puRW       = getReweightingFunction(data="PU_2017_41530_XSecCentral",  mc=mcHist)
            nTrueInt_puRWDown   = getReweightingFunction(data="PU_2017_41530_XSecDown",     mc=mcHist)
            nTrueInt_puRWUp     = getReweightingFunction(data="PU_2017_41530_XSecUp",       mc=mcHist)
        elif options.year == 2018:
            nTrueInt_puRW       = getReweightingFunction(data="PU_2018_59740_XSecCentral",  mc=mcHist)
            nTrueInt_puRWDown   = getReweightingFunction(data="PU_2018_59740_XSecDown",     mc=mcHist)
            nTrueInt_puRWUp     = getReweightingFunction(data="PU_2018_59740_XSecUp",       mc=mcHist)

#branches to be kept for data and MC
branchKeepStrings_DATAMC = [\
    "run", "luminosityBlock", "event",
    "PV_*",
    "nJet", "Jet_*",
    "nMuon", "Muon_*",
    "nPhoton", "Photon_*",
    "fixed*",
    "MET_*",
    "Flag_*", "HLT_*", "L1_*",
]

#branches to be kept for MC samples only
branchKeepStrings_MC = [\
    "Generator_*",
    "genWeight",
    "Pileup_nTrueInt",
    "GenPart_*", "nGenPart",
    "GenJet_*", "nGenJet",
    "Pileup_*",
]

#branches to be kept for data only
branchKeepStrings_DATA = []

if sample.isData:
    lumiScaleFactor   = None
    branchKeepStrings = branchKeepStrings_DATAMC + branchKeepStrings_DATA
    json = allSamples[0].json
    from FWCore.PythonUtilities.LumiList import LumiList
    lumiList = LumiList( os.path.expandvars( json ) )
    logger.info( "Loaded json %s", json )
    lumi = 1
else:
    lumiScaleFactor = xSection * targetLumi / float( sample.normalization ) if xSection is not None else None
    branchKeepStrings = branchKeepStrings_DATAMC + branchKeepStrings_MC
    if   options.year == 2016: lumi = 35.92
    elif options.year == 2017: lumi = 41.53
    elif options.year == 2018: lumi = 59.74

# get nano variable lists
NanoVars = NanoVariables( options.year )
#VarString ... "var1/type,var2/type"
#Variables ... ["var1/type","var2/type"]
#VarList   ... ["var1", "var2"]

readGenVarString      = NanoVars.getVariableString(   "Gen",      postprocessed=False, data=sample.isData )
readGenJetVarString   = NanoVars.getVariableString(   "GenJet",   postprocessed=False, data=sample.isData )
readJetVarString      = NanoVars.getVariableString(   "Jet",      postprocessed=False, data=sample.isData, skipSyst=True )
readElectronVarString = NanoVars.getVariableString(   "Electron", postprocessed=False, data=sample.isData )
readMuonVarString     = NanoVars.getVariableString(   "Muon",     postprocessed=False, data=sample.isData )
readPhotonVarString   = NanoVars.getVariableString(   "Photon",   postprocessed=False, data=sample.isData )

readGenVarList        = NanoVars.getVariableNameList( "Gen",      postprocessed=False, data=sample.isData )
readGenJetVarList     = NanoVars.getVariableNameList( "GenJet",   postprocessed=False, data=sample.isData )
readJetVarList        = NanoVars.getVariableNameList( "Jet",      postprocessed=False, data=sample.isData, skipSyst=True  )
readElectronVarList   = NanoVars.getVariableNameList( "Electron", postprocessed=False, data=sample.isData )
readMuonVarList       = NanoVars.getVariableNameList( "Muon",     postprocessed=False, data=sample.isData )
readPhotonVarList     = NanoVars.getVariableNameList( "Photon",   postprocessed=False, data=sample.isData )

readMuonVariables   = NanoVars.getVariables(        "Muon",   postprocessed=False, data=sample.isData )

writeGenVarString     = NanoVars.getVariableString(   "Gen",      postprocessed=True,  data=sample.isData )
writeGenJetVarString  = NanoVars.getVariableString(   "GenJet",   postprocessed=True,  data=sample.isData )
writeJetVarString     = NanoVars.getVariableString(   "Jet",      postprocessed=True,  data=sample.isData, skipSyst=True  )
writeMuonVarString  = NanoVars.getVariableString(   "Muon",   postprocessed=True,  data=sample.isData, skipSyst=True  )
writePhotonVarString  = NanoVars.getVariableString(   "Photon",   postprocessed=True,  data=sample.isData, skipSyst=True  )

writeJetVarList       = NanoVars.getVariableNameList( "Jet",      postprocessed=True,  data=sample.isData, skipSyst=True  )
writeBJetVarList      = NanoVars.getVariableNameList( "BJet",     postprocessed=True,  data=sample.isData, skipSyst=True  )
writeGenVarList       = NanoVars.getVariableNameList( "Gen",      postprocessed=True,  data=sample.isData )
writeGenJetVarList    = NanoVars.getVariableNameList( "GenJet",   postprocessed=True,  data=sample.isData )
writeMuonVarList    = NanoVars.getVariableNameList( "Muon",   postprocessed=True,  data=sample.isData, skipSyst=True  )
writePhotonVarList    = NanoVars.getVariableNameList( "Photon",   postprocessed=True,  data=sample.isData, skipSyst=True  )

writeGenVariables     = NanoVars.getVariables( "Gen",      postprocessed=True,  data=sample.isData )
writeGenJetVariables  = NanoVars.getVariables( "GenJet",   postprocessed=True,  data=sample.isData )
writeJetVariables     = NanoVars.getVariables( "Jet",      postprocessed=True,  data=sample.isData, skipSyst=True  )
writeBJetVariables    = NanoVars.getVariables( "BJet",     postprocessed=True,  data=sample.isData, skipSyst=True  )
writeMuonVariables  = NanoVars.getVariables( "Muon",   postprocessed=True,  data=sample.isData, skipSyst=True  )
writePhotonVariables  = NanoVars.getVariables( "Photon",   postprocessed=True,  data=sample.isData, skipSyst=True  )

# Read Variables
read_variables  = map( TreeVariable.fromString, ['run/I', 'luminosityBlock/I', 'event/l'] )

read_variables.extend( map( TreeVariable.fromString, ["MET_pt/F", "MET_phi/F"] ) )

read_variables += [ TreeVariable.fromString('nElectron/I'),
                    VectorTreeVariable.fromString('Electron[%s]'%readElectronVarString) ]
read_variables += [ TreeVariable.fromString('nMuon/I'),
                    VectorTreeVariable.fromString('Muon[%s]'%readMuonVarString) ]
read_variables += [ TreeVariable.fromString('nPhoton/I'),
                    VectorTreeVariable.fromString('Photon[%s]'%readPhotonVarString) ]
read_variables += [ TreeVariable.fromString('nJet/I'),
                    VectorTreeVariable.fromString('Jet[%s]'%readJetVarString) ]
if isMC:
    read_variables += [ TreeVariable.fromString('genWeight/F') ]
    read_variables += [ TreeVariable.fromString('Pileup_nTrueInt/F') ]
    read_variables += [ TreeVariable.fromString('nGenPart/I'),
                        VectorTreeVariable.fromString('GenPart[%s]'%readGenVarString, nMax = 1000) ] # all needed for genMatching
    read_variables += [ TreeVariable.fromString('nLHEPart/I'),
                        VectorTreeVariable.fromString('LHEPart[%s]'%'phi/F,pt/F,pdgId/I,eta/F', nMax = 1000) ]
    read_variables += [ TreeVariable.fromString('nGenJet/I'),
                        VectorTreeVariable.fromString('GenJet[%s]'%readGenJetVarString) ]

# Write Variables
new_variables  = []
new_variables += [ 'weight/F', 'year/I', 'lumi/F' ]

# Jets
new_variables += [ 'nJetGood/I' ] 
new_variables += [ 'JetGood0_'  + var for var in writeJetVariables ]
new_variables += [ 'JetGood1_'  + var for var in writeJetVariables ]

# BJets
new_variables += [ 'nBTag/I']
new_variables += [ 'nBTagGood/I']
new_variables += [ 'Bj0_' + var for var in writeBJetVariables ]
new_variables += [ 'Bj1_' + var for var in writeBJetVariables ]

# Leptons
new_variables += [ 'nMuonTight/I']
new_variables += [ 'nLeadMuonTight/I']
new_variables += [ 'MuonTight0_'       + var for var in writeMuonVariables ]
new_variables += [ 'MuonTight1_'       + var for var in writeMuonVariables ]

# Photons
new_variables += [ 'nPhotonLoose/I' ] 
new_variables += [ 'PhotonLoose0_'            + var for var in writePhotonVariables ]
new_variables += [ 'nPhotonMedium/I' ] 
new_variables += [ 'PhotonMedium0_'            + var for var in writePhotonVariables ]
new_variables += [ 'nPhotonTight/I' ] 
new_variables += [ 'PhotonTight0_'            + var for var in writePhotonVariables ]
new_variables += [ 'nPhotonMVA/I' ] 
new_variables += [ 'PhotonMVA0_'            + var for var in writePhotonVariables ]

# Others
new_variables += [ 'ht/F' ]
new_variables += [ 'minLepJetdR/F' ]
new_variables += [ 'minGLJetdR/F', 'minGLLepdR/F']
new_variables += [ 'minGMJetdR/F', 'minGMLepdR/F']
new_variables += [ 'minGTJetdR/F', 'minGTLepdR/F']
new_variables += [ 'minGMVAJetdR/F', 'minGMVALepdR/F']
new_variables += [ 'l0gLDR/F', 'l1gLDR/F']
new_variables += [ 'l0gMDR/F', 'l1gMDR/F']
new_variables += [ 'l0gTDR/F', 'l1gTDR/F']
new_variables += [ 'l0gMVADR/F', 'l1gMVADR/F']

new_variables += [ 'mll/F',  'mllgL/F',  'mllgM/F',  'mllgT/F',  'mllgMVA/F' ] 
new_variables += [ 'lldR/F', 'lldPhi/F' ] 

new_variables += [ 'isTTGamma/I', 'isZWGamma/I', 'isTGamma/I', 'isGJets/I', 'overlapRemoval/I' ]
new_variables += [ 'reweightPU/F', 'reweightPUDown/F', 'reweightPUUp/F' ]

new_variables += ['jsonPassed/I']

# Overlap removal Selection
genPhotonSel_TTG_OR = genPhotonSelector( 'overlapTTGamma' )
genPhotonSel_ZG_OR  = genPhotonSelector( 'overlapZGamma' )
genPhotonSel_T_OR   = genPhotonSelector( 'overlapSingleTopTch' )
genPhotonSel_GJ_OR  = genPhotonSelector( 'overlapGJets' )
# Gen Selection
genLeptonSel = genLeptonSelector()
genPhotonSel = genPhotonSelector()
genJetSel    = genJetSelector()
# Jet Selection
recoJetSel              = jetSelector( options.year ) #pt_nom?

# Define a reader
reader = sample.treeReader( variables=read_variables, selectionString="&&".join(skimConds) )

# Replace unsign. char type with integer (only necessary for output electrons)
def convertUnits( coll ):
    for p in coll:
        if abs(p['pdgId'])==11 and isinstance( p['lostHits'], basestring ): p['lostHits']    = ord( p['lostHits'] )
        if abs(p['pdgId'])==13 and isinstance( p['pfIsoId'], basestring ):  p['pfIsoId']     = ord( p['pfIsoId'] )
        if isMC and isinstance( p['genPartFlav'], basestring ):             p['genPartFlav'] = ord( p['genPartFlav'] )

def get4DVec( part ):
  vec = ROOT.TLorentzVector()
  vec.SetPtEtaPhiM( part['pt'], part['eta'], part['phi'], 0 )
  return vec

def get2DVec( part ):
  vec = ROOT.TVector2( part["pt"]*cos(part["phi"]), part["pt"]*sin(part["phi"]) )
  return vec

def interpret_weight(weight_id):
    str_s = weight_id.split('_')
    res={}
    for i in range(len(str_s)/2):
        res[str_s[2*i]] = float(str_s[2*i+1].replace('m','-').replace('p','.'))
    return res

def fill_vector_collection( event, collection_name, collection_varnames, objects):
    setattr( event, "n"+collection_name, len(objects) )
    for i_obj, obj in enumerate(objects):
        for var in collection_varnames:
            getattr(event, collection_name+"_"+var)[i_obj] = obj[var]

def fill_vector( event, collection_name, collection_varnames, obj):
    if not obj: return #fills default values in variable
    for var in collection_varnames:
        setattr(event, collection_name+"_"+var, obj[var] )


def filler( event ):
    # shortcut
    r = reader.event

    event.isData = isData
    event.year   = options.year
    event.lumi   = lumi

    if isMC:

        # weight
        event.weight = lumiScaleFactor*r.genWeight if lumiScaleFactor is not None else 0
        #print event.weight, lumiScaleFactor*r.genWeight, sample.xSection, sample.normalization

        # PU reweighting
        event.reweightPU      = nTrueInt_puRW     ( r.Pileup_nTrueInt )
        event.reweightPUDown  = nTrueInt_puRWDown ( r.Pileup_nTrueInt )
        event.reweightPUUp    = nTrueInt_puRWUp   ( r.Pileup_nTrueInt )

        # GEN Particles
        gPart = getParticles( r, collVars=readGenVarList,    coll="GenPart" )
        gJets = getParticles( r, collVars=readGenJetVarList, coll="GenJet" )

        gPart.sort( key = lambda p: -p['pt'] )
        gJets.sort( key = lambda p: -p['pt'] )

        # Overlap removal flags for ttgamma/ttbar and Zgamma/DY
        GenPhoton                  = filterGenPhotons( gPart, status='all' )

        # OR ttgamma/tt
        GenIsoPhotonTTG            = filter( lambda g: isIsolatedPhoton( g, gPart, coneSize=0.1,  ptCut=5, excludedPdgIds=[12,-12,14,-14,16,-16] ), GenPhoton    )
        GenIsoPhotonNoMesonTTG     = filter( lambda g: not hasMesonMother( getParentIds( g, gPart ) ), GenIsoPhotonTTG )

        # OR DY/ZG, WG/WJets
        GenIsoPhoton               = filter( lambda g: isIsolatedPhoton( g, gPart, coneSize=0.05,  ptCut=5, excludedPdgIds=[12,-12,14,-14,16,-16] ), GenPhoton    )
        GenIsoPhotonNoMeson        = filter( lambda g: not hasMesonMother( getParentIds( g, gPart ) ), GenIsoPhoton )

        # OR singleT/tG
        GenIsoPhotonNoMesonTG      = filter( lambda g: not photonFromTopDecay( getParentIds( g, gPart ) ), GenIsoPhotonNoMeson )

        # OR GJets/QCD
        GenIsoPhotonGJets          = filter( lambda g: isIsolatedPhoton( g, gPart, coneSize=0.4,  ptCut=5, excludedPdgIds=[12,-12,14,-14,16,-16] ), GenPhoton    )
        GenIsoPhotonNoMesonGJets   = filter( lambda g: not hasMesonMother( getParentIds( g, gPart ) ), GenIsoPhotonGJets )

        event.isTTGamma = len( filter( lambda g: genPhotonSel_TTG_OR(g), GenIsoPhotonNoMesonTTG     ) ) > 0
        event.isZWGamma = len( filter( lambda g: genPhotonSel_ZG_OR(g),  GenIsoPhotonNoMeson        ) ) > 0
        event.isTGamma  = len( filter( lambda g: genPhotonSel_T_OR(g),   GenIsoPhotonNoMesonTG      ) ) > 0
        event.isGJets   = len( filter( lambda g: genPhotonSel_GJ_OR(g),  GenIsoPhotonNoMesonGJets   ) ) > 0

        # new OR flag: Apply overlap removal directly in pp to better handle the plots
        if options.flagTTGamma:
            event.overlapRemoval = event.isTTGamma     #good TTgamma event
        elif options.flagTTBar:
            event.overlapRemoval = not event.isTTGamma #good TTbar event
        elif options.flagZWGamma:
            event.overlapRemoval = event.isZWGamma     #good Zgamma, Wgamma event
        elif options.flagDYWJets:
            event.overlapRemoval = not event.isZWGamma #good DY, WJets event
        elif options.flagTGamma:
            event.overlapRemoval = event.isTGamma      #good TGamma event
        elif options.flagSingleTopTch:
            event.overlapRemoval = not event.isTGamma  #good singleTop t-channel event
        elif options.flagGJets:
            event.overlapRemoval = event.isGJets       #good gamma+jets event
        elif options.flagQCD:
            event.overlapRemoval = not event.isGJets   #good QCD event
        else:
            event.overlapRemoval = 1 # all other events

        event.jsonPassed  = 1

    elif isData:
        event.isTTGamma = 1
        event.isZWGamma = 1
        event.isTGamma  = 1
        event.isGJets   = 1
        event.overlapRemoval = 1 # all other events
        event.weight     = 1.
        event.reweightPU = 1
        # lumi lists and vetos
        event.jsonPassed  = lumiList.contains( r.run, r.luminosityBlock )
        # make data weight zero if JSON was not passed
        if not event.jsonPassed: event.weight = 0
        # store decision to use after filler has been executed
        event.jsonPassed_ = event.jsonPassed
    else:
        raise NotImplementedError( "isMC %r isData %r " % (isMC, isData) )

    # Photons
    allPhotons = getParticles( r, readPhotonVarList, coll="Photon" )
    allPhotons.sort( key = lambda g: -g['pt'] )
    convertUnits( allPhotons )

    for g in allPhotons:
        g['photonCat']      = -1
        g['photonCatMagic'] = -1
        g['leptonMother']   = -1
        g['mother']         = -1

    # Photons
    loosePhotons = list( filter( lambda g: g["pt"]>=10 and abs(g["eta"])<=2.5 and g["cutBased" if options.year == 2016 else "cutBasedBitmap"]>=1, allPhotons ) )
    event.nPhotonLoose            = len( loosePhotons )

    mediumPhotons = list( filter( lambda g: g["pt"]>=10 and abs(g["eta"])<=2.5 and g["cutBased" if options.year == 2016 else "cutBasedBitmap"]>=2, allPhotons ) )
    event.nPhotonMedium            = len( mediumPhotons )

    tightPhotons = list( filter( lambda g: g["pt"]>=10 and abs(g["eta"])<=2.5 and g["cutBased" if options.year == 2016 else "cutBasedBitmap"]>=3, allPhotons ) )
    event.nPhotonTight            = len( tightPhotons )

    MVAPhotons = list( filter( lambda g: g["pt"]>=10 and abs(g["eta"])<=2.5 and g["mvaID_WP80"], allPhotons ) )
    event.nPhotonMVA            = len( MVAPhotons )

    # Store analysis photons + default photons for a faster plot script
    p0, p1 = ( loosePhotons + [None,None] )[:2]
    fill_vector( event, "PhotonLoose0",  writePhotonVarList, p0 )

    p0, p1 = ( mediumPhotons + [None,None] )[:2]
    fill_vector( event, "PhotonMedium0",  writePhotonVarList, p0 )

    p0, p1 = ( tightPhotons + [None,None] )[:2]
    fill_vector( event, "PhotonTight0",  writePhotonVarList, p0 )

    p0, p1 = ( MVAPhotons + [None,None] )[:2]
    fill_vector( event, "PhotonMVA0",  writePhotonVarList, p0 )

    # Leptons
    allMuons = getParticles( r, readMuonVarList, coll="Muon" )
    allMuons.sort( key = lambda l: -l['pt'] )
    convertUnits( allMuons )

    tightMuons = list( filter( lambda l: l["pt"]>=10 and abs(l["eta"])<=2.4 and l["tightId"], allMuons ) )
    leadtightMuons = list( filter( lambda l: l["pt"]>=20, tightMuons ) )

    event.nMuonTight     = len(tightMuons)
    event.nLeadMuonTight = len(leadtightMuons)

    # Store analysis Muons + 2 default Muons for a faster plotscript
    lt0, lt1       = ( tightMuons       + [None,None] )[:2]
    # Semi-leptonic analysis
    fill_vector( event, "MuonTight0", writeMuonVarList, lt0 )
    fill_vector( event, "MuonTight1", writeMuonVarList, lt1 )

    # Jets
    allJets  = getParticles( r, collVars=readJetVarList, coll="Jet" )

    for j in allJets:
        j["isBJet"] = isBJet( j, tagger=tagger, year=options.year )
        j["isGood"] = 0 #not used
        j["clean"] = 0 #not used

    # Loose jets w/o pt/eta requirement
    goodJets = list( filter( lambda j: recoJetSel(j), allJets ) )
    goodJets = deltaRCleaning( goodJets, tightMuons, dRCut=0.4 )
    goodJets = deltaRCleaning( goodJets, mediumPhotons, dRCut=0.4 )

    event.nJetGood                = len(goodJets)

    # Store analysis jets + 2 default jets for a faster plotscript
    j0, j1       = ( goodJets + [None,None] )[:2]
    fill_vector( event, "JetGood0",  writeJetVarList, j0 )
    fill_vector( event, "JetGood1",  writeJetVarList, j1 )

    # bJets
    bJets    = list( filter( lambda x: x["isBJet"], goodJets ) )

    event.nBTagGood = len( bJets )

    # Store bJets + 2 default bjets for a faster plot script
    bj0, bj1 = ( list(bJets) + [None,None] )[:2]
    fill_vector( event, "Bj0", writeBJetVarList, bj0 )
    fill_vector( event, "Bj1", writeBJetVarList, bj1 )

    event.ht = sum( [ j['pt'] for j in goodJets ] )

    # variables w/ photons
    if len(loosePhotons) > 0:
        if goodJets:
            event.minGLJetdR = min( deltaR( loosePhotons[0], j ) for j in goodJets )
        if tightMuons:
            event.minGLLepdR = min( deltaR( loosePhotons[0], l ) for l in tightMuons )
        if len(tightMuons)>0:
            event.l0gLDR = deltaR( loosePhotons[0], tightMuons[0] )
        if len(tightMuons)>1:
            event.l1gLDR = deltaR( loosePhotons[0], tightMuons[1] )
            event.mllgL = ( get4DVec(tightMuons[0]) + get4DVec(tightMuons[1]) + get4DVec(loosePhotons[0]) ).M()

    if len(mediumPhotons) > 0:
        if goodJets:
            event.minGMJetdR = min( deltaR( mediumPhotons[0], j ) for j in goodJets )
        if tightMuons:
            event.minGMLepdR = min( deltaR( mediumPhotons[0], l ) for l in tightMuons )
        if len(tightMuons)>0:
            event.l0gMDR = deltaR( mediumPhotons[0], tightMuons[0] )
        if len(tightMuons)>1:
            event.l1gMDR = deltaR( mediumPhotons[0], tightMuons[1] )
            event.mllgM = ( get4DVec(tightMuons[0]) + get4DVec(tightMuons[1]) + get4DVec(mediumPhotons[0]) ).M()

    if len(tightPhotons) > 0:
        if goodJets:
            event.minGTJetdR = min( deltaR( tightPhotons[0], j ) for j in goodJets )
        if tightMuons:
            event.minGTLepdR = min( deltaR( tightPhotons[0], l ) for l in tightMuons )
        if len(tightMuons)>0:
            event.l0gTDR = deltaR( tightPhotons[0], tightMuons[0] )
        if len(tightMuons)>1:
            event.l1gTDR = deltaR( tightPhotons[0], tightMuons[1] )
            event.mllgT = ( get4DVec(tightMuons[0]) + get4DVec(tightMuons[1]) + get4DVec(tightPhotons[0]) ).M()

    if len(MVAPhotons) > 0:
        if goodJets:
            event.minGMVAJetdR = min( deltaR( MVAPhotons[0], j ) for j in goodJets )
        if tightMuons:
            event.minGMVALepdR = min( deltaR( MVAPhotons[0], l ) for l in tightMuons )
        if len(tightMuons)>0:
            event.l0gMVADR = deltaR( MVAPhotons[0], tightMuons[0] )
        if len(tightMuons)>1:
            event.l1gMVADR = deltaR( MVAPhotons[0], tightMuons[1] )
            event.mllgMVA = ( get4DVec(tightMuons[0]) + get4DVec(tightMuons[1]) + get4DVec(MVAPhotons[0]) ).M()


    if len(tightMuons) > 1:
        event.lldR   = deltaR( tightMuons[0], tightMuons[1] )
        event.lldPhi = deltaPhi( tightMuons[0]['phi'], tightMuons[1]['phi'] )
        event.mll    = ( get4DVec(tightMuons[0]) + get4DVec(tightMuons[1]) ).M()

    if len(goodJets) > 0 and len(tightMuons) > 0:
        event.leptonJetdR = min( deltaR( l, j ) for j in goodJets for l in tightMuons )


# Create a maker. Maker class will be compiled. This instance will be used as a parent in the loop
treeMaker_parent = TreeMaker(
    sequence  = [ filler ],
    variables = [ TreeVariable.fromString(x) for x in new_variables ],
    treeName = "Events"
    )

# Split input in ranges
if options.nJobs>1 and not options.fileBasedSplitting:
    eventRanges = reader.getEventRanges( nJobs = options.nJobs )
else:
    eventRanges = reader.getEventRanges( maxNEvents = options.eventsPerJob, minJobs = options.minNJobs )

logger.info( "Splitting into %i ranges of %i events on average. FileBasedSplitting: %s. Job number %s",  
        len(eventRanges), 
        (eventRanges[-1][1] - eventRanges[0][0])/len(eventRanges), 
        'Yes' if options.fileBasedSplitting else 'No',
        options.job)
#Define all jobs
jobs = [ (i, range) for i, range in enumerate( eventRanges ) ]

#assert False, ""

if options.fileBasedSplitting and len(eventRanges)>1:
    raise RuntimeError("Using fileBasedSplitting but have more than one event range!")

clonedEvents = 0
convertedEvents = 0
outputLumiList = {}

# there are a lot of eventRanges, however only one of those is processed
for ievtRange, eventRange in enumerate( eventRanges ):

    if not options.fileBasedSplitting and options.nJobs>1:
        if ievtRange != options.job: continue

    logger.info( "Processing range %i/%i from %i to %i which are %i events.",  ievtRange, len(eventRanges), eventRange[0], eventRange[1], eventRange[1]-eventRange[0] )

    tmp_directory = ROOT.gDirectory
    outputfile = ROOT.TFile.Open(outputFilePath, 'recreate')
    tmp_directory.cd()

    if options.small: 
        logger.info("Running 'small'. Not more than %i events"%maxNEvents) 
        numEvents  = eventRange[1] - eventRange[0]
        eventRange = ( eventRange[0], eventRange[0] +  min( [ numEvents, maxNEvents ] ) )

    # Set the reader to the event range
    reader.setEventRange( eventRange )

    # Clone the empty maker in order to avoid recompilation at every loop iteration
    clonedTree    = reader.cloneTree( branchKeepStrings, newTreename = "Events", rootfile = outputfile )
    clonedEvents += clonedTree.GetEntries()
    maker = treeMaker_parent.cloneWithoutCompile( externalTree=clonedTree )

    maker.start()
    # Do the thing
    reader.start()

    while reader.run():
        maker.run()
        if isData and maker.event.jsonPassed_:
            if reader.event.run not in outputLumiList.keys():
                outputLumiList[reader.event.run] = set( [ reader.event.luminosityBlock ] )
            else:
                if reader.event.luminosityBlock not in outputLumiList[reader.event.run]:
                    outputLumiList[reader.event.run].add(reader.event.luminosityBlock)

    convertedEvents += maker.tree.GetEntries()
    maker.tree.Write()
    outputfile.Close()
    logger.info( "Written %s", outputFilePath)

    # Destroy the TTree
    maker.clear()
    
logger.info( "Converted %i events of %i, cloned %i",  convertedEvents, reader.nEvents , clonedEvents )

# Storing JSON file of processed events
if isData:
    jsonFile = filename + '_%s.json' %( 0 if options.nJobs==1 else options.job )
    LumiList( runsAndLumis = outputLumiList ).writeJSON( jsonFile )
    logger.info( "Written JSON file %s",  jsonFile )

logger.info( "Copying log file to %s", output_directory )
copyLog = subprocess.call( [ 'rsync', logFile, output_directory ] )
if copyLog:
    logger.info( "Copying log from %s to %s failed", logFile, output_directory )
else:
    logger.info( "Successfully copied log file" )
    os.remove( logFile )
    logger.info( "Removed temporary log file" )

for dirname, subdirs, files in os.walk( output_directory ):
    logger.debug( 'Found directory: %s',  dirname )

    for fname in files:
        if not fname.endswith(".root") or fname.startswith("nanoAOD_") or "_for_" in fname: continue # remove that for copying log files

        source  = os.path.abspath( os.path.join( dirname, fname ) )
        target  = os.path.join( targetPath, fname )

        if checkRootFile( source, checkForObjects=["Events"] ) and deepCheckRootFile( source ) and deepCheckWeight( source ):
            logger.info( "Source: File check ok!" )
        else:
            raise Exception("Corrupt rootfile at source! File not copied: %s"%source )

        cmd = [ 'rsync', source, target ]
        logger.info( "Issue copy command: %s", " ".join( cmd ) )
        subprocess.call( cmd )

        if checkRootFile( target, checkForObjects=["Events"] ) and deepCheckRootFile( target ) and deepCheckWeight( target ):
            logger.info( "Target: File check ok!" )
        else:
            logger.info( "Corrupt rootfile at target! Trying again: %s"%target )
            logger.info( "2nd try: Issue copy command: %s", " ".join( cmd ) )
            subprocess.call( cmd )

            # Many files are corrupt after copying, a 2nd try fixes that
            if checkRootFile( target, checkForObjects=["Events"] ) and deepCheckRootFile( target ) and deepCheckWeight( target ):
                logger.info( "2nd try successfull!" )
            else:
                # if not successful, the corrupt root file needs to be deleted from DPM
                cmd = [ 'rm', target ]
                logger.info( "2nd try: No success, removing file: %s"%target )
                logger.info( "Issue rm command: %s", " ".join( cmd ) )
#                    subprocess.call( cmd )
                raise Exception("Corrupt rootfile at target! File not copied: %s"%source )

existingSample = Sample.fromFiles( "existing", targetFilePath, treeName = "Events" )
nEventsExist = existingSample.getYieldFromDraw(weightString="1")['val']
if nEvents == nEventsExist:
    logger.info( "All events processed!")
elif not options.small:
    logger.info( "Error: Target events not equal to processing sample events! Is: %s, should be: %s!"%(nEventsExist, nEvents) )
    logger.info( "Removing file from target." )
    os.remove( targetFilePath )
    logger.info( "Sorry." )

# There is a double free corruption due to stupid ROOT memory management which leads to a non-zero exit code
# Thus the job is resubmitted on condor even if the output is ok
# Current idea is that the problem is with xrootd having a non-closed root file
# Let's see if this works...
sample.clear()
shutil.rmtree( output_directory, ignore_errors=True )
