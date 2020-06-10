# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetHatchesLineWidth(5)

import os, sys, copy
from math                             import sqrt

# RootTools
from RootTools.core.standard           import *

# Analysis
from Analysis.Tools.metFilters         import getFilterCut
from Analysis.Tools.helpers            import add_histos

# Internal Imports
from TTGammaEFT.Tools.user             import plot_directory, cache_directory
from TTGammaEFT.Tools.cutInterpreter   import cutInterpreter
from TTGammaEFT.Tools.TriggerSelector  import TriggerSelector

from TTGammaEFT.Analysis.Setup         import Setup
from TTGammaEFT.Analysis.SetupHelpers  import *
from TTGammaEFT.Analysis.EstimatorList import EstimatorList

from TTGammaEFT.Samples.color          import color
from Analysis.Tools.MergingDirDB      import MergingDirDB

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

addSF = True
ptBins  = [0, 45, 65, 80, 100, 120, -1]
etaBins = [0, 1.479, 1.7, 2.1, -1]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                        help="Log level for logging")
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv26_v1",                                             help="plot sub-directory")
argParser.add_argument("--selection",          action="store",      default="WJets2", type=str,                                              help="reco region")
argParser.add_argument("--addCut",             action="store",      default=None, type=str,                                                  help="additional cuts")
argParser.add_argument("--variable",           action="store",      default="LeptonTight0_eta", type=str,                                    help="variable to plot")
argParser.add_argument("--variation",         action="store",      default=None,                                                     help="Which systematic variation to run. Don't specify for producing plots.")
argParser.add_argument("--binning",            action="store",      default=[20,-2.4,2.4],  type=float, nargs="*",                           help="binning of plots")
argParser.add_argument("--year",               action="store",      default=2016,   type=int,  choices=[2016,2017,2018],                     help="Which year to plot?")
argParser.add_argument("--mode",               action="store",      default="all",  type=str,  choices=["mu", "e", "all"],                   help="lepton selection")
argParser.add_argument("--overwrite",          action="store_true",                                                                          help="overwrite cache?")
args = argParser.parse_args()

args.binning[0] = int(args.binning[0])

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile=None )
logger_rt = logger_rt.get_logger( args.logLevel, logFile=None )

def jetSelectionModifier( sys, returntype = "func"):
    # Need to make sure all jet variations of the following observables are in the ntuple
    variiedJetObservables = ["nJetGoodInvSieie", "nBTagGoodInvSieie", "&m3", "&ht"]
    if returntype == "func":
        def changeCut_( string ):
            for s in variiedJetObservables:
                string = string.replace(s, s+"_"+sys)
            return string
        return changeCut_
    elif returntype == "list":
        return [ v+"_"+sys for v in variiedJetObservables ] # change that after next pp

def muonSelectionModifier( sys, returntype = "func"):
    # Need to make sure all muon variations of the following observables are in the ntuple
    variiedMuonObservables = ['nMuonVeto','nMuonTight','nLeptonVetoIsoCorr','nLeptonTight','mllgammatight','mLtight0GammaNoSieieNoChgIso','mLtight0Gamma','mlltight']
    if returntype == "func":
        def changeCut_( string ):
            for s in variiedMuonObservables:
                string = string.replace(s, s+"_"+sys)
            string = string.replace("triggered", "triggered"+"_"+sys)
            return string
        return changeCut_
    elif returntype == "list":
        return [ v+"_"+sys for v in variiedMuonObservables ] # change that after next pp

def eleSelectionModifier( sys, returntype = "func"):
    # Need to make sure all Ele variations of the following observables are in the ntuple
    variiedEleObservables = ['nPhotonGood', 'nPhotonNoChgIsoNoSieie','nElectronVeto', 'nElectronVetoIsoCorr', 'nElectronTight', 'nLeptonVetoIsoCorr','nLeptonTight','mllgammatight','mLtight0GammaNoSieieNoChgIso','mLtight0Gamma','mlltight']
#    variiedEleObservables = ['nElectronVeto', 'nElectronVetoIsoCorr', 'nElectronTight', 'nLeptonVetoIsoCorr','nLeptonTight','mllgammatight','mLtight0GammaNoSieieNoChgIso','mLtight0Gamma','mlltight']
    if returntype == "func":
        def changeCut_( string ):
            for s in variiedEleObservables:
                string = string.replace(s, s+"_"+sys)
            string = string.replace("PhotonNoChgIsoNoSieie0", "PhotonNoChgIsoNoSieie0"+"_"+sys)
            pt = "PhotonNoChgIsoNoSieie0"+"_"+sys+"_pt"
            string = string.replace(pt, "0.5*(%s+%s)"%(pt+"_totalUp",pt+"_totalDown"))
            string = string.replace("triggered", "triggered"+"_"+sys)
            return string
        return changeCut_
    elif returntype == "list":
        return [ v+"_"+sys for v in variiedEleObservables ] # change that after next pp

def metSelectionModifier( sys, returntype = 'func'):
    #Need to make sure all MET variations of the following observables are in the ntuple
    variiedMetObservables = ["nJetGoodInvSieie", "nBTagGoodInvSieie", "mT", "MET_pt"]
    if returntype == "func":
        def changeCut_( string ):
            for s in variiedMetObservables:
                string = string.replace(s, s+'_'+sys)
            return string
        return changeCut_
    elif returntype == "list":
        return [ v+'_'+sys for v in variiedMetObservables ]

