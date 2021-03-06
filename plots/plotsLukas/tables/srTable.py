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
argParser.add_argument("--year",               action="store",      default="2016",   type=str,  choices=["2016","2017","2018","RunII"],               help="which year?")
argParser.add_argument("--label",              action="store",      default="Region",  type=str, nargs="*",                            help="which region label?")
argParser.add_argument("--cores",            action="store",  default=1,      type=int,                        help="run multicore?")
args = argParser.parse_args()

args.label = " ".join(args.label)
args.label = args.label.replace("geq", "$\\geq$")

if args.year != "RunII": args.year = int(args.year)

if not os.path.isdir("logs"): os.mkdir("logs")

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
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74

if "2" in args.controlRegion and not "2p" in args.controlRegion:
    DYSF_val    = DY2SF_val
    misIDSF_val = misID2SF_val
elif "3" in args.controlRegion and not "3p" in args.controlRegion:
    DYSF_val    = DY3SF_val
    misIDSF_val = misID3SF_val
elif "4" in args.controlRegion and not "4p" in args.controlRegion:
    DYSF_val    = DY4SF_val
    misIDSF_val = misID4SF_val
elif "5" in args.controlRegion:
    DYSF_val    = DY5SF_val
    misIDSF_val = misID5SF_val
elif "2p" in args.controlRegion:
    DYSF_val    = DY2pSF_val
    misIDSF_val = misID2pSF_val
elif "3p" in args.controlRegion:
    DYSF_val    = DY3pSF_val
    misIDSF_val = misID3pSF_val
elif "4p" in args.controlRegion:
    DYSF_val    = DY4pSF_val
    misIDSF_val = misID4pSF_val

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
photonSelection = not allRegions[args.controlRegion]["noPhotonCR"]
allPhotonRegions = allRegions[args.controlRegion]["inclRegion"] + allRegions[args.controlRegion]["regions"] if photonSelection else allRegions[args.controlRegion]["inclRegion"]

noCat_sel = "all"
allCat    = ["all","gen","misID","had"]

blind = False
if photonSelection:
    if "SR" in args.controlRegion:
        inclRegionsTTG = inclRegionsTTGloose
        regionsTTG = regionsTTGloose
        blind = args.year != 2016
    ptDict = {str(inclRegionsTTG[0]):"all", str(regionsTTG[0]):"lowPT", str(regionsTTG[1]):"medPT", str(regionsTTG[2]):"highPT"}
    catSel = ["all","gen","misID","had"]
else:
    ptDict = {str(noPhotonRegionTTG[0]):"all"}
    catSel = ["all"]

setup          = Setup(year=args.year, photonSelection=False, checkOnly=True)
estimators     = EstimatorList(setup)
allEstimators  = estimators.constructEstimatorList( allProcesses )
mc  = list(set([e.name.split("_")[0] for e in allEstimators]))

if not args.noData:
    allEstimators += [DataObservation(name="Data", process=setup.processes["Data"], cacheDir=setup.defaultCacheDir())]

if args.controlRegion:
    setup = setup.sysClone(parameters=CR_para)

def wrapper(arg):
        r,channel,setup,estimate,cat,est = arg
        estimate.initCache(setup.defaultCacheDir())
        if estimate.name == "Data" and blind:
            res = u_float(0,0)
        else:
            res = estimate.cachedEstimate(r, channel, setup, overwrite=False, checkOnly=True)
        if args.removeNegative and res < 0: res = u_float(0,0)
        return est, str(r), cat, channel, res.tuple()

if args.controlRegion and args.controlRegion.startswith('DY'):
    channels = dilepChannels
else:
    channels = lepChannels


regions = [(m, pt, cat) for m in [allMode] + channels for pt in ptDict.values() for cat in catSel]

# create dictionary structure
yields = {}
signal = {}
for estName in [e.name for e in allEstimators] + ["MC","MC_gen","MC_misID","MC_had"]:
    est = estName.split("_")[0]
    yields[est] = {}
    for i_region, region in enumerate(allPhotonRegions):
        yields[est][ptDict[str(region)]] = {}
        signal[ptDict[str(region)]] = {}
        for i_cat, cat in enumerate(allCat):
            yields[est][ptDict[str(region)]][cat] = {}
            for i_mode, mode in enumerate(channels + [allMode]):
                 yields[est][ptDict[str(region)]][cat][mode] = u_float(0)
                 signal[ptDict[str(region)]][mode] = u_float(0)

jobs = []
for estimator in allEstimators:
    cat = estimator.name.split("_")[-1] if estimator.name.split("_")[-1] in ["gen","misID","had"] else "all"
    if cat == "had": continue
    est = estimator.name.split("_")[0]
    for i_region, region in enumerate(allPhotonRegions):
        for i_mode, mode in enumerate(channels):
            jobs.append( (region, mode, setup, estimator, cat, est) )

if args.cores > 1:
    from multiprocessing import Pool
    pool = Pool( processes=args.cores )
    results = pool.map( wrapper, jobs )
    pool.close()
