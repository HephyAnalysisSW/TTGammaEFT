#!/usr/bin/env python

import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy
from time import sleep

# RootTools
from RootTools.core.standard          import *
from RootTools.plot.helpers    import copyIndexPHP
# Internal Imports
from TTGammaEFT.Tools.user               import plot_directory

from TTGammaEFT.Analysis.Setup           import Setup
from TTGammaEFT.Analysis.EstimatorList   import EstimatorList
from TTGammaEFT.Analysis.SetupHelpers    import dilepChannels, lepChannels, allProcesses, allRegions, QCDTF_updates

# Analysis Imports
from Analysis.Tools.u_float              import u_float
import Analysis.Tools.syncer as syncer

loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']
CRChoices     = allRegions.keys()
ptBins  = [0, 45, 65, 80, 100, 120, -1]
etaBins = [0, 1.479, 1.7, 2.1, -1]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",          action="store",  default="INFO",             choices=loggerChoices,      help="Log level for logging")
argParser.add_argument("--plot_directory",    action="store",  default="102X_TTG_ppv22_v1")
argParser.add_argument("--year",              action="store",  default="2016",     type=str, choices=["2016", "2017", "2018", "RunII"], help="Which year?")
argParser.add_argument("--mode",              action="store",  default="e",      type=str, choices=["e", "mu"],        help="Which lepton selection?")
argParser.add_argument("--nJetCorrected",     action="store_true",                                                     help="Correct for nJet dependence?")
args = argParser.parse_args()

if args.year != "RunII": args.year = int(args.year)

