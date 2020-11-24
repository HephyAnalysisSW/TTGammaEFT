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

import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

lumi_scale = 1 #35.92

CR_para = allRegions[args.controlRegion]["parameters"]
photonSelection = not allRegions[args.controlRegion]["noPhotonCR"]
allPhotonRegions = allRegions[args.controlRegion]["inclRegion"] + allRegions[args.controlRegion]["regions"] if photonSelection else allRegions[args.controlRegion]["inclRegion"]

noCat_sel = "all"
allCat    = ["all","gen","misID","np"]

blind = False
if photonSelection:
    if "SR" in args.controlRegion:
        inclRegionsTTG = inclRegionsTTGloose
        regionsTTG = regionsTTGloose
        blind = args.year != 2016
    ptDict = {str(inclRegionsTTG[0]):"all", str(regionsTTG[0]):"lowPT", str(regionsTTG[1]):"medPT", str(regionsTTG[2]):"highPT"}
    catSel = ["all","gen","misID","np"]
else:
    ptDict = {str(noPhotonRegionTTG[0]):"all"}
    catSel = ["all"]

setup          = Setup(year=args.year, photonSelection=False, checkOnly=True)
estimators     = EstimatorList(setup)
allProcesses   = [item for item in allProcesses if not "fakes-DD" in item and not "_had" in item]
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
for estName in [e.name for e in allEstimators] + ["MC","MC_gen","MC_misID","MC_np","MC_PU","MC_fake","MC_hp"]:
    est = estName.split("_")[0]
    yields[est] = {}
    for i_region, region in enumerate(allPhotonRegions):
        yields[est][ptDict[str(region)]] = {}
        signal[ptDict[str(region)]] = {}
        for i_cat, cat in enumerate(["gen","misID","np","PU","fake","hp","all"]):
            yields[est][ptDict[str(region)]][cat] = {}
            for i_mode, mode in enumerate(channels + [allMode]):
                 yields[est][ptDict[str(region)]][cat][mode] = u_float(0)
                 signal[ptDict[str(region)]][mode] = u_float(0)

jobs = []
for estimator in allEstimators:
    cat = estimator.name.split("_")[-1] if estimator.name.split("_")[-1] in ["gen","misID","np","hp","fake","PU"] else "all"
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
    if y <= 0 or not "QCD" in est or cat != "all": continue
    yields[est][ptDict[str(region)]]["np"][mode] = yields[est][ptDict[str(region)]][cat][mode]

    # fill all and MC entries for each cat
    if yields[est][ptDict[str(region)]]["np"][mode] > 0:
        yields[est][ptDict[str(region)]]["np"][allMode] += yields[est][ptDict[str(region)]]["np"][mode]
        yields["MC"][ptDict[str(region)]]["np"][allMode] += yields[est][ptDict[str(region)]]["np"][mode]
        yields["MC"][ptDict[str(region)]]["np"][mode]    += yields[est][ptDict[str(region)]]["np"][mode]

# fill all as sum of cats
for est in list(set([e.name.split("_")[0] for e in allEstimators])):
#    est = estimator.name.split("_")[0]
    for i_region, region in enumerate(allPhotonRegions):
        for i_mode, mode in enumerate(channels):

            if yields[est][ptDict[str(region)]]["all"][mode] <= 0:
                yields[est][ptDict[str(region)]]["all"][mode] = 0
                for i_cat, cat in enumerate(["gen","misID","np"]):
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
            if cat in ["hp", "fake", "PU"]: continue
            for mode in yields[estimator][region][cat].keys():
                if yields[estimator][region][cat][mode] < 0:
                    yields[estimator][region][cat][mode] = str(u_float(0))
                elif estimator == "Data":
                    yields[estimator][region][cat][mode] = str(int(yields[estimator][region][cat][mode].val))
                else:
                    if cat == "np" and estimator != "MC" and not "QCD" in estimator:
                        had  = yields[estimator][region]["np"][mode].val
                        pu   = yields[estimator][region]["PU"][mode].val*100/had if had else 0
                        hp   = yields[estimator][region]["hp"][mode].val*100/had if had else 0
                        fake = yields[estimator][region]["fake"][mode].val*100/had if had else 0
                        yields[estimator][region][cat][mode] = "%.2f (%.1f%s/%.1f%s/%.1f%s)"%(yields[estimator][region][cat][mode].val, hp, "\\%", fake, "\\%", pu, "\\%" ) + " "
                    else:
                        yields[estimator][region][cat][mode] = "%.2f"%yields[estimator][region][cat][mode].val + " "


