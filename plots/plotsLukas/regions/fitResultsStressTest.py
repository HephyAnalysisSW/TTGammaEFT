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
argParser.add_argument("--plotRegions",          action='store', nargs="*",     default=None,    help="which regions to plot?")
argParser.add_argument("--plotChannels",         action='store', nargs="*",     default=None,    help="which regions to plot?")
argParser.add_argument("--plotYear",             action="store",                default=None,    help="Which year to plot from combined fits?")
argParser.add_argument("--postFit",              action="store_true",                            help="Apply pulls?")
argParser.add_argument("--preliminary",          action="store_true",                            help="Run expected?")
argParser.add_argument("--year",                 action="store",      type=str, default="2016",    help="Which year?")
args = argParser.parse_args()

# logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile = None )
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

args.year = 2016
lumi_scale = 35.92

plotDirectory = "/mnt/hephy/cms/lukas.lechner/www/TTGammaEFT/fitEFTStressTest/2016/v1/"

# replace the combineResults object by the substituted card object
cardFile      = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/2016/limits/cardFiles/defaultSetup/expected/SR3PtUnfoldEFT_SR4pPtUnfoldEFT_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_splitScale.txt"
Results = CombineResults( cardFile=cardFile, plotDirectory=plotDirectory, year=args.year, bkgOnly=False, isSearch=False )

bfcardFile    = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/2016/limits/cardFiles/defaultSetup/expected/SR3PtUnfoldEFT_SR4pPtUnfoldEFT_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_splitScale_ST0001.txt"
Results01 = CombineResults( cardFile=bfcardFile, plotDirectory=plotDirectory, year=args.year, bkgOnly=False, isSearch=False )

cardFilem045    = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/2016/limits/cardFiles/defaultSetup/expected/SR3PtUnfoldEFT_SR4pPtUnfoldEFT_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_splitScale_ST0002.txt"
Results02 = CombineResults( cardFile=cardFilem045, plotDirectory=plotDirectory, year=args.year, bkgOnly=False, isSearch=False )

cardFileI045    = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/2016/limits/cardFiles/defaultSetup/expected/SR3PtUnfoldEFT_SR4pPtUnfoldEFT_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_splitScale_ST0004.txt"
Results04 = CombineResults( cardFile=cardFileI045, plotDirectory=plotDirectory, year=args.year, bkgOnly=False, isSearch=False )


def replaceHistoBinning( hists ):
        subCard = "SR3PtUnfoldEFT"
        reg = allRegions[subCard]["regions"]
        thresh = [ r.vals.values()[0][0] for r in reg ]
        bins, min, max = len(reg), reg[0].vals.values()[0][0], reg[-1].vals.values()[0][1]
        max = thresh[-1] + 2*(thresh[-1] - thresh[-2])
        thresh += [max]
        print thresh

        for h_key, h in hists.iteritems():
            h_sub = ROOT.TH1F(h.GetName(), h.GetName(), bins, array.array('d', thresh) )
            for i in range(h_sub.GetNbinsX()):
                h_sub.SetBinContent( i+1, h.GetBinContent(i+1))
                h_sub.SetBinError( i+1, h.GetBinError(i+1))
            hists[h_key] = h_sub.Clone(h_key)
            del h_sub
        return hists

if   args.year == 2016 or (args.plotYear and args.plotYear == "2016"): lumi_scale = 35.92
elif args.year == 2017 or (args.plotYear and args.plotYear == "2017"): lumi_scale = 41.53
elif args.year == 2018 or (args.plotYear and args.plotYear == "2018"): lumi_scale = 59.74
elif args.year == "2016": lumi_scale = int(35.92 + 41.53 + 59.74)

# Text on the plots
def drawLObjects():
    global lumi_scale
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right

    tex2 = ROOT.TLatex()
    tex2.SetNDC()
    tex2.SetTextSize(0.055)
    tex2.SetTextAlign(11) # align right

    line = (0.69, 0.95, "%s fb^{-1} (13 TeV)"%str(lumi_scale))
    line2 = (0.15, 0.95, "CMS")

    return [tex2.DrawLatex(*line2), tex.DrawLatex(*line)]

