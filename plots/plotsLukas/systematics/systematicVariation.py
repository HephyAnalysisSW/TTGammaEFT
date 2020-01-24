#!/usr/bin/env python
""" analysis script for standard plots with systematic errors
"""

# Standard imports and batch mode
import ROOT
ROOT.gROOT.SetBatch(True)
import operator
import pickle, os, time, sys
from math                             import sqrt, cos, sin, pi, atan2

# RootTools
from RootTools.core.standard          import *

#Analysis / StopsDilepton / Samples
from TTGammaEFT.Tools.user            import plot_directory, cache_directory
from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter
from TTGammaEFT.Tools.TriggerSelector import TriggerSelector
from Analysis.Tools.helpers           import deltaPhi, add_histos
from Analysis.Tools.metFilters        import getFilterCut
from Analysis.Tools.puReweighting     import getReweightingFunction
from Analysis.Tools.MergingDirDB      import MergingDirDB

from TTGammaEFT.Analysis.SetupHelpers import default_misIDSF, default_DYSF
from TTGammaEFT.Samples.color         import color
#default_misIDSF = 2.38

loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",          action="store",      default="INFO",      choices=loggerChoices,                       help="Log level for logging")
argParser.add_argument("--plot_directory",    action="store",      default="102X_TTG_ppv18_v9")
argParser.add_argument("--selection",         action="store",      default="nLepTight1-nLepVeto1-nJet4p-nBTag1p-nPhoton1p")
argParser.add_argument("--variation",         action="store",      default=None,                                                     help="Which systematic variation to run. Don't specify for producing plots.")
argParser.add_argument("--small",             action="store_true",                                                                   help="Run only on a small subset of the data?")
argParser.add_argument("--overwrite",         action="store_true",                                                                   help="Overwrite?")
argParser.add_argument("--year",              action="store",      default=None,   type=int, choices=[2016,2017,2018],               help="Which year to plot?")
argParser.add_argument("--mode",              action="store",      default="all", type=str, choices=["mu", "e", "all", "eetight", "mumutight", "SFtight", "muetight"], help="plot lepton mode" )

args = argParser.parse_args()

# Logger
import Analysis.Tools.logger as logger
logger = logger.get_logger( args.logLevel, logFile = None )

logger.info( "Working in year %i", args.year )

addMisIDSF = False
addDYSF    = False
selDir     = args.selection
if args.selection.count("addMisIDSF"):
    addMisIDSF = True
    args.selection = "-".join( [ item for item in args.selection.split("-") if item != "addMisIDSF" ] )
if args.selection.count("addDYSF"):
    addDYSF = True
    args.selection = "-".join( [ item for item in args.selection.split("-") if item != "addDYSF" ] )

def jetSelectionModifier( sys, returntype = "func"):
    # Need to make sure all jet variations of the following observables are in the ntuple
    variiedJetObservables = ["nJetGood", "nBTagGood"] # change that after next pp
    if returntype == "func":
        def changeCut_( string ):
            for s in variiedJetObservables:
                string = string.replace(s, s+"_"+sys)
            return string
        return changeCut_
    elif returntype == "list":
        return [ v+"_"+sys for v in variiedJetObservables ] # change that after next pp

def metSelectionModifier( sys, returntype = 'func'):
    #Need to make sure all MET variations of the following observables are in the ntuple
    variiedMetObservables = ['dl_mt2ll', 'dl_mt2blbl', 'MET_significance', 'met_pt', 'metSig']
    if returntype == "func":
        def changeCut_( string ):
            for s in variiedMetObservables:
                string = string.replace(s, s+'_'+sys)
            return string
        return changeCut_
    elif returntype == "list":
        return [ v+'_'+sys for v in variiedMetObservables ]

# these are the nominal MC weights we always apply
nominalMCWeights = ["weight", "reweightL1Prefire", "reweightPU", "reweightLeptonTightSF", "reweightLeptonTrackingTightSF", "reweightPhotonSF", "reweightPhotonElectronVetoSF", "reweightBTag_SF"]

# weight the MC according to a variation
def MC_WEIGHT( variation, returntype = "string"):
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
    if returntype == "string":
        return "*".join(variiedMCWeights)
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

