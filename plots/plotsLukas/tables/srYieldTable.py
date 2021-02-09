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
argParser.add_argument("--year",               action="store",      default="RunII",   type=str,  choices=["2016","2017","2018","RunII"],               help="which year?")
argParser.add_argument("--label",              action="store",      default="Region SR3p",  type=str, nargs="*",                            help="which region label?")
args = argParser.parse_args()

args.label = " ".join(args.label)
args.label = args.label.replace("geq", "$\\geq$")

if args.year != "RunII": args.year = int(args.year)

if not os.path.isdir("logs"): os.mkdir("logs")

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74
else: lumi_scale = 35.92 + 41.53 + 59.74

CR_para = allRegions["SR3pTable"]["parameters"]
regions = allRegions["SR3pTable"]["inclRegion"] + allRegions["SR3pTable"]["regions"]
channels = ["all"]

mc  = ["TTG","Top","WG","ZG","WJets","DY_LO","GQCD","other","all_mc"]
allEst = []
allEst += [s for s in mc]
allEst += [s+"_gen" for s in mc]
allEst += [s+"_misID" for s in mc]
allEst += [s+"_had" for s in mc]
allEst += [s+"_hp" for s in mc]
allEst += [s+"_fake" for s in mc]
allEst += [s+"_PU" for s in mc]


years = [2016,2017,2018] if args.year == "RunII" else [args.year]
setup = {}
estimators = {}
allEstimators = {}
for y in years:
    setup[y]          = Setup(year=y, photonSelection=True, checkOnly=True)
    estimators[y]     = EstimatorList(setup[y])
    allEstimators[y]  = estimators[y].constructEstimatorList( allEst )
    for estimate in allEstimators[y]:
        estimate.initCache(setup[y].defaultCacheDir())

    setup[y] = setup[y].sysClone(parameters=CR_para)

def getVals(proc, ptRegion):
        print proc, ptRegion
        ests = [proc+s for s in ["", "_gen","_misID","_had","_hp","_fake","_PU"]]
        filteredEsts = []
        for est in ests:
            filteredEsts.append( [e for e in allEstimators[years[0]] if e.name == est ][0] )
        hadProc =  [ e for e in allEstimators[years[0]] if e.name == proc+"_had" ][0]

        reg = regions[:2] if ptRegion == "low" else regions[2:]
        procVals = []

        for r in reg:
            res = {}
            for e in filteredEsts:
                res[e.name] = 0

            res["had"+hadProc.name] = 0

            for y in years:
                filteredEsts = []
                for est in ests:
                    filteredEsts.append( [e for e in allEstimators[y] if e.name == est ][0] )
                hadProc =  [ e for e in allEstimators[y] if e.name == proc+"_had" ][0]

                res["had"+hadProc.name] += hadProc.cachedEstimate(r, "all", setup[y], overwrite=False, checkOnly=False).val
                for e in filteredEsts:
                    res[e.name] += e.cachedEstimate(r, "all", setup[y], overwrite=False, checkOnly=False).val


            for e in filteredEsts:
                if e.name.endswith("_hp") or e.name.endswith("_fake") or e.name.endswith("_PU"):
                    res[e.name] *= 100./ res["had"+hadProc.name] if res["had"+hadProc.name] > 0 else 0.
                procVals.append(float(res[e.name]))
        return tuple(procVals)

