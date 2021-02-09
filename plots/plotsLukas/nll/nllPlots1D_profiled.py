#!/usr/bin/env python

#https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/blob/102x/data/tutorials/count_toys_with_signif_lt_localmax.C#L42-L58

import os, copy, sys
import ctypes
import ROOT
from math                                import sqrt
import operator
from itertools import groupby 

# TTGammaEFT
from TTGammaEFT.Tools.user              import plot_directory, cache_directory
from TTGammaEFT.Tools.Cache             import Cache
from TTGammaEFT.Analysis.SetupHelpers    import *

from Analysis.Tools.MergingDirDB         import MergingDirDB
import Analysis.Tools.syncer as syncer

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
argParser.add_argument( "--addMisIDSF",         action="store_true",                                                        help="add default misID scale factor" )
argParser.add_argument('--tag',                 action='store',      default="combined",        type=str,                                             help='tag for unc studies')
argParser.add_argument('--variables',           action='store',      default='ctZI', type=str, nargs=1, choices=["ctZ","ctZI"],                      help="argument plotting variables")
argParser.add_argument( "--expected",           action="store_true",                                                        help="Use sum of backgrounds instead of data." )
argParser.add_argument( "--inclRegion",         action="store_true",                                                        help="use inclusive photon pt region" )
argParser.add_argument( "--useRegions",         action="store",      nargs='*',       type=str, choices=allRegions.keys(),  help="Which regions to use?" )
argParser.add_argument( "--useChannels",        action="store",      nargs='*', default=None,   type=str, choices=["e", "mu", "all", "comb"], help="Which lepton channels to use?" )
argParser.add_argument('--withbkg',             action='store_true',                                                                                  help='with bkg?')
argParser.add_argument('--withEFTUnc',             action='store_true',                                                        help="add EFT uncertainty?")
args = argParser.parse_args()

if args.year != "RunII": args.year = int(args.year)

# Logging
import Analysis.Tools.logger as logger
logger = logger.get_logger(       args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

args.variables = args.variables[0]

# load and define the EFT sample
from TTGammaEFT.Samples.genTuples_TTGamma_EFT_postProcessed  import *
eftSample = TTG_2WC_ref

regionNames = []
for reg in allRegions.keys():
    if reg in args.useRegions:
        regionNames.append(reg)

# use the regions as key for caches
regionNames.sort()
if args.addDYSF:     regionNames.append("addDYSF")
if args.addMisIDSF:  regionNames.append("addMisIDSF")
if args.inclRegion:  regionNames.append("incl")
if args.useChannels:  regionNames.append("_".join([ch for ch in args.useChannels if not "tight" in ch]))

if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74
elif args.year == "RunII": lumi_scale = 35.92 + 41.53 + 59.74

baseDir       = os.path.join( cache_directory, "analysis",  str(args.year) if args.year != "RunII" else "COMBINED", "limits", "withbkg" if args.withbkg else "withoutbkg" )
if args.withEFTUnc: baseDir = os.path.join( baseDir, "withEFTUnc" )
cacheFileName = os.path.join( baseDir, "calculatednll" )
nllCache      = MergingDirDB( cacheFileName )

print cacheFileName

directory = os.path.join( plot_directory, "nllPlotsApp", str(args.year), "_".join( regionNames ))
addon = "expected" if args.expected else "observed"
if args.plotData: addon += "_check"
plot_directory_ = os.path.join( directory, addon )

if not os.path.isdir( plot_directory_ ):
    try: os.makedirs( plot_directory_ )
    except: pass

#binning range
xRange = eftParameterRange["ctZ"]
yRange = eftParameterRange["ctZI"]




#xRange       = np.linspace( -1.0, 1.0, 30, endpoint=False)
#halfstepsize = 0.5 * ( xRange[1] - xRange[0] )
#xRange       = [ round(el + halfstepsize, 3) for el in xRange ] + [0]
#xRange.sort()
#yRange = xRange

print xRange
print yRange
def getNllData( varx, vary ):
    EFTparams = ["ctZ", str(varx), "ctZI", str(vary)]
    configlist = regionNames + EFTparams
    configlist.append("incl" if args.inclRegion else "diff")
    configlist.append("expected" if args.expected else "observed")
    sConfig = "_".join(configlist)

    if not nllCache.contains(sConfig):
        return None

    nll = nllCache.get(sConfig)

    if nll["nll"] == 0: return None

    nll = nll["nll"] + nll["nll0"]

    return float(nll)


logger.info("Loading cache data" )
points = [ (0,0) ] #SM point
points += [ (0, varY) for varY in yRange] #1D plots
points += [ (varX, 0) for varX in xRange] #1D plots
points += [ (varX, varY) for varY in yRange for varX in xRange] #2D plots

nllData  = [ (varx, vary, getNllData( varx, vary )) for (varx, vary) in points ]
nllData  = [ x for x in nllData if x[2] ]
sm_nll   = getNllData(0,0)

nllData  = [ (x, y, -2*(nll - sm_nll)) for x, y, nll in nllData ]
nllData.sort( key = lambda res: (res[0 if args.variables=="ctZ" else 1], res[2]) )

xNLL = []
for key, group in groupby( nllData, operator.itemgetter(0 if args.variables=="ctZ" else 1) ):
    x, y, res = list(group)[0]
    if res < 0: continue
    xNLL.append((x if args.variables=="ctZ" else y, res))

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

polString = "[0]*x**2+[1]*x**3+[2]*x**4+[3]*x**5+[4]*x**6" #+[5]*x**7+[6]*x**8+[7]*x**9+[8]*x**10+[9]*x**11+[10]*x**12"
xPlotLow, xPlotHigh = args.xRange

def plot1D( dat, var, xmin, xmax, lumi_scale ):
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
    xhist.GetYaxis().SetRangeUser( -0.01, 5.5 )
    xhist.GetXaxis().SetRangeUser( xmin, xmax )
    xhist.GetXaxis().SetLimits(xmin, xmax)


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

    funcName = "profiled log-likelihood ratio"
    leg = ROOT.TLegend(0.3,0.7,0.7,0.87)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.035)
    leg.AddEntry( func, funcName ,"l")
    leg.AddEntry( func68, "68%s CL [%.2f, %.2f]"%("%",x68min, x68max), "f")
    leg.AddEntry( func95, "95%s CL [%.2f, %.2f]"%("%",x95min, x95max), "f")
    leg.Draw()

    xTitle = var.replace("c", "C_{").replace("I", "}^{[Im]").replace('p','#phi') + '}'
    xhist.GetXaxis().SetTitle( xTitle + ' [(#Lambda/TeV)^{2}]' )

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

    plotname = "%s%s%s_profiled"%(var, "", "_%s"%args.tag if args.tag != "combined" else "")
    if args.withbkg: plotname += "_wBkg"
    if args.withEFTUnc: plotname += "_wEFTUnc"
    for e in [".png",".pdf",".root"]:
        cans.Print( plot_directory_ + "/%s%s"%(plotname, e) )

    copyIndexPHP( plot_directory_ )

#    for e in [".png",".pdf",".root"]:
#        cans.Print( plot_directory_ + "/%s%s%s"%(var, "_profiled" if profiled else "", e) )

xmin = xPlotLow  if xPlotLow  else -2.49
xmax = xPlotHigh if xPlotHigh else 2.49
plot1D( xNLL, args.variables, xmin, xmax, lumi_scale )

