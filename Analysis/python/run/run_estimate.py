#!/usr/bin/env python

import sys

from TTGammaEFT.Analysis.regions         import regionsTTG, noPhotonRegionTTG, inclRegionsTTG, inclRegionsTTGfake, regionsTTGfake
from TTGammaEFT.Analysis.Setup           import Setup
from TTGammaEFT.Analysis.EstimatorList   import EstimatorList
from TTGammaEFT.Analysis.MCBasedEstimate import MCBasedEstimate
from TTGammaEFT.Analysis.DataObservation import DataObservation
from TTGammaEFT.Analysis.SetupHelpers    import dilepChannels, lepChannels, allProcesses, allRegions

from helpers                             import splitList

loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']
CRChoices     = allRegions.keys()
# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",         action="store",  default="INFO",           choices=loggerChoices, help="Log level for logging")
argParser.add_argument("--noSystematics",    action="store_true",                                              help="no systematics?")
argParser.add_argument("--selectEstimator",  action="store",  default=None,   type=str,                        help="select estimator?")
argParser.add_argument("--runOnLxPlus",      action="store_true",                                              help="Change the global redirector of samples")
#argParser.add_argument("--selectRegion",     action="store",  default=-1,     type=int,                        help="select region?")
argParser.add_argument("--year",             action="store",  default="2016",   type=str,                        help="Which year?")
argParser.add_argument("--cores",            action="store",  default=1,      type=int,                        help="How many threads?")
argParser.add_argument("--controlRegion",    action="store",  default=None,   type=str, choices=CRChoices,     help="For CR region?")
argParser.add_argument("--overwrite",        action="store_true",                                              help="overwrite existing results?")
argParser.add_argument("--checkOnly",        action="store_true",                                              help="check values?")
argParser.add_argument("--createExecFile",   action="store_true",                                              help="get exec file for missing estimates?")
argParser.add_argument('--nJobs',            action='store',  default=1,        type=int,                      help="Maximum number of simultaneous jobs.")
argParser.add_argument('--job',              action='store',  default=0,        type=int,                      help="Run only job i")
args = argParser.parse_args()

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
setup            = Setup( year=args.year, photonSelection=photonSelection and not "QCD" in args.selectEstimator, checkOnly=args.checkOnly, runOnLxPlus=args.runOnLxPlus ) #photonselection always false for qcd estimate

# Select estimate
if args.selectEstimator == "Data":
    estimate = DataObservation(name="Data", process=setup.processes["Data"], cacheDir=setup.defaultCacheDir())
    estimate.isData = True
else:
    estimators = EstimatorList( setup, processes=[args.selectEstimator] )
    estimate   = getattr( estimators, args.selectEstimator )
    estimate.isData = False

if not estimate:
    logger.warning(args.selectEstimator + " not known")
    sys.exit(0)

setup            = setup.sysClone( parameters=parameters )

def wrapper(arg):
        r,channel,setup,addon = arg
        logger.info("Running estimate for region %s, channel %s in setup %s for estimator %s"%(r,channel, args.controlRegion if args.controlRegion else "None", args.selectEstimator if args.selectEstimator else "None"))
        res = estimate.cachedEstimate(r, channel, setup, signalAddon=addon, save=True, overwrite=args.overwrite, checkOnly=(args.checkOnly or args.createExecFile))
        return (estimate.uniqueKey(r, channel, setup), res )

estimate.initCache(setup.defaultCacheDir())

jobs=[]
for channel in channels:
    for (i, r) in enumerate(allPhotonRegions):
#        if args.selectRegion != i: continue
        jobs.append((r, channel, setup, None))
        if not estimate.isData and not args.noSystematics:
            if "TTG" in args.selectEstimator:
                jobs.extend(estimate.getSigSysJobs(r, channel, setup))
            else:
                jobs.extend(estimate.getBkgSysJobs(r, channel, setup))

if args.nJobs != 1:
    jobs = splitList( jobs, args.nJobs)[args.job]

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


if args.createExecFile:
    for res in results:
        if res[1].val < 0:
            with open( "est/missingEstimates_%i_%s_%s_%s.sh"%(args.year, args.controlRegion, args.selectEstimator, args.selectRegion), "w" if args.overwrite else "a" ) as f:
                f.write( "python " + " ".join( [ item for item in sys.argv if item not in ["--createExecFile", "--checkOnly"] ] ) + "\n" )
            sys.exit(0)

