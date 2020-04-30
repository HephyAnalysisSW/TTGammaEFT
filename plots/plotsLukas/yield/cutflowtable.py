#!/usr/bin/env python
''' Analysis script for standard plots
'''

# Standard imports
import ROOT, os, imp, sys, copy
#ROOT.gROOT.SetBatch(True)
import itertools
from math                                import isnan, ceil, pi

# RootTools
from RootTools.core.standard             import *

# Internal Imports
from TTGammaEFT.Tools.user               import plot_directory
from TTGammaEFT.Tools.cutInterpreter     import cutInterpreter
from TTGammaEFT.Tools.TriggerSelector_postprocessed    import TriggerSelector

from Analysis.Tools.metFilters           import getFilterCut
from Analysis.Tools.u_float              import u_float

# Default Parameter
loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                  help="Log level for logging")
argParser.add_argument('--selection',          action='store',      default='dilepOS-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1p')
argParser.add_argument('--small',              action='store_true',                                                                    help='Run only on a small subset of the data?', )
argParser.add_argument('--useCorrectedIsoVeto', action='store_true',                                                                    help='Use the leptonVeto with corrected Iso values?', )
#argParser.add_argument('--year',               action='store',      default=None,   type=int,  choices=[2016,2017,2018],               help="which year?")
args = argParser.parse_args()

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

#os.environ["gammaSkim"]="True" if "hoton" in args.selection or "pTG" in args.selection else "False"
#from TTGammaEFT.Samples.nanoTuples_Sync_semilep_postProcessed      import TTG_sync_16 as TTG_16
from TTGammaEFT.Samples.nanoTuples_Sync_semilep_postProcessed      import TT_sync_16  as TTG_16
#from TTGammaEFT.Samples.nanoTuples_Summer16_private_incl_postProcessed      import TTG_NoFullyHad_fnal_16 as TTG_16
#from TTGammaEFT.Samples.nanoTuples_Fall17_private_incl_postProcessed        import TTG_NoFullyHad_fnal_17 as TTG_17
#from TTGammaEFT.Samples.nanoTuples_Autumn18_private_incl_postProcessed      import TTG_NoFullyHad_fnal_18 as TTG_18
#from TTGammaEFT.Samples.nanoTuples_Summer16_private_incl_postProcessed      import TTG_NoFullyHad_priv_16 as TTG_16
#from TTGammaEFT.Samples.nanoTuples_Fall17_private_incl_postProcessed        import TTG_NoFullyHad_priv_17 as TTG_17
#from TTGammaEFT.Samples.nanoTuples_Autumn18_private_incl_postProcessed      import TTG_NoFullyHad_priv_18 as TTG_18

# Read variables and sequences
read_variables  = ["weight/F", 
                   "nJetGood/I", "nBTagGood/I",
                   "nLeptonGood/I", "nLeptonTight/I", "nLeptonVeto/I", "nElectronGood/I", "nMuonGood/I",
                   "nPhotonGood/I",
                   "mll/F", "mllgamma/F",
                  ]
if "nLepTight1" in args.selection:
    read_variables += ["nLeptonVetoIsoCorr/I", "nInvLepTight1/I"]

read_variables_MC = ["isTTGamma/I", "isZWGamma/I", "isTGamma/I", "overlapRemoval/I",
                     "reweightPU/F", "reweightPUDown/F", "reweightPUUp/F", "reweightPUVDown/F", "reweightPUVUp/F",
                     "reweightLeptonTightSF/F", "reweightLeptonTightSFUp/F", "reweightLeptonTightSFDown/F",
                     "reweightLeptonTrackingTightSF/F",
                     "reweightLepton2lSF/F", "reweightLepton2lSFUp/F", "reweightLepton2lSFDown/F",
                     "reweightLeptonTracking2lSF/F",
                     "reweightTrigger/F", "reweightTriggerUp/F", "reweightTriggerDown/F",
                     "reweightInvTrigger/F", "reweightInvTriggerUp/F", "reweightInvTriggerDown/F",
                     "reweightPhotonSF/F", "reweightPhotonSFUp/F", "reweightPhotonSFDown/F",
                     "reweightPhotonElectronVetoSF/F",
                     "reweightBTag_SF/F", "reweightBTag_SF_b_Down/F", "reweightBTag_SF_b_Up/F", "reweightBTag_SF_l_Down/F", "reweightBTag_SF_l_Up/F",
                     'reweightL1Prefire/F', 'reweightL1PrefireUp/F', 'reweightL1PrefireDown/F',
                    ]

