#!/usr/bin/env python

import sys

from TTGammaEFT.Analysis.regions         import regionsTTG, noPhotonRegionTTG, inclRegionsTTG, inclRegionsTTGfake, regionsTTGfake
from TTGammaEFT.Analysis.DataDrivenFakeEstimate import DataDrivenFakeEstimate
from TTGammaEFT.Analysis.SetupHelpers    import *
from TTGammaEFT.Analysis.Setup           import Setup

from Analysis.Tools.u_float              import u_float

loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']
CRChoices     = allRegions.keys()
# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",         action="store",  default="INFO",           choices=loggerChoices, help="Log level for logging")
argParser.add_argument("--year",             action="store",  default=2016,   type=int,                        help="Which year?")
argParser.add_argument("--cores",            action="store",  default=1,      type=int,                        help="run multicore?")
argParser.add_argument("--controlRegion",    action="store",  default="SR4pM3",   type=str, choices=CRChoices,     help="For CR region?")
argParser.add_argument("--label",             action="store",      default="Region",  type=str, nargs="*",                            help="which region label?")
args = argParser.parse_args()

args.label = " ".join(args.label)

# Logging
import Analysis.Tools.logger as logger
logger = logger.get_logger(   args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

logger.debug("Start run_estimate.py")

if not args.controlRegion:
    logger.warning("ControlRegion not known")
    sys.exit(0)

if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74

parameters       = allRegions[args.controlRegion]["parameters"]
channels         = allRegions[args.controlRegion]["channels"] 
photonSelection  = not allRegions[args.controlRegion]["noPhotonCR"]
allPhotonRegions = allRegions[args.controlRegion]["inclRegion"] + allRegions[args.controlRegion]["regions"] if photonSelection else allRegions[args.controlRegion]["regions"]
setup            = Setup( year=args.year, photonSelection=False, checkOnly=False )

estimate = DataDrivenFakeEstimate( "fakes-DD" )
estimate.initCache(setup.defaultCacheDir())
estimate.isData = False

setup            = setup.sysClone( parameters=parameters )

def wrapper(arg):
        # INFO: fakeFactor = fakesData / fakesMC * kappaData * kappaMC
        key,subkey,r,channel,setup = arg
        logger.info("Running estimate for region %s, channel %s in setup %s"%(r,channel, args.controlRegion if args.controlRegion else "None"))
#        fakeFactor = estimate.cachedFakeFactor(r, channel, setup, checkOnly=True).val
        kappaData  = estimate._kappaData(r, channel, setup)
        kappaMC    = estimate._kappaMC(r, channel, setup)
        fakesData  = estimate._fakesData(r, channel, setup)
        fakesMC    = estimate._fakesMC(r, channel, setup)
        ddfakes    = fakesData * kappaMC * kappaData
        sf         = ddfakes / fakesMC if fakesMC.val > 0 else u_float(0)
        return (key, subkey, channel, fakesData.tuple(), kappaData.tuple(), kappaMC.tuple(), ddfakes.tuple(), fakesMC.tuple(), sf.tuple() )

def strToKey( r ):
    print r
    r   = r.replace("\\","\\\\").replace("#","\\")
    print r
    if len(r.split(","))>1:
        out = tuple(r.split(",")) if "p_{T}" in r else ("inclusive", r)
    else:
        out = (r,"inclusive") if "p_{T}" in r else ("inclusive", "inclusive")
    print out
    out = ( "$%s$"%o if o !="inclusive" else o for o in out)
    print out
    return out

jobs=[]
resDict = {}
for (i, r) in enumerate(allPhotonRegions):
    key, subkey = strToKey(r.texString())
    print key, subkey
    if not key in resDict.keys(): resDict[key] = {}
    if not subkey in resDict[key].keys(): resDict[key][subkey] = {}
    for channel in channels:
        resDict[key][subkey][channel] = (0,0,0,0,0)
        jobs.append((key, subkey, r, channel, setup))

if args.cores > 1:
    from multiprocessing import Pool
    pool = Pool( processes=args.cores )
    results = pool.map( wrapper, jobs )
    pool.close()
else:
    results    = map(wrapper, jobs)

for key, subkey, ch, a, b, c, d, e, f in results:
    resDict[key][subkey][ch] = (a,b,c,d,e,f)
    print key, subkey, ch, resDict[key][subkey][ch]

def printFakesTable():

    with open("logs/fakeFactors_%i_%s.log"%(args.year,args.controlRegion), "w") as f:

        f.write("\\begin{frame}\n")
        f.write("\\frametitle{DataDriven-Fakes - %s}\n\n"%args.label)

        f.write("\\begin{table}\n")
        f.write("\\centering\n")

        f.write("\\resizebox{0.9\\textwidth}{!}{\n")
        f.write("\\begin{tabular}{c||c|c|c||c||c||c||c|c|c||c||c||c}\n")

        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("\\multicolumn{13}{c}{%s}\\\\ \n"%( ", ".join( [args.controlRegion] ) ) )
        f.write("\\hline\n")
        f.write("\\multicolumn{13}{c}{%i: $\\mathcal{L}=%s$ fb$^{-1}$}\\\\ \n"%(args.year, "{:.2f}".format(lumi_scale)))
        f.write("\\hline\n")
        f.write("\\hline\n")
        for pt in sorted(resDict.keys(), key = lambda n: [i for i, l in enumerate(["inclusive", "20 \\leq", "120 \\leq", "220 \\leq"]) if l in n][0] ):
            resD = resDict[pt]
            f.write("\\multicolumn{13}{c}{}\\\\ \n")
            f.write("\\hline\n")
            f.write("\\hline\n")
            f.write("\\multicolumn{13}{c}{%s}\\\\ \n"%(pt))
            f.write("\\hline\n")
            f.write("       & \\multicolumn{6}{c||}{ \\textbf{e channel} } & \\multicolumn{6}{c}{\\textbf{$\\mu$ channel}}\\\\ \n")
            f.write("\\hline\n")
            f.write("\\textbf{Region} & fakes high chgIso & $r_\\text{iso}^\\text{HS}$ & $\\kappa_\\text{MC}$ & \\textbf{DD-fakes} & \\textbf{MC-fakes} & \\textbf{DD-Fakes/MC-Fakes} & fakes high chgIso & $r_\\text{iso}^\\text{HS}$ & $\\kappa_\\text{MC}$ & DD-fakes & MC-fakes & \\textbf{DD-Fakes/MC-Fakes} \\\\ \n")
            f.write("\\hline\n")
            for reg in sorted(resD.keys()):
                res = resD[reg]
                f.write("%s & %.2f $\\pm$ %.2f & %.2f $\\pm$ %.2f & %.2f $\\pm$ %.2f & \\textbf{%.2f $\\pm$ %.2f} & \\textbf{%.2f $\\pm$ %.2f} & \\textbf{%.2f $\\pm$ %.2f} & %.2f $\\pm$ %.2f & %.2f $\\pm$ %.2f & %.2f $\\pm$ %.2f & \\textbf{%.2f $\\pm$ %.2f} & \\textbf{%.2f $\\pm$ %.2f} & \\textbf{%.2f $\\pm$ %.2f} \\\\ \n"%(reg,res["e"][0][0],res["e"][0][1],res["e"][1][0],res["e"][1][1],res["e"][2][0],res["e"][2][1],res["e"][3][0],res["e"][3][1],res["e"][4][0],res["e"][4][1],res["e"][5][0],res["e"][5][1],res["mu"][0][0],res["mu"][0][1],res["mu"][1][0],res["mu"][1][1],res["mu"][2][0],res["mu"][2][1],res["mu"][3][0],res["mu"][3][1],res["mu"][4][0],res["mu"][4][1],res["mu"][5][0],res["mu"][5][1]) )
                f.write("\\hline\n")
            f.write("\\hline\n")

        f.write("\\multicolumn{13}{c}{}\\\\ \n")
        f.write("\\hline\n")
        f.write("\\hline\n")

        f.write("\\end{tabular}\n")
        f.write("}\n\n") #resizebox

        f.write("\\end{table}\n\n")
        f.write("\\end{frame}\n")
        f.write("\n\n\n")


printFakesTable()
