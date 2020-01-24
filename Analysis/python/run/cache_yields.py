''' Plot script pTG shape + WC
'''

# Standard imports 
import sys, os, pickle, copy, ROOT

# RootTools
from RootTools.core.standard   import *

# turn off graphics
ROOT.gROOT.SetBatch( True )

# TTGammaEFT
from TTGammaEFT.Tools.user              import cache_directory
from TTGammaEFT.Tools.TriggerSelector   import TriggerSelector
from TTGammaEFT.Tools.cutInterpreter    import cutInterpreter
from TTGammaEFT.Tools.Cache             import Cache
from TTGammaEFT.Analysis.regions        import recoTTGammaRegions as regions
from Analysis.Tools.metFilters          import getFilterCut
from Analysis.Tools.MergingDirDB               import MergingDirDB

# Default Parameter
loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                                help="Log level for logging")
argParser.add_argument('--selection',          action='store',      default='nLepTight1-nLepVeto1-nJet4p-nBTag1p-pTG20-nPhoton1p')
argParser.add_argument('--small',              action='store_true',                                                                                  help='Run only on a small subset of the data?', )
argParser.add_argument('--year',               action='store',      default=None,   type=int,  choices=[2016,2017,2018],                             help="Which year to plot?")
argParser.add_argument('--noData',             action='store_true', default=False,                                                                   help='also plot data?')
argParser.add_argument('--overwrite',          action='store_true',                                                                                  help='Overwrite Database entries?', )
argParser.add_argument('--inclusive',          action='store_true',                                                                                  help='run inclusive regions', )
argParser.add_argument('--manual',             action='store_true',                                                                                  help='run no regions, but add it manually to the selection string', )
argParser.add_argument('--noQCD',              action='store_true',                                                                                  help='run w/o QCD', )
argParser.add_argument('--QCDOnly',            action='store_true',                                                                                  help='run only QCD estimate', )
argParser.add_argument('--checkOnly',          action='store_true',                                                                                  help='Just check if yield is already calculated', )
argParser.add_argument('--cores',              action='store',      default=1,                       type=int,                                       help='number of cpu cores for multicore processing')
argParser.add_argument('--gammaCat',           action='store',      default='all')
argParser.add_argument('--ptBin',              action='store',      default='all')
argParser.add_argument('--mode',               action='store',      default='all')
argParser.add_argument('--sieie',              action='store',      default='all')
argParser.add_argument('--chgIso',             action='store',      default='all')
args = argParser.parse_args()


# Logging
if __name__=="__main__":
    import Analysis.Tools.logger as logger
    logger = logger.get_logger( args.logLevel, logFile=None)
    import RootTools.core.logger as logger_rt
    logger_rt = logger_rt.get_logger( args.logLevel, logFile=None )
else:
    import logging
    logger = logging.getLogger(__name__)


if args.inclusive and not args.manual:
    from TTGammaEFT.Analysis.regions        import recoTTGammaRegionsIncl as regions
elif not args.manual:
    from TTGammaEFT.Analysis.regions        import recoTTGammaRegions     as regions
else:
    regions = ["manual"]

cache_dir = os.path.join(cache_directory, "yields", str(args.year))
yield_dirDB = MergingDirDB( cache_dir )
if not yield_dirDB: raise

#res = "_".join( ["sample", args.selection, "small" if args.small else "full"] )
res = {"sample":None, "selection":args.selection, "mode":args.mode, "ptBin":args.ptBin, "cat":args.gammaCat, "sieie":args.sieie, "chgIso":args.chgIso, "small":args.small}
sel = "-".join( [args.selection, args.mode, args.ptBin, args.gammaCat, args.sieie, args.chgIso ] )

qcdSel = args.selection + "-" + args.gammaCat if args.gammaCat != "all" else args.selection
res["sample"] = "QCD"
cached_QCD = yield_dirDB.contains( frozenset(res.items()) )
if cached_QCD and float(yield_dirDB.get( frozenset(res.items()) )) < 0:
    cached_QCD = False

