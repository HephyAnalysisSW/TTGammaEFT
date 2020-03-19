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
from TTGammaEFT.Tools.TriggerSelector    import TriggerSelector

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
argParser.add_argument('--noData',             action='store_true', default=False,                                                     help='also plot data?')
argParser.add_argument('--signal',             action='store',      default=None,   nargs='?', choices=[None],                         help="Add signal to plot")
argParser.add_argument('--year',               action='store',      default=None,   type=int,  choices=[2016,2017,2018],               help="which year?")
argParser.add_argument('--onlyTTG',            action='store_true', default=False,                                                     help="Plot only ttG")
argParser.add_argument('--normalize',          action='store_true', default=False,                                                     help="Normalize yields" )
args = argParser.parse_args()

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)


addQCD = args.year == 2016

os.environ["gammaSkim"]="True" if "hoton" in args.selection or "pTG" in args.selection else "False"
if "dilep" in args.selection:
    if args.year == 2016:
        from TTGammaEFT.Samples.nanoTuples_Summer16_private_postProcessed      import *
        if not args.noData:
            from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_postProcessed import *

    elif args.year == 2017:
        from TTGammaEFT.Samples.nanoTuples_Fall17_private_postProcessed        import *
        if not args.noData:
            from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_postProcessed import *

    elif args.year == 2018:
        from TTGammaEFT.Samples.nanoTuples_Autumn18_private_postProcessed      import *
        if not args.noData:
            from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_postProcessed import *

elif "nLepTight1" in args.selection:
    os.environ["gammaSkim"]="True" if os.environ["gammaSkim"] == "True" and not addQCD else "False"
    if args.year == 2016:
        from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed      import *
        if not args.noData:
            from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import *

    elif args.year == 2017:
        from TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed        import *
        if not args.noData:
            from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import *

    elif args.year == 2018:
        from TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed      import *
        if not args.noData:
            from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import *



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
# Sequence
sequence = []

# Sample definition
if "dilep" in args.selection:
    if args.year == 2016:
            mc = [ TTG_16, DY_LO_16, TT_pow_16, singleTop_16, ZG_16, other_16 ]
    elif args.year == 2017:
            mc = [ TTG_17, DY_LO_17, TT_pow_17, singleTop_17, ZG_17, other_17 ]
    elif args.year == 2018:
            mc = [ TTG_18, DY_LO_18, TT_pow_18, singleTop_18, ZG_18, other_18 ]

    weightString   = "reweightTrigger*reweightL1Prefire*reweightPU*reweightLepton2lSF*reweightLeptonTracking2lSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF"

elif "nLepTight1" in args.selection:
    #print "selection"
    if args.year == 2016:
        mc = [ TTG_16, TT_pow_16, DY_LO_16, singleTop_16, WJets_16, TG_16, WG_NLO_16, ZG_16, other_16 ]
        if addQCD:
            qcd   = QCD_16
            gjets = GJets_16
    elif args.year == 2017:
        mc = [ TTG_17, TT_pow_17, DY_LO_17, singleTop_17, WJets_17, TG_17, WG_NLO_17, ZG_17, other_17 ]
        if addQCD:
            qcd   = QCD_17
            gjets = GJets_17
    elif args.year == 2018:
        mc = [ TTG_18, TT_pow_18, DY_LO_18, singleTop_18, WJets_18, TG_18, WG_NLO_18, ZG_18, other_18 ]
        if addQCD:
            qcd   = QCD_18
            gjets = GJets_18

    weightString   = "reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF"


if args.noData:
    if args.year == 2016:   lumi_scale = 35.92
    elif args.year == 2017: lumi_scale = 41.53
    elif args.year == 2018: lumi_scale = 59.74
    stack = Stack( mc )
else:
    if args.year == 2016:   data_sample = Run2016
    elif args.year == 2017: data_sample = Run2017
    elif args.year == 2018: data_sample = Run2018
    data_sample.texName        = "data (legacy)"
    data_sample.name           = "data"
    data_sample.read_variables = [ "event/I", "run/I" ]
    data_sample.scale          = 1
    lumi_scale                 = data_sample.lumi * 0.001
    stack                      = Stack( mc, data_sample )

