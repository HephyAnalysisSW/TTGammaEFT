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

# get brute force all of them
for nJet in [(2,2), (3,3), (4,-1)]:
        nj = str(nJet[0])
        print nJet
        # inclusive tf
        nJetLow, nJetHigh = nJet

        QCDTF = copy.deepcopy(QCDTF_updates)
        QCDTF["CR"]["nJet"] = ( nJetLow, nJetHigh )
        QCDTF["SR"]["nJet"] = ( nJetLow, nJetHigh )

        qcdUpdate  = { "CR":QCDTF["CR"], "SR":QCDTF["SR"] }
#        cachedTF["0bMC"][nj]["incl"]["incl"] = estimate0b0p.cachedQCDMCTransferFactor(args.mode, setup0b0p, qcdUpdates=qcdUpdate, checkOnly=False)
        print estimate1b0p.cachedQCDMCTransferFactor(args.mode, setup1b0p, qcdUpdates=qcdUpdate, checkOnly=False)