weightString   = "1" #"%f*weight*reweightL1Prefire*reweightPU*reweightLepton2lSF*reweightLeptonTracking2lSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF"%lumi_scale

ptSel     = ['all', 'lowPT', 'medPT', 'highPT']
allYears  = ['2016', '2017', '2018']
pthadSel  = ['lowhadPT', 'medhadPT', 'highhadPT']
catSel    = ['photoncat0', 'photoncat1', 'photoncat2', 'photoncat3']
hadcatSel = ['photonhadcat0', 'photonhadcat1', 'photonhadcat2', 'photonhadcat3']
noCat_sel = "all"

allCats     = [noCat_sel] + catSel
allModes    = allYears #ptSel

args.selection = "triggerCut-METfilter-" + args.selection + "-overlapRemoval"
allSel = ["entries"] + [ "-".join( args.selection.split("-")[:i+1] ) for i, _ in enumerate(args.selection.split("-")) ]
print allSel

yields = {}
for i_mode, mode in enumerate(allModes):
    yields[mode] = {}
    for i_cat, cat in enumerate(allCats):
        yields[mode][cat] = {}
        yields[mode][cat]["MC"] = 0
        for sel in allSel:
            yields[mode][cat][sel] = 0

def calculation( arg ):

    mode, cat, sel = arg

    TTG = TTG_16
#    if   mode == "2016": TTG = TTG_16
#    elif mode == "2017": TTG = TTG_17
#    elif mode == "2018": TTG = TTG_18

    triggercut = False
    filtercut  = False
    overlapcut = False

    selCut = sel
    if selCut == "entries":
        weight = "1"
        selCut = "all"
#    elif selCut == "genweight*lumi":
#        weight = "%f*weight"%lumi_scale
#        selCut = "all"
#    elif selCut == "genweight*lumi*SF":
#        weight = weightString
#        selCut = "all"
    else:
        weight = weightString
    if "triggerCut" in selCut:
        selCut = selCut.replace("triggerCut","")
        triggercut = True
    if "METfilter" in selCut:
        selCut = selCut.replace("METfilter","")
        filtercut = True
    if "overlapRemoval" in selCut:
        selCut = selCut.replace("overlapRemoval","")
        overlapcut = True
    selCut = "-".join( [ cut for cut in selCut.split("-") if cut ] )

    if not selCut: selCut = "all"
    #print("Calcuating yield for mode %s and category %s and selection %s"%(mode,cat,sel))

    selCuts = [ cutInterpreter.cutString( "-".join( [ selCut, cat ] ) ) ]

    filterCutMc   = getFilterCut( int(mode), isData=False, skipBadChargedCandidate=True, skipVertexFilter=False )
    tr            = TriggerSelector( int(mode) )
    triggerCutMc  = tr.getSelection()
#    tr            = TriggerSelector( int(mode), singleLepton=True )
#    triggerCutMc  = tr.getSelection( "MC" )

    if triggercut: selCuts += [triggerCutMc]
    if filtercut:  selCuts += [filterCutMc]
    if overlapcut: selCuts += ["overlapRemoval==1"]

    preSelectionSR = "&&".join( selCuts )
