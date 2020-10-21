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
import Analysis.Tools.syncer as syncer

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
argParser.add_argument("--variation",          action="store",      default=None,                                                            help="Which systematic variation to run. Don't specify for producing plots.")
argParser.add_argument("--binning",            action="store",      default=[20,-2.4,2.4],  type=float, nargs="*",                           help="binning of plots")
argParser.add_argument("--year",               action="store",      default="2016",   type=str,  choices=["2016","2017","2018","RunII"],     help="Which year to plot?")
argParser.add_argument("--mode",               action="store",      default="all",  type=str,  choices=["mu", "e", "all","SFtight","eetight","mumutight"],         help="lepton selection")
argParser.add_argument("--overwrite",          action="store_true",                                                                          help="overwrite cache?")
argParser.add_argument("--postfit",            action="store_true",                                                                          help="overwrite cache?")
argParser.add_argument("--photonCat",          action="store_true",                                                                          help="all plots in one directory?")
argParser.add_argument("--inclQCDTF",          action="store_true",                                                                          help="run with incl QCD TF?")
argParser.add_argument("--paperPlot",          action="store_true",                                                                          help="change labeling for paper")
args = argParser.parse_args()

addSF = args.postfit
args.binning[0] = int(args.binning[0])
if args.year != "RunII": args.year = int(args.year)

replaceRegionNaming = {
    "WJets2": "0#gamma0b2j",
    "WJets3": "0#gamma0b3j",
    "WJets3p": "0#gamma0b3pj",
    "WJets4p": "0#gamma0b4pj",
    "TT2": "0#gamma1b2j",
    "TT3": "0#gamma1b3j",
    "TT3p": "0#gamma1b3pj",
    "TT4p": "0#gamma1b4pj",
}

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile=None )
logger_rt = logger_rt.get_logger( args.logLevel, logFile=None )

def jetSelectionModifier( sys, returntype = "func"):
    # Need to make sure all jet variations of the following observables are in the ntuple
    variiedJetObservables = ["nJetGood", "nBTagGood", "&m3", "&ht"]
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
    variiedMuonObservables = ['triggered','nMuonTight','nLeptonVetoIsoCorr','nLeptonTight','mllgammatight','mLtight0GammaNoSieieNoChgIso','mLtight0Gamma','mlltight']
    if returntype == "func":
        def changeCut_( string ):
            for s in variiedMuonObservables:
                string = string.replace(s, s+"_"+sys)
            return string
        return changeCut_
    elif returntype == "list":
        return [ v+"_"+sys for v in variiedMuonObservables ] # change that after next pp

def eleSelectionModifier( sys, returntype = "func"):
    # Need to make sure all Ele variations of the following observables are in the ntuple
    variiedEleObservables = ['triggered','nPhotonGood', 'nPhotonNoChgIsoNoSieie', 'nElectronVetoIsoCorr', 'nElectronTight','nLeptonVetoIsoCorr','nLeptonTight','mllgammatight','mLtight0GammaNoSieieNoChgIso','mLtight0Gamma','mlltight']
#    variiedEleObservables = ['nPhotonGood', 'nPhotonNoChgIsoNoSieie']
    if returntype == "func":
        def changeCut_( string ):
            for s in variiedEleObservables:
                string = string.replace(s, s+"_"+sys)
            return string
        return changeCut_
    elif returntype == "list":
        return [ v+"_"+sys for v in variiedEleObservables ] # change that after next pp

def metSelectionModifier( sys, returntype = 'func'):
    #Need to make sure all MET variations of the following observables are in the ntuple
#    variiedMetObservables = ["nJetGood", "nBTagGood", "mT", "MET_pt"]
    variiedMetObservables = ["mT", "MET_pt"]
    if returntype == "func":
        def changeCut_( string ):
            for s in variiedMetObservables:
                string = string.replace(s, s+'_'+sys)
            return string
        return changeCut_
    elif returntype == "list":
        return [ v+'_'+sys for v in variiedMetObservables ]