stack.extend( [ [s] for s in signals ] )

for sample in mc + signals:
    sample.read_variables = read_variables_MC
    sample.scale          = lumi_scale
    sample.style          = styles.fillStyle( sample.color )

if args.small:
    for sample in stack.samples:
        sample.normalization=1.
        sample.reduceFiles( factor=15 )
        sample.scale /= sample.normalization

filterCutData = getFilterCut( args.year, isData=True, skipBadChargedCandidate=True )
filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )
tr            = TriggerSelector( args.year, singleLepton=args.selection.count("nLepTight1") )
triggerCutMc  = tr.getSelection( "MC" )

# Loop over channels
#allModes = [ 'mumu', 'mue', 'ee', 'SF', 'all' ]
#allModes = [ 'mue', 'SF' ]

lowSieie   = "PhotonNoChgIsoNoSieie0_sieie<0.01015"
highSieie  = "PhotonNoChgIsoNoSieie0_sieie>0.011"

lowChgIso   = "PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt<1.141"
highChgIso  = "PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt>1.141"

lowPT  = "PhotonNoChgIsoNoSieie0_pt>=20&&PhotonNoChgIsoNoSieie0_pt<120"
medPT  = "PhotonNoChgIsoNoSieie0_pt>=120&&PhotonNoChgIsoNoSieie0_pt<220"
highPT = "PhotonNoChgIsoNoSieie0_pt>=220"

noCat_sel = "(1)"
cat_sel0  = "PhotonNoChgIsoNoSieie0_photonCat==0"
cat_sel1  = "PhotonNoChgIsoNoSieie0_photonCat==1"
cat_sel2  = "PhotonNoChgIsoNoSieie0_photonCat==2"
cat_sel3  = "PhotonNoChgIsoNoSieie0_photonCat==3"

allCats  = [ noCat_sel, cat_sel0, cat_sel1, cat_sel2, cat_sel3 ]
allModes = [
            '&&'.join([lowSieie,lowChgIso,lowPT]),
            '&&'.join([lowSieie,lowChgIso,medPT]),
            '&&'.join([lowSieie,lowChgIso,highPT]),
            '&&'.join([highSieie,lowChgIso,lowPT]),
            '&&'.join([highSieie,lowChgIso,medPT]),
            '&&'.join([highSieie,lowChgIso,highPT]),
            '&&'.join([lowSieie,highChgIso,lowPT]),
            '&&'.join([lowSieie,highChgIso,medPT]),
            '&&'.join([lowSieie,highChgIso,highPT]),
            '&&'.join([highSieie,highChgIso,lowPT]),
            '&&'.join([highSieie,highChgIso,medPT]),
            '&&'.join([highSieie,highChgIso,highPT]),
]

regions = { 
            "20To120":  [ mode for mode in allModes if lowPT  in mode],
            "120To220": [ mode for mode in allModes if medPT  in mode],
            "220To-1":  [ mode for mode in allModes if highPT in mode],
}

yields = {}
qcdyield    = {}
for i_mode, mode in enumerate(allModes):
    yields[mode] = {}
    for i_cat, cat in enumerate(allCats):
        yields[mode][cat] = {}

def calcQCD( mode ):

    #print("Calculating QCD yield for mode %s"%mode)
    qcdSelection       = "-".join( [ item.replace("nLepTight1", "nInvLepTight1") if not "nBTag" in item else "nBTag0" for item in args.selection.replace("nLepVeto1-","").split("-") ] )
    preSelectionCR     = "&&".join( [ cutInterpreter.cutString( qcdSelection ), "weight<15", filterCutMc, mode, noCat_sel, triggerCutMc, "overlapRemoval==1"  ] )
    preSelectionCRData = "&&".join( [ cutInterpreter.cutString( qcdSelection ), filterCutData, mode, noCat_sel ] )

    yield_QCD_CR  = qcd.getYieldFromDraw(   selectionString=preSelectionCR, weightString="weight*%f*%s"%(lumi_scale,weightString) )['val']
    yield_QCD_CR += gjets.getYieldFromDraw( selectionString=preSelectionCR, weightString="weight*%f*%s"%(lumi_scale,weightString) )['val']

    datCR = data_sample.getYieldFromDraw( selectionString=preSelectionCRData, weightString="weight" )['val']
    #print("Got QCD data yield of %f for mode %s"%(datCR, mode))
    mcNoQCDTotal = 0
    for i_s, s in enumerate(mc):
        mcNoQCDTotal += s.getYieldFromDraw( selectionString=preSelectionCR, weightString="weight*%f*%s"%(s.scale,weightString) )['val']
        #print("Got QCD mc yield for sample %s of %f for mode %s"%(s.name, datCR, mode))
