#!/usr/bin/env python
''' Make flat ntuple from GEN data 
'''

# standard imports
import ROOT
import sys
import os
import subprocess
import shutil
import uuid

from math                                        import sqrt
from operator                                    import mul

# RootTools
from RootTools.core.standard                     import *

# User specific
import TTGammaEFT.Tools.user as user

# Tools for systematics
from TTGammaEFT.Tools.observables                import deltaR, deltaR2

from TTGammaEFT.Tools.genObjectSelection         import isGoodGenJet, isGoodGenLepton, isGoodGenPhoton
from TTGammaEFT.Tools.genObjectSelection         import genJetId

from TTGammaEFT.Tools.constants                  import defaultValue

from TTGammaEFT.Tools.WeightInfo                 import WeightInfo
from TTGammaEFT.Tools.HyperPoly                  import HyperPoly

from TTGammaEFT.Tools.GenSearch                  import GenSearch

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
    argParser.add_argument('--targetDir',                   action='store',         nargs='?',  type=str,                           default=user.postprocessing_output_directory, help="Name of the directory the post-processed files will be saved")
    argParser.add_argument('--processingEra',               action='store',         nargs='?',  type=str,                           default='TTGammaEFT_PP_v1',         help="Name of the processing era")
    argParser.add_argument('--small',                       action='store_true',                                                                                        help="Run the file on a small sample (for test purpose), bool flag set to True if used")
    argParser.add_argument('--addReweights',                action='store_true',                                                                                        help="Add reweights for sample EFT reweighting?")
    argParser.add_argument('--interpolationOrder',          action='store',         nargs='?',  type=int,                           default=2,                          help="Interpolation order for EFT weights.")

    return argParser

options = get_parser().parse_args()

# Logging
import TTGammaEFT.Tools.logger as logger
logFile = '/tmp/%s_%s_njob%s.txt'%('_'.join(options.samples), os.environ['USER'], str(0 if options.nJobs==1 else options.job) )
logger  = logger.get_logger(options.logLevel, logFile = logFile)

import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(options.logLevel, logFile = None )

#Samples: Load samples
maxN = None
if options.small:
    maxN = 1000
    options.job = 1
    options.nJobs = 100

# Load all samples to be post processed
from TTGammaEFT.Samples.genTuples_TTGamma import *
samples = map( eval, options.samples ) 
    
if len(samples)==0:
    logger.info( "No samples found. Was looking for %s. Exiting" % options.samples )
    sys.exit(-1)

elif len(samples)==1:
    sample = samples[0]

else:
    logger.info( "Combining samples not implemented yet. Exiting..." )
    sys.exit(-1)

# Cross section for postprocessed sample
xSection   = sample.xSection
nEvents    = sample.nEvents
lumiweight = xSection * 1000. / nEvents
pklFile    = sample.reweight_pkl

directory  = os.path.join( options.targetDir, options.processingEra ) 
postfix = '_small' if options.small else ''
output_directory = os.path.join( directory, "gen" + postfix, sample.name )

# Single file post processing
if options.nJobs>1:
    n_files_before = len(sample.files)
    sample = sample.split(options.nJobs)[options.job]
    n_files_after  = len(sample.files)
    logger.info( "Running job %i/%i over %i files from a total of %i.", options.job, options.nJobs, n_files_after, n_files_before)

if os.path.exists( output_directory ) and options.overwrite:
    if options.nJobs > 1:
        logger.warning( "NOT removing directory %s because nJobs = %i", output_directory, options.nJobs )
    else:
        logger.info( "Output directory %s exists. Deleting.", output_directory )
        shutil.rmtree( output_directory, ignore_errors=True )

if not os.path.exists( output_directory ):
    try:
        os.makedirs( output_directory )
        logger.info( "Created output directory %s.", output_directory )
    except:
        logger.info( "Directory %s already exists.", output_directory )
        pass

# Load reweight pickle file if supposed to keep weights. 
reweight_variables = []
if options.addReweights:

    # Determine coefficients for storing in vector
    # Sort Ids wrt to their position in the card file

    weightInfo = WeightInfo( pklFile )

    # weights for the ntuple
    rw_vector           = TreeVariable.fromString( "rw[w/F,"+",".join(w+'/F' for w in weightInfo.variables)+"]" )
    rw_vector.nMax      = weightInfo.nid
    reweight_variables += [ rw_vector ]

    # coefficients for the weight parametrization
    param_vector        = TreeVariable.fromString( "p[C/F]" )
    param_vector.nMax   = HyperPoly.get_ndof(weightInfo.nvar, options.interpolationOrder)
    hyperPoly           = HyperPoly( options.interpolationOrder )
    reweight_variables += [ param_vector ]
    reweight_variables += [ TreeVariable.fromString( "chi2_ndof/F" ) ]