def printYieldTable( m ):

    if (m != "e" and "misDY" in args.controlRegion): return

    with open("logs/%i_%sMC-%s.log"%(args.year,cr,m), "w") as f:
    
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
            f.write("%s & \\textbf{%s} & %s & %s & %s & \\textbf{%s} & %s & %s & %s & \\textbf{%s} & %s & %s & %s & \\textbf{%s} & %s & %s & %s \\\\ \n" %tuple( [s] + [ yields[s][pt][cat][m] for lep, pt, cat in regions if lep == m and cat in allCat]) )
            f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("MC total & \\textbf{%s} & %s & %s & %s & \\textbf{%s} & %s & %s & %s & \\textbf{%s} & %s & %s & %s & \\textbf{%s} & %s & %s & %s \\\\ \n" %tuple( [yields["MC"][pt][cat][m] for lep, pt, cat in regions if lep == m and cat in allCat] ))
        f.write("\\hline\n")
        if not args.noData:
            f.write("data total & \\textbf{%s} & \\multicolumn{3}{c||}{} & \\textbf{%s} & \\multicolumn{3}{c||}{} & \\textbf{%s} & \\multicolumn{3}{c||}{} & \\textbf{%s} & \\multicolumn{3}{c}{} \\\\ \n" %tuple( [ yields["Data"][pt][cat][m] for lep, pt, cat in regions if cat=="all" and lep == m and cat in allCat] ))
            f.write("\\hline\n")
            f.write("data/MC    & \\textbf{%.2f} & \\multicolumn{3}{c||}{} & \\textbf{%.2f} & \\multicolumn{3}{c||}{} & \\textbf{%.2f} & \\multicolumn{3}{c||}{} & \\textbf{%.2f} & \\multicolumn{3}{c}{} \\\\ \n" %tuple( [float(yields["Data"][pt][cat][m])/float(yields["MC"][pt][cat][m].split(" ")[0]) if float(yields["MC"][pt][cat][m].split(" ")[0]) > 0 and float(yields["Data"][pt][cat][m]) > 0 else 1. for lep, pt, cat in regions if cat == "all" if lep == m and cat in allCat] ))
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



def printNoPhotonYieldTable( ):

    with open("logs/%i_%s.log"%(args.year,cr), "w") as f:
 
        f.write("\\begin{frame}\n")
        f.write("\\frametitle{Yields - %s}\n\n"%args.label)

        f.write("\\begin{table}\n")
        f.write("\\centering\n")

        f.write("\\resizebox{0.9\\textwidth}{!}{\n")
        f.write("\\begin{tabular}{c||c||c|c|c||c||c|c|c||c||c|c|c}\n")

        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("\\multicolumn{13}{c}{%s}\\\\ \n"%( ", ".join( [cr] ) ) )
        f.write("\\hline\n")
        f.write("\\multicolumn{13}{c}{%i: $\\mathcal{L}=%s$ fb$^{-1}$}\\\\ \n"%(args.year, "{:.2f}".format(lumi_scale)))
        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("\\multicolumn{13}{c}{}\\\\ \n")

        f.write("\\hline\n")
        f.write("\\hline\n")
        if args.controlRegion.startswith("DY"):
            f.write("Sample  & \\multicolumn{4}{c||}{ SF (ee/$\\mu\\mu$) channel } & \\multicolumn{4}{c||}{ee channel} & \\multicolumn{4}{c}{$\\mu\\mu$ channel}\\\\ \n")
        else:
            f.write("Sample  & \\multicolumn{4}{c||}{ e/$\\mu$ channel } & \\multicolumn{4}{c||}{e channel} & \\multicolumn{4}{c}{$\\mu$ channel}\\\\ \n")
        f.write("\\hline\n")
        f.write("        & \\textbf{events} & $\\gamma$ & misID e & had $\\gamma$ / fake / PU $\\gamma$ & \\textbf{events} & $\\gamma$ & misID e & had $\\gamma$ / fake / PU $\\gamma$ & \\textbf{events} & $\\gamma$ & misID e & had $\\gamma$ / fake / PU $\\gamma$ \\\\ \n")
        f.write("\\hline\n")
        f.write("\\hline\n")
        for s in mc:
            f.write("%s & \\textbf{%s} &  &  &  & \\textbf{%s} &  &  &  & \\textbf{%s} &  &  &   \\\\ \n" %tuple( [s] + [ yields[s][pt][cat][lep] for lep, pt, cat in regions ]) )
            f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("MC total & \\textbf{%s} &  &  &  & \\textbf{%s} &  &  &  & \\textbf{%s} &  &  &   \\\\ \n" %tuple( [ yields["MC"][pt][cat][lep] for lep, pt, cat in regions] ))
        f.write("\\hline\n")
        if not args.noData:
            f.write("data total & \\textbf{%s} & \\multicolumn{3}{c||}{} & \\textbf{%s} & \\multicolumn{3}{c||}{} & \\textbf{%s} & \\multicolumn{3}{c}{} \\\\ \n" %tuple( [ yields["Data"][pt][cat][lep] for lep, pt, cat in regions if cat=="all"] ))
            f.write("\\hline\n")
            f.write("data/MC    & \\textbf{%.2f} & \\multicolumn{3}{c||}{} & \\textbf{%.2f} & \\multicolumn{3}{c||}{} & \\textbf{%.2f} & \\multicolumn{3}{c}{} \\\\ \n" %tuple( [float(yields["Data"][pt][cat][lep])/float(yields["MC"][pt][cat][lep]) if float(yields["MC"][pt][cat][lep]) and float(yields["Data"][pt][cat][lep]) else 1. for lep, pt, cat in regions if cat == "all"] ))
            f.write("\\hline\n")
        f.write("\\hline\n")
    
        f.write("\\end{tabular}\n")
        f.write("}\n\n") #resizebox

        f.write("\\end{table}\n\n")
        f.write("\\end{frame}\n")
        f.write("\n\n\n")


if not photonSelection:
    printNoPhotonYieldTable()
else:
    for m in [allMode] + channels:
        printYieldTable( m )
