#!/usr/bin/env python

#https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/blob/102x/data/tutorials/count_toys_with_signif_lt_localmax.C#L42-L58

import os, copy, sys
import ctypes
import ROOT
ROOT.gROOT.LoadMacro('$CMSSW_BASE/src/Analysis/Tools/scripts/tdrstyle.C')
ROOT.setTDRStyle()
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
argParser.add_argument('--splitScale',             action='store_true',                                                        help="split scale uncertainties in sources")
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
if args.splitScale:   regionNames.append("splitScale")

regionNamesExp = copy.deepcopy(regionNames)

if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74
elif args.year == "RunII": lumi_scale = int(35.92 + 41.53 + 59.74)

baseDir       = os.path.join( cache_directory, "analysis",  str(args.year) if args.year != "RunII" else "COMBINED", "limits", "withbkg" if args.withbkg else "withoutbkg" )
if args.withEFTUnc: baseDir = os.path.join( baseDir, "withEFTUnc" )
cacheFileName = os.path.join( baseDir, "calculatednll" )
nllCache      = MergingDirDB( cacheFileName )

print cacheFileName

directory = os.path.join( plot_directory, "nllPlotsJHEP", str(args.year), "_".join( regionNames ))
addon = "comb"
if args.plotData: addon += "_check"
plot_directory_ = os.path.join( directory, addon )

if not os.path.isdir( plot_directory_ ):
    try: os.makedirs( plot_directory_ )
    except: pass

#binning range
xRange = eftParameterRange["ctZ"]
yRange = eftParameterRange["ctZI"]

xRange = [ el for el in xRange if abs(el) <= 0.6 ]
yRange = [ el for el in yRange if abs(el) <= 0.6 ]

xRange = [ el for el in xRange if abs(el) > 0.05 ]
yRange = [ el for el in yRange if abs(el) > 0.05 ]



#xRange       = np.linspace( -1.0, 1.0, 30, endpoint=False)
#halfstepsize = 0.5 * ( xRange[1] - xRange[0] )
#xRange       = [ round(el + halfstepsize, 3) for el in xRange ] + [0]
#xRange.sort()
#yRange = xRange

print xRange
print yRange
def getNllData( varx, vary ):
    dict = {"ctZ":varx, "ctZI":vary}
    EFTparams = ["ctZ", str(dict["ctZ"]), "ctZI", str(dict["ctZI"])]

    configlist = regionNames + EFTparams
    configlist.append("incl" if args.inclRegion else "diff")
    configlist.append("observed")
    sConfig = "_".join(configlist)

    configlistExp = regionNamesExp + EFTparams
    configlistExp.append("incl" if args.inclRegion else "diff")
    configlistExp.append("expected")
    sConfigExp = "_".join(configlistExp)

    print sConfig
    if not nllCache.contains(sConfig):
        nll = None
    else:
        nll = nllCache.get(sConfig)
        if nll["nll"] == 0: nll = None
        else: nll = nll["nll"] + nll["nll0"]

    if not nllCache.contains(sConfigExp):
        nllExp = None
    else:
        nllExp = nllCache.get(sConfigExp)
        if nllExp["nll"] == 0: nllExp = None
        else: nllExp = nllExp["nll"] + nllExp["nll0"]

    return nll, nllExp


logger.info("Loading cache data" )
points = [ (0,0) ] #SM point
points += [ (0, varY) for varY in yRange] #1D plots
points += [ (varX, 0) for varX in xRange] #1D plots
points += [ (varX, varY) for varY in yRange for varX in xRange] #2D plots

nllData  = [ (varx, vary, getNllData( varx, vary )) for (varx, vary) in points ]
nllDataExp  = [ (x[0], x[1], x[2][1]) for x in nllData if x[2][1] ]
nllData  = [ (x[0], x[1], x[2][0]) for x in nllData if x[2][0] ]
sm_nllExp   = getNllData(0,0)[1]

#allResults = sorted([y for y in nllData], key=lambda x:x[2])
allResults = sorted([y for y in nllData], key=lambda x:x[2])
sm_nll   = allResults[0][2]
xmin   = allResults[0][0 if args.variables=="ctZ" else 1]


nllDataExp  = [ (x, y, 2*(nll - sm_nllExp)) for x, y, nll in nllDataExp ]
nllDataExp.sort( key = lambda res: (res[0 if args.variables=="ctZ" else 1], res[2]) )
nllData     = [ (x, y, 2*(nll - sm_nll)) for x, y, nll in nllData ]
nllData.sort( key = lambda res: (res[0 if args.variables=="ctZ" else 1], res[2]) )

