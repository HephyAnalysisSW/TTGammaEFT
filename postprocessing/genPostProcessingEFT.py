#!/usr/bin/env python
""" Make flat ntuple from GEN data 
"""

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
from Analysis.Tools.helpers                      import deltaR, deltaR2, deltaPhi, mT
from TTGammaEFT.Tools.helpers                    import m3

from TTGammaEFT.Tools.genObjectSelection         import isGoodGenJet, isGoodGenLepton, isGoodGenPhoton, genJetId
from TTGammaEFT.Tools.objectSelection            import *

from Analysis.Tools.WeightInfo                   import WeightInfo
from Analysis.Tools.HyperPoly                    import HyperPoly
from Analysis.Tools.GenSearch                    import GenSearch

logChoices      = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET", "SYNC"]

def get_parser():
    """ Argument parser for post-processing module.
    """
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser for nanoPostProcessing")

    argParser.add_argument("--logLevel",                    action="store",         nargs="?",              choices=logChoices,     default="INFO",                     help="Log level for logging")
    argParser.add_argument("--overwrite",                   action="store_true",                                                                                        help="Overwrite existing output files, bool flag set to True  if used")
    argParser.add_argument("--samples",                     action="store",         nargs="*",  type=str,                           default=["WZTo3LNu"],               help="List of samples to be post-processed, given as CMG component name")
    argParser.add_argument("--eventsPerJob",                action="store",         nargs="?",  type=int,                           default=300000000,                  help="Maximum number of events per job (Approximate!).") # mul by 100
    argParser.add_argument("--nJobs",                       action="store",         nargs="?",  type=int,                           default=1,                          help="Maximum number of simultaneous jobs.")
    argParser.add_argument("--job",                         action="store",                     type=int,                           default=0,                          help="Run only job i")
    argParser.add_argument("--minNJobs",                    action="store",         nargs="?",  type=int,                           default=1,                          help="Minimum number of simultaneous jobs.")
    argParser.add_argument("--targetDir",                   action="store",         nargs="?",  type=str,                           default=user.postprocessing_output_directory, help="Name of the directory the post-processed files will be saved")
    argParser.add_argument("--processingEra",               action="store",         nargs="?",  type=str,                           default="TTGammaEFT_PP_v1",         help="Name of the processing era")
    argParser.add_argument("--small",                       action="store_true",                                                                                        help="Run the file on a small sample (for test purpose), bool flag set to True if used")
    argParser.add_argument("--addReweights",                action="store_true",                                                                                        help="Add reweights for sample EFT reweighting?")
    argParser.add_argument("--noCleaning",                  action="store_true",                                                                                        help="No object deltaR cleaning?")
    argParser.add_argument("--interpolationOrder",          action="store",         nargs="?",  type=int,                           default=2,                          help="Interpolation order for EFT weights.")

    return argParser

options = get_parser().parse_args()

# Logging
import Analysis.Tools.logger as logger
logFile = "/tmp/%s_%s_njob%s.txt"%("_".join(options.samples), os.environ["USER"], str(0 if options.nJobs==1 else options.job) )
logger  = logger.get_logger(options.logLevel, logFile = logFile)

import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(options.logLevel, logFile = None )

#Samples: Load samples
maxN = None
if options.small:
    maxN = 1000
    options.job = 1
    options.nJobs = 200

# Load all samples to be post processed
from TTGammaEFT.Samples.genTuples_TTGamma_EFT import *
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
if options.addReweights: pklFile = sample.reweight_pkl

postfix = "_small" if options.small else ""
from TTGammaEFT.Tools.user import postprocessing_output_directory as user_directory
directory        = os.path.join( user_directory, options.processingEra )
output_directory = os.path.join( "/tmp/%s"%os.environ["USER"], str(uuid.uuid4()) )
targetPath       = os.path.join( directory, "gen" + postfix, sample.name )

# Single file post processing
if options.nJobs>1:
    n_files_before = len(sample.files)
    sample = sample.split(options.nJobs)[options.job]
    n_files_after  = len(sample.files)
    logger.info( "Running job %i/%i over %i files from a total of %i.", options.job, options.nJobs, n_files_after, n_files_before)

if os.path.exists( targetPath ) and options.overwrite:
    if options.nJobs > 1:
        logger.warning( "NOT removing directory %s because nJobs = %i", targetPath, options.nJobs )
    else:
        logger.info( "Output directory %s exists. Deleting.", targetPath )
        shutil.rmtree( targetPath, ignore_errors=True )

if not os.path.exists( targetPath ):
    try:
        os.makedirs( targetPath )
        logger.info( "Created output directory %s.", targetPath )
    except:
        logger.info( "Directory %s already exists.", targetPath )
        pass

if not os.path.exists( output_directory ):
    try:
        os.makedirs( output_directory )
        logger.info( "Created tmp directory %s.", output_directory )
    except:
        logger.info( "TmpDirectory %s already exists.", output_directory )
        pass