# Define all systematic variations
variations = {
    "central"                   : {"read_variables": [ "%s/F"%v for v in nominalMCWeights ]},
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
#    "jerUp"                     : {"selectionModifier":jetSelectionModifier("jerUp"),                                     "read_variables" : [ "%s/F"%v for v in nominalMCWeights + jetSelectionModifier("jerUp","list")]},
#    "jerDown"                   : {"selectionModifier":jetSelectionModifier("jerDown"),                                   "read_variables" : [ "%s/F"%v for v in nominalMCWeights + jetSelectionModifier("jerDown","list")]},
    "jesTotalUp"                : {"selectionModifier":jetSelectionModifier("jesTotalUp"),                                "read_variables" : [ "%s/F"%v for v in nominalMCWeights + jetSelectionModifier("jesTotalUp","list")]},
    "jesTotalDown"              : {"selectionModifier":jetSelectionModifier("jesTotalDown"),                              "read_variables" : [ "%s/F"%v for v in nominalMCWeights + jetSelectionModifier("jesTotalDown","list")]},
#    "unclustEnUp"               : {"selectionModifier":metSelectionModifier("unclustEnUp"),                               "read_variables" : [ "%s/F"%v for v in nominalMCWeights + jetSelectionModifier("unclustEnUp","list")]},
#    "unclustEnDown"             : {"selectionModifier":metSelectionModifier("unclustEnDown"),                             "read_variables" : [ "%s/F"%v for v in nominalMCWeights + jetSelectionModifier("unclustEnDown","list")]},
    "BTag_SF_b_Down"            : {"replaceWeight":("reweightBTag_SF","reweightBTag_SF_b_Down"),                          "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightBTag_SF_b_Down"]]},  
    "BTag_SF_b_Up"              : {"replaceWeight":("reweightBTag_SF","reweightBTag_SF_b_Up"),                            "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightBTag_SF_b_Up"] ]},
    "BTag_SF_l_Down"            : {"replaceWeight":("reweightBTag_SF","reweightBTag_SF_l_Down"),                          "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightBTag_SF_l_Down"]]},
    "BTag_SF_l_Up"              : {"replaceWeight":("reweightBTag_SF","reweightBTag_SF_l_Up"),                            "read_variables" : [ "%s/F"%v for v in nominalMCWeights + ["reweightBTag_SF_l_Up"] ]},
}

selection_systematics = [ "jerUp", "jerDown", "jesTotalUp", "jesTotalDown" ]
# Add a default selection modifier that does nothing
for key, variation in variations.iteritems():
    if not variation.has_key("selectionModifier"):
        variation["selectionModifier"] = lambda string:string
    if not variation.has_key("read_variables"):
        variation["read_variables"] = [] 

# Check if we know the variation
if args.variation is not None and args.variation not in variations.keys():
    raise RuntimeError( "Variation %s not among the known: %s", args.variation, ",".join( variation.keys() ) )

# arguments & directory
plot_subdirectory = args.plot_directory
if args.small:                    plot_subdirectory += "_small"
    
# Read variables and sequences
read_variables  = ["weight/F",
                   "PV_npvsGood/I",
                   "PV_npvs/I", "PV_npvsGood/I",
                   "nJetGood/I", "nBTagGood/I",
                   "nLeptonTight/I", "nElectronTight/I", "nMuonTight/I",
                   "nLeptonVeto/I", "nElectronVeto/I", "nMuonVeto/I",
                   "nPhotonGood/I",
                   "PhotonGood0[pt/F]",
                   "mlltight/F", "mllgammatight/F",
                   "mLtight0Gamma/F",
                   "m3/F", "ht/F",
                  ]
read_variables_MC = ["isTTGamma/I", "isZWGamma/I", "isTGamma/I", "overlapRemoval/I",
                     "reweightPU/F", "reweightPUDown/F", "reweightPUUp/F", "reweightPUVDown/F", "reweightPUVUp/F",
                     "reweightLeptonTightSF/F", "reweightLeptonTightSFUp/F", "reweightLeptonTightSFDown/F",
                     "reweightLeptonTrackingTightSF/F", "reweightLeptonTrackingTightSF/F", "reweightLeptonTrackingTightSF/F",
                     "reweightPhotonSF/F", "reweightPhotonSFUp/F", "reweightPhotonSFDown/F",
                     "reweightPhotonElectronVetoSF/F", "reweightPhotonElectronVetoSFUp/F", "reweightPhotonElectronVetoSFDown/F",
                     "reweightBTag_SF/F", "reweightBTag_SF_b_Down/F", "reweightBTag_SF_b_Up/F", "reweightBTag_SF_l_Down/F", "reweightBTag_SF_l_Up/F",
                     'reweightL1Prefire/F', 'reweightL1PrefireUp/F', 'reweightL1PrefireDown/F',
                    ]
