#!/usr/bin/env python

import sys

from TTGammaEFT.Analysis.regions         import regionsTTG, noPhotonRegionTTG, inclRegionsTTG, inclRegionsTTGfake, regionsTTGfake
from TTGammaEFT.Analysis.Setup           import Setup
from TTGammaEFT.Analysis.EstimatorList   import EstimatorList
from TTGammaEFT.Analysis.MCBasedEstimate import MCBasedEstimate
from TTGammaEFT.Analysis.DataObservation import DataObservation
from TTGammaEFT.Analysis.SetupHelpers    import dilepChannels, lepChannels, allProcesses, allRegions

from TTGammaEFT.Tools.user               import cache_directory
from Analysis.Tools.MergingDirDB         import MergingDirDB

# EFT Reweighting
from Analysis.Tools.WeightInfo          import WeightInfo

loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']
CRChoices     = allRegions.keys()
# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",         action="store",  default="INFO",           choices=loggerChoices, help="Log level for logging")
argParser.add_argument("--selectRegion",     action="store",  default=0,     type=int,                        help="select region?")
argParser.add_argument("--year",             action="store",  default=2016,   type=int,                        help="Which year?")
argParser.add_argument("--cores",            action="store",  default=1,      type=int,                        help="How many threads?")
argParser.add_argument("--controlRegion",    action="store",  default="SR4pM3",   type=str, choices=CRChoices,     help="For CR region?")
argParser.add_argument("--overwrite",        action="store_true",                                              help="overwrite existing results?")
argParser.add_argument("--checkOnly",        action="store_true",                                              help="check values?")
argParser.add_argument('--parameters',         action='store',      default=['ctZI', '2', 'ctWI', '2', 'ctZ', '2', 'ctW', '2'], type=str, nargs='+', help = "argument parameters")
argParser.add_argument('--order',              action='store',      default=2, type=int,                                                             help='Polynomial order of weight string(e.g. 2)') 
argParser.add_argument('--mode',               action='store',      default="all", type=str, choices=["mu", "e", "all"],               help="plot lepton mode" )

args = argParser.parse_args()

# Logging
import Analysis.Tools.logger as logger
logger = logger.get_logger(   args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

logger.debug("Start run_estimate.py")

if not args.controlRegion:
    logger.warning("ControlRegion not known")
    sys.exit(0)

# load and define the EFT sample
from TTGammaEFT.Samples.genTuples_TTGamma_EFT_postProcessed  import *
eftSample = TTG_4WC_ref

EFTparams = []
if args.parameters:
    coeffs = args.parameters[::2]
    str_vals = args.parameters[1::2]
    for i_param, (coeff, str_val, ) in enumerate(zip(coeffs, str_vals)):
        EFTparams.append(coeff)
        EFTparams.append(str_val)
print EFTparams


baseDir       = os.path.join( cache_directory, "analysis",  str(args.year), "eftEstimate" )
cacheFileName = os.path.join( baseDir, eftSample.name )
cache         = MergingDirDB( cacheFileName )

parameters       = allRegions[args.controlRegion]["parameters"]
channels         = allRegions[args.controlRegion]["channels"] 
photonSelection  = not allRegions[args.controlRegion]["noPhotonCR"]
allPhotonRegions = allRegions[args.controlRegion]["inclRegion"] + allRegions[args.controlRegion]["regions"] if photonSelection else allRegions[args.controlRegion]["regions"]
setup            = Setup( year=args.year, checkOnly=args.checkOnly )
setup            = setup.sysClone( parameters=parameters )

print setup.defaultParameters()

#settings for eft reweighting
w = WeightInfo( eftSample.reweight_pkl )
w.set_order( args.order )
variables = w.variables

def get_weight_string( parameters ):
    return w.get_weight_string( **parameters )

def wrapper(arg):
    r,channel,setup = arg
    key = (args.controlRegion, str(r), "_".join(EFTparams))
    if cache.contains( key ) and not args.overwrite:
        res = cache.get( key )
    else:
        selection = setup.genSelection( "MC", channel=channel, **setup.defaultParameters())["cut"]
        selection = "&&".join( [ selection, r.cutString() ] )
        smweightString = get_weight_string({})
        res = eftSample.getYieldFromDraw( selectionString=selection, weightString=smweightString)
        cache.add( key, res, overwrite=True )
        if args.parameters:
            coeffs = args.parameters[::2]
            str_vals = args.parameters[1::2]
            vals = list( map( float, str_vals ) )
            for i_param, (coeff, val, str_val, ) in enumerate(zip(coeffs, vals, str_vals)):
                weightString = get_weight_string({coeff:val}) 
                res = eftSample.getYieldFromDraw( selectionString=selection, weightString=weightString )
                cache.add( key, res, overwrite=True )
    return ( key, res )


jobs=[]
for channel in channels:
    for (i, r) in enumerate(allPhotonRegions):
        if args.selectRegion != i: continue
        jobs.append((r, channel, setup))

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
        print args.selectEstimator, res[0][0], res[0][1], res[0][2], res[1].val
    sys.exit(0)

