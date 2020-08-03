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
argParser.add_argument("--blinded",              action="store_true")
argParser.add_argument("--misIDPOI",             action="store_true",                            help="Use misID as POI")
argParser.add_argument("--ttPOI",             action="store_true",                            help="Use tt as POI")
argParser.add_argument("--wJetsPOI",             action="store_true",                            help="Use w+jets as POI")
argParser.add_argument("--wgPOI",             action="store_true",                            help="Use wgamma as POI")
argParser.add_argument("--dyPOI",             action="store_true",                            help="Use dy as POI")
argParser.add_argument("--overwrite",            action="store_true",                            help="Overwrite existing output files, bool flag set to True  if used")
argParser.add_argument("--postFit",              action="store_true",                            help="Apply pulls?")
argParser.add_argument("--expected",             action="store_true",                            help="Run expected?")
argParser.add_argument("--preliminary",          action="store_true",                            help="Run expected?")
#argParser.add_argument("--systOnly",             action="store_true",                            help="correlation matrix with systematics only?")
argParser.add_argument("--year",                 action="store",      type=str, default="2016",    help="Which year?")
argParser.add_argument("--carddir",              action='store',                default='limits/cardFiles/defaultSetup/observed',      help="which cardfile directory?")
argParser.add_argument("--cardfile",             action='store',                default='',      help="which cardfile?")
argParser.add_argument("--substituteCard",       action='store',                default=None,    help="which cardfile to substitute the plot with?")
argParser.add_argument("--plotRegions",          action='store', nargs="*",     default=None,    help="which regions to plot?")
argParser.add_argument("--plotChannels",         action='store', nargs="*",     default=None,    help="which regions to plot?")
argParser.add_argument("--plotNuisances",        action='store', nargs="*",     default=None,    help="plot specific nuisances?")
argParser.add_argument("--cores",                action="store", default=1,               type=int,                               help="Run on n cores in parallel")
argParser.add_argument("--linTest",              action="store", default=1,               type=float,                               help="factor for lintest")
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

if args.year != "combined": args.year = int(args.year)
# fix label (change later)
args.preliminary = True
# make sure the list is always in the same order
if args.plotNuisances: args.plotNuisances.sort()

if args.misIDPOI: default_processes = processesMisIDPOI
if args.ttPOI: default_processes = processesTTPOI
if args.wJetsPOI: default_processes = processesWJetsPOI
if args.dyPOI: default_processes = processesDYPOI
if args.wgPOI: default_processes = processesWGPOI

if args.plotChannels and "all" in args.plotChannels: args.plotChannels += ["e","mu"]
if args.plotChannels and "e"   in args.plotChannels: args.plotChannels += ["eetight"]
if args.plotChannels and "mu"  in args.plotChannels: args.plotChannels += ["mumutight"]

if   args.year == 2016: lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74
elif args.year == "combined": lumi_scale = 35.92 + 41.53 + 59.74

dirName  = "_".join( [ item for item in args.cardfile.split("_") if not (item.startswith("add") or item == "incl") ] )
add      = [ item for item in args.cardfile.split("_") if (item.startswith("add") or item == "incl")  ]
add.sort()
if args.expected: add += ["expected"]
if args.linTest != 1: add += ["linTest"+str(args.linTest)]
fit      = "_".join( ["postFit" if args.postFit else "preFit"] + add )

plotDirectory = os.path.join(plot_directory, "fit", str(args.year), fit, dirName)
cardFile      = os.path.join( cache_directory, "analysis", str(args.year) if args.year != "combined" else "COMBINED", args.carddir, args.cardfile+".txt" )
logger.info("Plotting from cardfile %s"%cardFile)

# replace the combineResults object by the substituted card object
Results = CombineResults( cardFile=cardFile, plotDirectory=plotDirectory, year=args.year, bkgOnly=args.bkgOnly, isSearch=False )
#print Results.fitResult