def printYieldTable():

    with open("logs/SR3pTable_%s.log"%str(args.year), "w") as f:
    
        f.write("\\begin{frame}\n")
        f.write("\\frametitle{Yields - %s}\n\n"%args.label)

        f.write("\\begin{table}\n")
        f.write("\\centering\n")

        f.write("\\resizebox{0.9\\textwidth}{!}{\n")
        f.write("\\begin{tabular}{c||c||c|c|c||c||c|c|c}\n")
        f.write("\\hline\n")
        f.write("\\multicolumn{9}{c}{%s, $\\nJet\\geq 3$, $e$+$\\mu$ channel}\\\\ \n"%str(args.year))
        f.write("\\hline\n")
        f.write("& \\multicolumn{4}{c||}{inclusive} & \\multicolumn{4}{c}{20 $\\leq$ \\pT($\\gamma$) $<$ 120 GeV} \\\\ \n")
        f.write("\\hline\n")
        f.write(" Sample & \\textbf{events} & $\\gamma$ & misID e & had $\\gamma$ / fake / PU $\\gamma$ & \\textbf{events} & $\\gamma$ & misID e & had $\\gamma$ / fake / PU $\\gamma$ \\\\ \n")
        f.write("\\hline\n")
        f.write("\\hline\n")

        f.write("tt$\\gamma$ & \\textbf{%.2f} & %.2f  & %.2f  & %.2f (%.1f percent /%.1f percent /%.1f percent )  & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) \\\\ \n"%getVals("TTG", ptRegion="low"))
        f.write("\\hline\n")
        f.write("t($\\gamma$)/tW($\\gamma$)/tt & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent )  & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) \\\\ \n"%getVals("Top", ptRegion="low"))
        f.write("\\hline\n")
        f.write("W$\\gamma$ & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent )  & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) \\\\ \n"%getVals("WG", ptRegion="low"))
        f.write("\\hline\n")
        f.write("Z$\\gamma$ & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) \\\\ \n"%getVals("ZG", ptRegion="low"))
        f.write("\\hline\n")
        f.write("W+jets & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) \\\\ \n"%getVals("WJets", ptRegion="low"))
        f.write("\\hline\n")
        f.write("Drell-Yan & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) \\\\ \n"%getVals("DY_LO", ptRegion="low"))
        f.write("\\hline\n")
        f.write("Multijet (MC) & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) \\\\ \n"%getVals("GQCD", ptRegion="low"))
        f.write("\\hline\n")
        f.write("Other & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) \\\\ \n"%getVals("other", ptRegion="low"))
        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("MC total & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent )  & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) \\\\ \n"%getVals("all_mc", ptRegion="low"))
        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write(" & \\multicolumn{4}{c||}{120 $\\leq$ \\pT($\\gamma$) $<$ 220 GeV} & \\multicolumn{4}{c}{\\pT($\\gamma$) $>$ 220 GeV}\\\\ \n")
        f.write("\\hline\n")
        f.write(" Sample & \\textbf{events} & $\\gamma$ & misID e & had $\\gamma$ / fake / PU $\\gamma$ & \\textbf{events} & $\\gamma$ & misID e & had $\\gamma$ / fake / PU $\\gamma$ \\\\ \n")
        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("tt$\\gamma$ & \\textbf{%.2f} & %.2f  & %.2f  & %f (%.1f percent /%.1f percent /%.1f percent )  & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) \\\\ \n"%getVals("TTG", ptRegion="high"))
        f.write("\\hline\n")
        f.write("t($\\gamma$)/tW($\\gamma$)/tt & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent )  & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) \\\\ \n"%getVals("Top", ptRegion="high"))
        f.write("\\hline\n")
        f.write("W$\\gamma$ & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent )  & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) \\\\ \n"%getVals("WG", ptRegion="high"))
        f.write("\\hline\n")
        f.write("Z$\\gamma$ & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) \\\\ \n"%getVals("ZG", ptRegion="high"))
        f.write("\\hline\n")
        f.write("W+jets & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) \\\\ \n"%getVals("WJets", ptRegion="high"))
        f.write("\\hline\n")
        f.write("Drell-Yan & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) \\\\ \n"%getVals("DY_LO", ptRegion="high"))
        f.write("\\hline\n")
        f.write("Multijet (MC) & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) \\\\ \n"%getVals("GQCD", ptRegion="high"))
        f.write("\\hline\n")
        f.write("Other & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) \\\\ \n"%getVals("other", ptRegion="high"))
        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("MC total & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent )  & \\textbf{%.2f} & %.2f & %.2f & %.2f (%.1f percent /%.1f percent /%.1f percent ) \\\\ \n"%getVals("all_mc", ptRegion="high"))
        f.write("\\hline\n")

        f.write("\\end{table}\n\n")
        f.write("\\end{frame}\n")
        f.write("\n")


printYieldTable()
