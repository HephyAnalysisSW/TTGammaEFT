#!/usr/bin/env python

import os, copy, sys
import ctypes
import ROOT
from math                                import sqrt

# TTGammaEFT
from TTGammaEFT.Tools.user              import plot_directory, cache_directory
from TTGammaEFT.Tools.Cache             import Cache
from TTGammaEFT.Analysis.SetupHelpers    import *

from Analysis.Tools.MergingDirDB         import MergingDirDB

# RootTools
from RootTools.core.standard   import *
from RootTools.plot.helpers    import copyIndexPHP
# turn off graphics
ROOT.gROOT.SetBatch( True )

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

# Arguments
import argparse

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',            action='store',      default='INFO', nargs='?', choices=loggerChoices,                                help="Log level for logging")
argParser.add_argument( "--year",               action="store",      default="2016",   type=str,                              help="Which year?" )
argParser.add_argument('--xRange',             action='store',      default=[None, None],  type=float, nargs=2,                          help="argument parameters")
argParser.add_argument('--plotData',            action='store_true',                                                                                  help='Plot data points?')
argParser.add_argument('--addDYSF',             action='store_true',                                                                                  help='Plot data points taken with --addDYSF?')
argParser.add_argument('--tag',                 action='store',      default="combined",        type=str,                                             help='tag for unc studies')
argParser.add_argument('--variables',           action='store',      default='ctZI', type=str, nargs=1, choices=["ctZ","ctZI", "ctW", "ctWI"],                      help="argument plotting variables")
argParser.add_argument( "--expected",           action="store_true",                                                        help="Use sum of backgrounds instead of data." )
argParser.add_argument( "--inclRegion",         action="store_true",                                                        help="use inclusive photon pt region" )
argParser.add_argument( "--useRegions",         action="store",      nargs='*',       type=str, choices=allRegions.keys(),  help="Which regions to use?" )
argParser.add_argument( "--withbkg",         action="store_true", help="reweight sample and bkg or sample only?" )
args = argParser.parse_args()

if args.year != "RunII": args.year = int(args.year)

