#!/usr/bin/env python

import sys

from TTGammaEFT.Analysis.regions         import *
from TTGammaEFT.Analysis.Setup           import Setup
from TTGammaEFT.Analysis.EstimatorList   import EstimatorList
from TTGammaEFT.Analysis.MCBasedEstimate import MCBasedEstimate
from TTGammaEFT.Analysis.DataObservation import DataObservation
from TTGammaEFT.Analysis.SetupHelpers    import dilepChannels, lepChannels, allProcesses, allRegions, customQCDTF_updates

from Analysis.Tools.u_float              import u_float

from helpers                             import splitList

loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']
CRChoices     = allRegions.keys()
qcdChoices    = customQCDTF_updates.keys()
# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",          action="store",  default="INFO",           choices=loggerChoices,      help="Log level for logging")
argParser.add_argument("--runOnLxPlus",       action="store_true",                                                   help="Change the global redirector of samples")
argParser.add_argument("--year",              action="store",  default="2016",   type=str,                             help="Which year?")
#argParser.add_argument("--cores",             action="store",  default=1,      type=int,                             help="How many threads?")
argParser.add_argument("--mode",              action="store",  default="all",  type=str, choices=["e", "mu", "all"], help="How many threads?")
argParser.add_argument("--controlRegion",     action="store",  default=None,   type=str, choices=CRChoices,          help="For CR region?")
argParser.add_argument("--customQCDUpdates",  action="store",  default=None,   type=str, choices=qcdChoices,         help="Custom QCD updates?")
argParser.add_argument("--overwrite",         action="store_true",                                                   help="overwrite existing results?")
argParser.add_argument("--checkOnly",         action="store_true",                                                   help="check values?")
#argParser.add_argument('--nJobs',             action='store',  default=1,      type=int,                             help="Maximum number of simultaneous jobs.")
#argParser.add_argument('--job',               action='store',  default=0,      type=int,                             help="Run only job i")
args = argParser.parse_args()

if args.year != "RunII": args.year = int(args.year)

# Logging
import Analysis.Tools.logger as logger
logger = logger.get_logger(   args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

logger.debug("Start run_transferFactor.py")

if args.customQCDUpdates:
    args.customQCDUpdates = customQCDTF_updates[args.customQCDUpdates]

if not args.controlRegion:
    logger.warning("ControlRegion not known")
    sys.exit(0)

parameters       = allRegions[args.controlRegion]["parameters"]
channels         = [args.mode] if args.mode != "all" else ["e", "mu"] #allRegions[args.controlRegion]["channels"] 
#regions          = allRegions[args.controlRegion]["inclRegion"] #if allRegions[args.controlRegion]["noPhotonCR"] else allRegions[args.controlRegion]["inclRegion"] + allRegions[args.controlRegion]["regions"] + regionsTTG20To120 + regionsTTG120To220 + regionsTTG220
setup            = Setup( year=args.year, photonSelection=False, checkOnly=args.checkOnly, runOnLxPlus=args.runOnLxPlus ) #photonselection always false for qcd estimate

estimators = EstimatorList( setup, processes=["QCD-DD"] )
estimate   = getattr(estimators, "QCD-DD")
estimate.isData = False

setup = setup.sysClone( parameters=parameters )
estimate.initCache(setup.defaultCacheDir())

def wrapper(arg):
#        r,channel,set = arg
        channel,set = arg
        logger.debug("Running transfer factor, channel %s in setup %s for QCD-DD"%(channel, args.controlRegion))
        res = estimate.cachedTransferFactor(channel, setup, qcdUpdates=args.customQCDUpdates, save=True, overwrite=args.overwrite, checkOnly=args.checkOnly)
        return (arg, res )

jobs=[]
for channel in channels:
    jobs.append((channel, setup))

results = map(wrapper, jobs)

#    for (i, r) in enumerate(regions):
#        jobs.append((r, channel, setup))

#if args.nJobs != 1:
#    jobs = splitList( jobs, args.nJobs)[args.job]

#if args.cores==1:
#    results = map(wrapper, jobs)
#else:
#    from multiprocessing import Pool
#    pool = Pool(processes=args.cores)
#    results = pool.map(wrapper, jobs)
#    pool.close()
#    pool.join()


if args.checkOnly:
    for res in results:
        print args.controlRegion, res[0][0], str(res[1])

