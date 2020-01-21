#!/usr/bin/env python

import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys
from time import sleep

# RootTools
from RootTools.core.standard          import *

# Internal Imports
from TTGammaEFT.Tools.user               import plot_directory

from TTGammaEFT.Analysis.Setup           import Setup
from TTGammaEFT.Analysis.EstimatorList   import EstimatorList
from TTGammaEFT.Analysis.SetupHelpers    import dilepChannels, lepChannels, allProcesses, allRegions, customQCDTF_updates

# Analysis Imports
from Analysis.Tools.u_float              import u_float

loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']
CRChoices     = allRegions.keys()

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",          action="store",  default="INFO",             choices=loggerChoices,      help="Log level for logging")
argParser.add_argument("--plot_directory",    action="store",  default="102X_TTG_ppv1_v1")
argParser.add_argument("--year",              action="store",  default=2016,     type=int, choices=[2016, 2017, 2018], help="Which year?")
argParser.add_argument("--mode",              action="store",  default="e",      type=str, choices=["e", "mu"],        help="Which lepton selection?")
args = argParser.parse_args()

# Logging
import Analysis.Tools.logger as logger
logger = logger.get_logger(   args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

extensions_ = ["pdf", "png", "root"]
plot_directory_ = os.path.join( plot_directory, 'transferFactor', args.plot_directory, args.mode )

if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74

parameters0b = allRegions["VG2"]["parameters"]
parameters1b = allRegions["SR2"]["parameters"]
setup        = Setup( year=args.year, photonSelection=False, checkOnly=True, runOnLxPlus=False )
estimators   = EstimatorList( setup, processes=["QCD-DD"] )
estimate     = getattr(estimators, "QCD-DD")

setup0b = setup.sysClone( parameters=parameters0b )
setup1b = setup.sysClone( parameters=parameters1b )
estimate.initCache(setup.defaultCacheDir())

cachedTF       = {}
cachedTF["0b"] = {}
cachedTF["1b"] = {}
# get brute force all of them
for key, qcdUpdate in customQCDTF_updates.iteritems():
    cachedTF["0b"][key] = estimate.cachedTransferFactor(args.mode, setup0b, qcdUpdates=qcdUpdate, checkOnly=True)
    cachedTF["1b"][key] = estimate.cachedTransferFactor(args.mode, setup1b, qcdUpdates=qcdUpdate, checkOnly=True)

color = [ ROOT.kAzure-3, ROOT.kRed-3, ROOT.kGreen-2, ROOT.kOrange ]
hists       = {}
hists2D     = {}
for b in range(2):
    hists2D["%ib"%b] = ROOT.TH2F("hist2D%ib"%b, "hist2D%ib"%b, 2, 0, 2, 3, 2, 5)
    hists2D["%ib"%b].GetZaxis().SetTitle( "QCD Transferfactor" )
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
        hists2D["%ib"%b].GetYaxis().SetBinLabel( j-1, str(j) )

    hists["%ib"%b]["nGUsed"] = ROOT.TH1F("hist%ib_nGUsed"%(b), "hist%ib_nGUsed"%(b), 2, 0, 2)
    hists["%ib"%b]["nGUsed"].style = styles.lineStyle( ROOT.kBlack, width=3, errors=True )
    hists["%ib"%b]["nGUsed"].legendText = "used TF (%s)"%args.mode.replace("mu","#mu")

    hists["%ib"%b]["nJUsed"] = ROOT.TH1F("hist%ib_nJUsed"%(b), "hist%ib_nJUsed"%(b), 3, 2, 5)
    hists["%ib"%b]["nJUsed"].style = styles.lineStyle( ROOT.kBlack, width=3, errors=True )
    hists["%ib"%b]["nJUsed"].legendText = "used TF (%s)"%args.mode.replace("mu","#mu")

    hists2D["%ib"%b].GetYaxis().SetBinLabel( j-1, str(j) )

for b in range(2):
    for p in range(2):
        for j in range(2,5):
            hists["%ib"%b]["nG%iJ"%j].SetBinContent( p+1, cachedTF["%ib"%b]["%iJ%iP"%(j,p)].val   )
            hists["%ib"%b]["nG%iJ"%j].SetBinError(   p+1, cachedTF["%ib"%b]["%iJ%iP"%(j,p)].sigma )
            hists["%ib"%b]["nG%iJ"%j].GetXaxis().SetBinLabel( p+1, str(p) )

            hists["%ib"%b]["nJ%iG"%p].SetBinContent( j-1, cachedTF["%ib"%b]["%iJ%iP"%(j,p)].val   )
            hists["%ib"%b]["nJ%iG"%p].SetBinError(   j-1, cachedTF["%ib"%b]["%iJ%iP"%(j,p)].sigma )
            hists["%ib"%b]["nJ%iG"%p].GetXaxis().SetBinLabel( j-1, str(j) )

            hists["%ib"%b]["nGUsed"].SetBinContent( p+1, cachedTF["%ib"%b]["2J0P"].val   )
            hists["%ib"%b]["nGUsed"].SetBinError(   p+1, cachedTF["%ib"%b]["2J0P"].sigma )
            hists["%ib"%b]["nGUsed"].GetXaxis().SetBinLabel( p+1, str(p) )

            hists["%ib"%b]["nJUsed"].SetBinContent( j-1, cachedTF["%ib"%b]["2J0P"].val   )
            hists["%ib"%b]["nJUsed"].SetBinError(   j-1, cachedTF["%ib"%b]["2J0P"].sigma )
            hists["%ib"%b]["nJUsed"].GetXaxis().SetBinLabel( j-1, str(j) )

            hists2D["%ib"%b].SetBinContent( p+1, j-1, cachedTF["%ib"%b]["%iJ%iP"%(j,p)].val   )
            hists2D["%ib"%b].SetBinError(   p+1, j-1, cachedTF["%ib"%b]["%iJ%iP"%(j,p)].sigma )


plots       = {}
plots2D     = {}
for b in range(2):
    plots2D["%ib"%b] = Plot2D.fromHisto( "TF2D_nBTag%i"%b, [[hists2D["%ib"%b]]], texX="N_{#gamma}", texY="N_{jets}" )
    plots["%ib"%b]   = {}
    plots["%ib"%b]["nJ"] = Plot.fromHisto( "TFnJet_nBTag%i"%(b),  [[hists["%ib"%b]["nJUsed"]]] + [[hists["%ib"%b]["nJ%iG"%p]] for p in range(2)[::-1]], texX="N_{jets}", texY="QCD Transferfactor" )
    plots["%ib"%b]["nG"] = Plot.fromHisto( "TFnPhoton_nBTag%i"%(b), [[hists["%ib"%b]["nGUsed"]]] + [[hists["%ib"%b]["nG%iJ"%j]] for j in range(2,5)[::-1]], texX="N_{#gamma}", texY="QCD Transferfactor" )

# Text on the plots
def drawObjects( lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS #bf{#it{Preliminary}}'),
      (0.65, 0.95, '%3.1f fb{}^{-1} (13 TeV)' % lumi_scale),
    ]
    return [tex.DrawLatex(*l) for l in lines]


def drawPlots( plot ):

    maxY = max( [ h.GetMaximum() for hList in plot.histos for h in hList ] )
    plotting.draw( plot,
                   plot_directory = plot_directory_,
                   extensions = extensions_,
                   logX = False, logY = False, sorting = False,
                   yRange = (0.0, maxY*2.5),
                   legend = [(0.2,0.75,0.9 if len(plot.histos) > 3 else 0.6,0.88), 2 if len(plot.histos) > 3 else 1],
                   drawObjects = drawObjects( lumi_scale ),
                   copyIndexPHP = True,
                 )

def draw2DPlots( plot ):

    plotting.draw2D( plot,
                    plot_directory = plot_directory_,
                    extensions = extensions_,
                    logX = False, logY = False, logZ = False,
                    zRange = (0.0, "auto"),
                    drawObjects = drawObjects( lumi_scale ),
                    copyIndexPHP = True,
                )

for b in range(2):
    draw2DPlots( plots2D["%ib"%b] )
    drawPlots( plots["%ib"%b]["nJ"] )
    drawPlots( plots["%ib"%b]["nG"] )