# Logging
import Analysis.Tools.syncer as syncer
import Analysis.Tools.logger as logger
logger = logger.get_logger(       args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

args.variables = args.variables[0]

# load the EFT samples
from TTGammaEFT.Samples.genTuples_TTGamma_EFT_postProcessed  import *

regionNames = []
for reg in allRegions.keys():
    if reg in args.useRegions:
        regionNames.append(reg)

# use the regions as key for caches
regionNames.sort()
if args.addDYSF:     regionNames.append("addDYSF")
if args.inclRegion:  regionNames.append("incl")

baseDir       = os.path.join( cache_directory, "analysis",  str(args.year), "limits", "withbkg" if args.withbkg else "withoutbkg" )
cacheFileName = os.path.join( baseDir, "calculatednll" )
nllCache      = MergingDirDB( cacheFileName )

print cacheFileName

directory = os.path.join( plot_directory, "nllPlots", str(args.year), "_".join( regionNames ))
addon = "expected" if args.expected else "observed"
if args.plotData: addon += "_check"
plot_directory_ = os.path.join( directory, addon, "withbkg" if args.withbkg else "withoutbkg", "incl" if args.inclRegion else "diff" )

if not os.path.isdir( plot_directory_ ):
    try: os.makedirs( plot_directory_ )
    except: pass

if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74
elif args.year == "RunII": lumi_scale = 35.92 + 41.53 + 59.74

#binning range
xRange = eftParameterRange[args.variables] 
print xRange
def getNllData(var1):
    dict = {"ctZ":0, "ctZI":0, "ctW":0, "ctWI":0}
    dict[args.variables] = var1
    EFTparams = ["ctZ", str(dict["ctZ"]), "ctZI", str(dict["ctZI"]),"ctW", str(dict["ctW"]), "ctWI", str(dict["ctWI"])]
    configlist = regionNames + EFTparams
    configlist.append("incl" if args.inclRegion else "diff")
    configlist.append("expected" if args.expected else "observed")
    #configlist.append("withbkg" if args.withbkg else "withoutbkg")
    sConfig = "_".join(configlist)
    print(nllCache.contains(sConfig))
    if nllCache.contains(sConfig): nll = nllCache.get(sConfig)
    else:                          nll = -999
    print nll
    print sConfig
    return float(nll)


logger.info("Loading cache data" )
points = [ (0) ] #SM point
points += [ (varX) for varX in xRange] #1D plots

nllData  = [ (var1, getNllData( var1 )) for var1 in points ]
sm_nll   = getNllData(0)

nllData  = [ (x, -2*(nll - sm_nll)) for x, nll in nllData  if nll > -998 ]
#length = len(nllData)
#for i in range(length):
 #   nllData[i][2] = 2*(nllData[i][2]-sm_nll)
  #  nllData[i] = tuple(nllData[i])

xNLL     = [ (x, nll) for x, nll in nllData if nll >= 0 ]

tmp = nllData
tmp.sort( key = lambda res: (res[0], res[1]) )

def toGraph( name, title, data ):
    result  = ROOT.TGraph( len(data) )
    result.SetName( name )
    result.SetTitle( "" )
    for j, datapoint in enumerate(data):
        x, val = datapoint
        result.SetPoint(j, x, val)
    c = ROOT.TCanvas()
    result.Draw()
    del c
    #res = ROOT.TGraphDelaunay(result)
    return result

polString = "[0]*x**2+[1]*x**3+[2]*x**4"#+[3]*x**5+[4]*x**6"#+[5]*x**7+[6]*x**8"#+[7]*x**9+[8]*x**10+[9]*x**11+[10]*x**12"
xPlotLow, xPlotHigh = args.xRange

def plot1D( dat, var, xmin, xmax ):
    # get TGraph from results data list
    xhist = toGraph( var, var, dat )
    func  = ROOT.TF1("func", polString, xmin, xmax )
    xhist.Fit(func,"NO")
    x68min = func.GetX( 0.989, xmin, 0 )
    x68max = func.GetX( 0.989, 0, xmax )
    x95min = func.GetX( 3.84, xmin, 0 )
    x95max = func.GetX( 3.84, 0, xmax )

    xhist.SetLineWidth(0)

    func.SetFillColor(ROOT.kWhite)
    func.SetFillStyle(1001)
    func.SetLineWidth(3)
    func.SetLineColor(ROOT.kBlack)
    func.SetNpx(1000)

    ROOT.gStyle.SetPadLeftMargin(0.14)
    ROOT.gStyle.SetPadRightMargin(0.1)
    ROOT.gStyle.SetPadTopMargin(0.11)
    ROOT.gStyle.SetPadBottomMargin(0.11)

    # Plot
    cans = ROOT.TCanvas("cans","cans",500,500)

    #if not None in args.zRange:
    xhist.GetYaxis().SetRangeUser( 0, 5.5 )
    xhist.GetXaxis().SetRangeUser( xmin, xmax )


    func95 = ROOT.TF1("func95",polString, x95min,x95max )
    xhist.Fit(func95,"NO")
    func95.SetFillColor(ROOT.kOrange+7)
    func95.SetFillStyle(1001)
    func95.SetLineWidth(0)
    func95.SetNpx(1000)

    func68 = ROOT.TF1("func68",polString, x68min,x68max )
    xhist.Fit(func68,"NO")
    func68.SetFillColor(ROOT.kSpring-1)
    func68.SetFillStyle(1001)
    func68.SetLineWidth(0)
    func68.SetNpx(1000)

    func.GetXaxis().SetRangeUser( xmin, xmax )
    func68.GetXaxis().SetRangeUser( xmin, xmax )
    func95.GetXaxis().SetRangeUser( xmin, xmax )

    xhist.Draw("ALO")
    func.Draw("COSAME")
    func95.Draw("FOSAME")
    func68.Draw("FOSAME")
#    xhist.Draw("LSAME")
    func.Draw("COSAME")
    if args.plotData: xhist.Draw("*SAME")

    # dashed line at 1
    line5 = ROOT.TLine(xmin, 0.989, xmax, 0.989 )
    line5.SetLineWidth(1)
    line5.SetLineStyle(7)
    line5.SetLineColor(ROOT.kBlack)
    # dashed line at 4
    line6 = ROOT.TLine(xmin, 3.84, xmax, 3.84 )
    line6.SetLineWidth(1)
    line6.SetLineStyle(7)
    line6.SetLineColor(ROOT.kBlack)

    line5.Draw()
    line6.Draw()

    xhist.GetYaxis().SetTitle("-2 #Delta ln L")

    print x68min, x68max
    print x95min, x95max

    funcName = "log-likelihood ratio"
    leg = ROOT.TLegend(0.3,0.7,0.7,0.87)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.035)
    leg.AddEntry( func, funcName ,"l")
    leg.AddEntry( func68, "68%s CL [%.2f, %.2f]"%("%",x68min, x68max), "f")
    leg.AddEntry( func95, "95%s CL [%.2f, %.2f]"%("%",x95min, x95max), "f")
    leg.Draw()

    xTitle = var.replace("c", "C_{").replace("I", "}^{[Im]").replace('p','#phi') + '}'
    xhist.GetXaxis().SetTitle( xTitle + ' (#Lambda/TeV)^{2}' )

    xhist.GetXaxis().SetTitleFont(42)
    xhist.GetYaxis().SetTitleFont(42)
    xhist.GetXaxis().SetLabelFont(42)
    xhist.GetYaxis().SetLabelFont(42)

#    xhist.GetXaxis().SetTitleOffset(1.3)
#    xhist.GetYaxis().SetTitleOffset(1.3)

    xhist.GetXaxis().SetTitleSize(0.042)
    xhist.GetYaxis().SetTitleSize(0.042)
    xhist.GetXaxis().SetLabelSize(0.04)
    xhist.GetYaxis().SetLabelSize(0.04)

    latex1 = ROOT.TLatex()
    latex1.SetNDC()
    latex1.SetTextSize(0.035)
    latex1.SetTextFont(42)
    latex1.SetTextAlign(11)

    addon = ""
    latex1.DrawLatex(0.15, 0.91, '#bf{CMS} #it{Simulation Preliminary} ' + addon),
    latex1.DrawLatex(0.64, 0.91, '#bf{%3.1f fb{}^{-1} (13 TeV)}' % lumi_scale)

    # Redraw axis, otherwise the filled graphes overlay
    cans.RedrawAxis()

    plotname = "%s%s%s"%(var, "", "_%s"%args.tag if args.tag != "combined" else "")
    for e in [".png",".pdf",".root"]:
        cans.Print( plot_directory_ + "/%s%s"%(plotname, e) )

    copyIndexPHP( plot_directory_ )

#    for e in [".png",".pdf",".root"]:
#        cans.Print( plot_directory_ + "/%s%s%s"%(var, "_profiled" if profiled else "", e) )


xmin = xPlotLow  if xPlotLow  else -1.49
xmax = xPlotHigh if xPlotHigh else 1.49
if args.variables == "ctW":
    xmin = -0.3
    xmax = 0.3
if args.variables == "ctWI":
    xmin = -0.8
    xmax = 0.8
plot1D( xNLL, args.variables, xmin, xmax )
print (xmin, xmax)
