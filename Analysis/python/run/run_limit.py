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

from TTGammaEFT.Tools.user               import cache_directory, combineReleaseLocation, cardfileLocation
from Analysis.Tools.MergingDirDB         import MergingDirDB
from Analysis.Tools.u_float              import u_float
from Analysis.Tools.cardFileWriter       import cardFileWriter
from Analysis.Tools.cardFileWriter.CombineResults       import CombineResults
from Analysis.Tools.getPostFit           import getPrePostFitFromMLF, getFitResults

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
argParser.add_argument( "--addMisIDSF",         action="store_true",                                                        help="add default misID scale factor" )
argParser.add_argument( "--addSSM",             action="store_true",                                                        help="add default signal strength modifer" )
argParser.add_argument( "--keepCard",           action="store_true",                                                        help="Overwrite existing output files" )
argParser.add_argument( "--expected",           action="store_true",                                                        help="Use sum of backgrounds instead of data." )
argParser.add_argument( "--useTxt",             action="store_true",                                                        help="Use txt based cardFiles instead of root/shape based ones?" )
argParser.add_argument( "--skipFitDiagnostics", action="store_true",                                                        help="Don't do the fitDiagnostics (this is necessary for pre/postfit plots, but not 2D scans)?" )
argParser.add_argument( "--year",               action="store",      default="2016",   type=str,                              help="Which year?" )
argParser.add_argument( "--linTest",            action="store",      default=1,   type=float,                              help="linearity test: scale data by factor" )
argParser.add_argument( "--runOnLxPlus",        action="store_true",                                                        help="Change the global redirector of samples")
argParser.add_argument( "--misIDPOI",           action="store_true",                                                        help="Change POI to misID SF")
argParser.add_argument( "--dyPOI",              action="store_true",                                                        help="Change POI to misID SF")
argParser.add_argument( "--wgPOI",              action="store_true",                                                        help="Change POI to WGamma SF")
argParser.add_argument( "--ttPOI",              action="store_true",                                                        help="Change POI to misID SF")
argParser.add_argument( "--wJetsPOI",           action="store_true",                                                        help="Change POI to misID SF")
argParser.add_argument( "--checkOnly",          action="store_true",                                                        help="Check the SF only")
argParser.add_argument( "--bkgOnly",            action="store_true",                                                        help="background only")
argParser.add_argument( "--unblind",            action="store_true",                                                        help="unblind 2017/2018")
argParser.add_argument( "--plot",               action="store_true",                                                        help="run plots?")
argParser.add_argument( "--noMCStat",           action="store_true",                                                        help="create file without MC stat?")
argParser.add_argument('--order',               action='store',      default=2, type=int,                                                             help='Polynomial order of weight string (e.g. 2)')
argParser.add_argument('--parameters',          action='store',      default=[], type=str, nargs='+',                       help = "argument parameters")
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
    locals()["setup"+key].bTagged      = locals()["setup"+key].parameters["nBTag"][1] != 0
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

baseDir       = os.path.join( cache_directory, "analysis",  str(args.year), "limits" )
limitDir      = os.path.join( baseDir, "cardFiles", args.label, "expected" if args.expected else "observed" )
if not os.path.exists( limitDir ): os.makedirs( limitDir )

cacheDir        = os.path.join( cache_directory, "modelling",  str(args.year) )

cacheFileName   = os.path.join( cacheDir, "Scale" )
scaleUncCache   = MergingDirDB( cacheFileName )

cacheFileName   = os.path.join( cacheDir, "PDF" )
pdfUncCache     = MergingDirDB( cacheFileName )

cacheFileName   = os.path.join( cacheDir, "PS" )
psUncCache      = MergingDirDB( cacheFileName )

if args.parameters:
    # load and define the EFT sample
    from TTGammaEFT.Samples.genTuples_TTGamma_EFT_postProcessed  import *
    eftSample = TTG_4WC_ref

    cacheFileName = os.path.join( baseDir, "calculatednll" )
    nllCache      = MergingDirDB( cacheFileName )

    baseDir       = os.path.join( cache_directory, "analysis", "eft" )
    cacheFileName = os.path.join( baseDir, eftSample.name )
    yieldCache    = MergingDirDB( cacheFileName )

    configlist = regionNames + EFTparams
    configlist.append("incl" if args.inclRegion else "diff")
    configlist.append("expected" if args.expected else "observed")

    sEFTConfig = "_".join(configlist)
    if not args.overwrite and nllCache.contains( sEFTConfig ): sys.exit(0)