if not cached_QCD and args.checkOnly:
    logger.info( "Yield for sample QCD not processed" )
if args.checkOnly and args.QCDOnly: sys.exit(0)

if (not args.overwrite) and cached_QCD:
    logger.info( "Yield for sample QCD already in database: %s" %yield_dirDB.get( frozenset(res.items()) ) )
    if args.QCDOnly: sys.exit(0)

elif not args.noQCD:
    # load cached qcd histograms
    qcd_cachedir = os.path.join(cache_directory, "qcdHistos")
    qcd_dirDB    = MergingDirDB(qcd_cachedir)
    if not qcd_dirDB: raise

    if "low" in args.ptBin:
        if args.sieie == "highSieie" and args.chgIso == "lowChgIso":
            plotname = "yield_invSieie_20ptG120"
        elif args.sieie == "lowSieie" and args.chgIso == "highChgIso":
            plotname = "yield_invChgIso_20ptG120"
        elif args.sieie == "highSieie" and args.chgIso == "highChgIso":
            plotname = "yield_invSieie_invChgIso_20ptG120"
        else:
            plotname = "yield_20ptG120"
         
    elif "med" in args.ptBin:
        if args.sieie == "highSieie" and args.chgIso == "lowChgIso":
            plotname = "yield_invSieie_120ptG220"
        elif args.sieie == "lowSieie" and args.chgIso == "highChgIso":
            plotname = "yield_invChgIso_120ptG220"
        elif args.sieie == "highSieie" and args.chgIso == "highChgIso":
            plotname = "yield_invSieie_invChgIso_120ptG220"
        else:
            plotname = "yield_120ptG220"

    elif "high" in args.ptBin:
        if args.sieie == "highSieie" and args.chgIso == "lowChgIso":
            plotname = "yield_invSieie_220ptGinf"
        elif args.sieie == "lowSieie" and args.chgIso == "highChgIso":
            plotname = "yield_invChgIso_220ptGinf"
        elif args.sieie == "highSieie" and args.chgIso == "highChgIso":
            plotname = "yield_invSieie_invChgIso_220ptGinf"
        else:
            plotname = "yield_220ptGinf"

    else:
        if args.sieie == "highSieie" and args.chgIso == "lowChgIso":
            plotname = "yield_invSieie"
        elif args.sieie == "lowSieie" and args.chgIso == "highChgIso":
            plotname = "yield_invChgIso"
        elif args.sieie == "highSieie" and args.chgIso == "highChgIso":
            plotname = "yield_invSieie_invChgIso"
        else:
            plotname = "yield"

    modes  = [ "e", "mu" ] if args.mode == "all" else [args.mode]
    rate   = 0

    for mode in modes:
        qcd_res = "_".join( ["qcdHisto", qcdSel, plotname, str(args.year), mode, "small" if args.small else "full"] + map( str, [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ] ) )
#        if args.sieie != "all" or args.chgIso != "all" or args.ptBin not in ["all", "lowPT", "medPT", "highPT"]:
#            logger.info( "No QCD histogram found for sieie or chgIso bins" )
#            rate = -1
#            break

        if not qcd_dirDB.contains( qcd_res ):
            logger.info( "No QCD histogram found in database: %s" %qcd_res )
            rate = -1
            break

        qcdHist = qcd_dirDB.get( qcd_res )
        rate   += qcdHist.Integral() 

    logger.info("Adding yield for sample QCD: %f"%rate)
    yield_dirDB.add( frozenset(res.items()), str(rate), overwrite=True )

    if args.QCDOnly: sys.exit(0)

# Samples
if args.year == 2016:
    from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed      import *
    if not args.noData:
        from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import *

elif args.year == 2017:
    from TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed        import *
    if not args.noData:
        from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import *

elif args.year == 2018:
    from TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed      import *
    if not args.noData:
        from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import *

# Sample definition
if args.year == 2016:
    mc = [ TTG_16, TT_pow_16, DY_LO_16, WJets_16, WG_16, ZG_16, rest_16]#, QCD_16 ]
