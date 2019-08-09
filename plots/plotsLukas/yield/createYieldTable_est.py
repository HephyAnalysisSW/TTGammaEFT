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

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                  help="Log level for logging")
argParser.add_argument("--controlRegion",      action="store",      default=None,   type=str,                                          help="For CR region?")
argParser.add_argument("--removeNegative",     action="store_true",                                                                    help="Set negative values to 0?", )
argParser.add_argument("--noData",             action="store_true", default=False,                                                     help="also plot data?")
argParser.add_argument("--year",               action="store",      default=None,   type=int,  choices=[2016,2017,2018],               help="which year?")
#argParser.add_argument("--mode",               action="store",      default="all",  type=str,                                          help="which lepton selection?")
argParser.add_argument("--label",              action="store",      default="Region",  type=str,                                          help="which region label?")
args = argParser.parse_args()

args.label = args.label.replace("geq", "$\\geq$")

if args.controlRegion.startswith("DY"):
    allMode = "SFtight"
else:
    allMode = "all"

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.86
elif args.year == 2018: lumi_scale = 58.83

addMisIDSF = False
addDYSF    = False
cr = args.controlRegion
if args.controlRegion.count("addMisIDSF"):
    addMisIDSF = True
    args.controlRegion = "-".join( [ item for item in args.controlRegion.split("-") if item != "addMisIDSF" ] )
if args.controlRegion.count("addDYSF"):
    addDYSF = True
    args.controlRegion = "-".join( [ item for item in args.controlRegion.split("-") if item != "addDYSF" ] )

CR_para = allRegions[args.controlRegion]["parameters"]
hadFakeSel  = False #"NoChgIsoNoSieiePhoton" in args.selection
photonSelection = not ("nPhoton" in CR_para and CR_para["nPhoton"][1] == 0) and not hadFakeSel
#allRegions = inclRegionsTTG + regionsTTG if photonSelection else noPhotonRegionTTG
allRegions = inclRegionsTTG + regionsTTG if photonSelection else noPhotonRegionTTG

catSel    = ["all", "photoncat0", "photoncat1", "photoncat2", "photoncat3"]
sieieSel  = ["all" ]
chgSel    = ["all" ]
noCat_sel = "all"

if hadFakeSel:
    ptDict = {str(inclRegionsTTG[0]):"all", str(regionsTTG[0]):"lowhadPT", str(regionsTTG[1]):"medhadPT", str(regionsTTG[2]):"highhadPT"}
    catSel = ["all", "photonhadcat0", "photonhadcat1", "photonhadcat2", "photonhadcat3"]
    sieieSel  = ["lowSieie", "highSieie"]
    chgSel    = ["lowChgIso", "highChgIso"]

elif not photonSelection:
    ptDict = {str(noPhotonRegionTTG[0]):"all"}
    catSel = ["all"]

else:
    ptDict = {str(inclRegionsTTG[0]):"all", str(regionsTTG[0]):"lowPT", str(regionsTTG[1]):"medPT", str(regionsTTG[2]):"highPT"}

setup          = Setup(year=args.year, photonSelection=photonSelection )#, checkOnly=True)
estimators     = EstimatorList(setup)
allEstimators  = estimators.constructEstimatorList( default_sampleList )
mc  = [e.name for e in allEstimators]
if not args.noData:
    allEstimators += [DataObservation(name="Data", sample=setup.samples["Data"], cacheDir=setup.defaultCacheDir())]

if args.controlRegion:
    setup = setup.sysClone(parameters=CR_para)

setup.verbose=True

def wrapper(arg):
        r,channel,setup,estimate = arg
        estimate.initCache(setup.defaultCacheDir())
        res = estimate.cachedEstimate(r, channel, setup, save=True, overwrite=False, checkOnly=True)
        if args.removeNegative and res < 0: res = u_float(0,0)
        return (estimate.uniqueKey(r, channel, setup), res )

if args.controlRegion and args.controlRegion.startswith('DY'):
#    channels = dilepChannels + ["SFtight"] if not mode else [mode]
    channels = dilepChannels
else:
#    channels = lepChannels + ["all"] if not mode else [mode]
    channels = lepChannels