# Load reweight pickle file if supposed to keep weights. 
reweight_variables = []
if options.addReweights:

    # Determine coefficients for storing in vector
    # Sort Ids wrt to their position in the card file

    weightInfo = WeightInfo( pklFile )

    # weights for the ntuple
    rw_vector           = TreeVariable.fromString( "rw[w/F,"+",".join(w+"/F" for w in weightInfo.variables)+"]" )
    rw_vector.nMax      = weightInfo.nid
    reweight_variables += [ rw_vector ]

    # coefficients for the weight parametrization
    param_vector        = TreeVariable.fromString( "p[C/F]" )
    param_vector.nMax   = HyperPoly.get_ndof(weightInfo.nvar, options.interpolationOrder)
    hyperPoly           = HyperPoly( options.interpolationOrder )
    reweight_variables += [ param_vector ]
    reweight_variables += [ TreeVariable.fromString( "chi2_ndof/F" ) ]


# ATLAS Unfolding
genLeptonSel_ATLASUnfold = genLeptonSelector( "ATLASUnfolding" )
genPhotonSel_ATLASUnfold = genPhotonSelector( "ATLASUnfolding" )
genJetSel_ATLASUnfold    = genJetSelector(    "ATLASUnfolding" )
# CMS Unfolding
genLeptonSel_CMSUnfold = genLeptonSelector( "CMSUnfolding" )
genPhotonSel_CMSUnfold = genPhotonSelector( "CMSUnfolding" )
genJetSel_CMSUnfold    = genJetSelector(    "CMSUnfolding" )

# variables
genJetVarStringRead  = "pt/F,eta/F,phi/F,isMuon/I,isElectron/I,isPhoton/I"
genJetVarStringWrite = "isBJet/I"
genJetVarStringWrite = genJetVarStringRead + "," + genJetVarStringWrite
genJetVars           = [ item.split("/")[0] for item in genJetVarStringWrite.split(",") ]
genJetVarsRead       = [ item.split("/")[0] for item in genJetVarStringRead.split(",") ]

genTopVarStringRead  = "pt/F,eta/F,phi/F,mass/F,pdgId/I"
genTopVarStringWrite = genTopVarStringRead
genTopVars           = [ item.split("/")[0] for item in genTopVarStringWrite.split(",") ]

genWVarStringRead  = "pt/F,eta/F,phi/F,mass/F,pdgId/I"
genWVarStringWrite = genWVarStringRead
genWVars           = [ item.split("/")[0] for item in genWVarStringWrite.split(",") ]

genLeptonVarStringRead  = "pt/F,eta/F,phi/F,pdgId/I"
genLeptonVarStringWrite = "motherPdgId/I,grandmotherPdgId/I"
genLeptonVarStringWrite = genLeptonVarStringRead + "," + genLeptonVarStringWrite
genLeptonVars           = [ item.split("/")[0] for item in genLeptonVarStringWrite.split(",") ]
genLeptonVarsRead       = [ item.split("/")[0] for item in genLeptonVarStringRead.split(",") ]

genParticleVarStringRead  = "pt/F,eta/F,phi/F,pdgId/I"
genParticleVarsRead       = [ item.split("/")[0] for item in genParticleVarStringRead.split(",") ]

genPhotonVarStringRead  = "pt/F,phi/F,eta/F,mass/F"
genPhotonVarStringWrite = "motherPdgId/I,grandmotherPdgId/I,relIso04_all/F,relIso03_all/F,photonLepdR/F,photonJetdR/F,photonAlldR/F,status/I"
genPhotonVarStringWrite = genPhotonVarStringRead + "," + genPhotonVarStringWrite
genPhotonVars           = [ item.split("/")[0] for item in genPhotonVarStringWrite.split(",") ]
genPhotonVarsRead       = [ item.split("/")[0] for item in genPhotonVarStringRead.split(",") ]

# Write Variables
new_variables  = []
new_variables += [ "run/I", "luminosity/I", "evt/l" ]
new_variables += [ "weight/F" ]

new_variables += [ "GenMET_pt/F", "GenMET_phi/F" ]
new_variables += [ "MET_pt/F", "MET_phi/F" ]

new_variables += [ "dPhiLepGamma/F", "dPhiTopHadGamma/F", "dPhiWHadGamma/F", "dPhiTopLepGamma/F", "dPhiWLepGamma/F", "dPhiBHadGamma/F", "dPhiBLepGamma/F" ]
new_variables += [ "dPhiBLepWLep/F", "dPhiWLepWHad/F", "dPhiBHadWHad/F", "dPhiBLepBHad/F", "dPhiTopLepTopHad/F", "dPhiLepMET/F" ]

new_variables += [ "dRLepGamma/F", "dRTopHadGamma/F", "dRWHadGamma/F", "dRTopLepGamma/F", "dRWLepGamma/F", "dRBHadGamma/F", "dRBLepGamma/F" ]
new_variables += [ "dRBLepWLep/F", "dRWLepWHad/F", "dRBHadWHad/F", "dRBLepBHad/F", "dRTopLepTopHad/F" ]

new_variables += [ "mT/F", "m3/F", "ht/F", "mLtight0Gamma/F" ]