else:
    results    = map(wrapper, jobs)

for est, region, cat, mode, y in results:
    if est == "TTG" and cat == "gen":
        signal[ptDict[str(region)]][mode] = u_float(y)
        signal[ptDict[str(region)]][allMode] += u_float(y)

    if y < 0: continue
    yields[est][ptDict[str(region)]][cat][mode] = u_float(y)

    if addDYSF and "DY" in est:
        yields[est][ptDict[str(region)]][cat][mode] *= DYSF_val[args.year].val
    if addMisIDSF and cat == "misID":
        yields[est][ptDict[str(region)]][cat][mode] *= misIDSF_val[args.year].val

    # fill all and MC entries for each cat
    if yields[est][ptDict[str(region)]][cat][mode] > 0:
        yields[est][ptDict[str(region)]][cat][allMode] += yields[est][ptDict[str(region)]][cat][mode]
        if est != "Data":
            yields["MC"][ptDict[str(region)]][cat][allMode] += yields[est][ptDict[str(region)]][cat][mode]
            yields["MC"][ptDict[str(region)]][cat][mode]    += yields[est][ptDict[str(region)]][cat][mode]


# categorize QCD as hadronic to make the yield table consistant
for est, region, cat, mode, y in results:
    if y <= 0 or not ("QCD" in est or "fake" in est) or cat != "all": continue
    yields[est][ptDict[str(region)]]["had"][mode] = yields[est][ptDict[str(region)]][cat][mode]

    # fill all and MC entries for each cat
    if yields[est][ptDict[str(region)]]["had"][mode] > 0:
        yields[est][ptDict[str(region)]]["had"][allMode] += yields[est][ptDict[str(region)]]["had"][mode]
        yields["MC"][ptDict[str(region)]]["had"][allMode] += yields[est][ptDict[str(region)]]["had"][mode]
        yields["MC"][ptDict[str(region)]]["had"][mode]    += yields[est][ptDict[str(region)]]["had"][mode]

# fill all as sum of cats
for estimator in allEstimators:
    est = estimator.name.split("_")[0]
    for i_region, region in enumerate(allPhotonRegions):
        for i_mode, mode in enumerate(channels):

            if yields[est][ptDict[str(region)]]["all"][mode] <= 0:
                yields[est][ptDict[str(region)]]["all"][mode] = 0
                for i_cat, cat in enumerate(["gen","misID","had"]):
                    yields[est][ptDict[str(region)]]["all"][mode]    += yields[est][ptDict[str(region)]][cat][mode]
                    yields[est][ptDict[str(region)]]["all"][allMode] += yields[est][ptDict[str(region)]][cat][mode]
                    if est != "Data":
                        yields["MC"][ptDict[str(region)]]["all"][allMode] += yields[est][ptDict[str(region)]][cat][mode]
                        yields["MC"][ptDict[str(region)]]["all"][mode]    += yields[est][ptDict[str(region)]][cat][mode]

mc.sort(key=lambda est: -float(yields[est][ptDict[str(allPhotonRegions[0])]]["all"][allMode].val))

# remove negative entries
for estimator in list(set([e.name.split("_")[0] for e in allEstimators])) + ["MC"]:
    for region in yields[estimator].keys():
        for cat in yields[estimator][region].keys():
            for mode in yields[estimator][region][cat].keys():
                if yields[estimator][region][cat][mode] < 0:
                    yields[estimator][region][cat][mode] = str(u_float(0))
                elif estimator == "Data":
                    yields[estimator][region][cat][mode] = str(int(yields[estimator][region][cat][mode].val))
                else:
                    yields[estimator][region][cat][mode] = "%.2f"%yields[estimator][region][cat][mode].val + " (%.1f%s)"%(yields[estimator][region][cat][mode].val*100/signal[region][mode].val if signal[region][mode].val else 0, "\\%")


