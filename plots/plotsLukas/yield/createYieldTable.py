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

from TTGammaEFT.Tools.user               import cache_directory
from Analysis.Tools.DirDB                import DirDB
from TTGammaEFT.Analysis.SetupHelpers    import default_DYSF, default_misIDSF
# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                  help="Log level for logging")
argParser.add_argument("--selection",          action="store",      default="dilepOS-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1p")
argParser.add_argument("--small",              action="store_true",                                                                    help="Run only on a small subset of the data?", )
argParser.add_argument("--runOnNonValid",      action="store_true",                                                                    help="Skip missing cached yields?", )
argParser.add_argument("--removeNegative",     action="store_true",                                                                    help="Set negative values to 0?", )
argParser.add_argument("--noData",             action="store_true", default=False,                                                     help="also plot data?")
argParser.add_argument("--year",               action="store",      default=None,   type=int,  choices=[2016,2017,2018],               help="which year?")
argParser.add_argument("--mode",               action="store",      default="all",  type=str,                                          help="which lepton selection?")
argParser.add_argument("--label",              action="store",      default="Region",  type=str,                                          help="which region label?")
args = argParser.parse_args()

args.label = args.label.replace("geq", "$\\geq$")

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

cache_dir = os.path.join(cache_directory, "yields", str(args.year))
yield_dirDB = DirDB( cache_dir )
if not yield_dirDB: raise

if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74

selDir = args.selection
addMisIDSF = False
addDYSF = False
if args.selection.count("addMisIDSF"):
    addMisIDSF = True
    args.selection = "-".join( [ item for item in args.selection.split("-") if item != "addMisIDSF" ] )
if args.selection.count("addDYSF"):
    addDYSF = True
    args.selection = "-".join( [ item for item in args.selection.split("-") if item != "addDYSF" ] )

res = {"sample":None, "selection":args.selection, "mode":"all", "ptBin":"all", "cat":"all", "sieie":"all", "chgIso":"all", "small":args.small}

mc = [ "TTG", "TT_pow", "DY_LO", "singleTop", "WJets", "TG", "WG", "ZG", "other" ]
if not "nLepTight2" in args.selection:
    mc += [ "QCD" ]

allSamples = mc if args.noData else ["data"] + mc

hadFakeSel  = "NoChgIsoNoSieiePhoton" in args.selection
noPhotonSel = not "nPhoton1p" in args.selection and not hadFakeSel
ptSel     = ["all", "lowPT", "medPT", "highPT"]
catSel    = ["all", "photoncat0", "photoncat1", "photoncat2", "photoncat3"]
sieieSel  = ["all" ]
chgSel    = ["all" ]
noCat_sel = "all"
modes     = [args.mode]
region    = "manual"

#for var in ptSel+pthadSel+catSel+hadcatSel+sieieSel+chgSel:
#    vars()[var] = cutInterpreter.cutString( var )

if hadFakeSel:
    catSel = ["all", "photonhadcat0", "photonhadcat1", "photonhadcat2", "photonhadcat3"]
    ptSel  = ["all", "lowhadPT", "medhadPT", "highhadPT"]
    sieieSel  = ["lowSieie", "highSieie"]
    chgSel    = ["lowChgIso", "highChgIso"]

if noPhotonSel:
    modes  = ["all", "e", "mu"] if not "nLepTight2" in args.selection else ["SFtight", "eetight", "mumutight"]
    catSel = ["all"]
    ptSel  = ["all"]

regions = [(mode, pt, sieie, chgIso, cat) for mode in modes for pt in ptSel for chgIso in chgSel for sieie in sieieSel for cat in catSel]

#if hadFakeSel:
#    sieieSel += ["all"]
#    chgSel   += ["all"]

yields = {}
for sample in allSamples + ["MC"]:
    yields[sample] = {}
    for i_sieie, sieie in enumerate(sieieSel):
        yields[sample][sieie] = {}
        for i_chgIso, chgIso in enumerate(chgSel):
            yields[sample][sieie][chgIso] = {}
            for i_pt, pt in enumerate(ptSel):
                yields[sample][sieie][chgIso][pt] = {}
                for i_cat, cat in enumerate(catSel):
                    yields[sample][sieie][chgIso][pt][cat] = {}
                    for i_mode, mode in enumerate(modes):
                        yields[sample][sieie][chgIso][pt][cat][mode] = 0

for sample in allSamples:
    res["sample"] = sample
    for i_sieie, sieie in enumerate(sieieSel):
        res["sieie"] = sieie
        for i_chgIso, chgIso in enumerate(chgSel):
            res["chgIso"] = chgIso