#regions = [(mode, pt, sieie, chgIso, cat) for mode in channels for pt in ptDict.values() for chgIso in chgSel for sieie in sieieSel for cat in catSel]
if photonSelection:
    regions = [(None, pt, sieie, chgIso, cat) for pt in ptDict.values() for chgIso in chgSel for sieie in sieieSel for cat in catSel]
else:
    regions = [(m, pt, sieie, chgIso, cat) for m in [allMode] + channels for pt in ptDict.values() for chgIso in chgSel for sieie in sieieSel for cat in catSel]


yields = {}
for est in [e.name for e in allEstimators] + ["MC"]:
    yields[est] = {}
    for i_sieie, sieie in enumerate(sieieSel):
        yields[est][sieie] = {}
        for i_chgIso, chgIso in enumerate(chgSel):
            yields[est][sieie][chgIso] = {}
            for i_region, region in enumerate(allRegions):
                yields[est][sieie][chgIso][ptDict[str(region)]] = {}
                for i_cat, cat in enumerate(catSel):
                    yields[est][sieie][chgIso][ptDict[str(region)]][cat] = {}
                    for i_mode, mode in enumerate(channels + [allMode]):
                        yields[est][sieie][chgIso][ptDict[str(region)]][cat][mode] = 0

for estimator in allEstimators:
    est = estimator.name
    for i_sieie, sieie in enumerate(sieieSel):
        for i_chgIso, chgIso in enumerate(chgSel):
            for i_region, region in enumerate(allRegions):
                for i_cat, cat in enumerate(catSel):
                    for i_mode, mode in enumerate(channels):

                        if cat == "all":
                            try:
                                yields[est][sieie][chgIso][ptDict[str(region)]][cat][mode] = int(round(wrapper( (region, mode, setup, estimator) )[1].val))
#                                print yields[est][sieie][chgIso][ptDict[str(region)]][cat][mode]
                                if addDYSF and "DY" in est:
                                    yields[est][sieie][chgIso][ptDict[str(region)]][cat][mode] *= default_DYSF
                            except:
                                yields[est][sieie][chgIso][ptDict[str(region)]][cat][mode] = 0#int(round(wrapper( (region, mode, setup, estimator) )[1].val))
                                pass
                        else:
                            yields[est][sieie][chgIso][ptDict[str(region)]][cat][mode] = 0#int(round(wrapper( (region, mode, setup, estimator) )[1].val))

                        yields[est][sieie][chgIso][ptDict[str(region)]][cat][allMode] += yields[est][sieie][chgIso][ptDict[str(region)]][cat][mode]
                        if est != "Data":
                            yields["MC"][sieie][chgIso][ptDict[str(region)]][cat][allMode] += yields[est][sieie][chgIso][ptDict[str(region)]][cat][mode]
                            yields["MC"][sieie][chgIso][ptDict[str(region)]][cat][mode] += yields[est][sieie][chgIso][ptDict[str(region)]][cat][mode]


