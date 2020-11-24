#!/usr/bin/env python

import sys

from TTGammaEFT.Analysis.regions         import regionsTTG, noPhotonRegionTTG, inclRegionsTTG, inclRegionsTTGfake, regionsTTGfake
from TTGammaEFT.Analysis.Setup           import Setup
from TTGammaEFT.Analysis.EstimatorList   import EstimatorList
from TTGammaEFT.Analysis.MCBasedEstimate import MCBasedEstimate
from TTGammaEFT.Analysis.DataObservation import DataObservation
from TTGammaEFT.Analysis.SetupHelpers    import *

from TTGammaEFT.Tools.user               import cache_directory
from Analysis.Tools.MergingDirDB         import MergingDirDB
from Analysis.Tools.u_float              import u_float

from helpers                             import chunks, splitList

# EFT Reweighting
from Analysis.Tools.WeightInfo          import WeightInfo

loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']
CRChoices     = allRegions.keys()
# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",         action="store",  default="INFO",           choices=loggerChoices, help="Log level for logging")
argParser.add_argument("--cores",            action="store",  default=1,      type=int,                        help="How many threads?")
argParser.add_argument("--controlRegion",    action="store",  default="SR4pM3",   type=str, choices=CRChoices,     help="For CR region?")
argParser.add_argument("--overwrite",        action="store_true",                                              help="overwrite existing results?")
argParser.add_argument("--checkOnly",        action="store_true",                                              help="check values?")
argParser.add_argument('--order',              action='store',      default=2, type=int,                                                             help='Polynomial order of weight string(e.g. 2)') 
argParser.add_argument('--nJobs',              action='store',      nargs='?', type=int, default=1,                                                  help="Maximum number of simultaneous jobs.")
argParser.add_argument('--job',                action='store',      nargs='?', type=int, default=0,                                                  help="Run only job i")
argParser.add_argument('--sample',             action='store',      default='TTG_4WC_ref', type=str,                                              help="Which sample to plot")
args = argParser.parse_args()



# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None)

logger.debug("Start run_estimate.py")

if args.checkOnly: args.overwrite = False

if not args.controlRegion:
    logger.warning("ControlRegion not known")
    sys.exit(0)

# load and define the EFT sample
from TTGammaEFT.Samples.genTuples_TTGamma_EFT_postProcessed  import *
eftSample = eval(args.sample)

#settings for eft reweighting
w = WeightInfo( eftSample.reweight_pkl )
w.set_order( args.order )
variables = w.variables

def get_weight_string( parameters ):
    return w.get_weight_string( **parameters )

baseDir       = os.path.join( cache_directory, "analysis", "eft" )
cacheFileName = os.path.join( baseDir, eftSample.name )
cache         = MergingDirDB( cacheFileName )

parameters       = allRegions[args.controlRegion]["parameters"]
channels         = allRegions[args.controlRegion]["channels"] 
photonSelection  = not allRegions[args.controlRegion]["noPhotonCR"]
allPhotonRegions = allRegions[args.controlRegion]["inclRegion"] + allRegions[args.controlRegion]["regions"] if photonSelection else allRegions[args.controlRegion]["regions"]
setup            = Setup( year=2016, checkOnly=args.checkOnly )
setup            = setup.sysClone( parameters=parameters )

def wrapper(arg):
    r,channel,setup,(ctZ,ctZI,ctW,ctWI) = arg
    EFTparams = [  "ctZ", str(ctZ), "ctZI", str(ctZI) ] #, "ctW", str(ctW), "ctWI", str(ctWI) ]
    params    = { "ctZ":ctZ, "ctZI":ctZI } #,  "ctW":ctW, "ctWI":ctWI }
    key = (args.controlRegion, str(r),channel, "_".join(EFTparams))
    print key
    if cache.contains( key ) and not args.overwrite:
        res = cache.get( key )
    elif not cache.contains( key ) and args.checkOnly:
        res = {"val":-1, "sigma":0}
    else:
        selection = setup.genSelection( "MC", channel=channel, **setup.defaultParameters())["cut"]
        selection = "&&".join( [ selection, r.cutString() ] )
        weightString = "ref_weight*(" + get_weight_string(params) + ")"
        res = eftSample.getYieldFromDraw( selectionString=selection, weightString=weightString )
        cache.add( key, res, overwrite=True )
    print "done", res
    return ( key, res )

jobs=[]
for channel in channels:
    for (i, r) in enumerate(allPhotonRegions):
        for ctZ in eftParameterRange["ctZ"]:
            for ctZI in eftParameterRange["ctZI"]:
                jobs.append((r, channel, setup, (ctZ, ctZI, 0, 0)))
#        for ctW in eftParameterRange["ctW"]:
#            for ctWI in eftParameterRange["ctWI"]:
#                jobs.append((r, channel, setup, (0, 0, ctW, ctWI)))

if args.nJobs > len(jobs):
    logger.info("Batch mode job splitting larger than number of points. Setting nJobs to %i"%len(jobs))
    args.nJobs = len(jobs)

if args.job >= args.nJobs:
    logger.info("Job number > total number of jobs. Exiting")
    sys.exit(0)

if args.nJobs != 1:
    logger.info("Running batch mode job %i of total %i jobs"%(args.job,args.nJobs))
    args.cores = 1
    total = len(jobs)
    jobs = splitList( jobs, args.nJobs)[args.job]
    logger.info("Calculating %i of total %i points"%(len(jobs), total))

print "Running over %i jobs"%len(jobs)
logger.info( "%i points to calculate" %(len(jobs)) )

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
        print res[0][0], res[0][1], res[0][2], "yield:", res[1]["val"]
    sys.exit(0)