xNLL = []
i=0
for key, group in groupby( nllData, operator.itemgetter(0 if args.variables=="ctZ" else 1) ):
    i+=1
#    if not i%2: continue
    x, y, res = list(group)[0]
#    if res < 0: continue
    xNLL.append((x if args.variables=="ctZ" else y, res))

xNLLExp = []
for key, group in groupby( nllDataExp, operator.itemgetter(0 if args.variables=="ctZ" else 1) ):
    x, y, res = list(group)[0]
#    if res < 0: continue
    xNLLExp.append((x if args.variables=="ctZ" else y, res))

with open("%s_1D_obs_profiled.dat"%args.variables,"w") as f:
    f.write("%s,-2DeltaNLL\n"%args.variables)
    for x, nll in xNLL:
        f.write(str(x)+","+str(nll)+"\n")

with open("%s_1D_exp_profiled.dat"%args.variables,"w") as f:
    f.write("%s,-2DeltaNLL\n"%args.variables)
    for x, nll in xNLLExp:
        f.write(str(x)+","+str(nll)+"\n")

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

print tuple([xmin]*8)
polStringExp = "[0]*x**2+[1]*x**3+[2]*x**4+[3]*x**5+[4]*x**6" #+[7]*x**7+[8]*x**8" #+[5]*x**7+[6]*x**8"#+[7]*x**9+[8]*x**10+[9]*x**11+[10]*x**12"
polString = "[0]+[1]*(x)+[2]*(x)**2+[3]*(x)**3+[4]*(x)**4+[5]*x**7+[6]*x**8+[7]*x**9+[8]*x**10+[9]*x**11+[10]*x**12"
#polString = "[0]*(x-%f)+[1]*(x-%f)**2+[2]*(x-%f)**3+[3]*(x-%f)**4"%(tuple([xmin]*4)) #+[5]*x**7+[6]*x**8"#+[7]*x**9+[8]*x**10+[9]*x**11+[10]*x**12"
xPlotLow, xPlotHigh = args.xRange

def plot1D( dat, datExp, var, xmin, xmax, lumi_scale ):
    # get TGraph from results data list
    xhist = toGraph( var, var, dat )
    func  = ROOT.TF1("func", polString, xmin, xmax )
    xhist.Fit(func,"NO")

    # compensate for small rounding issues
    # profiled limits must be worse than non-profiled ones
    # however due to the fitting the value can be e.g. 0.1648 in the profiled one and 0.1651 in the non-profiled one
    # make the profiled one slightly worse to compensate for that
    # ugly but works
    x68min = func.GetX( 0.989, xmin, 0 )
    x68max = func.GetX( 0.989, 0, xmax )
    x95min = func.GetX( 3.84, xmin, 0 )
    x95max = func.GetX( 3.84, 0, xmax )

    print "68min", x68min
    print "68max", x68max
    print "95min", x95min
    print "95max", x95max

#    x68min = round( abs(x68min), 2 ) if x68min > 0 else -round( abs( x68min), 2 )
#    x68max = round( abs(x68max), 2 ) if x68max > 0 else -round( abs( x68max), 2 )
#    x95min = round( abs(x95min), 2 ) if x95min > 0 else -round( abs( x95min), 2 )
#    x95max = round( abs(x95max), 2 ) if x95max > 0 else -round( abs( x95max), 2 )

    xhist.SetLineWidth(0)

    func.SetFillColor(ROOT.kWhite)
    func.SetFillStyle(1001)
    func.SetLineWidth(3)
    func.SetLineColor(ROOT.kBlack)
    func.SetNpx(1000)




    xhistExp = toGraph( var, var, datExp )
    funcExp  = ROOT.TF1("func", polStringExp, xmin, xmax )
    xhistExp.Fit(funcExp,"NO")

    xhist.SetLineWidth(0)

    func.SetFillColor(ROOT.kWhite)
    func.SetFillStyle(1001)
    func.SetLineWidth(3)
    func.SetLineColor(ROOT.kBlack)
    func.SetNpx(1000)


    funcExp.SetFillColor(ROOT.kWhite)
    funcExp.SetFillStyle(1001)
    funcExp.SetLineWidth(3)
