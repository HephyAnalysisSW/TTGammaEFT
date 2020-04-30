#!/usr/bin/env python

import sys, copy

from TTGammaEFT.Analysis.regions         import *
from TTGammaEFT.Analysis.Setup           import Setup
from TTGammaEFT.Analysis.EstimatorList   import EstimatorList
from TTGammaEFT.Analysis.MCBasedEstimate import MCBasedEstimate
from TTGammaEFT.Analysis.DataObservation import DataObservation
from TTGammaEFT.Analysis.SetupHelpers    import *

from Analysis.Tools.u_float              import u_float

from helpers                             import splitList

loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']
CRChoices     = allRegions.keys()

ptBins  = [0, 45, 65, 80, 100, 120, -1]
etaBins = [0, 1.479, 1.7, 2.1, -1]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",          action="store",  default="INFO",           choices=loggerChoices,      help="Log level for logging")
argParser.add_argument("--runOnLxPlus",       action="store_true",                                                   help="Change the global redirector of samples")
argParser.add_argument("--year",              action="store",  default=2016,     type=int,                             help="Which year?")
argParser.add_argument("--mode",              action="store",  default="all",    type=str, choices=["e", "mu", "all"], help="How many threads?")
argParser.add_argument("--controlRegion",     action="store",  default="WJets2", type=str, choices=CRChoices,          help="For CR region?")
argParser.add_argument("--overwrite",         action="store_true",                                                   help="overwrite existing results?")
argParser.add_argument("--checkOnly",         action="store_true",                                                   help="check values?")
argParser.add_argument('--nJobs',             action='store',  default=1,        type=int,                             help="Maximum number of simultaneous jobs.")
argParser.add_argument('--job',               action='store',  default=0,        type=int,                             help="Run only job i")
args = argParser.parse_args()

# Logging
import Analysis.Tools.logger as logger
logger = logger.get_logger(   args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

logger.debug("Start run_transferFactor.py")

if not args.controlRegion:
    logger.warning("ControlRegion not known")
    sys.exit(0)

parameters       = allRegions[args.controlRegion]["parameters"]
channels         = [args.mode] if args.mode != "all" else ["e", "mu"] #allRegions[args.controlRegion]["channels"] 
setup            = Setup( year=args.year, photonSelection=False, checkOnly=args.checkOnly, runOnLxPlus=args.runOnLxPlus ) #photonselection always false for qcd estimate

estimators = EstimatorList( setup, processes=["QCD-DD"] )
estimate   = getattr(estimators, "QCD-DD")
estimate.isData = False

setup = setup.sysClone( parameters=parameters )
estimate.initCache(setup.defaultCacheDir())

def wrapper(arg):
#        r,channel,set = arg
        setup, channel, nJetLow, nJetHigh, etaLow, etaHigh, ptLow, ptHigh = arg
        logger.debug("Running transfer factor, channel %s in setup %s for QCD-DD"%(channel, args.controlRegion))

        QCDTF = copy.deepcopy(QCDTF_updates)
        QCDTF["CR"]["nJet"] = ( nJetLow, nJetHigh )
        QCDTF["SR"]["nJet"] = ( nJetLow, nJetHigh )

        # Transfer Factor, get the QCD histograms always in barrel regions
        QCDTF["CR"]["leptonEta"] = ( etaLow, etaHigh )
        QCDTF["CR"]["leptonPt"]  = ( ptLow,  ptHigh   )
        QCDTF["SR"]["leptonEta"] = ( etaLow, etaHigh )
        QCDTF["SR"]["leptonPt"]  = ( ptLow,  ptHigh   )

        # define the 2016 e-channel QCD sideband in barrel only (bad mT fit in EC)
        if channel == "e" and args.year == 2016 and (etaHigh > 1.479 or etaHigh < 0):
            QCDTF["CR"]["leptonEta"] = ( 0, 1.479 )

        qcdUpdates  = { "CR":QCDTF["CR"], "SR":QCDTF["SR"] }
        transferFac = estimate.cachedTransferFactor( channel, setup, qcdUpdates=qcdUpdates, overwrite=args.overwrite, checkOnly=args.checkOnly )
        return (arg, transferFac )

jobs=[]
for channel in channels:
    for nJet in [(2,2), (3,3), (4,-1), (3,-1), (2,-1)]:
        for i_pt, pt in enumerate(ptBins[:-1]):
            for i_eta, eta in enumerate(etaBins[:-1]):
                nJetLow, nJetHigh = nJet
                etaLow, etaHigh   = eta, etaBins[i_eta+1]
                ptLow, ptHigh     = pt,  ptBins[i_pt+1]

                jobs.append( (setup, channel, nJetLow, nJetHigh, etaLow, etaHigh, ptLow, ptHigh) )

if args.nJobs != 1:
    jobs = splitList( jobs, args.nJobs)[args.job]

print "Running %i jobs"%len(jobs)
results = map(wrapper, jobs)

if args.checkOnly:
    for res in results:
        print args.controlRegion, res[0][1], "nJet", res[0][2], res[0][3], "eta", res[0][4], res[0][5], "pT", res[0][6], res[0][7], "TF:", str(res[1])

