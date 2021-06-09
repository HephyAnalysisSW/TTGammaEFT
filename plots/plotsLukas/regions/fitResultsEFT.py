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
plotDirectory = "/mnt/hephy/cms/lukas.lechner/www/TTGammaEFT/fitEFT/combined/v8/%s/%s"%(args.bestfit, "postfit" if args.postFit else "prefit")
#options = "--rMin 0.99 --rMax 1.01 --cminDefaultMinimizerTolerance=0.1 --cminDefaultMinimizerStrategy=0 --freezeParameters r"

# replace the combineResults object by the substituted card object
cardFile      = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/withbkg/cardFiles/defaultSetup/observed/SR3PtUnfoldEFT_SR4pPtUnfoldEFT_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF/ctZ_0_ctZI_0.txt"
#cardFile      = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/withbkg/cardFiles/defaultSetup/observed/SR3PtUnfoldEFT_SR4pPtUnfoldEFT_VG3_VG4p_misDY3_misDY4p_addDYSF/ctZ_0_ctZI_0.txt"
Results = CombineResults( cardFile=cardFile, plotDirectory=plotDirectory, year=args.year, bkgOnly=False, isSearch=False )

#rebinCard = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/withbkg/cardFiles/defaultSetup/observed/SR3PtUnfoldAll_SR4pPtUnfoldAll_addDYSF_addMisIDSF/ctZ_0_ctZI_0.txt"
##subCardFile = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/withbkg/cardFiles/defaultSetup/observed/SR3PtUnfoldAll_SR4pPtUnfoldAll_addDYSF_addMisIDSF/ctZ_0_ctZI_0.txt"
#subCardFile = Results.createRebinnedResults( rebinCard, skipStatOnly=True, setParameters="r=1", options=options )
#Results     = CombineResults( cardFile=subCardFile, plotDirectory=plotDirectory, year=args.year, bkgOnly=False, isSearch=False, rebinnedCardFile=rebinCard )

bfcardFile    = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/withbkg/cardFiles/defaultSetup/observed/SR3PtUnfoldEFT_SR4pPtUnfoldEFT_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF/%s.txt"%args.bestfit
Resultsbf = CombineResults( cardFile=bfcardFile, plotDirectory=plotDirectory, year=args.year, bkgOnly=False, isSearch=False )

cardFilem045    = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/withbkg/cardFiles/defaultSetup/observed/SR3PtUnfoldEFT_SR4pPtUnfoldEFT_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF/ctZ_-0.45_ctZI_0.txt"
Resultsm045 = CombineResults( cardFile=cardFilem045, plotDirectory=plotDirectory, year=args.year, bkgOnly=False, isSearch=False )

cardFileI045    = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/withbkg/cardFiles/defaultSetup/observed/SR3PtUnfoldEFT_SR4pPtUnfoldEFT_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF/ctZ_0_ctZI_0.45.txt"
ResultsI045 = CombineResults( cardFile=cardFileI045, plotDirectory=plotDirectory, year=args.year, bkgOnly=False, isSearch=False )

cardFile045    = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/withbkg/cardFiles/defaultSetup/observed/SR3PtUnfoldEFT_SR4pPtUnfoldEFT_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF/ctZ_0.45_ctZI_0.txt"
Results045 = CombineResults( cardFile=cardFile045, plotDirectory=plotDirectory, year=args.year, bkgOnly=False, isSearch=False )

#bfrebinCard = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/withbkg/cardFiles/defaultSetup/observed/SR3PtUnfoldAll_SR4pPtUnfoldAll_addDYSF_addMisIDSF/ctZ_-0.25_ctZI_-0.083.txt"
##bfsubCardFile = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/withbkg/cardFiles/defaultSetup/observed/SR3PtUnfoldAll_SR4pPtUnfoldAll_addDYSF_addMisIDSF/ctZ_-0.25_ctZI_-0.083.txt"
#bfsubCardFile = Resultsbf.createRebinnedResults( bfrebinCard, skipStatOnly=True, setParameters="r=1", options=options )
#Resultsbf     = CombineResults( cardFile=bfsubCardFile, plotDirectory=plotDirectory, year=args.year, bkgOnly=False, isSearch=False, rebinnedCardFile=bfrebinCard )

