''' Plot script WC parameter LogLikelihood
'''

# Standard imports 
import sys, os, pickle, copy, ROOT, time
import numpy as np

# Multiprocessing
from multiprocessing import Pool

# RootTools
from RootTools.core.standard   import *

# turn off graphics
ROOT.gROOT.SetBatch( True )

# TTGammaEFT
from TTGammaEFT.Tools.user              import combineReleaseLocation, cache_directory, cardfileLocation

from TTGammaEFT.Tools.genCutInterpreter import cutInterpreter

# get the reweighting function
from Analysis.Tools.WeightInfo          import WeightInfo
from Analysis.Tools.CardFileWriter      import CardFileWriter

from TTGammaEFT.Tools.Cache             import Cache

# Default Parameter
loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                                help="Log level for logging")
argParser.add_argument('--genSelection1l',     action='store',      default='dilepOS-pTG20-nPhoton1p-offZSFllg-offZSFll-mll40-nJet2p-nBTag1p')
argParser.add_argument('--genSelection2l',     action='store',      default='dilepOS-pTG20-nPhoton1p-offZSFllg-offZSFll-mll40-nJet2p-nBTag1p')
argParser.add_argument('--selection1l',        action='store',      default='nLepTight1-nLepVeto1-nJet4p-nBTag1p-pTG20-nPhoton1p')
argParser.add_argument('--selection2l',        action='store',      default='dilepOS-nLepVeto2-pTG20-nPhoton1p-offZSFllg-offZSFll-mll40-nJet2p-nBTag1p')
argParser.add_argument('--variables' ,         action='store',      default = ['ctZ', 'ctZI'], type=str, nargs=2,                                    help="argument plotting variables")
argParser.add_argument('--keepCards',          action='store_true',                                                                                  help='Keep all cardfiles?', )
argParser.add_argument('--small',              action='store_true',                                                                                  help='Run only on a small subset of the data?', )
argParser.add_argument('--overwrite',          action='store_true',                                                                                  help='Overwrite Database entries?', )
argParser.add_argument('--forceWriting',       action='store_true',                                                                                  help='Retry writing to DB with recovering file', )
argParser.add_argument('--order',              action='store',      default=2,                                                                       help='Polynomial order of weight string (e.g. 2)')
argParser.add_argument('--years',              action='store',      default=[ 2016, 2017 ], type=int, choices=[2016, 2017, 2018], nargs="*",         help="Which years to combine?")
argParser.add_argument('--selections',         action='store',      default=[ "1l", "2l" ], type=str, choices=["1l", "2l"], nargs="*",               help="Which selections to combine?")
argParser.add_argument('--binning',            action='store',      default=[30, -2, 2, 30, -2, 2 ], type=float, nargs=6,                            help="argument parameters")
argParser.add_argument('--cores',              action='store',      default=1,                       type=int,                                       help='number of cpu cores for multicore processing')
argParser.add_argument('--checkOnly',          action='store_true',                                                                                  help='Just check if yield is already calculated', )
argParser.add_argument('--inclusive',          action='store_true',                                                                                  help='run inclusive regions', )
args = argParser.parse_args()

if args.inclusive:
    from TTGammaEFT.Analysis.regions        import recoTTGammaRegionsIncl as regions
    from TTGammaEFT.Analysis.regions        import genTTGammaRegionsIncl  as genRegions
else:
    from TTGammaEFT.Analysis.regions        import recoTTGammaRegions     as regions
    from TTGammaEFT.Analysis.regions        import genTTGammaRegions      as genRegions

combinedAnalysis = len(args.years) != 1 or len(args.selections) != 1

tableName = "nllcache"
cache_dir_yields = os.path.join(cache_directory, "yields")
cache_dir_nll    = os.path.join(cache_directory, "nll")
if not os.path.isdir(cache_dir_nll):
    os.mkdir(cache_dir_nll)
dbFile = "NLLcache"
if   "1l" in args.selections and len(args.selections) == 1: dbFile += "_semilep"
elif "2l" in args.selections and len(args.selections) == 1: dbFile += "_dilep"
elif len(args.selections) > 1:                              dbFile += "_both"
if len(args.years) > 1:                                     dbFile += "_comb"
if args.inclusive:                                          dbFile += "_incl"
dbFile += ".sql"
dbPath = os.path.join(cache_dir_nll, dbFile)