# these are the nominal MC weights we always apply
nominalMCWeights = ["weight", "reweightTrigger", "reweightL1Prefire", "reweightPU", "reweightLeptonTightSF", "reweightLeptonTrackingTightSF", "reweightPhotonSF", "reweightPhotonElectronVetoSF", "reweightBTag_SF"]

if "2" in args.selection and not "2p" in args.selection:
    DYSF_val    = DY2SF_val
    misIDSF_val = misID2SF_val
    WGSF_val    = WG2SF_val
    ZGSF_val    = ZG2SF_val
    QCDSF_val   = QCD2SF_val
elif "3" in args.selection and not "3p" in args.selection:
    DYSF_val    = DY3SF_val
    misIDSF_val = misID3SF_val
    WGSF_val    = WG3SF_val
    ZGSF_val    = ZG3SF_val
    QCDSF_val   = QCD3SF_val
elif "4" in args.selection and not "4p" in args.selection:
    DYSF_val    = DY4SF_val
    misIDSF_val = misID4SF_val
    WGSF_val    = WG4SF_val
    ZGSF_val    = ZG4SF_val
    QCDSF_val   = QCD4SF_val
elif "5" in args.selection:
    DYSF_val    = DY5SF_val
    misIDSF_val = misID5SF_val
    WGSF_val    = WG5SF_val
    ZGSF_val    = ZG5SF_val
    QCDSF_val   = QCD5SF_val
elif "2p" in args.selection:
    DYSF_val    = DY2pSF_val
    misIDSF_val = misID2pSF_val
    WGSF_val    = WG2pSF_val
    ZGSF_val    = ZG2pSF_val
    QCDSF_val   = QCD2pSF_val
elif "3p" in args.selection:
    DYSF_val    = DY3pSF_val
    misIDSF_val = misID3pSF_val
    WGSF_val    = WG3pSF_val
    ZGSF_val    = ZG3pSF_val
    QCDSF_val   = QCD3pSF_val
elif "4p" in args.selection:
    DYSF_val    = DY4pSF_val
    misIDSF_val = misID4pSF_val
    WGSF_val    = WG4pSF_val
    ZGSF_val    = ZG4pSF_val
    QCDSF_val   = QCD4pSF_val

QCDTF_updates_2J = copy.deepcopy(QCDTF_updates)

# Accounting for 
leptonPtCutVar = "LeptonTightInvIso0_pt"
if args.mode == "e":
    leptonEtaCutVar = "abs(LeptonTightInvIso0_eta+LeptonTightInvIso0_deltaEtaSC)"
else:
    leptonEtaCutVar = "abs(LeptonTightInvIso0_eta)"

# weight the MC according to a variation
def MC_WEIGHT( variation, lumi_scale, returntype = "string"):
    variiedMCWeights = list(nominalMCWeights)   # deep copy
    if variation.has_key("replaceWeight"):
        for i_w, w in enumerate(variiedMCWeights):
            if w == variation["replaceWeight"][0]:
                variiedMCWeights[i_w] = variation["replaceWeight"][1]
                break
        # Let"s make sure we don't screw it up ... because we mostly do.
        if variiedMCWeights==nominalMCWeights:
            raise RuntimeError( "Tried to change weight %s to %s but didn't find it in list %r" % ( variation["replaceWeight"][0], variation["replaceWeight"][1], variiedMCWeights ))
    # multiply strings for ROOT weights
    weightString = "*".join(variiedMCWeights)
    weightString += "*%f"%lumi_scale
    if returntype == "string":
        return "((%s)+(%s*%f*((nPhotonGood>0)*(PhotonNoChgIsoNoSieie0_photonCatMagic==2))))"%(weightString,weightString,(misIDSF_val[args.year].val-1))
    if returntype == "invIso":
        weightStringInv = weightString.replace("reweightTrigger", "reweightInvIsoTrigger")
        return "((%s)+(%s*%f*((nPhotonNoChgIsoNoSieieInvLepIso0>0)*(PhotonNoChgIsoNoSieieInvLepIso0_photonCatMagic==2))))"%(weightStringInv,weightStringInv,(misIDSF_val[args.year].val-1))
    # create a function that multiplies the attributes of the event
    elif returntype == "func":
        getters = map( operator.attrgetter, variiedMCWeights)
        def weight_( event, sample):
            return reduce(operator.mul, [g(event) for g in getters], 1)
        return weight_
    elif returntype == "list":
        return variiedMCWeights

def data_weight( event, sample ):
    return event.weight

data_weight_string = "weight"

nominalPuWeight, upPUWeight, downPUWeight = "reweightPU", "reweightPUUp", "reweightPUDown"