new_variables += [ "nGenJets/I" ]
new_variables += [ "nGenBJet/I" ]
new_variables += [ "nGenLepton/I" ]
new_variables += [ "nGenMuon/I" ]
new_variables += [ "nGenElectron/I" ]
new_variables += [ "nGenPhoton/I" ]

new_variables += [ "GenLepton[%s]"   %genLeptonVarStringWrite ]
new_variables += [ "GenPhoton[%s]"   %genPhotonVarStringWrite ]
new_variables += [ "GenJet[%s]"      %genJetVarStringWrite ]
new_variables += [ "GenBJet[%s]"     %genJetVarStringWrite ]
new_variables += [ "GenTop[%s]"      %genTopVarStringWrite ]
new_variables += [ "GenTopLep[%s]"   %genTopVarStringWrite ]
new_variables += [ "GenTopHad[%s]"   %genTopVarStringWrite ]
new_variables += [ "GenW[%s]"        %genWVarStringWrite ]
new_variables += [ "GenWLep[%s]"     %genWVarStringWrite ]
new_variables += [ "GenWHad[%s]"     %genWVarStringWrite ]
new_variables += [ "GenBLep[%s]"     %genWVarStringWrite ]
new_variables += [ "GenBHad[%s]"     %genWVarStringWrite ]

new_variables += [ "GenPhotonATLASUnfold0_" + var for var in genPhotonVarStringWrite.split(",") ]
new_variables += [ "nGenJetsATLASUnfold/I" ]
new_variables += [ "nGenBJetATLASUnfold/I" ]
new_variables += [ "nGenLeptonATLASUnfold/I" ]
new_variables += [ "nGenMuonATLASUnfold/I" ]
new_variables += [ "nGenElectronATLASUnfold/I" ]
new_variables += [ "nGenPhotonATLASUnfold/I" ]

new_variables += [ "GenPhotonCMSUnfold0_" + var for var in genPhotonVarStringWrite.split(",") ]
new_variables += [ "GenLeptonCMSUnfold0_" + var for var in genLeptonVarStringWrite.split(",") ]
new_variables += [ "GenJetsCMSUnfold0_" + var for var in genJetVarStringWrite.split(",") ]
new_variables += [ "GenJetsCMSUnfold1_" + var for var in genJetVarStringWrite.split(",") ]
new_variables += [ "GenJetsCMSUnfold2_" + var for var in genJetVarStringWrite.split(",") ]
new_variables += [ "GenBJetCMSUnfold0_" + var for var in genJetVarStringWrite.split(",") ]
new_variables += [ "GenBJetCMSUnfold1_" + var for var in genJetVarStringWrite.split(",") ]
new_variables += [ "nGenJetsCMSUnfold/I" ]
new_variables += [ "nGenBJetCMSUnfold/I" ]
new_variables += [ "nGenLeptonCMSUnfold/I" ]
new_variables += [ "nGenMuonCMSUnfold/I" ]
new_variables += [ "nGenElectronCMSUnfold/I" ]
new_variables += [ "nGenPhotonCMSUnfold/I" ]

new_variables += [ "nLeptonTight/I" ]
new_variables += [ "nElectronTight/I" ]
new_variables += [ "nMuonTight/I" ]
new_variables += [ "nLeptonVetoIsoCorr/I" ]
new_variables += [ "nJetGood/I" ]
new_variables += [ "nBTagGood/I" ]
new_variables += [ "nPhotonGood/I" ]
new_variables += [ "nPhotonNoChgIsoNoSieie/I" ]
new_variables += [ "PhotonGood0_"  + var for var in genPhotonVarStringWrite.split(",") ]
new_variables += [ "PhotonNoChgIsoNoSieie0_"  + var for var in genPhotonVarStringWrite.split(",") ]
new_variables += [ "LeptonTight0_" + var for var in genLeptonVarStringWrite.split(",") ]

new_variables += [ "nGenJetsCMSUnfold/I" ]
new_variables += [ "nGenBJetCMSUnfold/I" ]
new_variables += [ "nGenLeptonCMSUnfold/I" ]
new_variables += [ "nGenMuonCMSUnfold/I" ]
new_variables += [ "nGenElectronCMSUnfold/I" ]
new_variables += [ "nGenPhotonCMSUnfold/I" ]


if options.addReweights:
    new_variables += [ "rw_nominal/F" ]
    new_variables += [ "ref_weight/F" ] # Lumi weight 1fb / w_0
#    new_variables += reweight_variables

products = {
    "lhe":{"type":"LHEEventProduct", "label":("externalLHEProducer")},
    "gp":{"type":"vector<reco::GenParticle>", "label":("genParticles")},
    "genJets":{"type":"vector<reco::GenJet>", "label":("ak4GenJets")},
    "genMET":{"type":"vector<reco::GenMET>",  "label":("genMetTrue")},
}

reader = sample.fwliteReader( products = products )

def get4DVec( part ):
    vec = ROOT.TLorentzVector()
    vec.SetPtEtaPhiM( part["pt"], part["eta"], part["phi"], 0 )
    return vec

