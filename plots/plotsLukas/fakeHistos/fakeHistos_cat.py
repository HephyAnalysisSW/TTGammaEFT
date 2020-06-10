# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy

# RootTools
from RootTools.core.standard           import *

# Analysis
from Analysis.Tools.metFilters         import getFilterCut

# Internal Imports
from TTGammaEFT.Tools.user             import plot_directory, cache_directory
from TTGammaEFT.Tools.cutInterpreter   import cutInterpreter
#from TTGammaEFT.Tools.TriggerSelector  import TriggerSelector

from TTGammaEFT.Analysis.SetupHelpers  import *
from TTGammaEFT.Analysis.Setup         import Setup
from TTGammaEFT.Analysis.EstimatorList import EstimatorList

from TTGammaEFT.Samples.color          import color
from Analysis.Tools.MergingDirDB      import MergingDirDB

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

addSF = False
ptBins  = [0, 45, 65, 80, 100, 120, -1]
etaBins = [0, 1.479, 1.7, 2.1, -1]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                        help="Log level for logging")
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv26_v1",                                             help="plot sub-directory")
argParser.add_argument("--selection",          action="store",      default="WJets2", type=str,                                              help="reco region")
argParser.add_argument("--addCut",             action="store",      default=None, type=str,                                                  help="additional cuts")
argParser.add_argument("--variable",           action="store",      default="LeptonTight0_eta", type=str,                                    help="variable to plot")
argParser.add_argument("--binning",            action="store",      default=[20,-2.4,2.4],  type=float, nargs="*",                           help="binning of plots")
argParser.add_argument("--year",               action="store",      default=2016,   type=int,  choices=[2016,2017,2018],                     help="Which year to plot?")
argParser.add_argument("--mode",               action="store",      default="all",  type=str,  choices=["mu", "e", "all"],                   help="lepton selection")
argParser.add_argument("--small",              action="store_true",                                                                          help="Run only on a small subset of the data?")
argParser.add_argument("--survey",             action="store_true",                                                                          help="all plots in one directory?")
argParser.add_argument("--overwrite",          action="store_true",                                                                          help="overwrite cache?")
args = argParser.parse_args()

args.binning[0] = int(args.binning[0])

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile=None )
logger_rt = logger_rt.get_logger( args.logLevel, logFile=None )

# Text on the plots
def drawObjects( lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    line = (0.65, 0.95, "%3.1f fb{}^{-1} (13 TeV)" % lumi_scale)
    lines = [
      (0.15, 0.95, "CMS #bf{#it{Preliminary}}"),
      line
    ]
    return [tex.DrawLatex(*l) for l in lines]

cache_dir = os.path.join(cache_directory, "drawHistos", str(args.year), args.selection, args.mode)
dirDB = MergingDirDB(cache_dir)
if not dirDB: raise

# Sample definition
os.environ["gammaSkim"]="False" #always false for QCD estimate
if args.year == 2016:
    from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed  import *
    from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import *
    mc          = [ TTG_16, Top_16, DY_LO_16, WJets_16, WG_16, ZG_16, rest_16 ]
    ttg         = TTG_16
    tt          = Top_16
    wjets       = WJets_16
    ttg         = TTG_16
    wg          = WG_16
    other       = rest_16
    data_sample = Run2016
elif args.year == 2017:
    from TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed    import *
    from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import *
    mc          = [ TTG_17, Top_17, DY_LO_17, WJets_17, WG_17, ZG_17, rest_17 ]
    ttg         = TTG_17
    tt          = Top_17
    wjets       = WJets_17
    ttg         = TTG_17
    wg          = WG_17
    other       = rest_17
    data_sample = Run2017
elif args.year == 2018:
    from TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed  import *
    from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import *
    mc          = [ TTG_18, Top_18, DY_LO_18, WJets_18, WG_18, ZG_18, rest_18 ]
    ttg         = TTG_18
    tt          = Top_18
    wjets       = WJets_18
    ttg         = TTG_18
    wg          = WG_18
    other       = rest_18
    data_sample = Run2018

read_variables_MC = ["isTTGamma/I", "isZWGamma/I", "isTGamma/I", "overlapRemoval/I",
                     "reweightPU/F", "reweightPUDown/F", "reweightPUUp/F", "reweightPUVDown/F", "reweightPUVUp/F",
                     "reweightLeptonTightSF/F", "reweightLeptonTightSFUp/F", "reweightLeptonTightSFDown/F",
                     "reweightLeptonTrackingTightSF/F",
                     "reweightTrigger/F", "reweightTriggerUp/F", "reweightTriggerDown/F",
                     "reweightInvIsoTrigger/F", "reweightInvIsoTriggerUp/F", "reweightInvIsoTriggerDown/F",
                     "reweightPhotonSF/F", "reweightPhotonSFUp/F", "reweightPhotonSFDown/F",
                     "reweightPhotonElectronVetoSF/F",
                     "reweightBTag_SF/F", "reweightBTag_SF_b_Down/F", "reweightBTag_SF_b_Up/F", "reweightBTag_SF_l_Down/F", "reweightBTag_SF_l_Up/F",
                     'reweightL1Prefire/F', 'reweightL1PrefireUp/F', 'reweightL1PrefireDown/F',
                    ]
read_variables = [ "weight/F",
                   "mT/F",
                   "mTinv/F",
                 ]

lumi_scale   = data_sample.lumi * 0.001

filterCutData = getFilterCut( args.year, isData=True,  skipBadChargedCandidate=True )
filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )

