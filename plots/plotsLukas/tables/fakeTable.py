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
from TTGammaEFT.Analysis.DataDrivenQCDEstimate import DataDrivenQCDEstimate
from TTGammaEFT.Analysis.SetupHelpers    import *

from Analysis.Tools.u_float              import u_float

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

addSF = True

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                  help="Log level for logging")
argParser.add_argument("--controlRegion",      action="store",      default=None,   type=str,                                          help="For CR region?")
argParser.add_argument("--removeNegative",     action="store_true",                                                                    help="Set negative values to 0?", )
argParser.add_argument("--cores",            action="store",  default=1,      type=int,                        help="run multicore?")
argParser.add_argument("--noData",             action="store_true", default=False,                                                     help="also plot data?")
argParser.add_argument("--year",               action="store",      default="2016",   type=str,  choices=["2016","2017","2018","RunII"],               help="which year?")
argParser.add_argument("--label",              action="store",      default="Region",  type=str, nargs="*",                            help="which region label?")
args = argParser.parse_args()

if args.year !=  "RunII": args.year = int(args.year)

args.label = " ".join(args.label)
args.label = args.label.replace("geq", "$\\geq$")
cr = args.controlRegion

if not os.path.isdir("logs"): os.mkdir("logs")
# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74

CR_para = allRegions[args.controlRegion]["parameters"]
photonSelection = True
allPhotonRegions = inclRegionsTTGloose + regionsTTGloose

catSel = ["all","gen","misID","had"]
sieieSel  = ["lowSieie", "highSieie"]
chgSel    = ["lowChgIso", "highChgIso"]
noCat_sel = "all"
allMode = "all"

ptDict = {str(inclRegionsTTGloose[0]):"all", str(regionsTTGloose[0]):"lowhadPT", str(regionsTTGloose[1]):"medhadPT", str(regionsTTGloose[2]):"highhadPT"}
channels = lepChannels
regions = [(m, pt, sieie, chgIso, cat) for m in [allMode] + channels for pt in ptDict.values() for chgIso in chgSel for sieie in sieieSel for cat in catSel]

blind = args.year != 2016

setup          = Setup(year=args.year, photonSelection=photonSelection )#, checkOnly=True)
estimators     = EstimatorList(setup)
allEstimators  = estimators.constructEstimatorList( allProcesses )
mc  = list(set([e.name.split("_")[0] for e in allEstimators]))

if not args.noData:
    allEstimators += [DataObservation(name="Data", process=setup.processes["Data"], cacheDir=setup.defaultCacheDir())]

if args.controlRegion:
    setup = setup.sysClone(parameters=CR_para)

if addSF:
    if setup.nJet == "2":
        DYSF_val    = DY2SF_val
        WGSF_val    = WG2SF_val
        ZGSF_val    = ZG2SF_val
        QCDSF_val   = QCD2SF_val
    elif setup.nJet == "3":
        DYSF_val    = DY3SF_val
        WGSF_val    = WG3SF_val
        ZGSF_val    = ZG3SF_val
        QCDSF_val   = QCD3SF_val
    elif setup.nJet == "4":
        DYSF_val    = DY4SF_val
        WGSF_val    = WG4SF_val
        ZGSF_val    = ZG4SF_val
        QCDSF_val   = QCD4SF_val
    elif setup.nJet == "5":
        DYSF_val    = DY5SF_val
        WGSF_val    = WG5SF_val
        ZGSF_val    = ZG5SF_val
        QCDSF_val   = QCD5SF_val
    elif setup.nJet == "2p":
        DYSF_val    = DY2pSF_val
        WGSF_val    = WG2pSF_val
        ZGSF_val    = ZG2pSF_val
        QCDSF_val   = QCD2pSF_val
    elif setup.nJet == "3p":
        DYSF_val    = DY3pSF_val
        WGSF_val    = WG3pSF_val
        ZGSF_val    = ZG3pSF_val
        QCDSF_val   = QCD3pSF_val
    elif setup.nJet == "4p":
        DYSF_val    = DY4pSF_val
        WGSF_val    = WG4pSF_val
        ZGSF_val    = ZG4pSF_val
        QCDSF_val   = QCD4pSF_val