def formatLabel( label ):
    reg = label.split(" ")[3]
    reg = reg.replace("3e","3")
    reg = reg.replace("4pe","4p")
    reg = reg.replace("3mu","3")
    reg = reg.replace("4pmu","4p")
    reg = reg.replace("All","")
    reg = reg.replace("PtUnfold","")
    reg = reg.replace("dRUnfold","")
    reg = reg.replace("AbsEtaUnfold","")
    reg = reg.replace("M3","")
    if not "mLtight0Gamma" in label.split(" ")[2]:
        reg = reg.replace("VG","ZG+WG")
    elif "mLtight0Gamma0" in label.split(" ")[2]:
        reg = reg.replace("VG","ZG")
    else:
        reg = reg.replace("VG","WG")

    reg = reg.replace("WG","HM")
    reg = reg.replace("ZG","LM")

    ch = label.split(" ")[1]
    ch = ch.replace("all","e+mu")
    ch = ch.replace("mu","#mu")
    ch = ch.replace("tight","")

    return reg + ", " + ch

labelFormater = formatLabel
labels = [ ( i, label ) for i, label in enumerate(Results.getBinLabels( labelFormater=lambda x:x.split(" "))[Results.channels[0]])]
if args.plotRegions:
    labels = filter( lambda (i,(year, ch, lab, reg)): reg in args.plotRegions, labels )
if args.plotChannels: labels = filter( lambda (i,(year, ch, lab, reg)): ch in args.plotChannels, labels )

# get list of labels
crName    = [ cr for i, (year, lep, reg, cr) in labels ]
plotBins  = [ i  for i, (year, lep, reg, cr) in labels ]
crLabel   = map( lambda (i,(year, ch, lab, reg)): ", ".join( [ reg, ch.replace("mu","#mu").replace("tight","") ] ), labels )
tmpLabels = map( lambda (i,(year, ch, lab, reg)): lab, labels )
ptLabels  = map( lambda (i,(year, ch, lab, reg)): convLabel(lab), labels )

for key, val in enumerate(crLabel):
    if "mLtight0Gamma" in tmpLabels[key]:
        if "mLtight0Gamma0" in tmpLabels[key]:
            crLabel[key] = val.replace("VG","ZG")
        else:
            crLabel[key] = val.replace("VG","WG")

nBins     = len(labels) #int(len(crLabel)/3.) if args.year == "2016" else len(crLabel)

