#!/usr/bin/env python

import os, copy, time, sys
import ROOT
from shutil                              import copyfile
from math                                import sqrt
from helpers                             import uniqueKey

from TTGammaEFT.Analysis.EstimatorList   import EstimatorList
from TTGammaEFT.Analysis.DataObservation import DataObservation
from TTGammaEFT.Analysis.MCBasedEstimate import MCBasedEstimate
from TTGammaEFT.Analysis.Setup           import Setup
from TTGammaEFT.Analysis.regions         import m3PtlooseRegions, regionsTTGlooseFine, regionsTTG, noPhotonRegionTTG, inclRegionsTTG, regionsTTGfake, inclRegionsTTGfake, chgIso_thresh, chgIsoRegions, pTG_thresh, highpTG_thresh, mLgRegions
from TTGammaEFT.Analysis.SetupHelpers    import *

from TTGammaEFT.Tools.user               import combineReleaseLocation, cardfileLocation, cache_directory
from Analysis.Tools.MergingDirDB         import MergingDirDB
from Analysis.Tools.u_float              import u_float
from TTGammaEFT.Tools.cardFileWriter       import cardFileWriter
from Analysis.Tools.cardFileWriter.CombineResults      import CombineResults
from Analysis.Tools.getPostFit           import getPrePostFitFromMLF, getFitResults
from TTGammaEFT.Tools.cutInterpreter     import cutInterpreter

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
argParser.add_argument( "--noFakeStat"  ,       action="store_true",                                                        help="skip the fake stat uncertainty" )
argParser.add_argument( "--addNJetUnc",         action="store_true",                                                        help="add the nJet uncertainties in the 4p channel" )
argParser.add_argument( "--addVGSF",            action="store_true",                                                        help="add default DY scale factor" )
argParser.add_argument( "--addZGSF",            action="store_true",                                                        help="add default DY scale factor" )
argParser.add_argument( "--addWGSF",            action="store_true",                                                        help="add default DY scale factor" )
argParser.add_argument( "--addDYSF",            action="store_true",                                                        help="add default DY scale factor" )
argParser.add_argument( "--addWJetsSF",         action="store_true",                                                        help="add default DY scale factor" )
argParser.add_argument( "--addMisIDSF",         action="store_true",                                                        help="add default misID scale factor" )
argParser.add_argument( "--addSSM",             action="store_true",                                                        help="add default signal strength modifer" )
argParser.add_argument( "--keepCard",           action="store_true",                                                        help="Overwrite existing output files" )
argParser.add_argument( "--expected",           action="store_true",                                                        help="Use sum of backgrounds instead of data." )
argParser.add_argument( "--useTxt",             action="store_true",                                                        help="Use txt based cardFiles instead of root/shape based ones?" )
argParser.add_argument( "--skipFitDiagnostics", action="store_true",                                                        help="Don't do the fitDiagnostics (this is necessary for pre/postfit plots, but not 2D scans)?" )
argParser.add_argument( "--skipTuneUnc",        action="store_true",                                                        help="Skip pdf/ps/scale/tune/color reconnection unc" )
argParser.add_argument( "--year",               action="store",      default="2016",   type=str,                            help="Which year?" )
argParser.add_argument( "--linTest",            action="store",      default=1,   type=float,                               help="linearity test: scale data by factor" )
argParser.add_argument( "--runOnLxPlus",        action="store_true",                                                        help="Change the global redirector of samples")
argParser.add_argument( "--misIDPOI",           action="store_true",                                                        help="Change POI to misID SF")
argParser.add_argument( "--dyPOI",              action="store_true",                                                        help="Change POI to misID SF")
argParser.add_argument( "--wgPOI",              action="store_true",                                                        help="Change POI to WGamma SF")
argParser.add_argument( "--ttPOI",              action="store_true",                                                        help="Change POI to misID SF")
argParser.add_argument( "--wJetsPOI",           action="store_true",                                                        help="Change POI to misID SF")
argParser.add_argument( "--checkOnly",          action="store_true",                                                        help="Check the SF only")
argParser.add_argument( "--bkgOnly",            action="store_true",                                                        help="background only")
argParser.add_argument( "--plot",               action="store_true",                                                        help="run plots?")
argParser.add_argument( "--noMCStat",           action="store_true",                                                        help="create file without MC stat?")
argParser.add_argument('--order',               action='store',      default=2, type=int,                                   help='Polynomial order of weight string (e.g. 2)')
argParser.add_argument('--parameters',          action='store',      default=[],  type=str, nargs='+',                      help = "argument parameters")
argParser.add_argument('--mode',                action='store',      default="all", type=str, choices=["mu", "e", "all"],   help="plot lepton mode" )
argParser.add_argument('--withbkg',             action='store_true',                                                        help="reweight sample and bkg or sample only?")
argParser.add_argument('--withEFTUnc',             action='store_true',                                                        help="add EFT uncertainty?")
argParser.add_argument('--freezeR',             action='store_true',                                                        help="add EFT uncertainty?")
argParser.add_argument('--freezeSigUnc',             action='store_true',                                                        help="add EFT uncertainty?")
argParser.add_argument('--addPtBinnedUnc',             action='store_true',                                                        help="add EFT uncertainty?")
argParser.add_argument('--notNormalized',             action='store_true',                                                        help="not normalized Scale uncertainties?")
args=argParser.parse_args()

if args.year != "RunII": args.year = int(args.year)
# linearity test with expected observation
if args.linTest != 1: args.expected = True

