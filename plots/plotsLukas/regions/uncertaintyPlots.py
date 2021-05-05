#!/usr/bin/env python

""" 
Get cardfile result plots
"""

# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy, math

import numpy as np
# Helpers
from plotHelpers                      import *
import array
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
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv47_v10",                                             help="plot sub-directory")
argParser.add_argument("--preliminary",          action="store_true",                            help="Run expected?")
argParser.add_argument("--expected",             action="store_true",                            help="Run expected?")
argParser.add_argument("--year",                 action="store",      type=str, default="2016",    help="Which year?")
argParser.add_argument("--plotYear",             action="store",                default=None,    help="Which year to plot from combined fits?")
argParser.add_argument("--carddir",              action='store',                default='limits/cardFiles/defaultSetup/observed',      help="which cardfile directory?")
argParser.add_argument("--cardfile",             action='store',                default='',      help="which cardfile?")
argParser.add_argument("--substituteCard",       action='store',                default=None,    help="which cardfile to substitute the plot with?")
argParser.add_argument("--plotRegions",          action='store', nargs="*",     default=None,    help="which regions to plot?")
argParser.add_argument("--plotChannels",         action='store', nargs="*",     default=None,    help="which regions to plot?")
argParser.add_argument("--bkgSubstracted",       action='store_true',           default=False,   help="plot region plot background substracted")
argParser.add_argument("--noData",               action='store_true',           default=False,   help="plot data?")
argParser.add_argument("--plotNuisances",        action='store', nargs="*",     default=None,    help="plot specific nuisances?")
argParser.add_argument("--postFit",              action="store_true",                            help="Apply pulls?")
args = argParser.parse_args()

# logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile = None )
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

args.preliminary = True



from Analysis.Tools.MergingDirDB      import MergingDirDB
from TTGammaEFT.Tools.user    import cache_directory
year = str(args.year)
if args.plotYear: year += "_" + str(args.plotYear)
cache_dir = os.path.join(cache_directory, "unfolding", str(args.year), "bkgSubstracted" if args.bkgSubstracted else "total", "expected" if args.expected else "observed", "postFit" if args.postFit else "preFit")
print cache_dir
dirDB = MergingDirDB(cache_dir)
if not dirDB: raise
addons = []

if args.plotRegions:  addons += args.plotRegions
if args.plotChannels: addons += args.plotChannels

if args.year == "combined" and not args.plotYear:
    years = ["2016","2017","2018"]
elif args.year == "combined" and args.plotYear:
    years = [args.plotYear]
else:
    years = [None]