# these are the nominal MC weights we always apply
nominalMCWeights = ["weight", "reweightHEM","reweightTrigger", "reweightL1Prefire", "reweightPU", "reweightLeptonTightSF", "reweightLeptonTrackingTightSF", "reweightPhotonSF", "reweightPhotonElectronVetoSF", "reweightBTag_SF"]
genCat = ["noChgIsoNoSieiephotoncat2","noChgIsoNoSieiephotoncat0","noChgIsoNoSieiephotoncat134"] if args.photonCat else [None]

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
    lumiString = "(35.92*(year==2016)+41.53*(year==2017)+59.74*(year==2018))"
    weightString = "*".join(variiedMCWeights)
    weightString += "*%s"%lumiString
    if returntype == "string":
        ws   = weightString
        if not (addSF and setup.isPhotonSelection): return ws
        ws16 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2016))" %(ws, misIDSF_val[2016].val)
        ws17 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2017))" %(ws, misIDSF_val[2017].val)
        ws18 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2018))" %(ws, misIDSF_val[2018].val)
        return ws + ws16 + ws17 + ws18
    if returntype == "invIso":
        wsInv   = weightString.replace("reweightTrigger", "reweightInvIsoTrigger")
        if not setup.isPhotonSelection: return wsInv #always add misIDSF in qcd sideband regions
        wsInv16 = "+(%s*(PhotonNoChgIsoNoSieieInvLepIso0_photonCatMagic==2)*(%f-1)*(year==2016))" %(wsInv, misIDSF_val[2016].val)
        wsInv17 = "+(%s*(PhotonNoChgIsoNoSieieInvLepIso0_photonCatMagic==2)*(%f-1)*(year==2017))" %(wsInv, misIDSF_val[2017].val)
        wsInv18 = "+(%s*(PhotonNoChgIsoNoSieieInvLepIso0_photonCatMagic==2)*(%f-1)*(year==2018))" %(wsInv, misIDSF_val[2018].val)
        return wsInv + wsInv16 + wsInv17 + wsInv18
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
      (0.235 if args.selection.startswith("WJets") or args.selection.startswith("TT") else 0.15, 0.95, "CMS #bf{#it{Preliminary}}%s"%(" (%s)"%(replaceRegionNaming[args.selection.replace("fake","SR")] if args.selection.replace("fake","SR") in replaceRegionNaming.keys() else args.selection.replace("fake","SR")) if not args.paperPlot else "" )),
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
    "eScaleUp"                  : {"selectionModifier":eleSelectionModifier("eScaleUp"),                                  "read_variables" : [ "%s/F"%v for v in nominalMCWeights + eleSelectionModifier("eScaleUp","list")]},
    "eScaleDown"                : {"selectionModifier":eleSelectionModifier("eScaleDown"),                                "read_variables" : [ "%s/F"%v for v in nominalMCWeights + eleSelectionModifier("eScaleDown","list")]},
    "eResUp"                  : {"selectionModifier":eleSelectionModifier("eResUp"),                                  "read_variables" : [ "%s/F"%v for v in nominalMCWeights + eleSelectionModifier("eResUp","list")]},
    "eResDown"                : {"selectionModifier":eleSelectionModifier("eResDown"),                                "read_variables" : [ "%s/F"%v for v in nominalMCWeights + eleSelectionModifier("eResDown","list")]},
#    "muTotalUp"                 : {"selectionModifier":muonSelectionModifier("muTotalUp"),                                "read_variables" : [ "%s/F"%v for v in nominalMCWeights + muonSelectionModifier("muTotalUp","list")]},
#    "muTotalDown"               : {"selectionModifier":muonSelectionModifier("muTotalDown"),                              "read_variables" : [ "%s/F"%v for v in nominalMCWeights + muonSelectionModifier("muTotalDown","list")]},
    "jerUp"                     : {"selectionModifier":jetSelectionModifier("jerUp"),                                     "read_variables" : [ "%s/F"%v for v in nominalMCWeights + jetSelectionModifier("jerUp","list")]},
    "jerDown"                   : {"selectionModifier":jetSelectionModifier("jerDown"),                                   "read_variables" : [ "%s/F"%v for v in nominalMCWeights + jetSelectionModifier("jerDown","list")]},
    "jesTotalUp"                : {"selectionModifier":jetSelectionModifier("jesTotalUp"),                                "read_variables" : [ "%s/F"%v for v in nominalMCWeights + jetSelectionModifier("jesTotalUp","list")]},
    "jesTotalDown"              : {"selectionModifier":jetSelectionModifier("jesTotalDown"),                              "read_variables" : [ "%s/F"%v for v in nominalMCWeights + jetSelectionModifier("jesTotalDown","list")]},
    "unclustEnUp"               : {"selectionModifier":metSelectionModifier("unclustEnUp"),                               "read_variables" : [ "%s/F"%v for v in nominalMCWeights]},
    "unclustEnDown"             : {"selectionModifier":metSelectionModifier("unclustEnDown"),                             "read_variables" : [ "%s/F"%v for v in nominalMCWeights]},
    "BTag_SF_b_Down"            : {"replaceWeight":("reweightBTag_SF","reweightBTag_SF_b_Down"),                          "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightBTag_SF_b_Down"]]},  
    "BTag_SF_b_Up"              : {"replaceWeight":("reweightBTag_SF","reweightBTag_SF_b_Up"),                            "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightBTag_SF_b_Up"] ]},
    "BTag_SF_l_Down"            : {"replaceWeight":("reweightBTag_SF","reweightBTag_SF_l_Down"),                          "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightBTag_SF_l_Down"]]},
    "BTag_SF_l_Up"              : {"replaceWeight":("reweightBTag_SF","reweightBTag_SF_l_Up"),                            "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightBTag_SF_l_Up"] ]},
}

