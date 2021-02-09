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
nuisances = [ p for p in Results.getPulls().keys() if p !="r" and not "prop" in p ]
#plotBins = [10,11,12,13,14,15,16,17,18,19,20,21]
plotBins = [34,35,36,37,38,39,40,41,42,43,44,45]

# get region histograms
if args.year == "combined":
        hists = Results.getRegionHistos( postFit=args.postFit, nuisances=nuisances, plotBins=plotBins )
        channels = ["dc_2016","dc_2017","dc_2018"]
#        hists_tmp = Results.getRegionHistos( postFit=args.postFit, nuisances=nuisances, plotBins=plotBins )
#        for i, dir in enumerate(Results.channels):
#            print i, dir
#            if i == 0:
#                hists = {key:hist.Clone(str(i)+dir+key) for key, hist in hists_tmp[dir].iteritems() if key not in nuisances}
#                for n in nuisances:
#                        hists.update( { n:{"up":hists_tmp[dir][n]["up"].Clone(str(i)+dir+n+"up"), "down":copy.deepcopy(hists_tmp[dir][n]["down"].Clone(str(i)+dir+n+"down"))} } )
#            else:
#               for key, hist in hists_tmp[dir].iteritems():
#                    if key in nuisances:
#                        hists[key]["up"].Add(hist["up"].Clone(str(i)+dir+key+"up"))
#                        hists[key]["down"].Add(hist["down"].Clone(str(i)+dir+key+"down"))
#                    else:
#                        hists[key].Add(hist.Clone(str(i)+dir+key))
else:
        hists = Results.getRegionHistos( postFit=args.postFit, nuisances=nuisances, plotBins=plotBins )
        channels = ["Bin0"]

for i_c, c in enumerate(channels):
        if i_c == 0:
            hists["total"] = hists[c]["total"].Clone()
            hists["signal"] = hists[c]["signal"].Clone()
            hists["total_background"] = hists[c]["total_background"].Clone()
        else:
            hists["total"].Add( hists[c]["total"] )
            hists["signal"].Add( hists[c]["signal"] )
            hists["total_background"].Add( hists[c]["total_background"] )

for c in channels:
    for n in nuisances:
        hists[c][n]["sys"] = hists[c]["total"].Clone()
        for i in range(hists[c]["total"].GetNbinsX()):
            hists[c][n]["sys"].SetBinError(i+1, hists[c][n]["up"].GetBinContent(i+1)-hists[c]["total"].GetBinContent(i+1) )