blinding = []
if args.year != 2016:
    if "lowSieieNoChgIso" in args.addCut:
        blinding += [ cutInterpreter.cutString( "lowSieieHighChgIso" ) ]
    if "lowChgIsoNoSieie" in args.addCut:
        blinding += [ cutInterpreter.cutString( "lowChgIsoHighSieie" ) ]


data_sample.setSelectionString( [filterCutData, "reweightHEM>0"] + blinding )
data_sample.setWeightString( "weight" )
if args.small:           
    data_sample.normalization = 1.
    data_sample.reduceFiles( factor=5 )
    data_sample.setWeightString( "weight*%f"%(1./data_sample.normalization) )

print data_sample.selectionString

for s in mc:
    s.setSelectionString( [ filterCutMc, "overlapRemoval==1" ] )
#    s.setSelectionString( [ filterCutMc, triggerCutMc, "overlapRemoval==1" ] )
    s.read_variables = read_variables_MC
    sampleWeight     = "1"
    if args.small:           
        s.normalization = 1.
        s.reduceFiles( factor=100 )
        sampleWeight = "%f"%(1./s.normalization)

replaceSelection = {
#    "nLeptonVetoIsoCorr": "nLeptonVetoNoIso",
    "nLeptonTight":       "nLeptonTightInvIso",
    "nMuonTight":         "nMuonTightInvIso",
    "nElectronTight":     "nElectronTightInvIso",
    "mLtight0Gamma":      "mLinvtight0Gamma",
    "ltight0GammadPhi":   "linvtight0GammadPhi",
    "ltight0GammadR":     "linvtight0GammadR",
    "nPhotonGood":        "nPhotonGoodInvLepIso",
    "nJetGood":           "nJetGoodInvLepIso",
    "nBTagGood":          "nBTagGoodInvLepIso",
    "mT":                 "mTinv",
    "m3":                 "m3inv",
    "LeptonTight0":       "LeptonTightInvIso0",
    "JetGood0":           "JetGoodInvLepIso0",
    "JetGood1":           "JetGoodInvLepIso1",
    "PhotonNoChgIsoNoSieie0": "PhotonNoChgIsoNoSieieInvLepIso0",
    "ltight0GammaNoSieieNoChgIsodR": "ltight0GammaNoSieieNoChgIsoInvLepIsodR",
}


if len(args.selection.split("-")) == 1 and args.selection in allRegions.keys():
    print( "Plotting region from SetupHelpers: %s"%args.selection )

    setup = Setup( year=args.year, photonSelection=False, checkOnly=False, runOnLxPlus=False ) #photonselection always false for qcd estimate
    setup = setup.sysClone( parameters=allRegions[args.selection]["parameters"] )

    selection = setup.selection( "MC", channel=args.mode, **setup.defaultParameters() )["prefix"]
    selection = cutInterpreter.cutString( selection )
    selection += "&&triggered==1"
    print selection
    if args.addCut:
        selection += "&&" + cutInterpreter.cutString( args.addCut )
    print( "Using selection string: %s"%selection )

    preSelection  = setup.selection("MC",   channel=args.mode, **setup.defaultParameters(update=QCD_updates))["prefix"]
    preSelection  = cutInterpreter.cutString( preSelection )
    preSelection += "&&triggeredInvIso==1"
    if args.addCut:
        addSel = cutInterpreter.cutString( args.addCut )
        for iso, invIso in replaceSelection.iteritems():
            addSel = addSel.replace(iso,invIso)
        preSelection += "&&" + addSel

    print( "Using qcd sideband selection string: %s"%preSelection )

