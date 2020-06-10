#!/usr/bin/env python

import os, copy, time, pickle
import ROOT
from shutil                              import copyfile
from math                                import sqrt
from helpers                             import uniqueKey

from TTGammaEFT.Analysis.EstimatorList   import EstimatorList
from TTGammaEFT.Analysis.Setup           import Setup
from TTGammaEFT.Analysis.DataObservation import DataObservation
from TTGammaEFT.Analysis.MCBasedEstimate import MCBasedEstimate
from TTGammaEFT.Analysis.regions         import regionsTTG, noPhotonRegionTTG, inclRegionsTTG, regionsTTGfake, inclRegionsTTGfake, chgIso_thresh, chgIsoRegions, gammaPT_thresholds, mLgRegions
from TTGammaEFT.Analysis.SetupHelpers    import *

from TTGammaEFT.Tools.user               import cache_directory, combineReleaseLocation, cardfileLocation
from Analysis.Tools.MergingDirDB         import MergingDirDB
from Analysis.Tools.u_float              import u_float
from Analysis.Tools.cardFileWriter       import cardFileWriter
from Analysis.Tools.getPostFit           import getPrePostFitFromMLF, getFitResults
from TTGammaEFT.Tools.cutInterpreter     import cutInterpreter

# load and define the EFT sample
from TTGammaEFT.Samples.genTuples_TTGamma_EFT_postProcessed  import *
eftSample = TTG_4WC_ref

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

# Arguments
import argparse
argParser=argparse.ArgumentParser(description="Argument parser" )
argParser.add_argument( "--logLevel",           action="store",      default="INFO",            choices=loggerChoices,      help="Log level for logging" )
argParser.add_argument( "--label",              action="store",      default="defaultSetup",    type=str,                   help="Label of results directory" )
argParser.add_argument( "--inclRegion",         action="store_true",                                                        help="use inclusive photon pt region" )
argParser.add_argument( "--overwrite",          action="store_true",                                                        help="Overwrite existing output files" )
argParser.add_argument( "--useRegions",         action="store",      nargs='*',       type=str, choices=allRegions.keys(),  help="Which regions to use?" )
argParser.add_argument( "--useChannels",        action="store",      nargs='*', default="all",   type=str, choices=["e", "mu", "all", "comb"], help="Which lepton channels to use?" )
argParser.add_argument( "--addVGSF",            action="store_true",                                                        help="add default DY scale factor" )
argParser.add_argument( "--addZGSF",            action="store_true",                                                        help="add default DY scale factor" )
argParser.add_argument( "--addWGSF",            action="store_true",                                                        help="add default DY scale factor" )
argParser.add_argument( "--addDYSF",            action="store_true",                                                        help="add default DY scale factor" )
argParser.add_argument( "--addWJetsSF",         action="store_true",                                                        help="add default DY scale factor" )
argParser.add_argument( "--addFakeSF",          action="store_true",                                                        help="add default fake scale factor" )
argParser.add_argument( "--addMisIDSF",         action="store_true",                                                        help="add default misID scale factor" )
argParser.add_argument( "--addSSM",             action="store_true",                                                        help="add default signal strength modifer" )
argParser.add_argument( "--keepCard",           action="store_true",                                                        help="Overwrite existing output files" )
argParser.add_argument( "--expected",           action="store_true",                                                        help="Use sum of backgrounds instead of data." )
argParser.add_argument( "--useTxt",             action="store_true",                                                        help="Use txt based cardFiles instead of root/shape based ones?" )
argParser.add_argument( "--skipFitDiagnostics", action="store_true",                                                        help="Don't do the fitDiagnostics (this is necessary for pre/postfit plots, but not 2D scans)?" )
argParser.add_argument( "--significanceScan",   action="store_true",                                                        help="Calculate significance instead?")
argParser.add_argument( "--year",               action="store",      default=2016,   type=int,                              help="Which year?" )
argParser.add_argument( "--runOnLxPlus",        action="store_true",                                                        help="Change the global redirector of samples")
argParser.add_argument( "--misIDPOI",           action="store_true",                                                        help="Change POI to misID SF")
argParser.add_argument( "--vgPOI",              action="store_true",                                                        help="Change POI to misID SF")
argParser.add_argument( "--ttPOI",              action="store_true",                                                        help="Change POI to misID SF")
argParser.add_argument( "--wJetsPOI",           action="store_true",                                                        help="Change POI to misID SF")
argParser.add_argument( "--checkOnly",          action="store_true",                                                        help="Check the SF only")
argParser.add_argument( "--bkgOnly",            action="store_true",                                                        help="background only")
argParser.add_argument( "--unblind",            action="store_true",                                                        help="unblind 2017/2018")
argParser.add_argument( "--plot",               action="store_true",                                                        help="run plots?")
argParser.add_argument('--order',              action='store',      default=2, type=int,                                                             help='Polynomial order of weight string (e.g. 2)')  
argParser.add_argument('--parameters',         action='store',      default=['ctZI', '2', 'ctWI', '2', 'ctZ', '2', 'ctW', '2'], type=str, nargs='+', help = "argument parameters")
argParser.add_argument('--mode',               action='store',      default="all", type=str, choices=["mu", "e", "all"],               help="plot lepton mode" )
args=argParser.parse_args()