def printHadFakeYieldTable( m ):

    with open("logs/%i_%s-%s.log"%(args.year,cr,m), "w") as f:
        f.write("\\begin{frame}\n")
        f.write("\\frametitle{Yields - %s}\n\n"%args.label)

        f.write("\\begin{table}\n")
        f.write("\\centering\n")

        for lowPT, highPT in [ (20,120), (120,220), (220,-1) ]:
            f.write("\\resizebox{0.8\\textwidth}{!}{\n")
            f.write("\\begin{tabular}{c||c||c|c|c|c||c||c|c|c|c||c||c|c|c|c||c||c|c|c|c}\n")

            if lowPT == 20:
                f.write("\\hline\n")
                f.write("\\hline\n")
                f.write("\\multicolumn{21}{c}{%s}\\\\ \n"%( ", ".join( [cr] + [m] ) ) )
                f.write("\\hline\n")
                f.write("\\multicolumn{21}{c}{%i: $\\mathcal{L}=%s$ fb$^{-1}$}\\\\ \n"%(args.year, "{:.2f}".format(lumi_scale)))
                f.write("\\hline\n")
                f.write("\\hline\n")
                f.write("\\multicolumn{21}{c}{}\\\\ \n")

            f.write("\\hline\n")
            f.write("\\hline\n")
            if highPT == -1:
                f.write("\\multicolumn{21}{c}{\\pT($\\gamma$) $>$ %i GeV}\\\\ \n"%(lowPT))
            else:
                f.write("\\multicolumn{21}{c}{%i $\\leq$ \\pT($\\gamma$) $<$ %i GeV}\\\\ \n"%(lowPT, highPT))
            f.write("\\hline\n")
            f.write("Sample  & \\multicolumn{5}{c||}{low $\\sigma_{i\\eta i\\eta}$, low chg Iso (SR)} & \\multicolumn{5}{c||}{high $\\sigma_{i\\eta i\\eta}$, low chg Iso  (NN2)}   & \\multicolumn{5}{c||}{low $\\sigma_{i\\eta i\\eta}$, high chg Iso (NN1)}   & \\multicolumn{5}{c}{high $\\sigma_{i\\eta i\\eta}$, high chg Iso  (CR)} \\\\ \n")
            f.write("\\hline\n")
            f.write("        & \\textbf{events} & $\gamma$ & had $\gamma$ & misID e & fake & \\textbf{events} & $\gamma$ & had $\gamma$ & misID e & fake & \\textbf{events} & $\gamma$ & had $\gamma$ & misID e & fake & \\textbf{events} & $\gamma$ & had $\gamma$ & misID e & fake \\\\ \n")
            f.write("\\hline\n")
            f.write("\\hline\n")
            for s in mc:
                f.write("%s & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i \\\\ \n" %tuple( [s.replace("_","\_")] + [ int(yields[s][sieie][chgIso][pt][cat][m]) for lep, pt, sieie, chgIso, cat in regions]) )
                f.write("\\hline\n")
            f.write("\\hline\n")
            f.write("MC total & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i \\\\ \n" %tuple( [int(yields["MC"][sieie][chgIso][pt][cat][m]) for lep, pt, sieie, chgIso, cat in regions] ))
            f.write("\\hline\n")
            if not args.noData:
                f.write("data total & \\textbf{%i} & \\multicolumn{4}{c||}{} & \\textbf{%i} & \\multicolumn{4}{c||}{} & \\textbf{%i} & \\multicolumn{4}{c||}{} & \\textbf{%i} & \\multicolumn{4}{c}{} \\\\ \n" %tuple( [int(yields["Data"][sieie][chgIso][pt][cat][m]) for lep, pt, sieie, chgIso, cat in regions if cat == "all"] ))
                f.write("\\hline\n")
                f.write("data/MC    & \\textbf{%.2f} & \\multicolumn{4}{c||}{} & \\textbf{%.2f} & \\multicolumn{4}{c||}{} & \\textbf{%.2f} & \\multicolumn{4}{c||}{} & \\textbf{%.2f} & \\multicolumn{4}{c}{} \\\\ \n" %tuple( [float(yields["Data"][sieie][chgIso][pt][cat][m])/float(yields["MC"][sieie][chgIso][pt][cat][m]) if float(yields["MC"][sieie][chgIso][pt][cat][m]) > 0 else 1. for lep, pt, sieie, chgIso, cat in regions if cat == "all"] ))
                f.write("\\hline\n")
            f.write("\\hline\n")
    
            if highPT == -1:
                f.write("\\multicolumn{21}{c}{}\\\\ \n")
                f.write("\\multicolumn{1}{c}{} & \\multicolumn{5}{c}{$\gamma$ = genuine photons} & \\multicolumn{5}{c}{had $\gamma$ = hadronic photons} & \\multicolumn{5}{c}{misID e = misID electrons} & \\multicolumn{5}{c}{fake = hadronic fakes} \\\\ \n")


            f.write("\\end{tabular}\n")
            f.write("}\n\n") #resizebox

        f.write("\\end{table}\n\n")
        f.write("\\end{frame}\n\n\n\n")




def printYieldTable( m ):

    with open("logs/%i_%s-%s.log"%(args.year,cr,m), "w") as f:
    
        if m in ["e", "all"]:
            f.write("\\begin{frame}\n")
            f.write("\\frametitle{Yields - %s}\n\n"%args.label)

        f.write("\\begin{table}\n")
        f.write("\\centering\n")

        f.write("\\resizebox{0.9\\textwidth}{!}{\n")
        f.write("\\begin{tabular}{c||c||c|c|c|c||c||c|c|c|c||c||c|c|c|c||c||c|c|c|c}\n")