def wrapper(arg):

        region,channel,setup,estimate, sieie, chgIso, cat, est = arg

        isSR = "low" in sieie and "low" in chgIso

        if   isSR: param = {"addMisIDSF":addSF}
        elif "low"  in sieie and "high" in chgIso: param = { "photonIso":"highChgIso",          "addMisIDSF":addSF }
        elif "high" in sieie and "low"  in chgIso: param = { "photonIso":"highSieie",           "addMisIDSF":addSF }
        elif "high" in sieie and "high" in chgIso: param = { "photonIso":"highChgIsohighSieie", "addMisIDSF":addSF }
        
        params = copy.deepcopy(setup.parameters)
        params.update( param )
        setup_fake = setup.sysClone(parameters=params)

        if estimate.name.lower() == "data":
            estimate = DataObservation(name="Data", process=setup.processes["Data"], cacheDir=setup.defaultCacheDir())
            estimate.initCache(setup_fake.defaultCacheDir())
            if isSR and blind:
                y = u_float(0,0)
            else:
                y = estimate.cachedEstimate( region, channel, setup_fake, checkOnly=True )
        elif "QCD" in estimate.name:
            if not "_" in estimate.name or "had" in estimate.name:
                estimate = DataDrivenQCDEstimate( name="QCD-DD" )
                estimate.initCache(setup.defaultCacheDir())
                y  = estimate.cachedEstimate( region, channel, setup_fake, checkOnly=True )
                y *= QCDSF_val[setup.year].val
                y  = u_float(y.val,0)
            else:
                y = u_float(0,0)
        else:
            estimate = MCBasedEstimate( name=estimate.name, process=setup.processes[estimate.name] )
            estimate.initCache(setup.defaultCacheDir())
            y = estimate.cachedEstimate( region, channel, setup_fake, checkOnly=True )

            if addSF:
                if "DY_LO" in estimate.name:    y *= DYSF_val[setup.year].val #add DY SF
                elif "WJets" in estimate.name:  y *= WJetsSF_val[setup.year].val #add WJets SF
                elif "TTG" in estimate.name:    y *= SSMSF_val[setup.year].val #add TTG SF
                elif "ZG" in estimate.name:     y *= ZGSF_val[setup.year].val #add ZGamma SF
                elif "WG" in estimate.name:     y *= WGSF_val[setup.year].val #add WGamma SF

        if args.removeNegative and y < 0: y = u_float(0,0)

        return est, sieie, chgIso, str(region), cat, channel, y.tuple()

yields = {}
for estName in [e.name for e in allEstimators] + ["MC","MC_gen","MC_misID","MC_had"]:
    est = estName.split("_")[0]
    yields[est] = {}
    for i_sieie, sieie in enumerate(sieieSel):
        yields[est][sieie] = {}
        for i_chgIso, chgIso in enumerate(chgSel):
            yields[est][sieie][chgIso] = {}
            for i_region, region in enumerate(allPhotonRegions):
                yields[est][sieie][chgIso][ptDict[str(region)]] = {}
                for i_cat, cat in enumerate(catSel):
                    yields[est][sieie][chgIso][ptDict[str(region)]][cat] = {}
                    for i_mode, mode in enumerate(channels + [allMode]):
                        yields[est][sieie][chgIso][ptDict[str(region)]][cat][mode] = u_float(0)

jobs = []
for estimator in allEstimators:
    cat = estimator.name.split("_")[-1] if estimator.name.split("_")[-1] in ["gen","misID","had"] else "all"
    est = estimator.name.split("_")[0]
    for i_sieie, sieie in enumerate(sieieSel):
        for i_chgIso, chgIso in enumerate(chgSel):
            for i_region, region in enumerate(allPhotonRegions):
                for i_mode, mode in enumerate(channels):
                    jobs.append( (region, mode, setup, estimator, sieie, chgIso, cat, est) )

if args.cores > 1:
    from multiprocessing import Pool
    pool = Pool( processes=args.cores )
    results = pool.map( wrapper, jobs )
    pool.close()
else:
    results    = map(wrapper, jobs)

for est, sieie, chgIso, region, cat, mode, y in results:
    if y < 0: continue
    yields[est][sieie][chgIso][ptDict[str(region)]][cat][mode] = u_float(y)
    if float(yields[est][sieie][chgIso][ptDict[str(region)]][cat][mode]) > 0:
        yields[est][sieie][chgIso][ptDict[str(region)]][cat][allMode] += yields[est][sieie][chgIso][ptDict[str(region)]][cat][mode]
        if est != "Data":
            yields["MC"][sieie][chgIso][ptDict[str(region)]][cat][allMode] += yields[est][sieie][chgIso][ptDict[str(region)]][cat][mode]
            yields["MC"][sieie][chgIso][ptDict[str(region)]][cat][mode]    += yields[est][sieie][chgIso][ptDict[str(region)]][cat][mode]