# Logging
import Analysis.Tools.logger as logger
logger = logger.get_logger(       args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

if args.useChannels and "comb" in args.useChannels: args.useChannels += ["mu", "e"]
if args.useChannels and "e"    in args.useChannels: args.useChannels += ["eetight"]
if args.useChannels and "mu"   in args.useChannels: args.useChannels += ["mumutight"]
if args.useChannels and "all"  in args.useChannels: args.useChannels  = None

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
    #default_setup.processes  = default_setup.estimators.constructProcessDict( processDict=default_processes )
    default_setup.processes["Data"] = default_setup.data
    default_setup.addon      = ""
    default_setup.regions    = inclRegionsTTG if args.inclRegion else regionsTTG

    default_photon_setup            = Setup( year=args.year, photonSelection=True, runOnLxPlus=args.runOnLxPlus, checkOnly=True )
    default_photon_setup.estimators = EstimatorList( default_photon_setup )
    default_photon_setup.data       = default_photon_setup.processes["Data"]
    #default_photon_setup.processes  = default_setup.estimators.constructProcessDict( processDict=default_processes )
    default_photon_setup.processes["Data"] = default_photon_setup.data
    default_photon_setup.addon      = ""
    default_photon_setup.regions    = inclRegionsTTG if args.inclRegion else regionsTTG

# Define SR, CR, channels and regions
with0pCR = False
with1pCR = False
setups = []

if args.parameters and args.withbkg:
    splitProcessDict = {}
    splitProcessDict["ST_tch_gen"]    = { "process":["ST_tch_gen"] }
#    splitProcessDict["ST_tch_had"]    = { "process":["ST_tch_had"] }
#    splitProcessDict["ST_tch_misID"]  = { "process":["ST_tch_misID"] }
    splitProcessDict["ST_sch_gen"]    = { "process":["ST_sch_gen"] }
#    splitProcessDict["ST_sch_had"]    = { "process":["ST_sch_had"] }
#    splitProcessDict["ST_sch_misID"]  = { "process":["ST_sch_misID"] }
    splitProcessDict["ST_tW_gen"]     = { "process":["ST_tW_gen"] }
#    splitProcessDict["ST_tW_had"]     = { "process":["ST_tW_had"] }
#    splitProcessDict["ST_tW_misID"]   = { "process":["ST_tW_misID"] }
    splitProcessDict["TT_pow_gen"]    = { "process":["TT_pow_gen"] }
#    splitProcessDict["TT_pow_had"]    = { "process":["TT_pow_had"] }
#    splitProcessDict["TT_pow_misID"]  = { "process":["TT_pow_misID"] }

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
    locals()["setup"+key].bTagged      = locals()["setup"+key].parameters["nBTag"][1] != 0
    locals()["setup"+key].regions      = val["inclRegion" if args.inclRegion else "regions"]

    # change to MC based fake estimation in expected
    if args.expected:
        if "processes" in val.keys() and "fakes" in  val["processes"].keys():
            if val["processes"]["fakes"]["process"][0] == "fakes-DD":
                val["processes"]["fakes"]["process"] = ["fakes-DDMC"]

    locals()["setup"+key].data         = default_setup.data if val["noPhotonCR"] else default_photon_setup.data
    locals()["setup"+key].processes    = estimators.constructProcessDict( processDict=val["processes"] ) if "processes" in val else default_setup.processes if val["noPhotonCR"] else default_photon_setup.processes
    locals()["setup"+key].processes["Data"] = locals()["setup"+key].data
    locals()["setup"+key].addon      = key
    if args.parameters and args.withbkg: locals()["setup"+key].split_processes = estimators.constructProcessDict( splitProcessDict )  

# sort regions accoring to ordering
for reg in limitOrdering:
    if "setup"+reg in locals():
        regionNames.append(reg)
        setups.append(locals()["setup"+reg])

# use the regions as key for caches
regionNames.sort()
if args.addWJetsSF:   regionNames.append("addWJetsSF")
if args.addDYSF:      regionNames.append("addDYSF")
if args.addVGSF:      regionNames.append("addVGSF")
if args.addWGSF:      regionNames.append("addWGSF")
if args.addZGSF:      regionNames.append("addZGSF")
if args.addSSM:       regionNames.append("addSSM")
if args.addMisIDSF:   regionNames.append("addMisIDSF")
if args.inclRegion:   regionNames.append("incl")
if args.misIDPOI:     regionNames.append("misIDPOI")
if args.wgPOI:        regionNames.append("wgPOI")
if args.dyPOI:        regionNames.append("dyPOI")
if args.wJetsPOI:     regionNames.append("wJetsPOI")
if args.ttPOI:        regionNames.append("ttPOI")
if args.useChannels:  regionNames.append("_".join([ch for ch in args.useChannels if not "tight" in ch]))
if args.linTest != 1: regionNames.append(str(args.linTest).replace(".","_"))
if args.noMCStat:     regionNames.append("noMCStat")
if args.noFakeStat:   regionNames.append("noFakeStat")
if args.freezeR:   regionNames.append("freezeR")
if args.freezeSigUnc:   regionNames.append("freezeSigUnc")
if args.addPtBinnedUnc:   regionNames.append("addPtBinnedUnc")
if args.notNormalized:   regionNames.append("notNormalized")

# partly corr btagging unc as suggested from pog contacts
ystring = "2016" if args.year == 2016 else "2017_2018"
heavyFlavor = "heavy_flavor_%s"%ystring
lightFlavor = "light_flavor_%s"%ystring

baseDir       = os.path.join( cache_directory, "analysis",  str(args.year), "limits" )
if args.parameters:
    baseDir   = os.path.join( baseDir, "withbkg" if args.withbkg else "withoutbkg" )
    if args.withEFTUnc: baseDir = os.path.join( baseDir, "withEFTUnc" )
limitDir      = os.path.join( baseDir, "cardFiles", args.label, "expected" if args.expected else "observed" )
if not os.path.exists( limitDir ): os.makedirs( limitDir )

cacheDir        = os.path.join( cache_directory, "modelling",  str(args.year), "inclusive" if args.parameters or args.notNormalized else "normalized" )
cacheFileName   = os.path.join( cacheDir, "Scale" )
scaleUncCache   = MergingDirDB( cacheFileName )
cacheFileName   = os.path.join( cacheDir, "PDF" )
pdfUncCache     = MergingDirDB( cacheFileName )
cacheFileName   = os.path.join( cacheDir, "PS" )
psUncCache      = MergingDirDB( cacheFileName )

if args.parameters:
    # read the EFT parameters
    eft =  "_".join(args.parameters)
    # load the EFT samples
    from TTGammaEFT.Samples.genTuples_TTGamma_EFT_postProcessed  import *

    cacheFileName        = os.path.join( baseDir, "calculatednll" )
    nllCache             = MergingDirDB( cacheFileName )
    print cacheFileName
    cacheFileName        = os.path.join( baseDir, "calculatedLimits" )
    limitCache           = MergingDirDB( cacheFileName )
    cacheFileName        = os.path.join( baseDir, "calculatedSignifs" )
    signifCache          = MergingDirDB( cacheFileName )

    # store all the different samples in different caches (signal=TTG, background=TT, tWG, tW, stg_tch, st_tch, stg_sch, st_sch)
    baseDir              = os.path.join( cache_directory, "analysis", "eft" )
    cacheFileName        = os.path.join( baseDir, 'TTG_2WC_ref' )
    yieldCache_TTG       = MergingDirDB( cacheFileName )
    print yieldCache_TTG
#    cacheFileName        = os.path.join( baseDir, 'TT_2WC_ref' )
#    yieldCache_TT        = MergingDirDB( cacheFileName )
    cacheFileName        = os.path.join( baseDir, 'tWG_2WC_ref' )
    yieldCache_tWG       = MergingDirDB( cacheFileName )
#    cacheFileName        = os.path.join( baseDir, 'tW_2WC_ref' )
#    yieldCache_tW        = MergingDirDB( cacheFileName )
    cacheFileName        = os.path.join( baseDir, 'stg_tch_2WC_ref' )
    yieldCache_stg_tch   = MergingDirDB( cacheFileName )
#    cacheFileName        = os.path.join( baseDir, 'st_tch_2WC_ref' )
#    yieldCache_st_tch    = MergingDirDB( cacheFileName )
    cacheFileName        = os.path.join( baseDir, 'stg_sch_2WC_ref' )
    yieldCache_stg_sch   = MergingDirDB( cacheFileName )
#    cacheFileName        = os.path.join( baseDir, 'st_sch_2WC_ref' )
#    yieldCache_st_sch    = MergingDirDB( cacheFileName )

    configlist = regionNames + args.parameters
    configlist.append("incl" if args.inclRegion else "diff")
    configlist.append("expected" if args.expected else "observed")

    sEFTConfig = "_".join(configlist)
    print(nllCache.get(sEFTConfig))
    print(nllCache.contains(sEFTConfig))
    print(sEFTConfig)
    if not args.overwrite and nllCache.contains( sEFTConfig ) and abs(nllCache.get(sEFTConfig)["nll0"])>0.1: sys.exit(0)

# JEC Tags, (standard is "Total")
jesTags = ['FlavorQCD', 'RelativeBal', 'HF', 'BBEC1', 'EC2', 'Absolute', 'Absolute_%i'%args.year, 'HF_%i'%args.year, 'EC2_%i'%args.year, 'RelativeSample_%i'%args.year, 'BBEC1_%i'%args.year]

def getScaleUnc(name, r, channel, setup):
    key      = uniqueKey( name, r, channel, setup ) + tuple(str(args.year))
    scaleUnc = scaleUncCache.get( key )
#    if scaleUnc > 0.5: scaleUnc = 0.5
    return scaleUnc #max(0.0004, scaleUnc)

def getPDFUnc(name, r, channel, setup):
    key    = uniqueKey( name, r, channel, setup ) + tuple(str(args.year))
    PDFUnc = pdfUncCache.get( key )
#    if PDFUnc > 0.5: PDFUnc = 0.5
    return PDFUnc #max(0.0004, PDFUnc)

def getPSUnc(name, r, channel, setup):
    key   = uniqueKey( name, r, channel, setup ) + tuple(str(args.year))
    PSUnc = psUncCache.get( key )
#    if PSUnc > 0.5: PSUnc = 0.5
    return PSUnc #max(0.0004, PSUnc)

def wrapper():
    c = cardFileWriter.cardFileWriter()
    c.releaseLocation = combineReleaseLocation

    if args.parameters:
        cardFileNameTxt   = os.path.join( limitDir, "_".join( regionNames ), eft + ".txt" )
    else:
        cardFileNameTxt   = os.path.join( limitDir, "_".join( regionNames ) + ".txt" )
    cardFileNameShape = cardFileNameTxt.replace( ".txt", "_shape.root" )
    cardFileName      = cardFileNameTxt
    print cardFileName

    pTG_thresh = [ 20, 35, 50, 65, 80, 100, 120, 140, 160, 200, 280, -999 ]
#[ 20, 35, 50, 65, 80, 120, 160, 200, 260, 320, -999 ]
    eta_thresh = list(np.linspace(start=0, stop=1.35, num=10)) + [1.4442]
    dR_thresh = [ 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, -999 ]
    freezeParams = []
    signalPT_regions = getRegionsFromThresholds( "PhotonNoChgIsoNoSieie0_pt", pTG_thresh )
    if not args.inclRegion and with1pCR and args.addPtBinnedUnc:
        if any( ["AbsEta" in cardRegions for cardRegions in args.useRegions] ):
            sigBin_thresh = eta_thresh
            sigVar = "abs(PhotonNoChgIsoNoSieie0_eta)"
            sigIndex = 1
        elif any( ["dR" in cardRegions for cardRegions in args.useRegions] ):
            sigBin_thresh = dR_thresh
            sigVar = "ltight0GammaNoSieieNoChgIsodR"
            sigIndex = 1
        else:
            sigBin_thresh = pTG_thresh
            sigVar = "PhotonNoChgIsoNoSieie0_pt"
            sigIndex = 0

        for i in range(len(sigBin_thresh)-1):
            freezeParams.append( "Signal_e_3_Bin%i_%s"%(i,str(args.year)) )
            freezeParams.append( "Signal_mu_3_Bin%i_%s"%(i,str(args.year)) )
            if i != sigIndex:
                freezeParams.append( "Signal_e_4p_Bin%i_%s"%(i,str(args.year)) )
                freezeParams.append( "Signal_mu_4p_Bin%i_%s"%(i,str(args.year)) )

    if ( not os.path.exists(cardFileNameTxt) or ( not os.path.exists(cardFileNameShape) and not args.useTxt ) ) or args.overwrite:

        if args.checkOnly:
            print cardFileNameShape
            logger.info("Combine Card not found. Please run without --checkOnly first!")
            return

        counter=0
        c.reset()
        c.setPrecision(3)
        shapeString     = "lnN" if args.useTxt else "shape"


        if args.parameters:
            c.addUncertainty( "EFT_nJet", shapeString)

        # experimental
        c.addUncertainty( "PU",            shapeString) #correlated
        for j in jesTags:
            c.addUncertainty( "JEC_%s"%j,           shapeString) #partly correlated
        c.addUncertainty( "JER_%i"%args.year,           shapeString) #uncorrelated
        c.addUncertainty( "EGammaScale",           shapeString) #correlated
        c.addUncertainty( "EGammaResolution",           shapeString) #correlated
        c.addUncertainty( heavyFlavor,           shapeString) #need to check
        c.addUncertainty( lightFlavor,           shapeString) #need to check
        c.addUncertainty( "Trigger_muons_%i"%args.year,       shapeString) #uncorrelated
        c.addUncertainty( "Trigger_electrons_%i"%args.year,       shapeString) #uncorrelated
        c.addUncertainty( "muon_ID_extrapolation",      shapeString) #correlated in e, split stat/syst in mu
        c.addUncertainty( "muon_ID_syst",      shapeString) #correlated in e, split stat/syst in mu
        c.addUncertainty( "muon_ID_sta_%i"%args.year,      shapeString) #correlated in e, split stat/syst in mu
        c.addUncertainty( "electron_ID",      shapeString) #correlated in e, split stat/syst in mu
        c.addUncertainty( "electron_reco", shapeString) #uncorrelated to e ID (non existing for mu)
        if args.year != 2018:
            c.addUncertainty( "L1_Prefiring",     shapeString) #need to check
        c.addUncertainty( "top_pt_reweighting",  shapeString)
        if with1pCR:
            c.addUncertainty( "photon_ID",      shapeString)
            c.addUncertainty( "pixelSeed_veto_%i"%args.year,       shapeString) #uncorrelated
#            # theory (PDF, scale, ISR)

            c.addUncertainty( "Tune",          shapeString)
            c.addUncertainty( "erdOn",         shapeString)
            c.addUncertainty( "GluonMove",    shapeString)
            c.addUncertainty( "QCDbased",     shapeString)
            c.addUncertainty( "Scale",         shapeString)
            c.addUncertainty( "PDF",           shapeString)
            c.addUncertainty( "Parton_Showering",            shapeString)

##        if args.year == 2016:
##            c.addUncertainty( "photon_ID_AltSig_2016",      shapeString)


        default_Signal_unc = 5.
        pTG_thresh = [ 20, 35, 50, 65, 80, 100, 120, 140, 160, 200, 280, -999 ]
#[ 20, 35, 50, 65, 80, 120, 160, 200, 260, 320, -999 ]
        eta_thresh = list(np.linspace(start=0, stop=1.35, num=10)) + [1.4442]
        dR_thresh = [ 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, -999 ]
        freezeParams = []
        signalPT_regions = getRegionsFromThresholds( "PhotonNoChgIsoNoSieie0_pt", pTG_thresh )
        if not args.inclRegion and with1pCR and args.addPtBinnedUnc:
            if any( ["AbsEta" in cardRegions for cardRegions in args.useRegions] ):
                sigBin_thresh = eta_thresh
                sigVar = "abs(PhotonNoChgIsoNoSieie0_eta)"
                sigIndex = 1
            elif any( ["dR" in cardRegions for cardRegions in args.useRegions] ):
                sigBin_thresh = dR_thresh
                sigVar = "ltight0GammaNoSieieNoChgIsodR"
                sigIndex = 1
            else:
                sigBin_thresh = pTG_thresh
                sigVar = "PhotonNoChgIsoNoSieie0_pt"
                sigIndex = 0

            for i in range(len(sigBin_thresh)-1):
                c.addUncertainty( "Signal_e_3_Bin%i_%s"%(i,str(args.year)), shapeString )
                c.addUncertainty( "Signal_mu_3_Bin%i_%s"%(i,str(args.year)), shapeString )
                if i != sigIndex:
                    c.addUncertainty( "Signal_e_4p_Bin%i_%s"%(i,str(args.year)), shapeString )
                    c.addUncertainty( "Signal_mu_4p_Bin%i_%s"%(i,str(args.year)), shapeString )

                freezeParams.append( "Signal_e_3_Bin%i_%s"%(i,str(args.year)) )
                freezeParams.append( "Signal_mu_3_Bin%i_%s"%(i,str(args.year)) )
                if i != sigIndex:
                    freezeParams.append( "Signal_e_4p_Bin%i_%s"%(i,str(args.year)) )
                    freezeParams.append( "Signal_mu_4p_Bin%i_%s"%(i,str(args.year)) )


        default_misIDpT_unc = 0.40
        misIDPT_thresholds = [ 20, 35, 50, 65, 80, 120, 160, -999 ]
        misIDPT_regions = getRegionsFromThresholds( "PhotonNoChgIsoNoSieie0_pt", misIDPT_thresholds )
        if not args.inclRegion and with1pCR:
            for i in range(1, len(misIDPT_thresholds)-1):
                c.addUncertainty( "misID_pT_Bin%i_%i"%(i,args.year), shapeString )

        default_WGpT_unc = 0.20
        WGPT_thresholds = [ 20, 65, 160, -999 ]
        WGPT_regions = getRegionsFromThresholds( "PhotonNoChgIsoNoSieie0_pt", WGPT_thresholds )
        if not args.inclRegion and with1pCR:
            for i in range(1, len(WGPT_thresholds)-1):
                c.addUncertainty( "WGamma_pT_Bin%i"%(i), shapeString )
                c.addUncertainty( "ZGamma_pT_Bin%i"%(i), shapeString )

        default_QCD1b_unc = 0.
        default_QCD0b_unc = 0.
        default_QCD_unc   = 0.5
        if not args.wgPOI:
            default_QCD1b_unc = 0.5*0.5 #uncorrelated part, 50% correlation between 0b and 1b, generally 50%uncertainty
            default_QCD0b_unc = 0.5*0.5 #uncorrelated part, 50% correlation between 0b and 1b, generally 50%uncertainty
            default_QCD_unc   = 0.5*0.866025 #correlated part, 50% correlation between 0b and 1b, generally 50%uncertainty
            c.addUncertainty( "QCD_1b_normalization", shapeString )
            c.addUncertainty( "QCD_0b_normalization", shapeString )
        c.addUncertainty( "QCD_normalization", shapeString )
#        c.addUncertainty( "QCD_TF", shapeString )

        default_TT_unc = 0.07
        c.addUncertainty( "TT_normalization", shapeString )

        default_HadFakes_MC_unc = 0.05
        default_HadFakes_DD_unc = 0.05
        ddBin = 0
        c.addUncertainty( "fake_photon_DD_normalization",   shapeString )
        c.addUncertainty( "fake_photon_MC_normalization",   shapeString )

        default_HadFakes_2017_unc = 0.20
        if args.year == 2017:
            c.addUncertainty( "fake_photon_model_2017",      shapeString )

        default_WG_unc    = 0.3
        if with1pCR and not args.wgPOI:
#            if args.parameters:
#                c.addUncertainty( "WGamma_normalization",   shapeString )
#            else:
                c.addFreeParameter("WGamma_normalization", '*WG*', 1, '[0.,2.]')

        default_ZG_unc    = 0.3
        c.addUncertainty( "ZGamma_normalization",      shapeString )

        default_ZG_gluon_unc    = 0.12 # only on the fraction of 2 gen b-jets in the SR
        default_WG_gluon_unc    = 0.04 # only on the fraction of 2 gen b-jets in the SR
        c.addUncertainty( "Gluon_splitting",      shapeString )

        default_Other_unc    = 0.30
        c.addUncertainty( "Other_normalization",      shapeString )

        default_misIDext_unc    = 0.1
        c.addUncertainty( "MisID_extrapolation_%i"%args.year,      shapeString )

        default_misID4p_unc    = 0.2
        default_ZG4p_unc    = 0.4
        default_WG4p_unc    = 0.2
        default_QCD0b4p_unc    = 0.2
        default_QCD1b4p_unc    = 0.2
        default_DY4p_unc    = 0.2
        if not (args.wgPOI or args.dyPOI):
            if (any( ["3" in name and not "4pM3" in name for name in args.useRegions] ) and any( ["4p" in name for name in args.useRegions] )) or args.addNJetUnc or any( ["3p" in name for name in args.useRegions] ):
                c.addUncertainty( "MisID_nJet_dependence_%i"%args.year,      shapeString )
                c.addUncertainty( "ZGamma_nJet_dependence",      shapeString )
                c.addUncertainty( "QCD_0b_nJet_dependence",      shapeString )
                c.addUncertainty( "QCD_1b_nJet_dependence",      shapeString )
                c.addUncertainty( "WGamma_nJet_dependence",      shapeString )

        default_DY_unc    = 0.08
        if any( [ name in ["DY2","DY3","DY4","DY4p","DY5"] for name in args.useRegions] ) and not args.dyPOI:
            c.addFreeParameter("DY_normalization", '*DY*', 1, '[0.,2.]')
        elif not args.dyPOI:
            c.addUncertainty( "DY_normalization", shapeString )

        default_MisID_unc    = 0.30

        if not args.addMisIDSF and not args.misIDPOI and with1pCR:
            c.addFreeParameter("MisID_normalization_%i"%args.year, '*misID*', 1, '[0.,5.]')
            #c.addFreeParameter("misID_%i"%args.year, 'misID', 1, '[0,5]')
        elif not args.misIDPOI and with1pCR:
#            if args.parameters:
#                c.addUncertainty( "MisID_normalization_%i"%args.year, shapeString )
#            else:
                c.addFreeParameter("MisID_normalization_%i"%args.year, '*misID*', 1, '[0.,2.]')
           #c.addFreeParameter("misID_%i"%args.year, 'misID', 1, '[0,2]')

        for setup in setups:
            observation = DataObservation( name="Data", process=setup.data, cacheDir=setup.defaultCacheDir() )

            if "3p" in setup.name:
                setup4p = setup.sysClone( parameters={"nJet":(4,-1)} )
                setup3 = setup.sysClone( parameters={"nJet":(3,3)} )

            for pName, pList in setup.processes.items():
                if pName == "Data": continue
                for e in pList:
                    e.initCache( setup.defaultCacheDir() )
                    if args.parameters and args.withbkg:
                        setup.split_processes['ST_tch_gen'][0].initCache( setup.defaultCacheDir() )
#                        setup.split_processes['ST_tch_had'][0].initCache( setup.defaultCacheDir() )
#                        setup.split_processes['ST_tch_misID'][0].initCache( setup.defaultCacheDir() )
                        setup.split_processes['ST_sch_gen'][0].initCache( setup.defaultCacheDir() )
#                        setup.split_processes['ST_sch_had'][0].initCache( setup.defaultCacheDir() )
#                        setup.split_processes['ST_sch_misID'][0].initCache( setup.defaultCacheDir() )
                        setup.split_processes['ST_tW_gen'][0].initCache( setup.defaultCacheDir() )
#                        setup.split_processes['ST_tW_had'][0].initCache( setup.defaultCacheDir() )
#                        setup.split_processes['ST_tW_misID'][0].initCache( setup.defaultCacheDir() )
                        setup.split_processes['TT_pow_gen'][0].initCache( setup.defaultCacheDir() )
#                        setup.split_processes['TT_pow_had'][0].initCache( setup.defaultCacheDir() )
#                        setup.split_processes['TT_pow_misID'][0].initCache( setup.defaultCacheDir() )
            for r in setup.regions:
                for i_ch, channel in enumerate(setup.channels):
                    if (args.useChannels and channel not in args.useChannels and not args.parameters) or (args.useChannels and channel not in args.useChannels and args.parameters and setup.signalregion): continue
                    if args.parameters:
                        # calc the ratios for the different samples (signal and background)
                        eftyield = 0
                        smyield = 0
                        eftyieldsch = 0
                        smyieldsch = 0
                        eftyieldtch = 0
                        smyieldtch = 0
                        eftyieldtW = 0
                        smyieldtW = 0
                        yield_st_tch_gen     = 0
                        yield_st_sch_gen     = 0
                        yield_tW_gen         = 0
                        yield_TT_gen         = 0
                        if "3p" in setup.name:
                            spR = [setup.name.replace("3p","3"),setup.name.replace("3p","4p")]
                        else:
                            spR = [setup.name]
                        if channel == "all":
                            schR = ["e","mu"]
                        else:
                            schR = [channel]
                        for sp in spR:
                            for sch in schR:
                                smyieldkey  =  (sp, str(r),sch, "ctZ_0_ctZI_0")
                                yieldkey    =  (sp, str(r),sch, str(eft))
                                # signal 
                                smyield     +=  yieldCache_TTG.get(smyieldkey)["val"]
                                eftyield    +=  yieldCache_TTG.get(yieldkey)["val"]

                                # background
                                if args.withbkg: 
                                    smyieldtW     +=  yieldCache_tWG.get(smyieldkey)["val"]
                                    eftyieldtW    +=  yieldCache_tWG.get(yieldkey)["val"]
                                    smyieldtch    +=  yieldCache_stg_tch.get(smyieldkey)["val"]
                                    eftyieldtch   +=  yieldCache_stg_tch.get(yieldkey)["val"]
                                    smyieldsch    +=  yieldCache_stg_sch.get(smyieldkey)["val"]
                                    eftyieldsch   +=  yieldCache_stg_sch.get(yieldkey)["val"]

                                    # calc the amount of each sample in the components defined in SetupHelpers
                                    yield_st_tch_gen     += setup.split_processes['ST_tch_gen'][0].cachedEstimate(r,channel,setup)
                                    yield_st_sch_gen     += setup.split_processes['ST_sch_gen'][0].cachedEstimate(r,channel,setup)
                                    yield_tW_gen         += setup.split_processes['ST_tW_gen'][0].cachedEstimate(r,channel,setup)
                                    yield_TT_gen         += setup.split_processes['TT_pow_gen'][0].cachedEstimate(r,channel,setup)

                        ratio_TTG   =  eftyield / smyield if smyield > 0 else 1
                        ratio_tWG       =  eftyieldtW / smyieldtW if smyieldtW > 0 else 1
                        ratio_stg_tch   =  eftyieldtch / smyieldtch if smyieldtch > 0 else 1
                        ratio_stg_sch   =  eftyieldsch / smyieldsch if smyieldsch > 0 else 1

                    niceName      = " ".join( [ channel, str(r), setup.addon ] )
                    binname       = "Bin%i"%counter
                    total_exp_bkg = 0

                    if args.misIDPOI:
                        c.addBin( binname, [ pName.replace("signal","TTG") for pName in setup.processes.keys() if not "misID" in pName and pName != "Data" ], niceName)
                    elif args.wgPOI:
                        c.addBin( binname, [ pName.replace("signal","TTG") for pName in setup.processes.keys() if not "WG" in pName and pName != "Data" ], niceName)
                    elif args.dyPOI:
                        c.addBin( binname, [ pName.replace("signal","TTG") for pName in setup.processes.keys() if not "DY" in pName and pName != "Data" ], niceName)
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

                        if pName == "Data": continue
                        misIDPOI = "misID" in pName and args.misIDPOI
                        dyPOI    = "DY" in pName and args.dyPOI
                        wgPOI    = "WG" in pName and args.wgPOI
                        wJetsPOI = "WJets" in pName and args.wJetsPOI
                        ttPOI    = "TT"    in pName and not "TTG" in pName and args.ttPOI

                        newPOI_input = any( [args.misIDPOI, args.dyPOI, args.wJetsPOI, args.ttPOI, args.wgPOI] )
                        newPOI       = any( [misIDPOI, dyPOI, wJetsPOI, ttPOI, wgPOI] )
                        
                        if newPOI_input and pName == "signal":
                            pName = "TTG"

                        signal   = True if newPOI else pName == "signal"
                        expected = u_float(0.,0.)

                        for e in pList:
                            exp_yield = e.cachedEstimate( r, channel, setup )

                            # no MC stat uncertainty for data-driven methods
                            if e.name.count( "QCD" ):
                                exp_yield.sigma = 0

#                            if args.noFakeStat and ("WG" in pName or "DY" in pName): #pName == "fakes" and setup.signalregion:
                            if args.noFakeStat and pName == "fakes" and setup.signalregion:
                                exp_yield.sigma = 0

                            if signal and args.linTest != 1:# and setup.signalregion:
                                exp_yield /= args.linTest
                            if signal and args.addSSM:
                                exp_yield *= SSMSF_val[args.year].val
                                logger.info( "Scaling signal by %f"%(SSMSF_val[args.year].val) )
                            if e.name.count( "WJets" ) and args.addWJetsSF:
                                exp_yield *= WJetsSF_val[args.year].val
                                logger.info( "Scaling WJets background %s by %f"%(e.name,WJetsSF_val[args.year].val) )
                            if e.name.count( "DY" ) and args.addDYSF:
#                                exp_yield *= DYSF_val[args.year].val
#                                logger.info( "Scaling DY background %s by %f"%(e.name,DYSF_val[args.year].val) )

                                if "2" in setup.name and not "2p" in setup.name:
                                    exp_yield *= DY2SF_val["RunII"].val
                                    logger.info( "Scaling DY background %s by %f"%(e.name,DY2SF_val["RunII"].val) )
                                elif "3" in setup.name and not "3p" in setup.name:
                                    exp_yield *= DY3SF_val["RunII"].val
                                    logger.info( "Scaling DY background %s by %f"%(e.name,DY3SF_val["RunII"].val) )
                                elif "4" in setup.name and not "4p" in setup.name:
                                    exp_yield *= DY4SF_val["RunII"].val
                                    logger.info( "Scaling DY background %s by %f"%(e.name,DY4SF_val["RunII"].val) )
                                elif "5" in setup.name:
                                    exp_yield *= DY5SF_val["RunII"].val
                                    logger.info( "Scaling DY background %s by %f"%(e.name,DY5SF_val["RunII"].val) )
                                elif "2p" in setup.name:
                                    exp_yield *= DY2pSF_val["RunII"].val
                                    logger.info( "Scaling DY background %s by %f"%(e.name,DY2pSF_val["RunII"].val) )
                                elif "3p" in setup.name:
                                    exp_yield *= DY3pSF_val["RunII"].val
                                    logger.info( "Scaling DY background %s by %f"%(e.name,DY3pSF_val["RunII"].val) )
                                elif "4p" in setup.name:
                                    exp_yield *= DY4pSF_val["RunII"].val
                                    logger.info( "Scaling DY background %s by %f"%(e.name,DY4pSF_val["RunII"].val) )
                                else:
                                    exp_yield *= DYSF_val["RunII"].val
                                    logger.info( "Scaling DY background %s by %f"%(e.name,DYSF_val["RunII"].val) )

                            if e.name.count( "WG" ) and args.addWGSF:
                                exp_yield *= WGSF_val[args.year].val
                                logger.info( "Scaling WG background %s by %f"%(e.name,WGSF_val[args.year].val) )
                            if e.name.count( "ZG" ) and args.addZGSF:
                                exp_yield *= ZGSF_val[args.year].val
                                logger.info( "Scaling ZG background %s by %f"%(e.name,ZGSF_val[args.year].val) )
                            if e.name.count( "misID" ) and args.addMisIDSF:
                                exp_yield *= misIDSF_val[args.year].val
                                logger.info( "Scaling misID background %s by %f"%(e.name,misIDSF_val[args.year].val) )
                            
                            total_exp_bkg += exp_yield.val
                            
                            if args.parameters:
                                # reweight the signal(TTGamma) with the calculated ratio
                                if e.name== 'TTG_gen': exp_yield *= ratio_TTG
                                # reweight also the background with the calculated ratio
                                if args.withbkg:
                                    if e.name== 'Top_gen':
                                        print('Top_gen:', exp_yield)
                                        print('sum of all Top_gen-samples:', yield_st_tch_gen + yield_st_sch_gen +yield_tW_gen + yield_TT_gen)
                                        exp_yield = ((yield_st_tch_gen)*ratio_stg_tch + (yield_st_sch_gen)*ratio_stg_sch + (yield_tW_gen)*ratio_tWG + (yield_TT_gen)*ratio_TTG)

                            e.expYield = exp_yield
                            expected  += exp_yield

                        logger.info( "Expectation for process %s: %s", pName, expected.val )

                        if newPOI_input and signal:
                            sigExp += expected
                            logger.info( "Adding expectation for process %s to signal. Total signal now: %s", pName, sigExp )
                        else:
                            c.specifyExpectation( binname, pName, expected.val ) #if expected.val > 0 else 0.01 )

                        # correct observation for eft
                        #if signal and args.linTest != 1:# and setup.signalregion:
                            #total_exp_bkg += expected.val*args.linTest
                        #else:
                            #total_exp_bkg += expected.val

                        if signal and expected.val <= 0.01: mute = True

                        for j in jesTags:
                            locals()["jec_%s"%j] = 0

                        fakestat, topPt, tune, erdOn, gluonMove, qcdBased, pu, mer, eer, ees, jer, sfb, sfl, trigger_e, trigger_mu, lepSF_e, lepSF_muExt, lepSF_muStat, lepSF_muSyst, lepTrSF, phFakeSF, phMisSF, phSF, phSFAltSig, eVetoSF, pfSF = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                        ps, scale, pdf, isr = 0, 0, 0, 0
                        wjets4p, wg4p, qcd0b4p, qcd1b4p= 0, 0, 0, 0
                        dyGenUnc, ttGenUnc, vgGenUnc, wjetsGenUnc, otherGenUnc, lowSieieUnc, highSieieUnc, misIDPtUnc = 0, 0, 0, 0, 0, 0, 0, 0
                        gluon, hadFakes17Unc, hadFakesUnc, wg, zg, misID4p, dy4p, zg4p, misIDUnc, qcdUnc, qcd0bUnc, qcd1bUnc, vgUnc, wgUnc, zgUnc, dyUnc, misExUnc, ttUnc, wjetsUnc, other0pUnc, otherUnc = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                        if not args.inclRegion and with1pCR and args.addPtBinnedUnc:
                            for i in range(len(sigBin_thresh)-1):
                                locals()["Signal_e_3_bin%i_unc"%i] = 0
                                locals()["Signal_e_4p_bin%i_unc"%i] = 0
                                locals()["Signal_mu_3_bin%i_unc"%i] = 0
                                locals()["Signal_mu_4p_bin%i_unc"%i] = 0

                        for i in range(1,len(misIDPT_thresholds)-1):
                            locals()["misID_bin%i_unc"%i] = 0

                        for i in range(1,len(WGPT_thresholds)-1):
                            locals()["WGamma_bin%i_unc"%i] = 0
                            locals()["ZGamma_bin%i_unc"%i] = 0

                        if expected.val:

#                            if args.noFakeStat and pName == "fakes" and setup.signalregion:
#                                expected.sigma = 0

                            for e in pList:
                                y_scale   = e.expYield.val / expected.val

                                r_noM3 = r
                                if "m3" in str(r).lower() and not args.inclRegion:
                                    # evaluate up/down variation systematics inclusive in M3 to avoid problems with the unfolding distribution (which is inclusive in m3)
                                    r_noM3 = getRegionsFromThresholds( "PhotonNoChgIsoNoSieie0_pt", list(r.vals["PhotonNoChgIsoNoSieie0_pt"]) if "PhotonNoChgIsoNoSieie0_pt" in r.vals.keys() else (20,-999) )[0]
                                y_noM3 = e.cachedEstimate( r_noM3, channel, setup ).val

                                ratio = {}
                                ratio["e"] = e.cachedEstimate( r_noM3, "e",   setup ).val / y_noM3 if channel == "all" and y_noM3 else 1.
                                ratio["mu"] = e.cachedEstimate( r_noM3, "mu",   setup ).val / y_noM3 if channel == "all" and y_noM3 else 1.
                                ratio["3"] = 1
                                ratio["3e"] = 1
                                ratio["3mu"] = 1
                                ratio["4p"] = 1
                                ratio["4pe"] = 1
                                ratio["4pmu"] = 1
                                if "3p" in setup.name:
                                    ratio["3"] = e.cachedEstimate( r_noM3, channel,   setup3 ).val / y_noM3 if y_noM3 else 1.
                                    ratio["3e"] = e.cachedEstimate( r_noM3, "e",   setup3 ).val / y_noM3 if channel == "all" and y_noM3 else 1.
                                    ratio["3mu"] = e.cachedEstimate( r_noM3, "mu",   setup3 ).val / y_noM3 if channel == "all" and y_noM3 else 1.
                                    ratio["4p"] = e.cachedEstimate( r_noM3, channel,   setup4p ).val / y_noM3 if y_noM3 else 1.
                                    ratio["4pe"] = e.cachedEstimate( r_noM3, "e",   setup4p ).val / y_noM3 if channel == "all" and y_noM3 else 1.
                                    ratio["4pmu"] = e.cachedEstimate( r_noM3, "mu",   setup4p ).val / y_noM3 if channel == "all" and y_noM3 else 1.
                                allCh = [channel] if channel != "all" else ["e","mu"]
                                allSetups = {setup.nJet:setup} if not "3p" in setup.name else {"3":setup3, "4p":setup4p}
                                for ch in allCh:
                                  for setupKey, stp in allSetups.iteritems():
                                    if setupKey+ch not in ratio.keys(): ratio[setupKey+ch] = 1

                                if e.name.count( "QCD" ):
                                    qcdUnc     += y_scale * default_QCD_unc
                                    qcd0bUnc   += y_scale * default_QCD0b_unc
                                    qcd1bUnc   += y_scale * default_QCD1b_unc
                                    if ("4" in setup.name or "3p" in setup.name):
                                        qcd0b4p += y_scale * default_QCD0b4p_unc * ratio["4p"]
                                        qcd1b4p += y_scale * default_QCD1b4p_unc * ratio["4p"]
                                    continue # no systematics for data-driven QCD

                                if e.name.count( "_had" ) or e.name.count( "fakes-DD" ):
                                    if e.name.count( "_had" ):
                                        hadFakesUnc += y_scale * default_HadFakes_MC_unc
                                    elif e.name.count( "fakes-DD" ):
                                        hadFakesUnc += y_scale * default_HadFakes_DD_unc
                                    if args.year == 2017 and setup.signalregion:
                                        downscaling = 1.
                                        if channel == "mu" or not ("4" in setup.name or "3p" in setup.name):
                                            downscaling = 0.
                                        if channel == "all":
                                            downscaling *= ratio["e"] if e.expYield.val else 0.
                                        downscaling *= ratio["4p"]
                                        hadFakes17Unc += y_scale * default_HadFakes_2017_unc * downscaling

                                if e.name.count( "DY" ):
                                    dyUnc    += y_scale * default_DY_unc

                                if e.name.count( "Top" ):
                                    ttUnc    += y_scale * default_TT_unc

                                if not args.inclRegion and signal and setup.signalregion:

                                    if args.addPtBinnedUnc:
                                      if ("PhotonGood0_pt" in r.vals.keys() or sigVar in r.vals.keys()):
                                        low, high = r.vals["PhotonGood0_pt" if "PhotonGood0_pt" in r.vals.keys() else sigVar]
                                        pT_indices = []
                                        for i_pt, thresh in enumerate(sigBin_thresh[:-1]):
                                            if (thresh >= low and thresh < high) or (sigBin_thresh[i_pt+1] > low and sigBin_thresh[i_pt+1] <= high) or (sigBin_thresh[i_pt+1] == -999 and (high == -999 or high > thresh)): pT_indices.append(i_pt)
                                      else:
                                        pT_indices = []

                                      if pT_indices:
                                        for pT_index in pT_indices:
                                            if channel == "e":
                                                if "4p" in setup.name:
                                                    locals()["Signal_e_4p_bin%i_unc"%pT_index] += y_scale * default_Signal_unc
                                                elif "3p" in setup.name:
                                                    locals()["Signal_e_3_bin%i_unc"%pT_index] += y_scale * default_Signal_unc * ratio["3"]
                                                    locals()["Signal_e_4p_bin%i_unc"%pT_index] += y_scale * default_Signal_unc * ratio["4p"]
                                                elif "3" in setup.name:
                                                    locals()["Signal_e_3_bin%i_unc"%pT_index] += y_scale * default_Signal_unc
                                            elif channel == "mu":
                                                if "4p" in setup.name:
                                                    locals()["Signal_mu_4p_bin%i_unc"%pT_index] += y_scale * default_Signal_unc
                                                elif "3p" in setup.name:
                                                    locals()["Signal_mu_3_bin%i_unc"%pT_index] += y_scale * default_Signal_unc * ratio["3"]
                                                    locals()["Signal_mu_4p_bin%i_unc"%pT_index] += y_scale * default_Signal_unc * ratio["4p"]
                                                elif "3" in setup.name:
                                                    locals()["Signal_mu_3_bin%i_unc"%pT_index] += y_scale * default_Signal_unc
                                            elif channel == "all":
                                                if "4p" in setup.name:
                                                    locals()["Signal_e_4p_bin%i_unc"%pT_index] += y_scale * ratio["e"] * default_Signal_unc
                                                    locals()["Signal_mu_4p_bin%i_unc"%pT_index] += y_scale * ratio["mu"] * default_Signal_unc
                                                elif "3p" in setup.name:
                                                    locals()["Signal_e_3_bin%i_unc"%pT_index] += y_scale * default_Signal_unc * ratio["3e"]
                                                    locals()["Signal_mu_3_bin%i_unc"%pT_index] += y_scale * default_Signal_unc * ratio["3mu"]
                                                    locals()["Signal_e_4p_bin%i_unc"%pT_index] += y_scale * default_Signal_unc * ratio["4pe"]
                                                    locals()["Signal_mu_4p_bin%i_unc"%pT_index] += y_scale *  default_Signal_unc * ratio["4pmu"]
                                                elif "3" in setup.name:
                                                    locals()["Signal_e_3_bin%i_unc"%pT_index] += y_scale * ratio["e"] * default_Signal_unc
                                                    locals()["Signal_mu_3_bin%i_unc"%pT_index] += y_scale * ratio["mu"] * default_Signal_unc

                                if not args.inclRegion and e.name.count( "misID" ):
                                    if ("PhotonGood0_pt" in r.vals.keys() or "PhotonNoChgIsoNoSieie0_pt" in r.vals.keys()):
                                        low, high = r.vals["PhotonGood0_pt" if "PhotonGood0_pt" in r.vals.keys() else "PhotonNoChgIsoNoSieie0_pt"]
                                        pT_indices = []
                                        for i_pt, thresh in enumerate(misIDPT_thresholds[:-1]):
                                            if (thresh >= low and thresh < high) or (misIDPT_thresholds[i_pt+1] > low and misIDPT_thresholds[i_pt+1] <= high) or (misIDPT_thresholds[i_pt+1] == -999 and (high == -999 or high > thresh)): pT_indices.append(i_pt)
                                    else:
                                        pT_indices = []

                                    if pT_indices:
                                        for pT_index in pT_indices:
                                            if pT_index == 0: continue
                                            locals()["misID_bin%i_unc"%pT_index] += y_scale * default_misIDpT_unc

                                if not args.inclRegion and (e.name.count( "WG" ) or e.name.count( "ZG" )):
                                    if ("PhotonGood0_pt" in r.vals.keys() or "PhotonNoChgIsoNoSieie0_pt" in r.vals.keys()):
                                        low, high = r.vals["PhotonGood0_pt" if "PhotonGood0_pt" in r.vals.keys() else "PhotonNoChgIsoNoSieie0_pt"]
                                        pT_indices = []
                                        for i_pt, thresh in enumerate(WGPT_thresholds[:-1]):
                                            if (thresh >= low and thresh < high) or (thresh <= low and thresh <= high and WGPT_thresholds[i_pt+1] >= low and WGPT_thresholds[i_pt+1] >= high) or (WGPT_thresholds[i_pt+1] > low and WGPT_thresholds[i_pt+1] <= high) or (WGPT_thresholds[i_pt+1] == -999 and (high == -999 or high > thresh)): pT_indices.append(i_pt)
                                    else:
                                        pT_indices = []

                                    if pT_indices:
                                        for pT_index in pT_indices:
                                            if pT_index == 0: continue
                                            if e.name.count( "WG" ):
                                                locals()["WGamma_bin%i_unc"%pT_index] += y_scale * default_WGpT_unc
                                            if e.name.count( "ZG" ):
                                                locals()["ZGamma_bin%i_unc"%pT_index] += y_scale * default_WGpT_unc

                                if e.expYield.val and "Unfold" in setup.name and not "Pt" in setup.name:
#any( ["Unfold" in cardRegions and not "Pt" in cardRegions for cardRegions in args.useRegions] ):
                                    # add fractional pt dependent uncertainties to eta/dR unfolding distributions
                                    # misIDPT_thresholds = [ 20, 35, 50, 65, 80, 120, 160, -999 ]
                                    # exp_yield = e.cachedEstimate( r, channel, setup )
                                    if not args.inclRegion and signal and setup.signalregion and False:
                                        # Skip that
                                        for i_pt, thresh in enumerate(pTG_thresh[:-1]):
                                            eSig = e.cachedEstimate( r+signalPT_regions[i_pt], channel, setup )
                                            sigFraction = eSig.val / e.expYield.val

                                            if channel == "e":
                                                if "4p" in setup.name:
                                                    locals()["Signal_e_4p_bin%i_unc"%i_pt] += y_scale * sigFraction * default_Signal_unc
                                                elif "3p" in setup.name:
                                                    locals()["Signal_e_3_bin%i_unc"%i_pt] += y_scale * sigFraction * default_Signal_unc * ratio["3"]
                                                    locals()["Signal_e_4p_bin%i_unc"%i_pt] += y_scale * sigFraction * default_Signal_unc * ratio["4p"]
                                                elif "3" in setup.name:
                                                    locals()["Signal_e_3_bin%i_unc"%i_pt] += y_scale * sigFraction * default_Signal_unc
                                            elif channel == "mu":
                                                if "4p" in setup.name:
                                                    locals()["Signal_mu_4p_bin%i_unc"%i_pt] += y_scale * sigFraction * default_Signal_unc
                                                elif "3p" in setup.name:
                                                    locals()["Signal_mu_3_bin%i_unc"%i_pt] += y_scale * sigFraction * default_Signal_unc * ratio["3"]
                                                    locals()["Signal_mu_4p_bin%i_unc"%i_pt] += y_scale * sigFraction * default_Signal_unc * ratio["4p"]
                                                elif "3" in setup.name:
                                                    locals()["Signal_mu_3_bin%i_unc"%i_pt] += y_scale * sigFraction * default_Signal_unc
                                            elif channel == "all":
                                                if "4p" in setup.name:
                                                    locals()["Signal_e_4p_bin%i_unc"%i_pt] += y_scale * sigFraction * ratio["e"] * default_Signal_unc
                                                    locals()["Signal_mu_4p_bin%i_unc"%i_pt] += y_scale * sigFraction * ratio["mu"] * default_Signal_unc
                                                elif "3p" in setup.name:
                                                    locals()["Signal_e_3_bin%i_unc"%i_pt] += y_scale * sigFraction * default_Signal_unc * ratio["3e"]
                                                    locals()["Signal_mu_3_bin%i_unc"%i_pt] += y_scale * sigFraction * default_Signal_unc * ratio["3mu"]
                                                    locals()["Signal_e_4p_bin%i_unc"%i_pt] += y_scale * sigFraction * default_Signal_unc * ratio["4pe"]
                                                    locals()["Signal_mu_4p_bin%i_unc"%i_pt] += y_scale * sigFraction *  default_Signal_unc * ratio["4pmu"]
                                                elif "3" in setup.name:
                                                    locals()["Signal_e_3_bin%i_unc"%i_pt] += y_scale * sigFraction * ratio["e"] * default_Signal_unc
                                                    locals()["Signal_mu_3_bin%i_unc"%i_pt] += y_scale * sigFraction * ratio["mu"] * default_Signal_unc

                                    if not args.inclRegion and e.name.count( "misID" ):
                                        for i_pt, thresh in enumerate(misIDPT_thresholds[:-1]):
                                            if i_pt == 0: continue
                                            eMisID = e.cachedEstimate( r+misIDPT_regions[i_pt], channel, setup )
                                            misIDFraction = eMisID.val / e.expYield.val
                                            locals()["misID_bin%i_unc"%i_pt] += y_scale * misIDFraction * default_misIDpT_unc

                                    if not args.inclRegion and (e.name.count( "WG" ) or e.name.count( "ZG" )):
                                        for i_pt, thresh in enumerate(WGPT_thresholds[:-1]):
                                            if i_pt == 0: continue
                                            eWG = e.cachedEstimate( r+WGPT_regions[i_pt], channel, setup )
                                            wgFraction = eWG.val / e.expYield.val
                                            if e.name.count( "WG" ):
                                                locals()["WGamma_bin%i_unc"%i_pt] += y_scale * wgFraction * default_WGpT_unc
                                            if e.name.count( "ZG" ):
                                                locals()["ZGamma_bin%i_unc"%i_pt] += y_scale * wgFraction * default_WGpT_unc



                                if e.name.count( "other" ):
                                    otherUnc += y_scale * default_Other_unc


                                if e.name.count( "WG" ):
                                    wg += y_scale * default_WG_unc
                                if e.name.count( "ZG" ):
                                    zg += y_scale * default_ZG_unc
                                    if setup.signalregion:
                                        gluon += y_scale * default_ZG_gluon_unc

                                if e.name.count( "WG" ) and setup.signalregion:
                                    gluon += y_scale * default_WG_gluon_unc

                                if e.name.count( "ZG" ) and ("4" in setup.name or "3p" in setup.name):
                                    zg4p += y_scale * default_ZG4p_unc * ratio["4p"]

                                if e.name.count( "DY" ) and ("4" in setup.name or "3p" in setup.name):
                                    dy4p += y_scale * default_DY4p_unc * ratio["4p"]

                                if e.name.count( "WG" ) and ("4" in setup.name or "3p" in setup.name):
                                    wg4p += y_scale * default_WG4p_unc * ratio["4p"]

                                if e.name.count( "misID" ):
                                    misIDUnc += y_scale * default_MisID_unc

                                if e.name.count( "misID" ) and ("4" in setup.name or "3p" in setup.name):
                                    misID4p += y_scale * default_misID4p_unc * ratio["4p"]

                                if e.name.count( "misID" ) and setup.signalregion:
                                    misExUnc += y_scale * default_misIDext_unc

                                for ch in allCh:
                                  for setupKey, stp in allSetups.iteritems():
                                    if signal and not "had" in e.name and not newPOI_input and not args.skipTuneUnc:
                                        tune      += y_scale * e.TuneSystematic(    r_noM3, ch, stp ).val * ratio[setupKey+ch]
                                        erdOn     += y_scale * e.ErdOnSystematic(   r_noM3, ch, stp ).val * ratio[setupKey+ch]
                                        qcdBased  += y_scale * e.QCDbasedSystematic(   r_noM3, ch, stp ).val * ratio[setupKey+ch]
                                        gluonMove += y_scale * e.GluonMoveSystematic(   r_noM3, ch, stp ).val * ratio[setupKey+ch]

                                        uncName = e.name if not args.parameters and not args.notNormalized else e.name.replace("TTG","TTG_NLO")
                                        scale   += y_scale * getScaleUnc( uncName, r_noM3, ch, stp ) * ratio[setupKey+ch]
                                        pdf     += y_scale * getPDFUnc(   uncName, r_noM3, ch, stp ) * ratio[setupKey+ch]
                                        uncName = e.name #PS weights not available in 2016 NLO sample
                                        ps      += y_scale * getPSUnc(    uncName, r_noM3, ch, stp ) * ratio[setupKey+ch]


                                    elif "Top" in e.name and not "had" in e.name and not args.skipTuneUnc:
                                        uncName = e.name.replace("Top","TT_pow")
                                        scale   += y_scale * getScaleUnc( uncName, r_noM3, ch, stp ) * ratio[setupKey+ch]
                                        pdf     += y_scale * getPDFUnc(   uncName, r_noM3, ch, stp ) * ratio[setupKey+ch]
#                                        ps      += y_scale * getPSUnc(    uncName, r_noM3, ch, stp ) * ratio[setupKey+ch]

                                    topPt  += y_scale * e.topPtSystematic( r_noM3, ch, stp ).val * ratio[setupKey+ch]

                                if channel == "e":
                                    trigger_e += y_scale * e.triggerSystematic(              r_noM3, channel, setup ).val
                                    lepSF_e   += y_scale * e.leptonSFSystematic(             r_noM3, channel, setup ).val
                                    lepTrSF += y_scale * e.leptonTrackingSFSystematic(     r_noM3, channel, setup ).val
                                elif channel == "mu":
                                    trigger_mu += y_scale * e.triggerSystematic(              r_noM3, channel, setup ).val
                                    lepSF_muExt    += y_scale * 0.005
                                    lepSF_muSyst   += y_scale * e.leptonSFSystSystematic(         r_noM3, channel, setup ).val
                                    lepSF_muStat   += y_scale * e.leptonSFStatSystematic(         r_noM3, channel, setup ).val
                                elif channel == "all":
                                    lepTrSF    += ratio["e"]  * y_scale * e.leptonTrackingSFSystematic(     r_noM3, "e", setup ).val

                                    lepSF_e    += ratio["e"]  * y_scale * e.leptonSFSystematic(             r_noM3, "e", setup ).val
                                    trigger_e  += ratio["e"]  * y_scale * e.triggerSystematic(              r_noM3, "e", setup ).val
                                    lepSF_muExt    += ratio["mu"] * y_scale * 0.005
                                    lepSF_muSyst   += ratio["mu"] * y_scale * e.leptonSFSystSystematic(             r_noM3, "mu", setup ).val
                                    lepSF_muStat   += ratio["mu"] * y_scale * e.leptonSFStatSystematic(             r_noM3, "mu", setup ).val
                                    trigger_mu += ratio["mu"] * y_scale * e.triggerSystematic(              r_noM3, "mu", setup ).val

                                for ch in allCh:
                                  for setupKey, stp in allSetups.iteritems():
                                    pu      += y_scale * e.PUSystematic(                   r_noM3, ch, stp ).val * ratio[setupKey+ch]

                                    for j in jesTags:
                                        locals()["jec_%s"%j] += y_scale * e.JECSystematic( r_noM3, ch, stp, jes=j ).val * ratio[setupKey+ch]
                                    jer     += y_scale * e.JERSystematic(                  r_noM3, ch, stp ).val * ratio[setupKey+ch]
                                    ees     += y_scale * e.EESSystematic(                  r_noM3, ch, stp ).val * ratio[setupKey+ch]
                                    eer     += y_scale * e.EERSystematic(                  r_noM3, ch, stp ).val * ratio[setupKey+ch]
                                    sfb     += y_scale * e.btaggingSFbSystematic(          r_noM3, ch, stp ).val * ratio[setupKey+ch]
                                    sfl     += y_scale * e.btaggingSFlSystematic(          r_noM3, ch, stp ).val * ratio[setupKey+ch]

                                    phSF    += y_scale * e.photonSFSystematic(             r_noM3, ch, stp ).val * ratio[setupKey+ch]
#                                    if args.year == 2016:
#                                        phSFAltSig    += y_scale * e.photonSFAltSigSystematic(             r_noM3, ch, stp ).val * ratio[setupKey+ch]
                                    eVetoSF += y_scale * e.photonElectronVetoSFSystematic( r_noM3, ch, stp ).val * ratio[setupKey+ch]
                                    if args.year != 2018:
                                        pfSF    += y_scale * e.L1PrefireSystematic(            r_noM3, ch, stp ).val * ratio[setupKey+ch]


                        def addUnc( c, name, binname, pName, unc, unc_yield, signal ):
                            if newPOI_input and signal:
                                if name in sigUnc: sigUnc[name] += u_float(0,unc)*unc_yield
                                else:              sigUnc[name]  = u_float(0,unc)*unc_yield
                            else:
                                if unc > 0:
                                    c.specifyUncertainty( name, binname, pName, 1 + unc )

                        if args.parameters and signal and "4p" in setup.name:
                            # 10% uncertainty on signal in 4p for LO/NLO nJet dependence
                            addUnc( c, "EFT_nJet", binname, pName, 0.10, expected.val, signal )

                        addUnc( c, "QCD_normalization", binname, pName, qcdUnc, expected.val, signal )

                        if setup.bTagged:
                            addUnc( c, "QCD_1b_nJet_dependence", binname, pName, qcd1b4p, expected.val, signal )
                            addUnc( c, "QCD_1b_normalization", binname, pName, qcd1bUnc, expected.val, signal )

                        if not setup.bTagged:
                            addUnc( c, "QCD_0b_normalization", binname, pName, qcd0bUnc, expected.val, signal )
                            addUnc( c, "QCD_0b_nJet_dependence", binname, pName, qcd0b4p, expected.val, signal )

                        addUnc( c, "TT_normalization", binname, pName, ttUnc, expected.val, signal )

                        if with1pCR:
                            addUnc( c, "Scale",         binname, pName, scale,   expected.val, signal )
                            addUnc( c, "PDF",           binname, pName, pdf,     expected.val, signal )
                            addUnc( c, "erdOn",         binname, pName, erdOn,   expected.val, signal )
                            addUnc( c, "QCDbased",         binname, pName, qcdBased,   expected.val, signal )
                            addUnc( c, "GluonMove",         binname, pName, gluonMove,   expected.val, signal )
                            addUnc( c, "Tune",          binname, pName, tune,    expected.val, signal )
                            addUnc( c, "Parton_Showering",          binname, pName, ps,    expected.val, signal )
                        for j in jesTags:
                            addUnc( c, "JEC_%s"%j,           binname, pName, locals()["jec_%s"%j],     expected.val, signal )
                        addUnc( c, "JER_%i"%args.year,           binname, pName, jer,     expected.val, signal )
                        addUnc( c, "EGammaScale",           binname, pName, ees,     expected.val, signal )
                        addUnc( c, "EGammaResolution",           binname, pName, eer,     expected.val, signal )
                        addUnc( c, "PU",            binname, pName, pu,      expected.val, signal )
                        addUnc( c, heavyFlavor,           binname, pName, sfb,     expected.val, signal )
                        addUnc( c, lightFlavor,           binname, pName, sfl,     expected.val, signal )
                        addUnc( c, "Trigger_electrons_%i"%args.year,       binname, pName, trigger_e, expected.val, signal )
                        addUnc( c, "electron_ID",      binname, pName, lepSF_e,   expected.val, signal )
                        addUnc( c, "electron_reco", binname, pName, lepTrSF, expected.val, signal )
                        addUnc( c, "Trigger_muons_%i"%args.year,       binname, pName, trigger_mu, expected.val, signal )
                        addUnc( c, "muon_ID_extrapolation",      binname, pName, lepSF_muExt,   expected.val, signal )
                        addUnc( c, "muon_ID_sta_%i"%args.year,      binname, pName, lepSF_muStat,   expected.val, signal )
                        addUnc( c, "muon_ID_syst",      binname, pName, lepSF_muSyst,   expected.val, signal )
                        if args.year != 2018:
                            addUnc( c, "L1_Prefiring",     binname, pName, pfSF,    expected.val, signal )
                        addUnc( c, "top_pt_reweighting", binname, pName, topPt, expected.val, signal )

                        if with1pCR:
                            addUnc( c, "photon_ID",      binname, pName, phSF,    expected.val, signal )
#                            if args.year == 2016:
#                                addUnc( c, "photon_ID_AltSig_2016",      binname, pName, phSFAltSig,    expected.val, signal )
                            addUnc( c, "pixelSeed_veto_%i"%args.year,       binname, pName, eVetoSF, expected.val, signal )

                        if not args.inclRegion and setup.signalregion and signal and args.addPtBinnedUnc:
                            for i in range(len(sigBin_thresh)-1):
                                addUnc( c, "Signal_mu_3_Bin%i_%s"%(i,str(args.year)), binname, pName, locals()["Signal_mu_3_bin%i_unc"%i], expected.val, signal )
                                addUnc( c, "Signal_e_3_Bin%i_%s"%(i,str(args.year)), binname, pName, locals()["Signal_e_3_bin%i_unc"%i], expected.val, signal )
                                if i != sigIndex:
                                    addUnc( c, "Signal_e_4p_Bin%i_%s"%(i,str(args.year)), binname, pName, locals()["Signal_e_4p_bin%i_unc"%i], expected.val, signal )
                                    addUnc( c, "Signal_mu_4p_Bin%i_%s"%(i,str(args.year)), binname, pName, locals()["Signal_mu_4p_bin%i_unc"%i], expected.val, signal )

                        if not args.inclRegion:
                            for i in range(1, len(misIDPT_thresholds)-1):
                                addUnc( c, "misID_pT_Bin%i_%i"%(i,args.year), binname, pName, locals()["misID_bin%i_unc"%i], expected.val, signal )

                            for i in range(1, len(WGPT_thresholds)-1):
                                addUnc( c, "WGamma_pT_Bin%i"%(i), binname, pName, locals()["WGamma_bin%i_unc"%i], expected.val, signal )
                                addUnc( c, "ZGamma_pT_Bin%i"%(i), binname, pName, locals()["ZGamma_bin%i_unc"%i], expected.val, signal )

#                        if args.parameters:
#                            addUnc( c, "MisID_normalization_%i"%args.year, binname, pName, misIDUnc, expected.val, signal )
#                            addUnc( c, "WGamma_normalization", binname, pName, wg, expected.val, signal )

                        addUnc( c, "DY_normalization", binname, pName, dyUnc, expected.val, signal )
                        addUnc( c, "MisID_extrapolation_%i"%args.year, binname, pName, misExUnc if setup.signalregion else 0, expected.val, signal )
                        addUnc( c, "Other_normalization", binname, pName, otherUnc, expected.val, signal )
                        addUnc( c, "ZGamma_normalization", binname, pName, zg, expected.val, signal )
                        addUnc( c, "MisID_nJet_dependence_%i"%args.year, binname, pName, misID4p, expected.val, signal )
                        addUnc( c, "ZGamma_nJet_dependence", binname, pName, zg4p, expected.val, signal )
                        addUnc( c, "WGamma_nJet_dependence", binname, pName, wg4p, expected.val, signal )
                        addUnc( c, "Gluon_splitting", binname, pName, gluon, expected.val, signal )

                        if setup.signalregion:
                            addUnc( c, "fake_photon_DD_normalization", binname, pName, hadFakesUnc, expected.val, signal )
                            addUnc( c, "fake_photon_MC_normalization", binname, pName, 0, expected.val, signal )

                            if args.year == 2017:
                                addUnc( c, "fake_photon_model_2017", binname, pName, hadFakes17Unc, expected.val, signal )
                        else:
                            addUnc( c, "fake_photon_MC_normalization", binname, pName, hadFakesUnc, expected.val, signal )
                            addUnc( c, "fake_photon_DD_normalization", binname, pName, 0, expected.val, signal )

                            if args.year == 2017:
                                addUnc( c, "fake_photon_model_2017", binname, pName, 0, expected.val, signal )

                        # MC bkg stat (some condition to neglect the smaller ones?)
                        if not args.noMCStat:
                            uname = "Stat_%s_%s"%(binname, pName if not (newPOI_input and signal) else "signal")
                            if not (newPOI_input and signal):
                                c.addUncertainty( uname, "lnN" )
                            if expected.val > 0:
                                addUnc( c, uname, binname, pName, expected.sigma/expected.val, expected.val, signal )

                    if newPOI_input:
                        if not args.noMCStat:
                            uname = "Stat_%s_%s"%(binname,"signal")
                            c.addUncertainty( uname, "lnN" )
                        c.specifyExpectation( binname, "signal", sigExp.val )
                        if sigExp.val:
                            for key, val in sigUnc.items():
                                if val.sigma/sigExp.val > 0:
                                    c.specifyUncertainty( key, binname, "signal", 1 + val.sigma/sigExp.val )

#                    if args.expected or (args.year in [2017,2018] and not args.unblind and setup.signalregion):
                    if args.expected:
                        #if args.linTest != 1:# and setup.signalregion:
                            #c.specifyObservation( binname, int( round( total_exp_bkg*args.linTest, 0 ) ) )
                            #logger.info( "Expected observation: %s", int( round( total_exp_bkg*args.linTest, 0 ) ) )
                        #else:
                            c.specifyObservation( binname, int( round( total_exp_bkg, 0 ) ) )
                            logger.info( "Expected observation: %s", int( round( total_exp_bkg, 0 ) ) )
                    else:
                        c.specifyObservation( binname,  int( observation.cachedObservation(r, channel, setup).val )  if not "null" in setup.name.lower() else 0 )
                        logger.info( "Observation: %s", int( observation.cachedObservation(r, channel, setup).val )  if not "null" in setup.name.lower() else 0 )

                    #if mute and total_exp_bkg <= 0.01:
                        #c.muted[binname] = True

        # Flat luminosity uncertainty
        c.addUncertainty( "Int_Luminosity_%i"%args.year, "lnN" )
        c.addUncertainty( "Int_Luminosity_corr", "lnN" )
        if args.year == 2016:
            c.addUncertainty( "Int_Luminosity_2016_2017", "lnN" )
            c.specifyFlatUncertainty( "Int_Luminosity_%i"%args.year, 1.022 ) #uncorrelated
            c.specifyFlatUncertainty( "Int_Luminosity_corr", 1.009 ) #correlated
            c.specifyFlatUncertainty( "Int_Luminosity_2016_2017", 1.008 ) #16-17 correlated
        elif args.year == 2017:
            c.addUncertainty( "Int_Luminosity_2016_2017", "lnN" )
            c.addUncertainty( "Int_Luminosity_2017_2018", "lnN" )
            c.specifyFlatUncertainty( "Int_Luminosity_%i"%args.year, 1.02 ) #uncorrelated
            c.specifyFlatUncertainty( "Int_Luminosity_corr", 1.008 ) #correlated
            c.specifyFlatUncertainty( "Int_Luminosity_2016_2017", 1.006 ) #16-17 correlated
            c.specifyFlatUncertainty( "Int_Luminosity_2017_2018", 1.004 ) #17-18 correlated
        elif args.year == 2018:
            c.addUncertainty( "Int_Luminosity_2017_2018", "lnN" )
            c.specifyFlatUncertainty( "Int_Luminosity_%i"%args.year, 1.015 ) #uncorrelated
            c.specifyFlatUncertainty( "Int_Luminosity_corr", 1.02 ) #correlated
            c.specifyFlatUncertainty( "Int_Luminosity_2017_2018", 1.003 ) #17-18 correlated

        cardFileNameTxt     = c.writeToFile( cardFileNameTxt )
        cardFileNameShape   = c.writeToShapeFile( cardFileNameShape, noMCStat=args.noMCStat, poisThresh=0 if args.parameters else 20 )
        cardFileName        = cardFileNameTxt if args.useTxt else cardFileNameShape
    else:
        logger.info( "File %s found. Reusing."%cardFileName )
        cardFileNameShape = cardFileNameShape.replace('.root', 'Card.txt')
        cardFileName      = cardFileNameTxt if args.useTxt else cardFileNameShape
    
    sConfig = "_".join(regionNames)
    res = None

    if args.parameters:
        options = "--expectSignal=1 --freezeParameters r --setParameters r=1 --X-rtd REMOVE_CONSTANT_ZERO_POINT=1"
        nll          = c.calcNLL( fname=cardFileName, options=options )
        nllCache.add( sEFTConfig, nll, overwrite=True )
        print nll
        print sEFTConfig
#        c.goodnessOfFitTest(cardFileName)
        if not args.plot: sys.exit(0)
    else:
        options = "--expectSignal=1"
        options += " --rMin 0.5 --rMax 1.5 --cminDefaultMinimizerTolerance=0.01"
        if args.freezeR:
            options = "--setParameters r=1 --freezeParameters r"
    res = c.calcLimit( cardFileName, options=options )
    options = ""

    if not args.skipFitDiagnostics:
        if not args.parameters:
            # options for running the bkg only fit with r=1
            options += " --customStartingPoint --expectSignal=1"
            if args.freezeR:
                options += " --rMin 0.99 --rMax 1.01"
#            options += " --rMin 0.5 --rMax 1.5 --cminDefaultMinimizerTolerance=0.01"

        else:
            options += " --rMin 0.99 --rMax 1.01"
        c.calcNuisances( cardFileName, bonly=args.bkgOnly, options=options )
        if args.freezeSigUnc:
            Results = CombineResults( cardFile=cardFileNameTxt, plotDirectory="./", year=args.year, bkgOnly=args.bkgOnly, isSearch=False )
            postFit = Results.getPulls( postFit=True )
            pulls = [ p+"="+str(postFit[p].val) for p in freezeParams ]
            c.calcNuisances( cardFileName, bonly=args.bkgOnly, options=options+" --setParameters %s --freezeParameters %s"%(",".join(pulls),",".join(freezeParams)) )

    if args.plot:
        path  = os.environ["CMSSW_BASE"]
        path +="/src/TTGammaEFT/plots/plotsLukas/regions"
        if args.expected:
            cdir  = "limits/cardFiles/defaultSetup/expected"
        else:
            cdir  = "limits/cardFiles/defaultSetup/observed"

        if args.parameters:
            cdir += "/" + cardFileNameTxt.split("/")[-2]
        cfile = cardFileNameTxt.split("/")[-1].split(".")[0]

        cmd = "python %s/fitResults.py --carddir %s --cardfile %s --linTest %s --year %i --plotCovMatrix --plotRegionPlot %s --cores %i %s %s %s %s %s %s"%(path, cdir, cfile, str(args.linTest), args.year, "--bkgOnly" if args.bkgOnly else "", 1, "--expected" if args.expected else "", "--wgPOI" if args.wgPOI else "", "--misIDPOI" if args.misIDPOI else "", "--ttPOI" if args.ttPOI else "", "--dyPOI" if args.dyPOI else "", "--wJetsPOI" if args.wJetsPOI else "")
        logger.info("Executing plot command: %s"%cmd)
        os.system(cmd)
        cmd = "python %s/fitResults.py --carddir %s --cardfile %s --linTest %s --year %i --plotCorrelations --plotCovMatrix --plotRegionPlot --plotImpacts --postFit %s --cores %i %s %s %s %s %s %s"%(path, cdir, cfile, str(args.linTest), args.year, "--bkgOnly" if args.bkgOnly else "", 1, "--expected" if args.expected else "", "--wgPOI" if args.wgPOI else "", "--misIDPOI" if args.misIDPOI else "", "--ttPOI" if args.ttPOI else "", "--dyPOI" if args.dyPOI else "", "--wJetsPOI" if args.wJetsPOI else "")
        logger.info("Executing plot command: %s"%cmd)
        os.system(cmd)

    ###################
    # extract the SFs #
    ###################
    if not args.useTxt and not args.skipFitDiagnostics and not args.parameters:
        # Would be a bit more complicated with the classical txt files, so only automatically extract the SF when using shape based datacards
        
        if not args.wgPOI:
            default_QCD1b_unc = 0.5*0.5 #uncorrelated part, 50% correlation between 0b and 1b, generally 50%uncertainty
            default_QCD0b_unc = 0.5*0.5 #uncorrelated part, 50% correlation between 0b and 1b, generally 50%uncertainty
            default_QCD_unc   = 0.5*0.866025 #correlated part, 50% correlation between 0b and 1b, generally 50%uncertainty
        else:
            default_QCD1b_unc = 0.
            default_QCD0b_unc = 0.
            default_QCD_unc   = 0.5
        default_HadFakes_DD_unc = 0.05
        default_HadFakes_MC_unc = 0.05
        default_HadFakes_2017_unc = 0.20
        default_ZG_unc    = 0.3
        default_Other_unc    = 0.30
        default_misID4p_unc    = 0.2
        default_ZG4p_unc    = 0.4
        default_DY4p_unc    = 0.2
        default_WG4p_unc    = 0.4
        default_DY_unc    = 0.08
        default_QCD0b4p_unc    = 0.2
        default_QCD1b4p_unc    = 0.4
        unc = {
                "QCD_normalization":default_QCD_unc,
                "QCD_0b_normalization":default_QCD0b_unc,
                "QCD_1b_normalization":default_QCD1b_unc,
                "ZGamma_normalization":default_ZG_unc,
                "Other_normalization":default_Other_unc,
                "fake_photon_DD_normalization":default_HadFakes_DD_unc,
                "fake_photon_MC_normalization":default_HadFakes_MC_unc,
                "fake_photon_model_2017":default_HadFakes_2017_unc,
                "MisID_nJet_dependence_%i"%args.year:default_misID4p_unc,
                "ZGamma_nJet_dependence":default_ZG4p_unc,
                "DY_nJet_dependence":default_DY4p_unc,
                "WGamma_nJet_dependence":default_WG4p_unc,
                "DY_normalization":default_DY_unc,
                "QCD_0b_nJet_dependence":default_QCD0b4p_unc,
                "QCD_1b_nJet_dependence":default_QCD1b4p_unc,
              }
        rateParam = [
                    "MisID_normalization_2016",
                    "MisID_normalization_2017",
                    "MisID_normalization_2018",
                    "WGamma_normalization",
#                    "DY_normalization",
                    ]

        Results = CombineResults( cardFile=cardFileNameTxt, plotDirectory="./", year=args.year, bkgOnly=args.bkgOnly, isSearch=False )
        postFit = Results.getPulls( postFit=True )

        if not os.path.isdir("logs"): os.mkdir("logs")
        write_time  = time.strftime("%Y %m %d %H:%M:%S", time.localtime())

        with open("logs/cardFiles.dat", "a") as f:
            f.write( cardFileNameTxt + "\n" )

        with open("logs/scaleFactors.dat", "a") as f:
            f.write( "\n\n" + cardFileNameTxt + "\n")

            sf = "{:20} {:4.2f} +- {:4.2f}".format( "POI", postFit["r"].val, postFit["r"].sigma )
            print sf
            f.write( str(args.year) + ": " + write_time + ": " + "_".join( regionNames ) + ": " + sf + "\n" )
            for sf_name in unc.keys():
                if sf_name not in postFit.keys(): continue
                sf = "{:20} {:4.2f} +- {:4.2f}".format( sf_name, 1+(postFit[sf_name].val*unc[sf_name]), postFit[sf_name].sigma*unc[sf_name] )
                print sf
                f.write( str(args.year) + ": " + write_time + ": " + "_".join( regionNames ) + ": " + sf + "\n" )
            for sf_name in rateParam:
                if sf_name not in postFit.keys(): continue
                sf = "{:20} {:4.2f} +- {:4.2f}".format( sf_name, postFit[sf_name].val, postFit[sf_name].sigma )
                print sf
                f.write( str(args.year) + ": " + write_time + ": " + "_".join( regionNames ) + ": " + sf + "\n" )


######################################
# Load the signals and run the code! #
######################################

results = wrapper()