# Logging
import Analysis.Tools.logger as logger
logger = logger.get_logger(   args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

extensions_ = ["pdf", "png", "root"]
plot_directory_ = os.path.join( plot_directory, 'QCDTFMCvsFit', str(args.year), args.plot_directory, args.mode+"_nJetCorr" if args.nJetCorrected else args.mode)
copyIndexPHP( plot_directory_ )

if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74
elif args.year == "RunII": lumi_scale = 35.92 + 41.53 + 59.74

parameters0b0p   = allRegions["WJets2"]["parameters"]
setup0b0p        = Setup( year=args.year, photonSelection=False, checkOnly=False)
estimators0b0p = EstimatorList( setup0b0p, processes=["QCD-DD"] )
estimate0b0p   = getattr(estimators0b0p, "QCD-DD")
setup0b0p      = setup0b0p.sysClone( parameters=parameters0b0p )
estimate0b0p.initCache(setup0b0p.defaultCacheDir())

parameters1b0p   = allRegions["TT2"]["parameters"]
setup1b0p        = Setup( year=args.year, photonSelection=False, checkOnly=False)
estimators1b0p = EstimatorList( setup1b0p, processes=["QCD-DD"] )
estimate1b0p   = getattr(estimators1b0p, "QCD-DD")
setup1b0p      = setup1b0p.sysClone( parameters=parameters1b0p )
estimate1b0p.initCache(setup1b0p.defaultCacheDir())

for nJet in [(2,2), (3,3), (4,-1)]:
    nJetLow, nJetHigh = nJet
    print nJetLow
#    print "0b"
#    estimate0b0p._nJetScaleFactor(args.mode, setup0b0p, evalForNJet=nJetLow, overwrite=True)
    print "1b"
    print estimate1b0p._nJetScaleFactor(args.mode, setup1b0p, evalForNJet=nJetLow, overwrite=True)

sys.exit()


cachedTF       = {}
cachedTF["0b"] = {}
cachedTF["1b"] = {}
cachedTF["0bMC"] = {}
cachedTF["1bMC"] = {}
for nJet in [(2,2), (3,3), (4,-1)]:
    nj = str(nJet[0])
    cachedTF["0b"][nj] = {}
    cachedTF["1b"][nj] = {}
    cachedTF["0bMC"][nj] = {}
    cachedTF["1bMC"][nj] = {}
    for i_eta, eta in enumerate(etaBins[:-1] + ["incl"]):
        etakey = str(eta)
        cachedTF["0b"][nj][etakey] = {}
        cachedTF["1b"][nj][etakey] = {}
        cachedTF["0bMC"][nj][etakey] = {}
        cachedTF["1bMC"][nj][etakey] = {}

if not args.nJetCorrected:
    func0b = estimate0b0p._nJetFitFunction(args.mode, setup0b0p, overwrite=False)
    func1b = estimate1b0p._nJetFitFunction(args.mode, setup1b0p, overwrite=False)

    line0b = ROOT.TLine( 2, func0b.Eval(1.5), 5, func0b.Eval(4.5) )
    line0b.SetLineWidth(3)
    line0b.SetLineColor(ROOT.kGreen-2)

    line1b = ROOT.TLine( 2, func1b.Eval(1.5), 5, func1b.Eval(4.5) )
    line1b.SetLineWidth(3)
    line1b.SetLineColor(ROOT.kGreen-2)


# get brute force all of them
for nJet in [(2,2), (3,3), (4,-1)]:
        nj = str(nJet[0])
        # inclusive tf
        nJetLow, nJetHigh = nJet
        etaLow, etaHigh   = 0, -1
        ptLow, ptHigh     = 0, -1

        QCDTF = copy.deepcopy(QCDTF_updates)
        QCDTF["CR"]["nJet"] = ( nJetLow, nJetHigh )
        QCDTF["SR"]["nJet"] = ( nJetLow, nJetHigh )

        # Transfer Factor, get the QCD histograms always in barrel regions
        QCDTF["CR"]["leptonEta"] = ( etaLow, etaHigh )
        QCDTF["CR"]["leptonPt"]  = ( ptLow,  ptHigh   )
        QCDTF["SR"]["leptonEta"] = ( etaLow, etaHigh )
        QCDTF["SR"]["leptonPt"]  = ( ptLow,  ptHigh   )

        qcdUpdate  = { "CR":QCDTF["CR"], "SR":QCDTF["SR"] }
        if args.nJetCorrected:
            nJetSF_0b0p = 1. / estimate0b0p._nJetScaleFactor(args.mode, setup0b0p, evalForNJet=nJetLow)
            nJetSF_1b0p = 1. / estimate1b0p._nJetScaleFactor(args.mode, setup1b0p, evalForNJet=nJetLow)
        else:
            nJetSF_0b0p = 1.
            nJetSF_1b0p = 1.

        cachedTF["0b"][nj]["incl"]["incl"] = estimate0b0p.cachedTransferFactor(args.mode, setup0b0p, qcdUpdates=qcdUpdate, checkOnly=False) * nJetSF_0b0p if nJetLow == 2 else u_float(-1,0)
        cachedTF["1b"][nj]["incl"]["incl"] = estimate1b0p.cachedTransferFactor(args.mode, setup1b0p, qcdUpdates=qcdUpdate, checkOnly=False) * nJetSF_1b0p if nJetLow == 2 else u_float(-1,0)
        cachedTF["0bMC"][nj]["incl"]["incl"] = estimate0b0p.cachedQCDMCTransferFactor(args.mode, setup0b0p, qcdUpdates=qcdUpdate, checkOnly=False) * nJetSF_0b0p
        cachedTF["1bMC"][nj]["incl"]["incl"] = estimate1b0p.cachedQCDMCTransferFactor(args.mode, setup1b0p, qcdUpdates=qcdUpdate, checkOnly=False) * nJetSF_1b0p
        # pt inclusive tf
        for i_eta, eta in enumerate(etaBins[:-1]):
            etakey = str(eta)
            etaLow, etaHigh   = eta, etaBins[i_eta+1]
            ptLow, ptHigh     = 0, -1

            QCDTF = copy.deepcopy(QCDTF_updates)
            QCDTF["CR"]["nJet"] = ( nJetLow, nJetHigh )
            QCDTF["SR"]["nJet"] = ( nJetLow, nJetHigh )

            # Transfer Factor, get the QCD histograms always in barrel regions
            QCDTF["CR"]["leptonEta"] = ( etaLow, etaHigh )
            QCDTF["CR"]["leptonPt"]  = ( ptLow,  ptHigh   )
            QCDTF["SR"]["leptonEta"] = ( etaLow, etaHigh )
            QCDTF["SR"]["leptonPt"]  = ( ptLow,  ptHigh   )

            qcdUpdate  = { "CR":QCDTF["CR"], "SR":QCDTF["SR"] }
            cachedTF["0b"][nj][etakey]["incl"] = estimate0b0p.cachedTransferFactor(args.mode, setup0b0p, qcdUpdates=qcdUpdate, checkOnly=False) * nJetSF_0b0p if nJetLow == 2 else u_float(-1,0)
            cachedTF["1b"][nj][etakey]["incl"] = estimate1b0p.cachedTransferFactor(args.mode, setup1b0p, qcdUpdates=qcdUpdate, checkOnly=False) * nJetSF_1b0p if nJetLow == 2 else u_float(-1,0)
            cachedTF["0bMC"][nj][etakey]["incl"] = estimate0b0p.cachedQCDMCTransferFactor(args.mode, setup0b0p, qcdUpdates=qcdUpdate, checkOnly=False) * nJetSF_0b0p
            cachedTF["1bMC"][nj][etakey]["incl"] = estimate1b0p.cachedQCDMCTransferFactor(args.mode, setup1b0p, qcdUpdates=qcdUpdate, checkOnly=False) * nJetSF_1b0p

        for i_pt, pt in enumerate(ptBins[:-1]):
            # eta inclusive tf
            ptkey = str(pt)
            etaLow, etaHigh   = 0, -1
            ptLow, ptHigh     = pt,  ptBins[i_pt+1]

            QCDTF = copy.deepcopy(QCDTF_updates)
            QCDTF["CR"]["nJet"] = ( nJetLow, nJetHigh )
            QCDTF["SR"]["nJet"] = ( nJetLow, nJetHigh )

            # Transfer Factor, get the QCD histograms always in barrel regions
            QCDTF["CR"]["leptonEta"] = ( etaLow, etaHigh )
            QCDTF["CR"]["leptonPt"]  = ( ptLow,  ptHigh   )
            QCDTF["SR"]["leptonEta"] = ( etaLow, etaHigh )
            QCDTF["SR"]["leptonPt"]  = ( ptLow,  ptHigh   )

            qcdUpdate  = { "CR":QCDTF["CR"], "SR":QCDTF["SR"] }
            cachedTF["0b"][nj]["incl"][ptkey] = estimate0b0p.cachedTransferFactor(args.mode, setup0b0p, qcdUpdates=qcdUpdate, checkOnly=False) * nJetSF_0b0p if nJetLow == 2 else u_float(-1,0)
            cachedTF["1b"][nj]["incl"][ptkey] = estimate1b0p.cachedTransferFactor(args.mode, setup1b0p, qcdUpdates=qcdUpdate, checkOnly=False) * nJetSF_1b0p if nJetLow == 2 else u_float(-1,0)
            cachedTF["0bMC"][nj]["incl"][ptkey] = estimate0b0p.cachedQCDMCTransferFactor(args.mode, setup0b0p, qcdUpdates=qcdUpdate, checkOnly=False) * nJetSF_0b0p
            cachedTF["1bMC"][nj]["incl"][ptkey] = estimate1b0p.cachedQCDMCTransferFactor(args.mode, setup1b0p, qcdUpdates=qcdUpdate, checkOnly=False) * nJetSF_1b0p

            for i_eta, eta in enumerate(etaBins[:-1]):
                etakey = str(eta)
                etaLow, etaHigh   = eta, etaBins[i_eta+1]
                ptLow, ptHigh     = pt,  ptBins[i_pt+1]

                QCDTF = copy.deepcopy(QCDTF_updates)
                QCDTF["CR"]["nJet"] = ( nJetLow, nJetHigh )
                QCDTF["SR"]["nJet"] = ( nJetLow, nJetHigh )

                # Transfer Factor, get the QCD histograms always in barrel regions
                QCDTF["CR"]["leptonEta"] = ( etaLow, etaHigh )
                QCDTF["CR"]["leptonPt"]  = ( ptLow,  ptHigh   )
                QCDTF["SR"]["leptonEta"] = ( etaLow, etaHigh )
                QCDTF["SR"]["leptonPt"]  = ( ptLow,  ptHigh   )

                qcdUpdate  = { "CR":QCDTF["CR"], "SR":QCDTF["SR"] }
                cachedTF["0b"][nj][etakey][ptkey] = estimate0b0p.cachedTransferFactor(args.mode, setup0b0p, qcdUpdates=qcdUpdate, checkOnly=False) * nJetSF_0b0p if nJetLow == 2 else u_float(-1,0)
                cachedTF["1b"][nj][etakey][ptkey] = estimate1b0p.cachedTransferFactor(args.mode, setup1b0p, qcdUpdates=qcdUpdate, checkOnly=False) * nJetSF_1b0p if nJetLow == 2 else u_float(-1,0)
                cachedTF["0bMC"][nj][etakey][ptkey] = estimate0b0p.cachedQCDMCTransferFactor(args.mode, setup0b0p, qcdUpdates=qcdUpdate, checkOnly=False) * nJetSF_0b0p
                cachedTF["1bMC"][nj][etakey][ptkey] = estimate1b0p.cachedQCDMCTransferFactor(args.mode, setup1b0p, qcdUpdates=qcdUpdate, checkOnly=False) * nJetSF_1b0p



for x in cachedTF["0b"]["2"].keys():
    for y in cachedTF["0b"]["2"][x].keys():
        print args.year, args.mode, "0b", "2jet", x, y, cachedTF["0b"]["2"][x][y]

print
for x in cachedTF["1b"]["2"].keys():
    for y in cachedTF["1b"]["2"][x].keys():
        print args.year, args.mode, "1b", "2jet", x, y, cachedTF["1b"]["2"][x][y]

sys.exit()

# Text on the plots
def drawObjects( lumi_scale, btags ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    sel = ""
    if btags == 0: sel = "0#gamma0b"
    if btags == 1: sel = "0#gamma1b"
    lines = [
      (0.15, 0.95, 'CMS #bf{#it{Preliminary}} (%s)'%sel),
      (0.65, 0.95, '%3.1f fb{}^{-1} (13 TeV)' % lumi_scale),
    ]
    return [tex.DrawLatex(*l) for l in lines]

def legMod( legend ):
#    nullhist = ROOT.TH1F("null","null", 3, 2, 5)
#    for j in range(1,7):
#       nullhist.SetBinContent( j, 100 )
#    nullhist.style = styles.lineStyle( ROOT.kGreen-2, width=3, errors=False )
#    nullhist.legendText = "lin. fit for N_{jet} corr."
    legend.AddEntry(line0b, "lin. fit for N_{jet} corr.", "l")


def drawPlots( plot, btags ):

    maxY = max( [ h.GetMaximum() for hList in plot.histos for h in hList ] )

    obj = []
    legMods = []
    if plot.name.count("incl") == 2 and not args.nJetCorrected:
        obj += [line0b if btags == 0 else line1b]
        legMods += [legMod]

    plotting.draw( plot,
                   plot_directory = plot_directory_,
                   extensions = extensions_,
                   logX = False, logY = False, sorting = False,
                   yRange = (0.0, maxY*2.5),
                   legend = [(0.2,0.7,0.6,0.88), 1],
                   drawObjects = drawObjects( lumi_scale, btags ) + obj,
                   legendModifications = legMods,
                   copyIndexPHP = True,
                   redrawHistos = True,
                 )

color = [ ROOT.kAzure-3, ROOT.kRed-3, ROOT.kGreen-2, ROOT.kOrange ]
hists       = {}
hists2D     = {}
legAddon = " (corr)" if args.nJetCorrected else ""
for i_eta, eta in enumerate(etaBins[:-1] + ["incl"]):
    etakey = str(eta)
    for i_pt, pt in enumerate(ptBins[:-1] + ["incl"]):
        ptkey = str(pt)
        etaLow, etaHigh   = ("%.2f"%eta, "%.2f"%etaBins[i_eta+1]) if eta != "incl" else ("incl", None)
        ptLow, ptHigh     = (str(pt),  str(ptBins[i_pt+1])) if pt != "incl" else ("incl", None)

        for b in range(2):
            hists["%ib"%b]   = {}
            hists["%ib"%b]["nJ"] = ROOT.TH1F("hist%ib_nJ"%(b), "hist%ib_nJ"%(b), 3, 2, 5)
            hists["%ib"%b]["nJ"].style = styles.errorStyle( color[0], width=3 )
            hists["%ib"%b]["nJ"].legendText = "fitted TF, N_{b-jets}=%i%s"%(b,legAddon)
            hists["%ib"%b]["nJMC"] = ROOT.TH1F("hist%ib_nJMC"%(b), "hist%ib_nJMC"%(b), 3, 2, 5)
            hists["%ib"%b]["nJMC"].style = styles.errorStyle( color[1], width=3 )
            hists["%ib"%b]["nJMC"].legendText = "Multijet MC TF, N_{b-jets}=%i%s"%(b,legAddon)

            addon = args.mode.replace("mu", "#mu")
#            addon += "#geq1 b-tag" if b==1 else "0 b-tag"
            if pt != "incl":
                addon += ", "
                addon += "%s #leq p_{T} < %s GeV"%(ptLow, ptHigh) if ptHigh and float(ptHigh) >= 0 else "p_{T} #geq %s GeV"%ptLow
            if eta != "incl":
                addon += ", "
                addon += "%s #leq |#eta| < %s"%(etaLow, etaHigh) if etaHigh and float(etaHigh) >= 0 else "|#eta| #geq %s"%etaLow

            hists["%ib"%b]["nJUsed"] = ROOT.TH1F("hist%ib_nJUsed"%(b), "hist%ib_nJUsed"%(b), 3, 2, 5)
            hists["%ib"%b]["nJUsed"].style = styles.lineStyle( ROOT.kBlack, width=3, errors=False )
            hists["%ib"%b]["nJUsed"].legendText = "used TF (%s)"%addon

        for b in range(2):
                for j in range(2,5):
                    hists["%ib"%b]["nJ"].SetBinContent( j-1, cachedTF["%ib"%(b)][str(j)][etakey][ptkey].val   )
                    hists["%ib"%b]["nJ"].SetBinError(   j-1, cachedTF["%ib"%(b)][str(j)][etakey][ptkey].sigma )
                    lab = str(j) if j != 4 else "#geq4"
                    hists["%ib"%b]["nJ"].GetXaxis().SetBinLabel( j-1, lab )

                    hists["%ib"%b]["nJMC"].SetBinContent( j-1, cachedTF["%ibMC"%(b)][str(j)][etakey][ptkey].val   )
                    hists["%ib"%b]["nJMC"].SetBinError(   j-1, cachedTF["%ibMC"%(b)][str(j)][etakey][ptkey].sigma )
                    lab = str(j) if j != 4 else "#geq4"
                    hists["%ib"%b]["nJMC"].GetXaxis().SetBinLabel( j-1, lab )

                    hists["%ib"%b]["nJUsed"].SetBinContent( j-1, cachedTF["%ib"%(b)]["2"][etakey][ptkey].val   )
                    hists["%ib"%b]["nJUsed"].SetBinError(   j-1, cachedTF["%ib"%(b)]["2"][etakey][ptkey].sigma )
                    hists["%ib"%b]["nJUsed"].GetXaxis().SetBinLabel( j-1, lab )

        plots       = {}
        plots2D     = {}
        for b in range(2):
            label = "TT" if b==1 else "WJets"
            label += "_pT%sTo%s"%(ptLow, ptHigh) if ptHigh and float(ptHigh) >= 0 else "_pT%s"%ptLow
            label += "_eta%sTo%s"%(etaLow, etaHigh) if etaHigh and float(etaHigh) >= 0 else "_eta%s"%etaLow
            plots["%ib"%b]   = {}
            plots["%ib"%b]["nJ"] = Plot.fromHisto( "QCDTFnJet_"+label,    [[hists["%ib"%b]["nJUsed"]]] + [[hists["%ib"%b]["nJ"]]]  + [[hists["%ib"%b]["nJMC"]]], texX="N_{jets}", texY="Multijet Transferfactor" )

        for b in range(2):
            drawPlots( plots["%ib"%b]["nJ"], b )