#    if args.mode == "e":
#        preSelection += "&&LeptonTightInvIso0_pfRelIso03_all<0.2"
#    else:
#        preSelection += "&&LeptonTightInvIso0_pfRelIso04_all<0.4"

#    preSelection_EC     = preSelection + "&&abs(LeptonTightInvIso0_eta)>1.479"
#    preSelection_Barrel = preSelection + "&&abs(LeptonTightInvIso0_eta)<=1.479"

else:
    raise Exception("Region not implemented")

if "2" in args.selection and not "2p" in args.selection:
    misIDSF_val = misID2SF_val
elif "3" in args.selection and not "3p" in args.selection:
    misIDSF_val = misID3SF_val
elif "4" in args.selection and not "4p" in args.selection:
    misIDSF_val = misID4SF_val
elif "5" in args.selection:
    misIDSF_val = misID5SF_val
elif "2p" in args.selection:
    misIDSF_val = misID2pSF_val
elif "3p" in args.selection:
    misIDSF_val = misID3pSF_val
elif "4p" in args.selection:
    misIDSF_val = misID4pSF_val

weightString    = "%f*weight*reweightHEM*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF"%lumi_scale
weightStringIL  = "%f*weight*reweightHEM*reweightInvIsoTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSFInvIso*reweightLeptonTrackingTightSFInvIso*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF"%lumi_scale
#weightStringInv = weightStringIL
#weightStringAR  = weightString
weightStringInv = "((%s)+(%s*%f*((nPhotonNoChgIsoNoSieieInvLepIso>0)*(PhotonNoChgIsoNoSieieInvLepIso0_photonCatMagic==2))))"%(weightStringIL,weightStringIL,(misIDSF_val[args.year].val-1))
weightStringAR  = "((%s)+(%s*%f*((nPhotonNoChgIsoNoSieie>0)*(PhotonNoChgIsoNoSieie0_photonCatMagic==2))))"%(weightString,weightString,(misIDSF_val[args.year].val-1))


replaceVariable = {
    "ltight0GammadR":     "linvtight0GammadR",
    "ltight0GammadPhi":   "linvtight0GammadPhi",
    "mT":                 "mTinv",
    "m3":                 "m3inv",
    "ht":                 "htinv",
    "nJetGood":           "nJetGoodInvLepIso",
    "lpTight":            "lpInvTight",
    "mLtight0Gamma":      "mLinvtight0Gamma",
    "JetGood0_eta":   "JetGoodInvLepIso0_eta",
    "JetGood0_pt":        "JetGoodInvLepIso0_pt",
    "JetGood0_phi":   "JetGoodInvLepIso0_phi",
    "JetGood1_eta":   "JetGoodInvLepIso1_eta",
    "JetGood1_pt":        "JetGoodInvLepIso1_pt",
    "JetGood1_phi":   "JetGoodInvLepIso1_phi",

    "LeptonTight0_pfRelIso03_all":   "LeptonTightInvIso0_pfRelIso03_all",
    "LeptonTight0_phi":   "LeptonTightInvIso0_phi",
    "LeptonTight0_eta":   "LeptonTightInvIso0_eta",
    "LeptonTight0_pt":    "LeptonTightInvIso0_pt",

    "PhotonGood0_phi":   "PhotonGoodInvLepIso0_phi",
    "PhotonGood0_eta":   "PhotonGoodInvLepIso0_eta",
    "PhotonGood0_pt":    "PhotonGoodInvLepIso0_pt",

    "PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt": "PhotonNoChgIsoNoSieieInvLepIso0_pfRelIso03_chg*PhotonNoChgIsoNoSieieInvLepIso0_pt",
    "PhotonNoChgIsoNoSieie0_pfRelIso03_chg": "PhotonNoChgIsoNoSieieInvLepIso0_pfRelIso03_chg",
    "PhotonNoChgIsoNoSieie0_sieie":          "PhotonNoChgIsoNoSieieInvLepIso0_sieie",

    "LeptonTight0_sip3d":    "LeptonTightInvIso0_sip3d",
    "LeptonTight0_dr03EcalRecHitSumEt":    "LeptonTightInvIso0_dr03EcalRecHitSumEt",
    "LeptonTight0_dr03HcalDepth1TowerSumEt":    "LeptonTightInvIso0_dr03HcalDepth1TowerSumEt",
    "LeptonTight0_dr03TkSumPt":    "LeptonTightInvIso0_dr03TkSumPt",
    "LeptonTight0_ip3d":    "LeptonTightInvIso0_ip3d",
    "LeptonTight0_r9":    "LeptonTightInvIso0_r9",
    "LeptonTight0_eInvMinusPInv":    "LeptonTightInvIso0_eInvMinusPInv",

    "LeptonTight0_dxy":    "LeptonTightInvIso0_dxy",
    "LeptonTight0_dz":    "LeptonTightInvIso0_dz",
    "LeptonTight0_sieie":    "LeptonTightInvIso0_sieie",
    "LeptonTight0_hoe":    "LeptonTightInvIso0_hoe",
    "cos(LeptonTight0_phi-MET_phi)":         "cos(LeptonTightInvIso0_phi-MET_phi)",
    "cos(LeptonTight0_phi-JetGood0_phi)":    "cos(LeptonTightInvIso0_phi-JetGoodInvLepIso0_phi)",
    "cos(LeptonTight0_phi-JetGood1_phi)":    "cos(LeptonTightInvIso0_phi-JetGoodInvLepIso1_phi)",
    "cos(JetGood0_phi-MET_phi)":             "cos(JetGoodInvLepIso0_phi-MET_phi)",
    "cos(JetGood0_phi-JetGood1_phi)":        "cos(JetGoodInvLepIso0_phi-JetGoodInvLepIso1_phi)",
}

