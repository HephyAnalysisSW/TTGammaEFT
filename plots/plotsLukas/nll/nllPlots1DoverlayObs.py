#!/usr/bin/env python

#https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/blob/102x/data/tutorials/count_toys_with_signif_lt_localmax.C#L42-L58

import os, copy, sys
import ctypes
import ROOT
ROOT.gROOT.LoadMacro('$CMSSW_BASE/src/Analysis/Tools/scripts/tdrstyle.C')
ROOT.setTDRStyle()
from math                                import sqrt

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

regionNamesExp = copy.deepcopy(regionNames)
#regionNamesExp.append("incl")

baseDir       = os.path.join( cache_directory, "analysis",  str(args.year) if args.year != "RunII" else "COMBINED", "limits", "withbkg" if args.withbkg else "withoutbkg" )
if args.withEFTUnc: baseDir = os.path.join( baseDir, "withEFTUnc" )
cacheFileName = os.path.join( baseDir, "calculatednll" )
nllCache      = MergingDirDB( cacheFileName )

directory = os.path.join( plot_directory, "nllPlotsPostCWR", str(args.year), "_".join( regionNames ))
addon = "comb"
if args.plotData: addon += "_check"
plot_directory_ = os.path.join( directory, addon )

if not os.path.isdir( plot_directory_ ):
    try: os.makedirs( plot_directory_ )
    except: pass

if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74
elif args.year == "RunII": lumi_scale = int(35.92 + 41.53 + 59.74)

#binning range
xRange = eftParameterRange[args.variables]

#xRange       = np.linspace( -1.0, 1.0, 30, endpoint=False)
#halfstepsize = 0.5 * ( xRange[1] - xRange[0] )
#xRange       = [ round(el + halfstepsize, 3) for el in xRange ] + [0]
#xRange.sort()


#print xRange
def getNllData( var1):
    dict = {"ctZI":0, "ctZ":0}
    dict[args.variables] = var1
    EFTparams = ["ctZ", str(dict["ctZ"]), "ctZI", str(dict["ctZI"])]

    configlist = regionNames + EFTparams
    configlist.append("incl" if args.inclRegion else "diff")
    configlist.append("observed")
    sConfig = "_".join(configlist)

    configlistExp = regionNamesExp + EFTparams
    configlistExp.append("incl" if args.inclRegion else "diff")
    configlistExp.append("expected")
    sConfigExp = "_".join(configlistExp)

#    print sConfigExp
#    print sConfig
    if not nllCache.contains(sConfig):
        nll = None
    else:
        nll = nllCache.get(sConfig)
        print var1, nll["nll"], nll["nll0"]
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
points = [ (0) ] #SM point
points += [ (varX) for varX in xRange] #1D plots

nllData  = [ (var1, getNllData( var1 )) for var1 in points ]
nllData  = [ x for x in nllData if x[1][0] and x[1][1] ]

_, sm_nllExp   = getNllData(0)

allResults = sorted([y for y in nllData], key=lambda x:x[1][0])
#for x in allResults: print x
sm_nll   = allResults[0][1][0]
#print sm_nll, allResults[0]
nllDataExp  = [ (x, 2*(nll[1] - sm_nllExp)) for x, nll in nllData if nll[1] ]
############
nllData  = [ (x, 2*(nll[0] - sm_nll)) for x, nll in nllData if nll[0] ]
#for x in nllData: print x

with open("%s_1D_obs.dat"%args.variables,"w") as f:
    f.write("%s,-2DeltaNLL\n"%args.variables)
    for x, nll in nllData:
        f.write(str(x)+","+str(nll)+"\n")

with open("%s_1D_exp.dat"%args.variables,"w") as f:
    f.write("%s,-2DeltaNLL\n"%args.variables)
    for x, nll in nllDataExp:
        f.write(str(x)+","+str(nll)+"\n")



print nllData
xNLL     = [ (x, nll) for x, nll in nllData if nll >= 0 and nll < 6]
xNLLExp = [ (x, nll) for x, nll in nllDataExp if nll >= 0 and nll < 6]

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