def printYieldTable( m ):

    if (m != "e" and "misDY" in args.controlRegion): return

    with open("logs/%i_%s-%s.log"%(args.year,cr,m), "w") as f:
    
        if m in ["e", "all"]:
            f.write("\\begin{frame}\n")
            f.write("\\frametitle{Yields - %s}\n\n"%args.label)

        f.write("\\begin{table}\n")
        f.write("\\centering\n")

        f.write("\\resizebox{0.9\\textwidth}{!}{\n")
        f.write("\\begin{tabular}{c||c||c|c|c||c||c|c|c||c||c|c|c||c||c|c|c}\n")

        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("\\multicolumn{17}{c}{%s}\\\\ \n"%( ", ".join( [cr] + [m] ) ) )
        f.write("\\hline\n")
        f.write("\\multicolumn{17}{c}{%i: $\\mathcal{L}=%s$ fb$^{-1}$}\\\\ \n"%(args.year, "{:.2f}".format(lumi_scale)))
        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("\\multicolumn{17}{c}{}\\\\ \n")

        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("Sample  & \\multicolumn{4}{c||}{inclusive} & \\multicolumn{4}{c||}{%i $\\leq$ \\pT($\\gamma$) $<$ %i GeV} & \\multicolumn{4}{c||}{%i $\\leq$ \\pT($\\gamma$) $<$ %i GeV} & \\multicolumn{4}{c}{\\pT($\\gamma$) $>$ %i GeV}\\\\ \n"%(20,120,120,220,220))
        f.write("\\hline\n")
        f.write("        & \\textbf{events} & $\\gamma$ & misID e & had $\\gamma$ / fake / PU $\\gamma$ & \\textbf{events} & $\\gamma$ & misID e & had $\\gamma$ / fake / PU $\\gamma$ & \\textbf{events} & $\\gamma$ & misID e & had $\\gamma$ / fake / PU $\\gamma$ & \\textbf{events} & $\\gamma$ & misID e & had $\\gamma$ / fake / PU $\\gamma$ \\\\ \n")
        f.write("\\hline\n")
        f.write("\\hline\n")
        for s in mc:
            f.write("%s & \\textbf{%s} & %s & %s & %s & \\textbf{%s} & %s & %s & %s & \\textbf{%s} & %s & %s & %s & \\textbf{%s} & %s & %s & %s \\\\ \n" %tuple( [s] + [ yields[s][pt][cat][m] for lep, pt, cat in regions if lep == m]) )
            f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("MC total & \\textbf{%s} & %s & %s & %s & \\textbf{%s} & %s & %s & %s & \\textbf{%s} & %s & %s & %s & \\textbf{%s} & %s & %s & %s \\\\ \n" %tuple( [yields["MC"][pt][cat][m] for lep, pt, cat in regions if lep == m] ))
        f.write("\\hline\n")
        if not args.noData:
            f.write("data total & \\textbf{%s} & \\multicolumn{3}{c||}{} & \\textbf{%s} & \\multicolumn{3}{c||}{} & \\textbf{%s} & \\multicolumn{3}{c||}{} & \\textbf{%s} & \\multicolumn{3}{c}{} \\\\ \n" %tuple( [ yields["Data"][pt][cat][m] for lep, pt, cat in regions if cat=="all" and lep == m] ))
            f.write("\\hline\n")
            f.write("data/MC    & \\textbf{%.2f} & \\multicolumn{3}{c||}{} & \\textbf{%.2f} & \\multicolumn{3}{c||}{} & \\textbf{%.2f} & \\multicolumn{3}{c||}{} & \\textbf{%.2f} & \\multicolumn{3}{c}{} \\\\ \n" %tuple( [float(yields["Data"][pt][cat][m])/float(yields["MC"][pt][cat][m].split(" ")[0]) if float(yields["MC"][pt][cat][m].split(" ")[0]) > 0 and float(yields["Data"][pt][cat][m]) > 0 else 1. for lep, pt, cat in regions if cat == "all" if lep == m] ))
#            f.write("data/MC    & \\textbf{%.2f} & \\multicolumn{3}{c||}{} & \\textbf{%.2f} & \\multicolumn{3}{c||}{} & \\textbf{%.2f} & \\multicolumn{3}{c||}{} & \\textbf{%.2f} & \\multicolumn{3}{c}{} \\\\ \n" %tuple( [float(yields["Data"][pt][cat][m])/float(yields["MC"][pt][cat][m]) if yields["MC"][pt][cat][m] != "" and yields["Data"][pt][cat][m] != "" and float(yields["MC"][pt][cat][m]) > 0 else 1. for lep, pt, cat in regions if cat == "all" and lep == m] ))
            f.write("\\hline\n")
        f.write("\\hline\n")
    
        f.write("\\multicolumn{17}{c}{}\\\\ \n")
#        f.write("\\multicolumn{1}{c}{} & \\multicolumn{4}{c}{$\\gamma$ = genuine photons} & \\multicolumn{4}{c}{had $\\gamma$ = hadronic photons} & \\multicolumn{4}{c}{misID e = misID electrons} & \\multicolumn{4}{c}{fake = hadronic fakes} \\\\ \n")
        f.write("\\multicolumn{1}{c}{} & \\multicolumn{3}{c}{$\\gamma$ = genuine photons} & \\multicolumn{3}{c}{had $\\gamma$ = hadronic photons} & \\multicolumn{3}{c}{misID e = misID electrons}  & \\multicolumn{3}{c}{fake = hadronic fakes} & \\multicolumn{3}{c}{PU $\\gamma$ = PU photons} & \\multicolumn{1}{c}{}\\\\ \n")


        f.write("\\end{tabular}\n")
        f.write("}\n\n") #resizebox

        f.write("\\end{table}\n\n")
        if m in ["mu", "all"] or (m == "e" and "misDY" in args.controlRegion):
            f.write("\\end{frame}\n")
        f.write("\n\n\n")


for m in [allMode] + channels:
    printYieldTable( m )