# Text on the plots
def drawObjects( lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    line = (0.65, 0.95, "%3.1f fb{}^{-1} (13 TeV)" % lumi_scale)
    lines = [
      (0.15, 0.95, "CMS #bf{#it{Preliminary}}"),
      line
    ]
    return [tex.DrawLatex(*l) for l in lines]

# Define all systematic variations
variations = {
    "central"                   : {"read_variables": [ "%s/F"%v for v in nominalMCWeights ]},
    "TriggerUp"                 : {"replaceWeight":("reweightTrigger","reweightTriggerUp"),                               "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightTriggerUp"] ]},
    "TriggerDown"               : {"replaceWeight":("reweightTrigger","reweightTriggerDown"),                             "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightTriggerDown"] ]},
    "L1PrefireUp"               : {"replaceWeight":("reweightL1Prefire","reweightL1PrefireUp"),                           "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightL1PrefireUp"] ]},
    "L1PrefireDown"             : {"replaceWeight":("reweightL1Prefire","reweightL1PrefireDown"),                         "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightL1PrefireDown"] ]},
    "PUUp"                      : {"replaceWeight":(nominalPuWeight,upPUWeight),                                          "read_variables" : [ "%s/F"%v for v in nominalMCWeights + [upPUWeight] ]},
    "PUDown"                    : {"replaceWeight":(nominalPuWeight,downPUWeight),                                        "read_variables" : [ "%s/F"%v for v in nominalMCWeights + [downPUWeight] ]},
    "LeptonSFTightUp"           : {"replaceWeight":("reweightLeptonTightSF","reweightLeptonTightSFUp"),                   "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightLeptonTightSFUp"]]},
    "LeptonSFTightDown"         : {"replaceWeight":("reweightLeptonTightSF","reweightLeptonTightSFDown"),                 "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightLeptonTightSFDown"]]},
    "LeptonSFTrackingTightUp"   : {"replaceWeight":("reweightLeptonTrackingTightSF","reweightLeptonTrackingTightSFUp"),   "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightLeptonTrackingTightSFUp"]]},
    "LeptonSFTrackingTightDown" : {"replaceWeight":("reweightLeptonTrackingTightSF","reweightLeptonTrackingTightSFDown"), "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightLeptonTrackingTightSFDown"]]},
    "PhotonSFUp"                : {"replaceWeight":("reweightPhotonSF","reweightPhotonSFUp"),                             "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightPhotonSFUp"]]},
    "PhotonSFDown"              : {"replaceWeight":("reweightPhotonSF","reweightPhotonSFDown"),                           "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightPhotonSFDown"]]},
    "PhotonElectronVetoSFUp"    : {"replaceWeight":("reweightPhotonElectronVetoSF","reweightPhotonElectronVetoSFUp"),     "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightPhotonElectronVetoSFUp"]]},
    "PhotonElectronVetoSFDown"  : {"replaceWeight":("reweightPhotonElectronVetoSF","reweightPhotonElectronVetoSFDown"),   "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightPhotonElectronVetoSFDown"]]},
    "eTotalUp"                  : {"selectionModifier":eleSelectionModifier("eTotalUp"),                                  "read_variables" : [ "%s/F"%v for v in nominalMCWeights + eleSelectionModifier("eTotalUp","list")]},
    "eTotalDown"                : {"selectionModifier":eleSelectionModifier("eTotalDown"),                               "read_variables" : [ "%s/F"%v for v in nominalMCWeights + eleSelectionModifier("eTotalDown","list")]},
    "muTotalUp"                 : {"selectionModifier":muonSelectionModifier("muTotalUp"),                                "read_variables" : [ "%s/F"%v for v in nominalMCWeights + muonSelectionModifier("muTotalUp","list")]},
    "muTotalDown"               : {"selectionModifier":muonSelectionModifier("muTotalDown"),                              "read_variables" : [ "%s/F"%v for v in nominalMCWeights + muonSelectionModifier("muTotalDown","list")]},
    "jerUp"                     : {"selectionModifier":jetSelectionModifier("jerUp"),                                     "read_variables" : [ "%s/F"%v for v in nominalMCWeights + jetSelectionModifier("jerUp","list")]},
    "jerDown"                   : {"selectionModifier":jetSelectionModifier("jerDown"),                                   "read_variables" : [ "%s/F"%v for v in nominalMCWeights + jetSelectionModifier("jerDown","list")]},
    "jesTotalUp"                : {"selectionModifier":jetSelectionModifier("jesTotalUp"),                                "read_variables" : [ "%s/F"%v for v in nominalMCWeights + jetSelectionModifier("jesTotalUp","list")]},
    "jesTotalDown"              : {"selectionModifier":jetSelectionModifier("jesTotalDown"),                              "read_variables" : [ "%s/F"%v for v in nominalMCWeights + jetSelectionModifier("jesTotalDown","list")]},
#    "unclustEnUp"               : {"selectionModifier":metSelectionModifier("unclustEnUp"),                               "read_variables" : [ "%s/F"%v for v in nominalMCWeights]},
#    "unclustEnDown"             : {"selectionModifier":metSelectionModifier("unclustEnDown"),                             "read_variables" : [ "%s/F"%v for v in nominalMCWeights]},
    "BTag_SF_b_Down"            : {"replaceWeight":("reweightBTag_SF","reweightBTag_SF_b_Down"),                          "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightBTag_SF_b_Down"]]},  
    "BTag_SF_b_Up"              : {"replaceWeight":("reweightBTag_SF","reweightBTag_SF_b_Up"),                            "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightBTag_SF_b_Up"] ]},
    "BTag_SF_l_Down"            : {"replaceWeight":("reweightBTag_SF","reweightBTag_SF_l_Down"),                          "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightBTag_SF_l_Down"]]},
    "BTag_SF_l_Up"              : {"replaceWeight":("reweightBTag_SF","reweightBTag_SF_l_Up"),                            "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightBTag_SF_l_Up"] ]},
}