sequence = []
signals = []

# Samples
os.environ["gammaSkim"]="True" if ("hoton" in args.selection or "pTG" in args.selection) else "False"
#os.environ["gammaSkim"]="False"
if args.year == 2016:
    from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed  import *
    from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import *
    mc  = [ TTG_16, TT_pow_16, DY_LO_16, WJets_16, WG_16, ZG_16, rest_16 ]
    qcd = QCD_16
    dy  = DY_LO_16

elif args.year == 2017:
    from TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed    import *
    from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import *
    mc = [ TTG_17, TT_pow_17, DY_LO_17, WJets_17, WG_17, ZG_17, rest_17 ]
    qcd = QCD_17
    dy  = DY_LO_17

elif args.year == 2018:
    from TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed  import *
    from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import *
    mc = [ TTG_18, TT_pow_18, DY_LO_18, WJets_18, WG_18, ZG_18, rest_18 ]
    qcd = QCD_18
    dy  = DY_LO_18

qcd.texName = "QCD (data)"

# postions of MC components in list
position = {s.name:i_s for i_s,s in enumerate(mc)}

if args.year == 2016:
    data_sample = Run2016
    data_sample.texName = "data (2016)"
elif args.year == 2017:
    data_sample = Run2017
    data_sample.texName = "data (2017)"
elif args.year == 2018:
    data_sample = Run2018
    data_sample.texName = "data (2018)"

# Define samples
data_sample.name           = "data"
data_sample.read_variables = ["event/I","run/I"]
data_sample.style          = styles.errorStyle(ROOT.kBlack)
data_sample.scale          = 1.
lumi_scale                 = data_sample.lumi/1000
logger.info("Lumi scale is " + str(lumi_scale))
for sample in mc:
    sample.scale           = lumi_scale
    sample.style           = styles.fillStyle(sample.color)
    sample.read_variables  = ["Pileup_nTrueInt/F"]
    # append variables for systematics
    if args.variation is not None:
        sample.read_variables+=list(set(variations[args.variation]["read_variables"]))

# reduce if small
if args.small:
  data_sample.normalization = 1.
  data_sample.reduceFiles( to = 1 )
  data_sample.scale /= data_sample.normalization
  for sample in mc:
    sample.normalization = 1.
    #sample.reduceFiles( factor = 40 )
    sample.reduceFiles( to = 1 )
    sample.scale /= sample.normalization

modes = ["mu", "e"] if args.mode=="all" else [ args.mode ]

allPlots   = {}

logger.info("Working on modes: %s", ",".join(modes))

# Fire up the cache
dirDB = MergingDirDB( os.path.join(cache_directory, "systematicPlots", str(args.year), args.selection))

# QCD cache
qcd_dirDB     = MergingDirDB( os.path.join(cache_directory, "qcdHistos") )

filterCutData = getFilterCut( args.year, isData=True, skipBadChargedCandidate=True )
filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )
tr            = TriggerSelector( args.year, singleLepton=args.selection.count("nLepTight1") )
triggerCutMc  = tr.getSelection( "MC" )
preSelection  = cutInterpreter.cutString(args.selection)