#    qcdyield[mode] = int(round(datCR - mcNoQCDTotal))
    #print("Got QCD total yield of %f for mode %s"%(qcdyield[mode], mode))

    preSelectionSR = "&&".join( [ cutInterpreter.cutString( args.selection ), "weight<15", filterCutMc, mode, noCat_sel, triggerCutMc, "overlapRemoval==1"  ] )
    yield_QCD_SR   = qcd.getYieldFromDraw(   selectionString=preSelectionSR, weightString="weight*%f*%s"%(lumi_scale,weightString) )['val']
    yield_QCD_SR  += gjets.getYieldFromDraw( selectionString=preSelectionSR, weightString="weight*%f*%s"%(lumi_scale,weightString) )['val']
    transFacQCD    = yield_QCD_SR / yield_QCD_CR if yield_QCD_CR != 0 else 0

    yields[mode][noCat_sel]["QCD"] = int(round( (datCR - mcNoQCDTotal) * transFacQCD ))

    for cat in allCats:
        if cat == noCat_sel: continue
        if yields[mode][noCat_sel]["QCD"] > 0:

            preSelectionSR = "&&".join( [ cutInterpreter.cutString( args.selection ), "weight<15", filterCutMc, mode, cat, triggerCutMc, "overlapRemoval==1"  ] )
            yield_QCD_SR_cat  = qcd.getYieldFromDraw(   selectionString=preSelectionSR, weightString="weight*%f*%s"%(lumi_scale,weightString) )['val']
            yield_QCD_SR_cat += gjets.getYieldFromDraw( selectionString=preSelectionSR, weightString="weight*%f*%s"%(lumi_scale,weightString) )['val']
            transFacQCD   = yield_QCD_SR_cat / yield_QCD_SR if yield_QCD_SR != 0 else 0

            yields[mode][cat]["QCD"] = yields[mode][noCat_sel]["QCD"] * transFacQCD
        else:
            yields[mode][cat]["QCD"] = 0


def calcData( mode ):
    if args.year != 2016 and lowSieie in mode and lowChgIso in mode:
        yields[mode][noCat_sel][data_sample.name] = -1
        return
    #print("Calculating data yield for mode %s"%mode)
    preSelectionSRData = "&&".join( [ cutInterpreter.cutString( args.selection ), filterCutData, mode, noCat_sel] )
    if "dilep" in args.selection:
        preSelectionSRData = preSelectionSRData.replace("nLeptonVetoIsoCorr","nLeptonVeto")
    yields[mode][noCat_sel][data_sample.name] = int(round(data_sample.getYieldFromDraw( selectionString=preSelectionSRData, weightString="weight" )['val']))
    #print("Got data yield of %f for mode %s"%(yields[mode][noCat_sel][data_sample.name], mode))

def calculation( arg ):

    mode, cat = arg

#    print("Calculating yield for mode %s and category %s"%(mode,cat))

    yields[mode][cat]["MC"] = 0

    preSelectionSR = "&&".join( [ cutInterpreter.cutString( args.selection ), "weight<15", filterCutMc, mode, cat, triggerCutMc, "overlapRemoval==1"  ] )
    if "dilep" in args.selection:
        preSelectionSR = preSelectionSR.replace("nLeptonVetoIsoCorr","nLeptonVeto")

    for i_s, s in enumerate(mc):
#        if cat != noCat_sel and yields[mode][noCat_sel][s.name] < 0.5:
#            yields[mode][cat][s.name] = 0
#            continue
        yields[mode][cat][s.name] = int(round(s.getYieldFromDraw( selectionString=preSelectionSR, weightString="weight*%f*%s"%(s.scale,weightString) )['val']))
        yields[mode][cat]["MC"]  += yields[mode][cat][s.name]
