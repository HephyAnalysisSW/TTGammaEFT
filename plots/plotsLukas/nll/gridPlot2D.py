''' Plot script WC parameter LogLikelihood
'''

#https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/blob/102x/data/tutorials/count_toys_with_signif_lt_localmax.C#L42-L58

# Standard imports 
import sys, os, copy, ROOT
import ctypes

# RootTools
from RootTools.core.standard   import *
from RootTools.plot.helpers    import copyIndexPHP

# turn off graphics
ROOT.gROOT.SetBatch( True )

# TTGammaEFT
from TTGammaEFT.Tools.user              import plot_directory, cache_directory
from TTGammaEFT.Analysis.SetupHelpers    import *
from Analysis.Tools.MergingDirDB         import MergingDirDB
import Analysis.Tools.syncer as syncer

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

# Arguments
import argparse

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',            action='store',      default='INFO', nargs='?', choices=loggerChoices,                                help="Log level for logging")
argParser.add_argument('--xyRange',            action='store',      default=[None, None, None, None],  type=float, nargs=4,                          help="argument parameters")
argParser.add_argument('--tag',                 action='store',      default="combined",        type=str,                                             help='tag for unc studies')
argParser.add_argument('--variables' ,         action='store',      default = ['ctZ', 'ctZI'], type=str, nargs=2,                                    help="argument plotting variables")
args = argParser.parse_args()

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None)

plot_directory_ = os.path.join( plot_directory, "nllPlots" )

if not os.path.isdir( plot_directory_ ):
    try: os.makedirs( plot_directory_ )
    except: pass

#binning range
xRange = eftParameterRange[args.variables[0]]
yRange = eftParameterRange[args.variables[1]]


#xRange       = np.linspace( -1.0, 1.0, 30, endpoint=False)
#halfstepsize = 0.5 * ( xRange[1] - xRange[0] )
#xRange       = [ round(el + halfstepsize, 3) for el in xRange ] + [0]
#xRange.sort()
#yRange = xRange


points = [ (0,0) ] #SM point
points += [ (0, varY) for varY in yRange] #1D plots
points += [ (varX, 0) for varX in xRange] #1D plots
points += [ (varX, varY) for varY in yRange for varX in xRange] #2D plots

def toGraph2D( name, title, data ):
    result = ROOT.TGraph( len(data) )
    result.SetName( name )
    result.SetTitle( "" )
    for i, datapoint in enumerate(data):
        x, y = datapoint
        result.SetPoint(i, x, y)
    c = ROOT.TCanvas()
    result.Draw()
    del c
    return result

#get TGraph2D from results list
title = "TTG_%s_%s"%(args.variables[0], args.variables[1])
a = toGraph2D( title, title, points )
xbins = len(xRange)
ybins = len(yRange)
nxbins   = max( 1, min( 500, xbins ) )
nybins   = max( 1, min( 500, ybins ) )

#re-bin
hist = a #.GetHistogram().Clone()
hist.SetMarkerStyle(7)
hist.SetMarkerSize(2)

cans = ROOT.TCanvas("can_%s"%title,"",500,500)

pads = ROOT.TPad("pad_%s"%title,"",0.,0.,1.,1.)
#pads.SetRightMargin(0.20)
pads.SetLeftMargin(0.14)
pads.SetTopMargin(0.11)
pads.Draw()
pads.cd()

hist.Draw("AP")

if not None in args.xyRange[:2]:
    hist.GetXaxis().SetRangeUser( args.xyRange[0], args.xyRange[1] )
if not None in args.xyRange[2:]:
    hist.GetYaxis().SetRangeUser( args.xyRange[2], args.xyRange[3] )

xTitle = args.variables[0].replace("c", "C_{").replace("I", "}^{[Im]").replace('p','#phi') + '}'
yTitle = args.variables[1].replace("c", "C_{").replace("I", "}^{[Im]").replace('p','#phi') + '}'
hist.GetXaxis().SetTitle( xTitle + ' [(#Lambda/TeV)^{2}]' )
hist.GetYaxis().SetTitle( yTitle + ' [(#Lambda/TeV)^{2}]' )

hist.GetXaxis().SetTitleFont(42)
hist.GetYaxis().SetTitleFont(42)
hist.GetXaxis().SetLabelFont(42)
hist.GetYaxis().SetLabelFont(42)

#hist.GetXaxis().SetTitleOffset(1.05)
hist.GetYaxis().SetTitleOffset(1.45)

hist.GetXaxis().SetTitleSize(0.042)
hist.GetYaxis().SetTitleSize(0.042)
hist.GetXaxis().SetLabelSize(0.04)
hist.GetYaxis().SetLabelSize(0.04)

latex1 = ROOT.TLatex()
latex1.SetNDC()
latex1.SetTextSize(0.035)
latex1.SetTextFont(42)
latex1.SetTextAlign(11)

latex1.DrawLatex(0.15, 0.91, '#bf{CMS} #it{Preliminary}'),
#latex1.DrawLatex(0.70, 0.91, '#bf{13 TeV}')

latex2 = ROOT.TLatex()
latex2.SetNDC()
latex2.SetTextSize(0.04)
latex2.SetTextFont(42)
latex2.SetTextAlign(11)

# Redraw axis, otherwise the filled graphes overlay
pads.RedrawAxis()
l = ROOT.TLine()
l.DrawLine(cans.GetUxmin(), cans.GetUymax(), cans.GetUxmax(), cans.GetUymax());
l.DrawLine(cans.GetUxmax(), cans.GetUymin(), cans.GetUxmax(), cans.GetUymax());

plotname = "grid_".join(args.variables)
for e in [".png",".pdf",".root"]:
    cans.Print( plot_directory_ + "/%s%s"%(plotname, e) )

copyIndexPHP( plot_directory_ )