#postFit = Resultsbf.getPulls( postFit=True )
#freezeParams = "EFT_nJet=%f,r=1"%postFit["EFT_nJet"].val
#freezeParams = "r=1"
#options = "--setParameters %s --freezeParameters r,EFT_nJet"%freezeParams
#options = "--cminDefaultMinimizerStrategy=0 --cminDefaultMinimizerTolerance=0.001 --setParameters %s --freezeParameters r --exclude EFT_nJet"%freezeParams
#Results.getImpactPlot( expected=False, printPNG=False, cores=20, options=options, rMin=0.999, rMax=1.001 )
#sys.exit()


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
elif args.year == "combined": lumi_scale = int(35.92 + 41.53 + 59.74)

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

nBins     = len(labels) #int(len(crLabel)/3.) if args.year == "combined" else len(crLabel)

# region plot, sorted/not sorted, w/ or w/o +-1sigma changes in one nuisance
def plotRegions( sorted=True ):
    # get region histograms
    if args.year == "combined":
        hists_tmp = Results.getRegionHistos( postFit=args.postFit, plotBins=plotBins, addStatOnlyHistos=False, bkgSubstracted=False, labelFormater=labelFormater )
        for i, dir in enumerate(Results.channels if not args.plotYear else [key for key, val in Results.years.iteritems() if val == args.plotYear]):
            if i == 0:
                hists = {key:hist.Clone(str(i)+dir+key) for key, hist in hists_tmp[dir].iteritems()}
            else:
               for key, hist in hists_tmp[dir].iteritems():
                    hists[key].Add(hist.Clone(str(i)+dir+key))

        bfhists_tmp = Resultsbf.getRegionHistos( postFit=args.postFit, plotBins=plotBins, addStatOnlyHistos=False, bkgSubstracted=False, labelFormater=labelFormater )
