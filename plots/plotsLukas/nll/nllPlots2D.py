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
argParser.add_argument( "--year",               action="store",      default="2016",   type=str,                              help="Which year?" )
argParser.add_argument('--zRange',              action='store',      default=[0, 20],  type=float, nargs=2,                                  help="argument parameters")
argParser.add_argument('--xyRange',            action='store',      default=[None, None, None, None],  type=float, nargs=4,                          help="argument parameters")
argParser.add_argument('--plotData',            action='store_true',                                                                                  help='Plot data points?')
argParser.add_argument('--addDYSF',             action='store_true',                                                                                  help='Plot data points taken with --addDYSF?')
argParser.add_argument( "--addMisIDSF",         action="store_true",                                                        help="add default misID scale factor" )
argParser.add_argument('--tag',                 action='store',      default="combined",        type=str,                                             help='tag for unc studies')
argParser.add_argument('--variables' ,         action='store',      default = ['ctZ', 'ctZI'], type=str, nargs=2,                                    help="argument plotting variables")
argParser.add_argument( "--expected",           action="store_true",                                                        help="Use sum of backgrounds instead of data." )
argParser.add_argument( "--inclRegion",         action="store_true",                                                        help="use inclusive photon pt region" )
argParser.add_argument( "--useRegions",         action="store",      nargs='*',       type=str, choices=allRegions.keys(),  help="Which regions to use?" )
argParser.add_argument( "--useChannels",        action="store",      nargs='*', default=None,   type=str, choices=["e", "mu", "all", "comb"], help="Which lepton channels to use?" )
argParser.add_argument('--contours',           action='store_true',                                                                                  help='draw 1sigma and 2sigma contour line?')
argParser.add_argument('--smooth',             action='store_true',                                                                                  help='smooth histogram?')
argParser.add_argument('--withbkg',             action='store_true',                                                                                  help='with bkg?')
argParser.add_argument('--withEFTUnc',             action='store_true',                                                        help="add EFT uncertainty?")
argParser.add_argument('--binMultiplier',      action='store',      default=3,                 type=int,                                             help='bin multiplication factor')
args = argParser.parse_args()

if args.year != "RunII": args.year = int(args.year)

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None)

# load and define the EFT sample
from TTGammaEFT.Samples.genTuples_TTGamma_EFT_postProcessed  import *
eftSample = TTG_2WC_ref

if not args.xyRange[0]: args.xyRange[0] = -0.6
if not args.xyRange[1]: args.xyRange[1] = 0.6
if not args.xyRange[2]: args.xyRange[2] = -0.62
if not args.xyRange[3]: args.xyRange[3] = 0.7

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

baseDir       = os.path.join( cache_directory, "analysis",  str(args.year) if args.year != "RunII" else "COMBINED", "limits", "withbkg" if args.withbkg else "withoutbkg" )
if args.withEFTUnc: baseDir = os.path.join( baseDir, "withEFTUnc" )
cacheFileName = os.path.join( baseDir, "calculatednll" )
nllCache      = MergingDirDB( cacheFileName )
print cacheFileName

directory = os.path.join( plot_directory, "nllPlotsApp", str(args.year), "_".join( regionNames ))
addon = "expected" if args.expected else "observed"
plot_directory_ = os.path.join( directory, addon )

if not os.path.isdir( plot_directory_ ):
    try: os.makedirs( plot_directory_ )
    except: pass

if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74
elif args.year == "RunII": lumi_scale = int(35.92 + 41.53 + 59.74)

#binning range
xRange = eftParameterRange[args.variables[0]]
yRange = eftParameterRange[args.variables[1]]

xRange = [ el for el in xRange if abs(el) <= 0.6 ]
yRange = [ el for el in yRange if abs(el) <= 0.6 ]
xRange += [ 0.7 ]
yRange += [ 0.7 ]


#xRange       = np.linspace( -1.0, 1.0, 30, endpoint=False)
#halfstepsize = 0.5 * ( xRange[1] - xRange[0] )
#xRange       = [ round(el + halfstepsize, 3) for el in xRange ] + [0]
#xRange.sort()
#yRange = xRange


def getNllData( varx, vary ):
    dict = {"ctZI":0, "ctZ":0}
    dict[args.variables[0]] = varx
    dict[args.variables[1]] = vary
    EFTparams = ["ctZ", str(dict["ctZ"]), "ctZI", str(dict["ctZI"])]
    configlist = regionNames + EFTparams
    configlist.append("incl" if args.inclRegion else "diff")
    configlist.append("expected" if args.expected else "observed")
    sConfig = "_".join(configlist)

    if not nllCache.contains(sConfig):
        print sConfig
        return None  

    nll = nllCache.get(sConfig)

    if nll["nll"] == 0:
        print sConfig
        print nll
        return None

#    print nll

    nll = nll["nll"] + nll["nll0"]

    return float(nll)  


