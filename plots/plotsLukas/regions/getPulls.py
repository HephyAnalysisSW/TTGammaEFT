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

# TTGammaEFT
from TTGammaEFT.Tools.user            import plot_directory, cache_directory
from TTGammaEFT.Analysis.SetupHelpers import *

# RootTools
from RootTools.core.standard          import *

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--small",                action="store_true",                            help="small?")
argParser.add_argument("--logLevel",             action="store",                default="INFO",  help="log level?", choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"])
argParser.add_argument("--misIDPOI",             action="store_true",                            help="Use misID as POI")
argParser.add_argument("--ttPOI",             action="store_true",                            help="Use tt as POI")
argParser.add_argument("--wJetsPOI",             action="store_true",                            help="Use w+jets as POI")
argParser.add_argument("--wgPOI",             action="store_true",                            help="Use wgamma as POI")
argParser.add_argument("--dyPOI",             action="store_true",                            help="Use dy as POI")
argParser.add_argument("--postFit",              action="store_true",                            help="Apply pulls?")
argParser.add_argument("--year",                 action="store",      type=str, default="2016",    help="Which year?")
argParser.add_argument("--carddir",              action='store',                default='limits/cardFiles/defaultSetup/observed',      help="which cardfile directory?")
argParser.add_argument("--cardfile",             action='store',                default='',      help="which cardfile?")
args = argParser.parse_args()

# logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile = None )
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

if args.year != "combined": args.year = int(args.year)
# make sure the list is always in the same order

if args.misIDPOI: default_processes = processesMisIDPOI
if args.ttPOI: default_processes = processesTTPOI
if args.wJetsPOI: default_processes = processesWJetsPOI
if args.dyPOI: default_processes = processesDYPOI
if args.wgPOI: default_processes = processesWGPOI

lumi_scale = 35.92 + 41.53 + 59.74

dirName  = "_".join( [ item for item in args.cardfile.split("_") if not (item.startswith("add") or item == "incl") ] )
add      = [ item for item in args.cardfile.split("_") if (item.startswith("add") or item == "incl")  ]
add.sort()
fit      = "_".join( ["postFit" if args.postFit else "preFit"] + add )

plotDirectory = os.path.join(plot_directory, "fit", str(args.year), fit, dirName)
cardFile      = os.path.join( cache_directory, "analysis", str(args.year) if args.year != "combined" else "COMBINED", args.carddir, args.cardfile+".txt" )
logger.info("Plotting from cardfile %s"%cardFile)

# replace the combineResults object by the substituted card object
Results = CombineResults( cardFile=cardFile, plotDirectory=plotDirectory, year=args.year, isSearch=False )
#Results.htmlNuisanceReport()
#Results.tableNuisanceReport()

#sys.exit()
#for key, val in Results.getPulls( postFit=args.postFit ).iteritems():
#    if "prop" in key: continue
#    print key, str(val)
resultpostfit = {}
resultprefit  = {}
resPostFit    = Results.getUncertaintiesFromTxtCard( postFit=True )
resPreFit     = Results.getUncertaintiesFromTxtCard( postFit=False )

estPreFit = Results.getEstimates( bin=None, estimate=None, postFit=False )
estPostFit = Results.getEstimates( bin=None, estimate=None, postFit=True )

for year, yVal in resPostFit.iteritems():
    for bin, bVal in yVal.iteritems():
        if int(bin.replace("Bin","")) < 10: continue
        for process, pVal in bVal.iteritems():
            yieldSFPostFit = estPostFit[year][bin][process] / estPostFit[year][bin]["signal"]
            yieldSFPreFit  = estPreFit[year][bin][process] / estPreFit[year][bin]["signal"]
#            if estPreFit[year][bin][process].val <= 0.1: continue
            for nuisance, nVal in pVal.iteritems():
                if nVal == 0: continue
                n = "JEC" if nuisance.startswith("JEC") else nuisance
                n = "PU" if nuisance.startswith("PU") else n
                n = "fake_photon" if nuisance.startswith("fake_photon") else n
                n = "muon_ID" if nuisance.startswith("muon_ID") else n
                n = "QCD_normalization" if nuisance.startswith("QCD_") else n
                n = n.replace("_2016","").replace("_2017","").replace("_2018","") if "_201" in nuisance else n
                if n not in resultpostfit.keys():
                    resultpostfit[n] = []
                    resultprefit[n] = []
#                pfscaled = resPreFit[year][bin][process][nuisance]*yieldSFPreFit.val
#                if pfscaled*100 < 0.005: continue
                resultpostfit[n].append( nVal*yieldSFPostFit.val )
                resultprefit[n].append( resPreFit[year][bin][process][nuisance]*yieldSFPreFit.val )

for n, nVal in resultprefit.iteritems():
    print n, "\t", "%.2f"%(min(nVal)*100), "%.2f"%(max(nVal)*100),"\t" , "%.2f"%(min(resultpostfit[n])*100), "%.2f"%(max(resultpostfit[n])*100)