qcdPlotNames = {}
# loop over modes
for mode in modes:
    logger.info("Working on mode: %s", mode)

    leptonSelection = cutInterpreter.cutString( mode )
    # set selection
    data_sample.setSelectionString( [ filterCutData, leptonSelection ])
    for sample in mc:
        sample.setSelectionString(  [ filterCutMc,   leptonSelection, triggerCutMc, "overlapRemoval==1" ])

    # Use some defaults
    Plot.setDefaults( selectionString = preSelection )

    # if we"re running a variation specify
    if args.variation is not None:
        selectionModifier = variations[args.variation]["selectionModifier"]
        mc_weight         = MC_WEIGHT( variation = variations[args.variation], returntype="func")
    else:
        selectionModifier = None 
        mc_weight         = None 

    # Stack
    stack_mc   = Stack( mc )
    stack_data = Stack( data_sample )

    plots      = []

    if args.variation == "central":
        plots.append( Plot(
            name      = 'PhotonGood0_pt_data',
            texX      = 'p_{T}(#gamma_{0}) (GeV)',
            texY      = 'Number of Events',
            attribute = TreeVariable.fromString( "PhotonGood0_pt/F" ),
            binning   = [ 19, 20, 115 ],
            stack     = stack_data,
            weight    = data_weight,
        ))

    plots.append( Plot(
        name      = 'PhotonGood0_pt_mc',
        texX      = 'p_{T}(#gamma_{0}) (GeV)',
        texY      = 'Number of Events',
        attribute = TreeVariable.fromString( "PhotonGood0_pt/F" ),
        binning   = [ 19, 20, 115 ],
        stack     = stack_mc,
        selectionString = selectionModifier(cutInterpreter.cutString(args.selection)) if selectionModifier is not None else None,
        weight    = mc_weight,
    ))
    qcdPlotNames["PhotonGood0_pt_mc"] = {}
    qcdPlotNames["PhotonGood0_pt_mc"]["incl"]  = "PhotonGood0_pt"

    if args.variation == "central":
        plots.append( Plot(
            name      = 'nJetGood2_data',
            texX      = 'N_{jet}',
            texY      = 'Number of Events',
            attribute = TreeVariable.fromString( "nJetGood/I" ),
            binning   = [ 6, 2, 8 ],
            stack     = stack_data,
            weight    = data_weight,
        ))

    plots.append( Plot(
        name      = 'nJetGood2_mc',
        texX      = 'N_{jet}',
        texY      = 'Number of Events',
        attribute = TreeVariable.fromString('nJetGood/I') if args.variation not in selection_systematics else TreeVariable.fromString( "nJetGood_%s/I" % args.variation ),
        binning   = [ 6, 2, 8 ],
        stack     = stack_mc,
        selectionString = selectionModifier(cutInterpreter.cutString(args.selection)) if selectionModifier is not None else None,
        weight    = mc_weight,
    ))
    qcdPlotNames["nJetGood2_mc"] = {}
    qcdPlotNames["nJetGood2_mc"]["incl"]  = "nJetGood_semi2"

    if args.variation == "central":
        plots.append( Plot(
            name      = 'nJetGood3_data',
            texX      = 'N_{jet}',
            texY      = 'Number of Events',
            attribute = TreeVariable.fromString( "nJetGood/I" ),
            binning   = [ 5, 3, 8 ],
            stack     = stack_data,
            weight    = data_weight,
        ))

    plots.append( Plot(
        name      = 'nJetGood3_mc',
        texX      = 'N_{jet}',
        texY      = 'Number of Events',
        attribute = TreeVariable.fromString('nJetGood/I') if args.variation not in selection_systematics else TreeVariable.fromString( "nJetGood_%s/I" % args.variation ),
        binning   = [ 5, 3, 8 ],
        stack     = stack_mc,
        selectionString = selectionModifier(cutInterpreter.cutString(args.selection)) if selectionModifier is not None else None,
        weight    = mc_weight,
    ))
    qcdPlotNames["nJetGood3_mc"] = {}
    qcdPlotNames["nJetGood3_mc"]["incl"]  = "nJetGood_semi3"


    if args.variation == "central":
        plots.append( Plot(
            name      = 'nJetGood4_data',
            texX      = 'N_{jet}',
            texY      = 'Number of Events',
            attribute = TreeVariable.fromString( "nJetGood/I" ),
            binning   = [ 6, 4, 10 ],
            stack     = stack_data,
            weight    = data_weight,
        ))

    plots.append( Plot(
        name      = 'nJetGood4_mc',
        texX      = 'N_{jet}',
        texY      = 'Number of Events',
        attribute = TreeVariable.fromString('nJetGood/I') if args.variation not in selection_systematics else TreeVariable.fromString( "nJetGood_%s/I" % args.variation ),
        binning   = [ 6, 4, 10 ],
        stack     = stack_mc,
        selectionString = selectionModifier(cutInterpreter.cutString(args.selection)) if selectionModifier is not None else None,
        weight    = mc_weight,
    ))
    qcdPlotNames["nJetGood4_mc"] = {}
    qcdPlotNames["nJetGood4_mc"]["incl"]  = "nJetGood_semi"


    if args.variation == "central":
        plots.append( Plot(
            name      = 'mL0PhotonTight_data',
            texX      = 'M(#gamma,l_{0}) (GeV)',
            texY      = 'Number of Events',
            attribute = TreeVariable.fromString('mLtight0Gamma/F'),
            binning   = [ 17, 25, 195 ],
            stack     = stack_data,
            weight    = data_weight,
        ))

    plots.append( Plot(
        name      = 'mL0PhotonTight_mc',
        texX      = 'M(#gamma,l_{0}) (GeV)',
        texY      = 'Number of Events',
        attribute = TreeVariable.fromString('mLtight0Gamma/F'),
        binning   = [ 17, 25, 195 ],
        stack     = stack_mc,
        selectionString = selectionModifier(cutInterpreter.cutString(args.selection)) if selectionModifier is not None else None,
        weight    = mc_weight,
    ))
    qcdPlotNames["mL0PhotonTight_mc"] = {}
    qcdPlotNames["mL0PhotonTight_mc"]["incl"]        = "mL0PhotonTight_coarse"
    qcdPlotNames["mL0PhotonTight_mc"]["pTG20To120"]  = "mL0PhotonTight_20ptG120_coarse"
    qcdPlotNames["mL0PhotonTight_mc"]["pTG120To220"] = "mL0PhotonTight_120ptG220_coarse"
    qcdPlotNames["mL0PhotonTight_mc"]["pTG220"]      = "mL0PhotonTight_220ptGinf_coarse"

    if args.variation == "central":
        plots.append( Plot(
            name      = 'm3_data',
            texX      = 'M_{3} (GeV)',
            texY      = 'Number of Events',
            stack     = stack_data,
            attribute = TreeVariable.fromString('m3/F'),
            binning   = [ 22, 60, 500 ],
            weight    = data_weight,
        ))

    plots.append( Plot(
        name      = 'm3_mc',
        texX      = 'M_{3} (GeV)',
        texY      = 'Number of Events',
        attribute = TreeVariable.fromString('m3/F'),
        binning   = [ 22, 60, 500 ],
        stack     = stack_mc,
        selectionString = selectionModifier(cutInterpreter.cutString(args.selection)) if selectionModifier is not None else None,
        weight    = mc_weight,
    ))
    qcdPlotNames["m3_mc"] = {}
    qcdPlotNames["m3_mc"]["incl"]        = "m3_coarse"
    qcdPlotNames["m3_mc"]["pTG20To120"]  = "m3_20ptG120_coarse"
    qcdPlotNames["m3_mc"]["pTG120To220"] = "m3_120ptG220_coarse"
    qcdPlotNames["m3_mc"]["pTG220"]      = "m3_220ptGinf_coarse"

    if args.variation == "central":
        plots.append( Plot(
            name      = 'ht_data',
            texX      = 'H_{T} (GeV)',
            texY      = 'Number of Events',
            stack     = stack_data,
            attribute = TreeVariable.fromString('ht/F'),
            binning   = [ 20, 0, 600 ],
            weight    = data_weight,
        ))

    plots.append( Plot(
        name      = 'ht_mc',
        texX      = 'H_{T} (GeV)',
        texY      = 'Number of Events',
        attribute = TreeVariable.fromString('ht/F') if args.variation not in selection_systematics else TreeVariable.fromString( "ht_%s/I" % args.variation ),
        binning   = [ 20, 0, 600 ],
        stack     = stack_mc,
        selectionString = selectionModifier(cutInterpreter.cutString(args.selection)) if selectionModifier is not None else None,
        weight    = mc_weight,
    ))
    qcdPlotNames["ht_mc"] = {}
    qcdPlotNames["ht_mc"]["incl"] = "ht"


    if args.variation is not None:
        key  = (str(args.year), mode, args.variation, "small" if args.small else "full")
        if dirDB.contains(key) and not args.overwrite:
            normalisation_mc, normalisation_data, histos = dirDB.get( key )
            for i_p, h_s in enumerate(histos):
                plots[i_p].histos = h_s
            logger.info( "Loaded normalisations and histograms for %s in mode %s from cache.", str(args.year), mode)
        else:
            logger.info( "Obtain normalisations and histograms for %s in mode %s.", str(args.year), mode)
            # Calculate the normalisation yield for mt2ll<100
            normalization_selection_string = selectionModifier(cutInterpreter.cutString(args.selection))
            mc_normalization_weight_string = MC_WEIGHT(variations[args.variation], returntype="string")
            normalisation_mc = {s.name :s.scale*s.getYieldFromDraw(selectionString = normalization_selection_string, weightString = mc_normalization_weight_string)["val"] for s in mc}

            if args.variation == "central":
                normalisation_data = data_sample.scale*data_sample.getYieldFromDraw( selectionString = normalization_selection_string, weightString = data_weight_string)["val"]
            else:
                normalisation_data = -1

            logger.info( "Making plots.")
            plotting.fill(plots, read_variables = read_variables, sequence = sequence)

            # Delete lambda because we can"t serialize it
            for plot in plots:
                del plot.weight

            # save
            dirDB.add( key, (normalisation_mc, normalisation_data, [plot.histos for plot in plots]), overwrite = args.overwrite)

            logger.info( "Done with %s in channel %s.", args.variation, mode)

