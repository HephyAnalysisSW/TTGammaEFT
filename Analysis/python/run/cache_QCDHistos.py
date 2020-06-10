#!/usr/bin/env python
""" Analysis script for standard plots
"""

# Standard imports
import ROOT, os, imp, sys, copy
ROOT.gROOT.SetBatch(True)
import itertools
from math                             import isnan, ceil, pi, sqrt

# RootTools
from RootTools.core.standard          import *

# Internal Imports
from TTGammaEFT.Tools.user            import cache_directory
from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter
from TTGammaEFT.Tools.TriggerSelector import TriggerSelector
from TTGammaEFT.Tools.Variables       import NanoVariables

from TTGammaEFT.Analysis.Setup         import Setup
from TTGammaEFT.Analysis.EstimatorList import EstimatorList
from TTGammaEFT.Analysis.SetupHelpers  import *
from TTGammaEFT.Analysis.regions       import *

from Analysis.Tools.metFilters        import getFilterCut
from Analysis.Tools.u_float           import u_float
from Analysis.Tools.MergingDirDB      import MergingDirDB

from helpers                          import splitList

addSF = True
# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]
photonCatChoices = [ "None", "PhotonGood0", "PhotonGood1", "PhotonMVA0", "PhotonNoChgIso0", "PhotonNoChgIsoNoSieie0", "PhotonNoSieie0" ]
recoPlotsPath = os.path.expandvars( "$CMSSW_BASE/src/TTGammaEFT/plots/plotsLukas/reco/" )

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                  help="Log level for logging")
#argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv1_v1")
argParser.add_argument("--plotFile",           action="store",      default="all_1l")
argParser.add_argument("--selection",          action="store",      default="dilepOS-nLepVeto2-pTG20-nPhoton1p-offZSFllg-offZSFll-mll40")
argParser.add_argument("--small",              action="store_true",                                                                    help="Run only on a small subset of the data?", )
argParser.add_argument("--overwrite",          action="store_true",                                                                    help="overwrite cache entry?", )
argParser.add_argument("--checkOnly",          action="store_true",                                                                    help="check cached histos?", )
argParser.add_argument("--year",               action="store",      default=None,   type=int,  choices=[2016,2017,2018],               help="Which year to plot?")
argParser.add_argument("--mode",               action="store",      default="None", type=str, choices=["mu", "e", "all"],              help="plot lepton mode" )
argParser.add_argument("--nJobs",              action="store",      default=1,      type=int, choices=[1,2,3,4,5],                     help="Maximum number of simultaneous jobs.")
argParser.add_argument("--job",                action="store",      default=0,      type=int, choices=[0,1,2,3,4],                     help="Run only job i")
argParser.add_argument("--runOnLxPlus",        action="store_true",                                                                    help="Change the global redirector of samples")
argParser.add_argument("--addBadEEJetVeto",    action="store_true",                                                                    help="remove BadEEJetVeto", )
argParser.add_argument("--addHEMweight",       action="store_true",                                                                    help="remove HEMweight", )
args = argParser.parse_args()

# Logging
if __name__=="__main__":
    import Analysis.Tools.logger as logger
    logger = logger.get_logger( args.logLevel, logFile=None)
    import RootTools.core.logger as logger_rt
    logger_rt = logger_rt.get_logger( args.logLevel, logFile=None )
else:
    import logging
    logger = logging.getLogger(__name__)

if args.checkOnly: args.overwrite = False

regionPlot = False
if len(args.selection.split("-")) == 1 and args.selection in allRegions.keys():
    logger.info( "Plotting region from SetupHelpers: %s"%args.selection )

    regionPlot = True
    setup = Setup( year=args.year, photonSelection=False, checkOnly=args.checkOnly, runOnLxPlus=False ) #photonselection always false for qcd estimate
    setup = setup.sysClone( parameters=allRegions[args.selection]["parameters"] )

    selection      = setup.selection( "MC", channel="all", **setup.defaultParameters() )
    args.selection = selection["prefix"]
    logger.info( "Using selection string: %s"%args.selection )

if args.year == 2017 and args.addBadEEJetVeto:
    args.selection += "-BadEEJetVeto"

print args.selection

cache_dir = os.path.join(cache_directory, "qcdHistos", str(args.year))
dirDB = MergingDirDB(cache_dir)
if not dirDB: raise

# Samples
if args.runOnLxPlus:
    # Set the redirector in the samples repository to the global redirector
    from Samples.Tools.config import redirector_global as redirector
os.environ["gammaSkim"]="False" #always false for QCD estimate
if args.year == 2016 and not args.checkOnly:
    from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed  import *
    from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import *
