#!/usr/bin/env python

""" 
Get cardfile result plots
"""

# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy

# Helpers
from plotHelpers                      import *

# Analysis
from Analysis.Tools.cardFileWriter.CombineResults    import CombineResults

# TTGammaEFT
from TTGammaEFT.Tools.user            import plot_directory, cache_directory
from TTGammaEFT.Analysis.SetupHelpers import allRegions, processesMisIDPOI, default_processes

# RootTools
from RootTools.core.standard          import *

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--small",                action="store_true",                            help="small?")
argParser.add_argument("--logLevel",             action="store",                default="INFO",  help="log level?", choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"])
argParser.add_argument("--blinded",              action="store_true")
argParser.add_argument("--overwrite",            action="store_true",                            help="Overwrite existing output files, bool flag set to True  if used")
argParser.add_argument("--postFit",              action="store_true",                            help="Apply pulls?")
argParser.add_argument("--expected",             action="store_true",                            help="Run expected?")
argParser.add_argument("--preliminary",          action="store_true",                            help="Run expected?")
#argParser.add_argument("--systOnly",             action="store_true",                            help="correlation matrix with systematics only?")
argParser.add_argument("--year",                 action="store",      type=int, default=2016,    help="Which year?")
argParser.add_argument("--carddir",              action='store',                default='limits/cardFiles/defaultSetup/observed',      help="which cardfile directory?")
argParser.add_argument("--cardfile",             action='store',                default='',      help="which cardfile?")
argParser.add_argument("--substituteCard",       action='store',                default=None,    help="which cardfile to substitute the plot with?")
argParser.add_argument("--plotRegions",          action='store', nargs="*",     default=None,    help="which regions to plot?")
argParser.add_argument("--plotChannels",         action='store', nargs="*",     default=None,    help="which regions to plot?")
argParser.add_argument("--plotNuisances",        action='store', nargs="*",     default=None,    help="plot specific nuisances?")
argParser.add_argument("--cores",                action="store", default=1,               type=int,                               help="Run on n cores in parallel")
argParser.add_argument("--bkgOnly",              action='store_true',                            help="background fit?")
argParser.add_argument("--sorted",               action='store_true',           default=False,   help="sort histogram for each bin?")
argParser.add_argument("--plotRegionPlot",       action='store_true',           default=False,   help="plot RegionPlot")
argParser.add_argument("--plotImpacts",          action='store_true',           default=False,   help="plot Impacts")
argParser.add_argument("--plotCovMatrix",        action='store_true',           default=False,   help="plot covariance matrix")
argParser.add_argument("--plotCorrelations",     action='store_true',           default=False,   help="plot Correlation matrix")
argParser.add_argument("--bkgSubstracted",       action='store_true',           default=False,   help="plot region plot background substracted")
argParser.add_argument("--cacheHistogram",       action='store_true',           default=False,   help="store the histogram as cache")
args = argParser.parse_args()

# logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile = None )
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

# fix label (change later)
args.preliminary = True
# make sure the list is always in the same order
if args.plotNuisances: args.plotNuisances.sort()

if args.plotChannels and "all" in args.plotChannels: args.plotChannels += ["e","mu"]
if args.plotChannels and "e"   in args.plotChannels: args.plotChannels += ["eetight"]
if args.plotChannels and "mu"  in args.plotChannels: args.plotChannels += ["mumutight"]

if   args.year == 2016: lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74

dirName  = "_".join( [ item for item in args.cardfile.split("_") if not (item.startswith("add") or item == "incl") ] )
add      = [ item for item in args.cardfile.split("_") if (item.startswith("add") or item == "incl")  ]
add.sort()
fit      = "_".join( ["postFit" if args.postFit else "preFit"] + add )

plotDirectory = os.path.join(plot_directory, "fit", str(args.year), fit, dirName)
cardFile      = os.path.join( cache_directory, "analysis", str(args.year), args.carddir, args.cardfile+".txt" )
logger.info("Plotting from cardfile %s"%cardFile)

# replace the combineResults object by the substituted card object
Results = CombineResults( cardFile=cardFile, plotDirectory=plotDirectory, year=args.year, bkgOnly=args.bkgOnly, isSearch=False )
if args.substituteCard:
    subCardFile = os.path.join( cache_directory, "analysis", str(args.year), args.carddir, args.substituteCard+".txt" )
    subCardFile = Results.createRebinnedResults( subCardFile )
    del Results
    Results     = CombineResults( cardFile=subCardFile, plotDirectory=plotDirectory, year=args.year, bkgOnly=args.bkgOnly, isSearch=False )

# get list of labels
labelFormater   = lambda x: ", ".join( [x.split(" ")[2], x.split(" ")[0].replace("mu","#mu").replace("tight","")] )
labels = [ ( i, label ) for i, label in enumerate(Results.getBinLabels( labelFormater=lambda x:x.split(" "))) ]
if args.plotRegions:  labels = filter( lambda (i,(ch, lab, reg)): reg in args.plotRegions, labels )
if args.plotChannels: labels = filter( lambda (i,(ch, lab, reg)): ch in args.plotChannels, labels )

crName    = [ cr for i, (lep, reg, cr) in labels ]
plotBins  = [ i  for i, (lep, reg, cr) in labels ]
crLabel   = map( lambda (i,(ch, lab, reg)): ", ".join( [ reg, ch.replace("mu","#mu").replace("tight","") ] ), labels )
ptLabels  = map( lambda (i,(ch, lab, reg)): convLabel(lab), labels )
nBins     = len(crLabel)


if "misIDPOI" in args.cardfile:
    processes = processesMisIDPOI.keys()
else:
    card = args.substituteCard if args.substituteCard else args.cardfile
    processes = [ cr for cr in card.split("_") if (not args.plotRegions or (args.plotRegions and cr in args.plotRegions)) and cr in allRegions.keys() ]
    processes = allRegions[processes[0]]["processes"].keys()

###
### PLOTS
###

# region plot, sorted/not sorted, w/ or w/o +-1sigma changes in one nuisance
def plotRegions( sorted=True ):
    # get region histograms
    hists = Results.getRegionHistos( postFit=args.postFit, plotBins=plotBins, nuisances=args.plotNuisances, bkgSubstracted=args.bkgSubstracted, labelFormater=labelFormater, directory="Bin0" )["Bin0"]
    
    differential = False
    ch = "all"
    xLabel = ""
    if args.bkgSubstracted:
        subCard = args.substituteCard.split("_")
        if len(subCard) == 2 and subCard[1] in ["e", "mu"]:
            ch = subCard[1]
            differential = True
            reg = allRegions[subCard[0]]["regions"]
            bins, min, max = len(reg), reg[0].vals.values()[0][0], reg[-1].vals.values()[0][1]
            if max == -999:
                max    = reg[-1].vals.values()[0][0]
                bins -= 1
            xLabel = reg[0].vals.keys()[0]
            if "PhotonGood0" in xLabel:
                if xLabel.endswith("_pt"):  xLabel = "p_{T}(#gamma) [GeV]"
                if xLabel.endswith("_eta"): xLabel = "#eta(#gamma)"
            for h_key, h in hists.iteritems():
                h_sub = ROOT.TH1F(h.GetName(), h.GetName(), bins, min, max )
                for i in range(h_sub.GetNbinsX()):
                    h_sub.SetBinContent( i+1, h.GetBinContent(i+1))
                    h_sub.SetBinError( i+1, h.GetBinError(i+1))
                hists[h_key] = h_sub.Clone(h_key)
                del h_sub

    minMax = 0.5 if args.bkgSubstracted and xLabel.endswith("_pt") else 0.25
    if args.bkgSubstracted:
        boxes,     ratio_boxes     = getErrorBoxes( copy.copy(hists["data"]), minMax, lineColor=ROOT.kAzure-3, fillColor=ROOT.kAzure-3, hashcode=1001 )
        boxes_sys, ratio_boxes_sys = getErrorBoxes( copy.copy(hists["data_syst"]), minMax, lineColor=ROOT.kOrange-2, fillColor=ROOT.kOrange-2, hashcode=1001 )
    else:
        boxes,     ratio_boxes     = getUncertaintyBoxes( hists["total"], minMax, lineColor=ROOT.kGray+3, fillColor=ROOT.kGray+3, hashcode=formatSettings(nBins)["hashcode"] )

    hists["data"].style        = styles.errorStyle( ROOT.kBlack )
    hists["data"].legendText   = "data" if not args.bkgSubstracted else "bkg-sub. data (#color[92]{syst} + #color[61]{total} error, %s)"%(ch.replace("mu","#mu"))
    hists["data"].legendOption = "p" if args.bkgSubstracted else "p"

    if args.bkgSubstracted:
        hists["data_syst"].style        = styles.errorStyle( ROOT.kBlack )
        hists["data_syst"].notInLegend  = True

        hists["signal"].style      = styles.lineStyle( ROOT.kOrange+7, width=2, errors=True )
        hists["signal"].legendText = "SM prediction (detector level)"

    else:
        for h_key, h in hists.iteritems():
            if "total" in h_key or h_key not in processes: continue
            hists[h_key].legendText  = default_processes[h_key]["texName"]
            hists[h_key].style = styles.fillStyle( default_processes[h_key]["color"], errors=False )
            hists[h_key].LabelsOption("v","X")

    # some settings and things like e.g. uncertainty boxes
    drawObjects_       = drawObjects( nBins=nBins, isData=(not args.expected), lumi_scale=lumi_scale, postFit=args.postFit, cardfile=args.substituteCard if args.substituteCard else args.cardfile, preliminary=args.preliminary )
    drawObjects_      += boxes 
    if args.bkgSubstracted: drawObjects_ += boxes_sys
    drawObjects_      += drawDivisions( crLabel, misIDPOI=("misIDPOI" in args.cardfile) ) 
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
        ratioHistModifications += [lambda h: h.GetXaxis().SetLabelOffset(0.035)]

    # get histo list
    plots, ratioHistos = Results.getRegionHistoList( hists, processes=processes, noData=False, sorted=sorted and not args.bkgSubstracted, bkgSubstracted=args.bkgSubstracted )
#    if args.bkgSubstracted: plots += [[hists["empty"]]]

    addon = []
    if args.bkgSubstracted: addon += ["bkgSub"]
    if args.substituteCard: addon += ["rebinned"] + [ cr for cr in subCard if cr not in args.cardfile.split("_") ]
    if args.plotNuisances:  addon += args.plotNuisances

    # plot name
    if   args.plotRegions and args.plotChannels: plotName = "_".join( ["regions"] + addon + args.plotRegions + [ch for ch in args.plotChannels if not "tight" in ch] )
    elif args.plotRegions:                       plotName = "_".join( ["regions"] + addon + args.plotRegions )
    elif args.plotChannels:                      plotName = "_".join( ["regions"] + addon + [ch for ch in args.plotChannels if not "tight" in ch] )
    else:                                        plotName = "_".join( ["regions"] + addon )

    if args.cacheHistogram:
        from Analysis.Tools.MergingDirDB      import MergingDirDB
        from TTGammaEFT.Tools.user            import cache_directory
        cache_dir = os.path.join(cache_directory, "unfolding", str(args.year), "bkgSubstracted")
        dirDB = MergingDirDB(cache_dir)
        if not dirDB: raise
        name = ["bkgSubtracted", args.substituteCard, args.cardfile]
        if args.plotRegions:  name += args.plotRegions
        if args.plotChannels: name += args.plotChannels
        dirDB.add( "_".join(name), hists["data"], overwrite=True )


    if args.plotRegionPlot:

        plotting.draw(
            Plot.fromHisto( plotName,
                    plots,
                    texX = "" if not differential else xLabel,
                    texY = "Observed - Background" if args.bkgSubstracted else "Number of Events",
            ),
            logX = False, logY = True, sorting = False, 
            plot_directory    = plotDirectory,
            legend            = [ (0.2, 0.86 if args.bkgSubstracted else formatSettings(nBins)["legylower"], 0.9, 0.9), formatSettings(nBins)["legcolumns"] ] if not differential else (0.15,0.80,0.9,0.9),
            widths            = { "x_width":formatSettings(nBins)["padwidth"], "y_width":formatSettings(nBins)["padheight"], "y_ratio_width":formatSettings(nBins)["padratio"] } if not differential else {},
            yRange            = ( 0.7, hists["total"].GetMaximum()*formatSettings(nBins)["heightFactor"] ) if not differential else "auto",
            ratio             = { "yRange": (0.5, 1.5) if args.bkgSubstracted and xLabel.endswith("_pt") else (0.75, 1.25), "texY":"Theory/Data" if args.bkgSubstracted else "Data/MC", "histos":ratioHistos, "drawObjects":ratio_boxes if not args.bkgSubstracted else ratio_boxes + ratio_boxes_sys, "histModifications":ratioHistModifications },
            drawObjects       = drawObjects_ if not differential else drawObjectsDiff(lumi_scale) + boxes + boxes_sys,
            histModifications = histModifications,
            copyIndexPHP      = True,
            extensions        = ["png", "pdf", "root"] if args.bkgSubstracted else ["png"], # pdfs are quite large for sorted histograms (disco plot)
            redrawHistos      = args.bkgSubstracted,
        )

    del hists

# covariance matrix 2D plot
def plotCovariance():
    # get the results
    covhist = Results.getCovarianceHisto( postFit=args.postFit, labelFormater=labelFormater )

    histModifications  = []
    histModifications += [lambda h:h.GetYaxis().SetLabelSize(12)]
    histModifications += [lambda h:h.GetXaxis().SetLabelSize(12)]
    histModifications += [lambda h:h.GetZaxis().SetLabelSize(0.03)]

    canvasModifications  = []
    canvasModifications += [lambda c:c.SetLeftMargin(0.25)]
    canvasModifications += [lambda c:c.SetBottomMargin(0.25)]

    for log in [True, False]:
        drawObjects_ = drawCoObjects( lumi_scale=lumi_scale, bkgOnly=args.bkgOnly, postFit=args.postFit, incl=("incl" in args.cardfile), preliminary=args.preliminary )
        plotName     = "_".join( ["covarianceMatrix", "log" if log else "lin"] )

        plotting.draw2D(
            Plot2D.fromHisto( plotName,
                [[covhist]],
                texX = "",
                texY = "",
            ),
        logX = False, logY = False, logZ = log, 
        plot_directory      = plotDirectory,
        widths              = {"x_width":800, "y_width":800},
        zRange              = (0.000001,1) if log else (0,1),
        drawObjects         = drawObjects_,
        histModifications   = histModifications,
        canvasModifications = canvasModifications,
        copyIndexPHP        = True,
    )

    del covhist

# correlation of nuisances 2D plot
def plotCorrelations( systOnly ):
    # get the results
    corrhist     = Results.getCorrelationHisto( systOnly=systOnly )
    drawObjects_ = drawCoObjects( lumi_scale=lumi_scale, bkgOnly=args.bkgOnly, postFit=args.postFit, incl=("incl" in args.cardfile), preliminary=args.preliminary )

    addon = ""
    if systOnly:      addon += "_systOnly"
    if args.bkgOnly:  addon += "_bkgOnly"

    histModifications   = []
    histModifications  += [lambda h:h.GetYaxis().SetLabelSize(12)]
    histModifications  += [lambda h:h.GetXaxis().SetLabelSize(12)]
    histModifications  += [lambda h:h.GetZaxis().SetLabelSize(0.03)]

    canvasModifications  = []
    canvasModifications += [lambda c:c.SetLeftMargin(0.25)]
    canvasModifications += [lambda c:c.SetBottomMargin(0.25)]

    drawObjects_ = drawCoObjects( lumi_scale=lumi_scale, bkgOnly=args.bkgOnly, postFit=args.postFit, incl=("incl" in args.cardfile), preliminary=args.preliminary )

    plotting.draw2D(
        Plot2D.fromHisto("correlationMatrix"+addon,
            [[corrhist]],
            texX = "",
            texY = "",
        ),
        logX = False, logY = False, logZ = False, 
        plot_directory      = plotDirectory, 
        widths              = {"x_width":800, "y_width":800},
        zRange              = (-1,1),
        drawObjects         = drawObjects_,
        histModifications   = histModifications,
        canvasModifications = canvasModifications,
        copyIndexPHP        = True,
    )

    del corrhist

# impact plot
def plotImpacts():
    Results.getImpactPlot( expected=args.expected, printPNG=True, cores=args.cores )

if args.plotRegionPlot or args.cacheHistogram:
    plotRegions( sorted=True )
if args.plotCovMatrix:
    plotCovariance()
if args.plotCorrelations and args.postFit:
    plotCorrelations( systOnly=False )
    plotCorrelations( systOnly=True )
if args.plotImpacts and args.postFit:
    plotImpacts()
