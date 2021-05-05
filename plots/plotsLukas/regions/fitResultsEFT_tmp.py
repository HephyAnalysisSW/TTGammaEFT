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
argParser.add_argument("--postFit",              action="store_true",                            help="Apply pulls?")
argParser.add_argument("--preliminary",          action="store_true",                            help="Run expected?")
argParser.add_argument("--year",                 action="store",      type=str, default="2016",    help="Which year?")
argParser.add_argument("--bestfit",                 action="store",      type=str, default="ctZ_-0.25_ctZI_-0.083",    help="Which fit point")
args = argParser.parse_args()

# logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile = None )
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

args.year = "combined"
lumi_scale = int(35.92 + 41.53 + 59.74)

#bf = "ctZ_-0.25_ctZI_-0.083"
plotDirectory = "/mnt/hephy/cms/lukas.lechner/www/TTGammaEFT/fitEFT/combined/v0/%s/%s"%(args.bestfit, "postfit" if args.postFit else "prefit")
options = "--rMin 0.99 --rMax 1.01 --cminDefaultMinimizerTolerance=0.1 --cminDefaultMinimizerStrategy=0 --freezeParameters r"

# replace the combineResults object by the substituted card object
cardFile      = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/withbkg/cardFiles/defaultSetup/observed/SR3PtUnfoldEFT_SR4pPtUnfoldEFT_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF/ctZ_0_ctZI_0.txt"
Results = CombineResults( cardFile=cardFile, plotDirectory=plotDirectory, year=args.year, bkgOnly=False, isSearch=False )
#rebinCard = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/withbkg/cardFiles/defaultSetup/observed/SR3PtUnfoldEFTAll_SR4pPtUnfoldEFTAll_addDYSF_addMisIDSF/ctZ_0_ctZI_0.txt"
##subCardFile = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/withbkg/cardFiles/defaultSetup/observed/SR3PtUnfoldEFTAll_SR4pPtUnfoldEFTAll_addDYSF_addMisIDSF/ctZ_0_ctZI_0.txt"
#subCardFile = Results.createRebinnedResults( rebinCard, skipStatOnly=True, setParameters="r=1", options=options )
#Results     = CombineResults( cardFile=subCardFile, plotDirectory=plotDirectory, year=args.year, bkgOnly=False, isSearch=False, rebinnedCardFile=rebinCard )

bfcardFile    = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/withbkg/cardFiles/defaultSetup/observed/SR3PtUnfoldEFT_SR4pPtUnfoldEFT_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF/%s.txt"%args.bestfit
Resultsbf = CombineResults( cardFile=bfcardFile, plotDirectory=plotDirectory, year=args.year, bkgOnly=False, isSearch=False )
#bfrebinCard = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/withbkg/cardFiles/defaultSetup/observed/SR3PtUnfoldEFTAll_SR4pPtUnfoldEFTAll_addDYSF_addMisIDSF/ctZ_-0.25_ctZI_-0.083.txt"
##bfsubCardFile = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/withbkg/cardFiles/defaultSetup/observed/SR3PtUnfoldEFTAll_SR4pPtUnfoldEFTAll_addDYSF_addMisIDSF/ctZ_-0.25_ctZI_-0.083.txt"
#bfsubCardFile = Resultsbf.createRebinnedResults( bfrebinCard, skipStatOnly=True, setParameters="r=1", options=options )
#Resultsbf     = CombineResults( cardFile=bfsubCardFile, plotDirectory=plotDirectory, year=args.year, bkgOnly=False, isSearch=False, rebinnedCardFile=bfrebinCard )


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

    ch = label.split(" ")[1]
    ch = ch.replace("all","e+mu")
    ch = ch.replace("mu","#mu")
    ch = ch.replace("tight","")

    return reg + ", " + ch

labelFormater = formatLabel
labels = [ ( i, label ) for i, label in enumerate(Results.getBinLabels( labelFormater=lambda x:x.split(" "))[Results.channels[0]])]
if args.plotRegions:
    labels = filter( lambda (i,(year, ch, lab, reg)): reg in args.plotRegions, labels )

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

nBins     = len(labels) #int(len(crLabel)/3.) if args.year == "combined" else len(crLabel)

# region plot, sorted/not sorted, w/ or w/o +-1sigma changes in one nuisance
def plotRegions( sorted=True ):
    # get region histograms
    if args.year == "combined":
        hists_tmp = Results.getRegionHistos( postFit=args.postFit, plotBins=plotBins, addStatOnlyHistos=False, bkgSubstracted=False, labelFormater=labelFormater )
        for i, dir in enumerate(Results.channels):
            if i == 0:
                hists = {key:hist.Clone(str(i)+dir+key) for key, hist in hists_tmp[dir].iteritems()}
            else:
               for key, hist in hists_tmp[dir].iteritems():
                    print key, hist.GetNbinsX(), hists[key].GetNbinsX()
                    hists[key].Add(hist.Clone(str(i)+dir+key))

        bfhists_tmp = Resultsbf.getRegionHistos( postFit=args.postFit, plotBins=plotBins, addStatOnlyHistos=False, bkgSubstracted=False, labelFormater=labelFormater )