#            res["selection"] = args.selection

#            if chgIso == "lowChgIso" and sieie == "lowSieie":
#                res["sieie"] = "all"
#                res["chgIso"] = "all"
 #               res["selection"] = args.selection.replace("NoChgIsoNoSieiePhoton","nPhoton1p")

            for i_pt, pt in enumerate(ptSel):
                res["ptBin"] = pt
                for i_cat, cat in enumerate(catSel):
                    res["cat"] = cat
                    for i_mode, mode in enumerate(modes):
                        res["mode"] = mode

                        if not args.noData and (sample == "data") and cat != noCat_sel:
                            yields[sample][sieie][chgIso][pt][cat][mode] = -1
                            continue

                        # do not unblind 17 and 18
                        if not args.noData and (sample == "data") and cat == noCat_sel and hadFakeSel and sieie == "all" and chgIso == "all" and args.year != 2016:
                            yields[sample][sieie][chgIso][pt][cat][mode] = -1
                            continue

                        # do not unblind 17 and 18
                        if not args.noData and (sample == "data") and cat == noCat_sel and ("nLepTight1-nLepVeto1-nJet4p-nBTag1p-nPhoton1p" in args.selection or "nLepTight1-nLepVeto1-nJet3-nBTag1p-nPhoton1p" in args.selection) and args.year != 2016:
                            yields[sample][sieie][chgIso][pt][cat][mode] = -1
                            continue

                        if not yield_dirDB.contains( frozenset(res.items()) ):
                            print res
                            print("Yield for sample %s and selection %s and year %i and mode %s and cat %s and pt bin %s and sieie bin %s and chgIso bin %s not cached!"%(sample, args.selection, args.year, args.mode, cat, pt, sieie, chgIso))
                            if args.runOnNonValid:
                                yields[sample][sieie][chgIso][pt][cat][mode] = -1
                                continue
                            sys.exit(0)

                        yields[sample][sieie][chgIso][pt][cat][mode] = int(round(float(yield_dirDB.get( frozenset(res.items()) ))))
                        if "DY" in sample and addDYSF:
                            yields[sample][sieie][chgIso][pt][cat][mode] *= default_DYSF
                        if "2" in cat and addMisIDSF:
                            diff = yields[sample][sieie][chgIso][pt][cat][mode] * (default_misIDSF - 1)
                            yields[sample][sieie][chgIso][pt][cat][mode]   += diff
                            yields[sample][sieie][chgIso][pt]["all"][mode] += diff
                            yields["MC"][sieie][chgIso][pt]["all"][mode]   += diff

                        if args.removeNegative and yields[sample][sieie][chgIso][pt][cat][mode] < 0: yields[sample][sieie][chgIso][pt][cat][mode] = 0 #could be for QCD estimation or negative weights
                        if sample != "data":
                            yields["MC"][sieie][chgIso][pt][cat][mode] += yields[sample][sieie][chgIso][pt][cat][mode]
                            if args.removeNegative and yields["MC"][sieie][chgIso][pt][cat][mode] < 0: yields["MC"][sieie][chgIso][pt][cat][mode] = 0 #could be for QCD estimation or negative weights

def printHadFakeYieldTable():

    with open("logs/%i_%s-%s.log"%(args.year,selDir,args.mode), "w") as f:
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
                f.write("\\multicolumn{21}{c}{%s}\\\\ \n"%( ", ".join( selDir.split("-") + [args.mode] ) ) )
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
                f.write("%s & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i \\\\ \n" %tuple( [s.replace("_","\_")] + [ int(yields[s][sieie][chgIso][pt][cat][mode]) for mode, pt, sieie, chgIso, cat in regions]) )
                f.write("\\hline\n")
            f.write("\\hline\n")
            f.write("MC total & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i \\\\ \n" %tuple( [int(yields["MC"][sieie][chgIso][pt][cat][mode]) for mode, pt, sieie, chgIso, cat in regions] ))
            f.write("\\hline\n")
            if not args.noData:
                f.write("data total & \\textbf{%i} & \\multicolumn{4}{c||}{} & \\textbf{%i} & \\multicolumn{4}{c||}{} & \\textbf{%i} & \\multicolumn{4}{c||}{} & \\textbf{%i} & \\multicolumn{4}{c}{} \\\\ \n" %tuple( [int(yields["data"][sieie][chgIso][pt][cat][mode]) for mode, pt, sieie, chgIso, cat in regions if cat == "all"] ))
                f.write("\\hline\n")
                f.write("data/MC    & \\textbf{%.2f} & \\multicolumn{4}{c||}{} & \\textbf{%.2f} & \\multicolumn{4}{c||}{} & \\textbf{%.2f} & \\multicolumn{4}{c||}{} & \\textbf{%.2f} & \\multicolumn{4}{c}{} \\\\ \n" %tuple( [float(yields["data"][sieie][chgIso][pt][cat][mode])/float(yields["MC"][sieie][chgIso][pt][cat][mode]) if float(yields["MC"][sieie][chgIso][pt][cat][mode]) > 0 else 1. for mode, pt, sieie, chgIso, cat in regions if cat == "all"] ))
                f.write("\\hline\n")
            f.write("\\hline\n")
    
            if highPT == -1:
                f.write("\\multicolumn{21}{c}{}\\\\ \n")
                f.write("\\multicolumn{1}{c}{} & \\multicolumn{5}{c}{$\gamma$ = genuine photons} & \\multicolumn{5}{c}{had $\gamma$ = hadronic photons} & \\multicolumn{5}{c}{misID e = misID electrons} & \\multicolumn{5}{c}{fake = hadronic fakes} \\\\ \n")


            f.write("\\end{tabular}\n")
            f.write("}\n\n") #resizebox

        f.write("\\end{table}\n\n")
        f.write("\\end{frame}\n\n\n\n")




