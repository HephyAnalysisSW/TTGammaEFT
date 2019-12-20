#!/usr/bin/env python
""" Analysis script for standard plots
"""

# Standard imports
import ROOT, os, imp, sys, copy
#ROOT.gROOT.SetBatch(True)
import itertools
from math                                import isnan, ceil, pi

# RootTools
from RootTools.core.standard             import *

from TTGammaEFT.Analysis.regions         import regionsTTG, noPhotonRegionTTG, inclRegionsTTG
from TTGammaEFT.Analysis.Setup           import Setup
from TTGammaEFT.Analysis.EstimatorList   import EstimatorList
from TTGammaEFT.Analysis.MCBasedEstimate import MCBasedEstimate
from TTGammaEFT.Analysis.DataObservation import DataObservation
from TTGammaEFT.Analysis.SetupHelpers    import *

from Analysis.Tools.u_float              import u_float

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

defaultPhotonRegions = ['SR3', 'SR4p','VG3', 'VG4p', 'misDY3', 'misDY4p','misTT2']
defaultRegions = ['TT3', 'TT4p', 'WJets3', 'WJets4p']
# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                  help="Log level for logging")
argParser.add_argument("--regions",            action="store",      default=defaultRegions,   nargs="*",                               help="For CR region?")
#argParser.add_argument("--removeNegative",     action="store_true",                                                                    help="Set negative values to 0?", )
argParser.add_argument("--noPhoton",           action="store_true",                                                                    help="no photon regions")
argParser.add_argument("--year",               action="store",      default=None,   type=int,  choices=[2016,2017,2018],               help="which year?")
#argParser.add_argument("--mode",               action="store",      default="all",  type=str,                                          help="which lepton selection?")
#argParser.add_argument("--label",              action="store",      default="Region",  type=str,                                          help="which region label?")
args = argParser.parse_args()

args.label = "Transfer Factors QCD"
#args.label.replace("geq", "$\\geq$")

allMode = "all"

if not args.noPhoton and args.regions==defaultRegions:
    args.regions=defaultPhotonRegions

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74

sieieSel  = ["all" ]
chgSel    = ["all" ]

CR_para = allRegions[args.regions[0]]["parameters"]
hadFakeSel  = False #"NoChgIsoNoSieiePhoton" in args.selection
photonSelection = not args.noPhoton #not allRegions[args.regions[0]]["noPhotonCR"]
allPhotonRegions = inclRegionsTTG + regionsTTG if photonSelection else noPhotonRegionTTG
channels = allRegions[args.regions[0]]["channels"]

if hadFakeSel:
    ptDict = {str(inclRegionsTTG[0]):"all", str(regionsTTG[0]):"lowhadPT", str(regionsTTG[1]):"medhadPT", str(regionsTTG[2]):"highhadPT"}
    sieieSel  = ["lowSieie", "highSieie"]
    chgSel    = ["lowChgIso", "highChgIso"]

elif not photonSelection:
    ptDict = {str(noPhotonRegionTTG[0]):"all"}
else:
    ptDict = {str(inclRegionsTTG[0]):"all", str(regionsTTG[0]):"lowPT", str(regionsTTG[1]):"medPT", str(regionsTTG[2]):"highPT"}

if photonSelection:
    setup      = Setup(year=args.year, photonSelection=photonSelection, checkOnly=True)
    estimators = EstimatorList( setup, processes=["QCD-DD"] )
    estimate   = getattr(estimators, "QCD-DD")
    estimate.isData = False

    setups = {}
    setups[args.year] = {}
    for r in args.regions:
        setups[args.year][r] = setup.sysClone(parameters=allRegions[r]["parameters"])
        setups[args.year][r].verbose=True

else:
    setups = {}
    for y in [2016,2017,2018]:
        setup      = Setup(year=y, photonSelection=False, checkOnly=True)
        estimators = EstimatorList( setup, processes=["QCD-DD"] )
        estimate   = getattr(estimators, "QCD-DD")
        estimate.isData = False

        setups[y] = {}
        for r in args.regions:
            setups[y][r] = setup.sysClone(parameters=allRegions[r]["parameters"])
            setups[y][r].verbose=True