if args.variation is not None:
    logger.info( "Done with modes %s and variation %s of selection %s. Quit now.", ",".join( modes ), args.variation, args.selection )
    sys.exit(0)

systematics = [\
#    {"name":"JER",              "pair":("jerDown", "jerUp"),},
    {"name":"JEC",              "pair":("jesTotalDown", "jesTotalUp")},
#    {"name":"Unclustered",      "pair":("unclustEnDown", "unclustEnUp") },
    {"name":"PU",               "pair":("PUDown", "PUUp")},
    {"name":"BTag_b",           "pair":("BTag_SF_b_Down", "BTag_SF_b_Up" )},
    {"name":"BTag_l",           "pair":("BTag_SF_l_Down", "BTag_SF_l_Up")},
#    {"name":"trigger",          "pair":("DilepTriggerDown", "DilepTriggerUp")},
    {"name":"leptonSF",         "pair":("LeptonSFTightDown", "LeptonSFTightUp")},
    {"name":"leptonTrackingSF", "pair":("LeptonSFTrackingTightDown", "LeptonSFTrackingTightUp")},
    {"name":"photonSF",         "pair":("PhotonSFDown", "PhotonSFUp")},
    {"name":"evetoSF",          "pair":("PhotonElectronVetoSFDown", "PhotonElectronVetoSFUp")},
    {"name":"prefireSF",        "pair":("L1PrefireDown", "L1PrefireUp")},
]