selection_systematics = [ "jerUp", "jerDown", "jesTotalUp", "jesTotalDown" ]
variables_with_selection_systematics = [ "nJetGoodInvSieie", "nBTagGoodInvSieie", "ht", "m3" ]
metselection_systematics = [ "unclustEnUp", "unclustEnDown" ]
metvariables_with_selection_systematics = [ "MET_pt", "mT" ]
eleselection_systematics = [ "eTotalUp", "eTotalDown", "muTotalUp", "muTotalDown" ]
elevariables_with_selection_systematics = [ "nPhotonNoChgIsoNoSieie" ]
phoselection_systematics = [ "eTotalUp", "eTotalDown" ]
phovariables_with_selection_systematics = [ "nPhotonNoChgIsoNoSieie" ]
# Add a default selection modifier that does nothing
for key, variation in variations.iteritems():
    if not variation.has_key("selectionModifier"):
        variation["selectionModifier"] = lambda string:string
    if not variation.has_key("read_variables"):
        variation["read_variables"] = [] 

# Check if we know the variation
if args.variation is not None and args.variation not in variations.keys():
    raise RuntimeError( "Variation %s not among the known: %s", args.variation, ",".join( variation.keys() ) )

# Sample definition
os.environ["gammaSkim"]="False" #always false for QCD estimate
if args.year == 2016:
    from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed  import *
    from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import *
    mc          = [ TTG_16, Top_16, DY_LO_16, WJets_16, WG_16, ZG_16, rest_16 ]
    qcd         = QCD_16
    data_sample = Run2016
elif args.year == 2017:
    from TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed    import *
    from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import *
    mc          = [ TTG_17, Top_17, DY_LO_17, WJets_17, WG_17, ZG_17, rest_17 ]
    qcd         = QCD_17
    data_sample = Run2017
elif args.year == 2018:
    from TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed  import *
    from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import *
    mc          = [ TTG_18, Top_18, DY_LO_18, WJets_18, WG_18, ZG_18, rest_18 ]
    qcd         = QCD_18
    data_sample = Run2018

read_variables_MC = ["isTTGamma/I", "isZWGamma/I", "isTGamma/I", "overlapRemoval/I",
                     "reweightPU/F", "reweightPUDown/F", "reweightPUUp/F", "reweightPUVDown/F", "reweightPUVUp/F",
                     "reweightLeptonTightSF/F", "reweightLeptonTightSFUp/F", "reweightLeptonTightSFDown/F",
                     "reweightLeptonTrackingTightSF/F",
                     "reweightTrigger/F", "reweightTriggerUp/F", "reweightTriggerDown/F",
                     "reweightPhotonSF/F", "reweightPhotonSFUp/F", "reweightPhotonSFDown/F",
                     "reweightPhotonElectronVetoSF/F",
                     "reweightBTag_SF/F", "reweightBTag_SF_b_Down/F", "reweightBTag_SF_b_Up/F", "reweightBTag_SF_l_Down/F", "reweightBTag_SF_l_Up/F",
                     'reweightL1Prefire/F', 'reweightL1PrefireUp/F', 'reweightL1PrefireDown/F',
                    ]
read_variables = [ "weight/F",
                   "mT/F",
                   "mTinv/F",
                 ]

lumi_scale   = data_sample.lumi * 0.001

filterCutData = getFilterCut( args.year, isData=True,  skipBadChargedCandidate=True )
filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )

blinding = []
if args.year != 2016 and not "VGfake" in args.selection:
    if "lowSieieNoChgIso" in args.addCut:
        blinding += [ cutInterpreter.cutString( "lowSieieHighChgIso" ) ]
    if "lowChgIsoNoSieie" in args.addCut:
        blinding += [ cutInterpreter.cutString( "lowChgIsoHighSieie" ) ]


data_sample.setSelectionString( [filterCutData]+blinding )
data_sample.setWeightString( "weight" )

for s in mc:
    s.setSelectionString( [ filterCutMc, "overlapRemoval==1" ] )
    s.read_variables = read_variables_MC

replaceSelection = {
    "nLeptonVetoIsoCorr": "nLeptonVetoNoIso",
    "nLeptonTight":       "nLeptonTightInvIso",
    "nMuonTight":         "nMuonTightInvIso",
    "nElectronTight":     "nElectronTightInvIso",
    "mLtight0Gamma":      "mLinvtight0Gamma",
    "nPhotonGood":        "nPhotonGoodInvLepIso",
    "nJetGood":           "nJetGoodInvLepIso",
    "nBTagGood":          "nBTagGoodInvLepIso",
    "mT":                 "mTinv",
    "m3":                 "m3inv",
    "ht":                 "htinv",
    "LeptonTight0_eta":   "LeptonTightInvIso0_eta",
    "LeptonTight0_pt":    "LeptonTightInvIso0_pt",
    "PhotonGood0_pt":    "PhotonGoodInvLepIso0_pt",
    "PhotonGood0_phi":   "PhotonGoodInvLepIso0_phi",
    "PhotonGood0_eta":   "PhotonGoodInvLepIso0_eta",
    "PhotonNoChgIsoNoSieie0": "PhotonNoChgIsoNoSieieInvLepIso0",
}