#cov = Results.getCovarianceHisto(postFit=True)
#for i in range( cov.GetNbinsX() ):
#    for j in range( cov.GetNbinsY() ):
#        print i+1, j+1, cov.GetBinContent(i+1,j+1)
#sys.exit()
#Results.runFitDiagnostics()
#print Results.getUncertaintiesFromTxtCard( postFit=False )["Bin0"]["Bin39"]["DY_misID"]
#sys.exit()

# add all systematics histograms
allNuisances  = Results.getNuisancesList( addRateParameter=args.postFit )
#allNuisances  = Results.getNuisancesList( addRateParameter=False )
plotNuisances = allNuisances if args.plotNuisances and args.plotNuisances[0] == "total" else args.plotNuisances

print allNuisances

if args.substituteCard:
    rebinnedCardFile = os.path.join( cache_directory, "analysis", str(args.year) if args.year != "combined" else "COMBINED", args.carddir, args.substituteCard+".txt" )

#    subCardFile = Results.createRebinnedResults( rebinnedCardFile )
    subCardFile = "/scratch/lukas.lechner/TTGammaEFT/cache/analysis/2016/limits/cardFiles/defaultSetup/observed/SR3pM3_VG3p_misDY3p_addDYSF/SR3pdRUnfold_addDYSF.txt"
    del Results
    Results     = CombineResults( cardFile=subCardFile, plotDirectory=plotDirectory, year=args.year, bkgOnly=args.bkgOnly, isSearch=False, rebinnedCardFile=rebinnedCardFile )

# get list of labels
if args.plotRegions:  labels = filter( lambda (i,(year, ch, lab, reg)): reg in args.plotRegions, labels )
if args.plotChannels: labels = filter( lambda (i,(year, ch, lab, reg)): ch in args.plotChannels, labels )

labelFormater   = lambda x: ", ".join( [x.split(" ")[3], x.split(" ")[1].replace("mu","#mu").replace("tight","")] )
labels = [ ( i, label ) for i, label in enumerate(Results.getBinLabels( labelFormater=lambda x:x.split(" "))[Results.channels[0]])]
print labels
crName    = [ cr for i, (year, lep, reg, cr) in labels ]
plotBins  = [ i  for i, (year, lep, reg, cr) in labels ]
crLabel   = map( lambda (i,(year, ch, lab, reg)): ", ".join( [ reg, ch.replace("mu","#mu").replace("tight","") ] ), labels )
ptLabels  = map( lambda (i,(year, ch, lab, reg)): convLabel(lab), labels )
#print ptLabels
#sys.exit()
nBins     = len(crLabel) #int(len(crLabel)/3.) if args.year == "combined" else len(crLabel)

if "misIDPOI" in args.cardfile:
    processes = processesMisIDPOI.keys()
else:
    card = args.substituteCard if args.substituteCard else args.cardfile
    processes = [ cr for cr in card.split("_") if (not args.plotRegions or (args.plotRegions and cr in args.plotRegions)) and cr in allRegions.keys() ]
    processes = allRegions[processes[0]]["processes"].keys()

###
### PLOTS
###