elif args.year == 2017 and not args.checkOnly:
    from TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed    import *
    from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import *
elif args.year == 2018 and not args.checkOnly:
    from TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed  import *
    from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import *

def getYieldPlots():
    yieldPlots = []
    yieldPlots.append( Plot(
                name      = "yield",
                texX      = "yield",
                texY      = "Number of Events",
                attribute = lambda event, sample: event.nElectronTightInvIso,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )

    if "nPhoton0" in args.selection: return yieldPlots

    yieldPlots.append( Plot(
                name      = "yield_20ptG120",
                texX      = "yield",
                texY      = "Number of Events",
                attribute = lambda event, sample: event.nElectronTightInvIso if event.PhotonGood0_pt >= 20 and event.PhotonGood0_pt < 120 else -999,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )
    yieldPlots.append( Plot(
                name      = "yield_120ptG220",
                texX      = "yield",
                texY      = "Number of Events",
                attribute = lambda event, sample: event.nElectronTightInvIso if event.PhotonGood0_pt >= 120 and event.PhotonGood0_pt < 220 else -999,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )
    yieldPlots.append( Plot(
                name      = "yield_220ptGinf",
                texX      = "yield",
                texY      = "Number of Events",
                attribute = lambda event, sample: event.nElectronTightInvIso if event.PhotonGood0_pt >= 220 else -999,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )


    if not "NoChgIsoNoSieiePhoton" in args.selection: return yieldPlots

    yieldPlots.append( Plot(
                name      = "yield_invSieie",
                texX      = "yield",
                texY      = "Number of Events",
                attribute = lambda event, sample: event.nElectronTightInvIso if event.PhotonNoSieie0_sieie > 0.011 else -999,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )
    yieldPlots.append( Plot(
                name      = "yield_invSieie_20ptG120",
                texX      = "yield",
                texY      = "Number of Events",
                attribute = lambda event, sample: event.nElectronTightInvIso if event.PhotonNoSieie0_pt >= 20 and event.PhotonNoSieie0_pt < 120 and event.PhotonNoSieie0_sieie > 0.011 else -999,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )
    yieldPlots.append( Plot(
                name      = "yield_invSieie_120ptG220",
                texX      = "yield",
                texY      = "Number of Events",
                attribute = lambda event, sample: event.nElectronTightInvIso if event.PhotonNoSieie0_pt >= 120 and event.PhotonNoSieie0_pt < 220 and event.PhotonNoSieie0_sieie > 0.011 else -999,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )
    yieldPlots.append( Plot(
                name      = "yield_invSieie_220ptGinf",
                texX      = "yield",
                texY      = "Number of Events",
                attribute = lambda event, sample: event.nElectronTightInvIso if event.PhotonNoSieie0_pt >= 220 and event.PhotonNoSieie0_sieie > 0.011 else -999,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )



    yieldPlots.append( Plot(
                name      = "yield_invChgIso",
                texX      = "yield",
                texY      = "Number of Events",
                attribute = lambda event, sample: event.nElectronTightInvIso if event.PhotonNoChgIso0_pfRelIso03_chg * event.PhotonNoChgIso0_pt > 1.141 else -999,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )
    yieldPlots.append( Plot(
                name      = "yield_invChgIso_20ptG120",
                texX      = "yield",
                texY      = "Number of Events",
                attribute = lambda event, sample: event.nElectronTightInvIso if event.PhotonNoChgIso0_pt >= 20 and event.PhotonNoChgIso0_pt < 120 and event.PhotonNoChgIso0_pfRelIso03_chg * event.PhotonNoChgIso0_pt > 1.141 else -999,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )
    yieldPlots.append( Plot(
                name      = "yield_invChgIso_120ptG220",
                texX      = "yield",
                texY      = "Number of Events",
                attribute = lambda event, sample: event.nElectronTightInvIso if event.PhotonNoChgIso0_pt >= 120 and event.PhotonNoChgIso0_pt < 220 and event.PhotonNoChgIso0_pfRelIso03_chg * event.PhotonNoChgIso0_pt > 1.141 else -999,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )
    yieldPlots.append( Plot(
                name      = "yield_invChgIso_220ptGinf",
                texX      = "yield",
                texY      = "Number of Events",
                attribute = lambda event, sample: event.nElectronTightInvIso if event.PhotonNoChgIso0_pt >= 220 and event.PhotonNoChgIso0_pfRelIso03_chg * event.PhotonNoChgIso0_pt > 1.141 else -999,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )


    yieldPlots.append( Plot(
                name      = "yield_invSieie_invChgIso",
                texX      = "yield",
                texY      = "Number of Events",
                attribute = lambda event, sample: event.nElectronTightInvIso if event.PhotonNoChgIsoNoSieie0_sieie > 0.011 and event.PhotonNoChgIsoNoSieie0_pfRelIso03_chg * event.PhotonNoChgIsoNoSieie0_pt > 1.141 else -999,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )
    yieldPlots.append( Plot(
                name      = "yield_invSieie_invChgIso_20ptG120",
                texX      = "yield",
                texY      = "Number of Events",
                attribute = lambda event, sample: event.nElectronTightInvIso if event.PhotonNoChgIsoNoSieie0_pt >= 20 and event.PhotonNoChgIsoNoSieie0_pt < 120 and event.PhotonNoChgIsoNoSieie0_sieie > 0.011 and event.PhotonNoChgIsoNoSieie0_pfRelIso03_chg * event.PhotonNoChgIsoNoSieie0_pt > 1.141 else -999,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )
    yieldPlots.append( Plot(
                name      = "yield_invSieie_invChgIso_120ptG220",
                texX      = "yield",
                texY      = "Number of Events",
                attribute = lambda event, sample: event.nElectronTightInvIso if event.PhotonNoChgIsoNoSieie0_pt >= 120 and event.PhotonNoChgIsoNoSieie0_pt < 220 and event.PhotonNoChgIsoNoSieie0_sieie > 0.011 and event.PhotonNoChgIsoNoSieie0_pfRelIso03_chg * event.PhotonNoChgIsoNoSieie0_pt > 1.141 else -999,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )
    yieldPlots.append( Plot(
                name      = "yield_invSieie_invChgIso_220ptGinf",
                texX      = "yield",
                texY      = "Number of Events",
                attribute = lambda event, sample: event.nElectronTightInvIso if event.PhotonNoChgIsoNoSieie0_pt >= 220 and event.PhotonNoChgIsoNoSieie0_sieie > 0.011 and event.PhotonNoChgIsoNoSieie0_pfRelIso03_chg * event.PhotonNoChgIsoNoSieie0_pt > 1.141 else -999,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )

    return yieldPlots


# get nano variable lists
NanoVars        = NanoVariables( args.year )

jetVarString     = NanoVars.getVariableString(   "Jet",    postprocessed=True, data=True, plot=True )
jetVariableNames = NanoVars.getVariableNameList( "Jet",    postprocessed=True, data=True, plot=True )
bJetVariables    = NanoVars.getVariables(        "BJet",   postprocessed=True, data=True, plot=True )
leptonVarString  = NanoVars.getVariableString(   "Lepton", postprocessed=True, data=True, plot=True )
leptonVariables  = NanoVars.getVariables(        "Lepton", postprocessed=True, data=True, plot=True )
leptonVarList    = NanoVars.getVariableNameList( "Lepton", postprocessed=True, data=True, plot=True )
photonVariables  = NanoVars.getVariables(        "Photon", postprocessed=True, data=True, plot=True )
photonVarList    = NanoVars.getVariableNameList( "Photon", postprocessed=True, data=True, plot=True )
photonVarString  = NanoVars.getVariableString(   "Photon", postprocessed=True, data=True, plot=True )
genVariables     = NanoVars.getVariables(        "Gen",    postprocessed=True, data=False,             plot=True )
genVarString     = NanoVars.getVariableString(   "Gen",    postprocessed=True, data=False,             plot=True )
genVarList       = NanoVars.getVariableNameList( "Gen",    postprocessed=True, data=False,             plot=True )

# Read variables and sequences
read_variables  = ["weight/F",
                   "nLeptonVetoIsoCorr/I",
                   "nLeptonVetoNoIso/I",
                   "nLeptonTight/I",       "nLeptonTightInvIso/I",
                   "nMuonTight/I",         "nMuonTightInvIso/I",
                   "nElectronTight/I",     "nElectronTightInvIso/I",
                   "nPhotonGood/I",        "nPhotonGoodInvLepIso/I",
                   "nJetGood/I",           "nJetGoodInvLepIso/I",
                   "nBTagGood/I",          "nBTagGoodInvLepIso/I",
                   "nElectronTightInvIso/I",
                   "nMuonTightInvIso/I",
                   "nLeptonTightNoIso/I",
                   "nLeptonTightInvIso/I",
                   "nLeptonVetoInvIsoTight/I",
                   "PV_npvsGood/I",
                   "PV_npvs/I", "PV_npvsGood/I",
                   "nJetGood/I", "nBTagGood/I",
                   "lpTight/F", "lpInvTight/F",
                   "nJet/I", "nBTag/I",
                   "Jet[%s]" %jetVarString,
                   "Lepton[%s]" %leptonVarString,
                   "nLepton/I", "nElectron/I", "nMuon/I",
                   "nLeptonGood/I", "nElectronGood/I", "nMuonGood/I",
                   "nLeptonTight/I", "nElectronTight/I", "nMuonTight/I",
                   "nLeptonVeto/I", "nElectronVeto/I", "nMuonVeto/I",
                   "Photon[%s]" %photonVarString,
                   "nPhoton/I",
                   "nPhotonGood/I",
                   "MET_pt/F", "MET_phi/F", "METSig/F", "ht/F",
                   "mlltight/F", "mllgammatight/F",
                   "mLtight0Gamma/F",
                   "mLinvtight0Gamma/F",
                   "ltight0GammadR/F", "ltight0GammadPhi/F",
                   "m3/F", "m3wBJet/F",
                   "m3inv/F", "m3wBJetinv/F",
                   "mT/F", "mT2lg/F", "mTinv/F", "mT2linvg/F",
                   "photonJetdR/F", "tightLeptonJetdR/F",
                   "reweightHEM/F",
                   "ht/F", "htinv/F",
                  ]

read_variables += [ "%s_photonCat/I"%item for item in photonCatChoices if item != "None" ]
read_variables += [ "%s_photonCatMagic/I"%item for item in photonCatChoices if item != "None" ]

read_variables += map( lambda var: "PhotonMVA0_"              + var, photonVariables )
read_variables += map( lambda var: "PhotonGood0_"             + var, photonVariables )
read_variables += map( lambda var: "PhotonGoodInvLepIso0_"    + var, photonVariables )
read_variables += map( lambda var: "PhotonNoChgIso0_"         + var, photonVariables )
read_variables += map( lambda var: "PhotonNoSieie0_"          + var, photonVariables )
read_variables += map( lambda var: "PhotonNoChgIsoNoSieie0_"  + var, photonVariables )

read_variables += map( lambda var: "MisIDElectron0_"          + var, leptonVariables )

read_variables += map( lambda var: "LeptonGood0_"             + var, leptonVariables )
read_variables += map( lambda var: "LeptonGood1_"             + var, leptonVariables )
read_variables += map( lambda var: "LeptonTightInvIso0_"      + var, leptonVariables )
read_variables += map( lambda var: "LeptonTight0_"            + var, leptonVariables )
read_variables += map( lambda var: "LeptonTight1_"            + var, leptonVariables )
read_variables += map( lambda var: "Bj0_"                     + var, bJetVariables )
read_variables += map( lambda var: "Bj1_"                     + var, bJetVariables )

read_variables_MC = ["isTTGamma/I", "isZWGamma/I", "isTGamma/I", "overlapRemoval/I",
                     "nGenWElectron/I", "nGenWMuon/I", "nGenWTau/I", "nGenW/I", "nGenWJets/I", "nGenWTauElectron/I", "nGenWTauMuon/I", "nGenWTauJets/I",
                     "nGenElectron/I",
                     "nGenMuon/I",
                     "nGenPhoton/I",
                     "nGenBJet/I",
                     "nGenTop/I",
                     "nGenJet/I",
                     "nGenPart/I",
                     "reweightPU/F", "reweightPUDown/F", "reweightPUUp/F", "reweightPUVDown/F", "reweightPUVUp/F",
                     "reweightLeptonTightSF/F", "reweightLeptonTightSFUp/F", "reweightLeptonTightSFDown/F",
                     "reweightLeptonTrackingTightSF/F",
                     "reweightTrigger/F", "reweightTriggerUp/F", "reweightTriggerDown/F",
                     "reweightPhotonSF/F", "reweightPhotonSFUp/F", "reweightPhotonSFDown/F",
                     "reweightPhotonElectronVetoSF/F",
                     "reweightBTag_SF/F", "reweightBTag_SF_b_Down/F", "reweightBTag_SF_b_Up/F", "reweightBTag_SF_l_Down/F", "reweightBTag_SF_l_Up/F",
                     "reweightL1Prefire/F", "reweightL1PrefireUp/F", "reweightL1PrefireDown/F",
                    ]

sequence = []

# Sample definition
if args.year == 2016 and not args.checkOnly:
    mc          = [ TTG_16, TT_pow_16, DY_LO_16, WJets_16, WG_16, ZG_16, rest_16 ]
    data_sample = Run2016
    qcd         = QCD_16
    gjets       = GJets_16

elif args.year == 2017 and not args.checkOnly:
    mc          = [ TTG_17, TT_pow_17, DY_LO_17, WJets_17, WG_17, ZG_17, rest_17 ]
    data_sample = Run2017
    qcd         = QCD_17
    gjets       = GJets_17

elif args.year == 2018 and not args.checkOnly:
    mc          = [ TTG_18, TT_pow_18, DY_LO_18, WJets_18, WG_18, ZG_18, rest_18 ]
    data_sample = Run2018
    qcd         = QCD_18
    gjets       = GJets_18


if not args.checkOnly:
    data_sample.read_variables = [ "event/I", "run/I", "luminosityBlock/I" ]
    data_sample.scale          = 1
    lumi_scale                 = data_sample.lumi * 0.001
    stack                      = Stack( mc, data_sample )

else:
    mc = []
    stack = Stack( mc )


sampleWeight = lambda event, sample: (event.reweightTrigger*event.reweightL1Prefire*event.reweightPU*event.reweightLeptonTightSF*event.reweightLeptonTrackingTightSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF)+((misIDSF_val[args.year].val-1)*(event.nPhotonGood>0)*(event.PhotonGood0_photonCatMagic==2)*event.reweightL1Prefire*event.reweightPU*event.reweightLeptonTightSF*event.reweightLeptonTrackingTightSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF)
weightString = "reweightL1Prefire*reweightTrigger*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF"

weightStringMisIDSF = "(%s)+(%s*%f*((nPhotonGood>0)*(PhotonGood0_photonCatMagic==2)))"%(weightString,weightString,(misIDSF_val[args.year].val-1))

for sample in mc:
    sample.read_variables = read_variables_MC
    sample.weight         = sampleWeight
    sample.scale          = lumi_scale
    if addSF:
        if "DY" in sample.name:
            sample.scale *= DYSF_val[args.year].val
        elif "WJets" in sample.name:
            sample.scale *= WJetsSF_val[args.year].val
        elif "ZG" in sample.name:
            sample.scale *= ZGSF_val[args.year].val
        elif "WG" in sample.name:
            sample.scale *= WGSF_val[args.year].val
        elif "TTG" in sample.name:
            sample.scale *= SSMSF_val[args.year].val

if args.small and not args.checkOnly:
    for sample in stack.samples:
        sample.normalization = 1.
        sample.reduceFiles( factor=20 )
        sample.scale /= sample.normalization

weight_ = lambda event, sample: event.weight
if args.addHEMweight:
    weight_ = lambda event, sample: event.weight*event.reweightHEM

replaceSelection = {
    "nLeptonVetoIsoCorr": "nLeptonVetoNoIso",
    "nLeptonTight":       "nLeptonTightInvIso",
    "nMuonTight":         "nMuonTightInvIso",
    "nElectronTight":     "nElectronTightInvIso",
    "mLtight0Gamma":      "mLinvtight0Gamma",
    "nPhotonGood":        "nPhotonGoodInvLepIso",
    "nJetGood":           "nJetGoodInvLepIso",
    "nBTagGood":          "nBTagGoodInvLepIso",
    "LeptonTight0":       "LeptonTightInvIso0",
}

if regionPlot:
    selection    = setup.selection("MC",   channel="all", **setup.defaultParameters( update=QCD_updates ))
    if args.year == 2017 and args.addBadEEJetVeto: selection["prefix"] += "-BadEEJetVeto"
    preSelection = "&&".join( [ cutInterpreter.cutString( selection["prefix"] ) ] )
else:
    selection        = [ item if not "nBTag" in item else "nBTag0" for item in args.selection.split("-") ]
    preSelection     = "&&".join( [ cutInterpreter.cutString( "-".join(selection) ) ] )

    selection        = [ item if not "nBTag"   in item else "nBTag0"   for item in args.selection.split("-") ]
    selection        = [ item if not "nJet"    in item else "nJet2"    for item in selection ]
    selection        = [ item if not "nPhoton" in item else "nPhoton0" for item in selection ]
    preSelectionTFCR = "&&".join( [ cutInterpreter.cutString( "-".join(selection) ) ] )

    selection        = [ item if not "nJet"    in item else "nJet2"    for item in args.selection.split("-") ]
    selection        = [ item if not "nPhoton" in item else "nPhoton0" for item in selection ]
    preSelectionTFSR = "&&".join( [ cutInterpreter.cutString( "-".join(selection) ) ] )

    for key, val in replaceSelection.items():
        preSelection     = preSelection.replace( key, val )
        preSelectionTFCR = preSelectionTFCR.replace( key, val )

filterCutData = getFilterCut( args.year, isData=True,  skipBadChargedCandidate=True )
filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )
tr            = TriggerSelector( args.year, singleLepton=True )
triggerCutMc  = tr.getSelection( "MC" )
print preSelection
Plot.setDefaults( stack=stack, weight=staticmethod( weight_ ), selectionString=preSelection, addOverFlowBin="upper" )
# Import plots list (AFTER setDefaults!!)
plotListFile = os.path.join( recoPlotsPath, "plotLists", args.plotFile + ".py" )
if not os.path.isfile( plotListFile ):
    logger.info( "Plot file not found: %s", plotListFile )
    sys.exit(1)

plotModule = imp.load_source( "plotLists", os.path.expandvars( plotListFile ) )
from plotLists import plotListData as plotList

# plotList
addPlots = []

# Loop over channels
yields   = {}
allPlots = {}
if args.mode != "None":
    allModes = [ args.mode ]
else:
    allModes = [ "mu", "e" ] if not args.selection.count("nLepTight2") else ["mumutight","muetight","eetight"]
    if args.nJobs != 1:
        allModes = splitList( allModes, args.nJobs)[args.job]

invPlotNames = { 
                "leptonTightInvIso0_pt":              "leptonTight0_pt",
                "leptonTightInvIso0_eta":             "leptonTight0_eta",
                "leptonTightInvIso0_phi":             "leptonTight0_phi",
                "mLinv0PhotonTight":                  "mL0PhotonTight",
                "mLinv0PhotonTight_20ptG120":         "mL0PhotonTight_20ptG120",
                "mLinv0PhotonTight_120ptG220":        "mL0PhotonTight_120ptG220",
                "mLinv0PhotonTight_220ptGinf":        "mL0PhotonTight_220ptGinf",
                "mLinv0PhotonTight_coarse":           "mL0PhotonTight_coarse",
                "mLinv0PhotonTight_20ptG120_coarse":  "mL0PhotonTight_20ptG120_coarse",
                "mLinv0PhotonTight_120ptG220_coarse": "mL0PhotonTight_120ptG220_coarse",
                "mLinv0PhotonTight_220ptGinf_coarse": "mL0PhotonTight_220ptGinf_coarse",
                "mTinv":                              "mT",
                "mTinv_20ptG120":                     "mT_20ptG120",
                "mTinv_120ptG220":                    "mT_120ptG220",
                "mTinv_220ptGinf":                    "mT_220ptGinf",
                "mT2lginv":                           "mT2lg",
                "mT2lginv_20ptG120":                  "mT2lg_20ptG120",
                "mT2lginv_120ptG220":                 "mT2lg_120ptG220",
                "mT2lginv_220ptGinf":                 "mT2lg_220ptGinf",
                "Lpinv":                              "Lp",
                'nPhotonGoodInvIso':                  "nPhotonGood",
                "nElectronGoodInvIso":                "nElectronGood",
                "nMuonGoodInvIso":                    "nMuonGood",
                "nLeptonGoodInvIso":                  "nLeptonGood",
                "nElectronTightInvIso":               "nElectronTight",
                "nMuonTightInvIso":                   "nMuonTight",
                "nLeptonTightInvIso":                 "nLeptonTight",
                "jetGoodinv0_pt_wide":                "jetGood0_pt_wide",
                "jetGoodinv0_pt":                     "jetGood0_pt",
                "jetGoodinv0_eta":                    "jetGood0_eta",
                "jetGoodinv0_phi":                    "jetGood0_phi",
                "jetGoodinv0_neHEF":                  "jetGood0_neHEF",
                "jetGoodinv0_neEmEF":                 "jetGood0_neEmEF",
                "jetGoodinv0_chEmHEF":                "jetGood0_chEmHEF",
                "jetGoodinv0_chHEF":                  "jetGood0_chHEF",
                "jetGoodinv1_pt_wide":                "jetGood1_pt_wide",
                "jetGoodinv1_pt":                     "jetGood1_pt",
                "jetGoodinv1_eta":                    "jetGood1_eta",
                "jetGoodinv1_phi":                    "jetGood1_phi",
                "jetGoodinv1_neHEF":                  "jetGood1_neHEF",
                "jetGoodinv1_neEmEF":                 "jetGood1_neEmEF",
                "jetGoodinv1_chEmHEF":                "jetGood1_chEmHEF",
                "jetGoodinv1_chHEF":                  "jetGood1_chHEF",
                "nJetGoodInvIso":                     "nJetGood",
                "nJetGoodInvIso_wide":                "nJetGood_wide",
                "nJetGoodInvIso_semi":                "nJetGood_semi",
                "nJetGoodInvIso_semi2":               "nJetGood_semi2",
                "nJetGoodInvIso_semi3":               "nJetGood_semi3",
                "nJetGoodInvIso_20ptG120":            "nJetGood_20ptG120",
                "nJetGoodInvIso_120ptG220":           "nJetGood_120ptG220",
                "nJetGoodInvIso_220ptGinf":           "nJetGood_220ptGinf",
                "nBJetGoodInvIso":                    "nBJetGood",
                "nBJetGoodInvIso_20ptG120":           "nBJetGood_20ptG120",
                "nBJetGoodInvIso_120ptG220":          "nBJetGood_120ptG220",
                "nBJetGoodInvIso_220ptGinf":          "nBJetGood_220ptGinf",
                "htinv":                              "ht",
                "m3inv":                              "m3",
                "m3inv_coarse":                       "m3_coarse",
                "m3inv_20ptG120":                     "m3_20ptG120",
                "m3inv_120ptG220":                    "m3_120ptG220",
                "m3inv_220ptGinf":                    "m3_220ptGinf",
                "m3inv_20ptG120_coarse":              "m3_20ptG120_coarse",
                "m3inv_120ptG220_coarse":             "m3_120ptG220_coarse",
                "m3inv_220ptGinf_coarse":             "m3_220ptGinf_coarse",
                "leptonTightinv0_hoe":                "leptonTight0_hoe",
                "leptonTightinv0_eInvMinusPInv":      "leptonTight0_eInvMinusPInv",
                "leptonTightinv0_convVeto":           "leptonTight0_convVeto",
                "leptonTightinv0_sieie":              "leptonTight0_sieie",
                "leptonTightinv0_sip3d":                    "leptonTight0_sip3d",
                "leptonTightinv0_lostHits":                 "leptonTight0_lostHits",
                "leptonTightinv0_dr03EcalRecHitSumEt":      "leptonTight0_dr03EcalRecHitSumEt",
                "leptonTightinv0_dr03HcalDepth1TowerSumEt": "leptonTight0_dr03HcalDepth1TowerSumEt",
                "leptonTightinv0_dr03TkSumPt":              "leptonTight0_dr03TkSumPt",
                "leptonTightinv0_dxy":                      "leptonTight0_dxy",
                "leptonTightinv0_dz":                       "leptonTight0_dz",
                "leptonTightinv0_ip3d":                     "leptonTight0_ip3d",
                "leptonTightinv0_r9":                       "leptonTight0_r9",
                "mindRJetTightLeptoninv":             "mindRJetTightLepton",
                "dRLTight0PhotonGood0inv":            "dRLTight0PhotonGood0",
                "dPhiLTight0PhotonGood0inv":          "dPhiLTight0PhotonGood0",
 }

bSelection = [ sel for sel in args.selection.split("-") if "nBTag" in sel ][:1]

for index, mode in enumerate( allModes ):
    logger.info( "Computing plots for mode %s", mode )

    print cutInterpreter.cutString( mode + "Inv" )
    plots  = []
    plots += plotList
    plots += getYieldPlots()
    plots += addPlots

    # some plots make no sense to create histos from
    plots = [ plot for plot in plots if plot.name not in invPlotNames.values() ]
    plots = [ plot for plot in plots if not ("nBJet" in plot.name and "ptG" in plot.name) ]
    if bSelection and "p" in bSelection[0]: #remove bjet plots if more than 1 bjet bin in plots (can not be modeled by data driven QCD estimate)
        plots = [ plot for plot in plots if not "nBJet" in plot.name ]

    for plot in plots:
        if plot.name in invPlotNames.keys():
            plot.name = invPlotNames[plot.name]

    if not args.overwrite:
        allPlots = []
        for plot in plots:
            if dirDB.contains("_".join( ["qcdHisto" if not args.addHEMweight else "qcdHisto_hemWeight", args.selection, plot.name, str(args.year), mode, "small" if args.small else "full"] + map( str, plot.binning ) )):
                if not "yield" in plot.name: continue
                qcdYield =  dirDB.get("_".join( ["qcdHisto" if not args.addHEMweight else "qcdHisto_hemWeight", args.selection, plot.name, str(args.year), mode, "small" if args.small else "full"] + map( str, plot.binning ) )).Integral()
                print("QCD estimate for plot %s in year %i, selection %s, mode %s: %f"%(plot.name, args.year, args.selection, mode, float(qcdYield)))
            else:
                print("Plot for year %i and selection %s and mode %s not cached!"%(args.year, args.selection, mode))
                allPlots.append(plot)
        if args.checkOnly or not allPlots: sys.exit(0)
        plots = allPlots

    # Define selections
    isoleptonSelection = cutInterpreter.cutString( mode )
    leptonSelection    = cutInterpreter.cutString( mode + "Inv" )

    data_sample.setSelectionString( [ filterCutData, leptonSelection ] )
    for sample in mc + signals:
        sample.setSelectionString( [ filterCutMc, leptonSelection, triggerCutMc, "overlapRemoval==1" ] )

    plotting.fill( plots, read_variables=read_variables, sequence=sequence )

    # Transfer factor
    if regionPlot:
        # get cached transferfactors
        estimators      = EstimatorList( setup, processes=["QCD-DD"] )
        estimate        = getattr(estimators, "QCD-DD")
        estimate.isData = False
        estimate.initCache(setup.defaultCacheDir())

        transFacQCD = estimate.cachedTransferFactor(mode, setup, save=True, overwrite=False, checkOnly=False)
        transFacQCD = transFacQCD.val
        print transFacQCD
        logger.info("Calculated transfer factor for inclusive region: %f"%transFacQCD)

    else:
        preSelectionSRData = "&&".join( [ preSelectionTFSR, filterCutData, isoleptonSelection ] )
        preSelectionCRData = "&&".join( [ preSelectionTFCR, filterCutData, leptonSelection    ] )
        preSelectionSRMC   = "&&".join( [ preSelectionTFSR, filterCutMc,   isoleptonSelection, triggerCutMc, "overlapRemoval==1"  ] )
        preSelectionCRMC   = "&&".join( [ preSelectionTFCR, filterCutMc,   leptonSelection,    triggerCutMc, "overlapRemoval==1"  ] )

        # Calculate yields for Data
        data_sample.setSelectionString( "(1)" )
        data_sample.setWeightString( "(1)" )
        yield_data_CR  = data_sample.getYieldFromDraw( selectionString=preSelectionCRData, weightString="weight" )["val"]
        yield_data_SR  = data_sample.getYieldFromDraw( selectionString=preSelectionSRData, weightString="weight" )["val"]
        yield_mc_CR    = 0
        yield_mc_SR    = 0

        for sample in mc:
            sample.setSelectionString( "(1)" )
            sample.setWeightString( "(1)" )
            y_CR = sample.getYieldFromDraw( selectionString=preSelectionCRMC, weightString="weight*%f*%s"%(sample.scale,weightStringMisIDSF) )["val"]
            y_SR = sample.getYieldFromDraw( selectionString=preSelectionSRMC, weightString="weight*%f*%s"%(sample.scale,weightStringMisIDSF) )["val"]

            if addSF:
                if "DY" in sample.name:
                    y_CR *= DYSF_val[setup.year] #add DY SF
                    y_SR *= DYSF_val[setup.year] #add DY SF
                elif "WJets" in sample.name:
                    y_CR *= WJetsSF_val[setup.year] #add WJets SF
                    y_SR *= WJetsSF_val[setup.year] #add WJets SF
                elif "ZG" in sample.name:
                    y_CR *= ZGSF_val[setup.year] #add ZGamma SF
                    y_SR *= ZGSF_val[setup.year] #add ZGamma SF
                elif "WG" in sample.name:
                    y_CR *= WGSF_val[setup.year] #add WGamma SF
                    y_SR *= WGSF_val[setup.year] #add WGamma SF
                elif "TTG" in sample.name:
                    y_CR *= SSMSF_val[setup.year] #add SSM
                    y_SR *= SSMSF_val[setup.year] #add SSM


            yield_mc_CR += y_CR
            yield_mc_SR += y_SR

        transFacQCD = (yield_data_SR - yield_mc_SR) / (yield_data_CR - yield_mc_CR) if yield_mc_CR != yield_data_CR else 0.
        if transFacQCD < 0: transFacQCD = 0
        logger.info( "Inclusive TF: %f"%transFacQCD )

    for plot in plots:
        qcdHist  = copy.deepcopy(plot.histos[1][0])
        for h in plot.histos[0]:
            qcdHist.Add( h, -1 )

        # remove negative bins
        for i in range(qcdHist.GetNbinsX()):
            if qcdHist.GetBinContent(i+1) < 0:
                qcdHist.SetBinContent(i+1, 0)

        qcdHist.Scale( transFacQCD )

        cacheName = "_".join( ["qcdHisto" if not args.addHEMweight else "qcdHisto_hemWeight", args.selection, plot.name, str(args.year), mode, "small" if args.small else "full"] + map( str, plot.binning ) )
        logger.info( "Adding QCD plot for %s for mode %s"%(plot.name, mode) )
        dirDB.add( cacheName, qcdHist, overwrite=True )