# JEC Tags, (standard is "Total")
jesTags = ['FlavorQCD', 'RelativeBal', 'HF', 'BBEC1', 'EC2', 'Absolute', 'Absolute_%i'%args.year, 'HF_%i'%args.year, 'EC2_%i'%args.year, 'RelativeSample_%i'%args.year, 'BBEC1_%i'%args.year]

def getScaleUnc(name, r, channel, setup):
    key      = uniqueKey( name, r, channel, setup ) + tuple(str(args.year))
    scaleUnc = scaleUncCache.get( key )
    return max(0.0005, scaleUnc)

def getPDFUnc(name, r, channel, setup):
    key    = uniqueKey( name, r, channel, setup ) + tuple(str(args.year))
    PDFUnc = pdfUncCache.get( key )
    return max(0.0005, PDFUnc)

def getPSUnc(name, r, channel, setup):
    key   = uniqueKey( name, r, channel, setup ) + tuple(str(args.year))
    PSUnc = psUncCache.get( key )
    return max(0.0005, PSUnc)

def wrapper():
    c = cardFileWriter.cardFileWriter()
    c.releaseLocation = combineReleaseLocation

    if args.parameters:
        cardFileNameTxt   = os.path.join( limitDir, "_".join( regionNames ), eft + ".txt" )
    else:
        cardFileNameTxt   = os.path.join( limitDir, "_".join( regionNames ) + ".txt" )
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
        c.addUncertainty( "PU",            shapeString) #correlated
        for j in jesTags:
            c.addUncertainty( "JEC_%s"%j,           shapeString) #partly correlated
        c.addUncertainty( "JER_%i"%args.year,           shapeString) #uncorrelated
        c.addUncertainty( "EGamma_Scale",           shapeString) #correlated
        c.addUncertainty( "EGamma_Resolution",       shapeString) #correlated
        c.addUncertainty( "Muon_pT_error",           shapeString) #correlated
        c.addUncertainty( "heavy_flavor",           shapeString) #need to check
        c.addUncertainty( "light_flavor",           shapeString) #need to check
        c.addUncertainty( "Trigger_muons_%i"%args.year,       shapeString) #uncorrelated
        c.addUncertainty( "Trigger_electrons_%i"%args.year,       shapeString) #uncorrelated
        c.addUncertainty( "muon_ID_syst",      shapeString) #correlated in e, split stat/syst in mu
        c.addUncertainty( "muon_ID_stat_%i"%args.year,      shapeString) #correlated in e, split stat/syst in mu
        c.addUncertainty( "electron_ID",      shapeString) #correlated in e, split stat/syst in mu
        c.addUncertainty( "electron_reco", shapeString) #uncorrelated to e ID (non existing for mu)
        c.addUncertainty( "L1_Prefiring",     shapeString) #need to check
        if with1pCR:
            c.addUncertainty( "photon_ID",      shapeString)
            c.addUncertainty( "pixelSeed_veto_%i"%args.year,       shapeString) #uncorrelated
            # theory (PDF, scale, ISR)
            c.addUncertainty( "Tune",          shapeString)
            c.addUncertainty( "erdOn",         shapeString)
            c.addUncertainty( "Scale",         shapeString)
            c.addUncertainty( "PDF",           shapeString)
            c.addUncertainty( "Parton_Showering",            shapeString)
#            c.addUncertainty( "ISR",           shapeString)

        default_TTGpT_unc = 0.05
        gammaPT_thresholds = sorted(list(set(pTG_thresh + highpTG_thresh)))
        gammaPT_thresholds = gammaPT_thresholds[1:] + [ gammaPT_thresholds[0] ]