def replaceHistoBinning( hists ):
        subCard = args.substituteCard.split("_")
        reg = allRegions[subCard[0]]["regions"]
        thresh = [ r.vals.values()[0][0] for r in reg ]
        bins, min, max = len(reg), reg[0].vals.values()[0][0], reg[-1].vals.values()[0][1]
        if max == -999:
            max = thresh[-1] + 2*(thresh[-1] - thresh[-2])
            thresh += [max]
        else:
            thresh += [ reg[-1].vals.values()[0][1] ]
        xLabel = reg[0].vals.keys()[0]
        if "PhotonGood0" in xLabel or "PhotonNoChgIsoNoSieie0" in xLabel or xLabel in ["ltight0GammaNoSieieNoChgIsodPhi", "ltight0GammaNoSieieNoChgIsodR"]:
            if xLabel.endswith("_pt"):  xLabel = "p_{T}(#gamma) [GeV]"
            if xLabel.endswith("_eta"): xLabel = "#eta(#gamma)"
            if xLabel.endswith("dR"): xLabel = "#DeltaR(#gamma,l)"
            if xLabel.endswith("dPhi"): xLabel = "#Delta#phi(#gamma,l)"

        differential = True
        ch = subCard[-1]
        for h_key, h in hists.iteritems():
            if isinstance( h, dict ):
                h_sub_up = ROOT.TH1F(h["up"].GetName(), h["up"].GetName(), bins, array.array('d', thresh) )
                h_sub_down = ROOT.TH1F(h["down"].GetName(), h["down"].GetName(), bins, array.array('d', thresh) )
                for i in range(h_sub_up.GetNbinsX()):
                    h_sub_up.SetBinContent( i+1, h["up"].GetBinContent(i+1))
                    h_sub_up.SetBinError( i+1, h["up"].GetBinError(i+1))
                    h_sub_down.SetBinContent( i+1, h["down"].GetBinContent(i+1))
                    h_sub_down.SetBinError( i+1, h["down"].GetBinError(i+1))
                h_sub_up.legendText = h["up"].legendText
                h_sub_up.style = h["up"].style
                h_sub_down.legendText = h["down"].legendText
                h_sub_down.style = h["down"].style
                hists[h_key] = {"up":h_sub_up,"down":h_sub_down}
                del h_sub_up
                del h_sub_down
            else:
                h_sub = ROOT.TH1F(h.GetName(), h.GetName(), bins, array.array('d', thresh) )#min, max )
                for i in range(h_sub.GetNbinsX()):
                    h_sub.SetBinContent( i+1, h.GetBinContent(i+1))
                    h_sub.SetBinError( i+1, h.GetBinError(i+1))
                hists[h_key] = h_sub.Clone(h_key)
                del h_sub
        return hists

