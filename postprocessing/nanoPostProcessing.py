#!/usr/bin/env python

# standard imports
import ROOT
import sys
import os
import subprocess
import shutil
import uuid

from math                                        import sqrt, cos, sin, atan2
from operator                                    import mul

# RootTools
from RootTools.core.standard                     import *

# DeepCheck RootFiles
from Analysis.Tools.helpers                      import checkRootFile, deepCheckRootFile, deepCheckWeight

# Tools for systematics
from Analysis.Tools.helpers                      import checkRootFile, bestDRMatchInCollection, deltaR, deltaPhi, mT, lp
from Analysis.Tools.MetSignificance              import MetSignificance
from TTGammaEFT.Tools.helpers                    import m3
from TTGammaEFT.Tools.user                       import cache_directory

from TTGammaEFT.Tools.objectSelection            import *
from TTGammaEFT.Tools.Variables                  import NanoVariables

from Analysis.Tools.overlapRemovalTTG            import photonFromTopDecay, hasMesonMother, getParentIds, isIsolatedPhoton, getPhotonCategory, hasLeptonMother, getPhotonMother, getAdvancedPhotonCategory
from Analysis.Tools.puProfileCache               import puProfile
from Analysis.Tools.L1PrefireWeight              import L1PrefireWeight
from Analysis.Tools.mt2Calculator                import mt2Calculator

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
    argParser.add_argument('--writeToDPM',                  action='store_true',                                                                                        help="Write output to DPM?")
    argParser.add_argument('--runOnLxPlus',                 action='store_true',                                                                                        help="Change the global redirector of samples to run on lxplus")
    argParser.add_argument('--fileBasedSplitting',          action='store_true',                                                                                        help="Split njobs according to files")
    argParser.add_argument('--processingEra',               action='store',         nargs='?',  type=str,                           default='TTGammaEFT_PP_v1',         help="Name of the processing era")
    argParser.add_argument('--skim',                        action='store',         nargs='?',  type=str,                           default='dilep',                    help="Skim conditions to be applied for post-processing")
    argParser.add_argument('--small',                       action='store_true',                                                                                        help="Run the file on a small sample (for test purpose), bool flag set to True if used")
    argParser.add_argument('--year',                        action='store',                     type=int,   choices=[2016,2017,2018],  required = True,                    help="Which year?")
    argParser.add_argument('--interpolationOrder',          action='store',         nargs='?',  type=int,                           default=2,                          help="Interpolation order for EFT weights.")
    argParser.add_argument('--triggerSelection',            action='store_true',                                                                                        help="Trigger selection?" )
    argParser.add_argument('--addPreFiringFlag',            action='store_true',                                                                                        help="Add flag for events w/o prefiring?" )
    argParser.add_argument('--topReco',                     action='store_true',                                                                                        help="Run Top Reco?")
    argParser.add_argument('--checkOnly',                   action='store_true',                                                                                        help="Check files at target and remove corrupt ones without reprocessing? Not possible with overwrite!")
    argParser.add_argument('--flagTTGamma',                 action='store_true',                                                                                        help="Check overlap removal for ttgamma")
    argParser.add_argument('--flagTTBar',                   action='store_true',                                                                                        help="Check overlap removal for ttbar")
    argParser.add_argument('--flagZWGamma',                 action='store_true',                                                                                        help="Check overlap removal for Zgamma/Wgamma")
    argParser.add_argument('--flagDYWJets',                 action='store_true',                                                                                        help="Check overlap removal for DY/WJets")
    argParser.add_argument('--flagTGamma',                  action='store_true',                                                                                        help="Check overlap removal for TGamma")
    argParser.add_argument('--flagSingleTopTch',            action='store_true',                                                                                        help="Check overlap removal for singleTop t-channel")
    argParser.add_argument('--flagGJets',                   action='store_true',                                                                                        help="Check overlap removal for GJets")
    argParser.add_argument('--flagQCD',                     action='store_true',                                                                                        help="Check overlap removal for QCD")
    argParser.add_argument('--skipSF',                      action='store_true',                                                                                        help="Skip scale factors")
    argParser.add_argument('--skipNanoTools',               action='store_true',                                                                                        help="Skip nanoTools")
    argParser.add_argument('--skipSystematicVariations',    action='store_true',                                                                                        help="Skip syst var")
    argParser.add_argument('--reuseNanoAOD',                action='store_true',                                                                                        help="Keep nanoAOD output?")
    argParser.add_argument('--reduceSizeBy',                action='store',                     type=int,                           default=1,                          help="Reduce the size of the sample by a factor of...")
    return argParser

options = get_parser().parse_args()

# B-Tagger
tagger = 'DeepCSV'
#tagger = 'CSVv2'

if len( filter( lambda x: x, [options.flagTTGamma, options.flagTTBar, options.flagZWGamma, options.flagDYWJets, options.flagTGamma, options.flagSingleTopTch, options.flagGJets, options.flagQCD] ) ) > 1:
    raise Exception("Overlap removal flag can only be True for ONE flag!" )

# Logging
import Analysis.Tools.logger as logger
logdir  = "/tmp/%s/"%str(uuid.uuid4())
logFile = '%s/%s_%s_%s_njob%s.txt'%(logdir, options.skim, '_'.join(options.samples), os.environ['USER'], str(0 if options.nJobs==1 else options.job) )
if not os.path.exists( logdir ):
    try: os.makedirs( logdir )
    except: pass
logger  = logger.get_logger(options.logLevel, logFile = logFile)


import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(options.logLevel, logFile = None )

import Samples.Tools.logger as logger_samples
logger_samples = logger_samples.get_logger(options.logLevel, logFile = None )

# Flags 
isDiLepGamma   = options.skim.lower().startswith('dilepgamma')
isDiLep        = options.skim.lower().startswith('dilep') and not isDiLepGamma
isSemiLepGamma = options.skim.lower().startswith('semilepgamma')
isSemiLep      = options.skim.lower().startswith('semilep') and not isSemiLepGamma

twoJetCond             = "(Sum$(Jet_pt>=29&&abs(Jet_eta)<=2.41)>=2)"

semilepNoIsoCond_ele   = "(Sum$(Electron_pt>=34&&abs(Electron_eta)<=2.11)>=1)"
semilepNoIsoCond_mu    = "(Sum$(Muon_pt>=29&&abs(Muon_eta)<=2.41)>=1)"
semilepNoIsoCond       = "(" + "||".join( [semilepNoIsoCond_ele, semilepNoIsoCond_mu] ) + ")"

semilepCond_ele        = "(Sum$(Electron_pt>=34&&abs(Electron_eta)<=2.11&&Electron_cutBased>=4)>=1)"
semilepCond_mu         = "(Sum$(Muon_pt>=29&&abs(Muon_eta)<=2.41&&Muon_tightId&&Muon_pfRelIso04_all<=0.16)>=1)"
semilepCond            = "(" + "||".join( [semilepCond_ele, semilepCond_mu] ) + ")"

dilepCond_sublead      = "(Sum$(Electron_pt>=14&&Electron_cutBased>=4&&abs(Electron_eta)<=2.41&&Electron_pfRelIso03_all<=0.13)+Sum$(Muon_pt>=14&&abs(Muon_eta)<=2.41&&Muon_mediumId&&Muon_pfRelIso03_all<=0.13))>=2"
dilepCond_lead         = "(Sum$(Electron_pt>=24&&Electron_cutBased>=4&&abs(Electron_eta)<=2.41&&Electron_pfRelIso03_all<=0.13)+Sum$(Muon_pt>=24&&abs(Muon_eta)<=2.41&&Muon_mediumId&&Muon_pfRelIso03_all<=0.13))>=1"
dilepCond              = "&&".join( [dilepCond_lead, dilepCond_sublead] )

gammaCond              = "(Sum$(Photon_pt>=19&&abs(Photon_eta)<=1.5&&Photon_electronVeto&&Photon_pixelSeed==0)>=1)"

# additional conditions for testing
addCond                = "(1)"
#addCond                = "(Sum$(Photon_genPartIdx<0)>0)"
#addCond                = "(Photon_genPartIdx<0)"

skimConds = []
if isDiLepGamma:
    skimConds += [dilepCond, gammaCond, addCond]
elif isDiLep:
    skimConds += [dilepCond, addCond]
elif isSemiLepGamma:
    skimConds += [semilepCond, gammaCond, addCond]  #performance: ~1.5k events left (1 ttbar semilep file)
elif isSemiLep:
    skimConds += [semilepNoIsoCond, addCond] #performance: ~75k events left (1 ttbar semilep file)
else:
    skimConds = ["(1)"]

#Samples: Load samples
maxNFiles = None
if options.small:
    maxNFiles = 1
    maxNEvents = 10000
    options.job = 0
    options.nJobs = 1 # set high to just run over 1 input file

if options.runOnLxPlus:
    # Set the redirector in the samples repository to the global redirector
    from Samples.Tools.config import redirector_global as redirector

if options.year == 2016:
    from Samples.nanoAOD.Summer16_private_legacy_v1 import *
    from Samples.nanoAOD.Summer16_private           import *
#    from Samples.nanoAOD.Run2016_14Dec2018          import *
    from Samples.nanoAOD.Run2016_17Jul2018_private  import *
elif options.year == 2017:
    from Samples.nanoAOD.Fall17_private_legacy_v1   import *
    from Samples.nanoAOD.Fall17_private             import *
#    from Samples.nanoAOD.Run2017_14Dec2018          import *
    from Samples.nanoAOD.Run2017_31Mar2018_private  import *
elif options.year == 2018:
    from Samples.nanoAOD.Autumn18_private_legacy_v1 import *
    from Samples.nanoAOD.Autumn18_private           import *
#    from Samples.nanoAOD.Run2018_14Dec2018          import *
    from Samples.nanoAOD.Run2018_17Sep2018_private  import *

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

# systematic variations
addSystematicVariations = (not isData) and (not options.skipSystematicVariations)

#Samples: combine if more than one
if len(samples)>1:
    sample_name =  samples[0].name+"_comb"
    logger.info( "Combining samples %s to %s.", ",".join(s.name for s in samples), sample_name )
    sample      = Sample.combine(sample_name, samples, maxN=maxNFiles)
    sampleForPU = Sample.combine(sample_name, samples, maxN=-1)
elif len(samples)==1:
    sample      = samples[0]
    sampleForPU = samples[0]

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

# output directory (store temporarily when running on dpm)
if options.writeToDPM:
    from TTGammaEFT.Tools.user import dpm_directory as user_directory
    from Samples.Tools.config  import redirector    as redirector_hephy
    # Allow parallel processing of N threads on one worker
    output_directory = os.path.join( '/tmp/%s'%os.environ['USER'], str(uuid.uuid4()) )
    targetPath       = redirector_hephy + os.path.join( user_directory, 'postprocessed',  options.processingEra, options.skim + postfix, sampleDir )
else:
    # User specific
    from TTGammaEFT.Tools.user import postprocessing_output_directory as user_directory
    directory  = os.path.join( user_directory, options.processingEra ) 
    output_directory = os.path.join( directory, options.skim+postfix, sampleDir )

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
filename, ext = os.path.splitext( outputFilePath )

if os.path.exists( output_directory ) and options.overwrite:
    if options.nJobs > 1:
        logger.warning( "NOT removing directory %s because nJobs = %i", output_directory, options.nJobs )
    else:
        logger.info( "Output directory %s exists. Deleting.", outputFilePath )
#        shutil.rmtree( output_directory, ignore_errors=True )
        shutil.rmtree( outputFilePath, ignore_errors=True )