#        if not args.inclRegion and with1pCR:
#            for i in range(len(gammaPT_thresholds)-1):
#                c.addUncertainty( "TTG_pT_Bin%i"%i, shapeString )

        default_misIDpT_unc = 0.20
        misIDPT_thresholds = [ 20, 35, 50, 65, 80, 120, 160, -999 ]
        if not args.inclRegion and with1pCR:
            for i in range(len(misIDPT_thresholds)-1):
                c.addUncertainty( "misID_pT_Bin%i_%i"%(i,args.year), shapeString )

        default_QCD_unc = 0.5
        c.addUncertainty( "QCD_1b_normalization", shapeString )
        c.addUncertainty( "QCD_0b_normalization", shapeString )
#        c.addUncertainty( "QCD_TF", shapeString )

        default_HadFakes_unc = 0.15
        c.addUncertainty( "fake_photon_normalization",      shapeString )

        default_HadFakes_2017_unc = 0.20
        if args.year == 2017:
            c.addUncertainty( "fake_photon_model_2017",      shapeString )

        if with1pCR and not args.wgPOI:
            c.addFreeParameter("WGamma_normalization", '*WG*', 1, '[0.,2.]')

        default_ZG_unc    = 0.3
        c.addUncertainty( "ZGamma_normalization",      shapeString )

        default_ZG_gluon_unc    = 0.12 # only on the fraction of 2 gen b-jets in the SR
        default_WG_gluon_unc    = 0.04 # only on the fraction of 2 gen b-jets in the SR
        c.addUncertainty( "Gluon_splitting",      shapeString )

        default_Other_unc    = 0.30
        c.addUncertainty( "Other_normalization",      shapeString )

        default_misID4p_unc    = 0.5
        if any( ["3" in name and not "4pM3" in name for name in args.useRegions] ) and any( ["4p" in name for name in args.useRegions] ):
            c.addUncertainty( "MisID_nJet_dependence",      shapeString )

        default_ZG4p_unc    = 0.8
        if any( ["3" in name and not "4pM3" in name for name in args.useRegions] ) and any( ["4p" in name for name in args.useRegions] ):
            c.addUncertainty( "ZGamma_nJet_dependence",      shapeString )

        default_DY4p_unc    = 0.8
        if any( ["3" in name and not "4pM3" in name for name in args.useRegions] ) and any( ["4p" in name for name in args.useRegions] ):
            c.addUncertainty( "ZJets_nJet_dependence",      shapeString )
    
        default_WG4p_unc    = 0.5
        if any( ["3" in name and not "4pM3" in name for name in args.useRegions] ) and any( ["4p" in name for name in args.useRegions] ):
            c.addUncertainty( "WGamma_nJet_dependence",      shapeString )
    
        default_DY_unc    = 0.08
        if any( [ name in ["DY2","DY3","DY4","DY4p","DY5"] for name in args.useRegions] ) and not args.dyPOI:
            c.addFreeParameter("ZJets_normalization", '*DY*', 1, '[0.,2.]')
#            c.addFreeParameter("DY", 'DY', 1, '[0.5,1.5]')
        elif not args.dyPOI:
            c.addUncertainty( "ZJets_normalization", shapeString )
            c.addUncertainty( "ZJets_extrapolation", shapeString )

        if not args.addMisIDSF and not args.misIDPOI and with1pCR:
            c.addFreeParameter("MisID_normalization_%i"%args.year, '*misID*', 1, '[0.,5.]')
#            c.addFreeParameter("misID_%i"%args.year, 'misID', 1, '[0,5]')
        elif not args.misIDPOI and with1pCR:
            c.addFreeParameter("MisID_normalization_%i"%args.year, '*misID*', 1, '[0.,2.]')