logger.info("Loading cache data" )
points = [ (0,0) ] #SM point
points += [ (0, varY) for varY in yRange] #1D plots
points += [ (varX, 0) for varX in xRange] #1D plots
points += [ (varX, varY) for varY in yRange for varX in xRange] #2D plots

nllData  = [ (varx, vary, getNllData( varx, vary )) for (varx, vary) in points ]
nllData  = [ x for x in nllData if x[2] ]

if args.expected:
    sm_nll   = getNllData(0,0)
    bfx, bfy = 0,0
else:
#    allResults = sorted([y for y in nllData if abs(y[0])<0.5 and abs(y[1])<0.5], key=lambda x:-x[2])
    allResults = sorted([y for y in nllData ], key=lambda x:x[2])
    sm_nll   = allResults[0][2]
    bfx, bfy = allResults[0][0], allResults[0][1]
    print allResults[0]

#nllData  = [ (x, y, -2*(nll - sm_nll) if -2*(nll - sm_nll) < 20 and -2*(nll - sm_nll) > 0 else 20) for x, y, nll in nllData ]
nllData  = [ (x, y, 2*(nll - sm_nll) ) for x, y, nll in nllData ]
nllData  += [ (x, -0.7, 40) for x in xRange ]
nllData  += [ (x, 0.7, 40) for x in xRange ]
nllData  += [ (-0.7, x, 40) for x in yRange ]
nllData  += [ (0.7, x, 40) for x in yRange ]

#if args.year == "RunII":
#    nllData  += [ (0.6, x, 30) for x in xRange ]
#    nllData  += [ (-0.6, x, 30) for x in xRange ]
#    nllData  += [ (x, 0.6, 30) for x in xRange ]
#    nllData  += [ (x, -0.6, 30) for x in xRange ]

if args.expected:
    nllData  = [ x for x in nllData if x[2] > 0 ]
#for x in nllData:
#    if abs(x[0]) < 0.35: print x
#sys.exit()


tmp = nllData
tmp.sort( key = lambda res: (res[0], res[1]) )


def toGraph2D( name, title, data ):
    result = ROOT.TGraph2D( len(data) )
    debug = ROOT.TGraph()
    result.SetName( name )
    result.SetTitle( "" )
    for i, datapoint in enumerate(data):
        x, y, val = datapoint
        result.SetPoint(i, x, y, val)
        debug.SetPoint(i, x, y)
    c = ROOT.TCanvas()
    result.Draw()
    debug.Draw()
    del c
    return result, debug

#get TGraph2D from results list
title = "TTG_%s_%s"%(args.variables[0], args.variables[1])
a, debug = toGraph2D( title, title, nllData )
xbins = len(xRange)
ybins = len(yRange)
nxbins   = max( 1, min( 500, xbins*args.binMultiplier ) )
nybins   = max( 1, min( 500, ybins*args.binMultiplier ) )

#re-bin
hist = a.GetHistogram().Clone()
a.SetNpx( nxbins )
a.SetNpy( nybins )
hist = a.GetHistogram().Clone()

#smoothing
if args.smooth: hist.Smooth()

cans = ROOT.TCanvas("can_%s"%title,"",500,500)

contours = [2.28, 5.99]# (68%, 95%) for 2D
if args.contours:
    histsForCont = hist.Clone()
    c_contlist = ((ctypes.c_double)*(len(contours)))(*contours)
    histsForCont.SetContour(len(c_contlist),c_contlist)
    histsForCont.Draw("contzlist")
    cans.Update()
    conts = ROOT.gROOT.GetListOfSpecials().FindObject("contours")
    cont_p1 = conts.At(0).Clone()
    cont_p2 = conts.At(1).Clone()

pads = ROOT.TPad("pad_%s"%title,"",0.,0.,1.,1.)
pads.SetRightMargin(0.20)
pads.SetLeftMargin(0.14)
pads.SetTopMargin(0.11)
pads.Draw()
pads.cd()

hist.Draw("colz")

#draw contour lines
if args.contours:
    for conts in [cont_p2]:
        for cont in conts:
            cont.SetLineColor(ROOT.kOrange+7)
            cont.SetLineWidth(3)
#            cont.SetLineStyle(7)
            cont.Draw("same")
    for conts in [cont_p1]:
        for cont in conts:
            cont.SetLineColor(ROOT.kSpring-1)
            cont.SetLineWidth(3)
#            cont.SetLineStyle(7)
            cont.Draw("same")


hist.GetZaxis().SetTitle("-2 #Delta ln L")

if not None in args.zRange:
    hist.GetZaxis().SetRangeUser( args.zRange[0], args.zRange[1] )
if not None in args.xyRange[:2]:
    hist.GetXaxis().SetRangeUser( args.xyRange[0], args.xyRange[1] )
#    hist.GetXaxis().SetLimits( args.xyRange[0], args.xyRange[1] )
if not None in args.xyRange[2:]:
    hist.GetYaxis().SetRangeUser( args.xyRange[2], args.xyRange[3] )