nllCache  = Cache( dbPath, tableName, ["cardname", "year", "WC1_name", "WC1_val", "WC2_name", "WC2_val", "nll_prefit", "nll_postfit" ] )
if nllCache is None: raise


# Logging
if __name__=="__main__":
    import Analysis.Tools.logger as logger
    logger = logger.get_logger( args.logLevel, logFile=None)
    import RootTools.core.logger as logger_rt
    logger_rt = logger_rt.get_logger( args.logLevel, logFile=None )
else:
    import logging
    logger = logging.getLogger(__name__)


# Samples
if 2016 in args.years:
    from TTGammaEFT.Samples.nanoTuples_Summer16_private_postProcessed      import *
if 2017 in args.years:
    from TTGammaEFT.Samples.nanoTuples_Fall17_private_postProcessed        import *
if 2018 in args.years:
    from TTGammaEFT.Samples.nanoTuples_Autumn18_private_postProcessed      import *

# Gen Samples
from TTGammaEFT.Samples.genTuples_TTGamma_postProcessed                import *

#signalSample = TTG_SingleLeptFromT_1L_test_EFT
genSignalSample = {}
genSignalSample["1l"] = TTG_DiLept_1L_EFT
genSignalSample["2l"] = TTG_DiLept_1L_EFT

selection = {}
selection["1l"] = args.selection1l
selection["2l"] = args.selection2l

genSelection = {}
genSelection["1l"] = args.genSelection1l
genSelection["2l"] = args.genSelection2l

cardname  = [ genSignalSample[sel].name for sel in args.selections ]
cardname += map( str, args.years )
cardname += args.selections
cardname += [ args.variables[0], "var1", args.variables[1], "var2" ]
cardname += [ selection[sel] for sel in args.selections ]
cardname += [ 'small' if args.small else 'full' ]
if args.inclusive: cardname += [ 'incl' ]
cardname  = '_'.join( cardname )

logger.info( "General card name: %s" %cardname )

command = os.path.expandvars("$CMSSW_BASE/src/TTGammaEFT/Tools/scripts/recoverDB.sh")
def recoverDB( path, file ):
    os.system("%s %s %s"%(command, file, path))

def isInDatabase( var1, var2 ):
    card = cardname.replace("var1", str(var1)).replace("var2", str(var2))
    res  = {'cardname':card, "year":"combined", "WC1_name":args.variables[0], "WC1_val":var1, "WC2_name":args.variables[1], "WC2_val":var2}
    nCacheFiles = nllCache.contains( res )
#    if args.checkOnly:
#        if not nCacheFiles: logger.info( "Limit not calculated for %s=%s, %s=%s!" %(args.variables[0], str(var1), args.variables[1], str(var2)) )
#        return True

    if nCacheFiles: return True
    else: return False

#binning range
xbins, xlow, xhigh = args.binning[:3]
xbins = int(xbins)
ybins, ylow, yhigh = args.binning[3:]
ybins = int(ybins)

if xbins > 1:
    xRange       = np.linspace( xlow, xhigh, xbins, endpoint=False)
    halfstepsize = 0.5 * ( xRange[1] - xRange[0] )
    xRange       = [ round(el + halfstepsize, 3) for el in xRange ]
else:
    xRange = [ 0.5 * ( xlow + xhigh ) ]

if ybins > 1:
    yRange = np.linspace( ylow, yhigh, ybins, endpoint=False)
    halfstepsize = 0.5 * ( yRange[1] - yRange[0] )
    yRange = [ round(el + halfstepsize, 3) for el in yRange ]
else:
    yRange = [ 0.5 * ( ylow + yhigh ) ]

# check if already in database before calculations
points2D  = [ (0, 0) ] #SM point
points2D += [ (0, varY) for varY in yRange] #1D plots
points2D += [ (varX, 0) for varX in xRange] #1D plots
points2D += [ (varX, varY) for varY in yRange for varX in xRange] #2D plots

logger.info( "Checking %i points" %(len(points2D)) )

