#!/usr/bin/env python

import os, copy, time
import ROOT
from shutil                              import copyfile
from math                                import sqrt
from helpers                             import uniqueKey

from TTGammaEFT.Analysis.EstimatorList   import EstimatorList
from TTGammaEFT.Analysis.DataObservation import DataObservation
from TTGammaEFT.Analysis.MCBasedEstimate import MCBasedEstimate
from TTGammaEFT.Analysis.Setup           import Setup
from TTGammaEFT.Analysis.regions         import regionsTTG, noPhotonRegionTTG, inclRegionsTTG, regionsTTGfake, inclRegionsTTGfake, chgIso_thresh, chgIsoRegions, gammaPT_thresholds, mLgRegions
from TTGammaEFT.Analysis.SetupHelpers    import *

from TTGammaEFT.Tools.user               import combineReleaseLocation, cardfileLocation, cache_directory
from Analysis.Tools.MergingDirDB         import MergingDirDB
from Analysis.Tools.u_float              import u_float
from TTGammaEFT.Tools.cardFileWriter       import cardFileWriter
from Analysis.Tools.getPostFit           import getPrePostFitFromMLF, getFitResults

from Analysis.Tools.cardFileWriter.CombineResults   import CombineResults

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
argParser.add_argument( "--noMCStat",           action="store_true",                                                        help="create file without MC stat?")
argParser.add_argument( "--noFakeStat"  ,       action="store_true",                                                        help="skip the fake stat uncertainty" )
argParser.add_argument( "--addVGSF",            action="store_true",                                                        help="add default DY scale factor" )
argParser.add_argument( "--addZGSF",            action="store_true",                                                        help="add default DY scale factor" )
argParser.add_argument( "--addWGSF",            action="store_true",                                                        help="add default DY scale factor" )
argParser.add_argument( "--addDYSF",            action="store_true",                                                        help="add default DY scale factor" )
argParser.add_argument( "--addWJetsSF",         action="store_true",                                                        help="add default DY scale factor" )
argParser.add_argument( "--addMisIDSF",         action="store_true",                                                        help="add default misID scale factor" )
argParser.add_argument( "--addSSM",             action="store_true",                                                        help="add default signal strength modifer" )
argParser.add_argument( "--keepCard",           action="store_true",                                                        help="Overwrite existing output files" )
argParser.add_argument( "--expected",           action="store_true",                                                        help="Use sum of backgrounds instead of data." )
argParser.add_argument( "--misIDPOI",           action="store_true",                                                        help="Change POI to misID SF")
argParser.add_argument( "--wgPOI",              action="store_true",                                                        help="Change POI to WGamma SF")
argParser.add_argument( "--dyPOI",              action="store_true",                                                        help="Change POI to misID SF")
argParser.add_argument( "--ttPOI",              action="store_true",                                                        help="Change POI to misID SF")
argParser.add_argument( "--wJetsPOI",           action="store_true",                                                        help="Change POI to misID SF")
argParser.add_argument( "--checkOnly",          action="store_true",                                                        help="Check the SF only")
argParser.add_argument( "--bkgOnly",            action="store_true",                                                        help="background only")
argParser.add_argument( "--plot",               action="store_true",                                                        help="run plots?")
argParser.add_argument( "--useTxt",             action="store_true",                                                        help="Use txt based cardFiles instead of root/shape based ones?" )
argParser.add_argument( "--skipFitDiagnostics", action="store_true",                                                        help="Don't do the fitDiagnostics (this is necessary for pre/postfit plots" )
argParser.add_argument( "--significanceScan",   action="store_true",                                                        help="Calculate significance instead?")
argParser.add_argument( "--linTest",            action="store",      default=1,   type=float,                              help="linearity test: scale data by factor" )
argParser.add_argument('--order',               action='store',      default=2, type=int,                                                             help='Polynomial order of weight string (e.g. 2)')
argParser.add_argument('--parameters',          action='store',      default=[], type=str, nargs='+',                       help = "argument parameters")
argParser.add_argument('--withbkg',             action='store_true',                                                        help="reweight sample and bkg or sample only?")
argParser.add_argument('--withEFTUnc',             action='store_true',                                                        help="add EFT uncertainty?")
argParser.add_argument('--freezeR',             action='store_true',                                                        help="add EFT uncertainty?")
argParser.add_argument('--freezeSigUnc',             action='store_true',                                                        help="add EFT uncertainty?")
argParser.add_argument('--addPtBinnedUnc',             action='store_true',                                                        help="add EFT uncertainty?")
args=argParser.parse_args()

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