#polString = "[0]*x**2+[1]*x**3+[2]*x**4+[3]*x**5+[4]*x**6" #+[5]*x**7+[6]*x**8"#+[7]*x**9+[8]*x**10+[9]*x**11+[10]*x**12"
polString = "[0]+[1]*x+[2]*x**2+[3]*x**3+[4]*x**4+[5]*x**5+[6]*x**6" #+[5]*x**7+[6]*x**8"#+[7]*x**9+[8]*x**10+[9]*x**11+[10]*x**12"
xPlotLow, xPlotHigh = args.xRange

def plot1D( dat, datExp, var, xmin, xmax ):
    # get TGraph from results data list
    xhist = toGraph( var, var, dat )
    xhistExp = toGraph( var+"Exp", var, datExp )

#    polStringExp = "[0]+[1]*x+[2]*x**2+[3]*x**3+[4]*x**4+[5]*x**5+[6]*x**6+[7]*x**7+[8]*x**8" #+[7]*x**7+[8]*x**8" #+[5]*x**7+[6]*x**8"#+[7]*x**9+[8]*x**10+[9]*x**11+[10]*x**12"
    polStringExp = "[0]*x**2+[1]*x**3+[2]*x**4+[3]*x**5+[4]*x**6" #+[7]*x**7+[8]*x**8" #+[5]*x**7+[6]*x**8"#+[7]*x**9+[8]*x**10+[9]*x**11+[10]*x**12"
    polString = "[0]+[1]*x+[2]*x**2+[3]*x**3+[4]*x**4+[5]*x**5+[6]*x**6" #+[7]*x**7+[8]*x**8" #+[5]*x**7+[6]*x**8"#+[7]*x**9+[8]*x**10+[9]*x**11+[10]*x**12"

    func  = ROOT.TF1("func", polString, xmin, xmax )
    xhist.Fit(func,"NO")

    ym = func.GetMinimum(xmin, xmax)
    xm = func.GetX(ym, xmin, xmax )
    nDat = []
    for (x,d) in dat: nDat.append((x,d-ym))
    del xhist
    xhist = toGraph( var, var, nDat )
#    polString = "[0]*(x-%f)**2+[1]*(x-%f)**3+[2]*(x-%f)**4+[3]*(x-%f)**5+[4]*(x-%f)**6"%(xm,xm,xm,xm,xm) #+[7]*x**9+[8]*x**10+[9]*x**11+[10]*x**12"
    polString = "[0]*(x-%f)**2+[1]*(x-%f)**3+[2]*(x-%f)**4+[3]*(x-%f)**5+[4]*(x-%f)**6"%(xm,xm,xm,xm,xm) #+[7]*x**9+[8]*x**10+[9]*x**11+[10]*x**12"
    del func
    dat = nDat
    func  = ROOT.TF1("func", polString, xmin, xmax )
    xhist.Fit(func,"NO")

    x68min = func.GetX( 0.989, xmin, xm )
    x68max = func.GetX( 0.989, xm, xmax )

    ym2 = func.GetMinimum(xmin, 0)
    xm2 = func.GetX(ym2, xmin, 0 )
    x68pmin = func.GetX( 0.989, xmin, xm2 )
    x68pmax = func.GetX( 0.989, xm2, 0 )

    if args.year == 2016 and args.inclRegion and (args.useChannels and args.useChannels[0]=="mu"):
        ym = func.GetMinimum(0, xmax)
        xm = func.GetX(ym, 0, xmax )
        x68min = func.GetX( 0.989, 0, xm )
        x68max = func.GetX( 0.989, xm, xmax )

        ym2 = func.GetMinimum(xmin, 0)
        xm2 = func.GetX(ym2, xmin, 0 )
        x68pmin = func.GetX( 0.989, xmin, xm2 )
        x68pmax = func.GetX( 0.989, xm2, 0 )


    if args.variables == "ctZI" and (args.year == 2018 or args.year == "RunII") and not args.inclRegion:
        ym2 = func.GetMinimum(0, xmax)
        xm2 = func.GetX(ym2, 0, xmax )
        x68pmin = func.GetX( 0.989, 0, xm2 )
        x68pmax = func.GetX( 0.989, xm2, xmax )
        x68min = func.GetX( 0.989, xmin, xm )
        x68max = func.GetX( 0.989, xm, 0 )