#            c.addFreeParameter("misID_%i"%args.year, 'misID', 1, '[0,2]')

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

                        # calc eft ratio
                        ratio = 1.
                        if args.parameters:                        

                            smyieldkey  =  (setup.name, str(r),channel,  "ctZ_0_ctZI_0")
                            if yieldCache.contains( smyieldkey ): smyield =  yieldCache.get(smyieldkey)["val"]
                            else:                                 raise Exception("yieldCache does not contain key")

                            yieldkey    =  (setup.name, str(r),channel, str(eft))
                            if yieldCache.contains( yieldkey ): eftyield =  yieldCache.get(yieldkey)["val"]
                            else:                               raise Exception("yieldCache does not contain key")

                            if smyield > 0: ratio = eftyield / smyield

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

                            if signal and args.parameters: exp_yield *= ratio
                            if signal and args.linTest != 1:# and setup.signalregion:
                                exp_yield /= args.linTest
                                
                            if signal and args.addSSM:
                                exp_yield *= SSMSF_val["RunII"].val
                                logger.info( "Scaling signal by %f"%(SSMSF_val["RunII"].val) )
                            if e.name.count( "WJets" ) and args.addWJetsSF:
                                exp_yield *= WJetsSF_val["RunII"].val
                                logger.info( "Scaling WJets background %s by %f"%(e.name,WJetsSF_val["RunII"].val) )
                            if e.name.count( "DY" ) and args.addDYSF:

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
                                exp_yield *= WGSF_val["RunII"].val
                                logger.info( "Scaling WG background %s by %f"%(e.name,WGSF_val["RunII"].val) )
                            if e.name.count( "ZG" ) and args.addZGSF:
                                exp_yield *= ZGSF_val["RunII"].val
                                logger.info( "Scaling ZG background %s by %f"%(e.name,ZGSF_val["RunII"].val) )
                            if e.name.count( "misID" ) and args.addMisIDSF:
                                exp_yield *= misIDSF_val[args.year].val
                                logger.info( "Scaling misID background %s by %f"%(e.name,misIDSF_val[args.year].val) )
                            e.expYield = exp_yield
                            expected  += exp_yield

                        logger.info( "Expectation for process %s: %s", pName, expected.val )

                        if newPOI_input and signal:
                            sigExp += expected
                            logger.info( "Adding expectation for process %s to signal. Total signal now: %s", pName, sigExp )
                        else:
                            c.specifyExpectation( binname, pName, expected.val ) #if expected.val > 0 else 0.01 )

                        # correct observation for eft
                        if signal and args.parameters:
                            total_exp_bkg += (expected.val/ratio) if ratio else 0
                        elif signal and args.linTest != 1:# and setup.signalregion:
                            total_exp_bkg += expected.val*args.linTest
                        else:
                            total_exp_bkg += expected.val
                        if signal and expected.val <= 0.01: mute = True

                        for j in jesTags:
                            locals()["jec_%s"%j] = 0
                        tune, erdOn, pu, mer, eer, ees, jer, sfb, sfl, trigger_e, trigger_mu, lepSF_e, lepSF_muStat, lepSF_muSyst, lepTrSF, phSF, eVetoSF, pfSF = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                        ps, scale, pdf, isr = 0, 0, 0, 0
                        qcdTF3, qcdTF4, wjets4p, wg4p = 0, 0, 0, 0
                        dyGenUnc, ttGenUnc, vgGenUnc, wjetsGenUnc, otherGenUnc, misIDUnc, lowSieieUnc, highSieieUnc, misIDPtUnc = 0, 0, 0, 0, 0, 0, 0, 0, 0
                        gluon, hadFakes17Unc, hadFakesUnc, wg, zg, misID4p, dy4p, zg4p, misIDUnc, qcdUnc, vgUnc, wgUnc, zgUnc, dyUnc, ttUnc, wjetsUnc, other0pUnc, otherUnc = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                        for i in range(len(gammaPT_thresholds)-1):
                            locals()["ttg_bin%i_unc"%i] = 0
                        for i in range(len(misIDPT_thresholds)-1):
                            locals()["misID_bin%i_unc"%i] = 0

                        if expected.val:
                            for e in pList:
                                y_scale   = e.expYield.val / expected.val

                                if e.name.count( "QCD" ):
                                    qcdUnc   += y_scale * default_QCD_unc
                                    qcdTF3   += y_scale * e.expYield.sigma / e.expYield.val
                                    continue # no systematics for data-driven QCD

                                if e.name.count( "DY" ):
                                    dyUnc    += y_scale * default_DY_unc
                                if e.name.count( "TT_pow" ) or (args.ttPOI and signal):
                                    ttUnc    += y_scale * default_TT_unc

                                if not args.inclRegion and not newPOI_input and (signal and setup.signalregion):
                                        pT_index = max( [ i_pt if ptCut.cutString() in r.cutString() else -1 for i_pt, ptCut in enumerate(regionsTTGlooseFine) ] )
                                        if pT_index >= 0:
                                            locals()["ttg_bin%i_unc"%pT_index] += y_scale * default_TTGpT_unc

                                if not args.inclRegion and e.name.count( "misID" ):
                                        pT_index = max( [ i_pt if ptCut.cutString() in r.cutString() else -1 for i_pt, ptCut in enumerate(regionsTTG) ] )
                                        if pT_index == -1:
                                            pT_index = max( [ i_pt if ptCut.cutString().replace("PhotonGood","PhotonNoChgIsoNoSieie") in r.cutString() else -1 for i_pt, ptCut in enumerate(regionsTTG) ] )
                                            if pT_index == -1:
                                                pT_index = max( [ i_pt if ptCut.cutString().replace("PhotonGood","PhotonNoChgIsoNoSieie") in r.cutString() else -1 for i_pt, ptCut in enumerate(regionsTTGlooseFine) ] )
                                                if pT_index >= len(regionsTTG): pT_index = len(regionsTTG)-1
                                        if pT_index >= 0:
                                            locals()["misID_bin%i_unc"%pT_index] += y_scale * default_misIDpT_unc

                                if e.name.count( "other" ):
                                    otherUnc += y_scale * default_Other_unc

                                if e.name.count( "_had" ) or e.name.count( "fakes-DD" ):
                                    hadFakesUnc += y_scale * default_HadFakes_unc
                                    if args.year == 2017:
                                        hadFakes17Unc += y_scale * default_HadFakes_2017_unc

                                if e.name.count( "ZG" ):
                                    zg += y_scale * default_ZG_unc
                                    if setup.signalregion:
                                        gluon += y_scale * default_ZG_gluon_unc

                                if e.name.count( "ZG" ) and "4" in setup.name:
                                    zg4p += y_scale * default_ZG4p_unc

                                if e.name.count( "DY" ) and "4" in setup.name:
                                    dy4p += y_scale * default_DY4p_unc

                                if e.name.count( "WG" ) and "4" in setup.name:
                                    wg4p += y_scale * default_WG4p_unc
                                    if setup.signalregion:
                                        gluon += y_scale * default_WG_gluon_unc

                                if e.name.count( "misID" ) and "4" in setup.name:
                                    misID4p += y_scale * default_misID4p_unc

                                if signal and not newPOI_input:
                                    tune    += y_scale * e.TuneSystematic(    r, channel, setup ).val
                                    erdOn   += y_scale * e.ErdOnSystematic(   r, channel, setup ).val
                                    scale   += y_scale * getScaleUnc( e.name, r, channel, setup )
                                    pdf     += y_scale * getPDFUnc(   e.name, r, channel, setup )
                                    ps      += y_scale * getPSUnc(    e.name, r, channel, setup )

                                if channel == "e":
                                    trigger_e += y_scale * e.triggerSystematic(              r, channel, setup ).val
                                    lepSF_e   += y_scale * e.leptonSFSystematic(             r, channel, setup ).val
                                    lepTrSF += y_scale * e.leptonTrackingSFSystematic(     r, channel, setup ).val
                                elif channel == "mu":
                                    trigger_mu += y_scale * e.triggerSystematic(              r, channel, setup ).val
                                    lepSF_muSyst   += y_scale * e.leptonSFSystSystematic(         r, channel, setup ).val
                                    lepSF_muStat   += y_scale * e.leptonSFStatSystematic(         r, channel, setup ).val
                                elif channel == "all":
                                    y_e  = e.cachedEstimate( r, "e",   setup )
                                    y_mu = e.cachedEstimate( r, "mu",  setup )
                                    e_ratio  = y_e.val  / e.expYield.val if e.expYield.val else 0
                                    mu_ratio = y_mu.val / e.expYield.val if e.expYield.val else 0

                                    lepTrSF    += e_ratio  * y_scale * e.leptonTrackingSFSystematic(     r, channel, setup ).val

                                    lepSF_e    += e_ratio  * y_scale * e.leptonSFSystematic(             r, channel, setup ).val
                                    trigger_e  += e_ratio  * y_scale * e.triggerSystematic(              r, channel, setup ).val
                                    lepSF_muSyst   += mu_ratio * y_scale * e.leptonSFSystSystematic(             r, channel, setup ).val
                                    lepSF_muStat   += mu_ratio * y_scale * e.leptonSFStatSystematic(             r, channel, setup ).val
                                    trigger_mu += mu_ratio * y_scale * e.triggerSystematic(              r, channel, setup ).val

                                pu      += y_scale * e.PUSystematic(                   r, channel, setup ).val

                                for j in jesTags:
                                    locals()["jec_%s"%j] = y_scale * e.JECSystematic( r, channel, setup, jes=j ).val