if not args.overwrite:
    points2D = [ (x,y) for x,y in points2D if not isInDatabase( x, y ) ]

    if args.checkOnly:
        print "Limit not calculated for %i points" %len(points2D)
        logger.info( "Limit not calculated for %i points" %(len(points2D)) )
        sys.exit(0)

    if not points2D: sys.exit(0) #nothing to calculate

w = {}
for sel in args.selections:
    w[sel] = WeightInfo( genSignalSample[sel].reweight_pkl )
    w[sel].set_order( int(args.order) )

# Sample definition
lumi_scale = {}
mc         = {}
ttGSample  = {}
tr = {}

for sel in args.selections:
    tr[sel]        = {}
    mc[sel]        = {}
    ttGSample[sel] = {}

if 2016 in args.years:
    lumi_scale[2016]       = 35.92
    if "1l" in args.selections:
        mc["1l"][2016]         = [ TT_pow_16, DY_LO_16, singleTop_16, WJets_16, ZG_16, other_16 ]
        ttGSample["1l"][2016]  = TTG_16
    if "2l" in args.selections:
        mc["2l"][2016]         = [ DY_LO_16, TT_pow_16, ZG_16, singleTop_16, other_16 ]
        ttGSample["2l"][2016]  = TTG_16

if 2017 in args.years:
    lumi_scale[2017]       = 41.53
    if "1l" in args.selections:
        mc["1l"][2017]         = [ DY_LO_17, TG_17, WJets_17, WG_17, TT_pow_17, singleTop_17, other_17 ]
        ttGSample["1l"][2017]  = TTG_17
    if "2l" in args.selections:
        mc["2l"][2017]         = [ DY_LO_17, TT_pow_17, singleTop_17, other_17 ]
        ttGSample["2l"][2017]  = TTG_17

if 2018 in args.years:
    lumi_scale[2018]       = 59.74
    if "1l" in args.selections:
        mc["1l"][2018]         = [ TT_pow_18, singleTop_18, DY_LO_18, other_18 ]
        ttGSample["1l"][2018]  = TTG_18
    if "2l" in args.selections:
        mc["2l"][2018]         = [ DY_LO_18, TT_pow_18, singleTop_18, other_18 ]
        ttGSample["2l"][2018]  = TTG_18

