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
argParser.add_argument("--variable",           action="store",      default="LeptonTightNoSieie0_sieie", type=str,                                    help="variable to plot")
argParser.add_argument("--binning",            action="store",      default=[20,-2.4,2.4],  type=float, nargs="*",                           help="binning of plots")
argParser.add_argument("--year",               action="store",      default=2016,   type=int,  choices=[2016,2017,2018],                     help="Which year to plot?")
argParser.add_argument("--small",              action="store_true",                                                                          help="Run only on a small subset of the data?")
argParser.add_argument("--survey",             action="store_true",                                                                          help="all plots in one directory?")
argParser.add_argument("--photonCat",          action="store_true",                                                                          help="all plots in one directory?")
argParser.add_argument("--overwrite",          action="store_true",                                                                          help="overwrite cache?")
argParser.add_argument("--blind",              action="store_true",                                                                          help="blind SR?")
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

cache_dir = os.path.join(cache_directory, "drawHistos", str(args.year), args.selection, "e")
dirDB = MergingDirDB(cache_dir)
if not dirDB: raise

# Sample definition
os.environ["gammaSkim"]="False" #always false for QCD estimate
if args.year == 2016:
    import TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed as mc_samples
    from   TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import Run2016 as data_sample
elif args.year == 2017:
    import TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed as mc_samples
    from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import Run2017 as data_sample
elif args.year == 2018:
    import TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed as mc_samples
    from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import Run2018 as data_sample

mc = [ mc_samples.TTG, mc_samples.Top, mc_samples.DY_LO, mc_samples.WJets, mc_samples.WG, mc_samples.ZG, mc_samples.rest ]

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

replaceSelection = {
    "nLeptonTightNoSieie":                   "nLeptonTightNoSieieInvIso",
#    "nMuonTightNoSieie":                     "nMuonTightNoSieieInvIso",
#    "nElectronTightNoSieie":                 "nElectronTightNoSieieInvIso",
    "nJetGoodNoLepSieie":                    "nJetGoodNoLepSieieInvLepIso",
    "nBTagGoodNoLepSieie":                   "nBTagGoodNoLepSieieInvLepIso",
    "nPhotonGood":                           "nPhotonGoodInvLepIso",
    "LeptonTightNoSieie0":                   "LeptonTightInvIsoNoSieie0",
}

filterCutData = getFilterCut( args.year, isData=True,  skipBadChargedCandidate=True )
filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )

blinding = []
if args.year != 2016 and args.blind:
    blinding += [ cutInterpreter.cutString( "highSieieLep" ) ]

data_sample.setSelectionString( [filterCutData, "reweightHEM>0"] + blinding )
data_sample.setWeightString( "weight" )
if args.small:           
    data_sample.normalization = 1.
    data_sample.reduceFiles( factor=5 )
    data_sample.setWeightString( "weight*%f"%(1./data_sample.normalization) )


for s in mc:
    s.setSelectionString( [ filterCutMc, "overlapRemoval==1" ] )
    s.read_variables = read_variables_MC
    sampleWeight     = "1"
    if args.small:           
        s.normalization = 1.
        s.reduceFiles( factor=100 )
        sampleWeight = "%f"%(1./s.normalization)

selection = cutInterpreter.cutString( args.selection )
selection += "&&nElectronTightNoSieie==1"
selection += "&&triggeredNoSieie==1"
if args.addCut:
    selection += "&&" + cutInterpreter.cutString( args.addCut )

preSelection  = cutInterpreter.cutString( args.selection.replace("BTag1p","BTag0") )
for iso, invIso in replaceSelection.iteritems():
    preSelection = preSelection.replace(iso,invIso)
if args.addCut:
    addSel = cutInterpreter.cutString( args.addCut )
    for iso, invIso in replaceSelection.iteritems():
        addSel = addSel.replace(iso,invIso)
    preSelection += "&&" + addSel
preSelection += "&&nElectronTightNoSieieInvIso==1"
preSelection += "&&triggeredInvIsoNoSieie==1"


