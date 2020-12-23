# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy

# RootTools
from RootTools.core.standard           import *

# Analysis
import Analysis.Tools.syncer as syncer
from Analysis.Tools.helpers import getObjFromFile

# Internal Imports
from TTGammaEFT.Tools.user             import plot_directory
from TTGammaEFT.Tools.cutInterpreter   import cutInterpreter

from TTGammaEFT.Samples.color          import color

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                        help="Log level for logging")
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv26_v1",                                             help="plot sub-directory")
argParser.add_argument("--year",               action="store",      default=2016,   type=int,  choices=[2016,2017,2018],                     help="Which year to plot?")
args = argParser.parse_args()

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


dataDir = "$CMSSW_BASE/src/Analysis/Tools/data/photonSFData/"
if args.year == 2016:
    g_file = 'g2016_egammaPlots_MWP_PhoSFs_2016_LegacyReReco_New_private.root'
    g_key  = "EGamma_SF2D"
elif args.year == 2017:
    g_file = 'g2017_PhotonsMedium_mod_private_BostonAdded.root'
    g_key  = "EGamma_SF2D"
elif args.year == 2018:
    g_file = 'g2018_PhotonsMedium_mod_private_BostonAdded.root'
    g_key  = "EGamma_SF2D"

if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74

sfHist = getObjFromFile( os.path.expandvars( os.path.join( dataDir, g_file ) ), g_key )

for i in range( sfHist.GetNbinsX() ):
    for j in range( sfHist.GetNbinsY() ):
        sfHist.SetBinContent(i+1,j+1, float("%.3f"%sfHist.GetBinError(i+1,j+1)))

Plot2D.setDefaults()
plots = []
plots.append( Plot2D.fromHisto( "photonIDUnc_%i"%args.year,           [[sfHist]], texX="SuperCluster #eta", texY="p_{T} [GeV]" ) )

for plot in plots:

    plot.drawOption = "COLZTEXT"
    legend = (0.2,0.75,0.9,0.9)

    plot_directory_ = os.path.join( plot_directory, "PhotonID", str(args.year) )

    plotting.draw2D( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = True, logZ = False,
                       zRange = (0.85,1.1) if "scaleFactor" in plot.name else (0,0.1),
                       drawObjects = drawObjects( lumi_scale ),
                       copyIndexPHP = True,
#                       oldColors = True,
                       )