for estimator in allEstimators:
    est = estimator.name.split("_")[0]
    for i_sieie, sieie in enumerate(sieieSel):
        for i_chgIso, chgIso in enumerate(chgSel):
            for i_region, region in enumerate(allPhotonRegions):
                for i_mode, mode in enumerate(channels):

                    if yields[est][sieie][chgIso][ptDict[str(region)]]["all"][mode] <= 0:
                        yields[est][sieie][chgIso][ptDict[str(region)]]["all"][mode] = u_float(0)
                        for i_cat, cat in enumerate(["gen","misID","had"]):
                            yields[est][sieie][chgIso][ptDict[str(region)]]["all"][mode]    += yields[est][sieie][chgIso][ptDict[str(region)]][cat][mode]
                            yields[est][sieie][chgIso][ptDict[str(region)]]["all"][allMode] += yields[est][sieie][chgIso][ptDict[str(region)]][cat][mode]
                            if est != "Data":
                                yields["MC"][sieie][chgIso][ptDict[str(region)]]["all"][allMode] += yields[est][sieie][chgIso][ptDict[str(region)]][cat][mode]
                                yields["MC"][sieie][chgIso][ptDict[str(region)]]["all"][mode]    += yields[est][sieie][chgIso][ptDict[str(region)]][cat][mode]

mc.sort(key=lambda est: -yields[est]["lowSieie"]["lowChgIso"][ptDict[str(allPhotonRegions[0])]]["all"][allMode].val)

# remove negative entries
for estName in [e.name for e in allEstimators] + ["MC","MC_gen","MC_misID","MC_had"]:
    estimator = estName.split("_")[0]
    for i_sieie, sieie in enumerate(sieieSel):
        for i_chgIso, chgIso in enumerate(chgSel):
            for region in yields[estimator][sieie][chgIso].keys():
                for cat in yields[estimator][sieie][chgIso][region].keys():
                    for mode in yields[estimator][sieie][chgIso][region][cat].keys():
                        if yields[estimator][sieie][chgIso][region][cat][mode] < 0:
                            yields[estimator][sieie][chgIso][region][cat][mode] = str(u_float(0))
                        else:
                            yields[estimator][sieie][chgIso][region][cat][mode] = str(yields[estimator][sieie][chgIso][region][cat][mode]) #"%.2f"%float(yields[estimator][sieie][chgIso][region][cat][mode])

