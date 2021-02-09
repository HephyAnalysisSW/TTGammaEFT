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
resPostFit    = Results.getUncertaintiesFromTxtCard( postFit=True )
resPreFit     = Results.getUncertaintiesFromTxtCard( postFit=False )

estPreFit = Results.getEstimates( bin=None, estimate=None, postFit=False )
estPostFit = Results.getEstimates( bin=None, estimate=None, postFit=True )

totalYieldSFPostFit = {}
totalYieldSFPreFit = {}
totalSignalYieldSFPostFit = {}
totalSignalYieldSFPreFit = {}
totalBkgYieldSFPostFit = {}
totalBkgYieldSFPreFit = {}
resultpostfit = {}
resultprefit = {}

modelUnc = [
            "Tune",
            "QCDbased",
            "Scale",
            "GluonMove",
            "PDF",
            "Parton_Showering",
            "erdOn",
]

bkgUnc = [
            "WGamma_nJet_dependence",
            "WGamma_normalization",
            "WGamma_pT_Bin1",
            "WGamma_pT_Bin2",
            "ZGamma_nJet_dependence",
            "ZGamma_normalization",
            "ZGamma_pT_Bin1",
            "ZGamma_pT_Bin2",
            "DY_normalization",
            "MisID_extrapolation_2016",
            "MisID_nJet_dependence_2016",
            "MisID_normalization_2016",
            "misID_pT_Bin1_2016",
            "misID_pT_Bin2_2016",
            "misID_pT_Bin3_2016",
            "misID_pT_Bin4_2016",
            "misID_pT_Bin5_2016",
            "misID_pT_Bin6_2016",

            "MisID_extrapolation_2017",
            "MisID_nJet_dependence_2017",
            "MisID_normalization_2017",
            "misID_pT_Bin1_2017",
            "misID_pT_Bin2_2017",
            "misID_pT_Bin3_2017",
            "misID_pT_Bin4_2017",
            "misID_pT_Bin5_2017",
            "misID_pT_Bin6_2017",

            "MisID_extrapolation_2018",
            "MisID_nJet_dependence_2018",
            "MisID_normalization_2018",
            "misID_pT_Bin1_2018",
            "misID_pT_Bin2_2018",
            "misID_pT_Bin3_2018",
            "misID_pT_Bin4_2018",
            "misID_pT_Bin5_2018",
            "misID_pT_Bin6_2018",

            "QCD_1b_nJet_dependence",
            "QCD_1b_normalization",
            "QCD_normalization",
            "fake_photon_DD_normalization",
            "Other_normalization",
            "TT_normalization",
]

#for year, yVal in resPostFit.iteritems():
#    for bin, bVal in yVal.iteritems():
#        if int(bin.replace("Bin","")) < 10: continue # only SR
##        if int(bin.replace("Bin","")) % 2: continue # only e
#        tmp = []
#        for process, pVal in bVal.iteritems():
##            if estPreFit[year][bin][process] < 0.01: continue
#            if not resPreFit[year][bin][process]["PU"]: continue
#            tmp.append(resPreFit[year][bin][process]["PU"])
#        print len(tmp)
#        tmp = sorted(tmp)
##        tmp = tmp[1:-1]
#        print year, bin, min(tmp), max(tmp), tmp
#sys.exit()

for year, yVal in resPostFit.iteritems():
    totalYieldSFPostFit[year] = {}
    totalYieldSFPreFit[year] = {}
    totalSignalYieldSFPostFit[year] = {}
    totalSignalYieldSFPreFit[year] = {}
    totalBkgYieldSFPostFit[year] = {}
    totalBkgYieldSFPreFit[year] = {}
    resultpostfit[year] = {}
    resultprefit[year] = {}
    for bin, bVal in yVal.iteritems():
        print bin
        if int(bin.replace("Bin","")) < 10: continue # only SR
        totalYieldSFPostFit[year][bin] = 0
        totalYieldSFPreFit[year][bin]  = 0
        totalSignalYieldSFPostFit[year][bin] = 0
        totalSignalYieldSFPreFit[year][bin]  = 0
        totalBkgYieldSFPostFit[year][bin] = 0
        totalBkgYieldSFPreFit[year][bin]  = 0
        tmp_resultpostfit = {}
        tmp_resultprefit = {}
        if not bin in resultpostfit.keys():
            resultpostfit[year][bin] = {}
            resultprefit[year][bin] = {}
        for process, pVal in bVal.iteritems():
