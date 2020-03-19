#!/usr/bin/env python

""" 
Extraction of PDF and scale uncertainties in the SRs
"""

# Standard imports
import ROOT
import os
import sys
import math

# RootTools
from RootTools.core.standard           import *

# TTGammaEFT
from TTGammaEFT.Analysis.SetupHelpers    import *
from TTGammaEFT.Analysis.Setup           import Setup
from TTGammaEFT.Analysis.EstimatorList   import EstimatorList
from TTGammaEFT.Analysis.regions         import *
from TTGammaEFT.Analysis.MCBasedEstimate import MCBasedEstimate
from TTGammaEFT.Analysis.DataObservation import DataObservation

from helpers                           import uniqueKey

# Analysis
from Analysis.Tools.MergingDirDB       import MergingDirDB
from Analysis.Tools.u_float            import u_float

# use this for job splitting
from RootTools.core.helpers            import partition

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]
CRChoices     = allRegions.keys()

# Arguments
import argparse
argParser=argparse.ArgumentParser(description="Argument parser" )
argParser.add_argument( "--logLevel",            action="store",      default="INFO",         choices=loggerChoices,      help="Log level for logging" )
argParser.add_argument( "--selectRegion",        action="store",      default=None, type=int,                             help="select region?" )
argParser.add_argument( "--controlRegion",       action="store",      default=None, type=str, choices=CRChoices,          help="For CR region?" )
argParser.add_argument( "--selectEstimator",     action="store",      default=None, type=str,                             help="select estimator?" )
argParser.add_argument( "--year",                action="store",      default=2016, type=int, choices=[2016, 2017, 2018], help="which year?" )
argParser.add_argument( "--nJobs",               action="store",      default=1, type=int,                                help="How many jobs?" )
argParser.add_argument( "--job",                 action="store",      default=0, type=int,                                help="Which job?" )
argParser.add_argument( "--overwrite",           action="store_true",                                                     help="Overwrite existing output files, bool flag set to True  if used" )
argParser.add_argument( "--checkOnly",           action="store_true",                                                     help="check values?" )
argParser.add_argument( "--combine",             action="store_true",                                                     help="calculate final uncertainties?" )
argParser.add_argument( "--runOnLxPlus",         action="store_true",                                                     help="Change the global redirector of samples")
args = argParser.parse_args()

