#!/usr/bin/env python

""" 
Get cardfile result plots
"""

# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy, math

import numpy as np
# Helpers
from plotHelpers                      import *
import array
# Analysis
from Analysis.Tools.cardFileWriter.CombineResults    import CombineResults
import Analysis.Tools.syncer as syncer

# TTGammaEFT
from TTGammaEFT.Tools.user            import plot_directory, cache_directory
from TTGammaEFT.Analysis.SetupHelpers import *

# RootTools
from RootTools.core.standard          import *

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",             action="store",                default="INFO",  help="log level?", choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"])
argParser.add_argument("--preliminary",          action="store_true",                            help="Run expected?")
argParser.add_argument("--year",                 action="store",      type=str, default="2016",    help="Which year?")
argParser.add_argument("--plotYear",             action="store",                default=None,    help="Which year to plot from combined fits?")
argParser.add_argument("--carddir",              action='store',                default='limits/cardFiles/defaultSetup/observed',      help="which cardfile directory?")
argParser.add_argument("--cardfile",             action='store',                default='',      help="which cardfile?")
argParser.add_argument("--substituteCard",       action='store',                default=None,    help="which cardfile to substitute the plot with?")
argParser.add_argument("--plotNuisances",        action='store', nargs="*",     default=None,    help="plot specific nuisances?")
args = argParser.parse_args()

# logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile = None )
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

cardFile      = os.path.join( cache_directory, "analysis", str(args.year) if args.year != "combined" else "COMBINED", args.carddir, args.cardfile+".txt" )
if args.substituteCard:
    cardFile = cardFile.replace(".txt","/%s.txt"%args.substituteCard)

Results     = CombineResults( cardFile=cardFile, plotDirectory=".", year=args.year, bkgOnly=False, isSearch=False )



args.plotNuisances = [
#            "QCD_0b_nJet_dependence",
#            "QCD_0b_normalization",
            "QCD_1b_nJet_dependence",
            "QCD_1b_normalization",
            "QCD_normalization",
            "TT_normalization",
            "WGamma_nJet_dependence",
            "WGamma_normalization",
            "WGamma_pT_Bin1",
            "WGamma_pT_Bin2",
            "ZGamma_nJet_dependence",
            "ZGamma_normalization",
            "ZGamma_pT_Bin1",
            "ZGamma_pT_Bin2",
            "fake_photon_DD_normalization",
            "fake_photon_MC_normalization",
            "DY_extrapolation",
            "DY_nJet_dependence",
            "DY_normalization",
            "MisID_extrapolation_2016",
            "MisID_nJet_dependence_2016",
            "MisID_normalization_2016",
            "Other_normalization",
            "misID_pT_Bin1_2016",
            "misID_pT_Bin2_2016",
            "misID_pT_Bin3_2016",
            "misID_pT_Bin4_2016",
            "misID_pT_Bin5_2016",
            "misID_pT_Bin6_2016",
]


args.plotNuisances = [
#    "Int_Luminosity_2016",
    "prop_binBin0_bin8",
    "r",
]

for n in args.plotNuisances:
    print "Nuisance:", n

#    print "ZG",  Results.getCorrelationMatrixEntryByNuisances( n, "photon_ID" )

    Results.printCorrelations( n, nMax=15 )
    print
    print