if len(args.selection.split("-")) == 1 and args.selection in allRegions.keys():
    print( "Plotting region from SetupHelpers: %s"%args.selection )

    setup = Setup( year=args.year, photonSelection=False, checkOnly=False, runOnLxPlus=False ) #photonselection always false for qcd estimate
    setup = setup.sysClone( parameters=allRegions[args.selection]["parameters"] )

    allSelection  = setup.selection( "MC", channel="all", **setup.defaultParameters() )["prefix"]
    selection     = allSelection + "-" + args.mode
    selection     = cutInterpreter.cutString( selection )
    if args.addCut:
        selection += "&&" + cutInterpreter.cutString( args.addCut )
    selection += "&&triggered==1"
    print( "Using selection string: %s"%selection )

    preSelection  = setup.selection("MC",   channel="all", **setup.defaultParameters(update=QCD_updates))["prefix"]
    preSelection += "-" + args.mode + "Inv"
    preSelection  = cutInterpreter.cutString( preSelection )
    if args.addCut:
        addSel = cutInterpreter.cutString( args.addCut )
        for iso, invIso in replaceSelection.iteritems():
            addSel = addSel.replace(iso,invIso)
        preSelection += "&&" + addSel
    preSelection += "&&triggeredInvIso==1"
    print
    print preSelection
    print
else:
    raise Exception("Region not implemented")

replaceLabel = {
    "PhotonNoChgIsoNoSieie0_sieie": "#sigma_{i#eta i#eta}(#gamma)",
    "LeptonTight0_eta": "#eta(l_{0})",
    "MET_pt": "E^{miss}_{T} (GeV)",
    "mT": "M_{T} (GeV)",
    "mLtight0Gamma": "M(#gamma,l_{0}) (GeV)",
}

replaceVariable = {
    "ltight0GammadR":     "linvtight0GammadR",
    "ltight0GammadPhi":   "linvtight0GammadPhi",
    "mT":                 "mTinv",
    "m3":                 "m3inv",
    "ht":                 "htinv",
    "lpTight":            "lpInvTight",
    "mLtight0Gamma":      "mLinvtight0Gamma",
    "LeptonTight0_phi":   "LeptonTightInvIso0_phi",
    "LeptonTight0_eta":   "LeptonTightInvIso0_eta",
    "LeptonTight0_pt":    "LeptonTightInvIso0_pt",
    "PhotonGood0_pt":    "PhotonGoodInvLepIso0_pt",
    "PhotonGood0_phi":   "PhotonGoodInvLepIso0_phi",
    "PhotonGood0_eta":   "PhotonGoodInvLepIso0_eta",
    "PhotonNoChgIsoNoSieie0_sieie": "PhotonNoChgIsoNoSieieInvLepIso0_sieie",
    "cos(LeptonTight0_phi-MET_phi)":         "cos(LeptonTightInvIso0_phi-MET_phi)",
    "cos(LeptonTight0_phi-JetGood0_phi)":    "cos(LeptonTightInvIso0_phi-JetGoodInvLepIso0_phi)",
    "cos(LeptonTight0_phi-JetGood1_phi)":    "cos(LeptonTightInvIso0_phi-JetGoodInvLepIso1_phi)",
    "cos(JetGood0_phi-MET_phi)":             "cos(JetGoodInvLepIso0_phi-MET_phi)",
    "cos(JetGood0_phi-JetGood1_phi)":        "cos(JetGoodInvLepIso0_phi-JetGoodInvLepIso1_phi)",
}

invVariable = replaceVariable[args.variable] if args.variable in replaceVariable.keys() else args.variable

# Fire up the cache
cache_dir = os.path.join(cache_directory, "systematicPlots", str(args.year), args.selection)
dirDB = MergingDirDB(cache_dir)
if not dirDB: raise