#            if "QCD" in process: continue
            yieldSFPostFit = estPostFit[year][bin][process] # / estPostFit[year][bin]["signal"]
            yieldSFPreFit  = estPreFit[year][bin][process] # / estPreFit[year][bin]["signal"]
            totalYieldSFPostFit[year][bin] +=  yieldSFPostFit.val
            totalYieldSFPreFit[year][bin] += yieldSFPreFit.val
            if process == "signal":
                totalSignalYieldSFPostFit[year][bin] +=  yieldSFPostFit.val
                totalSignalYieldSFPreFit[year][bin] += yieldSFPreFit.val
            else:
                totalBkgYieldSFPostFit[year][bin] +=  yieldSFPostFit.val
                totalBkgYieldSFPreFit[year][bin] += yieldSFPreFit.val

#            if estPreFit[year][bin][process].val <= 0.1: continue
#            if estPreFit[year][bin][process].val <= 0.1: continue
            for nuisance, nVal in pVal.iteritems():
#                if nuisance == "DY_normalization": print nVal
#                if nVal == 0: continue
#                n = "JEC" if nuisance.startswith("JEC") else nuisance
##                n = "PU" if nuisance.startswith("PU") else n
#                n = "fake_photon" if nuisance.startswith("fake_photon") else n
#                n = "muon_ID" if nuisance.startswith("muon_ID") else n
#                n = "QCD_normalization" if nuisance.startswith("QCD_") else n
#                n = n.replace("_2016","").replace("_2017","").replace("_2018","") if "_201" in nuisance else n
                n = nuisance
#                pfscaled = resPreFit[year][bin][process][nuisance]*yieldSFPreFit.val
#                if pfscaled*100 < 0.005: continue
                if n not in resultpostfit[year][bin].keys():
                    resultpostfit[year][bin][n] = []
                    resultprefit[year][bin][n] = []
                if n not in tmp_resultpostfit.keys():
                    tmp_resultpostfit[n] = []
                    tmp_resultprefit[n] = []
#                if resPreFit[year][bin][process][nuisance] == 0: continue
                tmp_resultpostfit[n].append( (1+nVal)*yieldSFPostFit.val )
                tmp_resultprefit[n].append( (1+resPreFit[year][bin][process][nuisance])*yieldSFPreFit.val )

        print totalYieldSFPostFit[year][bin], totalSignalYieldSFPostFit[year][bin], totalBkgYieldSFPostFit[year][bin]
        for n in tmp_resultpostfit.keys():
            if n in bkgUnc:
                resultpostfit[year][bin][n].append( sum(tmp_resultpostfit[n]) / totalBkgYieldSFPostFit[year][bin] )
                resultprefit[year][bin][n].append( sum(tmp_resultprefit[n]) / totalBkgYieldSFPreFit[year][bin] )
            elif n in modelUnc:
                resultpostfit[year][bin][n].append( sum(tmp_resultpostfit[n]) / totalSignalYieldSFPostFit[year][bin] )
                resultprefit[year][bin][n].append( sum(tmp_resultprefit[n]) / totalSignalYieldSFPreFit[year][bin] )
            else:
                resultpostfit[year][bin][n].append( sum(tmp_resultpostfit[n]) / totalYieldSFPostFit[year][bin] )
                resultprefit[year][bin][n].append( sum(tmp_resultprefit[n]) / totalYieldSFPreFit[year][bin] )

#for n, nVal in resultprefit["dc_2016"]["Bin10"].iteritems():
for n, nVal in resultprefit["Bin0"]["Bin10"].iteritems():
    pre = [ resultprefit[year][bin][n][0] for bin in resultprefit["Bin0"].keys() for year in resultprefit.keys()]
    post = [ resultpostfit[year][bin][n][0] for bin in resultpostfit["Bin0"].keys() for year in resultpostfit.keys()]
#    pre = [ resultprefit[year][bin][n][0] for bin in resultprefit["dc_2016"].keys() for year in resultprefit.keys()]
#    post = [ resultpostfit[year][bin][n][0] for bin in resultpostfit["dc_2016"].keys() for year in resultpostfit.keys()]
    print n, "\t", "%f"%(min(pre)-1), "%f"%(max(pre)-1),"\t" , "%f"%(min(post)-1), "%f"%(max(post)-1) #, pre
