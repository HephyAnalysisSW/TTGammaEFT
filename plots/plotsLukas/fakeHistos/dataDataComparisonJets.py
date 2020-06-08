# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy

# RootTools
from RootTools.core.standard           import *

# Analysis
from Analysis.Tools.metFilters         import getFilterCut

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
argParser.add_argument("--year",               action="store",      default=2016,   type=int,  choices=[2016,2017,2018],                     help="Which year to plot?")
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

cache_dir = os.path.join(cache_directory, "drawHistos", str(args.year), args.selection, args.mode)
dirDB = MergingDirDB(cache_dir)
if not dirDB: raise

# Sample definition
os.environ["gammaSkim"]="False" #always false for QCD estimate
if args.year == 2016:
    from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import *
    data_sample = Run2016
elif args.year == 2017:
    from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import *
    data_sample = Run2017
elif args.year == 2018:
    from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import *
    data_sample = Run2018

lumi_scale   = data_sample.lumi * 0.001

filterCutData = getFilterCut( args.year, isData=True,  skipBadChargedCandidate=True )

data_sample_2   = copy.deepcopy(data_sample)
data_sample_3   = copy.deepcopy(data_sample)
data_sample_4p  = copy.deepcopy(data_sample)

setup = Setup( year=args.year, photonSelection=False, checkOnly=False, runOnLxPlus=False ) #photonselection always false for qcd estimate
setup = setup.sysClone( parameters=allRegions[args.selection]["parameters"] )

selection = setup.selection( "MC", channel="all", **setup.defaultParameters() )["prefix"]
selection = cutInterpreter.cutString( selection.replace("4p","2") )
selection += "&&triggered==1"
if args.addCut:
    selection += "&&" + cutInterpreter.cutString( args.addCut )
print( "Using selection string: %s"%selection )

data_sample_2.setSelectionString( [filterCutData, "reweightHEM>0", cutInterpreter.cutString( args.mode ), selection] )
data_sample_2.setWeightString( "weight" )

setup = Setup( year=args.year, photonSelection=False, checkOnly=False, runOnLxPlus=False ) #photonselection always false for qcd estimate
setup = setup.sysClone( parameters=allRegions[args.selection]["parameters"] )

selection = setup.selection( "MC", channel="all", **setup.defaultParameters() )["prefix"]
selection = cutInterpreter.cutString( selection.replace("4p","3") )
selection += "&&triggered==1"
if args.addCut:
    selection += "&&" + cutInterpreter.cutString( args.addCut )
print( "Using selection string: %s"%selection )

data_sample_3.setSelectionString( [filterCutData, "reweightHEM>0", cutInterpreter.cutString( args.mode ), selection] )
data_sample_3.setWeightString( "weight" )

setup = Setup( year=args.year, photonSelection=False, checkOnly=False, runOnLxPlus=False ) #photonselection always false for qcd estimate
setup = setup.sysClone( parameters=allRegions[args.selection]["parameters"] )

selection = setup.selection( "MC", channel="all", **setup.defaultParameters() )["prefix"]
selection = cutInterpreter.cutString( selection )
selection += "&&triggered==1"
if args.addCut:
    selection += "&&" + cutInterpreter.cutString( args.addCut )
print( "Using selection string: %s"%selection )

data_sample_4p.setSelectionString( [filterCutData, "reweightHEM>0", cutInterpreter.cutString( args.mode ), selection] )
data_sample_4p.setWeightString( "weight" )

key = (data_sample_4p.name, "4p", args.variable, "_".join(map(str,args.binning)), data_sample_4p.weightString, data_sample_4p.selectionString, selection)
if dirDB.contains(key) and not args.overwrite:
    dataHist_4p = dirDB.get(key).Clone("4p")
else:
    dataHist_4p = data_sample_4p.get1DHistoFromDraw( args.variable, binning=args.binning )
    dirDB.add(key, dataHist_4p.Clone("4p"), overwrite=True)

key = (data_sample_3.name, "3", args.variable, "_".join(map(str,args.binning)), data_sample_3.weightString, data_sample_3.selectionString, selection)
if dirDB.contains(key) and not args.overwrite:
    dataHist_3 = dirDB.get(key).Clone("3")
else:
    dataHist_3 = data_sample_3.get1DHistoFromDraw( args.variable, binning=args.binning )
    dirDB.add(key, dataHist_3.Clone("3"), overwrite=True)

key = (data_sample_2.name, "2", args.variable, "_".join(map(str,args.binning)), data_sample_2.weightString, data_sample_2.selectionString, selection)
if dirDB.contains(key) and not args.overwrite:
    dataHist_2 = dirDB.get(key).Clone("2")
else:
    dataHist_2 = data_sample_2.get1DHistoFromDraw( args.variable, binning=args.binning )
    dirDB.add(key, dataHist_2.Clone("2"), overwrite=True)

dataHist_2.style         = styles.errorStyle( ROOT.kBlack )
dataHist_2.legendText    = "data (2 jets)"

dataHist_3.style         = styles.errorStyle( ROOT.kRed )
dataHist_3.legendText    = "data (3 jets)"

dataHist_4p.style         = styles.errorStyle( ROOT.kBlue )
dataHist_4p.legendText    = "data (#geq 4 jets)"

histos     = [[dataHist_2], [dataHist_3], [dataHist_4p]]

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

        ratio = {'yRange':(0.1,1.9), 'histos':[(0,2),(1,2)], 'texY': 'Data/Data'}

        selDir = "234jets"
        if args.addCut and not args.survey: selDir += "-" + args.addCut
        plot_directory_ = os.path.join( plot_directory, "fakeDataHistos", str(args.year), args.plot_directory, selDir, args.mode, "log" if log else "lin" )
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