#                                jec     += y_scale * e.JECSystematic(                  r, channel, setup ).val
                                jer     += y_scale * e.JERSystematic(                  r, channel, setup ).val
                                eer     += y_scale * e.MERSystematic(                  r, channel, setup ).val
                                ees     += y_scale * e.EESSystematic(                  r, channel, setup ).val
                                mer     += y_scale * e.MERSystematic(                  r, channel, setup ).val
                                sfb     += y_scale * e.btaggingSFbSystematic(          r, channel, setup ).val
                                sfl     += y_scale * e.btaggingSFlSystematic(          r, channel, setup ).val
                                phSF    += y_scale * e.photonSFSystematic(             r, channel, setup ).val
                                eVetoSF += y_scale * e.photonElectronVetoSFSystematic( r, channel, setup ).val
                                pfSF    += y_scale * e.L1PrefireSystematic(            r, channel, setup ).val


                        def addUnc( c, name, binname, pName, unc, unc_yield, signal ):
                            if newPOI_input and signal:
                                if name in sigUnc: sigUnc[name] += u_float(0,unc)*unc_yield
                                else:              sigUnc[name]  = u_float(0,unc)*unc_yield
                            else:
                                c.specifyUncertainty( name, binname, pName, 1 + unc )

                        if qcdUnc > 0.0005:
                            addUnc( c, "QCD_1b_normalization" if setup.bTagged else "QCD_0b_normalization", binname, pName, qcdUnc, expected.val, signal )

                        if with1pCR:
                            if scale > 0.0005: # and setup.signalregion:
                                addUnc( c, "Scale",         binname, pName, scale,   expected.val, signal )
                            if pdf > 0.0005: # and setup.signalregion:
                                addUnc( c, "PDF",           binname, pName, pdf,     expected.val, signal )
                            if erdOn > 0.0005: # and setup.signalregion:
                                addUnc( c, "erdOn",         binname, pName, erdOn,   expected.val, signal )
                            if tune > 0.0005: # and setup.signalregion:
                                addUnc( c, "Tune",          binname, pName, tune,    expected.val, signal )
                            if ps > 0.0005: # and setup.signalregion:
                                addUnc( c, "Parton_Showering",          binname, pName, tune,    expected.val, signal )
                        for j in jesTags:
                            if locals()["jec_%s"%j] > 0.0005:
                                addUnc( c, "JEC_%s"%j,           binname, pName, locals()["jec_%s"%j],     expected.val, signal )
