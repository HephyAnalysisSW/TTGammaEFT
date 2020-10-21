    #!/usr/bin/env python

""" 
cardfile linearity test plots
"""

# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy

# Analysis
from Analysis.Tools.cardFileWriter.CombineResults    import CombineResults
import Analysis.Tools.syncer as syncer

# TTGammaEFT
from TTGammaEFT.Tools.user            import plot_directory, cache_directory
from TTGammaEFT.Analysis.SetupHelpers import *

# RootTools
from RootTools.core.standard          import *

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--small",                action="store_true",                            help="small?")
argParser.add_argument("--logLevel",             action="store",                default="INFO",  help="log level?", choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"])
argParser.add_argument("--misIDPOI",             action="store_true",                            help="Use misID as POI")
argParser.add_argument("--ttPOI",             action="store_true",                            help="Use tt as POI")
argParser.add_argument("--wJetsPOI",             action="store_true",                            help="Use w+jets as POI")
argParser.add_argument("--wgPOI",             action="store_true",                            help="Use wgamma as POI")
argParser.add_argument("--dyPOI",             action="store_true",                            help="Use dy as POI")
argParser.add_argument("--overwrite",            action="store_true",                            help="Overwrite existing output files, bool flag set to True  if used")
argParser.add_argument("--year",                 action="store",      type=str, default="2016",    help="Which year?")
argParser.add_argument("--carddir",              action='store',                default='limits/cardFiles/defaultSetup/observed',      help="which cardfile directory?")
argParser.add_argument("--cardfile",             action='store',                default='',      help="which cardfile?")
argParser.add_argument("--substituteCard",       action='store',                default=None,    help="which cardfile to substitute the plot with?")
argParser.add_argument("--bkgOnly",              action='store_true',                            help="background fit?")
args = argParser.parse_args()

# logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile = None )
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

if args.year != "combined": args.year = int(args.year)

if   args.year == 2016: lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74
elif args.year == "combined": lumi_scale = 35.92 + 41.53 + 59.74

dirName  = "_".join( [ item for item in args.cardfile.split("_") if not (item.startswith("add") or item == "incl") ] )
add      = [ item for item in args.cardfile.split("_") if (item.startswith("add") or item == "incl")  ]
add.sort()
add += ["expected"]
fit      = "_".join( ["postFit"] + add )

plot_directory_ = os.path.join(plot_directory, "fit", str(args.year), fit, dirName)
cardFile      = os.path.join( cache_directory, "analysis", str(args.year) if args.year != "combined" else "COMBINED", args.carddir, args.cardfile+".txt" )
logger.info("Plotting from cardfile %s"%cardFile)

sr = [r for r in args.cardfile.split("_") if "SR" in r][0]
sr = sr.replace("M3","")
lintests = [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4]

hist = ROOT.TH1F("hist", "hist", len(lintests), min(lintests)-0.05, max(lintests)+0.05)
hist.style = styles.errorStyle( ROOT.kAzure-3, width=2 )
hist.legendText = "SSM (MC Signal / Multiplier)"
#hist.legendText = "SSM (Exp.Observation #times Multiplier)"

Results = CombineResults( cardFile=cardFile, plotDirectory=plot_directory_, year=args.year, bkgOnly=args.bkgOnly, isSearch=False )

for val in lintests:
    postFit = Results.runLinearityTest( val )

    bin = hist.FindBin(val)
    print str(val), str(postFit)
    hist.SetBinContent( bin, postFit.val )
    hist.SetBinError( bin, postFit.sigma/val )

line = ROOT.TLine( min(lintests)-0.05, min(lintests)-0.05, max(lintests)+0.05, max(lintests)+0.05 )
line.SetLineWidth(2)
#line.SetLineStyle(7)
line.SetLineColor(ROOT.kBlack)

plot = Plot.fromHisto( "LinearityTest",  [[hist]], texX="Multiplier", texY="Signal Strength Modifier" )

# Text on the plots
def drawObjects( lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS #bf{#it{Preliminary}}'),
      (0.65, 0.95, '%3.1f fb{}^{-1} (13 TeV)' % lumi_scale),
    ]
    return [tex.DrawLatex(*l) for l in lines]


def drawPlots( plot ):

    maxY = max( [ h.GetMaximum() for hList in plot.histos for h in hList ] )
    plotting.draw( plot,
                   plot_directory = plot_directory_,
                   logX = False, logY = False, sorting = False,
                   yRange = (0., 2.),
                   legend = [(0.2,0.75,0.9,0.88), 1],
                   drawObjects = drawObjects( lumi_scale ) + [line],
                   copyIndexPHP = True,
                 )

drawPlots( plot )