for i, year in enumerate(years):
    if year: addon = addons + [year]
    else:    addon = addons

    # data histogram
    name = ["bkgSubtracted" if args.bkgSubstracted else "total", args.substituteCard, args.cardfile, "data"]
    print "_".join(name+addon)
    data_tmp = dirDB.get( "_".join(name+addon) )
    # bkg substracted total histogram (signal) with total error
    name = ["bkgSubtracted" if args.bkgSubstracted else "total", args.substituteCard, args.cardfile, "signal" if args.bkgSubstracted else "total"]
    print "_".join(name+addon)
    signal_tmp = dirDB.get( "_".join(name+addon) )
    # bkg substracted total histogram (signal) with stat error
    name = ["bkgSubtracted" if args.bkgSubstracted else "total", args.substituteCard, args.cardfile, "signal_stat" if args.bkgSubstracted else "total_stat"]
    print "_".join(name+addon)
    stat_tmp = dirDB.get( "_".join(name+addon) )
    # experimental uncertainty
    name = ["bkgSubtracted" if args.bkgSubstracted else "total", args.substituteCard, args.cardfile, "experimental_Up"]
    print "_".join(name+addon)
    experimentalUp_tmp = dirDB.get( "_".join(name+addon) )
    name = ["bkgSubtracted" if args.bkgSubstracted else "total", args.substituteCard, args.cardfile, "experimental_Down"]
    print "_".join(name+addon)
    experimentalDown_tmp = dirDB.get( "_".join(name+addon) )
    # model uncertainty
    name = ["bkgSubtracted" if args.bkgSubstracted else "total", args.substituteCard, args.cardfile, "model_Up"]
    print "_".join(name+addon)
    modelUp_tmp = dirDB.get( "_".join(name+addon) )
    name = ["bkgSubtracted" if args.bkgSubstracted else "total", args.substituteCard, args.cardfile, "model_Down"]
    print "_".join(name+addon)
    modelDown_tmp = dirDB.get( "_".join(name+addon) )
    # background uncertainty
    name = ["bkgSubtracted" if args.bkgSubstracted else "total", args.substituteCard, args.cardfile, "background_Up"]
    print "_".join(name+addon)
    backgroundUp_tmp = dirDB.get( "_".join(name+addon) )
    name = ["bkgSubtracted" if args.bkgSubstracted else "total", args.substituteCard, args.cardfile, "background_Down"]
    print "_".join(name+addon)
    backgroundDown_tmp = dirDB.get( "_".join(name+addon) )
    # fakeModelling uncertainty
    name = ["bkgSubtracted" if args.bkgSubstracted else "total", args.substituteCard, args.cardfile, "fakeModelling_Up"]
    print "_".join(name+addon)
    fakeModellingUp_tmp = dirDB.get( "_".join(name+addon) )
    name = ["bkgSubtracted" if args.bkgSubstracted else "total", args.substituteCard, args.cardfile, "fakeModelling_Down"]
    print "_".join(name+addon)
    fakeModellingDown_tmp = dirDB.get( "_".join(name+addon) )

    for h in [experimentalUp_tmp, experimentalDown_tmp, modelUp_tmp, modelDown_tmp, backgroundUp_tmp, backgroundDown_tmp, fakeModellingDown_tmp, fakeModellingUp_tmp]:
        for ib in range(signal_tmp.GetNbinsX()):
            h.SetBinError(ib+1, abs(signal_tmp.GetBinContent(ib+1) - h.GetBinContent(ib+1)))
            h.SetBinContent(ib+1, signal_tmp.GetBinContent(ib+1))

    if i==0:
        data = data_tmp.Clone()
        signal = signal_tmp.Clone()
        stat = stat_tmp.Clone()
        experimentalUp = experimentalUp_tmp.Clone()
        experimentalDown = experimentalDown_tmp.Clone()
        modelUp = modelUp_tmp.Clone()
        modelDown = modelDown_tmp.Clone()
        backgroundUp = backgroundUp_tmp.Clone()
        backgroundDown = backgroundDown_tmp.Clone()
        fakeModellingUp = fakeModellingUp_tmp.Clone()
        fakeModellingDown = fakeModellingDown_tmp.Clone()
    else:
        data.Add(data_tmp)
        signal.Add(signal_tmp)
        stat.Add(stat_tmp)
        experimentalUp.Add(experimentalUp_tmp)
        experimentalDown.Add(experimentalDown_tmp)
        modelUp.Add(modelUp_tmp)
        modelDown.Add(modelDown_tmp)
        backgroundUp.Add(backgroundUp_tmp)
        backgroundDown.Add(backgroundDown_tmp)
        fakeModellingUp.Add(fakeModellingUp_tmp)
        fakeModellingDown.Add(fakeModellingDown_tmp)


for h in [experimentalUp, modelUp, backgroundUp, fakeModellingUp]:
    for ib in range(signal.GetNbinsX()):
        h.SetBinContent(ib+1, signal.GetBinContent(ib+1) + h.GetBinError(ib+1))
        h.SetBinError(ib+1, 0)

for h in [experimentalDown, modelDown, backgroundDown, fakeModellingDown]:
    for ib in range(signal.GetNbinsX()):
        h.SetBinContent(ib+1, signal.GetBinContent(ib+1) - h.GetBinError(ib+1))
        h.SetBinError(ib+1, 0)