if not os.path.exists( output_directory ):
    try:
        os.makedirs( output_directory )
        logger.info( "Created output directory %s.", output_directory )
    except:
        logger.info( "Directory %s already exists.", output_directory )
        pass

# checking overwrite or file exists
if not options.overwrite and options.writeToDPM:
    try:
        # ls the directory on DPM
        checkFile = "/cms" + targetPath.split("/cms")[1] + "/"
        cmd = [ "xrdfs", redirector_hephy, "ls", checkFile ]
        fileList = subprocess.check_output( cmd ).split("\n")[:-1]
        fileList = [ line.split(checkFile)[1].split(".root")[0] for line in fileList ]
    except:
        # Not even the directory exists on dpm
        fileList = []

    if sample.name in fileList:
        # Sample found on dpm, check if it is ok
        target  = os.path.join( targetPath, sample.name+".root" )
        if checkRootFile( target, checkForObjects=["Events"] ) and deepCheckRootFile( target ) and deepCheckWeight( target ):
            logger.info( "File already processed. Source: File check ok! Skipping." ) # Everything is fine, no overwriting
            sys.exit(0)
        else:
            logger.info( "File corrupt. Removing file from target." )
            cmd = [ "xrdfs", redirector_hephy, "rm", "/cms" + target.split("/cms")[1] ]
            subprocess.call( cmd )
            if options.checkOnly: sys.exit(0)
            logger.info( "Reprocessing." )
    else:
        logger.info( "Sample not processed yet." )
        if options.checkOnly: sys.exit(0)
        logger.info( "Processing." )

elif not options.overwrite and not options.writeToDPM:
    if os.path.isfile(outputFilePath):
        logger.info( "Output file %s found.", outputFilePath)
        if checkRootFile( outputFilePath, checkForObjects=["Events"] ) and deepCheckRootFile( outputFilePath ) and deepCheckWeight( outputFilePath ):
            logger.info( "File already processed. Source: File check ok! Skipping." ) # Everything is fine, no overwriting
            sys.exit(0)
        else:
            logger.info( "File corrupt. Removing file from target." )
            os.remove( outputFilePath )
            if options.checkOnly: sys.exit(0)
            logger.info( "Reprocessing." )
    else:
        logger.info( "Sample not processed yet." )
        if options.checkOnly: sys.exit(0)
        logger.info( "Processing." )

else:
    logger.info( "Overwriting.")

# Cross section for postprocessed sample
xSection = samples[0].xSection if isMC else None

if not options.skipSF:
    # Reweighting, Scalefactors, Efficiencies
    from Analysis.Tools.LeptonSF import LeptonSF
    LeptonSFMedium = LeptonSF( year=options.year, ID="medium" )
    LeptonSFTight = LeptonSF( year=options.year, ID="tight" )

    from Analysis.Tools.LeptonTrackingEfficiency import LeptonTrackingEfficiency
    LeptonTrackingSF = LeptonTrackingEfficiency( year=options.year )

    from Analysis.Tools.PhotonSF import PhotonSF as PhotonSF_
    PhotonSF = PhotonSF_( year=options.year )

    # not used anymore
    #from Analysis.Tools.PhotonReconstructionEfficiency import PhotonReconstructionEfficiency
    #PhotonRecEff = PhotonReconstructionEfficiency( year=options.year )

    # Update to other years when available
    from Analysis.Tools.PhotonElectronVetoEfficiency import PhotonElectronVetoEfficiency
    PhotonElectronVetoSF = PhotonElectronVetoEfficiency( year=options.year )

    from TTGammaEFT.Tools.TriggerEfficiency import TriggerEfficiency
    TriggerEff_withBackup = TriggerEfficiency( with_backup_triggers = True,  year=options.year )
    TriggerEff            = TriggerEfficiency( with_backup_triggers = False, year=options.year )

    # Update to other years when available
    from Analysis.Tools.BTagEfficiency import BTagEfficiency
    BTagEff = BTagEfficiency( year=options.year, tagger=tagger ) # default medium WP

    # PrefiringWeight
    L1PW = L1PrefireWeight( options.year )

    if isMC:
        from Analysis.Tools.puReweighting import getReweightingFunction
        if options.year == 2016:
            nTrueInt_puRW       = getReweightingFunction(data="PU_2016_35920_XSecCentral",  mc="Summer16")
            nTrueInt_puRWDown   = getReweightingFunction(data="PU_2016_35920_XSecDown",     mc="Summer16")
            nTrueInt_puRWUp     = getReweightingFunction(data="PU_2016_35920_XSecUp",       mc="Summer16")
            nTrueInt_puRWVDown  = getReweightingFunction(data="PU_2016_35920_XSecVDown",    mc="Summer16")
            nTrueInt_puRWVUp    = getReweightingFunction(data="PU_2016_35920_XSecVUp",      mc="Summer16")
        elif options.year == 2017:
            # messed up MC PU profiles
            puProfiles          = puProfile( source_sample=sampleForPU )
            mcHist              = puProfiles.cachedTemplate( selection="( 1 )", weight='genWeight', overwrite=False ) # use genWeight for amc@NLO samples. No problems encountered so far
            nTrueInt_puRW       = getReweightingFunction(data="PU_2017_41860_XSecCentral",  mc=mcHist)
            nTrueInt_puRWDown   = getReweightingFunction(data="PU_2017_41860_XSecDown",     mc=mcHist)
            nTrueInt_puRWUp     = getReweightingFunction(data="PU_2017_41860_XSecUp",       mc=mcHist)
            nTrueInt_puRWVDown  = getReweightingFunction(data="PU_2017_41860_XSecVDown",    mc=mcHist)
            nTrueInt_puRWVUp    = getReweightingFunction(data="PU_2017_41860_XSecVUp",      mc=mcHist)
        elif options.year == 2018:
            nTrueInt_puRW       = getReweightingFunction(data="PU_2018_58830_XSecCentral",  mc="Autumn18")
            nTrueInt_puRWDown   = getReweightingFunction(data="PU_2018_58830_XSecDown",     mc="Autumn18")
            nTrueInt_puRWUp     = getReweightingFunction(data="PU_2018_58830_XSecUp",       mc="Autumn18")
            nTrueInt_puRWVDown  = getReweightingFunction(data="PU_2018_58830_XSecVDown",    mc="Autumn18")
            nTrueInt_puRWVUp    = getReweightingFunction(data="PU_2018_58830_XSecVUp",      mc="Autumn18")

#branches to be kept for data and MC
branchKeepStrings_DATAMC = [\
    "run", "luminosityBlock", "event",
    "PV_npvs", "PV_npvsGood",
    "fixed*",
    "MET_*",
    "Flag_*", "HLT_*",
]

