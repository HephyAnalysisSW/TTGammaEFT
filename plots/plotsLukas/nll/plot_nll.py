''' Plot script WC parameter LogLikelihood
'''

# Standard imports 
import sys, os, pickle, copy, ROOT
import ctypes
import numpy as np

# Multiprocessing
from multiprocessing import Pool

# RootTools
from RootTools.core.standard   import *

# turn off graphics
ROOT.gROOT.SetBatch( True )

# TTGammaEFT
from TTGammaEFT.Tools.user              import plot_directory, cache_directory
from TTGammaEFT.Tools.cutInterpreter    import cutInterpreter
from TTGammaEFT.Tools.genCutInterpreter import cutInterpreter as genCutInterpreter

# get the reweighting function
from Analysis.Tools.WeightInfo          import WeightInfo
from Analysis.Tools.metFilters          import getFilterCut

from TTGammaEFT.Tools.Cache             import Cache

# Default Parameter
loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                                help="Log level for logging")
argParser.add_argument('--genSelection1l',     action='store',      default='dilepOS-pTG20-nPhoton1p-offZSFllg-offZSFll-mll40-nJet2p-nBTag1p')
argParser.add_argument('--genSelection2l',     action='store',      default='dilepOS-pTG20-nPhoton1p-offZSFllg-offZSFll-mll40-nJet2p-nBTag1p')
argParser.add_argument('--selection1l',        action='store',      default='nLepTight1-nLepVeto1-nJet4p-nBTag1p-pTG20-nPhoton1p')
argParser.add_argument('--selection2l',        action='store',      default='dilepOS-nLepVeto2-pTG20-nPhoton1p-offZSFllg-offZSFll-mll40-nJet2p-nBTag1p')
argParser.add_argument('--variables' ,         action='store',      default = ['ctZ', 'ctZI'], type=str, nargs=2,                                    help="argument plotting variables")
argParser.add_argument('--small',              action='store_true',                                                                                  help='Run only on a small subset of the data?', )
argParser.add_argument('--years',              action='store',      default=[ 2016, 2017 ], type=int, choices=[2016, 2017, 2018], nargs="*",         help="Which years to combine?")
argParser.add_argument('--selections',         action='store',      default=[ "1l", "2l" ], type=str, choices=["1l", "2l"], nargs="*",               help="Which selections to combine?")
argParser.add_argument('--binning',            action='store',      default=[50, -1, 1, 50, -1, 1 ], type=float, nargs=6,                            help="argument parameters")
argParser.add_argument('--contours',           action='store_true',                                                                                  help='draw 1sigma and 2sigma contour line?')
argParser.add_argument('--smooth',             action='store_true',                                                                                  help='smooth histogram?')
argParser.add_argument('--zRange',             action='store',      default=[None, None],      type=float, nargs=2,                                  help="argument parameters")
argParser.add_argument('--xyRange',            action='store',      default=[None, None, None, None],  type=float, nargs=4,                          help="argument parameters")
argParser.add_argument('--binMultiplier',      action='store',      default=3,                 type=int,                                             help='bin multiplication factor')
argParser.add_argument('--skipMissingPoints',  action='store_true',                                                                                  help='Set missing NLL points to 999?')
argParser.add_argument('--inclusive',          action='store_true',                                                                                  help='run inclusive regions', )
argParser.add_argument('--tag',                action='store',      default="combined",        type=str,                                             help='bin multiplication factor')
args = argParser.parse_args()

args = argParser.parse_args()

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None)


tableName = "nllcache"
cache_directory += "nll/"
dbFile = "NLLcache"
if   "1l" in args.selections and len(args.selections) == 1: dbFile += "_semilep"
elif "2l" in args.selections and len(args.selections) == 1: dbFile += "_dilep"
elif len(args.selections) > 1:                              dbFile += "_both"
if len(args.years) > 1:                                     dbFile += "_comb"
if args.inclusive:                                          dbFile += "_incl"
if args.tag != "combined":                                  dbFile += "_%s"%args.tag
dbFile += ".sql"

dbPath = cache_directory + dbFile

nllCache  = Cache( dbPath, tableName, ["cardname", "year", "WC1_name", "WC1_val", "WC2_name", "WC2_val", "nll_prefit", "nll_postfit" ] )
if nllCache is None: raise

# Gen Samples
from TTGammaEFT.Samples.genTuples_TTGamma_postProcessed                    import *
#signalSample = TTG_SingleLeptFromT_1L_test_EFT
genSignalSample = {}
genSignalSample["1l"] = TTG_DiLept_1L_EFT
genSignalSample["2l"] = TTG_DiLept_1L_EFT

selection = {}
selection["1l"] = args.selection1l
selection["2l"] = args.selection2l

genSelection = {}
genSelection["1l"] = args.genSelection1l
genSelection["2l"] = args.genSelection2l

cardname  = [ genSignalSample[sel].name for sel in args.selections ]
cardname += map( str, args.years )
cardname += args.selections
cardname += [ args.variables[0], "var1", args.variables[1], "var2" ]
cardname += [ selection[sel] for sel in args.selections ]
cardname += [ 'small' if args.small else 'full' ]
if args.inclusive: cardname += [ "incl" ]
if args.tag != "combined": cardname += [ args.tag ]
cardname  = '_'.join( cardname )