#    x68maxNew = func.GetX( 0.989, x68max+0.005, xmax )
#    ij = 0
#    while x68maxNew != x68max and ij < 10:
#        ij +=1
#        x68max = x68maxNew
#        x68maxNew = func.GetX( 0.989, x68max+0.005, xmax )

#    x68max = x68maxNew

    x95min = func.GetX( 3.84, xmin, xm )
    x95max = func.GetX( 3.84, xm, xmax )

    if (args.year == 2018 or (args.year == "RunII" and args.variables == "ctZ")) and not args.inclRegion and not args.withbkg:
        x95min = func.GetX( 3.84, xmin, xm )
        x95max = func.GetX( 3.84, xm, 0 )

        ym2 = func.GetMinimum(0.01, xmax)
        xm2 = func.GetX(ym2, 0.01, xmax )
        x95pmin = func.GetX( 3.84, 0.01, xm2 )
        x95pmax = func.GetX( 3.84, xm2, xmax )


    xhist.SetLineWidth(0)

    func.SetFillColor(ROOT.kWhite)
    func.SetFillStyle(1001)
    func.SetLineWidth(3)
    func.SetLineColor(ROOT.kBlack)
    func.SetNpx(1000)

    funcExp  = ROOT.TF1("funcExp", polStringExp, xmin, xmax )
    xhistExp.Fit(funcExp,"NO")
    x68minExp = funcExp.GetX( 0.989, xmin, 0 )
    x68maxExp = funcExp.GetX( 0.989, 0, xmax )
    x95minExp = funcExp.GetX( 3.84, xmin, 0 )
    x95maxExp = funcExp.GetX( 3.84, 0, xmax )

    xhistExp.SetLineWidth(0)

    funcExp.SetFillColor(ROOT.kWhite)
    funcExp.SetFillStyle(1001)
    funcExp.SetLineWidth(3)