default_QCD_unc = 0.5
default_ZG_unc = 0.3

# read the EFT parameters
EFTparams = []
if args.parameters:
    coeffs = args.parameters[::2]
    str_vals = args.parameters[1::2]
    for i_param, (coeff, str_val, ) in enumerate(zip(coeffs, str_vals)):
        EFTparams.append(coeff)
        EFTparams.append(str_val)

eft =  "_".join(EFTparams)


if args.keepCard:
    args.overwrite = False

regionNames = []
if not args.checkOnly:
    # Define estimators for CR
    default_setup            = Setup( year=2016, checkOnly=True )
    default_setup.estimators = EstimatorList( default_setup )
    default_setup.data       = default_setup.processes["Data"]
#    default_setup.processes  = default_setup.estimators.constructProcessDict( processDict=default_processes )
    default_setup.processes["Data"] = default_setup.data
    default_setup.addon      = ""
    default_setup.regions    = inclRegionsTTG if args.inclRegion else regionsTTG

    default_photon_setup            = Setup( year=2016, photonSelection=True, checkOnly=True )
    default_photon_setup.estimators = EstimatorList( default_photon_setup )
    default_photon_setup.data       = default_photon_setup.processes["Data"]
#    default_photon_setup.processes  = default_setup.estimators.constructProcessDict( processDict=default_processes )
    default_photon_setup.processes["Data"] = default_photon_setup.data
    default_photon_setup.addon      = ""
    default_photon_setup.regions    = inclRegionsTTG if args.inclRegion else regionsTTG

# Define SR, CR, channels and regions
setups = []
for key, val in allRegions.items():
    if not key in args.useRegions: continue
    if key not in limitOrdering:
        limitOrdering += [key]

    if args.checkOnly:
        locals()["setup"+key] = None
        continue

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
if args.inclRegion:  regionNames.append("incl")
if args.misIDPOI:    regionNames.append("misIDPOI")
if args.wgPOI:       regionNames.append("wgPOI")
if args.dyPOI:       regionNames.append("dyPOI")
if args.wJetsPOI:    regionNames.append("wJetsPOI")
if args.ttPOI:       regionNames.append("ttPOI")
if args.useChannels: regionNames.append("_".join([ch for ch in args.useChannels if not "tight" in ch]))
if args.linTest != 1: regionNames.append(str(args.linTest).replace(".","_"))
if args.noMCStat:     regionNames.append("noMCStat")
if args.noFakeStat:   regionNames.append("noFakeStat")
if args.freezeR:   regionNames.append("freezeR")
if args.freezeSigUnc:   regionNames.append("freezeSigUnc")
if args.addPtBinnedUnc:   regionNames.append("addPtBinnedUnc")

if args.parameters:
    # load and define the EFT sample
    from TTGammaEFT.Samples.genTuples_TTGamma_EFT_postProcessed  import *
    eftSample = TTG_2WC_ref

    baseDir       = os.path.join( cache_directory, "analysis",  "COMBINED", "limits" )
    baseDir       = os.path.join( baseDir, "withbkg" if args.withbkg else "withoutbkg" )
    cacheFileName = os.path.join( baseDir, "calculatednll" )
    nllCache      = MergingDirDB( cacheFileName )

    baseDir       = os.path.join( cache_directory, "analysis", "eft" )
    cacheFileName = os.path.join( baseDir, eftSample.name )
    yieldCache    = MergingDirDB( cacheFileName )

    configlist = regionNames + EFTparams
    configlist.append("incl" if args.inclRegion else "diff")
    configlist.append("expected" if args.expected else "observed")

    sEFTConfig = "_".join(configlist)
    if not args.overwrite and nllCache.contains( sEFTConfig ) and abs(nllCache.get(sEFTConfig)["nll0"])>0.1: sys.exit(0)


years = [2016,2017,2018]