if "Pt" in args.substituteCard:       minMax = 0.7 if args.bkgSubstracted else 0.4
elif "AbsEta" in args.substituteCard: minMax = 0.25 if args.bkgSubstracted else 0.15
elif "Eta" in args.substituteCard:    minMax = 0.7 if args.bkgSubstracted else 0.4
elif "Phi" in args.substituteCard:    minMax = 0.7 if args.bkgSubstracted else 0.4
elif "dRJet" in args.substituteCard:  minMax = 0.5 if args.bkgSubstracted else 0.3
elif "dR" in args.substituteCard:     minMax = 0.3 if args.bkgSubstracted else 0.2

#minMax = 0.1
_, boxes = getUncertaintyBoxes( signal, minMax, lineColor=ROOT.kOrange-2, fillColor=ROOT.kOrange-2, hashcode=None )
_, boxesStat = getUncertaintyBoxes( stat, minMax, lineColor=ROOT.kCyan+1, fillColor=ROOT.kCyan+1, hashcode=None )


totalUp = signal.Clone()
totalDown = signal.Clone()
statUp = stat.Clone()
statDown = stat.Clone()
for i in range(signal.GetNbinsX()):
    totalUp.SetBinContent(i+1, signal.GetBinContent(i+1)+signal.GetBinError(i+1))
    totalDown.SetBinContent(i+1, signal.GetBinContent(i+1)-signal.GetBinError(i+1))
    statUp.SetBinContent(i+1, signal.GetBinContent(i+1)+stat.GetBinError(i+1))
    statDown.SetBinContent(i+1, signal.GetBinContent(i+1)-stat.GetBinError(i+1))

scale = signal.Clone()
data.Divide(scale)
signal.Divide(scale)
totalUp.Divide(scale)
totalDown.Divide(scale)
stat.Divide(scale)
statUp.Divide(scale)
statDown.Divide(scale)
experimentalUp.Divide(scale)
experimentalDown.Divide(scale)
modelUp.Divide(scale)
modelDown.Divide(scale)
backgroundUp.Divide(scale)
backgroundDown.Divide(scale)
fakeModellingUp.Divide(scale)
fakeModellingDown.Divide(scale)

data.legendText = "Observed (e+#mu)"
data.style = styles.errorStyle( ROOT.kBlack )

#signal.legendText = "t#bar{t}#gamma SM prediction"
signal.legendText = None #"t#bar{t}#gamma SM prediction"
#signal.style = styles.lineStyle( ROOT.kOrange+7, width=3, errors=False )
signal.style = styles.lineStyle( ROOT.kBlack, width=3, errors=False )

totalUp.legendText = "Total Uncertainty"
totalUp.Scale(0)
#totalUp.style = styles.hashStyle(hashCode=3244)
totalUp.style = styles.fillStyle(ROOT.kOrange-2)


statUp.legendText = "Stat. Uncertainty"
statUp.Scale(0)
statUp.style = styles.fillStyle(ROOT.kCyan+1)

#experimentalUp.legendText = "Int. Luminosity (#pm1#sigma)"
experimentalUp.legendText = "Exp. Systematics (#pm1#sigma)"
experimentalDown.legendText = None
experimentalUp.style = styles.lineStyle( ROOT.kRed+1, width=3, dashed=True, errors=False )
experimentalDown.style = styles.lineStyle( ROOT.kRed+1, width=3, dashed=True, errors=False )

backgroundUp.legendText = "MisID-e/W#gamma/Z#gamma Modelling (#pm1#sigma)"
backgroundDown.legendText = None
backgroundUp.style = styles.lineStyle( ROOT.kGray+1, width=3, dashed=True, errors=False )
backgroundDown.style = styles.lineStyle( ROOT.kGray+1, width=3, dashed=True, errors=False )

fakeModellingUp.legendText = "had.#gamma/fake/QCD/Other Modelling (#pm1#sigma)"
fakeModellingDown.legendText = None
fakeModellingUp.style = styles.lineStyle( ROOT.kGreen-2, width=3, dashed=True, errors=False )
fakeModellingDown.style = styles.lineStyle( ROOT.kGreen-2, width=3, dashed=True, errors=False )