#        f.write("\\begin{tabular}{c||c||c|c|c|c||c||c|c|c|c||c||c|c|c|c}\n")

        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("\\multicolumn{21}{c}{%s}\\\\ \n"%( ", ".join( [cr] + [m] ) ) )
        f.write("\\hline\n")
        f.write("\\multicolumn{21}{c}{%i: $\\mathcal{L}=%s$ fb$^{-1}$}\\\\ \n"%(args.year, "{:.2f}".format(lumi_scale)))
        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("\\multicolumn{21}{c}{}\\\\ \n")

        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("Sample  & \\multicolumn{5}{c||}{inclusive} & \\multicolumn{5}{c||}{%i $\\leq$ \\pT($\\gamma$) $<$ %i GeV} & \\multicolumn{5}{c||}{%i $\\leq$ \\pT($\\gamma$) $<$ %i GeV} & \\multicolumn{5}{c}{\\pT($\\gamma$) $>$ %i GeV}\\\\ \n"%(20,120,120,220,220))
        f.write("\\hline\n")
        f.write("        & \\textbf{events} & $\gamma$ & had $\gamma$ & misID e & fake & \\textbf{events} & $\gamma$ & had $\gamma$ & misID e & fake & \\textbf{events} & $\gamma$ & had $\gamma$ & misID e & fake & \\textbf{events} & $\gamma$ & had $\gamma$ & misID e & fake \\\\ \n")
        f.write("\\hline\n")
        f.write("\\hline\n")
        for s in mc:
            f.write("%s & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i \\\\ \n" %tuple( [s.replace("_","\_")] + [ int(yields[s][sieie][chgIso][pt][cat][m]) for lep, pt, sieie, chgIso, cat in regions ]) )
            f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("MC total & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i \\\\ \n" %tuple( [int(yields["MC"][sieie][chgIso][pt][cat][m]) for lep, pt, sieie, chgIso, cat in regions] ))
        f.write("\\hline\n")
        if not args.noData:
            f.write("data total & \\textbf{%i} & \\multicolumn{4}{c||}{} & \\textbf{%i} & \\multicolumn{4}{c||}{} & \\textbf{%i} & \\multicolumn{4}{c||}{} & \\textbf{%i} & \\multicolumn{4}{c}{} \\\\ \n" %tuple( [ int(yields["Data"][sieie][chgIso][pt][cat][m]) for lep, pt, sieie, chgIso, cat in regions if cat=="all"] ))
            f.write("\\hline\n")
            f.write("data/MC    & \\textbf{%.2f} & \\multicolumn{4}{c||}{} & \\textbf{%.2f} & \\multicolumn{4}{c||}{} & \\textbf{%.2f} & \\multicolumn{4}{c||}{} & \\textbf{%.2f} & \\multicolumn{4}{c}{} \\\\ \n" %tuple( [float(yields["Data"][sieie][chgIso][pt][cat][m])/float(yields["MC"][sieie][chgIso][pt][cat][m]) if float(yields["MC"][sieie][chgIso][pt][cat][m]) > 0 else 1. for lep, pt, sieie, chgIso, cat in regions if cat == "all"] ))
            f.write("\\hline\n")
        f.write("\\hline\n")
    
        f.write("\\multicolumn{21}{c}{}\\\\ \n")
        f.write("\\multicolumn{1}{c}{} & \\multicolumn{5}{c}{$\gamma$ = genuine photons} & \\multicolumn{5}{c}{had $\gamma$ = hadronic photons} & \\multicolumn{5}{c}{misID e = misID electrons} & \\multicolumn{5}{c}{fake = hadronic fakes} \\\\ \n")


        f.write("\\end{tabular}\n")
        f.write("}\n\n") #resizebox

        f.write("\\end{table}\n\n")
        if m in ["mu", "all"]:
            f.write("\\end{frame}\n")
        f.write("\n\n\n")



def printNoPhotonYieldTable( ):

    with open("logs/%i_%s.log"%(args.year,cr), "w") as f:
 
        f.write("\\begin{frame}\n")
        f.write("\\frametitle{Yields - %s}\n\n"%args.label)

        f.write("\\begin{table}\n")
        f.write("\\centering\n")

        f.write("\\resizebox{0.9\\textwidth}{!}{\n")