#                        if jec > 0.0005:
#                            addUnc( c, "JEC",           binname, pName, jec,     expected.val, signal )
                        if jer > 0.0005:
                            addUnc( c, "JER_%i"%args.year,           binname, pName, jer,     expected.val, signal )
                        if ees > 0.0005:
                            addUnc( c, "EGamma_Scale",           binname, pName, ees,     expected.val, signal )
                        if eer > 0.0005:
                            addUnc( c, "EGamma_Resolution",           binname, pName, eer,     expected.val, signal )
                        if mer > 0.0005:
                            addUnc( c, "Muon_pT_error",           binname, pName, mer,     expected.val, signal )
                        if pu > 0.0005:
                            addUnc( c, "PU",            binname, pName, pu,      expected.val, signal )
                        if sfb > 0.0005:
                            addUnc( c, "heavy_flavor",           binname, pName, sfb,     expected.val, signal )
                        if sfl > 0.0005:
                            addUnc( c, "light_flavor",           binname, pName, sfl,     expected.val, signal )
                        if trigger_e > 0.0005:
                            addUnc( c, "Trigger_electrons_%i"%args.year,       binname, pName, trigger_e, expected.val, signal )
                        if lepSF_e > 0.0005:
                            addUnc( c, "electron_ID",      binname, pName, lepSF_e,   expected.val, signal )
                        if lepTrSF > 0.0005:
                            addUnc( c, "electron_reco", binname, pName, lepTrSF, expected.val, signal )
                        if trigger_mu > 0.0005:
                            addUnc( c, "Trigger_muons_%i"%args.year,       binname, pName, trigger_mu, expected.val, signal )
                        if lepSF_muStat > 0.0005:
                            addUnc( c, "muon_ID_stat_%i"%args.year,      binname, pName, lepSF_muStat,   expected.val, signal )
                        if lepSF_muSyst > 0.0005:
                            addUnc( c, "muon_ID_syst",      binname, pName, lepSF_muSyst,   expected.val, signal )
                        if pfSF > 0.0005:
                            addUnc( c, "L1_Prefiring",     binname, pName, pfSF,    expected.val, signal )
                        if with1pCR:
                            if phSF > 0.0005:
                                addUnc( c, "photon_ID",      binname, pName, phSF,    expected.val, signal )
                            if eVetoSF > 0.0005:
                                addUnc( c, "pixelSeed_veto_%i"%args.year,       binname, pName, eVetoSF, expected.val, signal )
                        

