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
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv49_vdiss",                                             help="plot sub-directory")
argParser.add_argument("--year",               action="store",      default=2016,   type=int,  choices=[2016,2017,2018],                     help="Which year to plot?")
args = argParser.parse_args()

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile=None )
logger_rt = logger_rt.get_logger( args.logLevel, logFile=None )

# Text on the plots
def drawObjects( lumi_scale, log=False ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right

    tex2 = ROOT.TLatex()
    tex2.SetNDC()
    tex2.SetTextSize(0.05)
    tex2.SetTextAlign(11) # align right
    line = (0.58, 0.95, "%.1f fb^{-1} (13 TeV)" % lumi_scale)
    line2 = (0.15, 0.95, "Private Work")
    return [tex2.DrawLatex(*line2), tex.DrawLatex(*line)]

dataDir = "$CMSSW_BASE/src/Analysis/Tools/data/photonSFData/"

if args.year == 2016:
    g_file = 'g2016_ScalingFactors_80X_Summer16.root'
    g_key  = "Scaling_Factors_HasPix_R9 Inclusive"
elif args.year == 2017:
    g_file = 'g2017_PixelSeed_ScaleFactors_2017.root'
    g_key  = "Medium_ID"
elif args.year == 2018:
    g_file = 'g2018_HasPix_2018_private.root'
#    g_key  = "uncertainty"
    g_key  = "scalefactor"

if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74

sfHist = getObjFromFile( os.path.expandvars( os.path.join( dataDir, g_file ) ), g_key )
#sfHist.Scale(100)
sfHist.SetMarkerSize(1.8)
sfHist.GetZaxis().SetTitleOffset( 0.9 )

#for i in range( sfHist.GetNbinsX() ):
#    for j in range( sfHist.GetNbinsY() ):
#        sfHist.SetBinContent(i+1,j+1, float("%.2f"%sfHist.GetBinError(i+1,j+1)))


Plot2D.setDefaults()
plots = []
#plots.append( Plot2D.fromHisto( "pixelUnc_%i"%args.year,           [[sfHist]], texY="|#eta(#gamma)|", texX="p_{T}(#gamma) [GeV]", texZ="Uncertainty [%]" ) )
plots.append( Plot2D.fromHisto( "pixelSF_%i"%args.year,           [[sfHist]], texY="|#eta(#gamma)|", texX="p_{T}(#gamma) [GeV]", texZ="Scale factor" ) )

for plot in plots:

    plot.drawOption = "COLZTEXT"
    legend = (0.2,0.75,0.9,0.9)

    plot_directory_ = os.path.join( plot_directory, "PhotonID", str(args.year) )

    plotting.draw2D( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = False, logZ = False,
                       zRange = (0.84,1.16) if "SF" in plot.name else (0,10),
                       drawObjects = drawObjects( lumi_scale ),
                       copyIndexPHP = True,
#                       oldColors = True,
                       )