# region plot, sorted/not sorted, w/ or w/o +-1sigma changes in one nuisance
def plotRegions( sorted=True ):
    # get region histograms
    if args.year == "combined":
        hists_tmp = Results.getRegionHistos( postFit=args.postFit, plotBins=plotBins, nuisances=plotNuisances, addStatOnlyHistos=True, bkgSubstracted=args.bkgSubstracted, labelFormater=labelFormater )
        for i, dir in enumerate(Results.channels):
            if i == 0:
                hists = {key:hist.Clone(str(i)+dir+key) for key, hist in hists_tmp[dir].iteritems() if not args.plotNuisances or key not in plotNuisances} #copy.deepcopy(hists_tmp)
                if args.plotNuisances:
                    for n in plotNuisances:
                        hists.update( { n:{"up":hists_tmp[dir][n]["up"].Clone(str(i)+dir+n+"up"), "down":copy.deepcopy(hists_tmp[dir][n]["down"].Clone(str(i)+dir+n+"down"))} } )
                        hists[n]["up"].legendText = hists_tmp[dir][n]["up"].legendText
                        hists[n]["up"].style      = hists_tmp[dir][n]["up"].style
                        hists[n]["down"].legendText = hists_tmp[dir][n]["down"].legendText
                        hists[n]["down"].style      = hists_tmp[dir][n]["down"].style
            else:
               for key, hist in hists_tmp[dir].iteritems():
                    if args.plotNuisances and key in plotNuisances:
                        hists[key]["up"].Add(hist["up"].Clone(str(i)+dir+key+"up"))
                        hists[key]["down"].Add(hist["down"].Clone(str(i)+dir+key+"down"))
                    else:
                        hists[key].Add(hist.Clone(str(i)+dir+key))

    else:
        hists = Results.getRegionHistos( postFit=args.postFit, plotBins=plotBins, nuisances=plotNuisances, addStatOnlyHistos=True, bkgSubstracted=args.bkgSubstracted, labelFormater=labelFormater )["Bin0"]

    if args.plotNuisances and args.plotNuisances[0] == "total":

        hists["totalUnc"]         = Results.sumNuisanceHistos(hists, addStatUnc=True, postFit=args.postFit)
        for i_n, ni in enumerate(plotNuisances):
            del hists[ni]

        error = []
        for i in range( hists["totalUnc"]["up"].GetNbinsX() ):
            print i+1, hists["totalUnc"]["relUp"].GetBinContent(i+1) - hists["total"].GetBinError( i+1 ) > 0, abs(hists["totalUnc"]["relUp"].GetBinContent(i+1) - hists["total"].GetBinError( i+1 )), abs(hists["totalUnc"]["relUp"].GetBinContent(i+1) - hists["total"].GetBinError( i+1 )) / hists["total"].GetBinError(i+1)
            error.append( abs(hists["totalUnc"]["relUp"].GetBinContent(i+1) - hists["total"].GetBinError( i+1 )) / hists["total"].GetBinError(i+1) )
        global max
        print "Max difference: %f, Mean difference: %f"%(max(error), np.mean(error))

    differential = False
    ch = "all"
    xLabel = ""
    if args.substituteCard: subCard = args.substituteCard.split("_")
    if args.bkgSubstracted and args.substituteCard:
        hists = replaceHistoBinning( hists )
        differential = True
        ch = subCard[-1]

    minMax = 0.29 #0.19 if args.postFit else 0.9
    if args.bkgSubstracted:
        minMax = 0.29 #0.19 if args.postFit else 0.9
        ratioCenter = None
        boxes,     ratio_boxes     = getErrorBoxes(   copy.copy(hists["signal"]), minMax, lineColor=ROOT.kOrange-2, fillColor=ROOT.kOrange-2, hashcode=1001, ratioCenter=ratioCenter )
        boxes_stat, ratio_boxes_stat = getErrorBoxes( copy.copy(hists["signal_stat"]), minMax, lineColor=ROOT.kAzure-3, fillColor=ROOT.kAzure-3, hashcode=1001, ratioCenter=ratioCenter )
    else:
        boxes,     ratio_boxes       = getUncertaintyBoxes( copy.copy(hists["total"]), minMax, lineColor=ROOT.kGray+3, fillColor=ROOT.kGray+3, hashcode=formatSettings(nBins)["hashcode"] )
        if args.postFit:
            boxes_stat, ratio_boxes_stat = getUncertaintyBoxes( copy.copy(hists["total_stat"]), minMax, lineColor=ROOT.kAzure-3, fillColor=ROOT.kAzure-3, hashcode=1001 )

    hists["data"].style        = styles.errorStyle( ROOT.kBlack )
    hists["data"].legendText   = "data" if not args.bkgSubstracted else "bkg-sub. data (#color[61]{stat}, #color[92]{total} error, %s)"%(ch.replace("mu","#mu") if ch != "all" else "e+#mu")
    hists["data"].legendOption = "p" if args.bkgSubstracted else "p"

    if args.bkgSubstracted:
        hists["signal"].style      = styles.lineStyle( ROOT.kOrange+7, width=2, errors=False )
        hists["signal"].legendText = "tt#gamma SM prediction"# (detector level)"

    else:
        for h_key, h in hists.iteritems():
            if "total" in h_key or h_key not in processes: continue
            hists[h_key].legendText  = default_processes[h_key]["texName"]
            hists[h_key].style = styles.fillStyle( default_processes[h_key]["color"], errors=False )
            hists[h_key].LabelsOption("v","X")


    # some settings and things like e.g. uncertainty boxes
    drawObjects_       = drawObjects( nBins=nBins, isData=(not args.expected), lumi_scale=lumi_scale, postFit=args.postFit, cardfile=args.substituteCard if args.substituteCard else args.cardfile, preliminary=args.preliminary )
    drawObjects_      += boxes 
    if args.postFit:
        drawObjects_      += boxes_stat