#    if not args.useCorrectedIsoVeto: preSelectionSR = preSelectionSR.replace("nLeptonVetoIsoCorr","nLeptonVeto")

    if mode != "2016" or (not "hoton" in selCut and cat != noCat_sel):
        yields[mode][cat][sel] = -1
        return

    print TTG.getEventList( preSelectionSR ).GetN()
    yields[mode][cat][sel] = TTG.getEventList( selectionString=preSelectionSR ).GetN() #int(round(TTG.getYieldFromDraw( selectionString=preSelectionSR, weightString=weight )['val']))
#    yields["incl"][cat][sel] += yields[mode][cat][sel]
    #print("Got yield of %f for selection %s and mode %s and category %s"%(yields[mode][cat][sel],sel,mode,cat))


def printAllYieldTable():

    with open("logs/cutFlow_%s.log"%(args.selection), "w") as f:
    
        f.write("\\begin{frame}\n")
        f.write("\\frametitle{Yields - Cutflow Table FNAL Samples}\n\n")

        if "-mu" in args.selection:
            f.write("\\begin{itemize}\n")
            f.write("\\item Muons\n")
            f.write("\\end{itemize}\n\n")

        elif "-e" in args.selection:
            f.write("\\begin{itemize}\n")
            f.write("\\item Electrons\n")
            f.write("\\end{itemize}\n\n")
        else:
            f.write("\\begin{itemize}\n")
            f.write("\\item Electrons + Muons\n")
            f.write("\\end{itemize}\n\n")


        f.write("\\begin{table}\n")
        f.write("\\centering\n")

        f.write("\\resizebox{0.9\\textwidth}{!}{\n")
#        f.write("\\begin{tabular}{c||c||c|c|c|c||c||c|c|c|c||c||c|c|c|c||c||c|c|c|c}\n")
        f.write("\\begin{tabular}{c||c||c|c|c|c||c||c|c|c|c||c||c|c|c|c}\n")

        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("\\multicolumn{16}{c}{%s}\\\\ \n"%( ", ".join( args.selection.split("-") ) ) )
        f.write("\\hline\n")
        f.write("\\multicolumn{16}{c}{}\\\\ \n")

        f.write("\\hline\n")
        f.write("\\hline\n")
        f.write("Cuts  & \\multicolumn{5}{c||}{2016} & \\multicolumn{5}{c||}{2017} & \\multicolumn{5}{c}{2018}\\\\ \n")
        f.write("\\hline\n")
        f.write("        & \\textbf{entries} & $\gamma$ & had $\gamma$ & misID e & fake & \\textbf{entries} & $\gamma$ & had $\gamma$ & misID e & fake & \\textbf{entries} & $\gamma$ & had $\gamma$ & misID e & fake \\\\ \n")
        f.write("\\hline\n")
        f.write("\\hline\n")
        for i_s, s in enumerate(allSel):
            f.write("\\hline\n")
            f.write("%s & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i \\\\ \n" %tuple( ["+ "+s.split("-")[-1] if i_s > 1 else s.split("-")[-1]] + [int(yields[mode][cat][s]) for mode in allModes for cat in allCats] ))
#        f.write("\\hline\n")
        f.write("\\hline\n")
    
        f.write("\\multicolumn{16}{c}{}\\\\ \n")
        f.write("\\multicolumn{4}{c}{$\gamma$ = genuine photons} & \\multicolumn{4}{c}{had $\gamma$ = hadronic photons} & \\multicolumn{4}{c}{misID e = misID electrons} & \\multicolumn{4}{c}{fake = hadronic fakes} \\\\ \n")


        f.write("\\end{tabular}\n")
        f.write("}\n\n") #resizebox

        f.write("\\end{table}\n\n")
        f.write("\\end{frame}\n")
        f.write("\n\n\n")



input = [ (mode, cat, sel) for mode in allModes for cat in allCats for sel in allSel ]

for inp in input:
    calculation( inp )

printAllYieldTable()