invVariable = replaceVariable[args.variable] if args.variable in replaceVariable.keys() else args.variable

print "Using variables: AR: %s, SB: %s"%(args.variable, invVariable)

# get cached transferfactors
estimators = EstimatorList( setup, processes=["QCD-DD"] )
estimate   = getattr(estimators, "QCD-DD")
estimate.initCache(setup.defaultCacheDir())

# Accounting for 
leptonPtCutVar = "LeptonTightInvIso0_pt"
if args.mode == "e":
    leptonEtaCutVar = "abs(LeptonTightInvIso0_eta+LeptonTightInvIso0_deltaEtaSC)"
else:
    leptonEtaCutVar = "abs(LeptonTightInvIso0_eta)"

QCDTF_updates_2J = copy.deepcopy(QCDTF_updates)

key = (data_sample.name, "AR", args.variable, "_".join(map(str,args.binning)), data_sample.weightString, data_sample.selectionString, selection)
if dirDB.contains(key) and not args.overwrite:
    dataHist = dirDB.get(key.Clone("dataAR"))
else:
    dataHist = data_sample.get1DHistoFromDraw( args.variable, binning=args.binning, selectionString=selection )
    dirDB.add(key, dataHist.Clone("dataAR"), overwrite=True)

dataHist_SB  = dataHist.Clone("data_SB")
dataHist_SB.Scale(0)

qcdHist = dataHist.Clone("qcd")
qcdHist.Scale(0)

for s in mc:
    s.setWeightString( weightStringAR + "*" + sampleWeight )
    key = (s.name, "AR", args.variable, "_".join(map(str,args.binning)), s.weightString, s.selectionString, selection)
    if dirDB.contains(key) and not args.overwrite and s.name != "WG":
        s.hist = dirDB.get(key).Clone(s.name)
    else:
        s.hist = s.get1DHistoFromDraw( args.variable, binning=args.binning, selectionString=selection )
        dirDB.add(key, s.hist.Clone(s.name), overwrite=True)

    if addSF:
        if "DY" in s.name:
            s.hist.Scale(DYSF_val[args.year].val)
        elif "WJets" in s.name:
            s.hist.Scale(WJetsSF_val[args.year].val)
        elif "ZG" in s.name:# and njets < 4:
            s.hist.Scale(ZGSF_val[args.year].val)
        elif "WG" in s.name:# and njets > 3:
            s.hist.Scale(WGSF_val[args.year].val)
        elif "TTG" in s.name:
            s.hist.Scale(SSMSF_val[args.year].val)

    s.hist_SB = copy.deepcopy(dataHist.Clone(s.name+"_SB"))
    s.hist_SB.Scale(0)

    s.hist_SB.style      = styles.fillStyle( s.color )
    s.hist_SB.legendText = s.texName
    s.hist.style         = styles.fillStyle( s.color )
    s.hist.legendText    = s.texName