def interpret_weight(weight_id):
    str_s = weight_id.split("_")
    res={}
    for i in range(len(str_s)/2):
        res[str_s[2*i]] = float(str_s[2*i+1].replace("m","-").replace("p","."))
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

##############################################
##############################################
##############################################

def filler( event ):

    event.run, event.luminosity, event.evt = reader.evt
    event.weight                           = lumiweight

    if reader.position % 100 == 0:
        logger.info( "At event %i/%i", reader.position, reader.nEvents )

    # EFT weights
    if options.addReweights:
        event.nrw    = weightInfo.nid
        lhe_weights  = reader.products["lhe"].weights()
        weights      = []
        param_points = []

        for weight in lhe_weights:
            # Store nominal weight (First position!) 
            if weight.id == "rwgt_1": event.rw_nominal = weight.wgt

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


    ##############################################
    ##############################################
    ##############################################

    # GEN Particles
    genPart = reader.products["gp"]

    # for searching
    search  = GenSearch( genPart )

    # MET
    GenMET           = { "pt":reader.products["genMET"][0].pt(), "phi":reader.products["genMET"][0].phi() }
    event.GenMET_pt  = GenMET["pt"]
    event.GenMET_phi = GenMET["phi"] 
    # reco naming
    event.MET_pt     = GenMET["pt"]
    event.MET_phi    = GenMET["phi"] 

    # find heavy objects before they decay
    GenT    = filter( lambda p: abs(p.pdgId()) == 6 and search.isLast(p),  genPart )

    GenTopLep = []
    GenWLep   = []
    GenTopHad = []
    GenWHad   = []
    GenBLep   = []
    GenBHad   = []
    GenWs     = []
    for top in GenT:
        GenW   = [ search.descend(w) for w in search.daughters(top) if abs(w.pdgId()) == 24 ]
        GenB   = [ search.descend(w) for w in search.daughters(top) if abs(w.pdgId()) == 5 ]
        if GenW:
            GenW = GenW[0]
            GenWs.append(GenW)
            wDecays = [ abs(l.pdgId()) for l in search.daughters(GenW) ]
            if 11 in wDecays or 13 in wDecays or 15 in wDecays:
                GenWLep.append(GenW)
                if GenB: GenBLep.append(GenB[0])
                GenTopLep.append(top)
            else:
                GenWHad.append(GenW)
                if GenB: GenBHad.append(GenB[0])
                GenTopHad.append(top)

    GenTops = map( lambda t:{ var: getattr( t, var )() for var in genTopVars }, GenT )
    GenTops.sort( key = lambda p:-p["pt"] )
    fill_vector_collection( event, "GenTop", genTopVars, GenTops ) 

    GenTopLep = map( lambda t:{ var: getattr( t, var )() for var in genTopVars }, GenTopLep )
    GenTopLep.sort( key = lambda p:-p["pt"] )
    fill_vector_collection( event, "GenTopLep", genTopVars, GenTopLep ) 

    GenTopHad = map( lambda t:{ var: getattr( t, var )() for var in genTopVars }, GenTopHad )
    GenTopHad.sort( key = lambda p:-p["pt"] )
    fill_vector_collection( event, "GenTopHad", genTopVars, GenTopHad ) 

    GenWs = map( lambda t:{ var: getattr( t, var )() for var in genWVars }, GenWs )
    GenWs.sort( key = lambda p:-p["pt"] )
    fill_vector_collection( event, "GenW", genWVars, GenWs ) 

    GenWLep = map( lambda t:{ var: getattr( t, var )() for var in genWVars }, GenWLep )
    GenWLep.sort( key = lambda p:-p["pt"] )
    fill_vector_collection( event, "GenWLep", genWVars, GenWLep ) 

    GenWHad = map( lambda t:{ var: getattr( t, var )() for var in genWVars }, GenWHad )
    GenWHad.sort( key = lambda p:-p["pt"] )
    fill_vector_collection( event, "GenWHad", genWVars, GenWHad ) 

    GenBLep = map( lambda t:{ var: getattr( t, var )() for var in genWVars }, GenBLep )
    GenBLep.sort( key = lambda p:-p["pt"] )
    fill_vector_collection( event, "GenBLep", genWVars, GenBLep ) 

    GenBHad = map( lambda t:{ var: getattr( t, var )() for var in genWVars }, GenBHad )
    GenBHad.sort( key = lambda p:-p["pt"] )
    fill_vector_collection( event, "GenBHad", genWVars, GenBHad ) 

    bPartonsFromTop = [ b for b in filter( lambda p: abs(p.pdgId()) == 5 and p.numberOfMothers() == 1 and abs(p.mother(0).pdgId()) == 6,  genPart ) ]

    # genParticles for isolation
    GenParticlesIso = [ l for l in filter( lambda p: abs( p.pdgId() ) not in [12,14,16] and p.pt() > 5 and p.status() == 1, genPart ) ]
    GenParticlesIso.sort( key = lambda p: -p.pt() )
    GenParticlesIso = [ { var: getattr(l, var)() for var in genParticleVarsRead } for l in GenParticlesIso ]

    # genLeptons
    GenLeptonAll = [ (search.ascend(l), l) for l in filter( lambda p: abs( p.pdgId() ) in [11,13] and search.isLast(p) and p.status() == 1, genPart ) ]
    GenLeptonAll.sort( key = lambda p: -p[1].pt() )
    GenLepton    = []

    for first, last in GenLeptonAll:

        mother            = first.mother(0) if first.numberOfMothers() > 0 else None
        grandmother_pdgId = -999
        mother_pdgId      = -999

        if mother:
            mother_pdgId      = mother.pdgId()
            mother_ascend     = search.ascend( mother )
            grandmother       = mother_ascend.mother(0) if mother.numberOfMothers() > 0 else None
            if grandmother:
                grandmother_pdgId = grandmother.pdgId()

        genLep = { var: getattr(last, var)() for var in genLeptonVarsRead }
        genLep["motherPdgId"]      = mother_pdgId
        genLep["grandmotherPdgId"] = grandmother_pdgId
        GenLepton.append( genLep )

    # Gen photons: particle-level isolated gen photons
    GenPhotonAll = [ ( search.ascend(l), l ) for l in filter( lambda p: abs( p.pdgId() ) == 22 and p.pt() > 5 and search.isLast(p), genPart ) ]
    GenPhotonAll.sort( key = lambda p: -p[1].pt() )
    GenPhoton    = []

    for first, last in GenPhotonAll:

        mother            = first.mother(0) if first.numberOfMothers() > 0 else None
        grandmother_pdgId = -999
        mother_pdgId      = -999

        if mother:
            mother_pdgId      = mother.pdgId()
            mother_ascend     = search.ascend( mother )
            grandmother       = mother_ascend.mother(0) if mother.numberOfMothers() > 0 else None
            if grandmother:
                grandmother_pdgId = grandmother.pdgId()

        GenP    = { var:getattr(last, var)() for var in genPhotonVarsRead }
        GenP["motherPdgId"]      = mother_pdgId
        GenP["grandmotherPdgId"] = grandmother_pdgId
        GenP["status"]           = last.status()

        close_particles = filter( lambda p: p!=last and deltaR2( {"phi":last.phi(), "eta":last.eta()}, {"phi":p.phi(), "eta":p.eta()} ) < 0.16 , search.final_state_particles_no_neutrinos )
        GenP["relIso04_all"] = sum( [ p.pt() for p in close_particles ], 0 ) / last.pt()

        close_particles = filter( lambda p: p!=last and deltaR2( {"phi":last.phi(), "eta":last.eta()}, {"phi":p.phi(), "eta":p.eta()} ) < 0.09 , search.final_state_particles_no_neutrinos )
        GenP["relIso03_all"] = sum( [ p.pt() for p in close_particles ], 0 ) / last.pt()

        GenPhoton.append( GenP )

    # Jets
    GenJetAll = list( filter( genJetId, reader.products["genJets"] ) )
    GenJetAll.sort( key = lambda p: -p.pt() )
    # Filter genJets
    GenJet = map( lambda t: {var: getattr(t, var)() for var in genJetVarsRead}, GenJetAll )
    # BJets
    GenBJet = [ b for b in filter( lambda p: abs(p.pdgId()) == 5,  genPart ) ]

    for GenJ in GenJet:
        GenJ["isBJet"] = min( [999] + [ deltaR2( GenJ, {"eta":b.eta(), "phi":b.phi() } ) for b in GenBJet ] ) < 0.04

    # gen b jets
    GenBJet = list( filter( lambda j: j["isBJet"], GenJet ) )

    # store minimum DR to jets
    for GenP in GenPhoton:
        GenP["photonJetdR"] =  min( [999] + [ deltaR( GenP, j ) for j in GenJet ] )
        GenP["photonLepdR"] =  min( [999] + [ deltaR( GenP, j ) for j in GenLepton ] )
        GenP["photonAlldR"] =  min( [999] + [ deltaR( GenP, j ) for j in GenParticlesIso if abs(GenP["pt"]-j["pt"])>0.01 and j["pdgId"] != 22 ] )

    fill_vector_collection( event, "GenPhoton", genPhotonVars, GenPhoton ) 
    fill_vector_collection( event, "GenLepton", genLeptonVars, GenLepton )
    fill_vector_collection( event, "GenJet",    genJetVars,    GenJet )
    fill_vector_collection( event, "GenBJet",   genJetVars,    GenBJet )

    event.nGenElectron = len( filter( lambda l: abs( l["pdgId"] ) == 11, GenLepton ) )
    event.nGenMuon     = len( filter( lambda l: abs( l["pdgId"] ) == 13, GenLepton ) )
    event.nGenLepton   = len(GenLepton)
    event.nGenPhoton   = len(GenPhoton)
    event.nGenBJet     = len(GenBJet)
    event.nGenJets     = len(GenJet)
    event.nGenBJet = len( GenBJet )

    ##############################################
    ##############################################
    ##############################################

    # Analysis specific variables

    # no meson mother
    GenLeptonCMSUnfold   = list( filter( lambda l: abs(l["motherPdgId"]) in [ 11, 13, 15, 23, 24, 25 ] and genLeptonSel_CMSUnfold( l ), GenLepton ) )
    GenLeptonATLASUnfold = list( filter( lambda l: abs(l["motherPdgId"]) in [ 11, 13, 15, 23, 24, 25 ] and genLeptonSel_ATLASUnfold( l ), GenLepton ) )

    GenPhotonCMSUnfold   = list( filter( lambda p: genPhotonSel_CMSUnfold(p)   and p["status"]==1, GenPhoton ) )
    GenPhotonATLASUnfold = list( filter( lambda p: genPhotonSel_ATLASUnfold(p) and p["status"]==1, GenPhoton ) )

    GenJetCMSUnfold   = list( filter( lambda j: genJetSel_CMSUnfold(j),   GenJet ) )
    GenJetATLASUnfold = list( filter( lambda j: genJetSel_ATLASUnfold(j), GenJet ) )

    GenBJetCMSUnfold   = list( filter( lambda j: genJetSel_CMSUnfold(j),   GenBJet ) )
    GenBJetATLASUnfold = list( filter( lambda j: genJetSel_ATLASUnfold(j), GenBJet ) )

    for GenP in GenPhotonCMSUnfold:
        GenP["photonJetdR"] =  min( [999] + [ deltaR( GenP, j ) for j in GenJetCMSUnfold ] )
        GenP["photonLepdR"] =  min( [999] + [ deltaR( GenP, j ) for j in GenLeptonCMSUnfold ] )
        GenP["photonAlldR"] =  min( [999] + [ deltaR( GenP, j ) for j in GenParticlesIso if abs(GenP["pt"]-j["pt"])>0.01 and j["pdgId"] != 22 ] )

    for GenP in GenPhotonATLASUnfold:
        GenP["photonJetdR"] =  min( [999] + [ deltaR( GenP, j ) for j in GenJetATLASUnfold ] )
        GenP["photonLepdR"] =  min( [999] + [ deltaR( GenP, j ) for j in GenLeptonATLASUnfold ] )
        GenP["photonAlldR"] =  min( [999] + [ deltaR( GenP, j ) for j in GenParticlesIso if abs(GenP["pt"]-j["pt"])>0.01 and j["pdgId"] != 22 ] )

    # Isolated
    GenPhotonCMSUnfold = filter( lambda g: g["photonAlldR"] > 0.1, GenPhotonCMSUnfold )
    GenPhotonCMSUnfold = filter( lambda g: abs(g["grandmotherPdgId"]) in range(37)+[2212] and abs(g["motherPdgId"]) in range(37)+[2212], GenPhotonCMSUnfold )

    GenPhotonATLASUnfold = filter( lambda g: g["relIso03_all"] < 0.1, GenPhotonATLASUnfold )
    GenPhotonATLASUnfold = filter( lambda g: abs(g["grandmotherPdgId"]) in range(37)+[2212] and abs(g["motherPdgId"]) in range(37)+[2212], GenPhotonATLASUnfold )

    for GenJ in GenJetATLASUnfold:
        GenJ["jetPhotondR"] =  min( [999] + [ deltaR( GenJ, p ) for p in GenPhotonATLASUnfold ] )
        GenJ["jetLepdR"]    =  min( [999] + [ deltaR( GenJ, p ) for p in GenLeptonATLASUnfold ] )

    for GenJ in GenBJetATLASUnfold:
        GenJ["jetPhotondR"] =  min( [999] + [ deltaR( GenJ, p ) for p in GenPhotonATLASUnfold ] )
        GenJ["jetLepdR"]    =  min( [999] + [ deltaR( GenJ, p ) for p in GenLeptonATLASUnfold ] )

    for GenJ in GenJetCMSUnfold:
        GenJ["jetPhotondR"] =  min( [999] + [ deltaR( GenJ, p ) for p in GenPhotonCMSUnfold ] )
        GenJ["jetLepdR"]    =  min( [999] + [ deltaR( GenJ, p ) for p in GenLeptonCMSUnfold ] )

    for GenJ in GenBJetCMSUnfold:
        GenJ["jetPhotondR"] =  min( [999] + [ deltaR( GenJ, p ) for p in GenPhotonCMSUnfold ] )
        GenJ["jetLepdR"]    =  min( [999] + [ deltaR( GenJ, p ) for p in GenLeptonCMSUnfold ] )

    # CMS Unfolding cleaning
    GenPhotonCMSUnfold = filter( lambda g: g["photonLepdR"] > 0.1, GenPhotonCMSUnfold )
    GenJetCMSUnfold    = filter( lambda g: g["jetPhotondR"] > 0.1, GenJetCMSUnfold )
    GenBJetCMSUnfold   = filter( lambda g: g["jetPhotondR"] > 0.1, GenBJetCMSUnfold )
    GenJetCMSUnfold    = filter( lambda g: g["jetLepdR"] > 0.4,    GenJetCMSUnfold )
    GenBJetCMSUnfold   = filter( lambda g: g["jetLepdR"] > 0.4,    GenBJetCMSUnfold )

    # ATLAS Unfolding cleaning
    GenPhotonATLASUnfold = filter( lambda g: g["photonLepdR"] > 1.0, GenPhotonATLASUnfold )
    GenJetATLASUnfold    = filter( lambda g: g["jetPhotondR"] > 0.4, GenJetATLASUnfold )
    GenBJetATLASUnfold   = filter( lambda g: g["jetPhotondR"] > 0.4, GenBJetATLASUnfold )
    GenJetATLASUnfold    = filter( lambda g: g["jetLepdR"] > 0.4,    GenJetATLASUnfold )
    GenBJetATLASUnfold   = filter( lambda g: g["jetLepdR"] > 0.4,    GenBJetATLASUnfold )

    GenPhotonCMSUnfold.sort( key = lambda p: -p["pt"] )
    genP0 = ( GenPhotonCMSUnfold[:1] + [None] )[0]
    if genP0: fill_vector( event, "GenPhotonCMSUnfold0",  genPhotonVars, genP0 )
    if genP0: fill_vector( event, "PhotonGood0",          genPhotonVars, genP0 )
    if genP0: fill_vector( event, "PhotonNoChgIsoNoSieie0",          genPhotonVars, genP0 )

    GenPhotonATLASUnfold.sort( key = lambda p: -p["pt"] )
    genP0 = ( GenPhotonATLASUnfold[:1] + [None] )[0]
    if genP0: fill_vector( event, "GenPhotonATLASUnfold0",  genPhotonVars, genP0 )

    GenLeptonCMSUnfold.sort( key = lambda p: -p["pt"] )
    genL0 = ( GenLeptonCMSUnfold[:1] + [None] )[0]
    if genL0: fill_vector( event, "GenLeptonCMSUnfold0",  genLeptonVars, genL0 )
    if genL0: fill_vector( event, "LeptonTight0",         genLeptonVars, genL0 )

    GenJetCMSUnfold.sort( key = lambda p: -p["pt"] )
    genJ0, genJ1, genJ2 = ( GenJetCMSUnfold[:3] + [None,None,None] )[:3]
    if genJ0: fill_vector( event, "GenJetsCMSUnfold0",  genJetVars, genJ0 )
    if genJ1: fill_vector( event, "GenJetsCMSUnfold1",  genJetVars, genJ1 )
    if genJ2: fill_vector( event, "GenJetsCMSUnfold2",  genJetVars, genJ2 )

    GenBJetCMSUnfold.sort( key = lambda p: -p["pt"] )
    genB0, genB1 = ( GenBJetCMSUnfold[:2] + [None,None] )[:2]
    if genB0: fill_vector( event, "GenBJetCMSUnfold0",  genJetVars, genB0 )
    if genB1: fill_vector( event, "GenBJetCMSUnfold1",  genJetVars, genB1 )

    event.nGenElectronCMSUnfold = len( filter( lambda l: abs( l["pdgId"] ) == 11, GenLeptonCMSUnfold ) )
    event.nGenMuonCMSUnfold     = len( filter( lambda l: abs( l["pdgId"] ) == 13, GenLeptonCMSUnfold ) )
    event.nGenLeptonCMSUnfold   = len(GenLeptonCMSUnfold)
    event.nGenPhotonCMSUnfold   = len(GenPhotonCMSUnfold)
    event.nGenBJetCMSUnfold     = len(GenBJetCMSUnfold)
    event.nGenJetsCMSUnfold     = len(GenJetCMSUnfold)

    # use reco naming for easier handling
    event.nLeptonTight         = event.nGenLeptonCMSUnfold
    event.nElectronTight       = event.nGenElectronCMSUnfold
    event.nMuonTight           = event.nGenMuonCMSUnfold
    event.nLeptonVetoIsoCorr   = event.nGenLeptonCMSUnfold
    event.nJetGood             = event.nGenJetsCMSUnfold
    event.nBTagGood            = event.nGenBJetCMSUnfold
    event.nPhotonGood          = event.nGenPhotonCMSUnfold
    event.nPhotonNoChgIsoNoSieie = event.nGenPhotonCMSUnfold

    event.nGenElectronATLASUnfold = len( filter( lambda l: abs( l["pdgId"] ) == 11, GenLeptonATLASUnfold ) )
    event.nGenMuonATLASUnfold     = len( filter( lambda l: abs( l["pdgId"] ) == 13, GenLeptonATLASUnfold ) )
    event.nGenLeptonATLASUnfold   = len(GenLeptonATLASUnfold)
    event.nGenPhotonATLASUnfold   = len(GenPhotonATLASUnfold)
    event.nGenBJetATLASUnfold     = len(GenBJetATLASUnfold)
    event.nGenJetsATLASUnfold     = len(GenJetATLASUnfold)


    ##############################################
    ##############################################
    ##############################################

    if GenPhotonCMSUnfold:
        if GenLeptonCMSUnfold:
            event.dPhiLepGamma     = deltaPhi( GenPhotonCMSUnfold[0]["phi"], GenLeptonCMSUnfold[0]["phi"] ) 
            event.dRLepGamma       = deltaR( GenPhotonCMSUnfold[0], GenLeptonCMSUnfold[0] ) 
        if GenTopHad:
            event.dPhiTopHadGamma  = deltaPhi( GenPhotonCMSUnfold[0]["phi"], GenTopHad[0]["phi"] ) 
            event.dRTopHadGamma    = deltaR( GenPhotonCMSUnfold[0], GenTopHad[0] ) 
        if GenWHad:
            event.dPhiWHadGamma    = deltaPhi( GenPhotonCMSUnfold[0]["phi"], GenWHad[0]["phi"] ) 
            event.dRWHadGamma      = deltaR( GenPhotonCMSUnfold[0], GenWHad[0] ) 
        if GenTopLep:
            event.dPhiTopLepGamma  = deltaPhi( GenPhotonCMSUnfold[0]["phi"], GenTopLep[0]["phi"] ) 
            event.dRTopLepGamma    = deltaR( GenPhotonCMSUnfold[0], GenTopLep[0] ) 
        if GenWLep:
            event.dPhiWLepGamma    = deltaPhi( GenPhotonCMSUnfold[0]["phi"], GenWLep[0]["phi"] )  
            event.dRWLepGamma      = deltaR( GenPhotonCMSUnfold[0], GenWLep[0] )  
        if GenBHad:
            event.dPhiBHadGamma    = deltaPhi( GenPhotonCMSUnfold[0]["phi"], GenBHad[0]["phi"] ) 
            event.dRBHadGamma      = deltaR( GenPhotonCMSUnfold[0], GenBHad[0] ) 
        if GenBLep:
            event.dPhiBLepGamma    = deltaPhi( GenPhotonCMSUnfold[0]["phi"], GenBLep[0]["phi"] )
            event.dRBLepGamma      = deltaR( GenPhotonCMSUnfold[0], GenBLep[0] )
    if GenBLep:
        if GenWLep:
            event.dPhiBLepWLep     = deltaPhi( GenBLep[0]["phi"], GenWLep[0]["phi"] ) 
            event.dRBLepWLep       = deltaR( GenBLep[0], GenWLep[0] ) 
        if GenBHad:
            event.dPhiBLepBHad     = deltaPhi( GenBLep[0]["phi"], GenBHad[0]["phi"] ) 
            event.dRBLepBHad       = deltaR( GenBLep[0], GenBHad[0] ) 
    if GenWHad:
        if GenBHad:
            event.dPhiBHadWHad     = deltaPhi( GenBHad[0]["phi"], GenWHad[0]["phi"] ) 
            event.dRBHadWHad       = deltaR( GenBHad[0], GenWHad[0] ) 
        if GenWLep:
            event.dPhiWLepWHad     = deltaPhi( GenWLep[0]["phi"], GenWHad[0]["phi"] ) 
            event.dRWLepWHad       = deltaR( GenWLep[0], GenWHad[0] ) 
    if GenTopLep and GenTopHad:
        event.dPhiTopLepTopHad     = deltaPhi( GenTopLep[0]["phi"], GenTopHad[0]["phi"] ) 
        event.dRTopLepTopHad       = deltaR( GenTopLep[0], GenTopHad[0] ) 
    if GenLeptonCMSUnfold:
        event.dPhiLepMET           = deltaPhi( GenLeptonCMSUnfold[0]["phi"], GenMET["phi"] )

    event.ht            = -999
    event.m3            = -999
    event.mT            = -999
    event.mLtight0Gamma = -999
    if GenJetCMSUnfold:
        event.ht = sum( [ j["pt"] for j in GenJetCMSUnfold ])
        event.m3 = m3( GenJetCMSUnfold )[0]

    if GenLeptonCMSUnfold:
        event.mT = mT( GenLeptonCMSUnfold[0], GenMET )
        if GenPhotonCMSUnfold:
            event.mLtight0Gamma = ( get4DVec(GenLeptonCMSUnfold[0]) + get4DVec(GenPhotonCMSUnfold[0]) ).M()

##############################################
##############################################
##############################################

tmp_dir     = ROOT.gDirectory
output_filename =  os.path.join(output_directory, sample.name + ".root")
target_filename =  os.path.join(targetPath, sample.name + ".root")

if os.path.exists( target_filename ) and not options.overwrite :
    logger.info( "File %s found. Quit.", output_filename )
    sys.exit(0)

output_file = ROOT.TFile( output_filename, "recreate" )
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

logger.info( "Copying output file %s to target %s"%(output_filename, target_filename) )
cmd = [ "rsync", "-av", output_filename, target_filename ]
logger.info( "Issue copy command: %s", " ".join( cmd ) )
subprocess.call( cmd )

shutil.rmtree( output_directory, ignore_errors=True )