def wrapper(arg, y):
        r,channel,est,estimate = arg
        setup = setups[y][est]
        logger.debug("Running transfer factor for region %s, channel %s in setup %s for QCD-DD"%(r,channel, est))
        estimate.initCache(setup.defaultCacheDir())
        res = estimate.cachedTransferFactor(r, channel, setup, checkOnly=True)
        return (arg, res )

#if photonSelection:
#    regions = [(None, pt, sieie, chgIso) for pt in ptDict.values() for chgIso in chgSel for sieie in sieieSel]
#else:

ratio = {}
yields = {}
print photonSelection
if photonSelection:
  regions = [(m, pt, sieie, chgIso) for m in channels for pt in ptDict.values() for chgIso in chgSel for sieie in sieieSel]
  for i_r, r in enumerate(args.regions):
    ratio[r] = {}
    yields[r] = {}
    for i_sieie, sieie in enumerate(sieieSel):
        ratio[r][sieie] = {}
        yields[r][sieie] = {}
        for i_chgIso, chgIso in enumerate(chgSel):
            ratio[r][sieie][chgIso] = {}
            yields[r][sieie][chgIso] = {}
            for i_region, region in enumerate(allPhotonRegions):
                ratio[r][sieie][chgIso][ptDict[str(region)]] = {}
                yields[r][sieie][chgIso][ptDict[str(region)]] = {}
                for i_mode, mode in enumerate(channels):
                    ratio[r][sieie][chgIso][ptDict[str(region)]][mode] = 0.
                    yields[r][sieie][chgIso][ptDict[str(region)]][mode] = u_float(0,0)

  for i_r, r in enumerate(args.regions):
    for i_sieie, sieie in enumerate(sieieSel):
        for i_chgIso, chgIso in enumerate(chgSel):
            for i_region, region in enumerate(allPhotonRegions):
                for i_mode, mode in enumerate(channels):
                    y     = wrapper( (region, mode, r, estimate), args.year )[1]
                    yields[r][sieie][chgIso][ptDict[str(region)]][mode] = y
                    ratio[r][sieie][chgIso][ptDict[str(region)]][mode] = y.sigma*100./y.val if y.val else 0.
                    print r, ptDict[str(region)], mode, y, y.sigma*100./y.val if y.val else 0.

else:
  regions = [(m, y) for y in [2016,2017,2018] for m in channels]
  region = noPhotonRegionTTG[0]
  for i_r, r in enumerate(args.regions):
    ratio[r] = {}
    yields[r] = {}
    for i_y, y in enumerate([2016,2017,2018]):
        ratio[r][y] = {}
        yields[r][y] = {}
        for i_mode, mode in enumerate(channels):
            ratio[r][y][mode] = 0.
            yields[r][y][mode] = u_float(0,0)

  for i_r, r in enumerate(args.regions):
    for i_y, year in enumerate([2016,2017,2018]):
        for i_mode, mode in enumerate(channels):
            y     = wrapper( (region, mode, r, estimate), year )[1]
            yields[r][year][mode] = y
            ratio[r][year][mode] = y.sigma*100./y.val if y.val else 0.
            print r, year, mode, y, y.sigma*100./y.val if y.val else 0.

