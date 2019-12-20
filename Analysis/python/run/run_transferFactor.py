#!/usr/bin/env python

import sys

from TTGammaEFT.Analysis.regions         import photonBinRegions, regionsTTG, noPhotonRegionTTG, inclRegionsTTG
from TTGammaEFT.Analysis.Setup           import Setup
from TTGammaEFT.Analysis.EstimatorList   import EstimatorList
from TTGammaEFT.Analysis.MCBasedEstimate import MCBasedEstimate
from TTGammaEFT.Analysis.DataObservation import DataObservation
from TTGammaEFT.Analysis.SetupHelpers    import dilepChannels, lepChannels, allProcesses, allRegions

from Analysis.Tools.u_float              import u_float

loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']
CRChoices     = allRegions.keys()
# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",         action="store",  default="INFO",           choices=loggerChoices, help="Log level for logging")
argParser.add_argument("--runOnLxPlus",      action="store_true",                                              help="Change the global redirector of samples")
argParser.add_argument("--year",             action="store",  default=2016,   type=int,                        help="Which year?")
argParser.add_argument("--cores",            action="store",  default=1,      type=int,                        help="How many threads?")
argParser.add_argument("--controlRegion",    action="store",  default=None,   type=str, choices=CRChoices,     help="For CR region?")
argParser.add_argument("--overwrite",        action="store_true",                                              help="overwrite existing results?")
argParser.add_argument("--checkOnly",        action="store_true",                                              help="check values?")
argParser.add_argument('--nJobs',            action='store',  default=1,      type=int,                        help="Maximum number of simultaneous jobs.")
argParser.add_argument('--job',              action='store',  default=0,      type=int,                        help="Run only job i")
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
channels         = allRegions[args.controlRegion]["channels"] 
#regions          = inclRegionsTTG + regionsTTG + photonBinRegions if not allRegions[args.controlRegion]["noPhotonCR"] else noPhotonRegionTTG
regions          = allRegions[args.controlRegion]["regions"] + allRegions[args.controlRegion]["inclRegion"]
setup            = Setup( year=args.year, photonSelection=False, checkOnly=args.checkOnly, runOnLxPlus=args.runOnLxPlus ) #photonselection always false for qcd estimate

estimators = EstimatorList( setup, processes=["QCD-DD"] )
estimate   = getattr(estimators, "QCD-DD")
estimate.isData = False

setup = setup.sysClone( parameters=parameters )
estimate.initCache(setup.defaultCacheDir())

def wrapper(arg):
        r,channel,set = arg
        logger.debug("Running transfer factor for region %s, channel %s in setup %s for QCD-DD"%(r,channel, args.controlRegion))
        res = estimate.cachedTransferFactor(r, channel, setup, save=True, overwrite=args.overwrite, checkOnly=args.checkOnly)
        return (arg, res )

jobs=[]
for channel in channels:
    for (i, r) in enumerate(regions):
        jobs.append((r, channel, setup))

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
        print args.controlRegion, res[0][0], res[0][1], str(res[1])