#        bfhists_tmp = Resultsbf.getRegionHistos( postFit=False, plotBins=plotBins, addStatOnlyHistos=False, bkgSubstracted=False, labelFormater=labelFormater )
        for i, dir in enumerate(Resultsbf.channels):
            if i == 0:
                histsbf = {key:hist.Clone(str(i)+dir+key+"eft") for key, hist in bfhists_tmp[dir].iteritems()}
            else:
               for key, hist in bfhists_tmp[dir].iteritems():
                    print key, hist.GetNbinsX(), histsbf[key].GetNbinsX()
                    histsbf[key].Add(hist.Clone(str(i)+dir+key+"eft"))

    ch = "all"
    xLabel = ""
    minMax = 0.17 # if args.postFit else 0.29
    boxes,     ratio_boxes       = getUncertaintyBoxes( copy.copy(hists["total"]), minMax, lineColor=ROOT.kGray+3, fillColor=ROOT.kGray+3, hashcode=formatSettings(nBins)["hashcode"] )

    bfEFTHist = histsbf["total"]
    bfEFTHist.style        = styles.lineStyle( ROOT.kRed, width=3 )
    bfEFTHist.legendText   = "EFT best fit"

    hists["data"].style        = styles.errorStyle( ROOT.kBlack )
    hists["data"].legendText   = "Observed"
    hists["data"].legendOption = "p"

    uncHist = hists["data"].Clone()
    uncHist.Scale(0)
    uncHist.style = styles.hashStyle(hashCode=3244)
    uncHist.legendText = "Uncertainty"

    for h_key, h in hists.iteritems():
        if "total" in h_key or h_key not in processes: continue
        print h_key, default_processes[h_key]["texName"], default_processes[h_key]["color"]
        hists[h_key].legendText  = default_processes[h_key]["texName"]
        hists[h_key].style = styles.fillStyle( default_processes[h_key]["color"], lineWidth = 1, errors=False )
        hists[h_key].LabelsOption("v","X")

    # some settings and things like e.g. uncertainty boxes
    drawObjects_       = drawObjects( nBins=nBins, isData=True, lumi_scale=lumi_scale, postFit=args.postFit, cardfile="", preliminary=False )
    drawObjects_      += boxes
    drawObjects_      += drawDivisions( crLabel, misIDPOI=False )
    drawObjects_      += drawPTDivisions( crLabel, ptLabels )

    histModifications  = []
    histModifications += [lambda h: h.GetYaxis().SetTitleSize(formatSettings(nBins)["textsize"])]
    histModifications += [lambda h: h.GetYaxis().SetLabelSize(formatSettings(nBins)["ylabelsize"])]
    histModifications += [lambda h: h.GetYaxis().SetTitleOffset(formatSettings(nBins)["textoffset"])]
    histModifications += [ setPTBinLabels(ptLabels, crName, fac=formatSettings(nBins)["offsetfactor"]*hists["total"].GetMaximum())]

    ratioHistModifications  = []
    ratioHistModifications += [lambda h: h.GetYaxis().SetTitleSize(formatSettings(nBins)["textsize"])]
    ratioHistModifications += [lambda h: h.GetYaxis().SetLabelSize(formatSettings(nBins)["ylabelsize"])]
    ratioHistModifications += [lambda h: h.GetYaxis().SetTitleOffset(formatSettings(nBins)["textoffset"])]
    ratioHistModifications += [lambda h: h.GetXaxis().SetTitleSize(formatSettings(nBins)["textsize"])]
    ratioHistModifications += [lambda h: h.GetXaxis().SetLabelSize(formatSettings(nBins)["xlabelsize"])]
    ratioHistModifications += [lambda h: h.GetXaxis().SetLabelOffset(0.035)]

    addon = []
    if args.plotRegions: addon += args.plotRegions
    if args.plotChannels: addon += args.plotChannels
    plotName = "_".join( ["regions"] + addon )

    plots, ratioHistos = Results.getRegionHistoList( hists, processes=processes, noData=False, sorted=True, unsortProcesses=True, bkgSubstracted=False, directory="dc_2016" )

    plots.append([bfEFTHist])
    ratioHistos.append((2, 0))
    plots.append([uncHist])

    plotting.draw(
        Plot.fromHisto( plotName,
                    plots,
                    texX = "",
                    texY = "Events",
        ),
        logX = False, logY = True, sorting = False,
        plot_directory    = plotDirectory,
        legend            = [ (0.17, formatSettings(nBins)["legylower"], 0.93, 0.9), formatSettings(nBins)["legcolumns"] ],
        widths            = { "x_width":formatSettings(nBins)["padwidth"], "y_width":formatSettings(nBins)["padheight"], "y_ratio_width":formatSettings(nBins)["padratio"] },
        yRange            = ( 7, hists["total"].GetMaximum()*formatSettings(nBins)["heightFactor"] ),
        ratio             = { "yRange": (1-minMax, 1+minMax), "texY":"Obs./Pred.", "histos":ratioHistos, "drawObjects":ratio_boxes, "histModifications":ratioHistModifications },
        drawObjects       = drawObjects_,
        histModifications = histModifications,
        copyIndexPHP      = True,
        extensions        = ["png"],
    )

    return

plotRegions( sorted=False )