print preSelection

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
if addSF:
    weightStringAR  = "((%s)+(%s*%f*((nPhotonNoChgIsoNoSieie>0)*(PhotonNoChgIsoNoSieie0_photonCatMagic==2))))"%(weightString,weightString,(misIDSF_val[args.year].val-1))
    weightStringInv = "((%s)+(%s*%f*((nPhotonNoChgIsoNoSieieInvLepIso>0)*(PhotonNoChgIsoNoSieieInvLepIso0_photonCatMagic==2))))"%(weightStringIL,weightStringIL,(misIDSF_val[args.year].val-1))
else:
    weightStringAR  = weightString
    weightStringInv = weightStringIL

replaceVariable = {
    "LeptonTightNoSieie0_pfRelIso03_all":   "LeptonTightInvIsoNoSieie0_pfRelIso03_all",
    "LeptonTightNoSieie0_phi":   "LeptonTightInvIsoNoSieie0_phi",
    "LeptonTightNoSieie0_eta":   "LeptonTightInvIsoNoSieie0_eta",
    "LeptonTightNoSieie0_pt":    "LeptonTightInvIsoNoSieie0_pt",
    "LeptonTightNoSieie0_sip3d":    "LeptonTightInvIsoNoSieie0_sip3d",
    "LeptonTightNoSieie0_dr03EcalRecHitSumEt":    "LeptonTightInvIsoNoSieie0_dr03EcalRecHitSumEt",
    "LeptonTightNoSieie0_dr03HcalDepth1TowerSumEt":    "LeptonTightInvIsoNoSieie0_dr03HcalDepth1TowerSumEt",
    "LeptonTightNoSieie0_dr03TkSumPt":    "LeptonTightInvIsoNoSieie0_dr03TkSumPt",
    "LeptonTightNoSieie0_ip3d":    "LeptonTightInvIsoNoSieie0_ip3d",
    "LeptonTightNoSieie0_r9":    "LeptonTightInvIsoNoSieie0_r9",
    "LeptonTightNoSieie0_eInvMinusPInv":    "LeptonTightInvIsoNoSieie0_eInvMinusPInv",
    "LeptonTightNoSieie0_dxy":    "LeptonTightInvIsoNoSieie0_dxy",
    "LeptonTightNoSieie0_dz":    "LeptonTightInvIsoNoSieie0_dz",
    "LeptonTightNoSieie0_sieie":    "LeptonTightInvIsoNoSieie0_sieie",
    "LeptonTightNoSieie0_hoe":    "LeptonTightInvIsoNoSieie0_hoe",
    "cos(LeptonTightNoSieie0_phi-MET_phi)":         "cos(LeptonTightInvIsoNoSieie0_phi-MET_phi)",
    "cos(LeptonTightNoSieie0_phi-JetGood0_phi)":    "cos(LeptonTightInvIsoNoSieie0_phi-JetGoodInvLepIso0_phi)",
    "cos(LeptonTightNoSieie0_phi-JetGood1_phi)":    "cos(LeptonTightInvIsoNoSieie0_phi-JetGoodInvLepIso1_phi)",
    "cos(JetGood0_phi-MET_phi)":             "cos(JetGoodInvLepIso0_phi-MET_phi)",
    "cos(JetGood0_phi-JetGood1_phi)":        "cos(JetGoodInvLepIso0_phi-JetGoodInvLepIso1_phi)",
}

invVariable = replaceVariable[args.variable] if args.variable in replaceVariable.keys() else args.variable

# get cached transferfactors
setup = Setup( year=args.year, photonSelection=False, checkOnly=False, runOnLxPlus=False ) #photonselection always false for qcd estimate
reg  = "TT" if "1p" in args.selection else "WJets"
reg += "4p" if "4p" in args.selection else "3"

setup = setup.sysClone( parameters=allRegions[reg]["parameters"] )
estimators = EstimatorList( setup, processes=["QCD-DD"] )
estimate   = getattr(estimators, "QCD-DD")
estimate.initCache(setup.defaultCacheDir())

# Accounting for 
leptonPtCutVar  = "LeptonTightInvIsoNoSieie0_pt"
leptonEtaCutVar = "abs(LeptonTightInvIsoNoSieie0_eta+LeptonTightInvIsoNoSieie0_deltaEtaSC)"
QCDTF_updates_2J = copy.deepcopy(QCDTF_updates)