plots = []
if args.variation == "central":

    # histo data
    key = (data_sample.name, "AR", args.variable, "_".join(map(str,args.binning)), data_sample.weightString, data_sample.selectionString, selection)
    if not dirDB.contains(key) or args.overwrite:
        dataHist = data_sample.get1DHistoFromDraw( args.variable, binning=args.binning, selectionString=selection, addOverFlowBin="upper" )
        dirDB.add(key, dataHist.Clone("dataAR"), overwrite=True)
    else:
        dataHist = dirDB.get(key)

    for s in mc:
        selectionModifier = variations[args.variation]["selectionModifier"]
        normalization_selection_string = selectionModifier(selection)
        mc_normalization_weight_string = MC_WEIGHT(variations[args.variation], lumi_scale, returntype="string")
        s.setWeightString( mc_normalization_weight_string )
        key = (s.name, "AR", args.variable, "_".join(map(str,args.binning)), s.weightString, s.selectionString, normalization_selection_string, args.variation)
        if not dirDB.contains(key) or args.overwrite:
            mcHist = s.get1DHistoFromDraw( args.variable, binning=args.binning, selectionString=selection, addOverFlowBin="upper" )
            dirDB.add(key, mcHist.Clone(s.name+"AR"), overwrite=True)

    key = ("QCD-DD", "AR", args.variable, "_".join(map(str,args.binning)), selection)
    if not dirDB.contains(key) or args.overwrite:
        qcdHist = dataHist.Clone("qcd")
        qcdHist.Scale(0)

        # get cached transferfactors
        estimators = EstimatorList( setup, processes=["QCD-DD"] )
        estimate   = getattr(estimators, "QCD-DD")
        estimate.initCache(setup.defaultCacheDir())

        mc_normalization_weight_string = MC_WEIGHT(variations[args.variation], lumi_scale, returntype="invIso")
        for i_pt, pt in enumerate(ptBins[:-1]):
            for i_eta, eta in enumerate(etaBins[:-1]):
                etaLow, etaHigh = eta, etaBins[i_eta+1]
                ptLow, ptHigh   = pt,  ptBins[i_pt+1]

                # Remove that for now
                # define the 2016 e-channel QCD sideband in barrel only (bad mT fit in EC)
                if False and args.mode == "e" and args.year == 2016 and (etaHigh > 1.479 or etaHigh < 0):
                    leptonPtEtaCut  = [ leptonEtaCutVar + ">=0", leptonPtCutVar + ">=" + str(ptLow) ]
                    leptonPtEtaCut += [ leptonEtaCutVar + "<1.479" ]
                    if ptHigh > 0:  leptonPtEtaCut += [ leptonPtCutVar + "<" + str(ptHigh) ]
                else:
                    leptonPtEtaCut = [ leptonEtaCutVar + ">=" + str(etaLow), leptonPtCutVar + ">=" + str(ptLow) ]
                    if etaHigh > 0: leptonPtEtaCut += [ leptonEtaCutVar + "<" + str(etaHigh) ]
                    if ptHigh > 0:  leptonPtEtaCut += [ leptonPtCutVar + "<" + str(ptHigh) ]

                leptonPtEtaCut = "&&".join( [preSelection] + leptonPtEtaCut )
    
                print "Running histograms for qcd selection:"
                print leptonPtEtaCut

                # histos
                key = (data_sample.name, "SB", args.variable, "_".join(map(str,args.binning)), data_sample.weightString, data_sample.selectionString, leptonPtEtaCut)
                if dirDB.contains(key) and not args.overwrite:
                    dataHist_SB_tmp = dirDB.get(key)
                else:
                    dataHist_SB_tmp = data_sample.get1DHistoFromDraw( invVariable, binning=args.binning, selectionString=leptonPtEtaCut, addOverFlowBin="upper" )
                    dirDB.add(key, dataHist_SB_tmp.Clone("dataSB"))

                qcdHist_tmp = dataHist_SB_tmp.Clone("qcdtmp_%i_%i"%(i_pt,i_eta))
    
                for s in mc:
                    s.setWeightString( mc_normalization_weight_string )
                    key = (s.name, "SB", args.variable, "_".join(map(str,args.binning)), s.weightString, s.selectionString, leptonPtEtaCut)
                    if dirDB.contains(key) and not args.overwrite:
                        s.hist_SB_tmp = dirDB.get(key)
                    else:
                        s.hist_SB_tmp = s.get1DHistoFromDraw( invVariable, binning=args.binning, selectionString=leptonPtEtaCut, addOverFlowBin="upper" )
                        dirDB.add(key, s.hist_SB_tmp.Clone(s.name+"SB"))
    
                    # apply SF after histo caching
                    if addSF:
                        if "DY" in s.name:
                            s.hist_SB_tmp.Scale(DYSF_val[args.year].val)
                        elif "WJets" in s.name:
                            s.hist_SB_tmp.Scale(WJetsSF_val[args.year].val)
                        elif "ZG" in s.name:# and njets < 4:
                            s.hist_SB_tmp.Scale(ZGSF_val[args.year].val)
                        elif "WG" in s.name:# and njets > 3:
                            s.hist_SB_tmp.Scale(WGSF_val[args.year].val)
                        elif "TTG" in s.name:
                            s.hist_SB_tmp.Scale(SSMSF_val[args.year].val)

                    qcdHist_tmp.Add(s.hist_SB_tmp, -1)


                # Transfer Factor, get the QCD histograms always in barrel regions
                QCDTF_updates_2J["CR"]["leptonEta"] = ( etaLow, etaHigh )
                QCDTF_updates_2J["CR"]["leptonPt"]  = ( ptLow,  ptHigh   )
                QCDTF_updates_2J["SR"]["leptonEta"] = ( etaLow, etaHigh )
                QCDTF_updates_2J["SR"]["leptonPt"]  = ( ptLow,  ptHigh   )

                # REMOVE THAT FOR NOW
                # define the 2016 e-channel QCD sideband in barrel only (bad mT fit in EC)
                if False and args.mode == "e" and args.year == 2016 and (etaHigh > 1.479 or etaHigh < 0):
                    QCDTF_updates_2J["CR"]["leptonEta"] = ( 0, 1.479 )

                qcdUpdates  = { "CR":QCDTF_updates_2J["CR"], "SR":QCDTF_updates_2J["SR"] }
                transferFac = estimate.cachedTransferFactor( args.mode, setup, qcdUpdates=qcdUpdates, overwrite=False, checkOnly=False )
        
                print "pt", ptLow, ptHigh, "eta", etaLow, etaHigh, "TF:", transferFac

                # remove negative bins
                for i in range(qcdHist_tmp.GetNbinsX()):
                    if qcdHist_tmp.GetBinContent(i+1) < 0: qcdHist_tmp.SetBinContent(i+1, 0)
    
                qcdHist_tmp.Scale(transferFac.val)
                qcdHist.Add(qcdHist_tmp)

        # create the datadriven qcd histogram
        key = ("QCD-DD", "AR", args.variable, "_".join(map(str,args.binning)), selection)
        dirDB.add(key, qcdHist.Clone("QCD"), overwrite=True)


