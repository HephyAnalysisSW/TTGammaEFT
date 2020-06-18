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
from TTGammaEFT.Tools.TriggerSelector  import TriggerSelector

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
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv41_v2",                                             help="plot sub-directory")
argParser.add_argument("--year",               action="store",      default="2016",   type=str,  choices=["2016","2017","2018","RunII"],                     help="Which year to plot?")
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

# Sample definition
os.environ["gammaSkim"]="False" #always false for QCD estimate
if args.year == 2016:
    postprocessing_directory = "TTGammaEFT_PP_2016_TTG_private_v44/semilep/"
    import TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed_ptstitched as mc_samples
    lumi_scale   = 35.92
elif args.year == 2017:
    postprocessing_directory = "TTGammaEFT_PP_2017_TTG_private_v44/semilep/"
    import TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed_ptstitched as mc_samples
    lumi_scale   = 41.53
elif args.year == 2018:
    postprocessing_directory = "TTGammaEFT_PP_2018_TTG_private_v44/semilep/"
    import TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed_ptstitched as mc_samples
    lumi_scale   = 59.74
elif args.year == "RunII":
    import TTGammaEFT.Samples.nanoTuples_RunII_postProcessed as mc_samples
    lumi_scale   = 137.2

mc = copy.deepcopy(mc_samples.TTG)#_stitched
mcStitched = mc_samples.TTG_stitched
mcLow = mc_samples.TTG
mcMed = mc_samples.TTG_med
mcHigh = mc_samples.TTG_high

mcStitched.setSelectionString( [ "pTStitching==1" ] )
mcLow.setSelectionString( [ "pTStitching==1" ] )
mcMed.setSelectionString( [ "pTStitching==1" ] )
mcHigh.setSelectionString( [ "pTStitching==1" ] )

#variable = "GenPhotonCMSUnfold0_pt"
variable = "stitchedPt"
binning = [30, 0, 300]
selection = "1"

mc.hist = mc.get1DHistoFromDraw( variable, binning=binning, selectionString=selection, weightString="weight*%f"%lumi_scale, addOverFlowBin="upper" )
mcStitched.hist = mcStitched.get1DHistoFromDraw( variable, binning=binning, selectionString=selection, weightString="weight*%f"%lumi_scale, addOverFlowBin="upper" )
mcLow.hist = mcLow.get1DHistoFromDraw( variable, binning=binning, selectionString=selection, weightString="weight*%f"%lumi_scale, addOverFlowBin="upper" )
mcMed.hist = mcMed.get1DHistoFromDraw( variable, binning=binning, selectionString=selection, weightString="weight*%f"%lumi_scale, addOverFlowBin="upper" )
mcHigh.hist = mcHigh.get1DHistoFromDraw( variable, binning=binning, selectionString=selection, weightString="weight*%f"%lumi_scale, addOverFlowBin="upper" )

mc.hist.style         = styles.lineStyle( ROOT.kBlack, width=2 )
mc.hist.legendText    = "tt#gamma (total)"

mcStitched.hist.style         = styles.lineStyle( ROOT.kOrange, width=2 )
mcStitched.hist.legendText    = "tt#gamma (total stitched)"

mcLow.hist.style         = styles.lineStyle( ROOT.kGreen+2, width=2 )
mcLow.hist.legendText    = "tt#gamma (low p_{T})"

mcMed.hist.style         = styles.lineStyle( ROOT.kBlue, width=2 )
mcMed.hist.legendText    = "tt#gamma (med p_{T})"

mcHigh.hist.style         = styles.lineStyle( ROOT.kRed, width=2 )
mcHigh.hist.legendText    = "tt#gamma (high p_{T})"

histos     = [[mcLow.hist, mcMed.hist, mcHigh.hist],[mc.hist], [mcStitched.hist]]

Plot.setDefaults()

plots = []
plots.append( Plot.fromHisto( variable,             histos,        texX = "p_{T}(#gamma)",                   texY = "Number of Events" ) )

for plot in plots:

    legend = [ (0.2,0.9-0.025*sum(map(len, plot.histos)),0.9,0.9), 3 ]

    for log in [True, False]:

        plot_directory_ = os.path.join( plot_directory, "ptStitching", str(args.year), args.plot_directory, "log" if log else "lin" )
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = log, sorting = True,
                       yRange = (0.3, "auto"),
                       ratio = {'histos':[(2,1)], 'texY': 'stitched/incl'},
                       drawObjects = drawObjects( lumi_scale ),
                       legend = legend,
                       copyIndexPHP = True,
                       )