def printHadFakeYieldTable( m ):

    with open("logs/qcdTF_%s-%s.log"%(args.year,m), "w") as f:
        f.write("\\begin{frame}\n")
        f.write("\\frametitle{Yields - %s}\n\n"%args.label)

        f.write("\\begin{table}\n")
        f.write("\\centering\n")

        for lowPT, highPT in [ (20,120), (120,220), (220,-1) ]:
            f.write("\\resizebox{0.8\\textwidth}{!}{\n")
            f.write("\\begin{tabular}{c||c||c|c|c||c||c|c|c||c||c|c|c||c||c|c|c}\n")

            if lowPT == 20:
                f.write("\\hline\n")
                f.write("\\hline\n")
                f.write("\\multicolumn{17}{c}{QCD Transfer Factor, %s}\\\\ \n"%m.replace("mu", "$\\mu$") )
                f.write("\\hline\n")
                f.write("\\multicolumn{17}{c}{%i: $\\mathcal{L}=%s$ fb$^{-1}$}\\\\ \n"%(args.year, "{:.2f}".format(lumi_scale)))
                f.write("\\hline\n")
                f.write("\\hline\n")
                f.write("\\multicolumn{17}{c}{}\\\\ \n")

            f.write("\\hline\n")
            f.write("\\hline\n")
            if highPT == -1:
                f.write("\\multicolumn{17}{c}{\\pT($\\gamma$) $>$ %i GeV}\\\\ \n"%(lowPT))
            else:
                f.write("\\multicolumn{17}{c}{%i $\\leq$ \\pT($\\gamma$) $<$ %i GeV}\\\\ \n"%(lowPT, highPT))
            f.write("\\hline\n")
            f.write("Region  & \\multicolumn{4}{c||}{low $\\sigma_{i\\eta i\\eta}$, low chg Iso (SR)} & \\multicolumn{4}{c||}{high $\\sigma_{i\\eta i\\eta}$, low chg Iso  (NN2)}   & \\multicolumn{4}{c||}{low $\\sigma_{i\\eta i\\eta}$, high chg Iso (NN1)}   & \\multicolumn{4}{c}{high $\\sigma_{i\\eta i\\eta}$, high chg Iso  (CR)} \\\\ \n")
            f.write("\\hline\n")
            f.write("        & \\textbf{events} & $\gamma$ & misID e & had $\gamma$ / fake & \\textbf{events} & $\gamma$ & misID e & had $\gamma$ / fake & \\textbf{events} & $\gamma$ & misID e & had $\gamma$ / fake & \\textbf{events} & $\gamma$ & misID e & had $\gamma$ / fake \\\\ \n")
            f.write("\\hline\n")
            f.write("\\hline\n")
            for r in args.regions:
                f.write("%s & \\textbf{%s} & %s & %s & \\textbf{%s} & %s & %s & \\textbf{%s} & %s & %s & \\textbf{%s} & %s & %s & %s \\\\ \n" %tuple( [r] + [ str(int(round(yields[r][sieie][chgIso][pt][m]))) if yields[r][sieie][chgIso][pt][m]>=0 else "" for lep, pt, sieie, chgIso in regions]) )
                f.write("\\hline\n")
            f.write("\\hline\n")
    
            if highPT == -1:
                f.write("\\multicolumn{17}{c}{}\\\\ \n")
                f.write("\\multicolumn{1}{c}{} & \\multicolumn{4}{c}{$\gamma$ = genuine photons} & \\multicolumn{4}{c}{had $\gamma$ = hadronic photons} & \\multicolumn{4}{c}{misID e = misID electrons} & \\multicolumn{4}{c}{fake = hadronic fakes} \\\\ \n")


            f.write("\\end{tabular}\n")
            f.write("}\n\n") #resizebox

        f.write("\\end{table}\n\n")
        f.write("\\end{frame}\n\n\n\n")




def printYieldTable( m ):

    with open("logs/qcdTF_%s-%s.log"%(args.year,m), "w") as f:
        print "logs/qcdTF_%s-%s.log"%(args.year,m)
    
        if m in ["e", "all"]:
            f.write("\\begin{frame}\n")
            f.write("\\frametitle{QCD Transfer Factor}\n\n")

        f.write("\\begin{table}\n")
        f.write("\\centering\n")

        f.write("\\resizebox{0.9\\textwidth}{!}{\n")
        f.write("\\begin{tabular}{c||c|c|c|c}\n")