# Logging
import Analysis.Tools.logger as logger
logger = logger.get_logger(       args.logLevel, logFile=None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger( args.logLevel, logFile=None )

# setup and sample
parameters       = allRegions[args.controlRegion]["parameters"]
channels         = allRegions[args.controlRegion]["channels"]
photonSelection  = not allRegions[args.controlRegion]["noPhotonCR"]
allPhotonRegions = allRegions[args.controlRegion]["inclRegion"] + allRegions[args.controlRegion]["regions"] if photonSelection else allRegions[args.controlRegion]["regions"]
regions          = allPhotonRegions if not args.selectRegion else [allPhotonRegions[args.selectRegion]]

setup            = Setup( year=args.year, photonSelection=photonSelection, checkOnly=args.checkOnly, runOnLxPlus=args.runOnLxPlus ) #photonselection always false for qcd es$
setup            = setup.sysClone( parameters=parameters )
estimates        = EstimatorList( setup, processes=[args.selectEstimator, "TTG"] )
estimate         = getattr( estimates, args.selectEstimator )
estimate.initCache( setup.defaultCacheDir() )

setupIncl        = Setup( year=args.year, photonSelection=False, checkOnly=args.checkOnly, runOnLxPlus=args.runOnLxPlus ) #photonselection always false for qcd es$
setupIncl        = setupIncl.sysClone( parameters={ "zWindow":"all", "nJet":(0,-1), "nBTag":(0,-1), "nPhoton":(0,-1) } )
estimates        = EstimatorList( setupIncl, processes=["TTG"] )
estimateIncl     = getattr( estimates, "TTG" )
estimateIncl.initCache( setupIncl.defaultCacheDir() )

logger.info( "Calculating PDF and Scale uncertainties for %s", args.selectEstimator)

""" 
OBJ: TBranch   nLHEPdfWeight    : 0 at: 0x51f1350
OBJ: TBranch   LHEPdfWeight    LHE pdf variation weights (w_var / w_nominal) for LHA IDs 91400 - 91432 : 0 at: 0x51f19a0

OBJ: TBranch   nLHEScaleWeight  : 0 at: 0x51f25a0
OBJ: TBranch   LHEScaleWeight  LHE scale variation weights (w_var / w_nominal); [0] is MUR="0.5" MUF="0.5"; [1] is MUR="0.5" MUF="0.5"; [2] is MUR="0.5" MUF="0.5"; [3] is MUR="0.5" MUF="0.5"; [4] is MUR="0.5" MUF="0.5"; [5] is MUR="0.5" MUF="1.0"; [6] is MUR="0.5" MUF="1.0"; [7] is MUR="0.5" MUF="1.0"; [8] is MUR="0.5" MUF="1.0"; [9] is MUR="0.5" MUF="1.0"; [10] is MUR="0.5" MUF="2.0"; [11] is MUR="0.5" MUF="2.0"; [12] is MUR="0.5" MUF="2.0"; [13] is MUR="0.5" MUF="2.0"; [14] is MUR="0.5" MUF="2.0"; [15] is MUR="1.0" MUF="0.5"; [16] is MUR="1.0" MUF="0.5"; [17] is MUR="1.0" MUF="0.5"; [18] is MUR="1.0" MUF="0.5"; [19] is MUR="1.0" MUF="0.5"; [20] is MUR="1.0" MUF="1.0"; [21] is MUR="1.0" MUF="1.0"; [22] is MUR="1.0" MUF="1.0"; [23] is MUR="1.0" MUF="1.0"; [24] is MUR="1.0" MUF="2.0"; [25] is MUR="1.0" MUF="2.0"; [26] is MUR="1.0" MUF="2.0"; [27] is MUR="1.0" MUF="2.0"; [28] is MUR="1.0" MUF="2.0"; [29] is MUR="2.0" MUF="0.5"; [30] is MUR="2.0" MUF="0.5"; [31] is MUR="2.0" MUF="0.5"; [32] is MUR="2.0" MUF="0.5"; [33] is MUR="2.0" MUF="0.5"; [34] is MUR="2.0" MUF="1.0"; [35] is MUR="2.0" MUF="1.0"; [36] is MUR="2.0" MUF="1.0"; [37] is MUR="2.0" MUF="1.0"; [38] is MUR="2.0" MUF="1.0"; [39] is MUR="2.0" MUF="2.0"; [40] is MUR="2.0" MUF="2.0"; [41] is MUR="2.0" MUF="2.0"; [42] is MUR="2.0" MUF="2.0"; [43] is MUR="2.0" MUF="2.0" : 0 at: 0x51f2b90

OBJ: TBranch   nPSWeight    : 0 at: 0x51f3cd0
OBJ: TBranch   PSWeight    dummy PS weight (1.0)  : 0 at: 0x51f42c0

"""

# dummy values for now
PDFType   = "hessian" #"replicas"
logger.info( "Using PDF type: %s"%PDFType )

#https://indico.cern.ch/event/860492/contributions/3624049/attachments/1957483/3252108/SystematicIssues.pdf
scale_indices       = [0,5,15,20,24,34,39] #20 central?
#scale_variations    = [ "abs(LHEScaleWeight[%i]/LHEScaleWeight[20])"%i for i in scale_indices ]
scale_variations    = [ "abs(LHEScaleWeight[%i])"%i for i in scale_indices ]

pdf_indices         = range(1,31)
PDF_variations      = [ "abs(LHEPdfWeight[%i]/LHEPdfWeight[0])"%i for i in pdf_indices ]

aS_variations       = [ "abs(LHEPdfWeight[31]/LHEPdfWeight[0])", "abs(LHEPdfWeight[32]/LHEPdfWeight[0])"]

# wrong PS weights in samples, need to be rescaled by LHEWeight_originalXWGTUP/Generator_weight
ps_indices          = range(4)# if args.year == 2016 else []
PS_variations       = [ "abs(PSWeight[%i])*LHEWeight_originalXWGTUP/Generator_weight"%i for i in ps_indices ]

variations          = scale_variations + PDF_variations + aS_variations + PS_variations
results             = {}
scale_systematics   = {}

# Results DB for scale and PDF uncertainties
cacheDir    = os.path.join( cache_directory, "modelling",  str(args.year) )
PDF_cache   = MergingDirDB( os.path.join( cacheDir, "PDF" ) )
scale_cache = MergingDirDB( os.path.join( cacheDir, "Scale" ) )
PS_cache    = MergingDirDB( os.path.join( cacheDir, "PS" ) )
if not PDF_cache:   raise
if not scale_cache: raise
if not PS_cache:    raise

def wrapper(arg):
        r, c, s, inclusive = arg
        logger.debug("Calculating estimate for %s in region %s and channel %s"%(args.selectEstimator, r, c))
        if inclusive:
            res = estimateIncl.cachedEstimate(r, c, s, save=True, overwrite=args.overwrite, checkOnly=args.checkOnly)
            return (estimateIncl.uniqueKey(r, c, s), res )
        else:
            res = estimate.cachedEstimate(r, c, s, save=True, overwrite=args.overwrite, checkOnly=args.checkOnly)
            return (estimate.uniqueKey(r, c, s), res )

jobs=[]

for region in regions:
    logger.debug("Queuing jobs for region %s", region)
    for c in channels:
        logger.debug("Queuing jobs for channel %s", c)
        jobs.append((region, c, setup, False))
        for var in variations:
            jobs.append((region, c, setup.sysClone(sys={"reweight":[var]}), False))
    
logger.debug("Queuing jobs for channel %s", c)
jobs.append((noRegions[0], "all", setupIncl, True))
for var in variations:
    jobs.append((noRegions[0], "all", setupIncl.sysClone(sys={"reweight":[var]}), True))
    
logger.info("Created %s jobs",len(jobs))

jobs = partition(jobs, args.nJobs)[args.job]

logger.info("Running over %s jobs", len(jobs))

results = []
if not args.combine:
    results = map(wrapper, jobs)
    logger.info("All done.")

if args.checkOnly:
    for res in results:
        print args.selectEstimator, res[0][0], res[0][1], args.controlRegion, res[1].val
    sys.exit(0)

if not args.combine: sys.exit(0)

logger.info("Combining...")

PDF_unc     = []
Scale_unc   = []
PS_unc      = []

logger.info("Getting inclusive yield")
sigma_incl_central       = estimateIncl.cachedEstimate(noRegions[0], 'all', setupIncl )
sigma_incl_central_scale = estimateIncl.cachedEstimate(noRegions[0], 'all', setupIncl.sysClone(sys={'reweight':["abs(LHEScaleWeight[20])"]}))

for c in channels:
    logger.info("Combining channel: %s", c)
    for region in regions:
        logger.info("Combining region: %s", region)
                
        # central yield inclusive and in region
        logger.info("Getting yield for region with scaleweight_central")

        sigma_central            = estimate.cachedEstimate(region, c, setup)
        sigma_central_scale      = estimate.cachedEstimate(region, c, setup.sysClone(sys={'reweight':["abs(LHEScaleWeight[20])"]}))

        scales        = []
        for var in scale_variations:
            logger.info("Getting inclusive yield with varied weight")
            simga_incl_reweight = estimateIncl.cachedEstimate(noRegions[0], 'all', setupIncl.sysClone(sys={'reweight':[var]}))
            norm                = sigma_incl_central_scale / simga_incl_reweight if simga_incl_reweight > 0 else 1.

            logger.info("Getting yield for region with varied weight")
            sigma_reweight     = estimate.cachedEstimate(region, c, setup.sysClone(sys={'reweight':[var]}))
            sigma_reweight_acc = sigma_reweight * norm

            unc = abs(sigma_reweight_acc - sigma_central_scale) / sigma_central_scale if sigma_central_scale > 0 else u_float(0)
            scales.append(unc.val)

        scale_rel = max(scales)

        # PDF
        delta_squared = 0
        for var in PDF_variations:

            logger.info("Getting yield for region with varied weight PDF")
            sigma_reweight     = estimate.cachedEstimate(region, c, setup.sysClone(sys={'reweight':[var]}))

            ## recommendation for hessian is to have delta_sigma = sum_k=1_N( (sigma_k - sigma_0)**2 )
            delta_squared += ( sigma_reweight.val - sigma_central.val )**2

        deltas_as = []
        for var in aS_variations:
            logger.info("Getting inclusive yield with varied weight aS")
            simga_incl_reweight = estimateIncl.cachedEstimate(noRegions[0], 'all', setupIncl.sysClone(sys={'reweight':[var]}))
            norm = sigma_incl_central / simga_incl_reweight if simga_incl_reweight > 0 else 1.

            logger.info("Getting yield for region with varied weight aS")
            sigma_reweight  = estimate.cachedEstimate(region, c, setup.sysClone(sys={'reweight':[var]}))
            sigma_reweight_acc = sigma_reweight * norm

            deltas_as.append(sigma_reweight_acc.val)

        if deltas_as:
            delta_sigma_alphaS = ( deltas_as[0] - deltas_as[1] ) * 0.5
            # add alpha_s and PDF in quadrature
            delta_squared += delta_sigma_alphaS**2

        # calculate uncertainty
        delta_sigma_total = math.sqrt( delta_squared )

        # make it relative wrt central value in region
        delta_sigma_rel = delta_sigma_total / sigma_central.val if sigma_central.val > 0 else 0.

        if delta_sigma_rel > 1: logger.info("ERROR: delta_sigma_rel > 1 for region %s and channel %s"%(region, c))

        # calculate the PS uncertainties
        if PS_variations:
            ps_scales        = []
            for var in PS_variations:

                logger.info("Getting yield for region with varied weight aS")
                sigma_reweight_PS     = estimate.cachedEstimate(region, c, setup.sysClone(sys={'reweight':[var]}))

                unc = abs( sigma_reweight_PS - sigma_central ) / sigma_central if sigma_central > 0 else u_float(0)
                ps_scales.append(unc.val)

            logger.info( "ISR up/down: %f, %f"%(round(ps_scales[0], 3), round( ps_scales[2], 3) ) )
            logger.info( "FSR up/down: %f, %f"%(round(ps_scales[1], 3), round( ps_scales[3], 3) ) )

            PS_scale_rel = max(ps_scales)
        else:
            PS_scale_rel = 0.

        niceName = " ".join([c, region.__str__()])
        logger.info("Calculated PDF, PS and scale uncertainties for region %s in channel %s"%(region, c))
        logger.info("Central x-sec: %s"%sigma_central)
        logger.info("Relative uncertainty: %s"%delta_sigma_rel)
        logger.info("Relative scale uncertainty: %s"%scale_rel)
        logger.info("Relative PS uncertainty: %s"%PS_scale_rel)
                
        PDF_unc.append(delta_sigma_rel)
        PS_unc.append(PS_scale_rel)
        Scale_unc.append(scale_rel)

        # Store results
        key = uniqueKey( args.selectEstimator, region, c, setup ) + tuple(str(args.year))
        PDF_cache.add(   key, delta_sigma_rel, overwrite=True )
        scale_cache.add( key, scale_rel,       overwrite=True )
        PS_cache.add(    key, PS_scale_rel,    overwrite=True )

logger.info("Min. PDF uncertainty: %.3f"%min(PDF_unc))
logger.info("Max. PDF uncertainty: %.3f"%max(PDF_unc))
logger.info("Av. PDF uncertainty: %.3f"%(sum(PDF_unc)/len(PDF_unc) if PDF_unc else 1.))
logger.info("Min. PS uncertainty: %.3f"%min(PS_unc))
logger.info("Max. PS uncertainty: %.3f"%max(PS_unc))
logger.info("Av. PS uncertainty: %.3f"%(sum(PS_unc)/len(PS_unc) if PS_unc else 1.))
logger.info("Min. scale uncertainty: %.3f"%min(Scale_unc))
logger.info("Max. scale uncertainty: %.3f"%max(Scale_unc))
logger.info("Av. scale uncertainty: %.3f"%(sum(Scale_unc)/len(Scale_unc) if Scale_unc else 1.))