#                        if qcdTF3:
#                            addUnc( c, "QCD_TF", binname, pName, qcdTF3, expected.val, signal )

                        if not args.inclRegion:
                            for i in range(len(gammaPT_thresholds)-1):
                                if locals()["ttg_bin%i_unc"%i] > 0.0005:
                                    addUnc( c, "TTG_pT_Bin%i"%i, binname, pName, locals()["ttg_bin%i_unc"%i], expected.val, signal )
                            for i in range(len(misIDPT_thresholds)-1):
                                if locals()["misID_bin%i_unc"%i] > 0.0005:
                                    addUnc( c, "misID_pT_Bin%i_%i"%(i,args.year), binname, pName, locals()["misID_bin%i_unc"%i], expected.val, signal )
#                                elif counter == 1 and not setup.signalregion and signal and not newPOI_input:
#                                    addUnc( c, "TTG_pT_Bin%i"%i, binname, pName, 0.0005, expected.val, signal )

                        if dyUnc > 0.0005:
                            addUnc( c, "ZJets_normalization", binname, pName, dyUnc, expected.val, signal )
                            addUnc( c, "ZJets_extrapolation", binname, pName, dyUnc, expected.val, signal )
                        if otherUnc > 0.0005:
                            addUnc( c, "Other_normalization", binname, pName, otherUnc, expected.val, signal )
                        if zg > 0.0005:
                            addUnc( c, "ZGamma_normalization", binname, pName, zg, expected.val, signal )
                        if misID4p > 0.0005:
                            addUnc( c, "MisID_nJet_dependence", binname, pName, misID4p, expected.val, signal )
                        if zg4p > 0.0005:
                            addUnc( c, "ZGamma_nJet_dependence", binname, pName, zg4p, expected.val, signal )
                        if dy4p > 0.0005:
                            addUnc( c, "ZJets_nJet_dependence", binname, pName, dy4p, expected.val, signal )
                        if wg4p > 0.0005:
                            addUnc( c, "WGamma_nJet_dependence", binname, pName, wg4p, expected.val, signal )
                        if gluon > 0.0005:
                            addUnc( c, "Gluon_splitting", binname, pName, gluon, expected.val, signal )
                        if hadFakesUnc > 0.0005: # and args.addFakeSF:
                            addUnc( c, "fake_photon_normalization", binname, pName, hadFakesUnc, expected.val, signal )
                        if hadFakes17Unc > 0.0005: # and args.addFakeSF:
                            addUnc( c, "fake_photon_model_2017", binname, pName, hadFakes17Unc, expected.val, signal )

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
                                c.specifyUncertainty( key, binname, "signal", 1 + val.sigma/sigExp.val )

                    if args.expected or (args.year in [2017,2018] and not args.unblind and setup.signalregion):
