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
import Analysis.Tools.syncer as syncer

loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']
CRChoices     = allRegions.keys()

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",          action="store",  default="INFO",             choices=loggerChoices,      help="Log level for logging")
argParser.add_argument("--plot_directory",    action="store",  default="102X_TTG_ppv29_v2")
argParser.add_argument("--year",              action="store",  default="2016",     type=str, choices=["2016", "2017", "2018", "RunII"], help="Which year?")
argParser.add_argument("--mode",              action="store",  default="e",      type=str, choices=["e", "mu"],        help="Which lepton selection?")
argParser.add_argument("--cores",             action="store",  default=1,        type=int,                             help="run multicore?")
argParser.add_argument("--overwrite",         action="store_true",                                                     help="overwrite?")
args = argParser.parse_args()

if args.year != "RunII": args.year = int(args.year)

# Logging
import Analysis.Tools.logger as logger
logger = logger.get_logger(   args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

ptBins  = [30, 80, 130, 180, -1]
etaBins = [0, 0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1, 2.4]

extensions_ = ["pdf", "png", "root"]
plot_directory_ = os.path.join( plot_directory, 'transferFactor', str(args.year), args.plot_directory, "ptEta", args.mode )

if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74
elif args.year == "RunII": lumi_scale = 35.92 + 41.53 + 59.74
print "hist2D"

parameters   = allRegions["WJets2"]["parameters"]
setup        = Setup( year=args.year, photonSelection=False, checkOnly=False, runOnLxPlus=False )
estimators   = EstimatorList( setup, processes=["QCD-DD"] )
estimate     = getattr(estimators, "QCD-DD")

setup = setup.sysClone( parameters=parameters )
estimate.initCache(setup.defaultCacheDir())

QCDTF_updates       = {}
QCDTF_updates["CR"] = { "invertLepIso":True, "nJet":(2,2), "nBTag":(0,0), "nPhoton":(0,0), "MET":(0,-1), "m3Window":"all", "zWindow":"all", "leptonEta":(0,1.479), "leptonPt":(0, -1) }
QCDTF_updates["SR"] = {                      "nJet":(2,2),                "nPhoton":(0,0), "MET":(0,-1), "m3Window":"all", "zWindow":"all", "leptonEta":(0,1.479), "leptonPt":(0, -1) }


upperPtBin = ptBins[-1] if ptBins[-1] > 0 else 2*ptBins[-2] - ptBins[-3]
hists2D = ROOT.TH2F("hist2D_%i_%s"%(args.year, args.mode), "hist2D_%i_%s"%(args.year, args.mode), len(etaBins)-1, etaBins[0], etaBins[-1], len(ptBins)-1, ptBins[0], upperPtBin)

jobs = []
for i_pt, pt in enumerate(ptBins[:-1]):
    for i_eta, eta in enumerate(etaBins[:-1]):
        jobs += [ [(eta, etaBins[i_eta+1]), (pt, ptBins[i_pt+1])] ]

def wrapper(arg):
    (eta, etaUp), (pt, ptUp) = arg
    print eta, etaUp, pt, ptUp
    QCDTF_updates["CR"]["leptonEta"] = ( eta, etaUp )
    QCDTF_updates["CR"]["leptonPt"]  = ( pt,  ptUp   )
    QCDTF_updates["SR"]["leptonEta"] = ( eta, etaUp )
    QCDTF_updates["SR"]["leptonPt"]  = ( pt,  ptUp   )

    qcdUpdates  = { "CR":QCDTF_updates["CR"], "SR":QCDTF_updates["SR"] }
    transferFac = estimate.cachedTransferFactor( args.mode, setup, qcdUpdates=qcdUpdates, overwrite=args.overwrite, checkOnly=False )

print "Running over %i datapoints!"%len(jobs)
    
if args.cores==1:
    results = map(wrapper, jobs)
else:
    from multiprocessing import Pool
    pool = Pool(processes=args.cores)
    pool.map(wrapper, jobs)
    pool.close()
    pool.join()


for i_pt, pt in enumerate(ptBins[:-1]):
    for i_eta, eta in enumerate(etaBins[:-1]):
        
        print (eta, etaBins[i_eta+1])
        print (pt, ptBins[i_pt+1])

        QCDTF_updates["CR"]["leptonEta"] = ( eta, etaBins[i_eta+1] )
        QCDTF_updates["CR"]["leptonPt"]  = ( pt,  ptBins[i_pt+1]   )
        QCDTF_updates["SR"]["leptonEta"] = ( eta, etaBins[i_eta+1] )
        QCDTF_updates["SR"]["leptonPt"]  = ( pt,  ptBins[i_pt+1]   )

        qcdUpdates  = { "CR":QCDTF_updates["CR"], "SR":QCDTF_updates["SR"] }
        transferFac = estimate.cachedTransferFactor( args.mode, setup, qcdUpdates=qcdUpdates, overwrite=False, checkOnly=False )
        print pt, eta, transferFac
        hists2D.SetBinContent( i_eta+1, i_pt+1, abs(transferFac.val)   )
        hists2D.SetBinError(   i_eta+1, i_pt+1, abs(transferFac.sigma) )
    
plots2D = Plot2D.fromHisto( "TF2D", [[hists2D]], texX="|#eta(l_{0})|", texY="p_{T}(l_{0}) [GeV]" )

# Text on the plots
def drawObjects( lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS #bf{#it{Preliminary}} (%s)'%args.selection),
      (0.68, 0.95, '%3.1f fb^{-1} (13 TeV)' % lumi_scale),
    ]
    return [tex.DrawLatex(*l) for l in lines]


def draw2DPlots( plot ):

    plotting.draw2D( plot,
                    plot_directory = plot_directory_,
                    extensions = extensions_,
                    logX = False, logY = False, logZ = False,
                    zRange = (0,6),
                    drawObjects = drawObjects( lumi_scale ),
                    copyIndexPHP = True,
                )

draw2DPlots( plots2D )