#        bfhists_tmp = Resultsbf.getRegionHistos( postFit=False, plotBins=plotBins, addStatOnlyHistos=False, bkgSubstracted=False, labelFormater=labelFormater )
        for i, dir in enumerate(Resultsbf.channels if not args.plotYear else [key for key, val in Resultsbf.years.iteritems() if val == args.plotYear]):
            if i == 0:
                histsbf = {key:hist.Clone(str(i)+dir+key+"eft") for key, hist in bfhists_tmp[dir].iteritems()}
            else:
               for key, hist in bfhists_tmp[dir].iteritems():
                    histsbf[key].Add(hist.Clone(str(i)+dir+key+"eft"))

        hists_tmpm045 = Resultsm045.getRegionHistos( postFit=args.postFit, plotBins=plotBins, addStatOnlyHistos=False, bkgSubstracted=False, labelFormater=labelFormater )
        for i, dir in enumerate(Resultsm045.channels if not args.plotYear else [key for key, val in Resultsm045.years.iteritems() if val == args.plotYear]):
            if i == 0:
                histsm045 = {key:hist.Clone(str(i)+dir+key+"eftm045") for key, hist in hists_tmpm045[dir].iteritems()}
            else:
               for key, hist in hists_tmpm045[dir].iteritems():
                    histsm045[key].Add(hist.Clone(str(i)+dir+key+"eftm045"))

        hists_tmpI045 = ResultsI045.getRegionHistos( postFit=args.postFit, plotBins=plotBins, addStatOnlyHistos=False, bkgSubstracted=False, labelFormater=labelFormater )
        for i, dir in enumerate(ResultsI045.channels if not args.plotYear else [key for key, val in ResultsI045.years.iteritems() if val == args.plotYear]):
            if i == 0:
                histsI045 = {key:hist.Clone(str(i)+dir+key+"eftI045") for key, hist in hists_tmpI045[dir].iteritems()}
            else:
               for key, hist in hists_tmpI045[dir].iteritems():
                    histsI045[key].Add(hist.Clone(str(i)+dir+key+"eftI045"))

        hists_tmp045 = Results045.getRegionHistos( postFit=args.postFit, plotBins=plotBins, addStatOnlyHistos=False, bkgSubstracted=False, labelFormater=labelFormater )
        for i, dir in enumerate(Results045.channels if not args.plotYear else [key for key, val in Results045.years.iteritems() if val == args.plotYear]):
            if i == 0:
                hists045 = {key:hist.Clone(str(i)+dir+key+"eft045") for key, hist in hists_tmp045[dir].iteritems()}
            else:
               for key, hist in hists_tmp045[dir].iteritems():
                    hists045[key].Add(hist.Clone(str(i)+dir+key+"eft045"))

    xLabel = ""

    differential = False
    if args.plotRegions and args.plotChannels:
        differential = True
        xLabel = "p_{T}(#gamma) [GeV]"
        hists    = replaceHistoBinning( hists )
        histsbf  = replaceHistoBinning( histsbf )
        histsm045 = replaceHistoBinning( histsm045 )
        histsI045 = replaceHistoBinning( histsI045 )
        hists045 = replaceHistoBinning( hists045 )

    minMax = 0.26 # if args.postFit else 0.29
    boxes,     ratio_boxes       = getUncertaintyBoxes( copy.copy(hists["total"]), minMax, lineColor=ROOT.kGray+3, fillColor=ROOT.kGray+3, hashcode=formatSettings(nBins)["hashcode"] if not differential else 3544 )

    bfEFTHist = histsbf["total"]
    bfEFTHist.SetName("bestFit")
    bfEFTHist.style        = styles.lineStyle( ROOT.kRed, width=3 )
    bfEFTHist.legendText   = "SM-EFT best fit"

    bfEFTHist_copy = copy.deepcopy(histsbf["total"])
    bfEFTHist_copy.style        = styles.lineStyle( ROOT.kRed, width=3 )
    bfEFTHist_copy.notInLegend   = True

    EFTHistm045 = histsm045["total"]
    EFTHistm045.SetName("ctZ-0.45")
    EFTHistm045.style        = styles.lineStyle( ROOT.kBlue, width=3, dashed=True )
    EFTHistm045.legendText   = "c_{tZ} = -0.45 (#Lambda/TeV)^{2}"

    EFTHistI045 = histsI045["total"]
    EFTHistI045.SetName("ctZI0.45")
    EFTHistI045.style        = styles.lineStyle( ROOT.kGreen+3 , width=3, dashed=True )
    EFTHistI045.legendText   = "c^{I}_{tZ} = 0.45 (#Lambda/TeV)^{2}"

    EFTHist045 = hists045["total"]
    EFTHist045.SetName("ctZ0.45")
    EFTHist045.style        = styles.lineStyle( ROOT.kCyan+1, width=3, dashed=True )
    EFTHist045.legendText   = "c_{tZ} = 0.45 (#Lambda/TeV)^{2}"

    hists["data"].style        = styles.errorStyle( ROOT.kBlack )
    hists["data"].legendText   = "Observed"