#branches to be kept for MC samples only
branchKeepStrings_MC = [\
    "Generator_*",
    "genWeight",
    "Pileup_nTrueInt",
    "GenPart_*", "nGenPart",
    "GenJet_*", "nGenJet",
    "Pileup_*",
    "LHE_*"
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
else:
    lumiScaleFactor = xSection * targetLumi / float( sample.normalization ) if xSection is not None else None
    branchKeepStrings = branchKeepStrings_DATAMC + branchKeepStrings_MC


# get nano variable lists
NanoVars = NanoVariables( options.year )
#VarString ... "var1/type,var2/type"
#Variables ... ["var1/type","var2/type"]
#VarList   ... ["var1", "var2"]

readGenVarString      = NanoVars.getVariableString(   "Gen",      postprocessed=False, data=sample.isData )
readGenJetVarString   = NanoVars.getVariableString(   "GenJet",   postprocessed=False, data=sample.isData )
readJetVarString      = NanoVars.getVariableString(   "Jet",      postprocessed=False, data=sample.isData, skipSyst=options.skipNanoTools )
readElectronVarString = NanoVars.getVariableString(   "Electron", postprocessed=False, data=sample.isData )
readMuonVarString     = NanoVars.getVariableString(   "Muon",     postprocessed=False, data=sample.isData )
readPhotonVarString   = NanoVars.getVariableString(   "Photon",   postprocessed=False, data=sample.isData )

readGenVarList        = NanoVars.getVariableNameList( "Gen",      postprocessed=False, data=sample.isData )
readGenJetVarList     = NanoVars.getVariableNameList( "GenJet",   postprocessed=False, data=sample.isData )
readJetVarList        = NanoVars.getVariableNameList( "Jet",      postprocessed=False, data=sample.isData, skipSyst=options.skipNanoTools  )
readElectronVarList   = NanoVars.getVariableNameList( "Electron", postprocessed=False, data=sample.isData )
readMuonVarList       = NanoVars.getVariableNameList( "Muon",     postprocessed=False, data=sample.isData )
readPhotonVarList     = NanoVars.getVariableNameList( "Photon",   postprocessed=False, data=sample.isData )

readLeptonVariables   = NanoVars.getVariables(        "Lepton",   postprocessed=False, data=sample.isData )

writeGenVarString     = NanoVars.getVariableString(   "Gen",      postprocessed=True,  data=sample.isData )
writeGenJetVarString  = NanoVars.getVariableString(   "GenJet",   postprocessed=True,  data=sample.isData )
writeJetVarString     = NanoVars.getVariableString(   "Jet",      postprocessed=True,  data=sample.isData, skipSyst=options.skipNanoTools  )
writeLeptonVarString  = NanoVars.getVariableString(   "Lepton",   postprocessed=True,  data=sample.isData )
writePhotonVarString  = NanoVars.getVariableString(   "Photon",   postprocessed=True,  data=sample.isData )

writeJetVarList       = NanoVars.getVariableNameList( "Jet",      postprocessed=True,  data=sample.isData, skipSyst=options.skipNanoTools  )
writeBJetVarList      = NanoVars.getVariableNameList( "BJet",     postprocessed=True,  data=sample.isData )
writeGenVarList       = NanoVars.getVariableNameList( "Gen",      postprocessed=True,  data=sample.isData )
writeGenJetVarList    = NanoVars.getVariableNameList( "GenJet",   postprocessed=True,  data=sample.isData )
writeLeptonVarList    = NanoVars.getVariableNameList( "Lepton",   postprocessed=True,  data=sample.isData )
writePhotonVarList    = NanoVars.getVariableNameList( "Photon",   postprocessed=True,  data=sample.isData )

writeGenVariables     = NanoVars.getVariables( "Gen",      postprocessed=True,  data=sample.isData )
writeGenJetVariables  = NanoVars.getVariables( "GenJet",   postprocessed=True,  data=sample.isData )
writeJetVariables     = NanoVars.getVariables( "Jet",      postprocessed=True,  data=sample.isData, skipSyst=options.skipNanoTools  )
writeBJetVariables    = NanoVars.getVariables( "BJet",     postprocessed=True,  data=sample.isData )
writeLeptonVariables  = NanoVars.getVariables( "Lepton",   postprocessed=True,  data=sample.isData )
writePhotonVariables  = NanoVars.getVariables( "Photon",   postprocessed=True,  data=sample.isData )

# Read Variables
read_variables  = map( TreeVariable.fromString, ['run/I', 'luminosityBlock/I', 'event/l'] )
read_variables += map( TreeVariable.fromString, ['MET_pt/F', 'MET_phi/F'] )

if not options.skipNanoTools:
    if options.year == 2017:
        read_variables += map(TreeVariable.fromString, [ 'METFixEE2017_pt/F', 'METFixEE2017_phi/F', 'METFixEE2017_pt_nom/F', 'METFixEE2017_phi_nom/F', 'MET_pt_min/F'])
        if isMC:
            read_variables += map(TreeVariable.fromString, [ 'METFixEE2017_pt_jesTotalUp/F', 'METFixEE2017_pt_jesTotalDown/F', 'METFixEE2017_pt_jerUp/F', 'METFixEE2017_pt_jerDown/F', 'METFixEE2017_pt_unclustEnDown/F', 'METFixEE2017_phi_unclustEnUp/F'])
    read_variables += map(TreeVariable.fromString, [ 'MET_pt_nom/F', 'MET_phi_nom/F' ])
    if isMC:
        read_variables += map(TreeVariable.fromString, [ 'MET_pt_jesTotalUp/F', 'MET_pt_jesTotalDown/F', 'MET_pt_jerUp/F', 'MET_pt_jerDown/F', 'MET_pt_unclustEnDown/F', 'MET_pt_unclustEnUp/F'])
        read_variables += map(TreeVariable.fromString, [ 'MET_phi_jesTotalUp/F', 'MET_phi_jesTotalDown/F', 'MET_phi_jerUp/F', 'MET_phi_jerDown/F', 'MET_phi_unclustEnDown/F', 'MET_phi_unclustEnUp/F'])

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
    read_variables += [ TreeVariable.fromString('nGenJet/I'),
                        VectorTreeVariable.fromString('GenJet[%s]'%readGenJetVarString) ]

# Write Variables
new_variables  = []
new_variables += [ 'weight/F' ]
new_variables += [ 'triggerDecision/I', 'isData/I']

# Jets
new_variables += [ 'nJet/I' ]
new_variables += [ 'nJetGood/I' ] 

new_variables += [ 'nJetGoodMVA/I' ] 
new_variables += [ 'nJetGoodNoChgIso/I' ] 
new_variables += [ 'nJetGoodNoSieie/I' ] 
new_variables += [ 'nJetGoodNoChgIsoNoSieie/I' ] 

new_variables += [ 'Jet[%s]'      %writeJetVarString ]
new_variables += [ 'JetGood0_'  + var for var in writeJetVariables ]
new_variables += [ 'JetGood1_'  + var for var in writeJetVariables ]

# BJets
new_variables += [ 'nBTag/I']
new_variables += [ 'nBTagGood/I']

new_variables += [ 'nBTagGoodMVA/I' ] 
new_variables += [ 'nBTagGoodNoChgIso/I' ] 
new_variables += [ 'nBTagGoodNoSieie/I' ] 
new_variables += [ 'nBTagGoodNoChgIsoNoSieie/I' ] 

new_variables += [ 'Bj0_' + var for var in writeBJetVariables ]
new_variables += [ 'Bj1_' + var for var in writeBJetVariables ]

# Leptons
new_variables += [ 'nLepton/I' ] 
new_variables += [ 'nLeptonVeto/I']
new_variables += [ 'nLeptonVetoIsoCorr/I']
new_variables += [ 'nLeptonMedium/I' ] 
new_variables += [ 'nLeptonGood/I' ] 
new_variables += [ 'nLeptonGoodLead/I' ] 
new_variables += [ 'nLeptonTight/I']
new_variables += [ 'nLeptonTightNoIso/I']
new_variables += [ 'nLeptonTightInvIso/I']
new_variables += [ 'nLeptonTightInvIsoLoose/I']
new_variables += [ 'nLeptonTightInvIsoVeto/I']

new_variables += [ 'nElectron/I',            'nMuon/I']
new_variables += [ 'nElectronVeto/I',        'nMuonVeto/I']
new_variables += [ 'nElectronVetoIsoCorr/I']
new_variables += [ 'nElectronMedium/I',      'nMuonMedium/I']
new_variables += [ 'nElectronGood/I',        'nMuonGood/I']
new_variables += [ 'nElectronGoodLead/I',    'nMuonGoodLead/I']
new_variables += [ 'nElectronTight/I',       'nMuonTight/I']
new_variables += [ 'nElectronTightNoIso/I',  'nMuonTightNoIso/I']
new_variables += [ 'nElectronTightInvIso/I', 'nMuonTightInvIso/I']
new_variables += [ 'nElectronTightInvIsoLoose/I', 'nMuonTightInvIsoLoose/I']
new_variables += [ 'nElectronTightInvIsoVeto/I', 'nMuonTightInvIsoVeto/I']

new_variables += [ 'Lepton[%s]'     %writeLeptonVarString ]

new_variables += [ 'LeptonGood0_'        + var for var in writeLeptonVariables ]
new_variables += [ 'LeptonGood1_'        + var for var in writeLeptonVariables ]
new_variables += [ 'LeptonTight0_'       + var for var in writeLeptonVariables ]
new_variables += [ 'LeptonTight1_'       + var for var in writeLeptonVariables ]
new_variables += [ 'LeptonTightInvIso0_' + var for var in writeLeptonVariables ]
new_variables += [ 'MisIDElectron0_'     + var for var in writeLeptonVariables ]

# Photons
new_variables += [ 'nPhoton/I' ] 
new_variables += [ 'nPhotonGood/I' ] 
new_variables += [ 'nPhotonMVA/I' ] 
new_variables += [ 'nPhotonNoChgIso/I' ] 
new_variables += [ 'nPhotonNoSieie/I' ] 
new_variables += [ 'nPhotonNoChgIsoNoSieie/I' ] 
new_variables += [ 'Photon[%s]'     %writePhotonVarString ]

new_variables += [ 'PhotonGood0_'            + var for var in writePhotonVariables ]
new_variables += [ 'PhotonMVA0_'            + var for var in writePhotonVariables ]
new_variables += [ 'mllgammaMVA/F' ] 
new_variables += [ 'PhotonGood1_'            + var for var in writePhotonVariables ]
new_variables += [ 'PhotonNoChgIso0_'        + var for var in writePhotonVariables ]
new_variables += [ 'mllgammaNoChgIso/F' ] 
new_variables += [ 'PhotonNoSieie0_'         + var for var in writePhotonVariables ]
new_variables += [ 'mllgammaNoSieie/F' ] 
new_variables += [ 'PhotonNoChgIsoNoSieie0_' + var for var in writePhotonVariables ]
new_variables += [ 'mllgammaNoChgIsoNoSieie/F' ] 

# Others
new_variables += [ 'ht/F' ]
new_variables += [ 'photonJetdR/F', 'photonLepdR/F', 'leptonJetdR/F', 'tightLeptonJetdR/F' ] 
new_variables += [ 'invtightLeptonJetdR/F' ] 
new_variables += [ 'MET_pt_photonEstimated/F', 'MET_phi_photonEstimated/F', 'METSig_photonEstimated/F' ]
new_variables += [ 'MET_pt/F', 'MET_phi/F', 'MET_pt_min/F', 'METSig/F' ]
if addSystematicVariations:
    for var in ['jesTotalUp', 'jesTotalDown', 'jerUp', 'jerDown', 'unclustEnUp', 'unclustEnDown']:
        new_variables.extend( ['nJetGood_'+var+'/I', 'nBTagGood_'+var+'/I','ht_'+var+'/F'] )
        new_variables.extend( ['MET_pt_'+var+'/F', 'MET_phi_'+var+'/F', 'METSig_'+var+'/F'] )

new_variables += [ 'mll/F',  'mllgamma/F' ] 
new_variables += [ 'mlltight/F',  'mllgammatight/F' ] 
new_variables += [ 'm3/F',   'm3wBJet/F', 'm3gamma/F' ] 
new_variables += [ 'lldR/F', 'lldPhi/F' ] 
new_variables += [ 'bbdR/F', 'bbdPhi/F' ] 
new_variables += [ 'mLtight0Gamma/F',  'mL0Gamma/F',  'mL1Gamma/F' ] 
new_variables += [ 'mLinvtight0Gamma/F' ] 
new_variables += [ 'lpTight/F' ] 
new_variables += [ 'lpInvTight/F' ] 
new_variables += [ 'l0GammadR/F',  'l0GammadPhi/F' ] 
new_variables += [ 'ltight0GammadR/F', 'ltight0GammadPhi/F' ] 
new_variables += [ 'linvtight0GammadR/F', 'linvtight0GammadPhi/F' ] 
new_variables += [ 'l1GammadR/F',  'l1GammadPhi/F' ] 
new_variables += [ 'j0GammadR/F',  'j0GammadPhi/F' ] 
new_variables += [ 'j1GammadR/F',  'j1GammadPhi/F' ] 

new_variables += [ 'mT/F', 'mT2ll/F', 'mT2lg/F', 'mT2bb/F', 'mT2blbl/F']
new_variables += [ 'mTinv/F', 'mT2linvg/F']
mt2Calculator = mt2Calculator()

if options.addPreFiringFlag: new_variables += [ 'unPreFirableEvent/I' ]

new_variables += [ "reweightHEM/F" ]
if isMC:
    new_variables += [ 'GenElectron[%s]' %writeGenVarString ]
    new_variables += [ 'GenMuon[%s]'     %writeGenVarString ]
    new_variables += [ 'GenPhoton[%s]'   %writeGenVarString ]
    new_variables += [ 'GenJets[%s]'      %writeGenJetVarString ]
    new_variables += [ 'GenBJet[%s]'     %writeGenJetVarString ]
    new_variables += [ 'GenTop[%s]'      %writeGenVarString ]
    new_variables += [ 'isTTGamma/I', 'isZWGamma/I', 'isTGamma/I', 'isGJets/I', 'overlapRemoval/I' ]

    new_variables += [ 'nGenW/I', 'nGenWJets/I', 'nGenWElectron/I', 'nGenWMuon/I','nGenWTau/I', 'nGenWTauJets/I', 'nGenWTauElectron/I', 'nGenWTauMuon/I' ]

    new_variables += [ 'reweightPU/F', 'reweightPUDown/F', 'reweightPUUp/F', 'reweightPUVDown/F', 'reweightPUVUp/F' ]

    if not options.skipSF:
        new_variables += [ 'reweightLepton2lSF/F', 'reweightLepton2lSFUp/F', 'reweightLepton2lSFDown/F' ]
        new_variables += [ 'reweightLeptonTracking2lSF/F', 'reweightLeptonTracking2lSFUp/F', 'reweightLeptonTracking2lSFDown/F' ]
        new_variables += [ 'reweightLeptonMediumSF/F', 'reweightLeptonMediumSFUp/F', 'reweightLeptonMediumSFDown/F' ]
#        new_variables += [ 'reweightLeptonTrackingMediumSF/F', 'reweightLeptonTrackingMediumSFUp/F', 'reweightLeptonTrackingMediumSFDown/F' ]
        new_variables += [ 'reweightLeptonTightSF/F', 'reweightLeptonTightSFUp/F', 'reweightLeptonTightSFDown/F' ]
        new_variables += [ 'reweightLeptonTrackingTightSF/F', 'reweightLeptonTrackingTightSFUp/F', 'reweightLeptonTrackingTightSFDown/F' ]

        new_variables += [ 'reweightDilepTrigger/F', 'reweightDilepTriggerUp/F', 'reweightDilepTriggerDown/F' ]
        new_variables += [ 'reweightDilepTriggerBackup/F', 'reweightDilepTriggerBackupUp/F', 'reweightDilepTriggerBackupDown/F' ]

        new_variables += [ 'reweightPhotonSF/F', 'reweightPhotonSFUp/F', 'reweightPhotonSFDown/F' ]
        new_variables += [ 'reweightPhotonElectronVetoSF/F', 'reweightPhotonElectronVetoSFUp/F', 'reweightPhotonElectronVetoSFDown/F' ]
#        new_variables += [ 'reweightPhotonReconstructionSF/F' ]

        new_variables += [ 'reweightL1Prefire/F', 'reweightL1PrefireUp/F', 'reweightL1PrefireDown/F' ]

        # Btag weights Method 1a
        for var in BTagEff.btagWeightNames:
            if var!='MC':
                new_variables += [ 'reweightBTag_'+var+'/F' ]

# TopReco
if options.topReco:
    # Import the main top reco class
    from Analysis.TopReco.TopReco import topReco
    # Variables
    for name in [ "lp", "lm", "jetB", "jetBbar", "Wp", "Wm", "neutrino", "neutrinoBar", "top", "topBar" ]:
        for var in ["pt", "eta", "phi", "mass"]:
            new_variables.append( "topReco_"+name+"_"+var+'/F' )
    # Simple setter for top reco candidates
    def setParticle( event, name, particle ):
        setattr( event, "topReco_"+name+"_pt", particle.Pt() )
        setattr( event, "topReco_"+name+"_eta", particle.Eta() )
        setattr( event, "topReco_"+name+"_phi", particle.Phi() )
        setattr( event, "topReco_"+name+"_mass", particle.M() )

if isData:
    new_variables += ['jsonPassed/I']

ptVar="pt_nom" if not options.skipNanoTools else "pt"

# Overlap removal Selection
genPhotonSel_TTG_OR = genPhotonSelector( 'overlapTTGamma' )
genPhotonSel_ZG_OR  = genPhotonSelector( 'overlapZWGamma' )
genPhotonSel_T_OR   = genPhotonSelector( 'overlapSingleTopTch' )
genPhotonSel_GJ_OR  = genPhotonSelector( 'overlapGJets' )
# Gen Selection
genLeptonSel = genLeptonSelector()
genPhotonSel = genPhotonSelector()
genJetSel    = genJetSelector()
# Electron Selection
recoElectronSel_veto    = eleSelector( "veto" )
recoElectronSel_medium  = eleSelector( "medium" )
recoElectronSel_tight2l = eleSelector( "tight2l" )
recoElectronSel_tight   = eleSelector( "tight" )
# Muon Selection
recoMuonSel_veto        = muonSelector( "veto" )
recoMuonSel_medium      = muonSelector( "medium" )
recoMuonSel_tight       = muonSelector( "tight" )
# Photon Selection
recoPhotonSel_medium    = photonSelector( 'medium', year=options.year )
recoPhotonSel_mva       = photonSelector( 'mva',    year=options.year )
# Jet Selection
recoJetSel              = jetSelector( options.year ) #pt_nom?

if options.addPreFiringFlag: 
    from Analysis.Tools.PreFiring import PreFiring
    PreFire = PreFiring( sampleDir )
    unPreFirableEvents = [ (event, run) for event, run, lumi in PreFire.getUnPreFirableEvents() ]
    del PreFire

# Trigger selection
if isData:
    from TTGammaEFT.Tools.TriggerSelector import TriggerSelector
    Ts          = TriggerSelector( options.year, singleLepton=(isSemiLep or isSemiLepGamma) )
    triggerCond = Ts.getSelection( options.samples[0] if isData else "MC" )
    logger.info("Sample will have the following trigger skim: %s"%triggerCond)
    skimConds.append( triggerCond )

if not options.skipNanoTools:
    # prepare metsignificance and jes/jer
    MetSig = MetSignificance( sample, options.year, output_directory )
    MetSig( "&&".join(skimConds) )
    newfiles = MetSig.getNewSampleFilenames()
#    sample.clear()
    sample.files = copy.copy(newfiles)
#    sample.name  = MetSig.name
    if isMC: sample.normalization = sample.getYieldFromDraw(weightString="genWeight")['val']
#    sample.isData = isData
#    del MetSig

# Trigger selection after nanotools
if isData and options.triggerSelection:
    from TTGammaEFT.Tools.TriggerSelector import TriggerSelector
    Ts          = TriggerSelector( options.year, singleLepton=isSemiLep )
    triggerCond = Ts.getSelection( options.samples[0] if isData else "MC" )
    logger.info("Sample will have the following trigger skim: %s"%triggerCond)
    skimConds.append( triggerCond )

# Define a reader
#sel = "&&".join(skimConds) if options.skipNanoTools else "(1)"
reader = sample.treeReader( variables=read_variables, selectionString="&&".join(skimConds) )

def getMetPhotonEstimated( met_pt, met_phi, photon ):
  met = ROOT.TLorentzVector()
  met.SetPtEtaPhiM(met_pt, 0, met_phi, 0 )
  gamma = ROOT.TLorentzVector()
  gamma.SetPtEtaPhiM(photon['pt'], photon['eta'], photon['phi'], photon['mass'] )
  metGamma = met + gamma
  return (metGamma.Pt(), metGamma.Phi())

## Calculate corrected met pt/phi using systematics for jets
def getMetJetCorrected(met_pt, met_phi, jets, var, ptVar='pt'):
    met_corr_px  = met_pt*cos(met_phi) + sum([(j[ptVar]-j['pt_'+var])*cos(j['phi']) if j[ptVar]>15 else 0 for j in jets])
    met_corr_py  = met_pt*sin(met_phi) + sum([(j[ptVar]-j['pt_'+var])*sin(j['phi']) if j[ptVar]>15 else 0 for j in jets])
    met_corr_pt  = sqrt(met_corr_px**2 + met_corr_py**2)
    met_corr_phi = atan2(met_corr_py, met_corr_px)
    return (met_corr_pt, met_corr_phi)

def getMetCorrected( r, var, addPhoton=None ):
    if not var: # why is this here??
        if addPhoton: return getMetPhotonEstimated(r.MET_pt_nom, r.MET_phi_nom, addPhoton)
        else:         return (r.MET_pt_nom, r.MET_phi_nom)

    elif var in [ "unclustEnUp", "unclustEnDown" ]:
        var_ = var
        MET_pt  = getattr(r, "MET_pt_"+var_)
        MET_phi = getattr(r, "MET_phi_"+var_)
        if addPhoton: return getMetPhotonEstimated(MET_pt, MET_phi, addPhoton)
        else:         return (MET_pt, MET_phi)

    else:
        raise ValueError

def addCorrRelIso( ele, mu, photons ):
    for e in ele:
        e["pfRelIso03_all_corr"] = e["pfRelIso03_all"]
        g = filter( lambda pho: e["index"] == pho["electronIdx"], photons )[:1]
        if g:
            e["pfRelIso03_all_corr"] = min( e["pfRelIso03_all"], g[0]["pfRelIso03_all"] )
    for m in mu:
        m["pfRelIso03_all_corr"] = m["pfRelIso03_all"]


def addMissingVariables( coll, vars ):
    for p in coll:
        for var_ in vars:
            var = var_.split("/")[0]
            if not var in p:
                p[var] = 0 if var_.endswith("/O") else -999

def addJetFlags( jets, cleaningLeptons, cleaningPhotons ):
    for j in jets:
        minDRLep    = min( [ deltaR( l, j ) for l in cleaningLeptons ] + [999] )
        minDRPhoton = min( [ deltaR( g, j ) for g in cleaningPhotons ] + [999] )
        j["clean"]  = minDRLep > 0.4 and minDRPhoton > 0.1
        j["isGood"] = recoJetSel( j, ptVar=ptVar ) and j["clean"]
        j["isBJet"] = isBJet( j, tagger=tagger, year=options.year )

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

    if options.addPreFiringFlag:
        event.unPreFirableEvent = ( int(r.event), int(r.run) ) in unPreFirableEvents

    if isMC:

        # weight
        event.weight = lumiScaleFactor*r.genWeight if lumiScaleFactor is not None else 0

        # GEN Particles
        gPart = getParticles( r, collVars=readGenVarList, coll="GenPart" )
        gJets = getParticles( r, collVars=readGenJetVarList, coll="GenJet" )

        # Gen Leptons in ttbar/gamma decays
        # get Ws from top or MG matrix element (from gluon)
        GenW = filter( lambda l: abs(l['pdgId']) == 24 and l["genPartIdxMother"] >= 0 and l["genPartIdxMother"] < len(gPart), gPart )
        GenW = filter( lambda l: abs(gPart[l["genPartIdxMother"]]["pdgId"]) in [6,21], GenW )
        # e/mu/tau with W mother
        GenLepWMother    = filter( lambda l: abs(l['pdgId']) in [11,13,15] and l["genPartIdxMother"] >= 0 and l["genPartIdxMother"] < len(gPart), gPart )
        GenLepWMother    = filter( lambda l: abs(gPart[l["genPartIdxMother"]]["pdgId"])==24, GenLepWMother )
        # e/mu with tau mother and tau has a W in parentsList
        GenLepTauMother  = filter( lambda l: abs(l['pdgId']) in [11,13] and l["genPartIdxMother"] >= 0 and l["genPartIdxMother"] < len(gPart), gPart )
        GenLepTauMother  = filter( lambda l: abs(gPart[l["genPartIdxMother"]]["pdgId"])==15 and 24 in map( abs, getParentIds( gPart[l["genPartIdxMother"]], gPart)), GenLepTauMother )

        GenWElectron = filter( lambda l: abs(l['pdgId']) == 11, GenLepWMother )
        GenWMuon     = filter( lambda l: abs(l['pdgId']) == 13, GenLepWMother )
        GenWTau      = filter( lambda l: abs(l['pdgId']) == 15, GenLepWMother )

        GenTauElectron = filter( lambda l: abs(l['pdgId']) == 11, GenLepTauMother )
        GenTauMuon     = filter( lambda l: abs(l['pdgId']) == 13, GenLepTauMother )

        gPart.sort( key = lambda p: -p['pt'] )
        gJets.sort( key = lambda p: -p['pt'] )

        # Overlap removal flags for ttgamma/ttbar and Zgamma/DY
        GenPhoton                  = filterGenPhotons( gPart, status='last' )

        # OR ttgamma/tt
        GenIsoPhotonTTG            = filter( lambda g: isIsolatedPhoton( g, gPart, coneSize=0.1,  ptCut=5, excludedPdgIds=[12,-12,14,-14,16,-16] ), GenPhoton    )
        GenIsoPhotonNoMesonTTG     = filter( lambda g: not hasMesonMother( getParentIds( g, gPart ) ), GenIsoPhotonTTG )

        # OR DY/ZG, WG/WJets
        GenIsoPhoton               = filter( lambda g: isIsolatedPhoton( g, gPart, coneSize=0.05,  ptCut=5, excludedPdgIds=[12,-12,14,-14,16,-16] ), GenPhoton    )
        GenIsoPhotonNoMeson        = filter( lambda g: not hasMesonMother( getParentIds( g, gPart ) ), GenIsoPhoton )

        # OR singleT/tG
#        GenIsoPhotonTG             = filter( lambda g: isIsolatedPhoton( g, gPart, coneSize=0.05, ptCut=5, excludedPdgIds=[12,-12,14,-14,16,-16] ), GenPhoton    )
#        GenIsoPhotonNoMesonTG      = filter( lambda g: not hasMesonMother( getParentIds( g, gPart ) ), GenIsoPhotonTG )
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

        # Gen Leptons in ttbar/gamma decays
        # get Ws from top or MG matrix element (from gluon)
        GenW = filter( lambda l: abs(l['pdgId']) == 24 and l["genPartIdxMother"] >= 0 and l["genPartIdxMother"] < len(gPart), gPart )
        GenW = filter( lambda l: abs(gPart[l["genPartIdxMother"]]["pdgId"]) in [6,21], GenW )

        # e/mu/tau with W mother
        GenLepWMother    = filter( lambda l: abs(l['pdgId']) in [11,13,15] and l["genPartIdxMother"] >= 0 and l["genPartIdxMother"] < len(gPart), gPart )
        GenLepWMother    = filter( lambda l: abs(gPart[l["genPartIdxMother"]]["pdgId"])==24, GenLepWMother )
        # e/mu with tau mother and tau has a W in parentsList
        GenLepTauMother  = filter( lambda l: abs(l['pdgId']) in [11,13] and l["genPartIdxMother"] >= 0 and l["genPartIdxMother"] < len(gPart), gPart )
        GenLepTauMother  = filter( lambda l: abs(gPart[l["genPartIdxMother"]]["pdgId"])==15 and 24 in map( abs, getParentIds( gPart[l["genPartIdxMother"]], gPart)), GenLepTauMother )

        GenWElectron = filter( lambda l: abs(l['pdgId']) == 11, GenLepWMother )
        GenWMuon     = filter( lambda l: abs(l['pdgId']) == 13, GenLepWMother )
        GenWTau      = filter( lambda l: abs(l['pdgId']) == 15, GenLepWMother )

        GenTauElectron = filter( lambda l: abs(l['pdgId']) == 11, GenLepTauMother )
        GenTauMuon     = filter( lambda l: abs(l['pdgId']) == 13, GenLepTauMother )

        gPart.sort( key = lambda p: -p['pt'] )

        # Split gen particles
        # still needs improvement with filterGen function
        GenElectron = list( filter( lambda l: genLeptonSel(l), filterGenElectrons( gPart, status='last' ) ) )
        GenMuon     = list( filter( lambda l: genLeptonSel(l), filterGenMuons( gPart, status='last' )     ) )
        GenPhoton   = list( filter( lambda g: genPhotonSel(g), GenPhoton                                  ) )
        GenTop      = list( filter( lambda t: genJetSel(t),    filterGenTops( gPart )                     ) )
        GenJet      = list( filter( lambda j: genJetSel(j),    gJets                                      ) )
        GenBJet     = list( filter( lambda j: genJetSel(j),    filterGenBJets( gJets )                    ) )

        # Store
        fill_vector_collection( event, "GenElectron", writeGenVarList,    GenElectron[:20] )
        fill_vector_collection( event, "GenMuon",     writeGenVarList,    GenMuon[:20]     )
        fill_vector_collection( event, "GenPhoton",   writeGenVarList,    GenPhoton[:20]   )
        fill_vector_collection( event, "GenBJet",     writeGenJetVarList, GenBJet[:20]     )
        fill_vector_collection( event, "GenJets",      writeGenJetVarList, GenJet[:20]      )
        fill_vector_collection( event, "GenTop",      writeGenVarList,    GenTop[:20]      )
        
        event.nGenElectron = len(GenElectron)
        event.nGenMuon     = len(GenMuon)
        event.nGenPhoton   = len(GenPhoton)
        event.nGenBJet     = len(GenBJet)
        event.nGenJets     = len(GenJet)
        event.nGenTop      = len(GenTop)

        # can't find jets from W in gParts, so assume non-Leptonic W decays are hadronic W decays
        event.nGenW            = len(GenW) # all W from tops
        event.nGenWJets        = len(GenW)-len(GenLepWMother) # W -> q q
        event.nGenWElectron    = len(GenWElectron) # W -> e nu
        event.nGenWMuon        = len(GenWMuon) # W -> mu nu
        event.nGenWTau         = len(GenWTau) # W -> tau nu
        event.nGenWTauJets     = len(GenWTau)-len(GenLepTauMother) # W -> tau nu, tau -> q q nu
        event.nGenWTauElectron = len(GenTauElectron) # W -> tau nu, tau -> e nu nu
        event.nGenWTauMuon     = len(GenTauMuon) # W -> tau nu, tau -> mu nu nu


    elif isData:
        event.overlapRemoval = 1 # all other events
        event.weight     = 1.
        event.ref_weight = 1.
        # lumi lists and vetos
        event.jsonPassed  = lumiList.contains( r.run, r.luminosityBlock )
        # make data weight zero if JSON was not passed
        if not event.jsonPassed: event.weight = 0
        # store decision to use after filler has been executed
        event.jsonPassed_ = event.jsonPassed
        event.overlapRemoval = 1 # No OR for data

    else:
        raise NotImplementedError( "isMC %r isData %r " % (isMC, isData) )

    # Leptons
    allElectrons = getParticles( r, readElectronVarList, coll="Electron" )
    allMuons     = getParticles( r, readMuonVarList,     coll="Muon" )

    allElectrons.sort( key = lambda l: -l['pt'] )
    allMuons.sort( key = lambda l: -l['pt'] )

    # Photons
    allPhotons = getParticles( r, readPhotonVarList, coll="Photon" )
    allPhotons.sort( key = lambda g: -g['pt'] )
    convertUnits( allPhotons )

    addMissingVariables( allElectrons, readLeptonVariables )
    addMissingVariables( allMuons,     readLeptonVariables )

    addCorrRelIso( allElectrons, allMuons, allPhotons )

    convertUnits( allElectrons )
    convertUnits( allMuons )

    vetoMuons     = list( filter( lambda l: recoMuonSel_veto(l),     allMuons ) )


    # similar to Ghent, remove electrons in dR<0.02 to muons
    allElectrons = deltaRCleaning( allElectrons, vetoMuons, dRCut=0.02 )

    allLeptons = allElectrons + allMuons
    allLeptons.sort( key = lambda l: -l['pt'] )

    # Veto electrons with corrected relIso
    vetoCorrIsoElectrons = filter( lambda l: recoElectronSel_veto(l, removedCuts=["pfRelIso03_all"]), allElectrons )
    vetoCorrIsoElectrons = filter( lambda l: l["pfRelIso03_all_corr"] <= getElectronIsoCutV2( l["pt"], l["eta"]+l["deltaEtaSC"], id="veto" ), vetoCorrIsoElectrons )

    # Filter leptons
    vetoElectrons = list( filter( lambda l: recoElectronSel_veto(l), allElectrons ) )
    vetoLeptons   = vetoElectrons + vetoMuons
    vetoLeptons.sort( key = lambda l: -l['pt'] )

    mediumElectrons = list( filter( lambda l: recoElectronSel_medium(l), allElectrons ) )
    mediumMuons     = list( filter( lambda l: recoMuonSel_medium(l),     allMuons ) )
    mediumLeptons   = mediumElectrons + mediumMuons
    mediumLeptons.sort( key = lambda l: -l['pt'] )

    mediumLeadingElectrons = list( filter( lambda l: recoElectronSel_medium(l, leading=True), mediumElectrons ) )
    mediumLeadingMuons     = list( filter( lambda l: recoMuonSel_medium(l, leading=True),     mediumMuons ) )
    mediumLeadingLeptons   = mediumLeadingElectrons + mediumLeadingMuons
    mediumLeadingLeptons.sort( key = lambda l: -l['pt'] )

    tight2lElectrons        = list( filter( lambda l: recoElectronSel_tight2l(l), allElectrons ) )
    tight2lLeadingElectrons = list( filter( lambda l: recoElectronSel_tight2l(l, leading=True), tight2lElectrons ) )
    leptons2l               = tight2lElectrons        + mediumMuons
    leadingLeptons2l        = tight2lLeadingElectrons + mediumLeadingMuons
    leptons2l.sort(        key = lambda l: -l['pt'] )
    leadingLeptons2l.sort( key = lambda l: -l['pt'] )

    tightElectrons = list( filter( lambda l: recoElectronSel_tight(l), allElectrons ) )
    tightMuons     = list( filter( lambda l: recoMuonSel_tight(l),     allMuons ) )
    tightLeptons   = tightElectrons + tightMuons
    tightLeptons.sort( key = lambda l: -l['pt'] )

    tightNoIsoElectrons = list( filter( lambda l: recoElectronSel_tight(l, removedCuts=["pfRelIso03_all"]), allElectrons ) )
    tightNoIsoMuons     = list( filter( lambda l: recoMuonSel_tight(l,     removedCuts=["pfRelIso04_all"]), allMuons ) )
    tightNoIsoLeptons   = tightNoIsoElectrons + tightNoIsoMuons
    tightNoIsoLeptons.sort( key = lambda l: -l['pt'] )

    tightInvIsoElectrons = list( filter( lambda l: l["pfRelIso03_all"]>getElectronIsoCutV2( l["pt"], l["eta"]+l["deltaEtaSC"], id="tight" ), tightNoIsoElectrons) )
    tightInvIsoMuons     = list( filter( lambda l: l["pfRelIso04_all"]>muonRelIsoCut, tightNoIsoMuons ) )
    tightInvIsoLeptons   = tightInvIsoElectrons + tightInvIsoMuons
    tightInvIsoLeptons.sort( key = lambda l: -l['pt'] )

    # tight leptons with inverted loose rel iso cut
    looseInvIsoElectrons = list( filter( lambda l: l["pfRelIso03_all"]>getElectronIsoCutV2( l["pt"], l["eta"]+l["deltaEtaSC"], id="loose" ), tightNoIsoElectrons) )
    looseInvIsoMuons     = list( filter( lambda l: l["pfRelIso04_all"]>muonRelIsoCutVeto, tightNoIsoMuons ) )
    looseInvIsoLeptons   = tightInvIsoElectrons + tightInvIsoMuons
    looseInvIsoLeptons.sort( key = lambda l: -l['pt'] )

    # tight leptons with inverted veto rel iso cut
    vetoInvIsoElectrons = list( filter( lambda l: l["pfRelIso03_all"]>getElectronIsoCutV2( l["pt"], l["eta"]+l["deltaEtaSC"], id="veto" ), tightNoIsoElectrons) )
    vetoInvIsoMuons     = list( filter( lambda l: l["pfRelIso04_all"]>muonRelIsoCutVeto, tightNoIsoMuons ) )
    vetoInvIsoLeptons   = tightInvIsoElectrons + tightInvIsoMuons
    vetoInvIsoLeptons.sort( key = lambda l: -l['pt'] )

    # Store lepton number
    event.nLepton           = len(allLeptons)
    event.nElectron         = len(allElectrons)
    event.nMuon             = len(allMuons)

    event.nLeptonVeto       = len(vetoLeptons)
    event.nElectronVeto     = len(vetoElectrons)
    event.nMuonVeto         = len(vetoMuons)

    event.nLeptonVetoIsoCorr   = len(vetoCorrIsoElectrons) + len(vetoMuons)
    event.nElectronVetoIsoCorr = len(vetoCorrIsoElectrons)

    event.nLeptonMedium     = len(mediumLeptons)
    event.nElectronMedium   = len(mediumElectrons)
    event.nMuonMedium       = len(mediumMuons)

    # good == 2l analysis
    event.nLeptonGood       = len(leptons2l)
    event.nElectronGood     = len(tight2lElectrons)
    event.nMuonGood         = len(mediumMuons)

    event.nLeptonGoodLead   = len(leadingLeptons2l)
    event.nElectronGoodLead = len(tight2lLeadingElectrons)
    event.nMuonGoodLead     = len(mediumLeadingMuons)

    event.nLeptonTight      = len(tightLeptons)
    event.nElectronTight    = len(tightElectrons)
    event.nMuonTight        = len(tightMuons)

    event.nLeptonTightNoIso   = len(tightNoIsoLeptons)
    event.nElectronTightNoIso = len(tightNoIsoElectrons)
    event.nMuonTightNoIso     = len(tightNoIsoMuons)

    event.nLeptonTightInvIso   = len(tightInvIsoLeptons)
    event.nElectronTightInvIso = len(tightInvIsoElectrons)
    event.nMuonTightInvIso     = len(tightInvIsoMuons)

    event.nLeptonTightInvIsoLoose   = len(looseInvIsoLeptons)
    event.nElectronTightInvIsoLoose = len(looseInvIsoElectrons)
    event.nMuonTightInvIsoLoose     = len(looseInvIsoMuons)

    event.nLeptonTightInvIsoVeto   = len(vetoInvIsoLeptons)
    event.nElectronTightInvIsoVeto = len(vetoInvIsoElectrons)
    event.nMuonTightInvIsoVeto     = len(vetoInvIsoMuons)

    # Select one tight and one medium lepton, the tight is included in the medium collection
    selectedLeptons           = leptons2l[:2]
    selectedTightLepton       = tightLeptons[:1]
    selectedInvIsoTightLepton = tightInvIsoLeptons[:1]

    # Store analysis Leptons + 2 default Leptons for a faster plotscript
    l0, l1         = ( selectedLeptons    + [None,None] )[:2]
    lt0, lt1       = ( tightLeptons       + [None,None] )[:2]
    ltinv0, ltinv1 = ( tightInvIsoLeptons + [None,None] )[:2]
    # Dileptonic analysis
    fill_vector( event, "LeptonGood0",  writeLeptonVarList, l0 )
    fill_vector( event, "LeptonGood1",  writeLeptonVarList, l1 )
    # Semi-leptonic analysis
    fill_vector( event, "LeptonTight0", writeLeptonVarList, lt0 )
    fill_vector( event, "LeptonTight1", writeLeptonVarList, lt1 )
    fill_vector( event, "LeptonTightInvIso0", writeLeptonVarList, ltinv0 )
    # Store all Leptons
    fill_vector_collection( event, "Lepton", writeLeptonVarList, allLeptons )

    # Photons
    if isMC:
        gPart.sort(key=lambda x: x["index"])
        # match photon with gen-particle and get its photon category -> reco Photon categorization
        for g in allPhotons:
#            g["genPartIdx"] = getGenPartIdx( g, gPart, coneSize=0.4, ptCut=5., excludedPdgIds=[ 12, -12, 14, -14, 16, -16 ] )
            genMatch = filter( lambda p: p['index'] == g['genPartIdx'], gPart )[0] if g['genPartIdx'] >= 0 else None
#            g['photonCat']    = getPhotonCategory( genMatch, gPart ) if g['genPartIdx'] != -2 else 4 # magic photons
            g['photonCat']    = getAdvancedPhotonCategory( g, gPart, coneSize=0.2, ptCut=5., excludedPdgIds=[ 12, -12, 14, -14, 16, -16 ] )
            g['leptonMother'] = hasLeptonMother( genMatch, gPart )
            g['mother']       = getPhotonMother( genMatch, gPart )
    else:
        for g in allPhotons:
            g['photonCat']    = -1
            g['leptonMother'] = -1
            g['mother']       = -1

    mediumPhotons                = list( filter( lambda g: recoPhotonSel_medium(g),                                          allPhotons ) )
    mvaPhotons                   = list( filter( lambda g: recoPhotonSel_mva(g),                                             allPhotons ) )
    mediumPhotonsNoChgIso        = list( filter( lambda g: recoPhotonSel_medium(g, removedCuts=["pfRelIso03_chg"]),          allPhotons ) )
    mediumPhotonsNoSieie         = list( filter( lambda g: recoPhotonSel_medium(g, removedCuts=["sieie"]),                   allPhotons ) )
    mediumPhotonsNoChgIsoNoSieie = list( filter( lambda g: recoPhotonSel_medium(g, removedCuts=["pfRelIso03_chg", "sieie"]), allPhotons ) )


    # DeltaR cleaning
    mediumPhotons                = deltaRCleaning( mediumPhotons,                selectedLeptons if isDiLep else selectedTightLepton, dRCut=0.1 )
    mvaPhotons                   = deltaRCleaning( mvaPhotons,                   selectedLeptons if isDiLep else selectedTightLepton, dRCut=0.1 )
    mediumPhotonsNoChgIso        = deltaRCleaning( mediumPhotonsNoChgIso,        selectedLeptons if isDiLep else selectedTightLepton, dRCut=0.1 )
    mediumPhotonsNoSieie         = deltaRCleaning( mediumPhotonsNoSieie,         selectedLeptons if isDiLep else selectedTightLepton, dRCut=0.1 )
    mediumPhotonsNoChgIsoNoSieie = deltaRCleaning( mediumPhotonsNoChgIsoNoSieie, selectedLeptons if isDiLep else selectedTightLepton, dRCut=0.1 )

    # misID electrons
    if mediumPhotons and allLeptons:
        misIdElectron = filter( lambda l: l["index"]==mediumPhotons[0]["electronIdx"], allElectrons ) + [None]
        fill_vector( event, "MisIDElectron0", writeLeptonVarList, misIdElectron[0] )

    # Jets
    allJets  = getParticles( r, collVars=readJetVarList, coll="Jet" )
    nHEMJets = len( filter( lambda j:j['pt']>20 and j['eta']>-3.2 and j['eta']<-1.0 and j['phi']>-2.0 and j['phi']<-0.5, allJets ))

    if isMC and not options.skipSF:
        for j in allJets: BTagEff.addBTagEffToJet( j )

    # Loose jets w/o pt/eta requirement
    allGoodJets = list( filter( lambda j: recoJetSel(j, ptVar=ptVar, removedCuts=["pt", "eta"]), allJets ) )
    addJetFlags( allGoodJets, selectedLeptons if isDiLep else selectedTightLepton, mediumPhotons )
    # Loose jets w/ pt/eta requirement (analysis jets)
    jets    = list( filter( lambda x: x["isGood"], allGoodJets ) )

    # DeltaR cleaning (now done in "isGood"
#    jets = deltaRCleaning( jets, selectedLeptons if isDiLep else selectedTightLepton, dRCut=0.4 ) # clean all jets against analysis leptons
#    jets = deltaRCleaning( jets, mediumPhotons, dRCut=0.1 ) # clean all jets against analysis photons
    

    # Store jets
    event.nJet      = len(allGoodJets)
    event.nJetGood  = len(jets)

    # get nJet for jets cleaned against photons with relaxed cuts
    goodJets                = list( filter( lambda j: recoJetSel(j, ptVar=ptVar), allGoodJets ) )
    goodJets                = deltaRCleaning( goodJets, selectedLeptons if isDiLep else selectedTightLepton, dRCut=0.4 ) # clean all jets against analysis leptons
    goodMVAJets             = deltaRCleaning( goodJets, mvaPhotons, dRCut=0.1 ) 
    goodNoChgIsoJets        = deltaRCleaning( goodJets, mediumPhotonsNoChgIso, dRCut=0.1 ) 
    goodNoSieieJets         = deltaRCleaning( goodJets, mediumPhotonsNoSieie, dRCut=0.1 ) 
    goodNoChgIsoNoSieieJets = deltaRCleaning( goodJets, mediumPhotonsNoChgIsoNoSieie, dRCut=0.1 ) 
    goodJets                = deltaRCleaning( goodJets, mediumPhotons, dRCut=0.1 ) 

    event.nJetGoodMVA             = len(goodMVAJets)
    event.nJetGoodNoChgIso        = len(goodNoChgIsoJets)
    event.nJetGoodNoSieie         = len(goodNoSieieJets)
    event.nJetGoodNoChgIsoNoSieie = len(goodNoChgIsoNoSieieJets)

    # store all loose jets
    fill_vector_collection( event, "Jet", writeJetVarList, allGoodJets)

    # Store analysis jets + 2 default jets for a faster plotscript
    j0, j1   = ( jets + [None,None] )[:2]
    # Dileptonic analysis
    fill_vector( event, "JetGood0",  writeJetVarList, j0 )
    fill_vector( event, "JetGood1",  writeJetVarList, j1 )

    # bJets
    allBJets = list( filter( lambda x: x["isBJet"], allGoodJets ) )
    bJets    = list( filter( lambda x: x["isBJet"], jets ) )
    nonBJets = list( filter( lambda x: not x["isBJet"], jets ) )

    # Store bJets + 2 default bjets for a faster plot script
    bj0, bj1 = ( list(bJets) + [None,None] )[:2]
    fill_vector( event, "Bj0", writeBJetVarList, bj0 )
    fill_vector( event, "Bj1", writeBJetVarList, bj1 )

    event.nBTag      = len(allBJets)
    event.nBTagGood  = len(bJets)

    # get nBTag for bjets cleaned against photons with relaxed cuts
    event.nBTagGoodMVA             = len( filter( lambda x: x["isBJet"], goodMVAJets ) )
    event.nBTagGoodNoChgIso        = len( filter( lambda x: x["isBJet"], goodNoChgIsoJets ) )
    event.nBTagGoodNoSieie         = len( filter( lambda x: x["isBJet"], goodNoSieieJets ) )
    event.nBTagGoodNoChgIsoNoSieie = len( filter( lambda x: x["isBJet"], goodNoChgIsoNoSieieJets ) )

    # store the correct MET (EE Fix for 2017, MET_min as backup in 2017)
    if options.year == 2017 and not options.skipNanoTools:
        # v2 recipe. Could also use our own recipe
        event.MET_pt     = r.METFixEE2017_pt
        event.MET_phi    = r.METFixEE2017_phi
        event.MET_pt_min = r.MET_pt_min
    elif not options.skipNanoTools:
        event.MET_pt     = r.MET_pt_nom
        event.MET_phi    = r.MET_phi_nom
        event.MET_pt_min = 0
    else:
        event.MET_pt     = r.MET_pt
        event.MET_phi    = r.MET_phi
        event.MET_pt_min = 0

    # Additional observables
    event.m3          = m3( jets )[0]
    event.m3wBJet     = m3( jets, nBJets=1, tagger=tagger, year=options.year )[0]
    if len(mediumPhotons) > 0:
        event.m3gamma = m3( jets, photon=mediumPhotons[0] )[0]

    event.ht = sum( [ j[ptVar] for j in jets ] )
    if event.ht > 0:
        event.METSig = event.MET_pt / sqrt( event.ht )

    # variables w/ photons
    if len(mediumPhotons) > 0:

#        if isMC:
#            # match photon with gen-particle and get its photon category -> reco Photon categorization
#            for g in mediumPhotons:
#                genMatch = filter( lambda p: p['index'] == g['genPartIdx'], gPart )[0] if g['genPartIdx'] > 0 and isMC else None
#                g['photonCat'] = getPhotonCategory( genMatch, gPart )

        # additional observables
        event.MET_pt_photonEstimated, event.MET_phi_photonEstimated = getMetPhotonEstimated( event.MET_pt, event.MET_phi, mediumPhotons[0] )

        if event.ht > 0:
            event.METSig_photonEstimated = event.MET_pt_photonEstimated / sqrt( event.ht )

        if jets:
            event.photonJetdR = min( deltaR( p, j ) for j in jets for p in mediumPhotons )

        if selectedLeptons:
            event.photonLepdR = min( deltaR( p, l ) for l in selectedLeptons for p in mediumPhotons )

        if len(tightLeptons) > 0:
            event.ltight0GammadPhi = deltaPhi( tightLeptons[0]['phi'], mediumPhotons[0]['phi'] )
            event.ltight0GammadR   = deltaR(   tightLeptons[0],        mediumPhotons[0] )
            event.mLtight0Gamma    = ( get4DVec(tightLeptons[0]) + get4DVec(mediumPhotons[0]) ).M()

        if len(tightInvIsoLeptons) > 0:
            event.linvtight0GammadPhi = deltaPhi( tightInvIsoLeptons[0]['phi'], mediumPhotons[0]['phi'] )
            event.linvtight0GammadR   = deltaR(   tightInvIsoLeptons[0],        mediumPhotons[0] )
            event.mLinvtight0Gamma    = ( get4DVec(tightInvIsoLeptons[0]) + get4DVec(mediumPhotons[0]) ).M()

        if len(selectedLeptons) > 0:
            event.l0GammadPhi = deltaPhi( selectedLeptons[0]['phi'], mediumPhotons[0]['phi'] )
            event.l0GammadR   = deltaR(   selectedLeptons[0],        mediumPhotons[0] )
            event.mL0Gamma    = ( get4DVec(selectedLeptons[0]) + get4DVec(mediumPhotons[0]) ).M()

        if len(selectedLeptons) > 1:
            event.l1GammadPhi = deltaPhi( selectedLeptons[1]['phi'], mediumPhotons[0]['phi'] )
            event.l1GammadR   = deltaR(   selectedLeptons[1],        mediumPhotons[0] )
            event.mL1Gamma    = ( get4DVec(selectedLeptons[1]) + get4DVec(mediumPhotons[0]) ).M()

        if len(jets) > 0:
            event.j0GammadPhi = deltaPhi( jets[0]['phi'], mediumPhotons[0]['phi'] )
            event.j0GammadR   = deltaR(   jets[0],        mediumPhotons[0] )

        if len(jets) > 1:
            event.j1GammadPhi = deltaPhi( jets[1]['phi'], mediumPhotons[0]['phi'] )
            event.j1GammadR   = deltaR(   jets[1],        mediumPhotons[0] )

    event.nPhoton                = len( allPhotons )
    event.nPhotonGood            = len( mediumPhotons )
    event.nPhotonMVA             = len( mvaPhotons )
    event.nPhotonNoChgIso        = len( mediumPhotonsNoChgIso )
    event.nPhotonNoSieie         = len( mediumPhotonsNoSieie )
    event.nPhotonNoChgIsoNoSieie = len( mediumPhotonsNoChgIsoNoSieie )

    # store all photons + default photons for a faster plot script
    fill_vector_collection( event, "Photon", writePhotonVarList, allPhotons[:20] )

    # Store analysis photons + default photons for a faster plot script
    p0, p1 = ( mediumPhotons + [None,None] )[:2]
    fill_vector( event, "PhotonGood0",  writePhotonVarList, p0 )
    fill_vector( event, "PhotonGood1",  writePhotonVarList, p1 )

    p0mva = ( mvaPhotons + [None] )[0]
    fill_vector( event, "PhotonMVA0",  writePhotonVarList, p0mva )

    p0NoChgIsoNoSieie = ( mediumPhotonsNoChgIsoNoSieie + [None] )[0]
    fill_vector( event, "PhotonNoChgIsoNoSieie0",  writePhotonVarList, p0NoChgIsoNoSieie )

    p0NoSieie = ( mediumPhotonsNoSieie + [None] )[0]
    fill_vector( event, "PhotonNoSieie0",  writePhotonVarList, p0NoSieie )

    p0NoChgIso = ( mediumPhotonsNoChgIso + [None] )[0]
    fill_vector( event, "PhotonNoChgIso0", writePhotonVarList, p0NoChgIso )

    if bj1:
        event.bbdR   = deltaR( bj0, bj1 )
        event.bbdPhi = deltaPhi( bj0['phi'], bj1['phi'] )

    if len(tightLeptons) > 1:
        event.lldRtight   = deltaR( tightLeptons[0], tightLeptons[1] )
        event.lldPhitight = deltaPhi( tightLeptons[0]['phi'], tightLeptons[1]['phi'] )
        event.mlltight    = ( get4DVec(tightLeptons[0]) + get4DVec(tightLeptons[1]) ).M()

        if len(mediumPhotons) > 0:
            event.mllgammatight = ( get4DVec(tightLeptons[0]) + get4DVec(tightLeptons[1]) + get4DVec(mediumPhotons[0]) ).M()

    if len(jets) > 0 and len(tightLeptons) > 0:
        event.tightLeptonJetdR = min( deltaR( tightLeptons[0], j ) for j in jets )

    if len(jets) > 0 and len(tightInvIsoLeptons) > 0:
        event.invtightLeptonJetdR = min( deltaR( tightInvIsoLeptons[0], j ) for j in jets )

    if len(selectedLeptons) > 1:
        event.lldR   = deltaR( selectedLeptons[0], selectedLeptons[1] )
        event.lldPhi = deltaPhi( selectedLeptons[0]['phi'], selectedLeptons[1]['phi'] )
        event.mll    = ( get4DVec(selectedLeptons[0]) + get4DVec(selectedLeptons[1]) ).M()

        if len(mediumPhotons) > 0:
            event.mllgamma = ( get4DVec(selectedLeptons[0]) + get4DVec(selectedLeptons[1]) + get4DVec(mediumPhotons[0]) ).M()
        if p0mva:
            event.mllgammaMVA = ( get4DVec(selectedLeptons[0]) + get4DVec(selectedLeptons[1]) + get4DVec(p0mva) ).M()
        if p0NoChgIso:
            event.mllgammaNoChgIso = ( get4DVec(selectedLeptons[0]) + get4DVec(selectedLeptons[1]) + get4DVec(p0NoChgIso) ).M()
        if p0NoSieie:
            event.mllgammaNoSieie = ( get4DVec(selectedLeptons[0]) + get4DVec(selectedLeptons[1]) + get4DVec(p0NoSieie) ).M()
        if p0NoChgIsoNoSieie:
            event.mllgammaNoChgIsoNoSieie = ( get4DVec(selectedLeptons[0]) + get4DVec(selectedLeptons[1]) + get4DVec(p0NoChgIsoNoSieie) ).M()

    if len(jets) > 0 and len(selectedLeptons) > 0:
        event.leptonJetdR = min( deltaR( l, j ) for j in jets for l in selectedLeptons )

    met = {'pt':event.MET_pt, 'phi':event.MET_phi}

    if len(tightLeptons) > 0:
        event.lpTight = lp( tightLeptons[0]["pt"], tightLeptons[0]["phi"], met["pt"], met["phi"] )
        event.mT      = mT( tightLeptons[0], met )

    if len(tightInvIsoLeptons) > 0:
        event.lpInvTight = lp( tightInvIsoLeptons[0]["pt"], tightInvIsoLeptons[0]["phi"], met["pt"], met["phi"] )
        event.mTinv      = mT( tightInvIsoLeptons[0], met )

    mt2Calculator.reset()
    mt2Calculator.setMet( met["pt"], met["phi"] )
    if len(tightInvIsoLeptons) > 0 and len(mediumPhotons) > 0:
        mt2Calculator.setLepton1( tightInvIsoLeptons[0]["pt"], tightInvIsoLeptons[0]["eta"], tightInvIsoLeptons[0]["phi"] )
        mt2Calculator.setLepton2( mediumPhotons[0]["pt"], mediumPhotons[0]["eta"], mediumPhotons[0]["phi"] )
        event.mT2linvg   = mt2Calculator.mt2ll()
    if len(tightLeptons) > 0 and len(mediumPhotons) > 0:
        mt2Calculator.setLepton1( tightLeptons[0]["pt"], tightLeptons[0]["eta"], tightLeptons[0]["phi"] )
        mt2Calculator.setLepton2( mediumPhotons[0]["pt"], mediumPhotons[0]["eta"], mediumPhotons[0]["phi"] )
        event.mT2lg   = mt2Calculator.mt2ll()
    if len(selectedLeptons) > 1:
        mt2Calculator.setLepton1( selectedLeptons[0]["pt"], selectedLeptons[0]["eta"], selectedLeptons[0]["phi"] )
        mt2Calculator.setLepton2( selectedLeptons[1]["pt"], selectedLeptons[1]["eta"], selectedLeptons[1]["phi"] )
        event.mT2ll   = mt2Calculator.mt2ll()
        if bj1:
            mt2Calculator.setBJet1( bj0["pt"], bj0["eta"], bj0["phi"] )
            mt2Calculator.setBJet2( bj1["pt"], bj1["eta"], bj1["phi"] )
            event.mT2bb   = mt2Calculator.mt2bb()
            event.mT2blbl = mt2Calculator.mt2blbl()

    jets_sys      = {}
    bjets_sys     = {}
    nonBjets_sys  = {}

    if addSystematicVariations and not options.skipNanoTools and not options.skipSF:
        jets_sys["jesTotalUp"]   = filter(lambda j: recoJetSel(j, ptVar="pt_jesTotalUp")   and j["clean"], allGoodJets)
        jets_sys["jesTotalDown"] = filter(lambda j: recoJetSel(j, ptVar="pt_jesTotalDown") and j["clean"], allGoodJets)
        jets_sys["jerUp"]        = filter(lambda j: recoJetSel(j, ptVar="pt_jerUp")        and j["clean"], allGoodJets)
        jets_sys["jerDown"]      = filter(lambda j: recoJetSel(j, ptVar="pt_jerDown")      and j["clean"], allGoodJets)
        for var in ['jesTotalUp', 'jesTotalDown', 'jerUp', 'jerDown']:
            setattr(event, 'MET_pt_'+var, getattr(r, 'METFixEE2017_pt_'+var) if options.year == 2017 else getattr(r, 'MET_pt_'+var) )
            bjets_sys[var]      = filter(lambda j: j["isBJet"], jets_sys[var])
            nonBjets_sys[var]   = filter(lambda j: not j["isBJet"], jets_sys[var])

            setattr(event, "nJetGood_"+var,  len(jets_sys[var]))
            setattr(event, "ht_"+var,        sum([j['pt_'+var] for j in jets_sys[var]]))
            setattr(event, "nBTagGood_"+var, len(bjets_sys[var]))

        for var in ['jesTotalUp', 'jesTotalDown', 'jerUp', 'jerDown', 'unclustEnUp', 'unclustEnDown']:
            for i in ["", "_photonEstimated"]:
                # use cmg MET correction values ecept for JER where it is zero. There, propagate jet variations.
                if 'jer' in var or 'jes' in var:
                  (MET_corr_pt, MET_corr_phi) = getMetJetCorrected(getattr(event, "MET_pt" + i), getattr(event,"MET_phi" + i), allJets, var, ptVar=ptVar)
                else:
                  (MET_corr_pt, MET_corr_phi) = getMetCorrected(r, var, mediumPhotons[0] if i.count("photonEstimated") and len(mediumPhotons) else None)

                setattr(event, "MET_pt" +i+"_"+var, MET_corr_pt)
                setattr(event, "MET_phi"+i+"_"+var, MET_corr_phi)
                ht = getattr(event, "ht_"+var) if 'unclust' not in var else event.ht
                setattr(event, "METSig" +i+"_"+var, getattr(event, "MET_pt"+i+"_"+var)/sqrt( ht ) if ht>0 else float('nan') )

    # Topreco
    if options.topReco:
        #topReco = TopReco( ROOT.Era.run2_13tev_2016_25ns, 2, 1, 0, 'btagDeepB', 0.6321 )
        solution = topReco.evaluate( selectedLeptons, jets, met = met)
        if solution:
            event.topReco_nBTag   = solution.ntags
            event.topReco_weight  = solution.weight
            event.topReco_recMtop = solution.recMtop
            event.topReco_met_pt  = solution.met.Pt()
            event.topReco_met_phi = solution.met.Phi()
            
            setParticle(event, "lp",             solution.lp) 
            setParticle(event, "lm",             solution.lm) 
            setParticle(event, "jetB",           solution.jetB) 
            setParticle(event, "jetBbar",        solution.jetBbar) 
            setParticle(event, "Wp",             solution.Wplus) 
            setParticle(event, "Wm",             solution.Wminus) 
            setParticle(event, "neutrino",       solution.neutrino) 
            setParticle(event, "neutrinoBar",    solution.neutrinoBar) 
            setParticle(event, "top",            solution.top) 
            setParticle(event, "topBar",         solution.topBar) 

    if isData:
        event.reweightHEM = (r.run>=319077 and nHEMJets==0) or r.run<319077
    else:
        event.reweightHEM = 1 if (nHEMJets==0 or options.year != 2018 ) else 0.3518 # 0.2% of Run2018B are HEM affected. Ignore that piece. Thus, if there is a HEM jet, scale the MC to 35.2% which is AB/ABCD

    # Reweighting
    if isMC and not options.skipSF:
        # PU reweighting
        event.reweightPU      = nTrueInt_puRW      ( r.Pileup_nTrueInt )
        event.reweightPUDown  = nTrueInt_puRWDown  ( r.Pileup_nTrueInt )
        event.reweightPUUp    = nTrueInt_puRWUp    ( r.Pileup_nTrueInt )
        event.reweightPUVDown = nTrueInt_puRWVDown ( r.Pileup_nTrueInt )
        event.reweightPUVUp   = nTrueInt_puRWVUp   ( r.Pileup_nTrueInt )

        # Lepton reweighting
        reweight2l      = [ LeptonSFMedium.getSF( pdgId=l['pdgId'], pt=l['pt'], eta=((l['eta']+l['deltaEtaSC']) if abs(l['pdgId'])==11 else l['eta']) ) for l in mediumMuons ]
        reweight2l     += [ LeptonSFTight.getSF( pdgId=l['pdgId'], pt=l['pt'], eta=((l['eta']+l['deltaEtaSC']) if abs(l['pdgId'])==11 else l['eta']) ) for l in tight2lElectrons ]
        reweight2lUp    = [ LeptonSFMedium.getSF( pdgId=l['pdgId'], pt=l['pt'], eta=((l['eta']+l['deltaEtaSC']) if abs(l['pdgId'])==11 else l['eta']), sigma = +1 ) for l in mediumMuons ]
        reweight2lUp   += [ LeptonSFTight.getSF( pdgId=l['pdgId'], pt=l['pt'], eta=((l['eta']+l['deltaEtaSC']) if abs(l['pdgId'])==11 else l['eta']), sigma = +1 ) for l in tight2lElectrons ]
        reweight2lDown  = [ LeptonSFMedium.getSF( pdgId=l['pdgId'], pt=l['pt'], eta=((l['eta']+l['deltaEtaSC']) if abs(l['pdgId'])==11 else l['eta']), sigma = -1 ) for l in mediumMuons ]
        reweight2lDown += [ LeptonSFTight.getSF( pdgId=l['pdgId'], pt=l['pt'], eta=((l['eta']+l['deltaEtaSC']) if abs(l['pdgId'])==11 else l['eta']), sigma = -1 ) for l in tight2lElectrons ]
        event.reweightLepton2lSF     = reduce( mul, reweight2l, 1 )
        event.reweightLepton2lSFUp   = reduce( mul, reweight2lUp, 1 )
        event.reweightLepton2lSFDown = reduce( mul, reweight2lDown, 1 )

        event.reweightLeptonTightSF     = reduce( mul, [ LeptonSFTight.getSF( pdgId=l['pdgId'], pt=l['pt'], eta=((l['eta']+l['deltaEtaSC']) if abs(l['pdgId'])==11 else l['eta'])             ) for l in selectedTightLepton ], 1 )
        event.reweightLeptonTightSFUp   = reduce( mul, [ LeptonSFTight.getSF( pdgId=l['pdgId'], pt=l['pt'], eta=((l['eta']+l['deltaEtaSC']) if abs(l['pdgId'])==11 else l['eta']), sigma = +1 ) for l in selectedTightLepton ], 1 )
        event.reweightLeptonTightSFDown = reduce( mul, [ LeptonSFTight.getSF( pdgId=l['pdgId'], pt=l['pt'], eta=((l['eta']+l['deltaEtaSC']) if abs(l['pdgId'])==11 else l['eta']), sigma = -1 ) for l in selectedTightLepton ], 1 )

        event.reweightLeptonTracking2lSF     = reduce( mul, [ LeptonTrackingSF.getSF( pdgId=l['pdgId'], pt=l['pt'], eta=((l['eta']+l['deltaEtaSC']) if abs(l['pdgId'])==11 else l['eta'])             ) for l in selectedLeptons ], 1 )
        event.reweightLeptonTracking2lSFUp   = reduce( mul, [ LeptonTrackingSF.getSF( pdgId=l['pdgId'], pt=l['pt'], eta=((l['eta']+l['deltaEtaSC']) if abs(l['pdgId'])==11 else l['eta']), sigma = +1 ) for l in selectedLeptons ], 1 )
        event.reweightLeptonTracking2lSFDown = reduce( mul, [ LeptonTrackingSF.getSF( pdgId=l['pdgId'], pt=l['pt'], eta=((l['eta']+l['deltaEtaSC']) if abs(l['pdgId'])==11 else l['eta']), sigma = -1 ) for l in selectedLeptons ], 1 )

        event.reweightLeptonTrackingTightSF     = reduce( mul, [ LeptonTrackingSF.getSF( pdgId=l['pdgId'], pt=l['pt'], eta=((l['eta']+l['deltaEtaSC']) if abs(l['pdgId'])==11 else l['eta'])             ) for l in selectedTightLepton ], 1 )
        event.reweightLeptonTrackingTightSFUp   = reduce( mul, [ LeptonTrackingSF.getSF( pdgId=l['pdgId'], pt=l['pt'], eta=((l['eta']+l['deltaEtaSC']) if abs(l['pdgId'])==11 else l['eta']), sigma = +1 ) for l in selectedTightLepton ], 1 )
        event.reweightLeptonTrackingTightSFDown = reduce( mul, [ LeptonTrackingSF.getSF( pdgId=l['pdgId'], pt=l['pt'], eta=((l['eta']+l['deltaEtaSC']) if abs(l['pdgId'])==11 else l['eta']), sigma = -1 ) for l in selectedTightLepton ], 1 )

        # Photon reweighting
        event.reweightPhotonSF     = reduce( mul, [ PhotonSF.getSF( pt=p['pt'], eta=p['eta']             ) for p in mediumPhotons ], 1 )
        event.reweightPhotonSFUp   = reduce( mul, [ PhotonSF.getSF( pt=p['pt'], eta=p['eta'], sigma = +1 ) for p in mediumPhotons ], 1 )
        event.reweightPhotonSFDown = reduce( mul, [ PhotonSF.getSF( pt=p['pt'], eta=p['eta'], sigma = -1 ) for p in mediumPhotons ], 1 )

        event.reweightPhotonElectronVetoSF     = reduce( mul, [ PhotonElectronVetoSF.getSF( pt=p['pt'], eta=p['eta']             ) for p in mediumPhotons ], 1 )
        event.reweightPhotonElectronVetoSFUp   = reduce( mul, [ PhotonElectronVetoSF.getSF( pt=p['pt'], eta=p['eta'], sigma = +1 ) for p in mediumPhotons ], 1 )
        event.reweightPhotonElectronVetoSFDown = reduce( mul, [ PhotonElectronVetoSF.getSF( pt=p['pt'], eta=p['eta'], sigma = -1 ) for p in mediumPhotons ], 1 )
#        event.reweightPhotonReconstructionSF = reduce( mul, [ PhotonRecEff.getSF( pt=p['pt'], eta=p['eta'] )         for p in mediumPhotons ], 1 )

        # B-Tagging efficiency method 1a
        for var in BTagEff.btagWeightNames:
            if var!='MC': setattr( event, 'reweightBTag_'+var, BTagEff.getBTagSF_1a( var, bJets, nonBJets ) )

        if len(selectedLeptons) > 1:
            # Trigger reweighting
            trig_eff, trig_eff_err         = TriggerEff.getSF( selectedLeptons[0], selectedLeptons[1] )
            event.reweightDilepTrigger     = trig_eff
            event.reweightDilepTriggerUp   = trig_eff + trig_eff_err
            event.reweightDilepTriggerDown = trig_eff - trig_eff_err

            trig_eff, trig_eff_err               = TriggerEff_withBackup.getSF( selectedLeptons[0], selectedLeptons[1] )
            event.reweightDilepTriggerBackup     = trig_eff
            event.reweightDilepTriggerBackupUp   = trig_eff + trig_eff_err
            event.reweightDilepTriggerBackupDown = trig_eff - trig_eff_err

        else:
            event.reweightDilepTrigger     = 0
            event.reweightDilepTriggerUp   = 0
            event.reweightDilepTriggerDown = 0
            
            event.reweightDilepTriggerBackup     = 0
            event.reweightDilepTriggerBackupUp   = 0
            event.reweightDilepTriggerBackupDown = 0

        # PreFiring
        if options.year == 2018:
            event.reweightL1Prefire, event.reweightL1PrefireUp, event.reweightL1PrefireDown = 1., 1., 1.
        else:
            event.reweightL1Prefire, event.reweightL1PrefireUp, event.reweightL1PrefireDown = L1PW.getWeight( allPhotons, allJets )

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
copyLog = subprocess.call( [ 'cp', logFile, output_directory ] )
if copyLog:
    logger.info( "Copying log from %s to %s failed", logFile, output_directory )
else:
    logger.info( "Successfully copied log file" )
    os.remove( logFile )
    logger.info( "Removed temporary log file" )

# Copying output to DPM or AFS and check the files
if options.writeToDPM:

    for dirname, subdirs, files in os.walk( output_directory ):
        logger.debug( 'Found directory: %s',  dirname )

        for fname in files:

            if not fname.endswith(".root") or fname.startswith("nanoAOD_") or "_for_" in fname: continue # remove that for copying log files

            source  = os.path.abspath( os.path.join( dirname, fname ) )
            target  = os.path.join( targetPath, fname )

            if fname.endswith(".root"):
                if checkRootFile( source, checkForObjects=["Events"] ) and deepCheckRootFile( source ) and deepCheckWeight( source ):
                    logger.info( "Source: File check ok!" )
                else:
                    raise Exception("Corrupt rootfile at source! File not copied: %s"%source )

            cmd = [ 'xrdcp', '-f',  source, target ]
            logger.info( "Issue copy command: %s", " ".join( cmd ) )
            subprocess.call( cmd )

            if fname.endswith(".root"):
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
                        logger.info( "2nd try: No success, removing file: %s"%target )
                        logger.info( "Issue rm command: %s", " ".join( cmd ) )
                        cmd = [ "xrdfs", redirector_hephy, "rm", "/cms" + target.split("/cms")[1] ]
                        subprocess.call( cmd )
                        raise Exception("Corrupt rootfile at target! File not copied: %s"%source )

    # Clean up.
    if not options.runOnLxPlus:
        # not needed on condor, container will be removed automatically
        subprocess.call( [ 'rm', '-rf', output_directory ] ) # Let's risk it.

else:
    if checkRootFile( outputFilePath, checkForObjects=["Events"] ) and deepCheckRootFile( outputFilePath ) and deepCheckWeight( outputFilePath ):
        logger.info( "Target: File check ok!" )
    else:
        logger.info( "Corrupt rootfile! Removing file: %s"%outputFilePath )
        os.remove( outputFilePath )
        raise Exception("Corrupt rootfile! File not copied: %s"%outputFilePath )

# There is a double free corruption due to stupid ROOT memory management which leads to a non-zero exit code
# Thus the job is resubmitted on condor even if the output is ok
# Current idea is that the problem is with xrootd having a non-closed root file
# Let's see if this works...
sample.clear()