def wrapper():

    c = cardFileWriter.cardFileWriter()
    c.releaseLocation = combineReleaseLocation
    txtcards = {}
    shapecards = {}
    
    # get the seperated cards
    for year in years:
        baseDir       = os.path.join( cache_directory, "analysis",  str(year), "limits" )
        if args.parameters:
            baseDir       = os.path.join( baseDir, "withbkg" if args.withbkg else "withoutbkg" )
        limitDir      = os.path.join( baseDir, "cardFiles", args.label, "expected" if args.expected else "observed" )

        if args.parameters:
            cardFileNameTxt   = os.path.join( limitDir, "_".join( regionNames ), eft + ".txt" )
        else:
            cardFileNameTxt   = os.path.join( limitDir, "_".join( regionNames ) + ".txt" )

        cardFileNameShape = cardFileNameTxt.replace( ".txt", "_shapeCard.txt" )
    
        #print cardFileName
        if not os.path.isfile(cardFileNameTxt):
            #raise IOError("File %s doesn't exist!"%cardFileName)
            print "File %s doesn't exist!"%cardFileNameTxt
            return

        txtcards[year] = cardFileNameTxt
        shapecards[year] = cardFileNameShape
    
    baseDir  = baseDir.replace('2018','COMBINED')
    limitDir = limitDir.replace('2018','COMBINED')
    
    if not os.path.isdir(limitDir):
        os.makedirs(limitDir)

    txtcombinedCard   = c.combineCards( txtcards, txtFileOnly=bool(args.parameters) )
    shapecombinedCard = c.combineCards( shapecards, txtFileOnly=bool(args.parameters) )
    combinedCard = txtcombinedCard if args.useTxt else shapecombinedCard
    print combinedCard

    if args.parameters:
        cardFileNameTxt   = os.path.join( limitDir, "_".join( regionNames ), eft + ".txt" )
    else:
        cardFileNameTxt   = os.path.join( limitDir, "_".join( regionNames ) + ".txt" )
    cardFileNameShape = cardFileNameTxt.replace( ".txt", "_shape.root" )
    cardFileName      = cardFileNameTxt
    logger.info( "File %s found. Reusing."%cardFileName )
    cardFileNameShape = cardFileNameShape.replace('.root', 'Card.txt')
    cardFileName      = cardFileNameTxt if args.useTxt else cardFileNameShape
    
    if args.parameters:
        options = "--expectSignal=1 --freezeParameters r --setParameters r=1  --X-rtd REMOVE_CONSTANT_ZERO_POINT=1"
        nll          = c.calcNLL( fname=cardFileName, options=options )
        nllCache.add( sEFTConfig, nll, overwrite=True )
        print nll
        print sEFTConfig
    else:
        options = ""
        if args.freezeR:
            options = "--setParameters r=1 --freezeParameters r"
        res = c.calcLimit( cardFileName, options=options )

        # options for running the bkg only fit with r=1
        options += " --customStartingPoint --expectSignal=1"
        if args.freezeR:
            options += " --rMin 0.99 --rMax 1.01"
        options += " --rMin 0.5 --rMax 1.5 --cminDefaultMinimizerTolerance=0.1"
        c.calcNuisances( cardFileName, bonly=args.bkgOnly, options=options )
        if args.freezeSigUnc:
            Results = CombineResults( cardFile=cardFileNameTxt, plotDirectory="./", year="combined", bkgOnly=args.bkgOnly, isSearch=False )
            postFit = Results.getPulls( postFit=True )
            freezeParams = [ p for p in postFit.keys() if p.startswith("Signal_") ]
            pulls = [ p+"="+str(postFit[p].val) for p in freezeParams ]
            print pulls
            c.calcNuisances( cardFileName, bonly=args.bkgOnly, options=options+" --setParameters %s --freezeParameters %s"%(",".join(pulls),",".join(freezeParams)) )

    if args.plot and not args.parameters:
        path  = os.environ["CMSSW_BASE"]
        path +="/src/TTGammaEFT/plots/plotsLukas/regions"
        if args.expected:
            cdir  = "limits/cardFiles/defaultSetup/expected"
        else:
            cdir  = "limits/cardFiles/defaultSetup/observed"
        cfile = cardFileNameTxt.split("/")[-1].split(".")[0]

        cmd = "python %s/fitResults.py --carddir %s --cardfile %s --linTest %s --year %s --plotCovMatrix --plotRegionPlot %s --cores %i %s %s %s %s %s %s"%(path, cdir, cfile, str(args.linTest), "combined", "--bkgOnly" if args.bkgOnly else "", 1, "--expected" if args.expected else "", "--misIDPOI" if args.misIDPOI else "", "--wgPOI" if args.wgPOI else "", "--ttPOI" if args.ttPOI else "", "--dyPOI" if args.dyPOI else "", "--wJetsPOI" if args.wJetsPOI else "")
        logger.info("Executing plot command: %s"%cmd)
        os.system(cmd)
        cmd = "python %s/fitResults.py --carddir %s --cardfile %s --linTest %s --year %s --plotCorrelations --plotCovMatrix --plotRegionPlot --plotImpacts --postFit %s --cores %i %s %s %s %s %s %s"%(path, cdir, cfile, str(args.linTest), "combined", "--bkgOnly" if args.bkgOnly else "", 1, "--expected" if args.expected else "", "--misIDPOI" if args.misIDPOI else "", "--wgPOI" if args.wgPOI else "", "--ttPOI" if args.ttPOI else "", "--dyPOI" if args.dyPOI else "", "--wJetsPOI" if args.wJetsPOI else "")