#    if not args.noQCD:
#        all   = all_noQCD_16
#        qcd   = QCD_16
#        gjets = GJets_16

elif args.year == 2017:
    mc = [ TTG_17, TT_pow_17, DY_LO_17, WJets_17, WG_17, ZG_17, rest_17]#, QCD_17 ]
#    if not args.noQCD:
#        all   = all_noQCD_17
#        qcd   = QCD_17
#        gjets = GJets_17

elif args.year == 2018:
    mc = [ TTG_18, TT_pow_18, DY_LO_18, WJets_18, WG_18, ZG_18, rest_18]#, QCD_18 ]
#    if not args.noQCD:
#        all   = all_noQCD_18
#        qcd   = QCD_18
#        gjets = GJets_18



filterCutData = getFilterCut( args.year, isData=True, skipBadChargedCandidate=True )
filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )
tr = TriggerSelector( args.year, singleLepton=args.selection.count("nLepTight") )
triggerCutMc  = tr.getSelection( "MC" )


if args.noData:
    if args.year == 2016:   lumi_scale = 35.92
    elif args.year == 2017: lumi_scale = 41.53
    elif args.year == 2018: lumi_scale = 59.74
    allSamples = mc
else:
    if args.year == 2016:   data_sample = Run2016
    elif args.year == 2017: data_sample = Run2017
    elif args.year == 2018: data_sample = Run2018
    data_sample.texName        = "data (legacy)"
    data_sample.name           = "data"
    lumi_scale                 = data_sample.lumi * 0.001
#    data_sample.setWeightString("weight")
#    data_sample.setSelectionString( [ filterCutData, cutInterpreter.cutString( args.selection ) ] )
    allSamples = [data_sample] + mc

weightString = "(weight*%f*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF)"%lumi_scale
#try to create a weightString which gives a SF of 2.25 to misID photon events for QCD estimate
#fancyWeightString = weightString + "+" + weightString + "*(PhotonGood0_photonCat==2)*1.25"

#for sample in mc:
#    sample.setWeightString(weightString)
#    if not "QCD" in sample.name:
#        sample.setSelectionString( [ filterCutMc, triggerCutMc, cutInterpreter.cutString( args.selection ), "overlapRemoval==1" ] )

#if not args.noQCD:
#    all.setWeightString(weightString)
#    qcd.setWeightString(weightString)
#    gjets.setWeightString(weightString)

if args.small:
    for sample in allSamples:
        sample.normalization=1.
        sample.reduceFiles( factor=15 )
#        sample.addWeightString("%f"%(1./sample.normalization))

replaceSelection = {
    "nLeptonTight":    "nLeptonTightInvIso",
    "nMuonTight":      "nMuonTightInvIso",
    "nElectronTight":  "nElectronTightInvIso",
    "mLtight0Gamma":   "mLinvtight0Gamma",
}


def cacheYields( (i_region, i_sample) ):
#def cacheYields( i_sample ):

    region = regions[i_region]
    sample = allSamples[i_sample]

    if sample.name==data_sample.name and args.gammaCat != "all": return
#    if ("QCD" in sample.name and args.noQCD) or ("QCD" in sample.name and args.noData): return
#    if not "QCD" in sample.name and args.QCDOnly: return

    logger.info( "At region %s for sample %s"%(region, sample.name) )

    res["sample"] = sample.name

    if yield_dirDB.contains( frozenset(res.items()) ) and not args.overwrite:
        if not args.checkOnly:
            logger.info( "Yield for sample %s at region %s already in database: %s" %(sample.name, region, yield_dirDB.get( frozenset(res.items()) ) ) )
            print "Yield for sample %s at region %s already in database: %s" %(sample.name, region, yield_dirDB.get( frozenset(res.items()) ) ) 
        return

    if args.checkOnly:
        logger.info( "Yield for sample %s at region %s not processed" %(sample.name, region) )
        return