def printYieldTable():

    with open("logs/%i_%s-%s.log"%(args.year,selDir,args.mode), "w") as f:
    
        if args.mode in ["e", "all"]:
            f.write("\\begin{frame}\n")
            f.write("\\frametitle{Yields - %s}\n\n"%args.label)

        f.write("\\begin{table}\n")
        f.write("\\centering\n")

        f.write("\\resizebox{0.9\\textwidth}{!}{\n")
        f.write("\\begin{tabular}{c||c||c|c|c|c||c||c|c|c|c||c||c|c|c|c||c||c|c|c|c}\n")
#        f.write("\\begin{tabular}{c||c||c|c|c|c||c||c|c|c|c||c||c|c|c|c}\n")

        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("\\multicolumn{21}{c}{%s}\\\\ \n"%( ", ".join( selDir.split("-") + [args.mode] ) ) )
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
            f.write("%s & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i \\\\ \n" %tuple( [s.replace("_","\_")] + [ int(yields[s][sieie][chgIso][pt][cat][mode]) for mode, pt, sieie, chgIso, cat in regions ]) )
            f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("MC total & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i \\\\ \n" %tuple( [int(yields["MC"][sieie][chgIso][pt][cat][mode]) for mode, pt, sieie, chgIso, cat in regions] ))
        f.write("\\hline\n")
        if not args.noData:
            f.write("data total & \\textbf{%i} & \\multicolumn{4}{c||}{} & \\textbf{%i} & \\multicolumn{4}{c||}{} & \\textbf{%i} & \\multicolumn{4}{c||}{} & \\textbf{%i} & \\multicolumn{4}{c}{} \\\\ \n" %tuple( [ int(yields["data"][sieie][chgIso][pt][cat][mode]) for mode, pt, sieie, chgIso, cat in regions if cat=="all"] ))
            f.write("\\hline\n")
            f.write("data/MC    & \\textbf{%.2f} & \\multicolumn{4}{c||}{} & \\textbf{%.2f} & \\multicolumn{4}{c||}{} & \\textbf{%.2f} & \\multicolumn{4}{c||}{} & \\textbf{%.2f} & \\multicolumn{4}{c}{} \\\\ \n" %tuple( [float(yields["data"][sieie][chgIso][pt][cat][mode])/float(yields["MC"][sieie][chgIso][pt][cat][mode]) if float(yields["MC"][sieie][chgIso][pt][cat][mode]) > 0 else 1. for mode, pt, sieie, chgIso, cat in regions if cat == "all"] ))
            f.write("\\hline\n")
        f.write("\\hline\n")
    
        f.write("\\multicolumn{21}{c}{}\\\\ \n")
        f.write("\\multicolumn{1}{c}{} & \\multicolumn{5}{c}{$\gamma$ = genuine photons} & \\multicolumn{5}{c}{had $\gamma$ = hadronic photons} & \\multicolumn{5}{c}{misID e = misID electrons} & \\multicolumn{5}{c}{fake = hadronic fakes} \\\\ \n")


        f.write("\\end{tabular}\n")
        f.write("}\n\n") #resizebox

        f.write("\\end{table}\n\n")
        if args.mode in ["mu", "all"]:
            f.write("\\end{frame}\n")
        f.write("\n\n\n")