dataHist_SB.style      = styles.errorStyle( ROOT.kBlack )
dataHist_SB.legendText = "data (%s)"%args.mode.replace("mu","#mu")
dataHist.style         = styles.errorStyle( ROOT.kBlack )
dataHist.legendText    = "data (%s)"%args.mode.replace("mu","#mu")

oneHist = dataHist.Clone("one")
oneHist.notInLegend = True
oneHist.style = styles.lineStyle( ROOT.kWhite, width=0 )
for i in range(oneHist.GetNbinsX()):
    oneHist.SetBinContent(i+1, 1)


for i_pt, pt in enumerate(ptBins[:-1]):
    for i_eta, eta in enumerate(etaBins[:-1]):
        etaLow, etaHigh = eta, etaBins[i_eta+1]
        ptLow, ptHigh   = pt,  ptBins[i_pt+1]

        # REMOVE THAT FOR NOW
        # define the 2016 e-channel QCD sideband in barrel only (bad mT fit in EC)
        if False and args.mode == "e" and args.year == 2016 and (etaHigh > 1.479 or etaHigh < 0):
            leptonPtEtaCut  = [ leptonEtaCutVar + ">=0", leptonPtCutVar + ">=" + str(ptLow) ]
            leptonPtEtaCut += [ leptonEtaCutVar + "<1.479" ]
            if ptHigh > 0:  leptonPtEtaCut += [ leptonPtCutVar + "<" + str(ptHigh) ]
        else:
            leptonPtEtaCut = [ leptonEtaCutVar + ">=" + str(etaLow), leptonPtCutVar + ">=" + str(ptLow) ]
            if etaHigh > 0: leptonPtEtaCut += [ leptonEtaCutVar + "<" + str(etaHigh) ]
            if ptHigh > 0:  leptonPtEtaCut += [ leptonPtCutVar + "<" + str(ptHigh) ]

        leptonPtEtaCut = "&&".join( [preSelection] + leptonPtEtaCut )

        print "Running histograms for qcd selection:"
        print leptonPtEtaCut

        # histos
        key = (data_sample.name, "SB", args.variable, "_".join(map(str,args.binning)), data_sample.weightString, data_sample.selectionString, leptonPtEtaCut)
        if dirDB.contains(key) and not args.overwrite:
            dataHist_SB_tmp = dirDB.get(key.Clone("SBdata"))
        else:
            dataHist_SB_tmp = data_sample.get1DHistoFromDraw( invVariable, binning=args.binning, selectionString=leptonPtEtaCut )
            dirDB.add(key, dataHist_SB_tmp.Clone("SBdata"), overwrite=True)

        dataHist_SB.Add(dataHist_SB_tmp)
        qcdHist_tmp = dataHist_SB_tmp.Clone("qcdtmp_%i_%i"%(i_pt,i_eta))

        for s in mc:
            s.setWeightString( weightStringInv + "*" + sampleWeight )
            key = (s.name, "SB", args.variable, "_".join(map(str,args.binning)), s.weightString, s.selectionString, leptonPtEtaCut)
            if dirDB.contains(key) and not args.overwrite and s.name != "WG":
                s.hist_SB_tmp = dirDB.get(key.Clone("SB"+s.name))
            else:
                s.hist_SB_tmp = s.get1DHistoFromDraw( invVariable, binning=args.binning, selectionString=leptonPtEtaCut )
                dirDB.add(key, s.hist_SB_tmp.Clone("SB"+s.name), overwrite=True)

            # apply SF after histo caching
            if addSF and False:
                if "DY" in s.name:
                    s.hist_SB_tmp.Scale(DYSF_val[args.year].val)
                elif "WJets" in s.name:
                    s.hist_SB_tmp.Scale(WJetsSF_val[args.year].val)
                elif "ZG" in s.name:# and njets < 4:
                    s.hist_SB_tmp.Scale(ZGSF_val[args.year].val)
                elif "WG" in s.name:# and njets > 3:
                    s.hist_SB_tmp.Scale(WGSF_val[args.year].val)
                elif "TTG" in s.name:
                    s.hist_SB_tmp.Scale(SSMSF_val[args.year].val)

            s.hist_SB.Add(s.hist_SB_tmp)
            qcdHist_tmp.Add(s.hist_SB_tmp, -1)


        # Transfer Factor, get the QCD histograms always in barrel regions
        QCDTF_updates_2J["CR"]["leptonEta"] = ( etaLow, etaHigh )
        QCDTF_updates_2J["CR"]["leptonPt"]  = ( ptLow,  ptHigh   )
        QCDTF_updates_2J["SR"]["leptonEta"] = ( etaLow, etaHigh )
        QCDTF_updates_2J["SR"]["leptonPt"]  = ( ptLow,  ptHigh   )

        # REMOVE THAT FOR NOW
        # define the 2016 e-channel QCD sideband in barrel only (bad mT fit in EC)
        if False and args.mode == "e" and args.year == 2016 and (etaHigh > 1.479 or etaHigh < 0):
            QCDTF_updates_2J["CR"]["leptonEta"] = ( 0, 1.479 )

        qcdUpdates  = { "CR":QCDTF_updates_2J["CR"], "SR":QCDTF_updates_2J["SR"] }
        transferFac = estimate.cachedTransferFactor( args.mode, setup, qcdUpdates=qcdUpdates, overwrite=False, checkOnly=False )

        print "pt", ptLow, ptHigh, "eta", etaLow, etaHigh, "TF:", transferFac

        # remove negative bins
        for i in range(qcdHist_tmp.GetNbinsX()):
            if qcdHist_tmp.GetBinContent(i+1) < 0: qcdHist_tmp.SetBinContent(i+1, 0)

        qcdHist_tmp.Scale(transferFac.val)
        qcdHist.Add(qcdHist_tmp)