genJetVarStringRead  = "pt/F,eta/F,phi/F,isMuon/I,isElectron/I,isPhoton/I"
genJetVarStringWrite = "matchBParton/I"
genJetVarStringWrite = genJetVarStringRead + "," + genJetVarStringWrite
genJetVars           = [ item.split("/")[0] for item in genJetVarStringWrite.split(",") ]
genJetVarsRead       = [ item.split("/")[0] for item in genJetVarStringRead.split(",") ]

genTopVarStringRead  = "pt/F,eta/F,phi/F,mass/F"
#genTopVarStringWrite = ""
genTopVarStringWrite = genTopVarStringRead# + "," + genTopVarStringWrite
genTopVars           = [ item.split("/")[0] for item in genTopVarStringWrite.split(",") ]

genLeptonVarStringRead  = "pt/F,eta/F,phi/F,pdgId/I"
genLeptonVarStringWrite = "motherPdgId/I,grandmotherPdgId/I"
genLeptonVarStringWrite = genLeptonVarStringRead + "," + genLeptonVarStringWrite
genLeptonVars           = [ item.split("/")[0] for item in genLeptonVarStringWrite.split(",") ]
genLeptonVarsRead       = [ item.split("/")[0] for item in genLeptonVarStringRead.split(",") ]

genPhotonVarStringRead  = "pt/F,phi/F,eta/F,mass/F"
genPhotonVarStringWrite = "motherPdgId/I,relIso04_all/F,photonLepdR/F,photonJetdR/F"
genPhotonVarStringWrite = genPhotonVarStringRead + "," + genPhotonVarStringWrite
genPhotonVars           = [ item.split("/")[0] for item in genPhotonVarStringWrite.split(",") ]
genPhotonVarsRead       = [ item.split("/")[0] for item in genPhotonVarStringRead.split(",") ]

# Write Variables
new_variables  = []#reweight_variables
new_variables += [ "run/I", "luminosity/I", "evt/l" ]
new_variables += [ "weight/F" ]
new_variables += [ "mll/F", "mllgamma/F" ]
new_variables += [ "nGenBJet/I" ]
new_variables += [ "nGenMuon/I" ]
new_variables += [ "nGenElectron/I" ]
new_variables += [ "GenMET_pt/F", "GenMET_phi/F" ]
new_variables += [ "GenLepton[%s]"   %genLeptonVarStringWrite ]
new_variables += [ "GenPhoton[%s]"   %genPhotonVarStringWrite ]
new_variables += [ "GenJet[%s]"      %genJetVarStringWrite ]
new_variables += [ "GenTop[%s]"      %genTopVarStringWrite ]

new_variables += [ "GenBj0_%s"% var for var in genJetVarStringWrite.split(',')]
new_variables += [ "GenBj1_%s"% var for var in genJetVarStringWrite.split(',')]


if options.addReweights:
    new_variables += [ "rw_nominal/F" ]
    new_variables += [ "ref_weight/F" ] # Lumi weight 1fb / w_0

products = {
    'lhe':{'type':'LHEEventProduct', 'label':("externalLHEProducer")},
    'gp':{'type':'vector<reco::GenParticle>', 'label':("genParticles")},
    'genJets':{'type':'vector<reco::GenJet>', 'label':("ak4GenJets")},
    'genMET':{'type':'vector<reco::GenMET>',  'label':("genMetTrue")},
}

reader = sample.fwliteReader( products = products )

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
    for var in collection_varnames:
        setattr(event, collection_name+"_"+var, obj[var] )

def filterParticles( coll, vars, pdgId ):
    particles = map( lambda t:{ var: getattr( t, var )() for var in vars }, filter( lambda p: abs(p.pdgId()) == pdgId and search.isLast(p), coll ) )

