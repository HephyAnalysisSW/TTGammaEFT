#!/usr/bin/env python

""" 
Get cardfile result plots
"""

# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys

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
labels = [ ( i, label ) for i, label in enumerate(Results.getBinLabels( labelFormater=lambda x:x.split(" "))) ]
if args.plotRegions:  labels = filter( lambda (i,(ch, lab, reg)): reg in args.plotRegions, labels )
if args.plotChannels: labels = filter( lambda (i,(ch, lab, reg)): ch in args.plotChannels, labels )

crName    = [ cr for i, (lep, reg, cr) in labels ]
plotBins  = [ i  for i, (lep, reg, cr) in labels ]

# Get formated labels out of binLabels
pTLabelFormater = lambda x: convLabel(x.split(" ")[1])
ptLabels        = Results.getBinLabels( labelFormater=pTLabelFormater ) 

labelFormater   = lambda x: ", ".join( [x.split(" ")[2], x.split(" ")[0].replace("mu","#mu").replace("tight","")] )
crLabel         = Results.getBinLabels( labelFormater=labelFormater )
nBins           = len(crLabel)


if "misIDPOI" in args.cardfile:
    processes = processesMisIDPOI.keys()
else:
    processes = [ cr for cr in args.cardfile.split("_") if (not args.plotRegions or (args.plotRegions and cr in args.plotRegions)) and cr in allRegions.keys() ]
    processes = allRegions[processes[0]]["processes"].keys()

###
### PLOTS
###

# region plot, sorted/not sorted, w/ or w/o +-1sigma changes in one nuisance
def plotRegions( sorted=True ):
    # get region histograms
    hists = Results.getRegionHistos( postFit=args.postFit, plotBins=plotBins, nuisances=args.plotNuisances, labelFormater=labelFormater )

    hists["data"].style        = styles.errorStyle( ROOT.kBlack )
    hists["data"].legendText   = "data"
    hists["data"].legendOption = "p"

    for h_key, h in hists.iteritems():
        if "total" in h_key or h_key not in processes: continue
        hists[h_key].legendText  = default_processes[h_key]["texName"]
        hists[h_key].style = styles.fillStyle( default_processes[h_key]["color"], errors=False )
        hists[h_key].LabelsOption("v","X")

    # some settings and things like e.g. uncertainty boxes
    minMax             = 0.3
    boxes, ratio_boxes = getUncertaintyBoxes( hists["total"], minMax )

    drawObjects_       = drawObjects( nBins=nBins, isData=(not args.expected), lumi_scale=lumi_scale, postFit=args.postFit, cardfile=args.substituteCard if args.substituteCard else args.cardfile, preliminary=args.preliminary )
    drawObjects_      += boxes 
    drawObjects_      += drawDivisions( crLabel, misIDPOI=("misIDPOI" in args.cardfile) ) 
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

    # get histo list
    plots, ratioHistos = Results.getRegionHistoList( hists, processes=processes, noData=False, sorted=sorted )

    addon = []
    if args.substituteCard: addon += ["sub"] + [ cr for cr in args.substituteCard.split("_") if cr not in args.cardfile.split("_") ]
    if args.plotNuisances:  addon += args.plotNuisances

    # plot name
    if   args.plotRegions and args.plotChannels: plotName = "_".join( ["regions"] + addon + args.plotRegions + args.plotChannels )
    elif args.plotRegions:                       plotName = "_".join( ["regions"] + addon + args.plotRegions )
    elif args.plotChannels:                      plotName = "_".join( ["regions"] + addon + args.plotChannels )
    else:                                        plotName = "_".join( ["regions"] + addon )

    plotting.draw(
        Plot.fromHisto( plotName,
                plots,
                texX = "",
                texY = "Number of Events",
        ),
        logX = False, logY = True, sorting = False, 
        plot_directory    = plotDirectory,
        legend            = [ (0.2, formatSettings(nBins)["legylower"], 0.9, 0.9), formatSettings(nBins)["legcolumns"] ],
        widths            = { "x_width":formatSettings(nBins)["padwidth"], "y_width":formatSettings(nBins)["padheight"], "y_ratio_width":formatSettings(nBins)["padratio"] },
        yRange            = ( 0.7, hists["total"].GetMaximum()*formatSettings(nBins)["heightFactor"] ),
        ratio             = { "yRange": ((1-minMax)*0.99, (1+minMax)*1.01), "texY":"Data/MC", "histos":ratioHistos, "drawObjects":ratio_boxes, "histModifications":ratioHistModifications },
        drawObjects       = drawObjects_,
        histModifications = histModifications,
        copyIndexPHP      = True,
        extensions = ["png"], # pdfs are quite large for sorted histograms (disco plot)
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

if args.plotRegionPlot:
    plotRegions( sorted=True )
if args.plotCovMatrix:
    plotCovariance()
if args.plotCorrelations and args.postFit:
    plotCorrelations( systOnly=False )
    plotCorrelations( systOnly=True )
if args.plotImpacts and args.postFit:
    plotImpacts()
