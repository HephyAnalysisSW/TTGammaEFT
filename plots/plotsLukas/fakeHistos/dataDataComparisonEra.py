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
    dataB = Run2017B
    dataC = Run2017C
    dataD = Run2017D
    dataE = Run2017E
    dataF = Run2017F
elif args.year == 2018:
    from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import *
    data_sample = Run2018

lumi_scale   = data_sample.lumi * 0.001

filterCutData = getFilterCut( args.year, isData=True,  skipBadChargedCandidate=True )

print dataB.name
print dataF.name

setup = Setup( year=args.year, photonSelection=False, checkOnly=False, runOnLxPlus=False ) #photonselection always false for qcd estimate
setup = setup.sysClone( parameters=allRegions[args.selection]["parameters"] )

selection = setup.selection( "MC", channel="all", **setup.defaultParameters() )["prefix"]
selection = cutInterpreter.cutString( selection )
selection += "&&triggered==1"
if args.addCut:
    selection += "&&" + cutInterpreter.cutString( args.addCut )
print( "Using selection string: %s"%selection )

dataB.setSelectionString( [filterCutData, "reweightHEM>0", cutInterpreter.cutString( args.mode ), selection] )
dataB.setWeightString( "weight" )

dataC.setSelectionString( [filterCutData, "reweightHEM>0", cutInterpreter.cutString( args.mode ), selection] )
dataC.setWeightString( "weight" )

dataD.setSelectionString( [filterCutData, "reweightHEM>0", cutInterpreter.cutString( args.mode ), selection] )
dataD.setWeightString( "weight" )

dataE.setSelectionString( [filterCutData, "reweightHEM>0", cutInterpreter.cutString( args.mode ), selection] )
dataE.setWeightString( "weight" )

dataF.setSelectionString( [filterCutData, "reweightHEM>0", cutInterpreter.cutString( args.mode ), selection] )
dataF.setWeightString( "weight" )

key = (dataB.name, "B", args.variable, "_".join(map(str,args.binning)), dataB.weightString, dataB.selectionString, selection)
if dirDB.contains(key) and not args.overwrite:
    dataHistB = dirDB.get(key).Clone("B")
else:
    dataHistB = dataD.get1DHistoFromDraw( args.variable, binning=args.binning )
    dirDB.add(key, dataHistB.Clone("B"), overwrite=True)

key = (dataC.name, "C", args.variable, "_".join(map(str,args.binning)), dataC.weightString, dataC.selectionString, selection)
if dirDB.contains(key) and not args.overwrite:
    dataHistC = dirDB.get(key).Clone("C")
else:
    dataHistC = dataD.get1DHistoFromDraw( args.variable, binning=args.binning )
    dirDB.add(key, dataHistC.Clone("C"), overwrite=True)

key = (dataD.name, "D", args.variable, "_".join(map(str,args.binning)), dataD.weightString, dataD.selectionString, selection)
if dirDB.contains(key) and not args.overwrite:
    dataHistD = dirDB.get(key).Clone("D")
else:
    dataHistD = dataD.get1DHistoFromDraw( args.variable, binning=args.binning )
    dirDB.add(key, dataHistD.Clone("D"), overwrite=True)

key = (dataE.name, "E", args.variable, "_".join(map(str,args.binning)), dataE.weightString, dataE.selectionString, selection)
if dirDB.contains(key) and not args.overwrite:
    dataHistE = dirDB.get(key).Clone("E")
else:
    dataHistE = dataD.get1DHistoFromDraw( args.variable, binning=args.binning )
    dirDB.add(key, dataHistE.Clone("E"), overwrite=True)

key = (dataF.name, "F", args.variable, "_".join(map(str,args.binning)), dataF.weightString, dataF.selectionString, selection)
if dirDB.contains(key) and not args.overwrite:
    dataHistF = dirDB.get(key).Clone("F")
else:
    dataHistF = dataD.get1DHistoFromDraw( args.variable, binning=args.binning )
    dirDB.add(key, dataHistF.Clone("F"), overwrite=True)

dataHistB.style         = styles.errorStyle( ROOT.kBlack )
dataHistB.legendText    = "data (era B)"

dataHistC.style         = styles.errorStyle( ROOT.kRed )
dataHistC.legendText    = "data (era C)"

dataHistD.style         = styles.errorStyle( ROOT.kBlue )
dataHistD.legendText    = "data (era D)"

dataHistE.style         = styles.errorStyle( ROOT.kOrange )
dataHistE.legendText    = "data (era E)"

dataHistF.style         = styles.errorStyle( ROOT.kGreen )
dataHistF.legendText    = "data (era F)"

histos     = [[dataHistF], [dataHistC], [dataHistD], [dataHistE], [dataHistB]]

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

        ratio = {'yRange':(0.1,1.9), 'histos':[(1,0),(2,0),(3,0),(4,0)], 'texY': 'era/eraB'}

        selDir = args.selection
        if args.addCut and not args.survey: selDir += "-" + args.addCut
        plot_directory_ = os.path.join( plot_directory, "fakeEraHistos", str(args.year), args.plot_directory, selDir, args.mode, "log" if log else "lin" )
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = log, #sorting = True,#plot.name != "mT_fit",
                       yRange = (0.3, "auto"),
                       ratio = ratio,
                       drawObjects = drawObjects( lumi_scale ),
                       scaling = { 1:0, 2:0, 3:0, 4:0 },
                       legend = legend,
                       copyIndexPHP = True,
                       )