key = (data_sample.name, "AR", args.variable, "_".join(map(str,args.binning)), data_sample.weightString, data_sample.selectionString, selection)
if dirDB.contains(key) and not args.overwrite:
    dataHist = dirDB.get(key).Clone("data")
else:
    dataHist = data_sample.get1DHistoFromDraw( args.variable, binning=args.binning, selectionString=selection )
    dirDB.add(key, dataHist.Clone("data"), overwrite=True)

dataHist_SB  = dataHist.Clone("data_SB")
dataHist_SB.Scale(0)


genCat = [None]
if args.photonCat:
    hists = {}
    genCat = ["noChgIsoNoSieiephotoncat0","noChgIsoNoSieiephotoncat1","noChgIsoNoSieiephotoncat2","noChgIsoNoSieiephotoncat3","noChgIsoNoSieiephotoncat4"]
    catSettings = { "noChgIsoNoSieiephotoncat0":{"texName":"gen #gamma", "color":color.gen},
                    "noChgIsoNoSieiephotoncat1":{"texName":"had #gamma", "color":color.had},
                    "noChgIsoNoSieiephotoncat2":{"texName":"misID-e", "color":color.misID},
                    "noChgIsoNoSieiephotoncat3":{"texName":"fake #gamma", "color":color.fakes},
                    "noChgIsoNoSieiephotoncat4":{"texName":"PU #gamma", "color":color.PU} }
    for g in genCat:
        hists[g] = dataHist.Clone(g)
        hists[g].Scale(0)

for s in mc:
    for g in genCat:
        selectionString = selection + "&&" + cutInterpreter.cutString( g ) if g else selection
        s.setWeightString( weightStringAR + "*" + sampleWeight )
        key = (s.name, "AR", args.variable, "_".join(map(str,args.binning)), s.weightString, s.selectionString, selectionString)
        if dirDB.contains(key) and not args.overwrite and s.name != "WG":
            s.hist = copy.deepcopy(dirDB.get(key).Clone(s.name))
        else:
            s.hist = s.get1DHistoFromDraw( args.variable, binning=args.binning, selectionString=selectionString )
            dirDB.add(key, s.hist.Clone(s.name), overwrite=True)

        if addSF:
            if "DY" in s.name:
                s.hist.Scale(DYSF_val[args.year].val)
            elif "WJets" in s.name:
                s.hist.Scale(WJetsSF_val[args.year].val)
            elif "Top" in s.name:
                s.hist.Scale(TTSF_val[args.year].val)
            elif "ZG" in s.name:# and njets < 4:
                s.hist.Scale(ZGSF_val[args.year].val)
            elif "other" in s.name:# and njets < 4:
                s.hist.Scale(otherSF_val[args.year].val)
            elif "WG" in s.name:# and njets > 3:
                s.hist.Scale(WGSF_val[args.year].val)
            elif "TTG" in s.name:
                s.hist.Scale(SSMSF_val[args.year].val)

        if args.photonCat:
            hists[g].Add(s.hist)

    s.hist_SB = copy.deepcopy(dataHist.Clone(s.name+"_SB"))
    s.hist_SB.Scale(0)

    s.hist_SB.style  = styles.fillStyle( s.color )
    s.hist_SB.legendText = s.texName
    s.hist.style         = styles.fillStyle( s.color )
    s.hist.legendText    = s.texName

if args.photonCat:
    hists[g].style = styles.fillStyle( catSettings[g]["color"] )
    hists[g].legendText = catSettings[g]["texName"]

dataHist_SB.style      = styles.errorStyle( ROOT.kBlack )
dataHist_SB.legendText = "data (e)"
dataHist.style         = styles.errorStyle( ROOT.kBlack )
dataHist.legendText    = "data (e)"

qcdHist = dataHist.Clone("qcd")
qcdHist.Scale(0)