modelUp.legendText = "t#bar{t}#gamma Modelling (#pm1#sigma)"
modelDown.legendText = None
modelUp.style = styles.lineStyle( ROOT.kBlue+1, width=3, dashed=True, errors=False )
modelDown.style = styles.lineStyle( ROOT.kBlue+1, width=3, dashed=True, errors=False )


if args.year == "2016":   lumi_scale = 35.92
elif args.year == "2017": lumi_scale = 41.53
elif args.year == "2018": lumi_scale = 59.74
elif args.year == "combined": lumi_scale = 35.92 + 41.53 + 59.74

if "Pt" in args.substituteCard:       xLabel = "p_{T}(#gamma) [GeV]"
elif "AbsEta" in args.substituteCard: xLabel = "|#eta(#gamma)|"
elif "Eta" in args.substituteCard:    xLabel = "#eta(#gamma)"
elif "Phi" in args.substituteCard:    xLabel = "#Delta#phi(#gamma,l)"
elif "dRJet" in args.substituteCard:  xLabel = "min. #DeltaR(#gamma,jet)"
elif "dR" in args.substituteCard:     xLabel = "#DeltaR(#gamma,l)"

Plot.setDefaults()
if args.noData:
#    histos = [[totalUp],[statUp],[experimentalUp],[experimentalDown],[modelUp],[modelDown],[backgroundUp],[backgroundDown],[fakeModellingUp],[fakeModellingDown],[signal]]
    histos = [[totalUp],[statUp],[experimentalUp],[experimentalDown],[modelUp],[modelDown],[signal]]
    addon = "_noData"
    nameAddon = "_%s"%args.plotYear if args.plotYear else ""
else:
#    histos = [[experimentalUp],[experimentalDown],[totalUp],[modelUp],[modelDown],[statUp],[backgroundUp],[backgroundDown],[fakeModellingUp],[fakeModellingDown],[data],[signal]]
    histos = [[experimentalUp],[experimentalDown],[totalUp],[modelUp],[modelDown],[statUp],[data],[signal]]
    addon = ""
    nameAddon = "_%s"%args.plotYear if args.plotYear else ""
plots = Plot.fromHisto( args.substituteCard+nameAddon, histos, texX = xLabel, texY = "Rel. Uncertainty" )

plot_directory_ = os.path.join( plot_directory, "uncertainty", str(args.year), args.plot_directory, "bkgSubstracted%s"%addon if args.bkgSubstracted else "total%s"%addon, "expected" if args.expected else "observed", "postFit" if args.postFit else "preFit" )

# Text on the plots
def drawObjects( lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    line = (0.68, 0.95, "%3.1f fb^{-1} (13 TeV)" % lumi_scale)
    lines = [
      (0.15, 0.95, "CMS #bf{#it{Preliminary}}"),
      line
    ]
    return [tex.DrawLatex(*l) for l in lines]


if "Pt" in args.substituteCard:       yRange = (0.8,1.3)
elif "AbsEta" in args.substituteCard: yRange = (0.93,1.1)
elif "Eta" in args.substituteCard:    yRange = (0.93,1.1)
elif "Phi" in args.substituteCard:    yRange = (0.93,1.1)
elif "dRJet" in args.substituteCard:  yRange = (0.7,1.45)
elif "dR" in args.substituteCard:     yRange = (0.93,1.1)


plotting.draw( plots,
               plot_directory = plot_directory_,
               logX = False, logY = False, sorting = False,
               yRange = yRange,
#               yRange = (1-minMax, 1.3+minMax if args.bkgSubstracted else 1.1+minMax),
               drawObjects = drawObjects( lumi_scale ) + boxes + boxesStat,
               legend = [(0.2,0.7,0.9,0.9),2],
               copyIndexPHP = True,
               redrawHistos = True,
             )