def printNoPhotonYieldTable():

    with open("logs/%i_%s.log"%(args.year,selDir), "w") as f:
    
        if args.mode in ["e", "all"]:
            f.write("\\begin{frame}\n")
            f.write("\\frametitle{Yields - %s}\n\n"%args.label)

        f.write("\\begin{table}\n")
        f.write("\\centering\n")

        f.write("\\resizebox{0.9\\textwidth}{!}{\n")
#        f.write("\\begin{tabular}{c||c||c|c|c|c||c||c|c|c|c||c||c|c|c|c||c||c|c|c|c}\n")
        f.write("\\begin{tabular}{c||c||c|c|c|c||c||c|c|c|c||c||c|c|c|c}\n")

        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("\\multicolumn{16}{c}{%s}\\\\ \n"%( ", ".join( selDir.split("-") ) ) )
        f.write("\\hline\n")
        f.write("\\multicolumn{16}{c}{%i: $\\mathcal{L}=%s$ fb$^{-1}$}\\\\ \n"%(args.year, "{:.2f}".format(lumi_scale)))
        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("\\multicolumn{16}{c}{}\\\\ \n")

        f.write("\\hline\n")
        f.write("\\hline\n")
        if "nLepTight2" in args.selection:
            f.write("Sample  & \\multicolumn{5}{c||}{ SF (ee/$\\mu\\mu$) channel } & \\multicolumn{5}{c||}{ee channel} & \\multicolumn{5}{c}{$\\mu\\mu$ channel}\\\\ \n")
        else:
            f.write("Sample  & \\multicolumn{5}{c||}{ e/$\\mu$ channel } & \\multicolumn{5}{c||}{e channel} & \\multicolumn{5}{c}{$\\mu$ channel}\\\\ \n")
        f.write("\\hline\n")
        f.write("        & \\textbf{events} & $\gamma$ & had $\gamma$ & misID e & fake & \\textbf{events} & $\gamma$ & had $\gamma$ & misID e & fake & \\textbf{events} & $\gamma$ & had $\gamma$ & misID e & fake \\\\ \n")
        f.write("\\hline\n")
        f.write("\\hline\n")
        for s in mc:
            f.write("%s & \\textbf{%i} & 0 & 0 & 0 & 0 & \\textbf{%i} & 0 & 0 & 0 & 0 & \\textbf{%i} & 0 & 0 & 0 & 0 \\\\ \n" %tuple( [s.replace("_","\_")] + [ int(yields[s][sieie][chgIso][pt][cat][mode]) for mode, pt, sieie, chgIso, cat in regions ]) )
            f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("MC total & \\textbf{%i} & 0 & 0 & 0 & 0 & \\textbf{%i} & 0 & 0 & 0 & 0 & \\textbf{%i} & 0 & 0 & 0 & 0 \\\\ \n" %tuple( [int(yields["MC"][sieie][chgIso][pt][cat][mode]) for mode, pt, sieie, chgIso, cat in regions] ))
        f.write("\\hline\n")
        if not args.noData:
            f.write("data total & \\textbf{%i} & \\multicolumn{4}{c||}{} & \\textbf{%i} & \\multicolumn{4}{c||}{} & \\textbf{%i} & \\multicolumn{4}{c}{} \\\\ \n" %tuple( [ int(yields["data"][sieie][chgIso][pt][cat][mode]) for mode, pt, sieie, chgIso, cat in regions if cat=="all"] ))
            f.write("\\hline\n")
            f.write("data/MC    & \\textbf{%.2f} & \\multicolumn{4}{c||}{} & \\textbf{%.2f} & \\multicolumn{4}{c||}{} & \\textbf{%.2f} & \\multicolumn{4}{c}{} \\\\ \n" %tuple( [float(yields["data"][sieie][chgIso][pt][cat][mode])/float(yields["MC"][sieie][chgIso][pt][cat][mode]) if float(yields["MC"][sieie][chgIso][pt][cat][mode]) > 0 else 1. for mode, pt, sieie, chgIso, cat in regions if cat == "all"] ))
            f.write("\\hline\n")
        f.write("\\hline\n")
    
#        f.write("\\multicolumn{16}{c}{}\\\\ \n")

        f.write("\\end{tabular}\n")
        f.write("}\n\n") #resizebox

        f.write("\\end{table}\n\n")
        if args.mode in ["mu", "all"]:
            f.write("\\end{frame}\n")
        f.write("\n\n\n")



if hadFakeSel:
    printHadFakeYieldTable()
elif noPhotonSel:
    printNoPhotonYieldTable()
else:
    printYieldTable()