# loop over modes
missing_cmds   = []
variation_data = {}
for mode in modes:
    logger.info("Working on mode: %s", mode)
    logger.info("Now attempting to load all variations from dirDB %s", dirDB.directory)
   
    for variation in variations.keys():
        key  = (str(args.year), mode, variation, "small" if args.small else "full")
        if dirDB.contains(key) and not args.overwrite:
            normalisation_mc, normalisation_data, histos = dirDB.get(key)
            variation_data[(mode, variation)] = {"histos":histos, "normalisation_mc":normalisation_mc, "normalisation_data":normalisation_data}
            logger.info( "Loaded normalisations and histograms for variation %s, year %s in mode %s from cache.", variation, str(args.year), mode)
        else:
            # prepare sub variation command
            cmd = ["python", "systematicVariation.py"]
            cmd.append("--logLevel %s"%args.logLevel)
            cmd.append("--plot_directory %s"%args.plot_directory)
            cmd.append("--selection %s"%args.selection)
            cmd.append("--variation %s"%variation)
            if args.small: cmd.append("--small")
            cmd.append("--mode %s"%args.mode)
            cmd.append("--year %s"%str(args.year))
            if args.overwrite: cmd.append("--overwrite")

            cmd_string = " ".join( cmd )
            missing_cmds.append( cmd_string )
            logger.info("Missing variation %s, year %s in mode %s in cache. Need to run: \n%s", variation, str(args.year), mode, cmd_string)

# write missing cmds
missing_cmds = list(set(missing_cmds))
if len(missing_cmds)>0:
    with file( "missing.sh", "w" ) as f:
        f.write("#!/bin/sh\n")
        for cmd in missing_cmds:
            f.write( cmd + "\n")
    logger.info( "Written %i variation commands to ./missing.sh. Now I quit!", len(missing_cmds) )
    sys.exit(0)
    