for i_pt, pt in enumerate(ptBins[:-1]):
    for i_eta, eta in enumerate(etaBins[:-1]):
        etaLow, etaHigh = eta, etaBins[i_eta+1]
        ptLow, ptHigh   = pt,  ptBins[i_pt+1]

        leptonPtEtaCut = [ leptonEtaCutVar + ">=" + str(etaLow), leptonPtCutVar + ">=" + str(ptLow) ]
        if etaHigh > 0: leptonPtEtaCut += [ leptonEtaCutVar + "<" + str(etaHigh) ]
        if ptHigh > 0:  leptonPtEtaCut += [ leptonPtCutVar + "<" + str(ptHigh) ]

        leptonPtEtaCut = "&&".join( [preSelection] + leptonPtEtaCut )

        print "Running histograms for qcd selection:"
        print leptonPtEtaCut

        # histos
        data_sample.setSelectionString( [filterCutData, "reweightHEM>0"] )
        key = (data_sample.name, "SB", args.variable, "_".join(map(str,args.binning)), data_sample.weightString, data_sample.selectionString, leptonPtEtaCut)
        if dirDB.contains(key) and not args.overwrite:
            dataHist_SB_tmp = dirDB.get(key).Clone("SBdata")
        else:
            dataHist_SB_tmp = data_sample.get1DHistoFromDraw( invVariable, binning=args.binning, selectionString=leptonPtEtaCut )
            dirDB.add(key, dataHist_SB_tmp.Clone("SBdata"), overwrite=True)

        dataHist_SB.Add(dataHist_SB_tmp)
        qcdHist_tmp = dataHist_SB_tmp.Clone("qcdtmp_%i_%i"%(i_pt,i_eta))

        for s in mc:
            s.setWeightString( weightStringInv + "*" + sampleWeight )
            key = (s.name, "SB", args.variable, "_".join(map(str,args.binning)), s.weightString, s.selectionString, leptonPtEtaCut)
            if dirDB.contains(key) and not args.overwrite:
                s.hist_SB_tmp = dirDB.get(key).Clone("SB"+s.name)
            else:
                s.hist_SB_tmp = s.get1DHistoFromDraw( invVariable, binning=args.binning, selectionString=leptonPtEtaCut )
                dirDB.add(key, s.hist_SB_tmp.Clone("SB"+s.name), overwrite=True)

            # apply SF after histo caching
            if addSF and False:
                if "DY" in s.name:
                    s.hist_SB_tmp.Scale(DYSF_val[args.year].val)
                elif "WJets" in s.name:
                    s.hist_SB_tmp.Scale(WJetsSF_val[args.year].val)
                elif "Top" in s.name:
                    s.hist_SB_tmp.Scale(TTSF_val[args.year].val)
                elif "ZG" in s.name:# and njets < 4:
                    s.hist_SB_tmp.Scale(ZGSF_val[args.year].val)
                elif "other" in s.name:# and njets < 4:
                    s.hist_SB_tmp.Scale(otherSF_val[args.year].val)
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

        qcdUpdates  = { "CR":QCDTF_updates_2J["CR"], "SR":QCDTF_updates_2J["SR"] }
        transferFac = estimate.cachedTransferFactor( "e", setup, qcdUpdates=qcdUpdates, overwrite=False, checkOnly=False )

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
qcdHist.legendText     = "QCD"

if args.photonCat:
    histos     = [[h for h in hists.values()] + [qcdHist], [dataHist]]
else:
    histos     = [[s.hist    for s in mc] + [qcdHist], [dataHist]]

Plot.setDefaults()
replaceLabel = {
    "PhotonNoChgIsoNoSieie0_sieie": "#sigma_{i#eta i#eta}(#gamma)",
    "PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt": "chg.Iso(#gamma)"
}

plots = []
plots.append( Plot.fromHisto( args.variable + "_" + args.addCut if args.survey else args.variable,             histos,        texX = replaceLabel[args.variable],                   texY = "Number of Events" ) )

for plot in plots:

    legend = [ (0.2,0.9-0.025*sum(map(len, plot.histos)),0.9,0.9), 3 ]

    for log in [True, False]:

        ratio = {'yRange':(0.1,1.9)}

        selDir = args.selection
        if args.addCut and not args.survey: selDir += "-" + args.addCut
        plot_directory_ = os.path.join( plot_directory, "noSieieHistos", str(args.year), args.plot_directory, selDir, "e_cat" if args.photonCat else "e", "log" if log else "lin" )
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = log, #sorting = True,#plot.name != "mT_fit",
                       yRange = (0.3, "auto"),
                       ratio = ratio,
                       drawObjects = drawObjects( lumi_scale ),
                       legend = legend,
                       copyIndexPHP = True,
                       )

