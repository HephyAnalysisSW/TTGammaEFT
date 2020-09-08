#!/usr/bin/env python

import sys, copy

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
argParser.add_argument("--year",             action="store",  default="2016",   type=str,                        help="Which year?")
argParser.add_argument("--cores",            action="store",  default=1,      type=int,                        help="How many threads?")
argParser.add_argument("--controlRegion",    action="store",  default=None,   type=str, choices=CRChoices,     help="For CR region?")
argParser.add_argument("--overwrite",        action="store_true",                                              help="overwrite existing results?")
argParser.add_argument("--checkOnly",        action="store_true",                                              help="check values?")
argParser.add_argument("--noInclusive",      action="store_true",                                              help="do not cache inclusive region")
argParser.add_argument('--nJobs',            action='store',  default=1,        type=int,                      help="Maximum number of simultaneous jobs.")
argParser.add_argument('--job',              action='store',  default=0,        type=int,                      help="Run only job i")
args = argParser.parse_args()

if args.year != "RunII": args.year = int(args.year)
if args.checkOnly: args.overwrite = False

# Logging
import Analysis.Tools.logger as logger
logger = logger.get_logger(   args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

logger.debug("Start run_estimate.py")

if not args.controlRegion:
    logger.warning("ControlRegion not known")
    sys.exit(0)

if not "3p" in args.controlRegion:
    print "Need the 3p region as input! Got %s"%args.controlRegion
    sys.exit(0)

print "Combining caches from %s and %s to %s"%(args.controlRegion.replace("3p","3"), args.controlRegion.replace("3p","4p"), args.controlRegion)

parameters3p     = allRegions[args.controlRegion]["parameters"]
parameters3      = allRegions[args.controlRegion.replace("3p","3")]["parameters"]
parameters4p     = allRegions[args.controlRegion.replace("3p","4p")]["parameters"]
channels         = allRegions[args.controlRegion]["channels"] 
photonSelection  = not allRegions[args.controlRegion]["noPhotonCR"]
if args.noInclusive:
    allPhotonRegions = allRegions[args.controlRegion]["regions"]
else:
    allPhotonRegions = allRegions[args.controlRegion]["inclRegion"] + allRegions[args.controlRegion]["regions"] if photonSelection else allRegions[args.controlRegion]["regions"]
setup            = Setup( year=args.year, photonSelection=photonSelection and not "QCD" in args.selectEstimator, checkOnly=True ) #photonselection always false for qcd estimate

# Select estimate
if args.selectEstimator == "Data":
    estimate = DataObservation(name="Data", process=setup.processes["Data"])
    estimate.isData = True
else:
    estimators = EstimatorList( setup, processes=[args.selectEstimator] )
    estimate   = getattr( estimators, args.selectEstimator )
    estimate.isData = False

if not estimate:
    logger.warning(args.selectEstimator + " not known")
    sys.exit(0)

estimate.initCache(setup.defaultCacheDir())
setup3p = setup.sysClone( parameters=parameters3p )
setup3  = setup.sysClone( parameters=parameters3 )
setup4p = setup.sysClone( parameters=parameters4p )

def wrapper(arg):
        r,channel,setup3p,addon,setup3,setup4p = arg
        logger.info("Running estimate for region %s, channel %s in setup %s for estimator %s"%(r,channel, args.controlRegion if args.controlRegion else "None", args.selectEstimator if args.selectEstimator else "None"))
        res3  = estimate.cachedEstimate(r, channel, setup3, signalAddon=addon, save=True, overwrite=False, checkOnly=True)
        res4p = estimate.cachedEstimate(r, channel, setup4p, signalAddon=addon, save=True, overwrite=False, checkOnly=True)
        if res3.val >= 0 and res4p.val >= 0:
            res3p = res3 + res4p
            toRes = estimate.writeToCache(r, channel, setup3p, res3p, signalAddon=addon, overwrite=args.overwrite)
        else:
            res3p = -1
            print "Did not copy: ", args.selectEstimator, estimate.uniqueKey(r, channel, setup3p), args.controlRegion
#        print "Got: 3: %s, 4p: %s, 3p: %s"%(res3, res4p, res3p)
        return (estimate.uniqueKey(r, channel, setup3p), res3p )

if "all" in channels: channels = ["e","mu","all"]
jobs=[]
for channel in channels:
    for (i, r) in enumerate(allPhotonRegions):
#        if args.selectRegion != i: continue
        jobs.append((r, channel, setup3p, None, setup3, setup4p))
        if not estimate.isData and not args.noSystematics:
            if "TTG" in args.selectEstimator:
                addJobs = estimate.getSigSysJobs(r, channel, setup3p)
            else:
                addJobs = estimate.getBkgSysJobs(r, channel, setup3p)
            for j in addJobs:
                jobs.append( tuple(list(j)+[setup3,setup4p]) )

print "Running %i jobs in total."%len(jobs)

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