def printHadFakeYieldTable( m ):

    with open("logs/%s_fake_%s-%s.log"%(args.year,cr,m), "w") as f:
        f.write("\\begin{frame}\n")
        f.write("\\frametitle{Yields - %s}\n\n"%args.label)

        f.write("\\begin{table}\n")
        f.write("\\centering\n")

        for iPT, (lowPT, highPT) in enumerate([ (20,120), (120,220), (220,-1) ]):
            ptNames = ["lowhadPT", "medhadPT", "highhadPT"][iPT]

            f.write("\\resizebox{0.8\\textwidth}{!}{\n")
            f.write("\\begin{tabular}{c||c||c|c|c||c||c|c|c||c||c|c|c||c||c|c|c}\n")

            if lowPT == 20:
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
            if highPT == -1:
                f.write("\\multicolumn{17}{c}{\\pT($\\gamma$) $>$ %i GeV}\\\\ \n"%(lowPT))
            else:
                f.write("\\multicolumn{17}{c}{%i $\\leq$ \\pT($\\gamma$) $<$ %i GeV}\\\\ \n"%(lowPT, highPT))
            f.write("\\hline\n")
            f.write("Sample  & \\multicolumn{4}{c||}{low $\\sigma_{i\\eta i\\eta}$, low chg Iso (SR - LsLc)} & \\multicolumn{4}{c||}{high $\\sigma_{i\\eta i\\eta}$, low chg Iso  (HsLc)}   & \\multicolumn{4}{c||}{low $\\sigma_{i\\eta i\\eta}$, high chg Iso (LsHc)}   & \\multicolumn{4}{c}{high $\\sigma_{i\\eta i\\eta}$, high chg Iso  (HsHc)} \\\\ \n")
            f.write("\\hline\n")
            f.write("        & \\textbf{events} & $\\gamma$ & misID e & had $\\gamma$ / fake / PU $\\gamma$ & \\textbf{events} & $\\gamma$ & misID e & had $\\gamma$ / fake / PU $\\gamma$ & \\textbf{events} & $\\gamma$ & misID e & had $\\gamma$ / fake / PU $\\gamma$ & \\textbf{events} & $\\gamma$ & misID e & had $\\gamma$ / fake / PU $\\gamma$ \\\\ \n")
            f.write("\\hline\n")
            f.write("\\hline\n")
            for s in mc:
                f.write("%s & \\textbf{%s} & %s & %s & %s & \\textbf{%s} & %s & %s & %s & \\textbf{%s} & %s & %s & %s & \\textbf{%s} & %s & %s & %s \\\\ \n" %tuple( [s] + [ yields[s][sieie][chgIso][pt][cat][m] for lep, pt, sieie, chgIso, cat in regions if lep == m and pt == ptNames]) )
                f.write("\\hline\n")
            f.write("\\hline\n")
            f.write("MC total & \\textbf{%s} & %s & %s & %s & \\textbf{%s} & %s & %s & %s & \\textbf{%s} & %s & %s & %s & \\textbf{%s} & %s & %s & %s \\\\ \n" %tuple( [yields["MC"][sieie][chgIso][pt][cat][m] for lep, pt, sieie, chgIso, cat in regions if lep == m and pt == ptNames] ))
            f.write("\\hline\n")
            if not args.noData:
                f.write("data total & \\textbf{%s} & \\multicolumn{3}{c||}{} & \\textbf{%s} & \\multicolumn{3}{c||}{} & \\textbf{%s} & \\multicolumn{3}{c||}{} & \\textbf{%s} & \\multicolumn{3}{c}{} \\\\ \n" %tuple( [yields["Data"][sieie][chgIso][pt][cat][m] for lep, pt, sieie, chgIso, cat in regions if cat == "all" and lep == m and pt == ptNames] ))
                f.write("\\hline\n")
                f.write("data/MC    & \\textbf{%.2f} & \\multicolumn{3}{c||}{} & \\textbf{%.2f} & \\multicolumn{3}{c||}{} & \\textbf{%.2f} & \\multicolumn{3}{c||}{} & \\textbf{%.2f} & \\multicolumn{3}{c}{} \\\\ \n" %tuple( [float(yields["Data"][sieie][chgIso][pt][cat][m])/float(yields["MC"][sieie][chgIso][pt][cat][m]) if yields["Data"][sieie][chgIso][pt][cat][m] != "" and yields["MC"][sieie][chgIso][pt][cat][m] != "" and float(yields["MC"][sieie][chgIso][pt][cat][m]) > 0 else 1. for lep, pt, sieie, chgIso, cat in regions if cat == "all" and lep == m and pt == ptNames] ))
                f.write("\\hline\n")
            f.write("\\hline\n")
    
            if highPT == -1:
                f.write("\\multicolumn{17}{c}{}\\\\ \n")
#                f.write("\\multicolumn{1}{c}{} & \\multicolumn{4}{c}{$\\gamma$ = genuine photons} & \\multicolumn{4}{c}{had $\\gamma$ = hadronic photons} & \\multicolumn{4}{c}{misID e = misID electrons} & \\multicolumn{4}{c}{fake = hadronic fakes} \\\\ \n")
                f.write("\\multicolumn{1}{c}{} & \\multicolumn{3}{c}{$\\gamma$ = genuine photons} & \\multicolumn{3}{c}{had $\\gamma$ = hadronic photons} & \\multicolumn{3}{c}{misID e = misID electrons} & \\multicolumn{3}{c}{fake = hadronic fakes} & \\multicolumn{3}{c}{PU $\\gamma$ = PU photons} & \\multicolumn{1}{c}{}\\\\ \n")


            f.write("\\end{tabular}\n")
            f.write("}\n\n") #resizebox

        f.write("\\end{table}\n\n")
        f.write("\\end{frame}\n\n\n\n")

for m in [allMode] + channels:
    printHadFakeYieldTable( m )