if args.variation:
    var = args.variable
    if args.variation.startswith("eTotal"):
        var = args.variable.replace("PhotonNoChgIsoNoSieie0_","PhotonNoChgIsoNoSieie0_"+args.variation+"_")
    if args.variable in variables_with_selection_systematics and args.variation in selection_systematics:
        var = args.variable + "_" + args.variation
    if args.variable in metvariables_with_selection_systematics and args.variation in metselection_systematics:
        var = args.variable + "_" + args.variation
    # if we"re running a variation specify
    print args.variation
    selectionModifier = variations[args.variation]["selectionModifier"]
    normalization_selection_string = selectionModifier(selection)
    mc_normalization_weight_string = MC_WEIGHT(variations[args.variation], lumi_scale, returntype="string")
    for s in mc:
        print
        print s.selectionString
        print normalization_selection_string
        print
        # Calculate the normalisation yield for mt2ll<100
        s.setWeightString( mc_normalization_weight_string )
        key = (s.name, "AR", var, "_".join(map(str,args.binning)), s.weightString, s.selectionString, normalization_selection_string, args.variation)
        if not dirDB.contains(key) or args.overwrite:
            s.hist = s.get1DHistoFromDraw( var, binning=args.binning, selectionString=normalization_selection_string, addOverFlowBin="upper" )
            dirDB.add(key, s.hist.Clone(s.name+var), overwrite=True)

        print( "Done with %s in channel %s.", args.variation, args.mode)

    print( "Done with mode %s and variation %s of selection %s. Quit now.", args.mode, args.variation, args.selection )
    sys.exit(0)


systematics = [\
    {"name":"MER",              "pair":("muTotalDown", "muTotalUp"),},
    {"name":"EER",              "pair":("eTotalDown", "eTotalUp"),},
    {"name":"JER",              "pair":("jerDown", "jerUp"),},
    {"name":"JEC",              "pair":("jesTotalDown", "jesTotalUp")},
#    {"name":"Unclustered",      "pair":("unclustEnDown", "unclustEnUp") },
    {"name":"PU",               "pair":("PUDown", "PUUp")},
    {"name":"BTag_b",           "pair":("BTag_SF_b_Down", "BTag_SF_b_Up" )},
    {"name":"BTag_l",           "pair":("BTag_SF_l_Down", "BTag_SF_l_Up")},
    {"name":"trigger",          "pair":("TriggerDown", "TriggerUp")},
    {"name":"leptonSF",         "pair":("LeptonSFTightDown", "LeptonSFTightUp")},
    {"name":"leptonTrackingSF", "pair":("LeptonSFTrackingTightDown", "LeptonSFTrackingTightUp")},
    {"name":"photonSF",         "pair":("PhotonSFDown", "PhotonSFUp")},
    {"name":"evetoSF",          "pair":("PhotonElectronVetoSFDown", "PhotonElectronVetoSFUp")},
    {"name":"prefireSF",        "pair":("L1PrefireDown", "L1PrefireUp")},
]


missing_cmds   = []
variation_data = {}
for s in mc:
    s.hist = {}
    for variation in variations.keys():
        selectionModifier = variations[variation]["selectionModifier"]
        normalization_selection_string = selectionModifier(selection)
        mc_normalization_weight_string = MC_WEIGHT(variations[variation], lumi_scale, returntype="string")
        s.setWeightString( mc_normalization_weight_string )
        var = args.variable if args.variable not in variables_with_selection_systematics or variation not in selection_systematics else args.variable + "_" + variation
        if variation.startswith("eTotal"):
            var = args.variable.replace("PhotonNoChgIsoNoSieie0_","PhotonNoChgIsoNoSieie0_"+variation+"_")
        key = (s.name, "AR", var, "_".join(map(str,args.binning)), s.weightString, s.selectionString, normalization_selection_string, variation)

#        print key
        if dirDB.contains(key) and not args.overwrite:
            s.hist[variation]               = dirDB.get(key).Clone(s.name+"_"+variation)
            s.hist[variation].style         = styles.fillStyle( s.color )
            s.hist[variation].legendText    = s.texName

            # apply SF after histo caching
            if addSF:
                if "DY" in s.name:
                    s.hist[variation].Scale(DYSF_val[args.year].val)
#                elif "WJets" in s.name:
#                    s.hist[variation].Scale(WJetsSF_val[args.year].val)
                elif "ZG" in s.name:# and njets < 4:
                    s.hist[variation].Scale(ZGSF_val[args.year].val)
                elif "WG" in s.name:# and njets > 3:
                    s.hist[variation].Scale(WGSF_val[args.year].val)
                elif "TTG" in s.name:
                    s.hist[variation].Scale(SSMSF_val[args.year].val)

        else:
            # prepare sub variation command
            cmd = ["python", "systematicVariationFakes.py"]
            cmd.append("--logLevel %s"%args.logLevel)
            cmd.append("--plot_directory %s"%args.plot_directory)
            cmd.append("--selection %s"%args.selection)
            if args.addCut: cmd.append("--addCut %s"%args.addCut)
            cmd.append("--variable %s"%args.variable)
            cmd.append("--binning %s"%" ".join(map(str,args.binning)))
            cmd.append("--variation %s"%variation)
            cmd.append("--mode %s"%args.mode)
            cmd.append("--year %s"%str(args.year))
            if args.overwrite: cmd.append("--overwrite")

            cmd_string = " ".join( cmd )
            missing_cmds.append( cmd_string )
            print("Missing variation %s, year %s in mode %s in cache. Need to run: \n%s", variation, str(args.year), args.mode, cmd_string)

keyQCD = ("QCD-DD", "AR", args.variable, "_".join(map(str,args.binning)), selection)
key = (data_sample.name, "AR", args.variable, "_".join(map(str,args.binning)), data_sample.weightString, data_sample.selectionString, selection)
if dirDB.contains(keyQCD) and dirDB.contains(key) and not args.overwrite:
    data_sample.hist = dirDB.get(key)