#        f.write("\\begin{tabular}{c||c||c|c|c|c||c||c|c|c|c||c||c|c|c|c}\n")

        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("\\multicolumn{5}{c}{\\textbf{QCD Transfer Factor, %s}}\\\\ \n"%m.replace("mu", "$\\mu$") )
        f.write("\\hline\n")
        f.write("\\multicolumn{5}{c}{\\textbf{%i:} $\\mathcal{L}=%s$ fb$^{-1}$}\\\\ \n"%(args.year, "{:.2f}".format(lumi_scale)))
        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("\\multicolumn{5}{c}{}\\\\ \n")

        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("\\textbf{Region}  & \\textbf{inclusive} & \\textbf{%i $\\leq$ \\pT($\\gamma$) $<$ %i GeV} & \\textbf{%i $\\leq$ \\pT($\\gamma$) $<$ %i GeV} & \\textbf{\\pT($\\gamma$) $>$ %i GeV}\\\\ \n"%(20,120,120,220,220))
        f.write("\\hline\n")
        f.write("\\hline\n")
        for r in args.regions:
            if "misIDDY" in r and m=="mu": continue
            f.write("\\textbf{%s} & %s & %s & %s & %s \\\\ \n" %tuple( [r] + [ "%s $\\pm$ %s (%s\\%%)"%('{:.4f}'.format(yields[r][sieie][chgIso][pt][lep].val), '{:.4f}'.format(yields[r][sieie][chgIso][pt][lep].sigma), '{:.1f}'.format(ratio[r][sieie][chgIso][pt][lep]) ) for lep, pt, sieie, chgIso in regions if lep == m]) )
            f.write("\\hline\n")
        f.write("\\hline\n")
    
        f.write("\\end{tabular}\n")
        f.write("}\n\n") #resizebox

        f.write("\\end{table}\n\n")
        if m in ["mu", "all"]:
            f.write("\\end{frame}\n")
        f.write("\n\n\n")



def printNoPhotonYieldTable( ):

    with open("logs/qcdTF.log", "w") as f:
 
        f.write("\\begin{frame}\n")
        f.write("\\frametitle{QCD Transfer Factor}\n\n")

        f.write("\\begin{table}\n")
        f.write("\\centering\n")

        f.write("\\resizebox{0.9\\textwidth}{!}{\n")
#        f.write("\\begin{tabular}{c||c||c|c|c|c||c||c|c|c|c||c||c|c|c|c||c||c|c|c|c}\n")
        f.write("\\begin{tabular}{c||c|c||c|c||c|c}\n")

        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("\\multicolumn{7}{c}{\\textbf{QCD Transfer Factor}}\\\\ \n" )
        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("\\textbf{Region}  & \\multicolumn{2}{c||}{\\textbf{2016}} & \\multicolumn{2}{c||}{\\textbf{2017}} & \\multicolumn{2}{c}{\\textbf{2018}}\\\\ \n")
        f.write("\\hline\n")
        f.write("        & \\textbf{e} & $\\mathbf{\\mu}$                  & \\textbf{e} & $\\mathbf{\\mu}$                  & \\textbf{e} & $\\mathbf{\\mu}$\\\\ \n")
        f.write("\\hline\n")
        f.write("\\hline\n")
        for r in args.regions:
            f.write("\\textbf{%s} & %s & %s & %s & %s & %s & %s\\\\ \n" %tuple( [r] + [ "%s $\\pm$ %s (%s\\%%)"%('{:.4f}'.format(yields[r][y][lep].val), '{:.4f}'.format(yields[r][y][lep].sigma), '{:.1f}'.format(ratio[r][y][lep]) ) for lep, y in regions]) )
            f.write("\\hline\n")
        f.write("\\hline\n")
    
#        f.write("\\multicolumn{7}{c}{}\\\\ \n")

        f.write("\\end{tabular}\n")
        f.write("}\n\n") #resizebox

        f.write("\\end{table}\n\n")
        f.write("\\end{frame}\n")
        f.write("\n\n\n")



if hadFakeSel:
    for m in channels:
        printHadFakeYieldTable( m )
elif not photonSelection:
    printNoPhotonYieldTable()
else:
    for m in channels:
        printYieldTable( m )
