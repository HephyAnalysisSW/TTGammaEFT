#!/usr/bin/env python

import sys

from TTGammaEFT.Analysis.regions         import regionsTTG, noPhotonRegionTTG, inclRegionsTTG, inclRegionsTTGfake, regionsTTGfake
from TTGammaEFT.Analysis.DataDrivenFakeEstimate import DataDrivenFakeEstimate
from TTGammaEFT.Analysis.SetupHelpers    import *
from TTGammaEFT.Analysis.Setup           import Setup
from helpers                             import splitList

loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']
CRChoices     = allRegions.keys()
# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",         action="store",  default="INFO",           choices=loggerChoices, help="Log level for logging")
#argParser.add_argument("--selectEstimator",  action="store",  default=None,   type=str,                        help="select estimator?")
argParser.add_argument("--year",             action="store",  default="2016",   type=str,                        help="Which year?")
argParser.add_argument("--cores",            action="store",  default=1,      type=int,                        help="How many threads?")
argParser.add_argument("--controlRegion",    action="store",  default="SR4pM3",   type=str, choices=CRChoices,     help="For CR region?")
argParser.add_argument("--overwrite",        action="store_true",                                              help="overwrite existing results?")
argParser.add_argument("--checkOnly",        action="store_true",                                              help="check values?")
argParser.add_argument('--nJobs',             action='store',  default=1,        type=int,                             help="Maximum number of simultaneous jobs.")
argParser.add_argument('--job',               action='store',  default=0,        type=int,                             help="Run only job i")
args = argParser.parse_args()

args.selectEstimator = "TT_pow_had"
if args.year != "RunII": args.year = int(args.year)

# Logging
import Analysis.Tools.logger as logger
logger = logger.get_logger(   args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

logger.debug("Start run_estimate.py")

if not args.controlRegion:
    logger.warning("ControlRegion not known")
    sys.exit(0)

parameters       = allRegions[args.controlRegion]["parameters"]
channels         = allRegions[args.controlRegion]["channels"] 
photonSelection  = not allRegions[args.controlRegion]["noPhotonCR"]
allPhotonRegions = allRegions[args.controlRegion]["inclRegion"] + allRegions[args.controlRegion]["regions"] if photonSelection else allRegions[args.controlRegion]["regions"]
setup            = Setup( year=args.year, photonSelection=False, checkOnly=args.checkOnly ) #photonselection always false for qcd estimate

estimate = DataDrivenFakeEstimate( args.selectEstimator, process=setup.processes[args.selectEstimator] )
estimate.initCache(setup.defaultCacheDir())
estimate.isData = False

if not estimate:
    logger.warning(args.selectEstimator + " not known")
    sys.exit(0)

setup            = setup.sysClone( parameters=parameters )

def wrapper(arg):
        r,channel,setup,addon = arg
        logger.info("Running estimate for region %s, channel %s in setup %s for estimator %s"%(r,channel, args.controlRegion if args.controlRegion else "None", args.selectEstimator if args.selectEstimator else "None"))
        res = estimate.cachedFakeFactor(r, channel, setup, overwrite=args.overwrite, checkOnly=args.checkOnly)
#        res = estimate.cachedEstimate(r, channel, setup, overwrite=args.overwrite, checkOnly=args.checkOnly)
        return (estimate.uniqueKey(r, channel, setup), res )

estimate.initCache(setup.defaultCacheDir())

jobs=[]
for channel in channels:
    for (i, r) in enumerate(allPhotonRegions):
        jobs.append((r, channel, setup, None))
#        if not estimate.isData and not args.noSystematics and not "DD" in args.selectEstimator:
#            if "TTG" in args.selectEstimator:
#                jobs.extend(estimate.getSigSysJobs(r, channel, setup))
#            else:
#                jobs.extend(estimate.getBkgSysJobs(r, channel, setup))

print len(jobs)
if args.nJobs != 1:
    jobs = splitList( jobs, args.nJobs)[args.job]

print jobs
if args.cores==1:
    results = map(wrapper, jobs)
else:
    from multiprocessing import Pool
    pool = Pool(processes=args.cores)
    results = pool.map(wrapper, jobs)
    pool.close()
    pool.join()


if args.checkOnly:
    for res in results:
        print args.selectEstimator, res[0][0], res[0][1], args.controlRegion, res[1].val
    sys.exit(0)

