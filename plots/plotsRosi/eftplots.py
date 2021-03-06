#!/usr/bin/env python

import os, copy, time, sys, pickle
import operator, ctypes
import ROOT
from shutil                              import copyfile
from math                                import sqrt

import numpy as np

# TTGammaEFT
from TTGammaEFT.Tools.user              import plot_directory, cache_directory
from TTGammaEFT.Tools.cutInterpreter    import cutInterpreter
from TTGammaEFT.Tools.genCutInterpreter import cutInterpreter as genCutInterpreter
from TTGammaEFT.Tools.Cache             import Cache

from TTGammaEFT.Analysis.SetupHelpers    import *

from Analysis.Tools.MergingDirDB         import MergingDirDB
from Analysis.Tools.WeightInfo          import WeightInfo
from Analysis.Tools.metFilters          import getFilterCut

# Multiprocessing
from multiprocessing import Pool

# RootTools
from RootTools.core.standard   import *

# turn off graphics
ROOT.gROOT.SetBatch( True )

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

# Arguments
import argparse

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                                help="Log level for logging")
argParser.add_argument('--genSelection1l',     action='store',      default='dilepOS-pTG20-nPhoton1p-offZSFllg-offZSFll-mll40-nJet2p-nBTag1p')
argParser.add_argument('--genSelection2l',     action='store',      default='dilepOS-pTG20-nPhoton1p-offZSFllg-offZSFll-mll40-nJet2p-nBTag1p')
argParser.add_argument('--selection1l',        action='store',      default='nLepTight1-nLepVeto1-nJet4p-nBTag1p-pTG20-nPhoton1p')
argParser.add_argument('--selection2l',        action='store',      default='dilepOS-nLepVeto2-pTG20-nPhoton1p-offZSFllg-offZSFll-mll40-nJet2p-nBTag1p')
argParser.add_argument('--variables' ,         action='store',      default = ['ctZI'], type=str, nargs=1,                                    help="argument plotting variables")
argParser.add_argument('--small',              action='store_true',                                                                                  help='Run only on a small subset of the data?', )
argParser.add_argument( "--year",               action="store",      default=2016,   type=int,                              help="Which year?" )
argParser.add_argument('--binning',            action='store',      default=[20, -1, 1], type=float, nargs=3,                            help="argument parameters")
argParser.add_argument('--selections',         action='store',      default=[ "1l" ], type=str, choices=["1l", "2l"], nargs="*",               help="Which selections to combine?")
argParser.add_argument('--contours',           action='store_true',                                                                                  help='draw 1sigma and 2sigma contour line?')
argParser.add_argument('--smooth',             action='store_true',                                                                                  help='smooth histogram?')
argParser.add_argument('--zRange',             action='store',      default=[None, None],      type=float, nargs=2,                                  help="argument parameters")
argParser.add_argument('--xyRange',            action='store',      default=[None, None],  type=float, nargs=2,                          help="argument parameters")
argParser.add_argument('--binMultiplier',      action='store',      default=3,                 type=int,                                             help='bin multiplication factor')
argParser.add_argument('--skipMissingPoints',  action='store_true',                                                                                  help='Set missing NLL points to 999?')
argParser.add_argument('--plotData',           action='store_true',                                                                                  help='Plot data points?')
argParser.add_argument('--tag',                action='store',      default="combined",        type=str,                                             help='tag for unc studies')
argParser.add_argument( "--expected",           action="store_true",                                                        help="Use sum of backgrounds instead of data." )
argParser.add_argument( "--inclRegion",         action="store_true",                                                        help="use inclusive photon pt region" )
argParser.add_argument( "--useRegions",         action="store",      nargs='*',       type=str, choices=allRegions.keys(),  help="Which regions to use?" )
args = argParser.parse_args()