sbInt = qcdHist.Integral()

# QCD SF?
qcdHist.Scale(QCDSF_val[args.year].val)

qcdHist.style          = styles.fillStyle( color.QCD )
qcdHist.legendText     = "QCD (%i)"%int(qcdHist.Integral())

qcdTemplate            = qcdHist.Clone("QCDTemplate")
qcdTemplate.style      = styles.fillStyle( color.QCD )
qcdTemplate.legendText = "QCD template (%i)"%int(sbInt)
qcdTemplate.Scale(1./ qcdTemplate.Integral() if qcdTemplate.Integral() else 0. )
maxQCD = qcdTemplate.GetMaximum()

histos     = [[s.hist    for s in mc] + [qcdHist], [dataHist]]
histos_SB  = [[s.hist_SB for s in mc],             [dataHist_SB], [qcdTemplate], [oneHist]]

Plot.setDefaults()
replaceLabel = {
    "PhotonNoChgIsoNoSieie0_sieie": "#sigma_{i#eta i#eta}(#gamma)",
    "PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt": "chg.Iso(#gamma)"
}

plots = []
plots.append( Plot.fromHisto( args.variable + "_" + args.addCut if args.survey else args.variable,             histos,        texX = replaceLabel[args.variable],                   texY = "Number of Events" ) )
#plots.append( Plot.fromHisto( args.variable+"_sideband", histos_SB,     texX = args.variable+" (QCD sideband)", texY = "Number of Events" ) )

for plot in plots:

    legend = [ (0.2,0.9-0.025*sum(map(len, plot.histos)),0.9,0.9), 3 ]

    for log in [True, False]:

        if "sideband" in plot.name:
            ratio = {'histos':[(2,3)], 'logY':log, 'texY': 'Template', 'yRange': (0.03, maxQCD*2) if log else (0.001, maxQCD*1.2)}
        else:
            ratio = {'yRange':(0.1,1.9)}
#            ratio = {'yRange':(0.65,1.35)}

        selDir = args.selection
        if args.addCut and not args.survey: selDir += "-" + args.addCut
        plot_directory_ = os.path.join( plot_directory, "fakeHistos", str(args.year), args.plot_directory, selDir, args.mode, "log" if log else "lin" )
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = log, #sorting = True,#plot.name != "mT_fit",
                       yRange = (0.3, "auto"),
                       ratio = ratio,
                       drawObjects = drawObjects( lumi_scale ),
                       legend = legend,
                       copyIndexPHP = True,
                       )