# make "all" and "SF" from ee/mumu/mue
new_modes = []
all_modes = list(modes)
if "mu" in modes and "e" in modes:
    new_modes.append( ("all", ("mu", "e")) )
    all_modes.append( "all" )
for variation in variations:
    for new_mode, old_modes in new_modes:
        new_key = ( new_mode, variation )
        variation_data[new_key] = {}
        # Adding up data_normalisation 
        if variation == "central":
            variation_data[new_key]["normalisation_data"] = sum( variation_data[( old_mode, variation )]["normalisation_data"] for old_mode in old_modes )
        else:
            variation_data[new_key]["normalisation_data"] = -1 

        # Adding up mc normalisation
        sample_keys = variation_data[( old_modes[0], variation )]["normalisation_mc"].keys()
        variation_data[new_key]["normalisation_mc"] = {}
        for sample_key in sample_keys: 
            variation_data[new_key]["normalisation_mc"][sample_key] = variation_data[( old_modes[0], variation )]["normalisation_mc"][sample_key]
            for mode in old_modes[1:]:
                variation_data[new_key]["normalisation_mc"][sample_key] += variation_data[( mode, variation )]["normalisation_mc"][sample_key]

        # Adding up histos (clone old_modes[0] at 3rd level, then add)
        variation_data[new_key]["histos"] = [[[ h.Clone() for h in hs ] for hs in plot_histos ] for plot_histos in variation_data[( old_modes[0], variation )]["histos"]]
        for mode in old_modes[1:]:
            for i_plot_histos, plot_histos in  enumerate(variation_data[( mode, variation )]["histos"]):
                for i_hs, hs in enumerate(plot_histos):
                    for i_h, h in enumerate(hs):
                        variation_data[new_key]["histos"][i_plot_histos][i_hs][i_h].Add(h)
                    

# SF for top central such that we get area normalisation 
dataMC_SF = {}
for mode in all_modes:
    # All SF to 1
    dataMC_SF[mode] = {variation:{s.name:1 for s in mc} for variation in variations}
    yield_data = variation_data[(mode,'central')]['normalisation_data']

def drawObjects( ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, "CMS Preliminary"),
      (0.45, 0.95, "L=%3.1f fb{}^{-1} (13 TeV)"% ( lumi_scale ) ),
      ]
    return [tex.DrawLatex(*l) for l in lines]


# remove pTG cuts in qcd key for cached histos
qcdSelection = "-".join( [ sel for sel in args.selection.split("-") if not "pTG" in sel ] )
qcdPtSelection = [ sel for sel in args.selection.split("-") if "pTG" in sel ]
if qcdPtSelection: qcdPtSelection = qcdPtSelection[0]
else:              qcdPtSelection = "incl"

def histmodification(log):
    def histmod(h):
#        h.GetXaxis().SetTitleOffset( 1.06 )
        h.GetYaxis().SetTitleOffset( 1.6 if log else 1.85 )

#        h.GetXaxis().SetTitleSize( 0.045 )
#        h.GetYaxis().SetTitleSize( 0.045 )

#        h.GetXaxis().SetLabelSize( 0.04 )
#        h.GetYaxis().SetLabelSize( 0.04 )
    return histmod