#        f.write("\\begin{tabular}{c||c||c|c|c|c||c||c|c|c|c||c||c|c|c|c||c||c|c|c|c}\n")
        f.write("\\begin{tabular}{c||c||c|c|c|c||c||c|c|c|c||c||c|c|c|c}\n")

        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("\\multicolumn{16}{c}{%s}\\\\ \n"%( ", ".join( [cr] ) ) )
        f.write("\\hline\n")
        f.write("\\multicolumn{16}{c}{%i: $\\mathcal{L}=%s$ fb$^{-1}$}\\\\ \n"%(args.year, "{:.2f}".format(lumi_scale)))
        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("\\multicolumn{16}{c}{}\\\\ \n")

        f.write("\\hline\n")
        f.write("\\hline\n")
        if args.controlRegion.startswith("DY"):
            f.write("Sample  & \\multicolumn{5}{c||}{ SF (ee/$\\mu\\mu$) channel } & \\multicolumn{5}{c||}{ee channel} & \\multicolumn{5}{c}{$\\mu\\mu$ channel}\\\\ \n")
        else:
            f.write("Sample  & \\multicolumn{5}{c||}{ e/$\\mu$ channel } & \\multicolumn{5}{c||}{e channel} & \\multicolumn{5}{c}{$\\mu$ channel}\\\\ \n")
        f.write("\\hline\n")
        f.write("        & \\textbf{events} & $\gamma$ & had $\gamma$ & misID e & fake & \\textbf{events} & $\gamma$ & had $\gamma$ & misID e & fake & \\textbf{events} & $\gamma$ & had $\gamma$ & misID e & fake \\\\ \n")
        f.write("\\hline\n")
        f.write("\\hline\n")
        for s in mc:
            f.write("%s & \\textbf{%i} & 0 & 0 & 0 & 0 & \\textbf{%i} & 0 & 0 & 0 & 0 & \\textbf{%i} & 0 & 0 & 0 & 0 \\\\ \n" %tuple( [s.replace("_","\_")] + [ int(yields[s][sieie][chgIso][pt][cat][lep]) for lep, pt, sieie, chgIso, cat in regions ]) )
            f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("MC total & \\textbf{%i} & 0 & 0 & 0 & 0 & \\textbf{%i} & 0 & 0 & 0 & 0 & \\textbf{%i} & 0 & 0 & 0 & 0 \\\\ \n" %tuple( [int(yields["MC"][sieie][chgIso][pt][cat][lep]) for lep, pt, sieie, chgIso, cat in regions] ))
        f.write("\\hline\n")
        if not args.noData:
            f.write("data total & \\textbf{%i} & \\multicolumn{4}{c||}{} & \\textbf{%i} & \\multicolumn{4}{c||}{} & \\textbf{%i} & \\multicolumn{4}{c}{} \\\\ \n" %tuple( [ int(yields["Data"][sieie][chgIso][pt][cat][lep]) for lep, pt, sieie, chgIso, cat in regions if cat=="all"] ))
            f.write("\\hline\n")
            f.write("data/MC    & \\textbf{%.2f} & \\multicolumn{4}{c||}{} & \\textbf{%.2f} & \\multicolumn{4}{c||}{} & \\textbf{%.2f} & \\multicolumn{4}{c}{} \\\\ \n" %tuple( [float(yields["Data"][sieie][chgIso][pt][cat][lep])/float(yields["MC"][sieie][chgIso][pt][cat][lep]) if float(yields["MC"][sieie][chgIso][pt][cat][lep]) > 0 else 1. for lep, pt, sieie, chgIso, cat in regions if cat == "all"] ))
            f.write("\\hline\n")
        f.write("\\hline\n")
    
#        f.write("\\multicolumn{16}{c}{}\\\\ \n")

        f.write("\\end{tabular}\n")
        f.write("}\n\n") #resizebox

        f.write("\\end{table}\n\n")
        f.write("\\end{frame}\n")
        f.write("\n\n\n")



if hadFakeSel:
    for m in [allMode] + channels:
        printHadFakeYieldTable( m )
elif not photonSelection:
    printNoPhotonYieldTable()
else:
    for m in [allMode] + channels:
        printYieldTable( m )