#    hist.GetYaxis().SetLimits( args.xyRange[2], args.xyRange[3] )

xTitle = args.variables[0].replace("c", "C_{").replace("I", "}^{[Im]").replace('p','#phi') + '}'
yTitle = args.variables[1].replace("c", "C_{").replace("I", "}^{[Im]").replace('p','#phi') + '}'
hist.GetXaxis().SetTitle( xTitle + ' [(#Lambda/TeV)^{2}]' )
hist.GetYaxis().SetTitle( yTitle + ' [(#Lambda/TeV)^{2}]' )

hist.GetXaxis().SetTitleFont(42)
hist.GetYaxis().SetTitleFont(42)
hist.GetZaxis().SetTitleFont(42)
hist.GetXaxis().SetLabelFont(42)
hist.GetYaxis().SetLabelFont(42)
hist.GetZaxis().SetLabelFont(42)

#hist.GetXaxis().SetTitleOffset(1.05)
hist.GetYaxis().SetTitleOffset(1.45)

hist.GetXaxis().SetTitleSize(0.042)
hist.GetYaxis().SetTitleSize(0.042)
hist.GetZaxis().SetTitleSize(0.042)
hist.GetXaxis().SetLabelSize(0.04)
hist.GetYaxis().SetLabelSize(0.04)
hist.GetZaxis().SetLabelSize(0.04)

SMpoint = ROOT.TGraph(1)
SMpoint.SetName("SMpoint")
BFpoint = ROOT.TGraph(1)
BFpoint.SetName("BFpoint")

SMpoint.SetPoint(0, 0, 0)
BFpoint.SetPoint(0, bfx, bfy)

SMpoint.SetMarkerStyle(20)
SMpoint.SetMarkerSize(2)
SMpoint.SetMarkerColor(ROOT.kOrange+1)
BFpoint.SetMarkerStyle(29)
BFpoint.SetMarkerSize(3)
BFpoint.SetMarkerColor(ROOT.kCyan-3)
#BFpoint.SetMarkerColor(ROOT.kGreen-3)

SMpoint.Draw("p same")
BFpoint.Draw("p same")

cont_p2.At(0).SetLineColor(ROOT.kOrange+7)
cont_p2.At(0).SetLineWidth(3)
cont_p1.At(0).SetLineColor(ROOT.kSpring-1)
cont_p1.At(0).SetLineWidth(3)

leg = ROOT.TLegend(0.15,0.75,0.87,0.87)
if args.contours:
    leg.SetNColumns(2)
leg.SetBorderSize(0)
leg.SetTextSize(0.03)
leg.SetFillStyle(0)
leg.AddEntry( SMpoint, "Standard Model","p")
if args.contours:
#    leg.AddEntry( ROOT.TObject(), " ","")
    leg.AddEntry( cont_p1.At(0), "68%s CL"%"%", "l")
leg.AddEntry( BFpoint, "Best Fit","p")
if args.contours:
#    leg.AddEntry( ROOT.TObject(), " ","")
    leg.AddEntry( cont_p2.At(0), "95%s CL"%"%", "l")
leg.Draw()


latex1 = ROOT.TLatex()
latex1.SetNDC()
latex1.SetTextSize(0.035)
latex1.SetTextFont(42)
latex1.SetTextAlign(11)

if args.expected:
    latex1.DrawLatex(0.15, 0.91, '#bf{CMS} #it{Simulation Preliminary}'),
else:
    latex1.DrawLatex(0.15, 0.91, '#bf{CMS} #it{Preliminary}'),
if isinstance(lumi_scale, int):
    latex1.DrawLatex(0.62, 0.91, '#bf{%i fb{}^{-1} (13 TeV)}' % lumi_scale)
else:
    latex1.DrawLatex(0.60, 0.91, '#bf{%3.1f fb{}^{-1} (13 TeV)}' % lumi_scale)

latex2 = ROOT.TLatex()
latex2.SetNDC()
latex2.SetTextSize(0.04)
latex2.SetTextFont(42)
latex2.SetTextAlign(11)

# Redraw axis, otherwise the filled graphes overlay
pads.RedrawAxis()
l = ROOT.TLine()
#l.DrawLine(cans.GetUxmin(), cans.GetUymax(), cans.GetUxmax(), cans.GetUymax());
#l.DrawLine(cans.GetUxmax(), cans.GetUymin(), cans.GetUxmax(), cans.GetUymax());
l.DrawLine(args.xyRange[0], args.xyRange[3], args.xyRange[1], args.xyRange[3]);
l.DrawLine(args.xyRange[1], args.xyRange[2], args.xyRange[1], args.xyRange[3]);

plotname = "_".join(args.variables)
if args.withbkg: plotname += "_wBkg"
if args.withEFTUnc: plotname += "_wEFTUnc"
for e in [".png",".pdf",".root"]:
    cans.Print( plot_directory_ + "/%s%s"%(plotname, e) )

copyIndexPHP( plot_directory_ )