#    funcExp.SetLineStyle(11)
    funcExp.SetLineColor(ROOT.kGray+1)
    funcExp.SetNpx(1000)


    ROOT.gStyle.SetPadLeftMargin(0.14)
    ROOT.gStyle.SetPadRightMargin(0.1)
    ROOT.gStyle.SetPadTopMargin(0.11)
    ROOT.gStyle.SetPadBottomMargin(0.11)

    # Plot
    cans = ROOT.TCanvas("cans","cans",500,500)

    #if not None in args.zRange:
    xhist.GetYaxis().SetRangeUser( 0, 5.5 )
    xhist.GetXaxis().SetRangeUser( xmin, xmax )
    xhist.GetXaxis().SetLimits(xmin, xmax)


    func95 = ROOT.TF1("func95",polString, x95min,x95max )
    xhist.Fit(func95,"NO")
    func95.SetFillColor(ROOT.kOrange+7)
    func95.SetFillStyle(1001)
    func95.SetLineWidth(0)
    func95.SetNpx(1000)

    if (args.year == 2018 or (args.year == "RunII" and args.variables == "ctZ")) and not args.inclRegion and not args.withbkg:
        func95p = ROOT.TF1("func95p",polString, x95pmin,x95pmax )
        xhist.Fit(func95p,"NO")
        func95p.SetFillColor(ROOT.kOrange+7)
        func95p.SetFillStyle(1001)
        func95p.SetLineWidth(0)
        func95p.SetNpx(1000)


    func68 = ROOT.TF1("func68",polString, x68min,x68max )
    xhist.Fit(func68,"NO")
    func68.SetFillColor(ROOT.kSpring-1)
    func68.SetFillStyle(1001)
    func68.SetLineWidth(0)
    func68.SetNpx(1000)

    func68p = ROOT.TF1("func68p",polString, x68pmin,x68pmax )
    xhist.Fit(func68p,"NO")
    func68p.SetFillColor(ROOT.kSpring-1)
    func68p.SetFillStyle(1001)
    func68p.SetLineWidth(0)
    func68p.SetNpx(1000)

    func.GetXaxis().SetRangeUser( xmin, xmax )
    func68.GetXaxis().SetRangeUser( xmin, xmax )
    func68p.GetXaxis().SetRangeUser( xmin, xmax )
    func95.GetXaxis().SetRangeUser( xmin, xmax )
    if (args.year == 2018 or (args.year == "RunII" and args.variables == "ctZ")) and not args.inclRegion and not args.withbkg:
        func95p.GetXaxis().SetRangeUser( xmin, xmax )

    func.GetYaxis().SetRangeUser( 0, 5 )
    func68.GetYaxis().SetRangeUser( 0, 5 )
    func68p.GetYaxis().SetRangeUser( 0, 5 )
    func95.GetYaxis().SetRangeUser( 0, 5 )


    func95Exp = ROOT.TF1("func95Exp",polStringExp, x95minExp,x95maxExp )
    xhistExp.Fit(func95Exp,"NO")
    func95Exp.SetFillColor(ROOT.kGray+2)
    func95Exp.SetFillStyle(1001)
    func95Exp.SetLineWidth(0)
    func95Exp.SetNpx(1000)

    func68Exp = ROOT.TF1("func68Exp",polStringExp, x68minExp,x68maxExp )
    xhistExp.Fit(func68Exp,"NO")
    func68Exp.SetFillColor(ROOT.kGray+1)
    func68Exp.SetFillStyle(1001)
    func68Exp.SetLineWidth(0)
    func68Exp.SetNpx(1000)

    funcExp.GetXaxis().SetRangeUser( xmin, xmax )
    func68Exp.GetXaxis().SetRangeUser( xmin, xmax )
    func95Exp.GetXaxis().SetRangeUser( xmin, xmax )

    funcExp.GetYaxis().SetRangeUser( 0, 5 )
    func68Exp.GetYaxis().SetRangeUser( 0, 5 )
    func95Exp.GetYaxis().SetRangeUser( 0, 5 )

    xhist.Draw("ALO")
#    func95Exp.Draw("FOSAME")
#    func68Exp.Draw("FOSAME")
    func.Draw("COSAME")
    func95.Draw("FOSAME")
    if (args.year == 2018 or (args.year == "RunII" and args.variables == "ctZ")) and not args.inclRegion and not args.withbkg:
        func95p.Draw("FOSAME")
    func68.Draw("FOSAME")
    if args.variables == "ctZ" and args.year == 2016 and args.inclRegion:
        func68p.Draw("FOSAME")
    if args.year == 2016 and args.inclRegion and (args.useChannels and args.useChannels[0]=="mu"):
        func68p.Draw("FOSAME")
    if args.variables == "ctZI" and (args.year == 2018 or args.year == "RunII") and not args.inclRegion:
        func68p.Draw("FOSAME")
    xhist.Draw("LSAME")
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

    if "%.2f"%x68pmax == "%.2f"%x68min: x68min = x68pmin
#    funcName = "Log-likelihood ratio"
    funcName = ""
    if args.variables == "ctZ" and args.year == 2016 and args.inclRegion and  x68pmin != x68min:
        leg = ROOT.TLegend(0.17,0.7,0.85,0.87)
    elif args.year == 2016 and args.inclRegion and (args.useChannels and args.useChannels[0]=="mu"):
        leg = ROOT.TLegend(0.17,0.7,0.85,0.87)
    elif (args.year == 2018 or args.year == "RunII") and not args.inclRegion:
#        leg = ROOT.TLegend(0.17,0.7,0.85,0.87)
#        if args.variables == "ctZ":
#            leg = ROOT.TLegend(0.23,0.7,0.85,0.889)
#        else:
#            leg = ROOT.TLegend(0.16,0.7,0.85,0.889)
        leg = ROOT.TLegend(0.4,0.67,0.68,0.85)
    else:
        leg = ROOT.TLegend(0.32,0.7,0.8,0.87)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.037)
    leg.AddEntry( func, "Observed" ,"l")
    leg.AddEntry( funcExp, "Expected" ,"l")

    leg.AddEntry( func68, "68%s CL"%("%") ,"f")
    leg.AddEntry( func95, "95%s CL"%("%") ,"f")

#    if args.variables == "ctZ" and args.year == 2016 and args.inclRegion and  x68pmin != x68min:
#        leg.AddEntry( func68, "68%s CL (observed) [%.2f, %.2f], [%.2f, %.2f]"%("%",x68pmin, x68pmax, x68min, x68max), "f")
#    elif args.year == 2016 and args.inclRegion and (args.useChannels and args.useChannels[0]=="mu"):
#        leg.AddEntry( func68, "68%s CL (observed) [%.2f, %.2f], [%.2f, %.2f]"%("%",x68pmin, x68pmax, x68min, x68max), "f")
#    elif args.variables == "ctZI" and (args.year == 2018 or args.year == "RunII") and not args.inclRegion:
#        leg.AddEntry( func68, "68%s CL (observed) [%.2f, %.2f], [%.2f, %.2f]"%("%",x68min, x68max, x68pmin, x68pmax), "f")
#    else:
#        leg.AddEntry( func68, "68%s CL (observed) [%.2f, %.2f]"%("%",x68min, x68max), "f")
#    if (args.year == 2018 or (args.year == "RunII" and args.variables == "ctZ")) and not args.inclRegion and not args.withbkg:
#        leg.AddEntry( func95, "95%s CL (observed) [%.2f, %.2f], [%.2f, %.2f]"%("%",x95min, x95max,x95pmin,x95pmax), "f")
#    else:
#        leg.AddEntry( func95, "95%s CL (observed) [%.2f, %.2f]"%("%",x95min, x95max), "f")
#    leg.AddEntry( func68Exp, "68%s CL (Exp) [%.2f, %.2f]"%("%",x68minExp, x68maxExp), "f")
#    leg.AddEntry( func95Exp, "95%s CL (Exp) [%.2f, %.2f]"%("%",x95minExp, x95maxExp), "f")
#    leg2 = ROOT.TLegend(0.17,0.7,0.85,0.889)
#    leg2.SetBorderSize(0)
#    leg2.Draw()

    leg.Draw()
    
    xTitle = var.replace("c", "c_{").replace("I", "}^{I").replace('p','#phi') + '}'
    xhist.GetXaxis().SetTitle( xTitle + ' [(#Lambda/TeV^{2})]' )

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
#    latex2.DrawLatex(0.15, 0.91, '#bf{CMS} #it{Preliminary} ' + addon),
    latex2.DrawLatex(0.15, 0.91, '#bf{CMS} ' + addon),
    if isinstance(lumi_scale, int):
        latex1.DrawLatex(0.67, 0.91, '#bf{%i fb^{-1} (13 TeV)}' % lumi_scale)
    else:
        latex1.DrawLatex(0.65, 0.91, '#bf{%3.1f fb^{-1} (13 TeV)}' % lumi_scale)

    # Redraw axis, otherwise the filled graphes overlay
    cans.RedrawAxis()

    plotname = "%s%s%s_wExp"%(var, "", "_%s"%args.tag if args.tag != "combined" else "")
    if args.withbkg: plotname += "_wBkg"
    if args.withEFTUnc: plotname += "_wEFTUnc"
    for e in [".png",".pdf",".root"]:
        cans.Print( plot_directory_ + "/%s%s"%(plotname, e) )

    copyIndexPHP( plot_directory_ )

#    for e in [".png",".pdf",".root"]:
#        cans.Print( plot_directory_ + "/%s%s%s"%(var, "_profiled" if profiled else "", e) )

xmin = xPlotLow  if xPlotLow  else -2.49
xmax = xPlotHigh if xPlotHigh else 2.49
plot1D( xNLL, xNLLExp, args.variables, xmin, xmax )