def calculation( (var1, var2) ):
    
    kwargs = { args.variables[0]:var1, args.variables[1]:var2 }

    card     = {}
    cardpath = {}
    #caching results
    for sel in args.selections:
      logger.info( "At %s selection", sel )

      for year in args.years:

        logger.info( "Creating cardfile for %i, %s=%s, %s=%s"%(year, args.variables[0], str(var1), args.variables[1], str(var2) ) ) 

        cardKey = str(year)+str(sel)
        card[cardKey]     = cardname.replace("var1", str(var1)).replace("var2", str(var2)).replace( "_".join(map(str,args.years)), cardKey ).replace( "_".join(args.selections), sel )
        cardpath[cardKey] = os.path.join( cardfileLocation, card[cardKey] + '.txt' )

        c = CardFileWriter()
        c.reset()
        c.releaseLocation = combineReleaseLocation

        c.addUncertainty('lumi',        'lnN')
        c.addUncertainty('JES',         'lnN')
        c.addUncertainty('btagging',    'lnN')
        c.addUncertainty('mistagging',  'lnN')
        c.addUncertainty('muonId',      'lnN')
        c.addUncertainty('electronId',  'lnN')

        signal_rate  = {}

        for i_region, region in enumerate(regions):

            logger.info( "At EFT region %s", region )

            signal_genRateEFT = w[sel].get_weight_yield( coeffList[sel][region], **kwargs )
            signal_genKFactor = signal_genRateEFT / signal_genRateSM[sel][region]

            signal_rate[region] = rate[sel][year][region][ttGSample[sel][year].name] * signal_genKFactor

            signal_btagging_uncertainty   [region] = 1.04# if not i_region   else 1.01
            signal_mistagging_uncertainty [region] = 1.04# if not i_region   else 1.01
            signal_muonId_uncertainty     [region] = 1.04# if not i_region   else 1.01
            signal_electronId_uncertainty [region] = 1.04# if not i_region   else 1.01
            signal_jes_uncertainty        [region] = 1.04# if not i_region   else 1.01

            bin_name  = "Region_%i" %i_region
            nice_name = region.__str__()
            c.addBin( bin_name, [ sample.name for sample in mc[sel][year] ], nice_name)

            c.specifyObservation( bin_name, observation[sel][year][region] )
            c.specifyExpectation( bin_name, 'signal', signal_rate[region] )

            c.specifyFlatUncertainty( 'lumi', 1.025 )
            c.specifyUncertainty( 'JES',        bin_name, 'signal', signal_jes_uncertainty       [region] )
            c.specifyUncertainty( 'btagging',   bin_name, 'signal', signal_btagging_uncertainty  [region] )
            c.specifyUncertainty( 'mistagging', bin_name, 'signal', signal_mistagging_uncertainty[region] )
            c.specifyUncertainty( 'muonId',     bin_name, 'signal', signal_muonId_uncertainty    [region] )
            c.specifyUncertainty( 'electronId', bin_name, 'signal', signal_electronId_uncertainty[region] )

            for sample in mc[sel][year]:
                c.specifyExpectation( bin_name, sample.name, rate[sel][year][region][sample.name] )

                c.specifyUncertainty( 'JES',        bin_name, sample.name, jes_uncertainty       [sel][year][region][sample.name] )
                c.specifyUncertainty( 'btagging',   bin_name, sample.name, btagging_uncertainty  [sel][year][region][sample.name] )
                c.specifyUncertainty( 'mistagging', bin_name, sample.name, mistagging_uncertainty[sel][year][region][sample.name] )
                c.specifyUncertainty( 'muonId',     bin_name, sample.name, muonId_uncertainty    [sel][year][region][sample.name] )
                c.specifyUncertainty( 'electronId', bin_name, sample.name, electronId_uncertainty[sel][year][region][sample.name] )
                    
        c.writeToFile( cardpath[cardKey] )
        logger.info( "Written card: %s"%cardpath[cardKey] )

    if combinedAnalysis:
        # combinin years, selections or both
        combinedCard = c.combineCards( cardpath )
        logger.info( "Using combined card: %s"%combinedCard )
    else:
        combinedCard = cardpath[cardKey]
        logger.info( "Using card: %s"%combinedCard )

    nll          = c.calcNLL( combinedCard )
    nll_prefit   = nll['nll0']
    nll_postfit  = nll['nll_abs']
    
    if nll_prefit  is None or abs(nll_prefit) > 10000 or abs(nll_prefit) < 1e-5:   nll_prefit  = 999
    if nll_postfit is None or abs(nll_postfit) > 10000 or abs(nll_postfit) < 1e-5: nll_postfit = 999

    if not args.keepCards and not (var1==0 and var2==0):
        os.remove( combinedCard )
        if combinedAnalysis:
            for sel in args.selections:
                for year in args.years:
                    cardKey = str(year)+str(sel)
                    os.remove( cardpath[cardKey] )

    card = cardname.replace("var1", str(var1)).replace("var2", str(var2))
    res = {'cardname':card, "year":"combined", "WC1_name":args.variables[0], "WC1_val":var1, "WC2_name":args.variables[1], "WC2_val":var2, "nll_prefit":nll_prefit, "nll_postfit":nll_postfit }
    logger.info( "NLL limit for %s = %f, %s = %f: nll_prefit = %f, nll_postfit = %f"%(args.variables[0], var1, args.variables[1], var2, nll_prefit, nll_postfit) )
    nllCache.add( res, nll_prefit, overwrite=True )

    del c

    if args.forceWriting:
        for i in range(10):
            if nllCache.contains( res ): return
            logger.info("LIMIT NOT WRITTEN! RECOVERING DB FILE AND TRYING AGAIN!")
            recoverDB( cache_dir_nll, dbFile )
            time.sleep(0.5)
            nllCache.add( res, nll_prefit, overwrite=True )


rate             = {}
observation      = {}
signal_genRateSM = {}
coeffList        = {}