#    funcExp.SetLineStyle(11)
    funcExp.SetLineColor(ROOT.kGray+1)
    funcExp.SetNpx(1000)


    x68min = funcExp.GetX( 0.989, xmin, 0 )
    x68max = funcExp.GetX( 0.989, 0, xmax )
    x95min = funcExp.GetX( 3.84, xmin, 0 )
    x95max = funcExp.GetX( 3.84, 0, xmax )

    print "expected"
    print "68min", x68min
    print "68max", x68max
    print "95min", x95min
    print "95max", x95max

    ROOT.gStyle.SetPadLeftMargin(0.14)
    ROOT.gStyle.SetPadRightMargin(0.1)
    ROOT.gStyle.SetPadTopMargin(0.11)
    ROOT.gStyle.SetPadBottomMargin(0.11)

    # Plot
    cans = ROOT.TCanvas("cans","cans",500,500)

    #if not None in args.zRange:
    xhist.GetYaxis().SetRangeUser( -0.01, 5.5 )
    xhist.GetXaxis().SetRangeUser( xmin, xmax )
#    xhist.GetXaxis().SetLimits(xmin, xmax)


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
    funcExp.Draw("COSAME")
    func.Draw("COSAME")
    if args.plotData: xhist.Draw("*SAME")
    if args.plotData: xhistExp.Draw("*SAME")

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

    funcName = ""
    empt = ROOT.TObject()
    leg = ROOT.TLegend(0.35,0.67,0.73,0.85)
#    leg = ROOT.TLegend(0.22,0.7,0.8,0.87)
    leg.SetNColumns(2)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.037)
    leg.AddEntry( func, "Observed","l")
    leg.AddEntry( func68, "68%s CL"%("%"), "f")
    leg.AddEntry( funcExp, "Expected" ,"l")
    leg.AddEntry( func95, "95%s CL"%("%"), "f")
    leg.AddEntry( empt, "profiled","")
    leg.Draw()

    xTitle = var.replace("c", "c_{").replace("I", "}^{I").replace('p','#phi') + '}'
    xhist.GetXaxis().SetTitle( xTitle + ' [(#Lambda/TeV)^{2}]' )

    xhist.GetXaxis().SetTitleFont(42)
    xhist.GetYaxis().SetTitleFont(42)
    xhist.GetXaxis().SetLabelFont(42)
    xhist.GetYaxis().SetLabelFont(42)

    xhist.GetXaxis().SetTitleOffset(1.1)
    xhist.GetYaxis().SetTitleOffset(0.85)

    xhist.GetXaxis().SetTitleSize(0.042)
    xhist.GetYaxis().SetTitleSize(0.042)
    xhist.GetXaxis().SetLabelSize(0.04)
    xhist.GetYaxis().SetLabelSize(0.04)

    latex1 = ROOT.TLatex()
    latex1.SetNDC()
    latex1.SetTextSize(0.035)
    latex1.SetTextFont(42)
    latex1.SetTextAlign(11)

    latex2 = ROOT.TLatex()
    latex2.SetNDC()
    latex2.SetTextSize(0.05)
    latex2.SetTextFont(42)
    latex2.SetTextAlign(11)

    addon = ""
#    latex1.DrawLatex(0.15, 0.91, '#bf{CMS} #it{Preliminary} ' + addon),
    latex2.DrawLatex(0.15, 0.91, '#bf{CMS} ' + addon),
    if isinstance(lumi_scale, int):
        latex1.DrawLatex(0.67, 0.91, '#bf{%i fb^{-1} (13 TeV)}' % lumi_scale)
    else:
        latex1.DrawLatex(0.67, 0.91, '#bf{%3.1f fb^{-1} (13 TeV)}' % lumi_scale)

    # Redraw axis, otherwise the filled graphes overlay
    cans.RedrawAxis()

    plotname = "%s%s%s_profiled_wExp"%(var, "", "_%s"%args.tag if args.tag != "combined" else "")
    if args.withbkg: plotname += "_wBkg"
    if args.withEFTUnc: plotname += "_wEFTUnc"
    for e in [".png",".pdf",".root"]:
        cans.Print( plot_directory_ + "/%s%s"%(plotname, e) )

    copyIndexPHP( plot_directory_ )

#    for e in [".png",".pdf",".root"]:
#        cans.Print( plot_directory_ + "/%s%s%s"%(var, "_profiled" if profiled else "", e) )

xmin = xPlotLow  if xPlotLow  else -2.49
xmax = xPlotHigh if xPlotHigh else 2.49
plot1D( xNLL, xNLLExp, args.variables, xmin, xmax, lumi_scale )