#    if "QCD" in sample.name:
#        qcdSelection       = "-".join( [ item if not "nBTag" in item else "nBTag0" for item in args.selection.split("-") ] + ["nBTag0"] )
#        qcdSelection       = "-".join( [ item for item in qcdSelection.split("-") if not "photoncat" in item and not "photonhadcat" in item and not "nLepVeto" in item ] )
#        preSelectionSR     = [ cutInterpreter.cutString( args.selection ), filterCutMc, triggerCutMc, "overlapRemoval==1" ]
#        preSelectionCR     = [ cutInterpreter.cutString( qcdSelection ),   filterCutMc, triggerCutMc, "overlapRemoval==1" ]
#        preSelectionCRData = [ cutInterpreter.cutString( qcdSelection ),   filterCutData ]
#        if region != "manual":
#            preSelectionSR     += [ region.cutString() ]
#            preSelectionCR     += [ region.cutString() ]
#            preSelectionCRData += [ region.cutString() ]

#        preSelectionSR     = "&&".join( preSelectionSR )
#        preSelectionCR     = "&&".join( preSelectionCR )
#        preSelectionCRData = "&&".join( preSelectionCRData )
#        for key, val in replaceSelection.items():
#            preSelectionCR     = preSelectionCR.replace(key, val)
#            preSelectionCRData = preSelectionCRData.replace(key, val)

#        yield_QCD_CR  = qcd.getYieldFromDraw(   selectionString=preSelectionCR, weightString=weightString )["val"]
#        yield_QCD_CR += gjets.getYieldFromDraw( selectionString=preSelectionCR, weightString=weightString )["val"]
#        yield_QCD_SR  = qcd.getYieldFromDraw(   selectionString=preSelectionSR, weightString=weightString )["val"]
#        yield_QCD_SR += gjets.getYieldFromDraw( selectionString=preSelectionSR, weightString=weightString )["val"]

#        transFacQCD    = yield_QCD_SR / yield_QCD_CR if yield_QCD_CR != 0 else 0
#        rate = 0

#        if transFacQCD != 0:
#            datCR        = data_sample.getYieldFromDraw( selectionString=preSelectionCRData, weightString="weight" )['val']

#            mcNoQCDTotal = 0
#            for s in mc:
#                if "QCD" in s.name: continue
#                y  = s.getYieldFromDraw( selectionString=preSelectionCR, weightString=fancyWeightString )['val']
#                if "DY" in s.name: y *= 1.17 #hard coded DY Scale Factor for QCD estimate
#                mcNoQCDTotal += y
#            rate = int(round( (datCR - mcNoQCDTotal) * transFacQCD ))

#    else:

    if sample.name == data_sample.name: 
        selection  = [ filterCutData, cutInterpreter.cutString( sel ) ]
    else:
        selection  = [ filterCutMc, triggerCutMc, cutInterpreter.cutString( sel ), "overlapRemoval==1" ]
    if region != "manual":
        selection += [ region.cutString() ]
    selectionString = "&&".join( selection )

    rate = sample.getYieldFromDraw( selectionString=selectionString, weightString=weightString if sample.name != data_sample.name else "weight")['val']

    logger.info("Adding yield for sample %s at region %s: %s"%(sample.name, str(region), str(rate)) )
    yield_dirDB.add( frozenset(res.items()), str(rate), overwrite=True )

# Multiprocessing
from multiprocessing import Pool

if not args.manual:
    for region in regions:
        region.name = str(region) # needed for Pool

# Objects can't be pickled, so args are indices of lists
input = [ (i_region, i_sample) for i_region, _ in enumerate(regions) for i_sample, _ in enumerate(allSamples) ]
#input = [ (i_region, 0) for i_region, _ in enumerate(regions) ]#for i_sample, _ in enumerate(allSamples) ]

logger.info( "Calculating %i yields for selection string %s"%(len(input), sel) )

pool = Pool( processes=args.cores )
_    = pool.map( cacheYields, input )
pool.close()