jesTags = ['Total']
jesVariations = ["jes"+j+"Up" for j in jesTags] + ["jes"+j+"Down" for j in jesTags]
selection_systematics = [ "jerUp", "jerDown" ] + jesVariations

variables_with_selection_systematics = [ "nJetGood", "nBTagGood", "ht", "m3" ]
metselection_systematics = [ "unclustEnUp", "unclustEnDown" ]
metvariables_with_selection_systematics = [ "MET_pt", "mT" ]
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
    import TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed as mc_samples
    from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import Run2016 as data_sample
elif args.year == 2017:
    import TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed as mc_samples
    from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import Run2017 as data_sample
elif args.year == 2018:
    import TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed as mc_samples
    from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import Run2018 as data_sample
elif args.year == "RunII":
    import TTGammaEFT.Samples.nanoTuples_RunII_postProcessed as mc_samples
    from TTGammaEFT.Samples.nanoTuples_RunII_postProcessed import RunII as data_sample

mc  = [ mc_samples.TTG, mc_samples.Top, mc_samples.DY_LO, mc_samples.WJets, mc_samples.WG, mc_samples.ZG, mc_samples.rest ]
qcd = mc_samples.QCD

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

data_sample.setSelectionString( filterCutData )
data_sample.setWeightString( "weight" )

for s in mc:
    s.setSelectionString( [ filterCutMc, "pTStitching==1", "overlapRemoval==1" ] )
    s.read_variables = read_variables_MC