btagging_uncertainty   = {}
mistagging_uncertainty = {}
jes_uncertainty        = {}
electronId_uncertainty = {}
muonId_uncertainty     = {}

signal_btagging_uncertainty    = {}
signal_mistagging_uncertainty  = {}
signal_jes_uncertainty         = {}
signal_electronId_uncertainty  = {}
signal_muonId_uncertainty      = {}

for i_sel, sel in enumerate(args.selections):
    rate[sel]             = {}
    observation[sel]      = {}
    coeffList[sel]        = {}
    signal_genRateSM[sel] = {}

    btagging_uncertainty  [sel] = {}
    mistagging_uncertainty[sel] = {}
    jes_uncertainty       [sel] = {}
    electronId_uncertainty[sel] = {}
    muonId_uncertainty    [sel] = {}

    for i_year, year in enumerate(args.years):
        rate[sel][year] = {}
        observation[sel][year] = {}

        btagging_uncertainty  [sel][year] = {}
        mistagging_uncertainty[sel][year] = {}
        jes_uncertainty       [sel][year] = {}
        electronId_uncertainty[sel][year] = {}
        muonId_uncertainty    [sel][year] = {}

        for i_region, region in enumerate(regions):
            rate[sel][year][region] = {}

            btagging_uncertainty  [sel][year][region] = {}
            mistagging_uncertainty[sel][year][region] = {}
            jes_uncertainty       [sel][year][region] = {}
            electronId_uncertainty[sel][year][region] = {}
            muonId_uncertainty    [sel][year][region] = {}

def getSMYields( year, sel ):
    for i_sample, sample in enumerate( mc[sel][year] + [ttGSample[sel][year]]):

        logger.info( "Getting yield for sample %s", sample.name )

        dbFilename = "yields_%s.sql"%sample.name
        yieldDB = Cache( os.path.join( cache_dir_yields, dbFilename ), "yields", [ "selection", "year", "small", "region", sample.name] )
        if not yieldDB: raise

        for i_region, region in enumerate(regions):
            logger.info( "At reco region %s", region )
            res = {"selection":selection[sel], "year":year, "small":args.small, "region":str(region), sample.name:sample.name }

            if yieldDB.contains( res ):
                rate[sel][year][region][sample.name] = round( float( yieldDB.getDicts( res )[0]["value"] ), 3 )
                logger.info("%i: Using yield for sample %s at region %s: %f"%(year, sample.name, region, rate[sel][year][region][sample.name]))
            else:
                logger.info("%i: Yield for sample %s at region %s not cached! Run caching script first"%(year, sample.name, region))
                sys.exit(1)

def setup( year, sel ):

    for i_region, region in enumerate(regions):
        # compute signal yield for this region (this is the final code)

        genRegion = genRegions[i_region]

        logger.info( "At reco region %s", region )
        logger.info( "At gen region %s", genRegion )

        for i_sample, sample in enumerate( mc[sel][year] + [ttGSample[sel][year]] ):
            btagging_uncertainty   [sel][year][region][sample.name] = 1.04# if not i_region else 1.01
            mistagging_uncertainty [sel][year][region][sample.name] = 1.04# if not i_region else 1.01
            jes_uncertainty        [sel][year][region][sample.name] = 1.04# if not i_region else 1.01
            electronId_uncertainty [sel][year][region][sample.name] = 1.04# if not i_region else 1.01
            muonId_uncertainty     [sel][year][region][sample.name] = 1.04# if not i_region else 1.01
                
        # ttgamma (background) SM rates, genRates same for all years
        genSel = "&&".join( [ cutInterpreter.cutString( genSelection[sel] ), genRegion.cutString() ] )
        coeffList[sel][region]        = w[sel].getCoeffListFromDraw( genSignalSample[sel], selectionString=genSel )
        signal_genRateSM[sel][region] = float( w[sel].get_weight_yield( coeffList[sel][region] ) )

        observation[sel][year][region] = int( round( sum( rate[sel][year][region].values() ) ) )

# run initial setup
for sel in args.selections:
    for year in args.years:
        getSMYields(year, sel)
        setup(year, sel)

# run calculations
pool = Pool( processes=args.cores )
_ = pool.map( calculation, points2D )
pool.close()