lumi = {}
lumi[2016] = 35.92
lumi[2017] = 41.53
lumi[2018] = 59.74
lumi_scale = sum( [ lumi[year] for year in args.years ])

def getNllData( var1, var2 ):
    card = cardname.replace("var1", str(var1)).replace("var2", str(var2))

    res  = {'cardname':card, "year":"combined", "WC1_name":args.variables[0], "WC1_val":var1, "WC2_name":args.variables[1], "WC2_val":var2}
    nCacheFiles = nllCache.contains( res )

    if nCacheFiles:
        cachedDict = nllCache.getDicts( res )[0]
        nll = cachedDict["nll_prefit"]
    else: 
        logger.info("Data for %s=%s and %s=%s not in cache!"%( args.variables[0], str(var1), args.variables[1], str(var2) ) )
        if args.skipMissingPoints: nll = 999
        else: sys.exit(1)
    return float(nll)

#binning range
xbins, xlow, xhigh = args.binning[:3]
xbins = int(xbins)
ybins, ylow, yhigh = args.binning[3:]
ybins = int(ybins)

if xbins > 1:
    xRange       = np.linspace( xlow, xhigh, xbins, endpoint=False)
    halfstepsize = 0.5 * ( xRange[1] - xRange[0] )
    xRange       = [ round(el + halfstepsize, 3) for el in xRange ]
else:
    xRange = [ 0.5 * ( xlow + xhigh ) ]

if ybins > 1:
    yRange = np.linspace( ylow, yhigh, ybins, endpoint=False)
    halfstepsize = 0.5 * ( yRange[1] - yRange[0] )
    yRange = [ round(el + halfstepsize, 3) for el in yRange ]
else:
    yRange = [ 0.5 * ( ylow + yhigh ) ]

logger.info("Loading cache data" )
points2D = [ (0, 0) ] #SM point
points2D += [ (0, varY) for varY in yRange] #1D plots
points2D += [ (varX, 0) for varX in xRange] #1D plots
points2D += [ (varX, varY) for varY in yRange for varX in xRange] #2D plots

nllData  = [ (var1, var2, getNllData( var1, var2 )) for var1, var2 in points2D ]
sm_nll   = filter( lambda (x, y, nll): x==0 and y==0, nllData )[0][2]
nllData  = [ (x, y, 2*(nll - sm_nll)) for x, y, nll in nllData ]

# Remove white spots in plots
nllData  = [ (x, y, nll) if nll > 1e-5 else (x, y, 1e-5) for x, y, nll in nllData ]

def toGraph2D( name, title, data ):
    result = ROOT.TGraph2D( len(data) )
    debug = ROOT.TGraph()
    result.SetName( name )
    result.SetTitle( title )
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
if not None in args.zRange[2:]:
    hist.GetYaxis().SetRangeUser( args.xyRange[2], args.xyRange[3] )

xTitle = args.variables[0].replace("c", "C_{").replace("I", "}^{[Im]").replace('p','#phi') + '}'
yTitle = args.variables[1].replace("c", "C_{").replace("I", "}^{[Im]").replace('p','#phi') + '}'
hist.GetXaxis().SetTitle( xTitle + ' (#Lambda/TeV)^{2}' )
hist.GetYaxis().SetTitle( yTitle + ' (#Lambda/TeV)^{2}' )

hist.GetXaxis().SetTitleFont(42)
hist.GetYaxis().SetTitleFont(42)
hist.GetZaxis().SetTitleFont(42)
hist.GetXaxis().SetLabelFont(42)
hist.GetYaxis().SetLabelFont(42)
hist.GetZaxis().SetLabelFont(42)

hist.GetXaxis().SetTitleOffset(1.15)
hist.GetYaxis().SetTitleOffset(1.25)

hist.GetXaxis().SetTitleSize(0.045)
hist.GetYaxis().SetTitleSize(0.045)
hist.GetZaxis().SetTitleSize(0.042)
hist.GetXaxis().SetLabelSize(0.04)
hist.GetYaxis().SetLabelSize(0.04)
hist.GetZaxis().SetLabelSize(0.04)

latex1 = ROOT.TLatex()
latex1.SetNDC()
latex1.SetTextSize(0.035)
latex1.SetTextFont(42)
latex1.SetTextAlign(11)

addon = "(%s)"%("+".join(args.selections))
latex1.DrawLatex(0.12, 0.92, '#bf{CMS} #it{Simulation Preliminary} ' + addon),
latex1.DrawLatex(0.63, 0.92, '#bf{%3.1f fb{}^{-1} (13 TeV)}' % lumi_scale)

latex2 = ROOT.TLatex()
latex2.SetNDC()
latex2.SetTextSize(0.04)
latex2.SetTextFont(42)
latex2.SetTextAlign(11)

y   = str(args.years[0]) if len(args.years)==1 else "combined"
sel = selection[args.selections[0]] if len(args.selections)==1 else "combined"
plot_directory_ = os.path.join( plot_directory, "NLLPlots%s"%("Incl" if args.inclusive else ""), y, sel, "_".join(args.variables) )

if not os.path.isdir( plot_directory_ ):
    try: os.makedirs( plot_directory_ )
    except: pass

plotname = "%s%s"%("_".join(args.variables), "_%s"%args.tag if args.tag != "combined" else "")
for e in [".png",".pdf",".root"]:
    cans.Print( plot_directory_ + "/%s%s"%(plotname, e) )

