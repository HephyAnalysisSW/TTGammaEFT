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

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                        help="Log level for logging")
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv26_v1",                                             help="plot sub-directory")
argParser.add_argument("--selection",          action="store",      default="WJets2", type=str,                                              help="reco region")
argParser.add_argument("--addCut",             action="store",      default=None, type=str,                                                  help="additional cuts")
argParser.add_argument("--variable",           action="store",      default="LeptonTight0_eta", type=str,                                    help="variable to plot")
argParser.add_argument("--binning",            action="store",      default=[20,-2.4,2.4],  type=float, nargs="*",                           help="binning of plots")
argParser.add_argument("--mode",               action="store",      default="all",  type=str,  choices=["mu", "e", "all"],                   help="lepton selection")
argParser.add_argument("--small",              action="store_true",                                                                          help="Run only on a small subset of the data?")
argParser.add_argument("--survey",             action="store_true",                                                                          help="all plots in one directory?")
argParser.add_argument("--photonCat",          action="store_true",                                                                          help="all plots in one directory?")
argParser.add_argument("--overwrite",          action="store_true",                                                                          help="overwrite cache?")
args = argParser.parse_args()

args.binning[0] = int(args.binning[0])

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

cache_dir = os.path.join(cache_directory, "drawHistos", "all", args.selection, args.mode)
dirDB = MergingDirDB(cache_dir)
if not dirDB: raise

# Sample definition
os.environ["gammaSkim"]="False" #always false for QCD estimat
from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import *
data2016 = Run2016
from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import *
data2017 = Run2017
from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import *
data2018 = Run2018

lumi_scale   = (data2016.lumi + data2017.lumi + data2018.lumi) * 0.001

filterCutData = getFilterCut( 2016, isData=True,  skipBadChargedCandidate=True )
data2016.setSelectionString( [filterCutData, "reweightHEM>0", cutInterpreter.cutString( args.mode )] )
data2016.setWeightString( "weight" )

filterCutData = getFilterCut( 2017, isData=True,  skipBadChargedCandidate=True )
data2017.setSelectionString( [filterCutData, "reweightHEM>0", cutInterpreter.cutString( args.mode )] )
data2017.setWeightString( "weight" )

filterCutData = getFilterCut( 2018, isData=True,  skipBadChargedCandidate=True )
data2018.setSelectionString( [filterCutData, "reweightHEM>0", cutInterpreter.cutString( args.mode )] )
data2018.setWeightString( "weight" )

setup = Setup( year=2016, photonSelection=False, checkOnly=False, runOnLxPlus=False ) #photonselection always false for qcd estimate
setup = setup.sysClone( parameters=allRegions[args.selection]["parameters"] )

selection = setup.selection( "MC", channel="all", **setup.defaultParameters() )["prefix"]
selection = cutInterpreter.cutString( selection )
selection += "&&triggered==1"
print selection
if args.addCut:
    selection += "&&" + cutInterpreter.cutString( args.addCut )
print( "Using selection string: %s"%selection )


key = (data2018.name, "18", args.variable, "_".join(map(str,args.binning)), data2018.weightString, data2018.selectionString, selection)
if dirDB.contains(key) and not args.overwrite:
    dataHist2018 = dirDB.get(key).Clone("edataAR18")
else:
    dataHist2018 = data2018.get1DHistoFromDraw( args.variable, binning=args.binning, selectionString=selection )
    dirDB.add(key, dataHist2018.Clone("edataAR18"), overwrite=True)

key = (data2017.name, "17", args.variable, "_".join(map(str,args.binning)), data2017.weightString, data2017.selectionString, selection)
if dirDB.contains(key) and not args.overwrite:
    dataHist2017 = dirDB.get(key).Clone("edataAR17")
else:
    dataHist2017 = data2017.get1DHistoFromDraw( args.variable, binning=args.binning, selectionString=selection )
    dirDB.add(key, dataHist2017.Clone("edataAR17"), overwrite=True)

key = (data2016.name, "16", args.variable, "_".join(map(str,args.binning)), data2016.weightString, data2016.selectionString, selection)
if dirDB.contains(key) and not args.overwrite:
    dataHist2016 = dirDB.get(key).Clone("mudataAR16")
else:
    dataHist2016 = data2016.get1DHistoFromDraw( args.variable, binning=args.binning, selectionString=selection )
    dirDB.add(key, dataHist2016.Clone("mudataAR17"), overwrite=True)

dataHist2016.style         = styles.errorStyle( ROOT.kBlack )
dataHist2016.legendText    = "data (2016)"

dataHist2017.style         = styles.errorStyle( ROOT.kRed )
dataHist2017.legendText    = "data (2017)"

dataHist2018.style         = styles.errorStyle( ROOT.kBlue )
dataHist2018.legendText    = "data (2018)"

histos     = [[dataHist2016], [dataHist2017], [dataHist2018]]

Plot.setDefaults()
replaceLabel = {
    "PhotonNoChgIsoNoSieie0_sieie": "#sigma_{i#eta i#eta}(#gamma)",
    "PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt": "chg.Iso(#gamma)"
}

plots = []
plots.append( Plot.fromHisto( args.variable + "_" + args.addCut if args.survey else args.variable,             histos,        texX = replaceLabel[args.variable],                   texY = "Number of Events" ) )

for plot in plots:

    legend = [ (0.2,0.9-0.025*sum(map(len, plot.histos)),0.9,0.9), 3 ]

    for log in [True, False]:

        ratio = {'yRange':(0.1,1.9), 'histos':[(0,1),(2,1)], 'texY': 'Data/Data'}

        selDir = args.selection
        if args.addCut and not args.survey: selDir += "-" + args.addCut
        plot_directory_ = os.path.join( plot_directory, "fakeDataHistos", "all", args.plot_directory, selDir, args.mode, "log" if log else "lin" )
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = log, #sorting = True,#plot.name != "mT_fit",
                       yRange = (0.3, "auto"),
                       ratio = ratio,
                       drawObjects = drawObjects( lumi_scale ),
                       scaling = { 1:0, 2:0 },
                       legend = legend,
                       copyIndexPHP = True,
                       )