def filler( event ):

    event.run, event.luminosity, event.evt = reader.evt
    event.weight                           = lumiweight

    if reader.position % 100 == 0:
        logger.info( "At event %i/%i", reader.position, reader.nEvents )

    # EFT weights
    if options.addReweights:
        event.nrw    = weightInfo.nid
        lhe_weights  = reader.products['lhe'].weights()
        weights      = []
        param_points = []

        for weight in lhe_weights:
            # Store nominal weight (First position!) 
            if weight.id == 'rwgt_1': event.rw_nominal = weight.wgt

            if not weight.id in weightInfo.id: continue

            pos                = weightInfo.data[weight.id]
            event.rw_w[pos]    = weight.wgt
            weights           += [ weight.wgt ]
            interpreted_weight = interpret_weight( weight.id ) 

            for var in weightInfo.variables:
                getattr( event, "rw_"+var )[pos] = interpreted_weight[var]

            # weight data for interpolation
            if not hyperPoly.initialized:
                param_points += [ tuple( interpreted_weight[var] for var in weightInfo.variables ) ]

        # get list of values of ref point in specific order
        ref_point_coordinates = [ weightInfo.ref_point_coordinates[var] for var in weightInfo.variables ]

        # Initialize with Reference Point
        if not hyperPoly.initialized:
            hyperPoly.initialize( param_points, ref_point_coordinates )

        coeff           = hyperPoly.get_parametrization( weights )
        event.np        = hyperPoly.ndof
        event.chi2_ndof = hyperPoly.chi2_ndof( coeff, weights )

        if event.chi2_ndof > 10**-6:
            logger.warning( "chi2_ndof is large: %f", event.chi2_ndof )

        for n in xrange( hyperPoly.ndof ):
            event.p_C[n] = coeff[n]

        # lumi weight / w0
        event.ref_weight = event.weight / coeff[0]


    # GEN Particles
    genPart = reader.products['gp']

    # for searching
    search  = GenSearch( genPart )

    # MET
    GenMET           = { 'pt':reader.products['genMET'][0].pt(), 'phi':reader.products['genMET'][0].phi() }
    event.GenMET_pt  = GenMET['pt']
    event.GenMET_phi = GenMET['phi'] 

    # find heavy objects before they decay
    GenTops = map( lambda t:{ var: getattr( t, var )() for var in genTopVars }, filter( lambda p: abs(p.pdgId()) == 6 and search.isLast(p),  genPart ) )
    GenTops.sort( key = lambda p:-p['pt'] )
    fill_vector_collection( event, "GenTop", genTopVars, GenTops ) 

    # genLeptons: prompt gen-leptons 
    GenLeptonsAll    = [ ( search.ascend(l), l ) for l in filter( lambda p: abs( p.pdgId() ) in [ 11, 13 ] and search.isLast(p) and p.pt() >= 0 and p.status() == 1,  genPart ) ]
    GenPromptLeptons = []
    GenLeptons       = []

    for first, last in GenLeptonsAll:

        mother = first.mother(0) if first.numberOfMothers() > 0 else None
        mother_pdgId      = 0
        grandmother_pdgId = 0 

        if mother:
            mother_pdgId      = mother.pdgId()
            mother_ascend     = search.ascend( mother )
            grandmother       = mother_ascend.mother(0) if mother.numberOfMothers() > 0 else None
            grandmother_pdgId = grandmother.pdgId() if grandmother else 0

        genLep = { var: getattr(last, var)() for var in genLeptonVarsRead }
        genLep['motherPdgId']      = mother_pdgId
        genLep['grandmotherPdgId'] = grandmother_pdgId
        GenLeptons.append( genLep )

        if abs( mother_pdgId ) in [ 11, 13, 15, 23, 24, 25 ]:
            GenPromptLeptons.append( genLep )

    # Filter gen leptons
    GenPromptLeptons =  list( filter( lambda l:isGoodGenLepton( l ), GenPromptLeptons ) )
    GenPromptLeptons.sort( key = lambda p:-p['pt'] )

    GenPromptElectrons =  list( filter( lambda l: abs(l['pdgId'])==11, GenPromptLeptons ) )
    GenPromptMuons     =  list( filter( lambda l: abs(l['pdgId'])==13, GenPromptLeptons ) )
    event.nGenElectron = len( GenPromptElectrons )
    event.nGenMuon     = len( GenPromptMuons )

    # Gen photons: particle-level isolated gen photons
    GenPhotonsAll = [ ( search.ascend(l), l ) for l in filter( lambda p: abs( p.pdgId() ) == 22 and p.pt() > 13 and search.isLast(p) and p.status() == 1, genPart ) ]
    GenPhotonsAll.sort( key = lambda p: -p[1].pt() )
    GenPhotons    = []

    for first, last in GenPhotonsAll[:10]:
        mother_pdgId = first.mother(0).pdgId() if first.numberOfMothers() > 0 else 0
        GenPhoton    = { var:getattr(last, var)() for var in genPhotonVarsRead }

        # kinematic photon selection
        if not isGoodGenPhoton( GenPhoton ): continue

        GenPhoton['motherPdgId'] = mother_pdgId
        GenPhoton['status']      = last.status()

        close_particles = filter( lambda p: p!=last and deltaR2( {'phi':last.phi(), 'eta':last.eta()}, {'phi':p.phi(), 'eta':p.eta()} ) < 0.16 , search.final_state_particles_no_neutrinos )
        GenPhoton['relIso04_all'] = sum( [ p.pt() for p in close_particles ], 0 ) / last.pt()
        # require isolation of 0.3 as in run card