# We plot now. 
for mode in all_modes:

    # For cached QCD histos
    if mode == "all" and args.selection.count("nLepTight2"):
        qcdModes = ["eetight", "mumutight", "muetight"]
    elif mode == "SFtight" and args.selection.count("nLepTight2"):
        qcdModes = ["eetight", "mumutight"]
    elif mode == "all" and args.selection.count("nLepTight1"):
        qcdModes = ["e", "mu"]
    else:
        qcdModes = [mode]

    for i_plot, plot in enumerate(plots):
        
        # for central (=no variation), we store plot_data_1, plot_mc_1, plot_data_2, plot_mc_2, ...
        data_histo_list = variation_data[(mode, "central")]["histos"][2*i_plot]
        mc_histo_list   = {"central": variation_data[(mode, "central")]["histos"][2*i_plot+1] }
        # for the other variations, there is no data
        for variation in variations.keys():
            if variation=="central": continue
            mc_histo_list[variation] = variation_data[(mode, variation)]["histos"][i_plot]

        # copy styles and tex
        data_histo_list[0][0].style = data_sample.style
        data_histo_list[0][0].legendText = data_sample.texName
        for i_mc_hm, mc_h in enumerate( mc_histo_list["central"][0] ):
            mc_h.style = stack_mc[0][i_mc_hm].style
            mc_h.legendText = stack_mc[0][i_mc_hm].texName

        # perform the scaling
        for variation in variations.keys():
            for s in mc:
                mc_histo_list[variation][0][position[s.name]].Scale( dataMC_SF[mode][variation][s.name] ) 
                if variation == "central" and (addMisIDSF or addDYSF) and s.name==dy.name:
                    if addDYSF:    mc_histo_list[variation][0][position[dy.name]].Scale( default_DYSF )
                    if addMisIDSF: mc_histo_list[variation][0][position[dy.name]].Scale( default_misIDSF ) #fix that!!!!!!!!

        # For cached QCD histos
        qcdHist = None
        if not "nBJet" in plot.name and not "category" in plot.name:
            qcdPlotName = qcdPlotNames[plot.name][qcdPtSelection] if plot.name in qcdPlotNames and qcdPtSelection in qcdPlotNames[plot.name] else "None"
            for i_m, m in enumerate(qcdModes):
                res = "_".join( ["qcdHisto", qcdSelection, qcdPlotName, str(args.year), m, "small" if args.small else "full"] + map( str, plot.binning ) )
                print res
                if qcd_dirDB.contains(res):
                    logger.info( "Adding QCD histogram from cache for plot %s"%qcdPlotName )
                    print( "Adding QCD histogram from cache for plot %s"%qcdPlotName )
                    if i_m == 0: qcdHist = copy.deepcopy(qcd_dirDB.get(res))
                    else:        qcdHist.Add( copy.deepcopy(qcd_dirDB.get(res)) )
                else:
                    logger.info( "No QCD histogram found for plot %s"%qcdPlotName )
                    print( "No QCD histogram found for plot %s"%qcdPlotName )
                    qcdHist = None

        if qcdHist:
            qcdHist.style = styles.fillStyle( color.QCD )
            mc_histo_list["central"][0].append(qcdHist)

        # Add histos, del the stack (which refers to MC only )
        plot.histos =  mc_histo_list["central"] + data_histo_list
        plot.stack  = Stack( mc + [qcd] if qcdHist else mc, [data_sample] ) 
        
        # Make boxes and ratio boxes
        boxes           = []
        ratio_boxes     = []
        # Compute all variied MC sums
        total_mc_histo   = {variation:add_histos( mc_histo_list[variation][0]) for variation in variations.keys() }

        # loop over bins & compute shaded uncertainty boxes
        boxes   = []
        r_boxes = []
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
            box.SetLineColor(ROOT.kBlack)
            box.SetFillStyle(3444)
            box.SetFillColor(ROOT.kBlack)
            boxes.append(box)

            r_box = ROOT.TBox( 
                total_mc_histo["central"].GetXaxis().GetBinLowEdge(i_b),  
                max(0.1, 1-sigma_rel), 
                total_mc_histo["central"].GetXaxis().GetBinUpEdge(i_b), 
                min(1.9, 1+sigma_rel) )
            r_box.SetLineColor(ROOT.kBlack)
            r_box.SetFillStyle(3444)
            r_box.SetFillColor(ROOT.kBlack)
            ratio_boxes.append(r_box)

        for log in [False, True]:
            plot_directory_ = os.path.join(plot_directory, "systematicPlots", str(args.year), plot_subdirectory, selDir, mode, "log" if log else "lin")
            #if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot
            if    mode == "all": plot.histos[1][0].legendText = "Data (%i)"%args.year
            else:                plot.histos[1][0].legendText = "Data (%s, %i)"%(mode, args.year)

            _drawObjects = []

            plotting.draw(plot,
              plot_directory = plot_directory_,
              ratio = {"yRange":(0.1,1.9), "drawObjects":ratio_boxes},
              logX = False, logY = log, sorting = True,
              yRange = (0.03, "auto") if log else (0.001, "auto"),
              #scaling = {0:1},
              legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 3),
              drawObjects = drawObjects() + boxes,
              copyIndexPHP = True, extensions = ["png", "pdf"],
              histModifications = [histmodification(log)],
            )         