for i_c, c in enumerate(channels):
    for n in nuisances:
        if i_c == 0:
            hists[n] = {}
            hists[n]["sys"] = hists[c][n]["sys"].Clone()
        else:
            hists[n]["sys"].Add( hists[c][n]["sys"] )
        if "JEC" in n:
            if not "JEC" in hists.keys():
                hists["JEC"] = {}
                hists["JEC"]["sys"] = hists[c][n]["sys"].Clone()
            else:
                hists["JEC"]["sys"].Add(hists[c][n]["sys"] )
        if "JER" in n:
            if not "JER" in hists.keys():
                hists["JER"] = {}
                hists["JER"]["sys"] = hists[c][n]["sys"].Clone()
            else:
                hists["JER"]["sys"].Add(hists[c][n]["sys"] )
        if "QCD_" in n:
            if not "QCD" in hists.keys():
                hists["QCD"] = {}
                hists["QCD"]["sys"] = hists[c][n]["sys"].Clone()
            else:
                hists["QCD"]["sys"].Add(hists[c][n]["sys"] )
        if "Luminosity" in n:
            if not "Luminosity" in hists.keys():
                hists["Luminosity"] = {}
                hists["Luminosity"]["sys"] = hists[c][n]["sys"].Clone()
            else:
                hists["Luminosity"]["sys"].Add(hists[c][n]["sys"] )
        if "MisID" in n:
            if not "MisID" in hists.keys():
                hists["MisID"] = {}
                hists["MisID"]["sys"] = hists[c][n]["sys"].Clone()
            else:
                hists["MisID"]["sys"].Add(hists[c][n]["sys"] )
        if "WGamma" in n:
            if not "WGamma" in hists.keys():
                hists["WGamma"] = {}
                hists["WGamma"]["sys"] = hists[c][n]["sys"].Clone()
            else:
                hists["WGamma"]["sys"].Add(hists[c][n]["sys"] )
        if "ZGamma" in n:
            if not "ZGamma" in hists.keys():
                hists["ZGamma"] = {}
                hists["ZGamma"]["sys"] = hists[c][n]["sys"].Clone()
            else:
                hists["ZGamma"]["sys"].Add(hists[c][n]["sys"] )
        if "muon_ID" in n:
            if not "muon_ID" in hists.keys():
                hists["muon_ID"] = {}
                hists["muon_ID"]["sys"] = hists[c][n]["sys"].Clone()
            else:
                hists["muon_ID"]["sys"].Add(hists[c][n]["sys"] )
        if "Trigger" in n:
            if not "Trigger" in hists.keys():
                hists["Trigger"] = {}
                hists["Trigger"]["sys"] = hists[c][n]["sys"].Clone()
            else:
                hists["Trigger"]["sys"].Add(hists[c][n]["sys"] )
        if "pixelSeed" in n:
            if not "pixelSeed" in hists.keys():
                hists["pixelSeed"] = {}
                hists["pixelSeed"]["sys"] = hists[c][n]["sys"].Clone()
            else:
                hists["pixelSeed"]["sys"].Add(hists[c][n]["sys"] )
        if "flavor" in n:
            if not "flavor" in hists.keys():
                hists["flavor"] = {}
                hists["flavor"]["sys"] = hists[c][n]["sys"].Clone()
            else:
                hists["flavor"]["sys"].Add(hists[c][n]["sys"] )

        if "fake_photon" in n:
            if not "fake_photon" in hists.keys():
                hists["fake_photon"] = {}
                hists["fake_photon"]["sys"] = hists[c][n]["sys"].Clone()
            else:
                hists["fake_photon"]["sys"].Add(hists[c][n]["sys"] )

        if "erdOn" in n or "QCDbased" in n or  "GluonMove" in n:
            if not "color" in hists.keys():
                hists["color"] = {}
                hists["color"]["sys"] = hists[c][n]["sys"].Clone()
            else:
                hists["color"]["sys"].Add(hists[c][n]["sys"] )


nuisances += ["JEC","JER","Luminosity","MisID","WGamma","ZGamma","muon_ID","Trigger","pixelSeed","flavor","fake_photon","color","QCD"]

for n in nuisances:
    for i in range( hists[n]["sys"].GetNbinsX() ):
        y = hists["total"].GetBinContent(i+1)
        hists[n]["sys"].SetBinContent(i+1, y + hists[n]["sys"].GetBinError(i+1) )

for n in nuisances:
        hists[n]["sys"].Add( hists["total"], -1 )
        t = hists[n]["sys"].Clone()
        s = hists[n]["sys"].Clone()
        b = hists[n]["sys"].Clone()
        t.Divide( hists["total"] )
        s.Divide( hists["signal"] )
        b.Divide( hists["total_background"] )
        print n, (t.GetMinimum(), t.GetMaximum()), (s.GetMinimum(), s.GetMaximum()), (b.GetMinimum(), b.GetMaximum())
        tl = [t.GetBinContent(i+1) for i in range(t.GetNbinsX())]
        sl = [s.GetBinContent(i+1) for i in range(s.GetNbinsX())]
        bl = [b.GetBinContent(i+1) for i in range(b.GetNbinsX())]
        tl = filter( lambda x: x>0, tl )
        sl = filter( lambda x: x>0, sl )
        bl = filter( lambda x: x>0, bl )
        print tl, min(tl + [999])
        print sl, min(sl + [999])
        print bl, min(bl + [999])
        print

#print hists.keys()
sys.exit()

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
#        if int(bin.replace("Bin","")) < 10: continue # only SR
        if int(bin.replace("Bin","")) < 34: continue # only SR
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

b = "dc_2016" if args.year == "combined" else "Bin0"
#for n, nVal in resultprefit[b]["Bin10"].iteritems():
for n, nVal in resultprefit[b]["Bin34"].iteritems():
    pre = [ resultprefit[year][bin][n][0] for bin in resultprefit[b].keys() for year in resultprefit.keys()]
    post = [ resultpostfit[year][bin][n][0] for bin in resultpostfit[b].keys() for year in resultpostfit.keys()]
    print n, "\t", "%f"%(min(pre)-1), "%f"%(max(pre)-1),"\t" , "%f"%(min(post)-1), "%f"%(max(post)-1) #, pre