# region plot, sorted/not sorted, w/ or w/o +-1sigma changes in one nuisance
def plotRegions( sorted=True ):
    # get region histograms
    hists = Results.getRegionHistos( postFit=args.postFit, plotBins=plotBins, addStatOnlyHistos=False, bkgSubstracted=False, labelFormater=labelFormater )["Bin0"]
    hists01 = Results01.getRegionHistos( postFit=args.postFit, plotBins=plotBins, addStatOnlyHistos=False, bkgSubstracted=False, labelFormater=labelFormater )["Bin0"]
    hists02 = Results02.getRegionHistos( postFit=args.postFit, plotBins=plotBins, addStatOnlyHistos=False, bkgSubstracted=False, labelFormater=labelFormater )["Bin0"]
    hists04 = Results04.getRegionHistos( postFit=args.postFit, plotBins=plotBins, addStatOnlyHistos=False, bkgSubstracted=False, labelFormater=labelFormater )["Bin0"]

    xLabel = ""

    differential = False
    if args.plotRegions and args.plotChannels:
        differential = True
        xLabel = "p_{T}(#gamma) [GeV]"
        hists    = replaceHistoBinning( hists )
        hists01  = replaceHistoBinning( hists01 )
        hists02 = replaceHistoBinning( hists02 )
        hists04 = replaceHistoBinning( hists04 )

    minMax = 0.99

    hists01H = hists01["signal"]
    hists01H.SetName("bestFit")
    hists01H.style        = styles.lineStyle( ROOT.kRed, width=3 )
    hists01H.legendText   = "Scale = 0.01%s * (p^{reco}_{T}-20 GeV)"%"%"

    hists01H_copy = copy.deepcopy(hists01["signal"])
    hists01H_copy.style        = styles.lineStyle( ROOT.kRed, width=3 )
    hists01H_copy.notInLegend   = True

    hists02H = hists02["signal"]
    hists02H.SetName("ctZ-0.45")
    hists02H.style        = styles.lineStyle( ROOT.kBlue, width=3, dashed=False )
    hists02H.legendText   = "Scale = 0.02%s * (p^{reco}_{T}-20 GeV)"%"%"

    hists04H = hists04["signal"]
    hists04H.SetName("ctZI0.45")
    hists04H.style        = styles.lineStyle( ROOT.kGreen+3 , width=3, dashed=False )
    hists04H.legendText   = "Scale = 0.04%s * (p^{reco}_{T}-20 GeV)"%"%"

    hists00H = hists["signal"]
    hists00H.SetName("nom")
    hists00H.style        = styles.lineStyle( ROOT.kBlack , width=3, dashed=False )
    hists00H.legendText   = "nominal"

    # some settings and things like e.g. uncertainty boxes
    drawObjects_       = drawObjects( nBins=nBins, isData=True, lumi_scale=lumi_scale, postFit=args.postFit, cardfile="", preliminary=False ) if not differential else drawLObjects()
    if not differential:
        drawObjects_      += drawDivisions( crLabel, misIDPOI=False )
        drawObjects_      += drawPTDivisions( crLabel, ptLabels )

    histModifications  = []
    if not differential:
        histModifications += [lambda h: h.GetYaxis().SetTitleSize(formatSettings(nBins)["textsize"])]
        histModifications += [lambda h: h.GetYaxis().SetLabelSize(formatSettings(nBins)["ylabelsize"])]
        histModifications += [lambda h: h.GetYaxis().SetTitleOffset(formatSettings(nBins)["textoffset"])]
        histModifications += [ setPTBinLabels(ptLabels, crName, fac=formatSettings(nBins)["offsetfactor"]*hists["signal"].GetMaximum())]

    ratioHistModifications  = []
    if not differential:
        ratioHistModifications += [lambda h: h.GetYaxis().SetTitleSize(formatSettings(nBins)["textsize"])]
        ratioHistModifications += [lambda h: h.GetYaxis().SetLabelSize(formatSettings(nBins)["ylabelsize"])]
        ratioHistModifications += [lambda h: h.GetYaxis().SetTitleOffset(formatSettings(nBins)["textoffset"])]
        ratioHistModifications += [lambda h: h.GetXaxis().SetTitleSize(formatSettings(nBins)["textsize"])]
        ratioHistModifications += [lambda h: h.GetXaxis().SetLabelSize(formatSettings(nBins)["xlabelsize"])]
        ratioHistModifications += [lambda h: h.GetXaxis().SetLabelOffset(0.045)]

    addon = []
    if args.plotYear:       addon += [args.plotYear]
    if args.plotRegions: addon += args.plotRegions
    if args.plotChannels: addon += args.plotChannels
    plotName = "_".join( ["regions"] + addon )

    plots = []
    plots.append([hists00H])
    plots.append([hists01H])
    plots.append([hists02H])
    plots.append([hists04H])

    ratioHistos = []
    ratioHistos.append((1, 0))
    ratioHistos.append((2, 0))
    ratioHistos.append((3, 0))

    if differential:
        legend = (0.33,0.6,0.9,0.9)
    else:
        legend = [ (0.17, formatSettings(nBins)["legylower"], 0.93, 0.9), formatSettings(nBins)["legcolumns"] ]
    plotting.draw(
        Plot.fromHisto( plotName,
                    plots,
                    texX = xLabel,
                    texY = "Events",
        ),
        logX = False, logY = True, sorting = False,
        plot_directory    = plotDirectory,
        legend            = legend,
        widths            = { "x_width":formatSettings(nBins)["padwidth"], "y_width":formatSettings(nBins)["padheight"], "y_ratio_width":formatSettings(nBins)["padratio"] } if not differential else {},
        yRange            = ( 7, hists["signal"].GetMaximum()*formatSettings(nBins)["heightFactor"] ) if not differential else (7,5e3),
        ratio             = { "yRange": (1-minMax, 1+minMax), "texY":"Obs./Pred.", "histos":ratioHistos, "histModifications":ratioHistModifications },
        drawObjects       = drawObjects_,
        histModifications = histModifications,
        copyIndexPHP      = True,
        extensions        = ["png","pdf","root"] if differential else ["png"],
    )

    return

plotRegions( sorted=False )