#    if args.bkgSubstracted: drawObjects_ += boxes_stat
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

    addon = []
    if args.bkgSubstracted: addon += ["bkgSub"]
    if args.substituteCard: addon += ["rebinned"] + [ cr for cr in subCard ]#if cr not in args.cardfile.split("_") ]
    if args.plotNuisances:  addon += args.plotNuisances

    # plot name
    if   args.plotRegions and args.plotChannels: plotName = "_".join( ["regions"] + addon + args.plotRegions + [ch for ch in args.plotChannels if not "tight" in ch] )
    elif args.plotRegions:                       plotName = "_".join( ["regions"] + addon + args.plotRegions )
    elif args.plotChannels:                      plotName = "_".join( ["regions"] + addon + [ch for ch in args.plotChannels if not "tight" in ch] )
    else:                                        plotName = "_".join( ["regions"] + addon )

    if args.cacheHistogram:
        from Analysis.Tools.MergingDirDB      import MergingDirDB
        from TTGammaEFT.Tools.user            import cache_directory
        cache_dir = os.path.join(cache_directory, "unfolding", str(args.year), "bkgSubstracted", "expected" if args.expected else "observed")
        dirDB = MergingDirDB(cache_dir)
        if not dirDB: raise
        addon = []
        if args.plotRegions:  addon += args.plotRegions
        if args.plotChannels: addon += args.plotChannels
        systematics = [ sys for sys in Results.getPulls( postFit=True ).keys() if not "prop" in sys ]
        # data histogram
        name = ["bkgSubtracted", args.substituteCard, args.cardfile, "data"]
        print "_".join(name+addon)
        dirDB.add( "_".join(name+addon), hists["data"], overwrite=True )
        # bkg substracted total histogram (signal) with total error
        name = ["bkgSubtracted", args.substituteCard, args.cardfile, "signal"]
        print "_".join(name+addon)
        dirDB.add( "_".join(name+addon), hists["signal"], overwrite=True )
        # bkg substracted total histogram (signal) with stat error
        name = ["bkgSubtracted", args.substituteCard, args.cardfile, "signal_stat"]
        print "_".join(name+addon)
        dirDB.add( "_".join(name+addon), hists["signal_stat"], overwrite=True )

    # get histo list
    plots, ratioHistos = Results.getRegionHistoList( hists, processes=processes, noData=False, sorted=sorted and not args.bkgSubstracted, bkgSubstracted=args.bkgSubstracted, directory="dc_2016" if args.year=="combined" else "Bin0" )
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
            ratio             = { "yRange": (1-minMax, 1+minMax), "texY":"Data/Pred." if args.bkgSubstracted else "Data/MC", "histos":ratioHistos, "drawObjects":ratio_boxes + ratio_boxes_stat if args.postFit else ratio_boxes, "histModifications":ratioHistModifications },
            drawObjects       = drawObjects_ if not differential else drawObjectsDiff(lumi_scale) + boxes + boxes_stat,
            histModifications = histModifications,
            copyIndexPHP      = True,
            extensions        = ["png", "pdf", "root"] if args.bkgSubstracted else ["png"], # pdfs are quite large for sorted histograms (disco plot)
            redrawHistos      = args.bkgSubstracted,
        )

    del hists

# covariance matrix 2D plot
def plotCovariance():
    # get the results
    covhist = Results.getCovarianceHisto( postFit=args.postFit, directory="Bin0", labelFormater=labelFormater, normalize=True )

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
def plotCorrelations():
    # get the results
    corrhist     = Results.getCorrelationHisto()
    drawObjects_ = drawCoObjects( lumi_scale=lumi_scale, bkgOnly=args.bkgOnly, postFit=args.postFit, incl=("incl" in args.cardfile), preliminary=args.preliminary )

    addon = ""
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
    plotCorrelations()
if args.plotImpacts and args.postFit:
    plotImpacts()