#    hists["data"].legendOption = "p"

    data_copy = hists["data"].Clone()
    data_copy.style        = styles.errorStyle( ROOT.kBlack )
    data_copy.notInLegend = True

    empty = copy.deepcopy(hists["data"].Clone())
    empty.Scale(0)
    empty.style        = styles.lineStyle( ROOT.kWhite, width=0 )
    empty.legendText = " "

    header = copy.deepcopy(hists["data"].Clone())
    header.Scale(0)
    header.style        = styles.lineStyle( ROOT.kWhite, width=0 )
    header.legendText = "e#mu channel, 3#geq4 jets"

    uncHist = hists["data"].Clone()
    uncHist.Scale(0)
    uncHist.style = styles.hashStyle(hashCode=3244 if not differential else 3544, lineColor = ROOT.kBlack, lineWidth=1)
    uncHist.legendText = "Uncertainty"
    uncHist.legendOption = "f"

    for h_key, h in hists.iteritems():
        if "total" in h_key or h_key not in processes: continue
        hists[h_key].legendText  = default_processes[h_key]["texName"]
        hists[h_key].style = styles.fillStyle( default_processes[h_key]["color"], lineWidth = 1, errors=False )
        if not differential:
            hists[h_key].LabelsOption("v","X")

    # some settings and things like e.g. uncertainty boxes
    drawObjects_       = drawObjects( nBins=nBins, isData=True, lumi_scale=lumi_scale, postFit=args.postFit, cardfile="", preliminary=False ) if not differential else drawLObjects()
    drawObjects_      += boxes
    if not differential:
        drawObjects_      += drawDivisions( crLabel, misIDPOI=False )
        drawObjects_      += drawPTDivisions( crLabel, ptLabels )

    histModifications  = []
    if not differential:
        histModifications += [lambda h: h.GetYaxis().SetTitleSize(formatSettings(nBins)["textsize"])]
        histModifications += [lambda h: h.GetYaxis().SetLabelSize(formatSettings(nBins)["ylabelsize"])]
        histModifications += [lambda h: h.GetYaxis().SetTitleOffset(formatSettings(nBins)["textoffset"])]
        histModifications += [ setPTBinLabels(ptLabels, crName, fac=formatSettings(nBins)["offsetfactor"]*hists["total"].GetMaximum())]

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

    if differential:
        plots = [ [hists[k] for k in ["signal", "fakes", "misID", "other", "WG", "QCD", "ZG"]] ]
        ratioHistos = [(1, 0)]
    else:
        plots, ratioHistos = Results.getRegionHistoList( hists, processes=processes, noData=False, sorted=not differential, unsortProcesses=True, bkgSubstracted=False, directory="dc_2016" )


#    rootfile = ROOT.TFile( "eft_pt_3mu.root", "RECREATE")
#    for h in hists.values() + [bfEFTHist,EFTHist045,EFTHistI045,EFTHistm045]:
#       h.Write()
#    rootfile.Close()
#    sys.exit()


    plots.append([bfEFTHist])
    if differential: plots.append([hists["data"]])
    plots.append([EFTHist045])
    plots.append([uncHist])
    plots.append([EFTHistI045])
    plots.append([empty])
    plots.append([EFTHistm045])
    plots.append([empty])
    plots.append([header])
    plots.append([bfEFTHist_copy])
    plots.append([data_copy])

    if differential:
        ratioHistos.append((3, 0))
        ratioHistos.append((5, 0))
        ratioHistos.append((7, 0))
        ratioHistos.append((1, 0))
        ratioHistos.append((2, 0))
    else:
        ratioHistos.append((3, 0))
        ratioHistos.append((4, 0))
        ratioHistos.append((5, 0))
        ratioHistos.append((2, 0))

    if differential:
        legend = [(0.23,0.48,0.9,0.9),2]
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
        yRange            = ( 7, hists["total"].GetMaximum()*formatSettings(nBins)["heightFactor"] ) if not differential else (7,9e4),
        ratio             = { "yRange": (1-minMax, 1+minMax), "texY":"Obs./Pred.", "histos":ratioHistos, "drawObjects":ratio_boxes, "histModifications":ratioHistModifications },
        drawObjects       = drawObjects_,
        histModifications = histModifications,
        copyIndexPHP      = True,
        extensions        = ["png","pdf","root"] if differential else ["png"],
    )

    return

plotRegions( sorted=False )