# Logging
import Analysis.Tools.logger as logger
logger = logger.get_logger(       args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

# load and define the EFT sample
from TTGammaEFT.Samples.genTuples_TTGamma_EFT_postProcessed  import *
eftSample = TTG_4WC_ref

regionNames = []
if args.useRegions: regionNames = args.useRegions
print regionNames
regionNames.sort() 
print regionNames

baseDir       = os.path.join( cache_directory, "analysis",  str(args.year), "limits" )
cacheFileName = os.path.join( baseDir, "calculatednll" )
nllCache      = MergingDirDB( cacheFileName )


directory = os.path.join( plot_directory, "NLLPlots", str(args.year), "_".join( regionNames ))
if args.inclRegion and not args.expected: direc = os.path.join( directory, "inclusive")
if not args.inclRegion and args.expected: direc = os.path.join( directory, "expected")
if args.inclRegion and args.expected: direc = os.path.join( directory, "inclusive and expected")
plot_directory_ = os.path.join( direc, "_".join(args.variables) )
print plot_directory_
if not os.path.isdir( plot_directory_ ):
    try: os.makedirs( plot_directory_ )
    except: pass

if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74

#binning range
xbins, xlow, xhigh = args.binning[:3]
xRange = eftParameterRange["ctZI"] 

def getNllData( var1):
    EFTparams = ["ctZ", str(0), "ctZI", str(var1)]
    configlist = regionNames + EFTparams
    configlist.append("incl" if args.inclRegion else "diff")
    configlist.append("expected" if args.expected else "observed")
    sConfig = "_".join(configlist)
    print sConfig
    nll  = nllCache.get(sConfig)
    print nll
    print nllCache.contains(sConfig)
    return float(nll)


logger.info("Loading cache data" )
points2D = [ (0) ] #SM point
points2D += [ (varX) for varX in xRange] #1D plots

nllData  = [ (var1, getNllData( var1 )) for var1 in points2D ]
print nllData
sm_nll   = getNllData(0)

nllData  = [ (x, -2*(nll - sm_nll)) for x, nll in nllData ]
#length = len(nllData)
#for i in range(length):
 #   nllData[i][2] = 2*(nllData[i][2]-sm_nll)
  #  nllData[i] = tuple(nllData[i])

xNLL     = [ (x, nll) for x, nll in nllData ]

tmp = nllData
tmp.sort( key = lambda res: (res[0], res[1]) )

def toGraph( name, title, data ):
    result  = ROOT.TGraph( len(data) )
    result.SetName( name )
    result.SetTitle( title )
    for j, datapoint in enumerate(data):
        x, val = datapoint
        result.SetPoint(j, x, val)
    c = ROOT.TCanvas()
    result.Draw()
    del c
    #res = ROOT.TGraphDelaunay(result)
    return result

polString = "[0]*x**2+[1]*x**3+[2]*x**4+[3]*x**5+[4]*x**6+[5]*x**7+[6]*x**8+[7]*x**9+[8]*x**10+[9]*x**11+[10]*x**12"
xPlotLow, xPlotHigh = args.xyRange

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

    #print args.selections, " ".join(args.selections+year), var, '68', x68min, x68max
    #print args.selections, " ".join(args.selections+year), var, '95', x95min, x95max

    ROOT.gStyle.SetPadLeftMargin(0.14)
    ROOT.gStyle.SetPadRightMargin(0.1)
    ROOT.gStyle.SetPadTopMargin(0.11)

    # Plot
    cans = ROOT.TCanvas("cans","cans",500,500)

    #if not None in args.zRange:
    xhist.GetYaxis().SetRangeUser( 0, 10 )
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

    #if not None in args.zRange:
     #   func.GetYaxis().SetRangeUser( args.zRange[0], args.zRange[1] )
      #  func68.GetYaxis().SetRangeUser( args.zRange[0], args.zRange[1] )
       # func95.GetYaxis().SetRangeUser( args.zRange[0], args.zRange[1] )
    func.GetXaxis().SetRangeUser( xmin, xmax )
    func68.GetXaxis().SetRangeUser( xmin, xmax )
    func95.GetXaxis().SetRangeUser( xmin, xmax )

    xhist.Draw("ALO")
    func.Draw("COSAME")
    func95.Draw("FOSAME")
    func68.Draw("FOSAME")
    if args.plotData: xhist.Draw("PSAME")
#    xhist.Draw("LSAME")
    func.Draw("COSAME")

    # Redraw axis, otherwise the filled graphes overlay
    cans.RedrawAxis()

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

    funcName = "log-likelihood ratio"
    leg = ROOT.TLegend(0.3,0.7,0.7,0.87)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.035)
    leg.AddEntry( func, funcName ,"l")
    leg.AddEntry( func68, "68% CL", "f")
    leg.AddEntry( func95, "95% CL", "f")
    leg.Draw()

    xTitle = var.replace("c", "C_{").replace("I", "}^{[Im]").replace('p','#phi') + '}'
    xhist.GetXaxis().SetTitle( xTitle + ' (#Lambda/TeV)^{2}' )

    xhist.GetXaxis().SetTitleFont(42)
    xhist.GetYaxis().SetTitleFont(42)
    xhist.GetXaxis().SetLabelFont(42)
    xhist.GetYaxis().SetLabelFont(42)

    xhist.GetXaxis().SetTitleOffset(1.3)
    xhist.GetYaxis().SetTitleOffset(1.3)

    xhist.GetXaxis().SetTitleSize(0.045)
    xhist.GetYaxis().SetTitleSize(0.045)
    xhist.GetXaxis().SetLabelSize(0.04)
    xhist.GetYaxis().SetLabelSize(0.04)

    latex1 = ROOT.TLatex()
    latex1.SetNDC()
    latex1.SetTextSize(0.035)
    latex1.SetTextFont(42)
    latex1.SetTextAlign(11)

    addon = "(%s)" %("+".join(args.selections))
    latex1.DrawLatex(0.15, 0.92, '#bf{CMS} #it{Simulation Preliminary} ' + addon),
    latex1.DrawLatex(0.64, 0.92, '#bf{%3.1f fb{}^{-1} (13 TeV)}' % lumi_scale)

    plotname = "%s%s%s"%(var, "", "_%s"%args.tag if args.tag != "combined" else "")
    for e in [".png",".pdf",".root"]:
        cans.Print( plot_directory_ + "/%s%s"%(plotname, e) )
#    for e in [".png",".pdf",".root"]:
#        cans.Print( plot_directory_ + "/%s%s%s"%(var, "_profiled" if profiled else "", e) )

for i, dat in enumerate( [ xNLL ] ):
    xmin = [ xlow ][i]   if not [ xPlotLow ][i]   else [ xPlotLow ][i]
    xmax = [ xhigh ][i] if not [ xPlotHigh ][i] else [ xPlotHigh ][i]
    var = args.variables[i]
    plot1D( dat, var, xmin, xmax )