#        print("Got yield of %f for sample %s and mode %s and category %s"%(yields[mode][cat][s.name],s.name,mode,cat))


def printTable():
    allSamples = [data_sample] + mc if not args.noData else mc

    with open("logs/%i_%s.log"%(args.year,args.selection), "w") as f:
        f.write("\\begin{table}\n")
        f.write("\\centering\n")

        for lowPT, highPT in [ (20,120), (120,220), (220,-1) ]:
            f.write("\\resizebox{0.8\\textwidth}{!}{\n")
            f.write("\\begin{tabular}{c||c||c|c|c|c||c||c|c|c|c||c||c|c|c|c||c||c|c|c|c}\n")

            if lowPT == 20:
                f.write("\\hline\n")
                f.write("\\hline\n")
                f.write("\\multicolumn{21}{c}{%s}\\\\ \n"%( ", ".join( args.selection.split("-") ) ) )
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
#                f.write("%s & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i \\\\ \n" %(s.name) + (int(yields[mode][cat][s.name] for mode in regions["%iTo%i"%(lowPT, highPT)] for cat in allCats) ))
                f.write("%s & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i \\\\ \n" %tuple( [s.name.replace("_","\_")] + [ int(yields[mode][cat][s.name]) for mode in regions["%iTo%i"%(lowPT, highPT)] for cat in allCats]) )
                f.write("\\hline\n")
            if "nLepTight1" in args.selection and not args.noData and not args.onlyTTG and addQCD:
                f.write("QCD & \\textbf{%i} & - & - & - & - & \\textbf{%i} & - & - & - & - & \\textbf{%i} & - & - & - & - & \\textbf{%i} & - & - & - & - \\\\ \n" %tuple( [ int(yields[mode][noCat_sel]["QCD"]) for mode in regions["%iTo%i"%(lowPT, highPT)] ]) )
                f.write("\\hline\n")
            f.write("\\hline\n")
            f.write("MC total & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i & \\textbf{%i} & %i & %i & %i & %i \\\\ \n" %tuple( [int(yields[mode][cat]["MC"]) for mode in regions["%iTo%i"%(lowPT, highPT)] for cat in allCats] ))
            f.write("\\hline\n")
            if not args.noData:
                f.write("data total & \\textbf{%i} & \\multicolumn{4}{c||}{} & \\textbf{%i} & \\multicolumn{4}{c||}{} & \\textbf{%i} & \\multicolumn{4}{c||}{} & \\textbf{%i} & \\multicolumn{4}{c}{} \\\\ \n" %tuple( [int(yields[mode][noCat_sel][data_sample.name]) for mode in regions["%iTo%i"%(lowPT, highPT)]] ))
                f.write("\\hline\n")
            f.write("\\hline\n")
    
            if highPT == -1:
                f.write("\\multicolumn{21}{c}{}\\\\ \n")
                f.write("\\multicolumn{1}{c}{} & \\multicolumn{5}{c}{$\gamma$ = genuine photons} & \\multicolumn{5}{c}{had $\gamma$ = hadronic photons} & \\multicolumn{5}{c}{misID e = misID electrons} & \\multicolumn{5}{c}{fake = hadronic fakes} \\\\ \n")


            f.write("\\end{tabular}\n")
            f.write("}\n\n") #resizebox

        f.write("\\end{table}\n")



# Multiprocessing
input = [ (mode, cat) for mode in allModes for cat in allCats ]
#from multiprocessing import Pool
#if "nLepTight1" in args.selection and not args.noData and not args.onlyTTG:
#    pool = Pool( processes=6 )
#    pool.map( calcQCD,  allModes )
#    pool.close()

#print qcdyield
#exit()
#if not args.noData:
#    pool = Pool( processes=6 )
#    pool.map( calcData, allModes )
#    pool.close()
#pool = Pool( processes=1 )
#pool.map( calculation, input )
#pool.close()

#print yields

if "nLepTight1" in args.selection and not args.noData and not args.onlyTTG and addQCD:
    for mode in allModes:
        calcQCD( mode )
if not args.noData:
    for mode in allModes:
        calcData( mode )
for arg in input:
    calculation( arg )
printTable()