#        if GenPhoton['relIso04_all'] < 0.3:
#            GenPhotons.append( GenPhoton )
        GenPhotons.append( GenPhoton )

    # deltaR cleaning to photons as in run card
    GenPhotons = list( filter( lambda p: min( [999] + [ deltaR2( p, l ) for l in GenPromptLeptons ] ) > 0.09, GenPhotons ) )

    # Jets
    GenJetsAll = list( filter( genJetId, reader.products['genJets'] ) )
    GenJets    = map( lambda t: {var: getattr(t, var)() for var in genJetVarsRead}, filter( lambda j: j.pt() > 30, GenJetsAll ) )
    # Filter genJets
    GenJets    = list( filter( lambda j: isGoodGenJet(j), GenJets ) )
    # deltaR cleaning to photons as in run card
    GenJets    = list( filter( lambda j: min( [999] + [ deltaR2( j, p ) for p in GenPhotons ] ) > 0.09, GenJets ) )
    # Delta R cleaning jets to leptons as in run card
    GenJets    = list( filter( lambda j: min( [999] + [ deltaR2( j, l ) for l in GenPromptLeptons ] ) > 0.16, GenJets ) )
    GenJets.sort( key = lambda p: -p['pt'] )

    # find b's from tops:
    bPartons = [ b for b in filter( lambda p: abs(p.pdgId()) == 5 and p.numberOfMothers() == 1 and abs(p.mother(0).pdgId()) == 6,  genPart ) ]

    # store if gen-jet is DR matched to a B parton in cone of 0.2
    for GenJet in GenJets:
        GenJet['matchBParton'] = min( [999] + [ deltaR2( GenJet, {'eta':b.eta(), 'phi':b.phi() } ) for b in bPartons ] ) < 0.04

    # gen b jets
    trueBjets    = list( filter( lambda j: j['matchBParton'], GenJets ) )
    trueNonBjets = list( filter( lambda j: not j['matchBParton'], GenJets ) )

    # Mimick b reconstruction ( if the trailing b fails acceptance, we supplement with the leading non-b jet ) 
    GenBj0, GenBj1 = ( trueBjets + trueNonBjets + [None, None] )[:2]
    if GenBj0: fill_vector( event, "GenBj0", genJetVars, GenBj0 ) 
    if GenBj1: fill_vector( event, "GenBj1", genJetVars, GenBj1 ) 

    # store minimum DR to jets
    for GenPhoton in GenPhotons:
        GenPhoton['photonJetdR'] =  min( [999] + [ deltaR( GenPhoton, j ) for j in GenJets ] )
        GenPhoton['photonLepdR'] =  min( [999] + [ deltaR( GenPhoton, j ) for j in GenLeptons ] )

    fill_vector_collection( event, "GenPhoton", genPhotonVars, GenPhotons ) 
    fill_vector_collection( event, "GenLepton", genLeptonVars, GenPromptLeptons )
    fill_vector_collection( event, "GenJet",    genJetVars,    GenJets )
    event.nGenBJet = len( trueBjets )


    # Ovservables
    if len( GenPromptLeptons ) > 1:
        event.mll = ( get4DVec(GenPromptLeptons[0]) + get4DVec(GenPromptLeptons[1]) ).M()
        if len(GenPhotons) > 0:
            event.mllgamma = ( get4DVec(GenPromptLeptons[0]) + get4DVec(GenPromptLeptons[1]) + get4DVec(GenPhotons[0]) ).M()


tmp_dir     = ROOT.gDirectory
output_filename =  os.path.join(output_directory, sample.name + '.root')

if os.path.exists( output_filename ) and not options.overwrite :
    logger.info( "File %s found. Quit.", output_filename )
    sys.exit(0)

output_file = ROOT.TFile( output_filename, 'recreate' )
output_file.cd()

maker = TreeMaker(
    sequence  = [ filler ],
    variables = [ TreeVariable.fromString(x) for x in new_variables ] + reweight_variables,
    treeName = "Events"
    )

tmp_dir.cd()

counter = 0
reader.start()
maker.start()

while reader.run( ):
    maker.run()

    counter += 1
    if counter == maxN: break

logger.info( "Done with running over %i events.", reader.nEvents )

output_file.cd()
maker.tree.Write()
output_file.Close()

logger.info( "Written output file %s", output_filename )