#                        if args.linTest != 1:# and setup.signalregion:
#                            c.specifyObservation( binname, int( round( total_exp_bkg*args.linTest, 0 ) ) )
#                            logger.info( "Expected observation: %s", int( round( total_exp_bkg*args.linTest, 0 ) ) )
#                        else:
                            c.specifyObservation( binname, int( round( total_exp_bkg, 0 ) ) )
                            logger.info( "Expected observation: %s", int( round( total_exp_bkg, 0 ) ) )
                    else:
                        c.specifyObservation( binname,  int( observation.cachedObservation(r, channel, setup).val )  if not "null" in setup.name.lower() else 0 )
                        logger.info( "Observation: %s", int( observation.cachedObservation(r, channel, setup).val )  if not "null" in setup.name.lower() else 0 )

#                    if mute and total_exp_bkg <= 0.01:
#                        c.muted[binname] = True

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
        cardFileNameShape   = c.writeToShapeFile( cardFileNameShape, noMCStat=args.noMCStat )
        cardFileName        = cardFileNameTxt if args.useTxt else cardFileNameShape
    else:
        logger.info( "File %s found. Reusing."%cardFileName )
        cardFileNameShape = cardFileNameShape.replace('.root', 'Card.txt')
        cardFileName      = cardFileNameTxt if args.useTxt else cardFileNameShape
    
    sConfig = "_".join(regionNames)
    res = None

    if args.parameters:
        nll          = c.calcNLL( cardFileName )
        nll_prefit   = nll['nll0']
        nll_postfit  = nll['nll_abs']
        NLL = nll['nll']

        if nll_prefit  is None or abs(nll_prefit) > 10000 or abs(nll_prefit) < 1e-5:   nll_prefit  = 999
        if nll_postfit is None or abs(nll_postfit) > 10000 or abs(nll_postfit) < 1e-5: nll_postfit = 999

        nllCache.add( sEFTConfig, NLL, overwrite=True )

    else:
            res = c.calcLimit( cardFileName )

            if not args.skipFitDiagnostics:
                c.calcNuisances( cardFileName, bonly=args.bkgOnly )

    if args.plot and not args.parameters:
        path  = os.environ["CMSSW_BASE"]
        path +="/src/TTGammaEFT/plots/plotsLukas/regions"
        if args.expected:
            cdir  = "limits/cardFiles/defaultSetup/expected"
        else:
            cdir  = "limits/cardFiles/defaultSetup/observed"
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
        
        default_QCD_unc = 0.5
        default_HadFakes_unc = 0.15
        default_HadFakes_2017_unc = 0.20
        default_ZG_unc    = 0.3
        default_Other_unc    = 0.30
        default_misID4p_unc    = 0.5
        default_ZG4p_unc    = 0.8
        default_DY4p_unc    = 0.8
        default_WG4p_unc    = 0.5
        default_DY_unc    = 0.08
        unc = {
                "QCD_normalization":default_QCD_unc,
                "ZGamma_normalization":default_ZG_unc,
                "Other_normalization":default_Other_unc,
                "fake_photon_normalization":default_HadFakes_unc,
                "fake_photon_model_2017":default_HadFakes_2017_unc,
                "MisID_nJet_dependence":default_misID4p_unc,
                "ZGamma_nJet_dependence":default_ZG4p_unc,
                "ZJets_nJet_dependence":default_DY4p_unc,
                "WGamma_nJet_dependence":default_WG4p_unc,
                "ZJets_normalization":default_DY_unc,
              }
        rateParam = [
                    "MisID_normalization_2016",
                    "MisID_normalization_2017",
                    "MisID_normalization_2018",
                    "WGamma_normalization",
#                    "ZJets_normalization",
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