else:
    # prepare sub variation command
    cmd = ["python", "systematicVariationFakes.py"]
    cmd.append("--logLevel %s"%args.logLevel)
    cmd.append("--plot_directory %s"%args.plot_directory)
    cmd.append("--selection %s"%args.selection)
    if args.addCut: cmd.append("--addCut %s"%args.addCut)
    cmd.append("--variable %s"%args.variable)
    cmd.append("--binning %s"%" ".join(map(str,args.binning)))
    cmd.append("--variation central")
    cmd.append("--mode %s"%args.mode)
    cmd.append("--year %s"%str(args.year))
    if args.overwrite: cmd.append("--overwrite")

    cmd_string = " ".join( cmd )
    missing_cmds.append( cmd_string )
    print("Missing variation %s, year %s in mode %s in cache. Need to run: \n%s", "central", str(args.year), args.mode, cmd_string)


# write missing cmds
missing_cmds = list(set(missing_cmds))
if missing_cmds:
    with file( "missing.sh", "w" ) as f:
        for cmd in missing_cmds:
            f.write( cmd + "\n")
    print( "Written %i variation commands to ./missing.sh. Now I quit!", len(missing_cmds) )
    sys.exit(0)


key = ("QCD-DD", "AR", args.variable, "_".join(map(str,args.binning)), selection)
print dirDB.contains(key)
qcdHist = dirDB.get(key)

if addSF:
    qcdHist.Scale(QCDSF_val[args.year].val)

qcdHist.style          = styles.fillStyle( color.QCD )
qcdHist.legendText     = "QCD (data)"

# for central (=no variation), we store plot_data_1, plot_mc_1, plot_data_2, plot_mc_2, ...
data_histo_list = [data_sample.hist]
mc_histo_list   = {variation:[s.hist[variation] for s in mc] + [qcdHist] for variation in variations.keys()}

# copy styles and tex
data_histo_list[0].style = styles.errorStyle( ROOT.kBlack )
data_histo_list[0].legendText = "data (%s)"%args.mode.replace("mu","#mu")

Plot.setDefaults()
plot        = Plot.fromHisto( args.variable, [mc_histo_list["central"]] + [data_histo_list], texX = replaceLabel[args.variable], texY = "Number of Events" )
plot.stack  = Stack( mc + [qcd], [data_sample] ) 

# Make boxes and ratio boxes
boxes           = []
ratio_boxes     = []
# Compute all variied MC sums
total_mc_histo   = {variation:add_histos( mc_histo_list[variation]) for variation in variations.keys() }

# loop over bins & compute shaded uncertainty boxes
for i_b in range(1, 1 + total_mc_histo["central"].GetNbinsX() ):
# Only positive yields
    total_central_mc_yield = total_mc_histo["central"].GetBinContent(i_b)
    if total_central_mc_yield<=0: continue
    variance = 0.
    for systematic in systematics:
        # Use "central-variation" (factor 1) and 0.5*(varUp-varDown)
        if "central" in systematic["pair"]: 
            factor = 1
        else:
            factor = 0.5
        # sum in quadrature
        variance += ( factor*(total_mc_histo[systematic["pair"][0]].GetBinContent(i_b) - total_mc_histo[systematic["pair"][1]].GetBinContent(i_b)) )**2

    sigma     = sqrt(variance)
    sigma_rel = sigma/total_central_mc_yield 

    box = ROOT.TBox( 
            total_mc_histo["central"].GetXaxis().GetBinLowEdge(i_b),
            max([0.03, (1-sigma_rel)*total_central_mc_yield]),
            total_mc_histo["central"].GetXaxis().GetBinUpEdge(i_b), 
            max([0.03, (1+sigma_rel)*total_central_mc_yield]) )
    box.SetLineColor(ROOT.kGray+2)
    box.SetFillStyle(3644)
    box.SetLineWidth(1)
    box.SetFillColor(ROOT.kGray+2)
    boxes.append(box)

    r_box = ROOT.TBox( 
        total_mc_histo["central"].GetXaxis().GetBinLowEdge(i_b),  
        max(0.1, 1-sigma_rel), 
        total_mc_histo["central"].GetXaxis().GetBinUpEdge(i_b), 
        min(1.9, 1+sigma_rel) )
    r_box.SetLineColor(ROOT.kGray+2)
    r_box.SetLineWidth(1)
    r_box.SetFillStyle(3644)
    r_box.SetFillColor(ROOT.kGray+2)
    ratio_boxes.append(r_box)

legend = [ (0.2,0.9-0.025*sum(map(len, plot.histos)),0.9,0.9), 3 ]
ratio = {'yRange':(0.1,1.9), "drawObjects":ratio_boxes}
#ratio = {'yRange':(0.65,1.35), "drawObjects":ratio_boxes}
#ratio = {'yRange':(0.45,1.55), "drawObjects":ratio_boxes}
for log in [True, False]:

        selDir = args.selection
        if args.addCut: selDir += "-" + args.addCut
        plot_directory_ = os.path.join( plot_directory, "systematics", str(args.year), args.plot_directory, selDir, args.mode, "log" if log else "lin" )
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = log, sorting = True,#plot.name != "mT_fit",
                       yRange = (0.3, "auto"),
                       ratio = ratio,
#                       drawObjects = drawObjects( lumi_scale ),
                       drawObjects = drawObjects( lumi_scale ) + boxes,
                       legend = legend,
                       copyIndexPHP = True,
                       )