#        cmd = "python %s/fitResults.py --carddir %s --cardfile %s --year %s --plotImpacts --postFit %s --cores %i %s %s %s %s %s"%(path, cdir, cfile, "combined", "--bkgOnly" if args.bkgOnly else "", 1, "--expected" if args.expected else "", "--misIDPOI" if args.misIDPOI else "", "--ttPOI" if args.ttPOI else "", "--dyPOI" if args.dyPOI else "", "--wJetsPOI" if args.wJetsPOI else "")
        logger.info("Executing plot command: %s"%cmd)
        os.system(cmd)

    ###################
    # extract the SFs #
    ###################
    if not args.parameters:
        default_QCD_unc = 0.5
        default_HadFakes_unc = 0.10
        default_ZG_unc    = 0.3
        default_Other_unc    = 0.30
        default_misID4p_unc    = 0.5
        default_ZG4p_unc    = 0.8
        default_DY4p_unc    = 0.8
        default_WG4p_unc    = 0.5
        default_DY_unc    = 0.1
        unc = {
                "QCD_normalization":default_QCD_unc,
                "ZGamma_normalization":default_ZG_unc,
                "Other_normalization":default_Other_unc,
                "fake_photon_normalization":default_HadFakes_unc,
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

        Results = CombineResults( cardFile=cardFileNameTxt, plotDirectory="./", year="combined", bkgOnly=args.bkgOnly, isSearch=False )
        postFit = Results.getPulls( postFit=True )

        if not os.path.isdir("logs"): os.mkdir("logs")
        write_time  = time.strftime("%Y %m %d %H:%M:%S", time.localtime())

        with open("logs/cardFiles.dat", "a") as f:
            f.write( cardFileNameTxt + "\n" )

        with open("logs/scaleFactors.dat", "a") as f:
            f.write( "\n\n" + cardFileNameTxt + "\n")

            sf = "{:20} {:4.2f} +- {:4.2f}".format( "POI", postFit["r"].val, postFit["r"].sigma )
            print sf
            f.write( str("combined") + ": " + write_time + ": " + "_".join( regionNames ) + ": " + sf + "\n" )
            for sf_name in unc.keys():
                if sf_name not in postFit.keys(): continue
                sf = "{:20} {:4.2f} +- {:4.2f}".format( sf_name, 1+(postFit[sf_name].val*unc[sf_name]), postFit[sf_name].sigma*unc[sf_name] )
                print sf
                f.write( str("combined") + ": " + write_time + ": " + "_".join( regionNames ) + ": " + sf + "\n" )
            for sf_name in rateParam:
                if sf_name not in postFit.keys(): continue
                sf = "{:20} {:4.2f} +- {:4.2f}".format( sf_name, postFit[sf_name].val, postFit[sf_name].sigma )
                print sf
                f.write( str("combined") + ": " + write_time + ": " + "_".join( regionNames ) + ": " + sf + "\n" )


######################################
# Load the signals and run the code! #
######################################

results = wrapper()


