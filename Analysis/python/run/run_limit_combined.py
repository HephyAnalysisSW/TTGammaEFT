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

from TTGammaEFT.Tools.user               import cache_directory, combineReleaseLocation, cardfileLocation
from Analysis.Tools.MergingDirDB         import MergingDirDB
from Analysis.Tools.u_float              import u_float
from Analysis.Tools.cardFileWriter       import cardFileWriter
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
argParser.add_argument( "--misIDPOI",           action="store_true",                                                        help="Change POI to misID SF")
argParser.add_argument( "--dyPOI",              action="store_true",                                                        help="Change POI to misID SF")
argParser.add_argument( "--ttPOI",              action="store_true",                                                        help="Change POI to misID SF")
argParser.add_argument( "--wJetsPOI",           action="store_true",                                                        help="Change POI to misID SF")
argParser.add_argument( "--checkOnly",          action="store_true",                                                        help="Check the SF only")
argParser.add_argument( "--bkgOnly",            action="store_true",                                                        help="background only")
argParser.add_argument( "--plot",               action="store_true",                                                        help="run plots?")
argParser.add_argument( "--useTxt",             action="store_true",                                                        help="Use txt based cardFiles instead of root/shape based ones?" )
argParser.add_argument( "--skipFitDiagnostics", action="store_true",                                                        help="Don't do the fitDiagnostics (this is necessary for pre/postfit plots" )
argParser.add_argument( "--significanceScan",   action="store_true",                                                        help="Calculate significance instead?")
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

default_QCD_unc = 0.5
default_ZG_unc = 0.3

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
if args.dyPOI:       regionNames.append("dyPOI")
if args.wJetsPOI:    regionNames.append("wJetsPOI")
if args.ttPOI:       regionNames.append("ttPOI")
if args.useChannels: regionNames.append("_".join([ch for ch in args.useChannels if not "tight" in ch]))

years = [2016,2017,2018]

def wrapper():

    c = cardFileWriter.cardFileWriter()
    c.releaseLocation = combineReleaseLocation
    txtcards = {}
    shapecards = {}
    
    # get the seperated cards
    for year in years:
        baseDir       = os.path.join( cache_directory, "analysis",  str(year), "limits" )
        limitDir      = os.path.join( baseDir, "cardFiles", args.label, "expected" if args.expected else "observed" )
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

    txtcombinedCard   = c.combineCards( txtcards )
    shapecombinedCard = c.combineCards( shapecards )
    combinedCard = txtcombinedCard if args.useTxt else shapecombinedCard
    print combinedCard

    cardFileNameTxt   = os.path.join( limitDir, "_".join( regionNames ) + ".txt" )
    cardFileNameShape = cardFileNameTxt.replace( ".txt", "_shape.root" )
    cardFileName      = cardFileNameTxt
    logger.info( "File %s found. Reusing."%cardFileName )
    cardFileNameShape = cardFileNameShape.replace('.root', 'Card.txt')
    cardFileName      = cardFileNameTxt if args.useTxt else cardFileNameShape
    
    sConfig = "_".join(regionNames)
    res = c.calcLimit( cardFileName )
    c.calcNuisances( cardFileName, bonly=args.bkgOnly )

    if args.plot:
        path  = os.environ["CMSSW_BASE"]
        path +="/src/TTGammaEFT/plots/plotsLukas/regions"
        if args.expected:
            cdir  = "limits/cardFiles/defaultSetup/expected"
        else:
            cdir  = "limits/cardFiles/defaultSetup/observed"
        cfile = cardFileNameTxt.split("/")[-1].split(".")[0]

        cmd = "python %s/fitResults.py --carddir %s --cardfile %s --year %s --plotCovMatrix --plotRegionPlot %s --cores %i %s %s %s %s %s"%(path, cdir, cfile, "combined", "--bkgOnly" if args.bkgOnly else "", 1, "--expected" if args.expected else "", "--misIDPOI" if args.misIDPOI else "", "--ttPOI" if args.ttPOI else "", "--dyPOI" if args.dyPOI else "", "--wJetsPOI" if args.wJetsPOI else "")
        logger.info("Executing plot command: %s"%cmd)
        os.system(cmd)
        cmd = "python %s/fitResults.py --carddir %s --cardfile %s --year %s --plotCorrelations --plotCovMatrix --plotRegionPlot --plotImpacts --postFit %s --cores %i %s %s %s %s %s"%(path, cdir, cfile, "combined", "--bkgOnly" if args.bkgOnly else "", 1, "--expected" if args.expected else "", "--misIDPOI" if args.misIDPOI else "", "--ttPOI" if args.ttPOI else "", "--dyPOI" if args.dyPOI else "", "--wJetsPOI" if args.wJetsPOI else "")
#        cmd = "python %s/fitResults.py --carddir %s --cardfile %s --year %s --plotImpacts --postFit %s --cores %i %s %s %s %s %s"%(path, cdir, cfile, "combined", "--bkgOnly" if args.bkgOnly else "", 1, "--expected" if args.expected else "", "--misIDPOI" if args.misIDPOI else "", "--ttPOI" if args.ttPOI else "", "--dyPOI" if args.dyPOI else "", "--wJetsPOI" if args.wJetsPOI else "")
        logger.info("Executing plot command: %s"%cmd)
        os.system(cmd)

    ###################
    # extract the SFs #
    ###################
    if not args.useTxt and not args.skipFitDiagnostics:
        # Would be a bit more complicated with the classical txt files, so only automatically extract the SF when using shape based datacards
        
        combineWorkspace = cardFileNameShape.replace( "shapeCard.txt","shapeCard_FD.root" )
        logger.info( "Extracting fit results from %s"%combineWorkspace )

        postFitResults = getFitResults( combineWorkspace )
        postFit        = postFitResults["tree_fit_b" if args.bkgOnly else "tree_fit_sb"]
        print postFit
        preFit         = postFitResults["tree_prefit"]
        printSF        = ["QCD_1p", "ZG_norm"]
        unc            = {"QCD_1p":default_QCD_unc, "ZG_norm":default_ZG_unc}

        if not os.path.isdir("logs"): os.mkdir("logs")
        write_time  = time.strftime("%Y %m %d %H:%M:%S", time.localtime())

        with open("logs/cardFiles.dat", "a") as f:
            f.write( cardFileNameTxt + "\n" )

        with open("logs/scaleFactors.dat", "a") as f:
            f.write( "\n\n" + cardFileNameTxt + ", Fit Status: %i\n"%postFit["fit_status"] )
            f.write( "\n\n POI: %f\n"%postFit["r"] )
            print
            print "## Scale Factors for backgrounds, fit status: %i ##"%postFit["fit_status"]
            print "POI: %f"%postFit["r"]

            for sf_name in printSF:
                if sf_name not in postFit.keys(): continue
                sf = "{:20}{:4.2f}".format( sf_name, 1+(postFit[sf_name]*unc[sf_name]) )
                print sf
                f.write( "combined" + ": " + write_time + ": " + "_".join( regionNames ) + ": " + sf + "\n" )

######################################
# Load the signals and run the code! #
######################################

results = wrapper()


