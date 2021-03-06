# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy

# RootTools
from RootTools.core.standard           import *

# Analysis
from Analysis.Tools.metFilters         import getFilterCut
import Analysis.Tools.syncer as syncer

# Internal Imports
from TTGammaEFT.Tools.user             import plot_directory, cache_directory
from TTGammaEFT.Tools.cutInterpreter   import cutInterpreter
#from TTGammaEFT.Tools.TriggerSelector  import TriggerSelector

from TTGammaEFT.Analysis.SetupHelpers  import *
from TTGammaEFT.Analysis.Setup         import Setup
from TTGammaEFT.Analysis.EstimatorList import EstimatorList

from TTGammaEFT.Samples.color          import color
from Analysis.Tools.MergingDirDB      import MergingDirDB

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

addSF = False

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                        help="Log level for logging")
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv26_v1",                                             help="plot sub-directory")
argParser.add_argument("--selection",          action="store",      default="WJets2", type=str,                                              help="reco region")
argParser.add_argument("--addCut",             action="store",      default=None, type=str,                                                  help="additional cuts")
argParser.add_argument("--year",               action="store",      default="2016",   type=str,  choices=["2016","2017","2018","RunII"],                     help="Which year to plot?")
argParser.add_argument("--mode",               action="store",      default="e",  type=str,  choices=["mu", "e"],                            help="lepton selection")
argParser.add_argument("--overwrite",          action="store_true",                                                                          help="overwrite cache?")
args = argParser.parse_args()

if args.year != "RunII": args.year = int(args.year)

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile=None )
logger_rt = logger_rt.get_logger( args.logLevel, logFile=None )

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

cache_dir = os.path.join(cache_directory, "drawHistos", str(args.year), args.selection, args.mode)
dirDB = MergingDirDB(cache_dir)
if not dirDB: raise

# Sample definition
os.environ["gammaSkim"]="False" #always false for QCD estimate
if args.year == 2016:
    from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import Run2016 as data_sample
elif args.year == 2017:
    from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import Run2017 as data_sample
elif args.year == 2018:
    from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import Run2018 as data_sample
elif args.year == "RunII":
    from TTGammaEFT.Samples.nanoTuples_RunII_postProcessed import RunII as data_sample

filterCutData = getFilterCut( args.year, isData=True,  skipBadChargedCandidate=True )
data_sample.setSelectionString( [filterCutData,"reweightHEM>0"] )
data_sample.setWeightString( "weight" )
lumi_scale   = data_sample.lumi * 0.001

replaceSelection = {
#    "nLeptonVetoIsoCorr": "nLeptonVetoNoIso",
    "nLeptonTight":       "nLeptonTightInvIso",
    "nMuonTight":         "nMuonTightInvIso",
    "nElectronTight":     "nElectronTightInvIso",
    "mLtight0Gamma":      "mLinvtight0Gamma",
    "nPhotonGood":        "nPhotonGoodInvLepIso",
    "nJetGood":           "nJetGoodInvLepIso",
    "nBTagGood":          "nBTagGoodInvLepIso",
    "mT":                 "mTinv",
    "m3":                 "m3inv",
    "LeptonTight0":       "LeptonTightInvIso0",
    "JetGood0":           "JetGoodInvLepIso0",
    "JetGood1":           "JetGoodInvLepIso1",
}


if len(args.selection.split("-")) == 1 and args.selection in allRegions.keys():
    print( "Plotting region from SetupHelpers: %s"%args.selection )

    setup = Setup( year=args.year, photonSelection=False, checkOnly=False, runOnLxPlus=False ) #photonselection always false for qcd estimate
    setup = setup.sysClone( parameters=allRegions[args.selection]["parameters"] )

    selection  = setup.selection( "MC", channel=args.mode, **setup.defaultParameters() )["prefix"]
    selection  = cutInterpreter.cutString( selection )
    selection += "&&triggered==1"
    if args.addCut:
        selection += "&&" + cutInterpreter.cutString( args.addCut )
    print( "Using selection string: %s"%args.selection )

    preSelection  = setup.selection("MC",   channel=args.mode, **setup.defaultParameters(update=QCD_updates))["prefix"]
    preSelection  = cutInterpreter.cutString( preSelection )
    preSelection += "&&triggeredInvIso==1"
    if args.addCut:
        addSel = cutInterpreter.cutString( args.addCut )
        for iso, invIso in replaceSelection.iteritems():
            addSel = addSel.replace(iso,invIso)
        preSelection += "&&" + addSel

else:
    raise Exception("Region not implemented")

# histos
binning = [24, 30, 150, 48, -2.4, 2.4]
var     = "LeptonTight0_eta:LeptonTight0_pt"
invVar  = "LeptonTightInvIso0_eta:LeptonTightInvIso0_pt"

dataHist_SB = data_sample.get2DHistoFromDraw( invVar, binning=binning, selectionString=preSelection )
dataHist    = data_sample.get2DHistoFromDraw( var,    binning=binning, selectionString=selection    )

divHist = dataHist.Clone("div")
divHist.Divide(dataHist_SB)

dataHist.GetZaxis().SetTitle( "Number of Events" )
dataHist_SB.GetZaxis().SetTitle( "Number of Events" )
divHist.GetZaxis().SetTitle( "Data (AR) / Data (SB)" )

Plot2D.setDefaults()

mode = args.mode.replace("mu","#mu")

plots = []
plots.append( Plot2D.fromHisto( "data_eta_pt",          [[dataHist]],    texX = "p_{T}(%s) [GeV]"%mode,                texY = "#eta(%s)"%mode ) )
plots.append( Plot2D.fromHisto( "data_eta_pt_sideband", [[dataHist_SB]], texX = "p_{T}(%s) [GeV] (sideband)"%mode, texY = "#eta(%s) (sideband)"%mode ) )
plots.append( Plot2D.fromHisto( "data_eta_pt_ratio",    [[divHist]],     texX = "p_{T}(%s) [GeV]"%mode, texY = "#eta(%s)"%mode ) )

for plot in plots:

    for log in [True, False]:

        selDir = args.selection
        if args.addCut: selDir += "-" + args.addCut
        plot_directory_ = os.path.join( plot_directory, "qcdChecks", str(args.year), args.plot_directory, selDir, args.mode, "log" if log else "lin" )

        plotting.draw2D( plot,
                         plot_directory = plot_directory_,
                         logX = False, logY = False, logZ = log,
                         zRange = (0.03, "auto") if log else (0.001, "auto"),
                         drawObjects = drawObjects( lumi_scale ),
                         copyIndexPHP = True,
                       )

