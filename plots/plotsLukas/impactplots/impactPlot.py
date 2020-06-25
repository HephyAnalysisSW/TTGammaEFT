#!/usr/bin/env python

import os
import ROOT
import shutil
import uuid

from Analysis.Tools.CombineResults import CombineResults
from TTGammaEFT.Tools.user         import analysis_results, plot_directory, combineReleaseLocation, cache_directory

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",       action="store", default="INFO",          nargs="?", choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"],    help="Log level for logging")
argParser.add_argument("--label",          action="store", default="defaultSetup",  type=str,                               help="Label of results directory" )
argParser.add_argument("--keepDir",        action="store_true",                                                             help="Keep the directory in the combine release after study is done?")
argParser.add_argument("--expected",       action="store_true",                                                             help="Use expected results?")
argParser.add_argument("--carddir",        action="store", default="limits/cardFiles/defaultSetup/observed",              nargs="?",                              help="which cardfile directory?")
argParser.add_argument("--cardfile",       action="store", default="",              nargs="?",                              help="which cardfile?")
argParser.add_argument("--cores",          action="store", default=1,               type=int,                               help="Run on n cores in parallel")
argParser.add_argument("--year",           action="store", default=2016,            type=int,                               help="Which year?")
argParser.add_argument("--bkgOnly",        action="store_true",                                                             help="Allow no signal?")
args = argParser.parse_args()


# Logging
import Analysis.Tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

dirName  = "_".join( [ item for item in args.cardfile.split("_") if item not in ["addDYSF", "addMisIDSF", "misIDPOI", "incl"] ] )
add  = [ item for item in args.cardfile.split("_") if item in ["addDYSF", "addMisIDSF", "misIDPOI", "incl"] ]
add.sort()
fit  = "_".join( ["postFit"] + add )

plotDirectory = os.path.join(plot_directory, "fit", str(args.year), fit, dirName)
cardFile      = os.path.join( cache_directory, "analysis", str(args.year), args.carddir, args.cardfile+".txt" )
Results       = CombineResults( cardFile=cardFile, plotDirectory=plotDirectory, year=args.year, bkgOnly=False, isSearch=False )
logger.info("Plotting from cardfile %s"%cardFile)

Results.getImpactPlot( expected=args.expected, printPNG=True, cores=args.cores )
