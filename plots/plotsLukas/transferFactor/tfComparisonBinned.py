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
args = argParser.parse_args()

if args.year != "RunII": args.year = int(args.year)

# Logging
import Analysis.Tools.logger as logger
logger = logger.get_logger(   args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

extensions_ = ["pdf", "png", "root"]
plot_directory_ = os.path.join( plot_directory, 'QCDTFComp', str(args.year), args.plot_directory, args.mode )
copyIndexPHP( plot_directory_ )

if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74
elif args.year == "RunII": lumi_scale = 35.92 + 41.53 + 59.74

parameters0b0p   = allRegions["WJets2"]["parameters"]
setup0b0p        = Setup( year=args.year, photonSelection=False, checkOnly=True)
estimators0b0p = EstimatorList( setup0b0p, processes=["QCD-DD"] )
estimate0b0p   = getattr(estimators0b0p, "QCD-DD")
setup0b0p      = setup0b0p.sysClone( parameters=parameters0b0p )
estimate0b0p.initCache(setup0b0p.defaultCacheDir())

parameters1b0p   = allRegions["TT2"]["parameters"]
setup1b0p        = Setup( year=args.year, photonSelection=False, checkOnly=True)
estimators1b0p = EstimatorList( setup1b0p, processes=["QCD-DD"] )
estimate1b0p   = getattr(estimators1b0p, "QCD-DD")
setup1b0p      = setup1b0p.sysClone( parameters=parameters1b0p )
estimate1b0p.initCache(setup1b0p.defaultCacheDir())

cachedTF       = {}
cachedTF["0b0p"] = {}
cachedTF["1b0p"] = {}
cachedTF["0b1p"] = {}
cachedTF["1b1p"] = {}
for nJet in [(2,2), (3,3), (4,-1)]:
    nj = str(nJet[0])
    cachedTF["0b0p"][nj] = {}
    cachedTF["1b0p"][nj] = {}
    cachedTF["0b1p"][nj] = {}
    cachedTF["1b1p"][nj] = {}
    for i_eta, eta in enumerate(etaBins[:-1] + ["incl"]):
        etakey = str(eta)
        cachedTF["0b0p"][nj][etakey] = {}
        cachedTF["1b0p"][nj][etakey] = {}
        cachedTF["0b1p"][nj][etakey] = {}
        cachedTF["1b1p"][nj][etakey] = {}

# get brute force all of them
for nP in [0,1]:
    for nJet in [(2,2), (3,3), (4,-1)]:
        nj = str(nJet[0])
        # inclusive tf
        nJetLow, nJetHigh = nJet
        etaLow, etaHigh   = 0, -1
        ptLow, ptHigh     = 0, -1

        QCDTF = copy.deepcopy(QCDTF_updates)
        QCDTF["CR"]["nJet"] = ( nJetLow, nJetHigh )
        QCDTF["SR"]["nJet"] = ( nJetLow, nJetHigh )
        QCDTF["CR"]["nPhoton"] = ( nP, nP )
        QCDTF["SR"]["nPhoton"] = ( nP, nP )
        if nP > 0:
            QCDTF["CR"]["zWindow"] = "offZeg"
            QCDTF["SR"]["zWindow"] = "offZeg"
            QCDTF["CR"]["addMisIDSF"] = True
            QCDTF["SR"]["addMisIDSF"] = True

        # Transfer Factor, get the QCD histograms always in barrel regions
        QCDTF["CR"]["leptonEta"] = ( etaLow, etaHigh )
        QCDTF["CR"]["leptonPt"]  = ( ptLow,  ptHigh   )
        QCDTF["SR"]["leptonEta"] = ( etaLow, etaHigh )
        QCDTF["SR"]["leptonPt"]  = ( ptLow,  ptHigh   )

        qcdUpdate  = { "CR":QCDTF["CR"], "SR":QCDTF["SR"] }
        cachedTF["0b%ip"%nP][nj]["incl"]["incl"] = estimate0b0p.cachedTransferFactor(args.mode, setup0b0p, qcdUpdates=qcdUpdate, checkOnly=True)
        cachedTF["1b%ip"%nP][nj]["incl"]["incl"] = estimate1b0p.cachedTransferFactor(args.mode, setup1b0p, qcdUpdates=qcdUpdate, checkOnly=True)
        # pt inclusive tf
        for i_eta, eta in enumerate(etaBins[:-1]):
            etakey = str(eta)
            etaLow, etaHigh   = eta, etaBins[i_eta+1]
            ptLow, ptHigh     = 0, -1

            QCDTF = copy.deepcopy(QCDTF_updates)
            QCDTF["CR"]["nJet"] = ( nJetLow, nJetHigh )
            QCDTF["SR"]["nJet"] = ( nJetLow, nJetHigh )
            QCDTF["CR"]["nPhoton"] = ( nP, nP )
            QCDTF["SR"]["nPhoton"] = ( nP, nP )
            if nP > 0:
                QCDTF["CR"]["zWindow"] = "offZeg"
                QCDTF["SR"]["zWindow"] = "offZeg"
                QCDTF["CR"]["addMisIDSF"] = True
                QCDTF["SR"]["addMisIDSF"] = True

            # Transfer Factor, get the QCD histograms always in barrel regions
            QCDTF["CR"]["leptonEta"] = ( etaLow, etaHigh )
            QCDTF["CR"]["leptonPt"]  = ( ptLow,  ptHigh   )
            QCDTF["SR"]["leptonEta"] = ( etaLow, etaHigh )
            QCDTF["SR"]["leptonPt"]  = ( ptLow,  ptHigh   )

            qcdUpdate  = { "CR":QCDTF["CR"], "SR":QCDTF["SR"] }
            cachedTF["0b%ip"%nP][nj][etakey]["incl"] = estimate0b0p.cachedTransferFactor(args.mode, setup0b0p, qcdUpdates=qcdUpdate, checkOnly=True)
            cachedTF["1b%ip"%nP][nj][etakey]["incl"] = estimate1b0p.cachedTransferFactor(args.mode, setup1b0p, qcdUpdates=qcdUpdate, checkOnly=True)

        for i_pt, pt in enumerate(ptBins[:-1]):
            # eta inclusive tf
            ptkey = str(pt)
            etaLow, etaHigh   = 0, -1
            ptLow, ptHigh     = pt,  ptBins[i_pt+1]

            QCDTF = copy.deepcopy(QCDTF_updates)
            QCDTF["CR"]["nJet"] = ( nJetLow, nJetHigh )
            QCDTF["SR"]["nJet"] = ( nJetLow, nJetHigh )
            QCDTF["CR"]["nPhoton"] = ( nP, nP )
            QCDTF["SR"]["nPhoton"] = ( nP, nP )
            if nP > 0:
                QCDTF["CR"]["zWindow"] = "offZeg"
                QCDTF["SR"]["zWindow"] = "offZeg"
                QCDTF["CR"]["addMisIDSF"] = True
                QCDTF["SR"]["addMisIDSF"] = True

            # Transfer Factor, get the QCD histograms always in barrel regions
            QCDTF["CR"]["leptonEta"] = ( etaLow, etaHigh )
            QCDTF["CR"]["leptonPt"]  = ( ptLow,  ptHigh   )
            QCDTF["SR"]["leptonEta"] = ( etaLow, etaHigh )
            QCDTF["SR"]["leptonPt"]  = ( ptLow,  ptHigh   )

            qcdUpdate  = { "CR":QCDTF["CR"], "SR":QCDTF["SR"] }
            cachedTF["0b%ip"%nP][nj]["incl"][ptkey] = estimate0b0p.cachedTransferFactor(args.mode, setup0b0p, qcdUpdates=qcdUpdate, checkOnly=True)
            cachedTF["1b%ip"%nP][nj]["incl"][ptkey] = estimate1b0p.cachedTransferFactor(args.mode, setup1b0p, qcdUpdates=qcdUpdate, checkOnly=True)

            for i_eta, eta in enumerate(etaBins[:-1]):
                etakey = str(eta)
                etaLow, etaHigh   = eta, etaBins[i_eta+1]
                ptLow, ptHigh     = pt,  ptBins[i_pt+1]

                QCDTF = copy.deepcopy(QCDTF_updates)
                QCDTF["CR"]["nJet"] = ( nJetLow, nJetHigh )
                QCDTF["SR"]["nJet"] = ( nJetLow, nJetHigh )
                QCDTF["CR"]["nPhoton"] = ( nP, nP )
                QCDTF["SR"]["nPhoton"] = ( nP, nP )
                if nP > 0:
                    QCDTF["CR"]["zWindow"] = "offZeg"
                    QCDTF["SR"]["zWindow"] = "offZeg"
                    QCDTF["CR"]["addMisIDSF"] = True
                    QCDTF["SR"]["addMisIDSF"] = True

                # Transfer Factor, get the QCD histograms always in barrel regions
                QCDTF["CR"]["leptonEta"] = ( etaLow, etaHigh )
                QCDTF["CR"]["leptonPt"]  = ( ptLow,  ptHigh   )
                QCDTF["SR"]["leptonEta"] = ( etaLow, etaHigh )
                QCDTF["SR"]["leptonPt"]  = ( ptLow,  ptHigh   )

                qcdUpdate  = { "CR":QCDTF["CR"], "SR":QCDTF["SR"] }
                cachedTF["0b%ip"%nP][nj][etakey][ptkey] = estimate0b0p.cachedTransferFactor(args.mode, setup0b0p, qcdUpdates=qcdUpdate, checkOnly=True)
                cachedTF["1b%ip"%nP][nj][etakey][ptkey] = estimate1b0p.cachedTransferFactor(args.mode, setup1b0p, qcdUpdates=qcdUpdate, checkOnly=True)


# Text on the plots
def drawObjects( lumi_scale, btags ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    sel = ""
    if btags == 0: sel = "WJets2"
    if btags == 1: sel = "TT2"
    lines = [
      (0.15, 0.95, 'CMS #bf{#it{Preliminary}} (%s)'%sel),
      (0.65, 0.95, '%3.1f fb{}^{-1} (13 TeV)' % lumi_scale),
    ]
    return [tex.DrawLatex(*l) for l in lines]


def drawPlots( plot, btags ):

    maxY = max( [ h.GetMaximum() for hList in plot.histos for h in hList ] )
    plotting.draw( plot,
                   plot_directory = plot_directory_,
                   extensions = extensions_,
                   logX = False, logY = False, sorting = False,
                   yRange = (0.0, maxY*2.5),
                   legend = [(0.2,0.7,0.9,0.88), 1],
                   drawObjects = drawObjects( lumi_scale, btags ),
                   copyIndexPHP = True,
                 )

def draw2DPlots( plot, btags ):

    plotting.draw2D( plot,
                    plot_directory = plot_directory_,
                    extensions = extensions_,
                    logX = False, logY = False, logZ = False,
                    zRange = (0.0, 1.0 if "nBTag0" in plot.name else 1.0),
                    drawObjects = drawObjects( lumi_scale, btags ),
                    copyIndexPHP = True,
                )

color = [ ROOT.kAzure-3, ROOT.kRed-3, ROOT.kGreen-2, ROOT.kOrange ]
hists       = {}
hists2D     = {}
for i_eta, eta in enumerate(etaBins[:-1] + ["incl"]):
    etakey = str(eta)
    for i_pt, pt in enumerate(ptBins[:-1] + ["incl"]):
        ptkey = str(pt)
        etaLow, etaHigh   = ("%.2f"%eta, "%.2f"%etaBins[i_eta+1]) if eta != "incl" else ("incl", None)
        ptLow, ptHigh     = (str(pt),  str(ptBins[i_pt+1])) if pt != "incl" else ("incl", None)

        for b in range(2):
            hists2D["%ib"%b] = ROOT.TH2F("hist2D%ib"%b, "hist2D%ib"%b, 2, 0, 2, 3, 2, 5)
            hists2D["%ib"%b].GetZaxis().SetTitle( "QCD TF rel. diff" )
            hists2D["%ib"%b].GetZaxis().SetTitleSize( 0.04 )
            hists["%ib"%b]   = {}
            for p in range(2):
                hists["%ib"%b]["nJ%iG"%p] = ROOT.TH1F("hist%ib_nJ%iG"%(b,p), "hist%ib_nJ%iG"%(b,p), 3, 2, 5)
                hists["%ib"%b]["nJ%iG"%p].style = styles.errorStyle( color[p], width=3 )
                hists["%ib"%b]["nJ%iG"%p].legendText = "N_{#gamma}=%i, N_{b-jets}=%i"%(p,b)
                hists2D["%ib"%b].GetXaxis().SetBinLabel( p+1, str(p) )
            for j in range(2,5):
                hists["%ib"%b]["nG%iJ"%j] = ROOT.TH1F("hist%ib_nG%iJ"%(b,j), "hist%ib_nG%iJ"%(b,j), 2, 0, 2)
                hists["%ib"%b]["nG%iJ"%j].style = styles.errorStyle( color[j-2], width=3 )
                hists["%ib"%b]["nG%iJ"%j].legendText = "N_{jets}=%i, N_{b-jets}=%i"%(j,b)
                lab = str(j) if j != 4 else "#geq4"
                hists2D["%ib"%b].GetYaxis().SetBinLabel( j-1, lab )

            addon = args.mode.replace("mu", "#mu")
#            addon += "#geq1 b-tag" if b==1 else "0 b-tag"
            if pt != "incl":
                addon += ", "
                addon += "%s #leq p_{T} < %s"%(ptLow, ptHigh) if ptHigh and float(ptHigh) >= 0 else "p_{T} #geq %s"%ptLow
            if eta != "incl":
                addon += ", "
                addon += "%s #leq |#eta| < %s"%(etaLow, etaHigh) if etaHigh and float(etaHigh) >= 0 else "|#eta| #geq %s"%etaLow

            hists["%ib"%b]["nGUsed"] = ROOT.TH1F("hist%ib_nGUsed"%(b), "hist%ib_nGUsed"%(b), 2, 0, 2)
            hists["%ib"%b]["nGUsed"].style = styles.lineStyle( ROOT.kBlack, width=3, errors=False )
            hists["%ib"%b]["nGUsed"].legendText = "used TF (%s)"%addon

            hists["%ib"%b]["nJUsed"] = ROOT.TH1F("hist%ib_nJUsed"%(b), "hist%ib_nJUsed"%(b), 3, 2, 5)
            hists["%ib"%b]["nJUsed"].style = styles.lineStyle( ROOT.kBlack, width=3, errors=False )
            hists["%ib"%b]["nJUsed"].legendText = "used TF (%s)"%addon

        for b in range(2):
            for p in range(2):
                for j in range(2,5):
                    hists["%ib"%b]["nG%iJ"%j].SetBinContent( p+1, cachedTF["%ib%ip"%(b,p)][str(j)][etakey][ptkey].val   )
                    hists["%ib"%b]["nG%iJ"%j].SetBinError(   p+1, cachedTF["%ib%ip"%(b,p)][str(j)][etakey][ptkey].sigma )
                    hists["%ib"%b]["nG%iJ"%j].GetXaxis().SetBinLabel( p+1, str(p) )

                    hists["%ib"%b]["nJ%iG"%p].SetBinContent( j-1, cachedTF["%ib%ip"%(b,p)][str(j)][etakey][ptkey].val   )
                    hists["%ib"%b]["nJ%iG"%p].SetBinError(   j-1, cachedTF["%ib%ip"%(b,p)][str(j)][etakey][ptkey].sigma )
                    lab = str(j) if j != 4 else "#geq4"
                    hists["%ib"%b]["nJ%iG"%p].GetXaxis().SetBinLabel( j-1, lab )

                    hists["%ib"%b]["nGUsed"].SetBinContent( p+1, cachedTF["%ib0p"%(b)]["2"][etakey][ptkey].val   )
                    hists["%ib"%b]["nGUsed"].SetBinError(   p+1, cachedTF["%ib0p"%(b)]["2"][etakey][ptkey].sigma )
                    hists["%ib"%b]["nGUsed"].GetXaxis().SetBinLabel( p+1, str(p) )

                    hists["%ib"%b]["nJUsed"].SetBinContent( j-1, cachedTF["%ib0p"%(b)]["2"][etakey][ptkey].val   )
                    hists["%ib"%b]["nJUsed"].SetBinError(   j-1, cachedTF["%ib0p"%(b)]["2"][etakey][ptkey].sigma )
                    hists["%ib"%b]["nJUsed"].GetXaxis().SetBinLabel( j-1, lab )

                    relTF = (cachedTF["%ib%ip"%(b,p)][str(j)][etakey][ptkey] - cachedTF["%ib0p"%(b)]["2"][etakey][ptkey]) / cachedTF["%ib0p"%(b)]["2"][etakey][ptkey] if cachedTF["%ib0p"%(b)]["2"][etakey][ptkey] else u_float(0)
                    hists2D["%ib"%b].SetBinContent( p+1, j-1, abs(relTF.val)   )
                    hists2D["%ib"%b].SetBinError(   p+1, j-1, abs(relTF.sigma) )


        plots       = {}
        plots2D     = {}
        for b in range(2):
            print "b", b
            label = "TT" if b==1 else "WJets"
            label += "_pT%sTo%s"%(ptLow, ptHigh) if ptHigh and float(ptHigh) >= 0 else "_pT%s"%ptLow
            label += "_eta%sTo%s"%(etaLow, etaHigh) if etaHigh and float(etaHigh) >= 0 else "_eta%s"%etaLow
            print "label", label
            plots2D["%ib"%b] = Plot2D.fromHisto( "QCDTF2D_"+label, [[hists2D["%ib"%b]]], texX="N_{#gamma}", texY="N_{jets}" )
            plots["%ib"%b]   = {}
            print hists["%ib"%b]["nJUsed"]
            print hists["%ib"%b]["nJ0G"]
            print hists["%ib"%b]["nJ1G"]
            print range(2)[::-1]
            plots["%ib"%b]["nJ"] = Plot.fromHisto( "QCDTFnJet_"+label,    [ [hists["%ib"%b]["nJUsed"]], [hists["%ib"%b]["nJ0G"]] ], texX="N_{jets}", texY="QCD Transferfactor" )
            plots["%ib"%b]["nJ"] = Plot.fromHisto( "QCDTFwPnJet_"+label,    [[hists["%ib"%b]["nJUsed"]]] + [[hists["%ib"%b]["nJ%iG"%p]] for p in range(2)[::-1]], texX="N_{jets}", texY="QCD Transferfactor" )
            plots["%ib"%b]["nG"] = Plot.fromHisto( "QCDTFnPhoton_"+label, [[hists["%ib"%b]["nGUsed"]]] + [[hists["%ib"%b]["nG%iJ"%j]] for j in range(2,5)[::-1]], texX="N_{#gamma}", texY="QCD Transferfactor" )

        for b in range(2):
            draw2DPlots( plots2D["%ib"%b], b )
            drawPlots( plots["%ib"%b]["nJ"], b )
            drawPlots( plots["%ib"%b]["nG"], b )