# Logging
import Analysis.Tools.logger as logger
logger = logger.get_logger(       args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

if args.useChannels and "comb" in args.useChannels: args.useChannels += ["mu", "e"]
if args.useChannels and "e"    in args.useChannels: args.useChannels += ["eetight"]
if args.useChannels and "mu"   in args.useChannels: args.useChannels += ["mumutight"]
if args.useChannels and "all"  in args.useChannels: args.useChannels  = None

# read the EFT parameters
EFTparams = []
if args.parameters:
    coeffs = args.parameters[::2]
    str_vals = args.parameters[1::2]
    for i_param, (coeff, str_val, ) in enumerate(zip(coeffs, str_vals)):
        EFTparams.append(coeff)
        EFTparams.append(str_val)

eft =  "_".join(EFTparams)

useCache = True
if args.keepCard:
    args.overwrite = False

def replaceDictKey( dict, fromKey, toKey ):
    dict[toKey] = copy.copy(dict[fromKey])
    del dict[fromKey]
    return dict

regionNames = []
if not args.checkOnly:
    # Define estimators for CR
    default_setup            = Setup( year=args.year, runOnLxPlus=args.runOnLxPlus, checkOnly=True )
    default_setup.estimators = EstimatorList( default_setup )
    default_setup.data       = default_setup.processes["Data"]
#    default_setup.processes  = default_setup.estimators.constructProcessDict( processDict=default_processes )
    default_setup.processes["Data"] = default_setup.data
    default_setup.addon      = ""
    default_setup.regions    = inclRegionsTTG if args.inclRegion else regionsTTG

    default_photon_setup            = Setup( year=args.year, photonSelection=True, runOnLxPlus=args.runOnLxPlus, checkOnly=True )
    default_photon_setup.estimators = EstimatorList( default_photon_setup )
    default_photon_setup.data       = default_photon_setup.processes["Data"]
#    default_photon_setup.processes  = default_setup.estimators.constructProcessDict( processDict=default_processes )
    default_photon_setup.processes["Data"] = default_photon_setup.data
    default_photon_setup.addon      = ""
    default_photon_setup.regions    = inclRegionsTTG if args.inclRegion else regionsTTG

# Define SR, CR, channels and regions
with0pCR = False
with1pCR = False
setups = []
for key, val in allRegions.items():
    if not key in args.useRegions: continue
    if key not in limitOrdering:
        limitOrdering += [key]

    if args.checkOnly:
        locals()["setup"+key] = None
        continue

    if val["noPhotonCR"]: with0pCR = True
    else:                 with1pCR = True

    locals()["setup"+key]              = default_setup.sysClone( parameters=val["parameters"] ) if val["noPhotonCR"] else default_photon_setup.sysClone( parameters=val["parameters"] )
    estimators                         = EstimatorList( locals()["setup"+key] )
    locals()["setup"+key].name         = key
    locals()["setup"+key].channels     = val["channels"] #default_setup.channels
    locals()["setup"+key].noPhotonCR   = val["noPhotonCR"]
    locals()["setup"+key].signalregion = "SR" in key
    locals()["setup"+key].regions      = val["inclRegion" if args.inclRegion else "regions"]
    locals()["setup"+key].data         = default_setup.data if val["noPhotonCR"] else default_photon_setup.data
    locals()["setup"+key].processes    = estimators.constructProcessDict( processDict=val["processes"] ) if "processes" in val else default_setup.processes if val["noPhotonCR"] else default_photon_setup.processes
    locals()["setup"+key].processes["Data"] = locals()["setup"+key].data
    locals()["setup"+key].addon      = key

# sort regions accoring to ordering
for reg in limitOrdering:
    if "setup"+reg in locals():
        regionNames.append(reg)
        setups.append(locals()["setup"+reg])

# use the regions as key for caches
regionNames.sort()
if args.addWJetsSF:  regionNames.append("addWJetsSF")
if args.addDYSF:     regionNames.append("addDYSF")
if args.addVGSF:     regionNames.append("addVGSF")
if args.addWGSF:     regionNames.append("addWGSF")
if args.addZGSF:     regionNames.append("addZGSF")
if args.addSSM:      regionNames.append("addSSM")
if args.addMisIDSF:  regionNames.append("addMisIDSF")
if args.addFakeSF:   regionNames.append("addFakeSF")
if args.misIDPOI:    regionNames.append("misIDPOI")
if args.vgPOI:       regionNames.append("vgPOI")
if args.wJetsPOI:    regionNames.append("wJetsPOI")
if args.ttPOI:       regionNames.append("ttPOI")
if args.useChannels: regionNames.append("_".join([ch for ch in args.useChannels if not "tight" in ch]))

baseDir       = os.path.join( cache_directory, "analysis",  str(args.year), "limits" )
limitDir      = os.path.join( baseDir, "cardFiles", args.label, "expected" if args.expected else "observed" )
if not os.path.exists( limitDir ): os.makedirs( limitDir )

cacheFileName = os.path.join( baseDir, "calculatednll" )
nllCache      = MergingDirDB( cacheFileName )

cacheFileName   = os.path.join( baseDir, "calculatedLimits" )
limitCache      = MergingDirDB( cacheFileName )

cacheFileName   = os.path.join( baseDir, "calculatedSignifs" )
signifCache     = MergingDirDB( cacheFileName )

cacheDir        = os.path.join( cache_directory, "modelling",  str(args.year) )

cacheFileName   = os.path.join( cacheDir, "Scale" )
scaleUncCache   = MergingDirDB( cacheFileName )

cacheFileName   = os.path.join( cacheDir, "PDF" )
pdfUncCache     = MergingDirDB( cacheFileName )

cacheFileName   = os.path.join( cacheDir, "PS" )
psUncCache      = MergingDirDB( cacheFileName )

baseDir       = os.path.join( cache_directory, "analysis", "eft" )
cacheFileName = os.path.join( baseDir, eftSample.name )
yieldCache    = MergingDirDB( cacheFileName )


def getScaleUnc(name, r, channel, setup):
    key      = uniqueKey( name, r, channel, setup ) + tuple(str(args.year))
    scaleUnc = scaleUncCache.get( key )
    return max(0.001, scaleUnc)

def getPDFUnc(name, r, channel, setup):
    key    = uniqueKey( name, r, channel, setup ) + tuple(str(args.year))
    PDFUnc = pdfUncCache.get( key )
    return max(0.001, PDFUnc)

def getPSUnc(name, r, channel, setup):
    key   = uniqueKey( name, r, channel, setup ) + tuple(str(args.year))
    PSUnc = psUncCache.get( key )
    return max(0.001, PSUnc)

configlist = regionNames + EFTparams
configlist.append("incl" if args.inclRegion else "diff")
configlist.append("expected" if args.expected else "observed")

sConfig = "_".join(configlist)
print nllCache.get(sConfig)
print nllCache.contains(sConfig)
if not args.overwrite and nllCache.contains( sConfig ): sys.exit(0)
print sConfig

def wrapper():
    c = cardFileWriter.cardFileWriter()
    c.releaseLocation = combineReleaseLocation
    
    cardFileNameTxt   = os.path.join( limitDir, "_".join( regionNames ), eft + ".txt" )
    cardFileNameShape = cardFileNameTxt.replace( ".txt", "_shape.root" )
    cardFileName      = cardFileNameTxt
    if ( not os.path.exists(cardFileNameTxt) or ( not os.path.exists(cardFileNameShape) and not args.useTxt ) ) or args.overwrite:

        if args.checkOnly:
            print cardFileNameShape
            logger.info("Combine Card not found. Please run without --checkOnly first!")
            return

        counter=0
        c.reset()
        c.setPrecision(3)
        shapeString     = "lnN" if args.useTxt else "shape"
        # experimental
        c.addUncertainty( "PU",            shapeString)
        c.addUncertainty( "JEC",           shapeString)
        c.addUncertainty( "JER",           shapeString)
        c.addUncertainty( "SFb",           shapeString)
        c.addUncertainty( "SFl",           shapeString)
        c.addUncertainty( "trigger",       shapeString)
        c.addUncertainty( "leptonSF",      shapeString)
        c.addUncertainty( "leptonTrackSF", shapeString)
        c.addUncertainty( "photonSF",      shapeString)
        c.addUncertainty( "eVetoSF",       shapeString)
        c.addUncertainty( "prefireSF",     shapeString)
        # theory (PDF, scale, ISR)
        c.addUncertainty( "Tune",          shapeString)
        c.addUncertainty( "erdOn",         shapeString)
        c.addUncertainty( "Scale",         shapeString)
        c.addUncertainty( "PDF",           shapeString)
        c.addUncertainty( "PS",            shapeString)
#        c.addUncertainty( "ISR",           shapeString)

        default_QCD_unc = 0.5
        c.addUncertainty( "QCD_norm", shapeString )
#        c.addUncertainty( "QCD_TF", shapeString )
#        c.addUncertainty( "QCD_lowMlg", shapeString )

        # Only if TT CR is used
        default_TT_unc = 0.05
        if any( [name=="TT3" or name=="TT4p" for name in args.useRegions] ) and not with1pCR:
            c.addFreeParameter('TT', 1, '[0.8,1.2]')
        else:
            c.addUncertainty( "TT_norm", shapeString )
                
        default_HadFakes_unc = 0.05
#        c.addUncertainty( "Fakes_norm",      shapeString )
        default_HadCorr_unc = 0.05
        addFakeUnc = False
        if any( ["fake" in name for name in args.useRegions] ):
            addFakeUnc = True
            c.addUncertainty( "fake_highSieie",  shapeString )
            c.addUncertainty( "fake_lowSieie",   shapeString )
            for i_iso, iso in enumerate(chgIsoRegions):
                print i_iso, iso
                c.addUncertainty( "fake_corr_%i"%i_iso,   shapeString )                

        if not args.vgPOI and with1pCR:
#            c.addFreeParameter('ZG', 1, '[0.5,1.5]')
            c.addFreeParameter('WG', 1, '[0.5,1.5]')

#        default_WG_unc    = 0.30
#        c.addUncertainty( "WG_norm",      shapeString )

        default_ZG_unc    = 0.2
        c.addUncertainty( "ZG_norm",      shapeString )

        default_Other_unc    = 0.15
        c.addUncertainty( "Other_norm",      shapeString )

#        default_ZG3_unc    = 0.15
#        c.addUncertainty( "ZG_nJet",      shapeString )

#        default_misID4p_unc    = 0.1
#        c.addUncertainty( "misID4p",      shapeString )

        default_TTGpT_unc    = 0.1
        if not args.inclRegion and with1pCR:
            for i in range(len(gammaPT_thresholds)-1):
                c.addUncertainty( "TTG_pTBin%i"%i, shapeString )

        # Only if WJets CR is used
        default_WJets_unc    = 0.2
        if any( ["WJets3" in name or "WJets4p" in name for name in args.useRegions] ) and not with1pCR:
            c.addFreeParameter('WJets', 1, '[0.5,1.5]')
        else:
            c.addUncertainty( "WJets_norm", shapeString )

        default_DY_unc    = 0.1
        if any( [ name in ["DY2","DY3","DY4","DY4p","DY5"] for name in args.useRegions] ) and not with1pCR:
            c.addFreeParameter('DY', 1, '[0.5,1.5]')
        else:
            c.addUncertainty( "DY_norm", shapeString )

        if not args.addMisIDSF and not args.misIDPOI and with1pCR:
            c.addFreeParameter('misID', 1, '[0,5]')
        elif not args.misIDPOI and with1pCR:
            c.addFreeParameter('misID', 1, '[0,2]')

        for setup in setups:
            observation = DataObservation( name="Data", process=setup.data, cacheDir=setup.defaultCacheDir() )
            for pName, pList in setup.processes.items():
                if pName == "Data": continue
                for e in pList:
                    e.initCache( setup.defaultCacheDir() )

            for r in setup.regions:
                for i_ch, channel in enumerate(setup.channels):
                    if args.useChannels and channel not in args.useChannels: continue

                    niceName      = " ".join( [ channel, str(r), setup.addon ] )
                    binname       = "Bin%i"%counter
                    total_exp_bkg = 0

                    if args.misIDPOI:
                        c.addBin( binname, [ pName.replace("signal","TTG") for pName in setup.processes.keys() if not "misID" in pName and pName != "Data" ], niceName)
                    elif args.vgPOI:
                        c.addBin( binname, [ pName.replace("signal","TTG") for pName in setup.processes.keys() if not "WG" in pName and not "ZG" in pName and not "VG" in pName and pName != "Data" ], niceName)
                    elif args.ttPOI:
                        c.addBin( binname, [ pName.replace("signal","TTG") for pName in setup.processes.keys() if not "TT" in pName and pName != "Data" ], niceName)
                    elif args.wJetsPOI:
                        c.addBin( binname, [ pName.replace("signal","TTG") for pName in setup.processes.keys() if not "WJets" in pName and pName != "Data" ], niceName)
                    else:
                        c.addBin( binname, [ pName for pName in setup.processes.keys() if pName != "signal" and pName != "Data" ], niceName)
    
                    counter      += 1

                    mute   = False
                    sigExp = u_float(0.,0.)
                    sigUnc = {}
                    for pName, pList in setup.processes.items():

                        #yields einlesen und ratio berechnen
                        smyieldkey  =  (setup.name, str(r),channel,  "ctZ_0_ctZI_0")
                        smyield     =  yieldCache.get(smyieldkey)["val"]
                        yieldkey    =  (setup.name, str(r),channel, str(eft))
                        if yieldCache.contains( yieldkey ): 
                            ratio       =  yieldCache.get(yieldkey)["val"]
                        else:
                            raise Exception("yieldCache does not contain key")
                        
                        if smyield > 0: ratio /= smyield
                        else: ratio = 1 

                            
                        print ratio
                        if pName == "Data": continue
                        misIDPOI = "misID" in pName and args.misIDPOI
                        vgPOI    = ("WG" in pName or "ZG" in pName or "VG" in pName) and args.vgPOI
                        wJetsPOI = "WJets" in pName and args.wJetsPOI
                        ttPOI    = "TT"    in pName and not "TTG" in pName and args.ttPOI

                        newPOI_input = any( [args.misIDPOI, args.vgPOI, args.wJetsPOI, args.ttPOI] )
                        newPOI       = any( [misIDPOI, vgPOI, wJetsPOI, ttPOI] )
                        
                        if newPOI_input and pName == "signal":
                            pName = "TTG"

                        signal   = True if newPOI else pName == "signal"
                        expected = u_float(0.,0.)

                        for e in pList:                           
                            exp_yield = e.cachedEstimate( r, channel, setup )
                            if signal: exp_yield *= ratio
                            if signal and args.addSSM:
                                exp_yield *= SSMSF_val[args.year].val
                                logger.info( "Scaling signal by %f"%(SSMSF_val[args.year].val) )
                            if e.name.count( "WJets" ) and args.addWJetsSF:
                                exp_yield *= WJetsSF_val[args.year].val
                                logger.info( "Scaling WJets background %s by %f"%(e.name,WJetsSF_val[args.year].val) )
                            if e.name.count( "DY" ) and args.addDYSF:
                                exp_yield *= DYSF_val[args.year].val
                                logger.info( "Scaling DY background %s by %f"%(e.name,DYSF_val[args.year].val) )
                            if e.name.count( "WG" ) and args.addWGSF:
                                exp_yield *= WGSF_val[args.year].val
                                logger.info( "Scaling WG background %s by %f"%(e.name,WGSF_val[args.year].val) )
                            if e.name.count( "ZG" ) and args.addZGSF:
                                exp_yield *= ZGSF_val[args.year].val
                                logger.info( "Scaling ZG background %s by %f"%(e.name,ZGSF_val[args.year].val) )
                            if e.name.count( "misID" ) and args.addMisIDSF:
                                exp_yield *= misIDSF_val[args.year].val
                                logger.info( "Scaling misID background %s by %f"%(e.name,misIDSF_val[args.year].val) )
                            if e.name.count( "had" ) and args.addFakeSF:
                                exp_yield *= fakeSF_val[args.year].val
                                logger.info( "Scaling fake background %s by %f"%(e.name,fakeSF_val[args.year].val) )
                            e.expYield = exp_yield
                            expected  += exp_yield

                        logger.info( "Expectation for process %s: %s", pName, expected.val )

                        if newPOI_input and signal:
                            sigExp += expected
                            logger.info( "Adding expectation for process %s to signal. Total signal now: %s", pName, sigExp )
                        else:
                            c.specifyExpectation( binname, pName, expected.val )

                        if signal: total_exp_bkg += (expected.val/ratio)
                        else: total_exp_bkg += expected.val

                        if signal and expected.val <= 0.01: mute = True

                        tune, erdOn, pu, jec, jer, sfb, sfl, trigger, lepSF, lepTrSF, phSF, eVetoSF, pfSF = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                        ps, scale, pdf, isr = 0, 0, 0, 0
                        qcdTF3, qcdTF4 = 0, 0
                        dyGenUnc, ttGenUnc, vgGenUnc, wjetsGenUnc, otherGenUnc, qcdhigh, misIDUnc, lowSieieUnc, highSieieUnc, misIDPtUnc = 0, 0, 0, 0, 0, 0.001, 0, 0.001, 0.001, 0.001
                        wg, zg, misID4p, zg3, misIDUnc, qcdUnc, vgUnc, wgUnc, zgUnc, dyUnc, ttUnc, wjetsUnc, other0pUnc, otherUnc = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                        for i in range(len(gammaPT_thresholds)-1):
                            locals()["ttg_bin%i_unc"%i] = 0

                        def getSFUncertainty( proc_yield, sf ):
                            up   = proc_yield * (1 + sf.sigma/sf.val)
                            down = proc_yield * (1 - sf.sigma/sf.val)
                            return abs(0.5*(up-down)/proc_yield) if proc_yield > 0 else max(up,down)

                        fakeCorrUnc = []
                        for i_iso, iso in enumerate(chgIsoRegions):
                            fakeCorrUnc.append(0)
                        if expected.val:
                            for e in pList:
                                y_scale   = e.expYield.val / expected.val

                                if e.name.count( "QCD" ):
                                    qcdUnc   += y_scale * default_QCD_unc
                                    qcdTF3   += y_scale * e.expYield.sigma / e.expYield.val
                                    if mLgRegions[0].cutString() in r.cutString() and channel=="e":
                                        qcdhigh   += y_scale * default_QCD_unc
                                    continue # no systematics for data-driven QCD

                                if not args.inclRegion and not newPOI_input and ((e.name.count( "signal" ) and setup.signalregion) or counter==1):
                                        pT_index = max( [ i_pt if ptCut.cutString() in r.cutString() else -1 for i_pt, ptCut in enumerate(regionsTTG) ] )
                                        if pT_index >= 0:
                                            locals()["ttg_bin%i_unc"%pT_index] = y_scale * default_TTGpT_unc
                                if e.name.count( "other" ):
                                    otherUnc += y_scale * default_Other_unc
                                if any( ["fake" in name for name in args.useRegions] ):
                                    if "low" in setup.name and e.name.count( "_had" ):
                                        lowSieieUnc += y_scale * default_HadFakes_unc #getSFUncertainty( proc_yield=e.expYield.val, sf=fakeSF_val[args.year] )
                                    if "high" in setup.name and e.name.count( "_had" ):
                                        highSieieUnc += y_scale * default_HadFakes_unc #getSFUncertainty( proc_yield=e.expYield.val, sf=fakeSF_val[args.year] )
#                                    if e.name.count( "_had" ):
#                                        hadFakesUnc += y_scale * default_HadFakes_unc #getSFUncertainty( proc_yield=e.expYield.val, sf=fakeSF_val[args.year] )
                                    for i_iso, iso in enumerate(chgIsoRegions):
                                        if iso.cutString() in r.cutString():
                                            fakeCorrUnc[i_iso] += y_scale * default_HadCorr_unc
                                        if not "fake" in setup.name and i_iso == 0 and e.name.count( "_had" ):
                                            fakeCorrUnc[i_iso] += y_scale * default_HadCorr_unc

                                if e.name.count( "ZG" ):
                                    zg += y_scale * default_ZG_unc

#                                if e.name.count( "WG" ):
#                                    wg += y_scale * default_WG_unc

#                                if e.name.count( "ZG" ) and "3" in setup.name:
#                                    zg3 += y_scale * default_ZG3_unc
#                                elif e.name.count( "ZG" ):
#                                    zg3 += y_scale * 0.001

#                                if e.name.count( "misID" ) and "4p" in setup.name:
#                                    misID4p += y_scale * default_misID4p_unc
#                                elif e.name.count( "misID" ):
#                                    misID4p += y_scale * 0.001

                                if signal and not newPOI_input:
                                    tune    += y_scale * e.TuneSystematic(    r, channel, setup ).val
                                    erdOn   += y_scale * e.ErdOnSystematic(   r, channel, setup ).val
                                    scale   += y_scale * getScaleUnc( e.name, r, channel, setup )
                                    pdf     += y_scale * getPDFUnc(   e.name, r, channel, setup )
                                    ps      += y_scale * getPSUnc(    e.name, r, channel, setup )

                                pu      += y_scale * e.PUSystematic(                   r, channel, setup ).val
                                jec     += y_scale * e.JECSystematic(                  r, channel, setup ).val
                                jer     += y_scale * e.JERSystematic(                  r, channel, setup ).val
                                sfb     += y_scale * e.btaggingSFbSystematic(          r, channel, setup ).val
                                sfl     += y_scale * e.btaggingSFlSystematic(          r, channel, setup ).val
                                trigger += y_scale * e.triggerSystematic(              r, channel, setup ).val
                                lepSF   += y_scale * e.leptonSFSystematic(             r, channel, setup ).val
                                lepTrSF += y_scale * e.leptonTrackingSFSystematic(     r, channel, setup ).val
                                phSF    += y_scale * e.photonSFSystematic(             r, channel, setup ).val
                                eVetoSF += y_scale * e.photonElectronVetoSFSystematic( r, channel, setup ).val
                                pfSF    += y_scale * e.L1PrefireSystematic(            r, channel, setup ).val


                        def addUnc( c, name, binname, pName, unc, unc_yield, signal ):
                            if newPOI_input and signal:
                                if name in sigUnc: sigUnc[name] += u_float(0,unc)*unc_yield
                                else:              sigUnc[name]  = u_float(0,unc)*unc_yield
                            else:
                                c.specifyUncertainty( name, binname, pName, 1 + unc )

                        if scale: # and setup.signalregion:
                            addUnc( c, "Scale",         binname, pName, scale,   expected.val, signal )
                        if pdf: # and setup.signalregion:
                            addUnc( c, "PDF",           binname, pName, pdf,     expected.val, signal )
                        if erdOn: # and setup.signalregion:
                            addUnc( c, "erdOn",         binname, pName, erdOn,   expected.val, signal )
                        if tune: # and setup.signalregion:
                            addUnc( c, "Tune",          binname, pName, tune,    expected.val, signal )
                        if ps: # and setup.signalregion:
                            addUnc( c, "PS",          binname, pName, tune,    expected.val, signal )
                        addUnc( c, "PU",            binname, pName, pu,      expected.val, signal )
                        addUnc( c, "JEC",           binname, pName, jec,     expected.val, signal )
                        addUnc( c, "JER",           binname, pName, jer,     expected.val, signal )
                        addUnc( c, "SFb",           binname, pName, sfb,     expected.val, signal )
                        addUnc( c, "SFl",           binname, pName, sfl,     expected.val, signal )
                        addUnc( c, "trigger",       binname, pName, trigger, expected.val, signal )
                        addUnc( c, "leptonSF",      binname, pName, lepSF,   expected.val, signal )
                        addUnc( c, "leptonTrackSF", binname, pName, lepTrSF, expected.val, signal )
                        addUnc( c, "photonSF",      binname, pName, phSF,    expected.val, signal )
                        addUnc( c, "eVetoSF",       binname, pName, eVetoSF, expected.val, signal )
                        addUnc( c, "prefireSF",     binname, pName, pfSF,    expected.val, signal )
                        

                        if qcdUnc:
                            addUnc( c, "QCD_norm", binname, pName, qcdUnc, expected.val, signal )

#                        if qcdTF3:
#                            addUnc( c, "QCD_TF", binname, pName, qcdTF3, expected.val, signal )

#                        if qcdhigh:
#                            addUnc( c, "QCD_lowMlg", binname, pName, qcdhigh, expected.val, signal )

                        if not args.inclRegion and with1pCR:
                            for i in range(len(gammaPT_thresholds)-1):
                                if locals()["ttg_bin%i_unc"%i]:
                                    addUnc( c, "TTG_pTBin%i"%i, binname, pName, locals()["ttg_bin%i_unc"%i], expected.val, signal )
                                elif counter == 1 and not setup.signalregion and signal and not newPOI_input:
                                    addUnc( c, "TTG_pTBin%i"%i, binname, pName, 0.01, expected.val, signal )
                        if dyUnc: # and args.addDYSF:
                            addUnc( c, "DY_norm", binname, pName, dyUnc, expected.val, signal )
                        if ttUnc and not args.ttPOI:
                            addUnc( c, "TT_norm", binname, pName, ttUnc, expected.val, signal )
#                        if vgUnc and not args.vgPOI and args.addVGSF:
#                            addUnc( c, "VG_norm", binname, pName, vgUnc, expected.val, signal )
                        if wjetsUnc and not args.wJetsPOI: # and args.addWJetsSF:
                            addUnc( c, "WJets_norm", binname, pName, wjetsUnc, expected.val, signal )
                        if otherUnc:
                            addUnc( c, "Other_norm", binname, pName, otherUnc, expected.val, signal )
                        if zg:
                            addUnc( c, "ZG_norm", binname, pName, zg, expected.val, signal )
#                        if wg:
#                            addUnc( c, "WG_norm", binname, pName, wg, expected.val, signal )
#                        if zg3:
#                            addUnc( c, "ZG_nJet", binname, pName, zg3, expected.val, signal )
#                        if misID4p:
#                            addUnc( c, "misID4p", binname, pName, misID4p, expected.val, signal )

#                        if hadFakesUnc: # and args.addFakeSF:
#                            addUnc( c, "Fakes_norm", binname, pName, hadFakesUnc, expected.val, signal )
                        if any( ["fake" in name for name in args.useRegions] ):
                            if lowSieieUnc:
                                addUnc( c, "fake_lowSieie", binname, pName, lowSieieUnc, expected.val, signal )
                            if highSieieUnc:
                                addUnc( c, "fake_highSieie", binname, pName, highSieieUnc, expected.val, signal )
                            if any(fakeCorrUnc) and addFakeUnc:
                                for i_iso, iso in enumerate(chgIsoRegions):
                                    addUnc( c, "fake_corr_%i"%i_iso, binname, pName, fakeCorrUnc[i_iso], expected.val, signal )                

                        # MC bkg stat (some condition to neglect the smaller ones?)
                        uname = "Stat_%s_%s"%(binname, pName if not (newPOI_input and signal) else "signal")
                        if not (newPOI_input and signal):
                            c.addUncertainty( uname, "lnN" )
                        addUnc( c, uname, binname, pName, (expected.sigma/expected.val) if expected.val > 0 else 0.01, expected.val, signal )

                    if newPOI_input:
                        uname = "Stat_%s_%s"%(binname,"signal")
                        c.addUncertainty( uname, "lnN" )
                        c.specifyExpectation( binname, "signal", sigExp.val )
                        if sigExp.val:
                            for key, val in sigUnc.items():
                                c.specifyUncertainty( key, binname, "signal", 1 + val.sigma/sigExp.val )

                    if args.expected or (args.year in [2017,2018] and not args.unblind and setup.signalregion):
                        c.specifyObservation( binname, int( round( total_exp_bkg, 0 ) ) )
                        logger.info( "Expected observation: %s", int( round( total_exp_bkg, 0 ) ) )
                    else:
                        c.specifyObservation( binname,  int( observation.cachedObservation(r, channel, setup).val ) )
                        logger.info( "Observation: %s", int( observation.cachedObservation(r, channel, setup).val ) )

                    if mute and total_exp_bkg <= 0.01:
                        c.muted[binname] = True

        # Flat luminosity uncertainty
        c.addUncertainty( "Lumi", "lnN" )
        c.specifyFlatUncertainty( "Lumi", 1.026 )

        cardFileNameTxt     = c.writeToFile( cardFileNameTxt )
        cardFileNameShape   = c.writeToShapeFile( cardFileNameShape )
        cardFileName        = cardFileNameTxt if args.useTxt else cardFileNameShape
    else:
        logger.info( "File %s found. Reusing."%cardFileName )
        cardFileNameShape = cardFileNameShape.replace('.root', 'Card.txt')
        cardFileName      = cardFileNameTxt if args.useTxt else cardFileNameShape
    

    sConfig = "_".join(configlist)

    nll          = c.calcNLL( cardFileName )
    nll_prefit   = nll['nll0']
    nll_postfit  = nll['nll_abs']
    NLL = nll['nll']    
    
    if nll_prefit  is None or abs(nll_prefit) > 10000 or abs(nll_prefit) < 1e-5:   nll_prefit  = 999
    if nll_postfit is None or abs(nll_postfit) > 10000 or abs(nll_postfit) < 1e-5: nll_postfit = 999

    nllCache.add( sConfig, NLL, overwrite=True )
    
    print NLL

######################################
# Load the signals and run the code! #
######################################

results = wrapper()