replaceSelection = {
    "nLeptonVetoIsoCorr": "nLeptonVetoNoIso",
    "nLeptonTight":       "nLeptonTightInvIso",
    "nMuonTight":         "nMuonTightInvIso",
    "nElectronTight":     "nElectronTightInvIso",
    "mLtight0Gamma":      "mLinvtight0Gamma",
    "nPhotonNoChgIsoNoSieie": "nPhotonNoChgIsoNoSieieInvLepIso",
    "nPhotonGood":        "nPhotonGoodInvLepIso",
    "nJetGood":           "nJetGoodInvLepIso",
    "nBTagGood":          "nBTagGoodInvLepIso",
#    "mT":                 "mTinv",
#    "m3":                 "m3inv",
#    "ht":                 "htinv",
    "LeptonTight0_eta":   "LeptonTightInvIso0_eta",
    "LeptonTight0_pt":    "LeptonTightInvIso0_pt",
    "PhotonGood0_pt":    "PhotonGoodInvLepIso0_pt",
    "PhotonGood0_phi":   "PhotonGoodInvLepIso0_phi",
    "PhotonGood0_eta":   "PhotonGoodInvLepIso0_eta",
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
    selection += "&&triggered==1&&reweightHEM>0"
    print( "Using selection string: %s"%args.selection )

    # no qcd in dilepton selections
    if "tight" in args.mode:
        preSelection = selection
    else:
        preSelection  = setup.selection("MC",   channel="all", **setup.defaultParameters(update=QCD_updates))["prefix"]
        preSelection += "-" + args.mode + "Inv"
        preSelection  = cutInterpreter.cutString( preSelection )
        if args.addCut:
            addSel = cutInterpreter.cutString( args.addCut )
            for iso, invIso in replaceSelection.iteritems():
                addSel = addSel.replace(iso,invIso)
            preSelection += "&&" + addSel
        preSelection += "&&triggeredInvIso==1&&reweightHEM>0"

else:
    raise Exception("Region not implemented")

lep = args.mode.replace("mu","#mu") if args.mode != "all" else "l"
replaceLabel = {
    "nElectronTight": "yield",
    "PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt": "chg.Iso(#gamma) [GeV]",
    "PhotonNoChgIsoNoSieie0_sieie": "#sigma_{i#eta i#eta}(#gamma)",
    "MET_pt": "E^{miss}_{T} [GeV]",
    "mT": "M_{T} [GeV]",
    "mLtight0Gamma": "M(#gamma,%s) [GeV]"%lep,
    "LeptonTight0_eta": "#eta(%s)"%lep,
    "LeptonTight0_phi": "#phi(%s)"%lep,
    "LeptonTight0_pt": "p_{T}(%s) [GeV]"%lep,
    "mlltight": "M(l,l) [GeV]",
    "m3": "M_{3} [GeV]",
    "ht": "H_{T} [GeV]",
    "lpTight": "L_{p}",
    "JetGood0_eta": "#eta(j_{0})",
    "JetGood0_phi": "#phi(j_{0})",
    "JetGood0_pt": "p_{T}(j_{0}) [GeV]",
    "JetGood1_eta": "#eta(j_{1})",
    "JetGood1_phi": "#phi(j_{1})",
    "JetGood1_pt": "p_{T}(j_{1}) [GeV]",
    "PhotonNoChgIsoNoSieie0_pt": "p_{T}(#gamma) [GeV]",
    "PhotonNoChgIsoNoSieie0_eta": "#eta(#gamma)",
    "PhotonNoChgIsoNoSieie0_phi": "#phi(#gamma)",
    "PhotonGood0_pt": "p_{T}(#gamma) [GeV]",
    "PhotonGood0_eta": "#eta(#gamma)",
    "PhotonGood0_phi": "#phi(#gamma)",
    "ltight0GammadPhi": "#Delta#phi(%s,#gamma)"%lep,
    "ltight0GammadR": "#DeltaR(%s,#gamma)"%lep,
    "photonJetdR": "min #DeltaR(j,#gamma)",
}

replaceVariable = {
    "nElectronTight":     "nElectronTightInvIso",
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
    "JetGood0_pt":    "JetGoodInvLepIso0_pt",
    "JetGood0_phi":   "JetGoodInvLepIso0_phi",
    "JetGood0_eta":   "JetGoodInvLepIso0_eta",
    "JetGood1_pt":    "JetGoodInvLepIso1_pt",
    "JetGood1_phi":   "JetGoodInvLepIso1_phi",
    "JetGood1_eta":   "JetGoodInvLepIso1_eta",
    "PhotonGood0_pt":    "PhotonGoodInvLepIso0_pt",
    "PhotonGood0_phi":   "PhotonGoodInvLepIso0_phi",
    "PhotonGood0_eta":   "PhotonGoodInvLepIso0_eta",
    "PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt": "PhotonNoChgIsoNoSieieInvLepIso0_pfRelIso03_chg*PhotonNoChgIsoNoSieieInvLepIso0_pt",
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
        dataHist = data_sample.get1DHistoFromDraw( args.variable, binning=args.binning, selectionString=selection, addOverFlowBin=None ) #"upper" )
        dirDB.add(key, dataHist.Clone("dataAR"), overwrite=True)
    else:
        dataHist = dirDB.get(key).Clone("dataAR")

    for s in mc:
      for g in genCat:
        selectionModifier = variations[args.variation]["selectionModifier"]
        normalization_selection_string = selectionModifier(selection)
        if args.photonCat: normalization_selection_string += "&&" + cutInterpreter.cutString( g )  
        mc_normalization_weight_string = MC_WEIGHT(variations[args.variation], lumi_scale, returntype="string")
        s.setWeightString( mc_normalization_weight_string )
        key = (s.name, "AR", args.variable, "_".join(map(str,args.binning)), s.weightString, s.selectionString, normalization_selection_string, args.variation)
        if not dirDB.contains(key) or args.overwrite:
            mcHist = s.get1DHistoFromDraw( args.variable, binning=args.binning, selectionString=normalization_selection_string, addOverFlowBin=None ) #"upper" )
            dirDB.add(key, mcHist.Clone(s.name+"AR"+g if g else s.name+"AR"), overwrite=True)

    key = ("QCD-DD", "ARincl" if args.inclQCDTF else "AR", args.variable, "_".join(map(str,args.binning)), selection)
    if not dirDB.contains(key) or args.overwrite:
        qcdHist = dataHist.Clone("qcd")
        qcdHist.Scale(0)

        # get cached transferfactors
        estimators = EstimatorList( setup, processes=["QCD-DD"] )
        estimate   = getattr(estimators, "QCD-DD")
        estimate.initCache(setup.defaultCacheDir())
        mc_normalization_weight_string = MC_WEIGHT(variations[args.variation], lumi_scale, returntype="invIso")
        allModes = ["eInv","muInv"] if args.mode == "all" else [args.mode + "Inv"]
        if "tight" in args.mode: allModes = []
        for mode in allModes:
            preSel = preSelection + "&&" + cutInterpreter.cutString( mode )
            for i_pt, pt in enumerate(ptBins[:-1]):
                for i_eta, eta in enumerate(etaBins[:-1]):
                    etaLow, etaHigh = eta, etaBins[i_eta+1]
                    ptLow, ptHigh   = pt,  ptBins[i_pt+1]

                    # Remove that for now
                    # define the 2016 e-channel QCD sideband in barrel only (bad mT fit in EC)
                    if False and mode == "eInv" and args.year == 2016 and (etaHigh > 1.479 or etaHigh < 0):
                        leptonPtEtaCut  = [ leptonEtaCutVar + ">=0", leptonPtCutVar + ">=" + str(ptLow) ]
                        leptonPtEtaCut += [ leptonEtaCutVar + "<1.479" ]
                        if ptHigh > 0:  leptonPtEtaCut += [ leptonPtCutVar + "<" + str(ptHigh) ]
                    else:
                        leptonPtEtaCut = [ leptonEtaCutVar + ">=" + str(etaLow), leptonPtCutVar + ">=" + str(ptLow) ]
                        if etaHigh > 0: leptonPtEtaCut += [ leptonEtaCutVar + "<" + str(etaHigh) ]
                        if ptHigh > 0:  leptonPtEtaCut += [ leptonPtCutVar + "<" + str(ptHigh) ]

                    leptonPtEtaCut = "&&".join( [preSel] + leptonPtEtaCut )
    
                    print "Running histograms for qcd selection:"

                    # histos
                    key = (data_sample.name, "SB", args.variable, "_".join(map(str,args.binning)), data_sample.weightString, data_sample.selectionString, leptonPtEtaCut)
                    if dirDB.contains(key) and not args.overwrite:
                        dataHist_SB_tmp = dirDB.get(key).Clone("dataSB"+mode)
                    else:
                        dataHist_SB_tmp = data_sample.get1DHistoFromDraw( invVariable, binning=args.binning, selectionString=leptonPtEtaCut, addOverFlowBin=None ) #"upper" )
                        dirDB.add(key, dataHist_SB_tmp.Clone("dataSB"+mode))

                    qcdHist_tmp = dataHist_SB_tmp.Clone("qcdtmp_%i_%i"%(i_pt,i_eta))
    
                    for s in mc:
                        s.setWeightString( mc_normalization_weight_string )
                        key = (s.name, "SB", args.variable, "_".join(map(str,args.binning)), s.weightString, s.selectionString, leptonPtEtaCut)
                        if dirDB.contains(key) and not args.overwrite:
                            s.hist_SB_tmp = dirDB.get(key).Clone(s.name+"SB")
                        else:
                            s.hist_SB_tmp = s.get1DHistoFromDraw( invVariable, binning=args.binning, selectionString=leptonPtEtaCut, addOverFlowBin=None ) #"upper" )
                            dirDB.add(key, s.hist_SB_tmp.Clone(s.name+"SB"))
    
                        # apply SF after histo caching
                        if addSF:
                            if setup.isPhotonSelection:
                                if "DY" in s.name:
                                    s.hist_SB_tmp.Scale(DYSF_val[args.year].val)
                                elif "ZG" in s.name:# and njets < 4:
                                    s.hist_SB_tmp.Scale(ZGSF_val[args.year].val)
                                elif "WG" in s.name:# and njets > 3:
                                    s.hist_SB_tmp.Scale(WGSF_val[args.year].val)
                                elif "TTG" in s.name:
                                    s.hist_SB_tmp.Scale(SSMSF_val[args.year].val)
                            else:
                                if "DY" in s.name:
                                    s.hist_SB_tmp.Scale(DYSF_val[args.year].val)
                                elif "WJets" in s.name:
                                    s.hist_SB_tmp.Scale(WJetsSF_val[args.year].val)

                        qcdHist_tmp.Add(s.hist_SB_tmp, -1)


                    # Transfer Factor, get the QCD histograms always in barrel regions
                    if args.inclQCDTF:
                        # run it this way since you may have already stored the sideband histograms
                        QCDTF_updates_2J["CR"]["leptonEta"] = ( 0, -1 )
                        QCDTF_updates_2J["CR"]["leptonPt"]  = ( 0, -1 )
                        QCDTF_updates_2J["SR"]["leptonEta"] = ( 0, -1 )
                        QCDTF_updates_2J["SR"]["leptonPt"]  = ( 0, -1 )
                    else:
                        QCDTF_updates_2J["CR"]["leptonEta"] = ( etaLow, etaHigh )
                        QCDTF_updates_2J["CR"]["leptonPt"]  = ( ptLow,  ptHigh   )
                        QCDTF_updates_2J["SR"]["leptonEta"] = ( etaLow, etaHigh )
                        QCDTF_updates_2J["SR"]["leptonPt"]  = ( ptLow,  ptHigh   )

                    # REMOVE THAT FOR NOW
                    # define the 2016 e-channel QCD sideband in barrel only (bad mT fit in EC)
                    if False and mode == "eInv" and args.year == 2016 and (etaHigh > 1.479 or etaHigh < 0) and not args.inclQCDTF:
                        QCDTF_updates_2J["CR"]["leptonEta"] = ( 0, 1.479 )

                    qcdUpdates  = { "CR":QCDTF_updates_2J["CR"], "SR":QCDTF_updates_2J["SR"] }
                    transferFac = estimate.cachedTransferFactor( mode.replace("Inv",""), setup, qcdUpdates=qcdUpdates, overwrite=False, checkOnly=False )
        
                    # remove negative bins
                    for i in range(qcdHist_tmp.GetNbinsX()):
                        if qcdHist_tmp.GetBinContent(i+1) < 0: qcdHist_tmp.SetBinContent(i+1, 0)
    
                    print "TF", transferFac.val
                    qcdHist_tmp.Scale(transferFac.val)

                    nJetUpdates = copy.deepcopy(qcdUpdates)
                    nJetUpdates["CR"]["leptonPt"] = ( 0, -1 )
                    nJetUpdates["SR"]["leptonPt"] = ( 0, -1 )

                    if setup.isBTagged:
#                        qcdHist_tmp.Scale(estimate._nJetScaleFactor("mu", setup, qcdUpdates=nJetUpdates))
                        qcdHist_tmp.Scale(estimate._nJetScaleFactor(mode.replace("Inv",""), setup, qcdUpdates=nJetUpdates))
                        print "njet", estimate._nJetScaleFactor(mode.replace("Inv",""), setup, qcdUpdates=nJetUpdates)

                    qcdHist.Add(qcdHist_tmp)

        # create the datadriven qcd histogram
        key = ("QCD-DD", "ARincl" if args.inclQCDTF else "AR", args.variable, "_".join(map(str,args.binning)), selection)
        dirDB.add(key, qcdHist.Clone("QCD"), overwrite=True)


if args.variation:
    var = args.variable
    if args.variable in variables_with_selection_systematics and args.variation in selection_systematics:
        var = args.variable + "_" + args.variation
    if args.variable in metvariables_with_selection_systematics and args.variation in metselection_systematics:
        var = args.variable + "_" + args.variation
    # if we"re running a variation specify
    print args.variation, var
    selectionModifier = variations[args.variation]["selectionModifier"]
    normalization_selection_string = selectionModifier(selection)
    mc_normalization_weight_string = MC_WEIGHT(variations[args.variation], lumi_scale, returntype="string")
    print normalization_selection_string
    for s in mc:
        # Calculate the normalisation yield for mt2ll<100
        s.setWeightString( mc_normalization_weight_string )
        key = (s.name, "AR", var, "_".join(map(str,args.binning)), s.weightString, s.selectionString, normalization_selection_string, args.variation)
        if not dirDB.contains(key) or args.overwrite:
            s.hist = s.get1DHistoFromDraw( var, binning=args.binning, selectionString=normalization_selection_string, addOverFlowBin=None ) #"upper" )
            dirDB.add(key, s.hist.Clone(s.name+var), overwrite=True)

        print( "Done with %s in channel %s.", args.variation, args.mode)

    print( "Done with mode %s and variation %s of selection %s. Quit now.", args.mode, args.variation, args.selection )
    sys.exit(0)


systematics = [\
#    {"name":"MER",              "pair":("muTotalDown", "muTotalUp"),},
    {"name":"EES",              "pair":("eScaleDown", "eScaleUp"),},
    {"name":"EER",              "pair":("eResDown", "eResUp"),},
    {"name":"JER",              "pair":("jerDown", "jerUp"),},
    {"name":"JEC",              "pair":("jesTotalDown", "jesTotalUp")},
    {"name":"Unclustered",      "pair":("unclustEnDown", "unclustEnUp") },
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
        gammaCat = genCat if variation == "central" and args.photonCat else ["all"]
        for g in gammaCat:
            if not variation in s.hist.keys(): s.hist[variation] = {}
            selectionModifier = variations[variation]["selectionModifier"]
            normalization_selection_string = selectionModifier(selection)
            if args.photonCat and variation == "central": normalization_selection_string += "&&" + cutInterpreter.cutString( g )  
            mc_normalization_weight_string = MC_WEIGHT(variations[variation], lumi_scale, returntype="string")
            s.setWeightString( mc_normalization_weight_string )
            var = args.variable
            if args.variable in variables_with_selection_systematics and variation in selection_systematics:
                var = args.variable + "_" + variation
            if args.variable in metvariables_with_selection_systematics and variation in metselection_systematics:
                var = args.variable + "_" + variation
            key = (s.name, "AR", var, "_".join(map(str,args.binning)), s.weightString, s.selectionString, normalization_selection_string, variation)

            if dirDB.contains(key) and not args.overwrite:
                s.hist[variation][g]               = dirDB.get(key).Clone(s.name+"_"+variation+g)
                if variation == "central": print s.name, g, s.hist[variation][g].Integral()
                s.hist[variation][g].style         = styles.fillStyle( s.color )
                s.hist[variation][g].legendText    = s.texName

                # apply SF after histo caching
                if addSF:
                    if setup.isPhotonSelection:
                        if "DY" in s.name:
                            s.hist[variation][g].Scale(DYSF_val[args.year].val)
                        elif "ZG" in s.name:# and njets < 4:
                            s.hist[variation][g].Scale(ZGSF_val[args.year].val)
                        elif "WG" in s.name:# and njets > 3:
                            s.hist[variation][g].Scale(WGSF_val[args.year].val)
                        elif "TTG" in s.name:
                            s.hist[variation][g].Scale(SSMSF_val[args.year].val)
                    else:
                        if "DY" in s.name:
                            s.hist[variation][g].Scale(DYSF_val[args.year].val)
                        elif "WJets" in s.name:
                            s.hist[variation][g].Scale(WJetsSF_val[args.year].val)

            else:
                # prepare sub variation command
                cmd = ["python", "systematicVariation.py"]
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
                if args.photonCat: cmd.append("--photonCat")
                if args.postfit: cmd.append("--postfit")
                if args.inclQCDTF: cmd.append("--inclQCDTF")

                cmd_string = " ".join( cmd )
                missing_cmds.append( cmd_string )
                print("Missing variation %s, year %s in mode %s in cache. Need to run: \n%s", variation, str(args.year), args.mode, cmd_string)

keyQCD = ("QCD-DD", "ARincl" if args.inclQCDTF else "AR", args.variable, "_".join(map(str,args.binning)), selection)
key = (data_sample.name, "AR", args.variable, "_".join(map(str,args.binning)), data_sample.weightString, data_sample.selectionString, selection)
if dirDB.contains(keyQCD) and dirDB.contains(key) and not args.overwrite:
    data_sample.hist = dirDB.get(key)
else:
    # prepare sub variation command
    cmd = ["python", "systematicVariation.py"]
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
    if args.photonCat: cmd.append("--photonCat")
    if args.postfit: cmd.append("--postfit")
    if args.inclQCDTF: cmd.append("--inclQCDTF")

    cmd_string = " ".join( cmd )
#    missing_cmds.append( cmd_string )
#    print("Missing variation %s, year %s in mode %s in cache. Need to run: \n%s", "central", str(args.year), args.mode, cmd_string)


# write missing cmds
if os.path.exists("missing.sh"): os.remove("missing.sh")
missing_cmds = list(set(missing_cmds))
if missing_cmds:
    with file( "missing.sh", "w" ) as f:
        for cmd in missing_cmds:
            if not "central" in cmd:
                f.write( cmd + "\n")
    print( "Written %i variation commands to ./missing.sh. Now I quit!", len(missing_cmds) )
    sys.exit(0)

#sys.exit(0)


key = ("QCD-DD", "ARincl" if args.inclQCDTF else "AR", args.variable, "_".join(map(str,args.binning)), selection)
print dirDB.contains(key)
qcdHist = dirDB.get(key)

print qcdHist.Integral()

if addSF and setup.isPhotonSelection:
    qcdHist.Scale(QCDSF_val[args.year].val)

qcdHist.style          = styles.fillStyle( color.QCD )
qcdHist.legendText     = "Multijet"

data_histo_list = [data_sample.hist]
for s in mc: print s.hist["central"]
mc_histo_list   = {variation:[s.hist[variation]["all" if variation != "central" or not args.photonCat else genCat[0]] for s in mc] + [qcdHist] for variation in variations.keys()}

# for central (=no variation), we store plot_data_1, plot_mc_1, plot_data_2, plot_mc_2, ...
if args.photonCat:
    catHists = [mc[0].hist["central"][g] for g in genCat]
    catSettings = { "noChgIsoNoSieiephotoncat0":{"texName":"Genuine #gamma",  "color":color.gen  },
                    "noChgIsoNoSieiephotoncat2":{"texName":"Misid. e",     "color":color.misID},
                    "noChgIsoNoSieiephotoncat134":{"texName":"Hadronic #gamma/fake",  "color":color.fakes  }}
#                    "noChgIsoNoSieiephotoncat1":{"texName":"had #gamma",  "color":color.had  },
#                    "noChgIsoNoSieiephotoncat3":{"texName":"fake #gamma", "color":color.fakes},
#                    "noChgIsoNoSieiephotoncat4":{"texName":"PU #gamma",   "color":color.PU}  }
    for i, g in enumerate(genCat):
        catHists[i].style = styles.fillStyle( catSettings[g]["color"] )
        catHists[i].legendText = catSettings[g]["texName"]
        for s in mc[1:]:
            catHists[i].Add(s.hist["central"][g])
    mc_histo_list["central"] = catHists + [qcdHist]

# copy styles and tex
data_histo_list[0].style = styles.errorStyle( ROOT.kBlack )
data_histo_list[0].legendText = "Observed (%s)"%args.mode.replace("mu","#mu").replace("all","e+#mu")

if args.variable == "nElectronTight":
    data_histo_list[0].GetXaxis().SetBinLabel( 1, "#mu" )
    data_histo_list[0].GetXaxis().SetBinLabel( 2, "e" )
    for h in mc_histo_list["central"]:
        h.GetXaxis().SetBinLabel( 1, "#mu" )
        h.GetXaxis().SetBinLabel( 2, "e" )


uncHist = data_histo_list[0].Clone()
uncHist.Scale(0)
uncHist.style = styles.hashStyle()
uncHist.legendText = "Uncertainty"

Plot.setDefaults()
plot        = Plot.fromHisto( args.variable, [mc_histo_list["central"]] + [data_histo_list] + [[uncHist]], texX = replaceLabel[args.variable], texY = "Number of Events" )
plot.stack  = Stack( mc + [qcd], [data_sample], [data_sample] ) 

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

histModifications  = []
histModifications += [lambda h: h.GetYaxis().SetTitleOffset(2.0)]

ratioHistModifications  = []
ratioHistModifications += [lambda h: h.GetYaxis().SetTitleOffset(2.0)]

legend = [ (0.2,0.9-0.025*sum(map(len, plot.histos)),0.9,0.9), 3 ]
#ratio = {'yRange':(0.1,1.9), "drawObjects":ratio_boxes}
#ratio = {'yRange':(0.51,1.49), "drawObjects":ratio_boxes}
#ratio = {'yRange':(0.99,1.01), "drawObjects":ratio_boxes}
ratio = {'yRange':(0.76,1.24), "drawObjects":ratio_boxes, "texY":"Obs./Pred.", "histModifications":ratioHistModifications}
for log in [True, False]:

        selDir = args.selection
        if args.addCut: selDir += "-" + args.addCut
        modeAddon = ""
        if args.photonCat: modeAddon += "_cat"
        if args.inclQCDTF: modeAddon += "_inclQCD"
        plot_directory_ = os.path.join( plot_directory, "systematics", str(args.year), args.plot_directory, selDir, "postfit" if args.postfit else "prefit", args.mode+modeAddon, "log" if log else "lin" )
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = log, sorting = not (plot.name == "mLtight0Gamma" and args.paperPlot and args.photonCat) ,
                       yRange = (0.3, "auto"),
                       ratio = ratio,
#                       drawObjects = drawObjects( lumi_scale ),
                       drawObjects = drawObjects( lumi_scale ) + boxes,
                       legend = legend,
                       histModifications = histModifications,
                       copyIndexPHP = True,
                       )



