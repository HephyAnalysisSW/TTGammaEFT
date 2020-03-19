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
from TTGammaEFT.Tools.TriggerSelector  import TriggerSelector

from TTGammaEFT.Analysis.SetupHelpers  import *
from TTGammaEFT.Analysis.Setup         import Setup
from TTGammaEFT.Analysis.EstimatorList import EstimatorList

from TTGammaEFT.Samples.color          import color
from Analysis.Tools.MergingDirDB      import MergingDirDB

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

addSF = True

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
    mc          = [ TTG_16, TT_pow_16, DY_LO_16, WJets_16, WG_16, ZG_16, Zinv_16, rest_16 ]
    ttg         = TTG_16
    tt          = TT_pow_16
    wjets       = WJets_16
    ttg         = TTG_16
    wg          = WG_16
    other       = rest_16
    data_sample = Run2016
elif args.year == 2017:
    from TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed    import *
    from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import *
    mc          = [ TTG_17, TT_pow_17, DY_LO_17, WJets_17, WG_17, ZG_17, Zinv_17, rest_17 ]
    ttg         = TTG_17
    tt          = TT_pow_17
    wjets       = WJets_17
    ttg         = TTG_17
    wg          = WG_17
    other       = rest_17
    data_sample = Run2017
elif args.year == 2018:
    from TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed  import *
    from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import *
    mc          = [ TTG_18, TT_pow_18, DY_LO_18, WJets_18, WG_18, ZG_18, Zinv_18, rest_18 ]
    ttg         = TTG_18
    tt          = TT_pow_18
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
                     "reweightInvTrigger/F", "reweightInvTriggerUp/F", "reweightInvTriggerDown/F",
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
weightString    = "%f*weight*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF"%lumi_scale
weightStringIL  = "%f*weight*reweightInvTrigger*reweightL1Prefire*reweightPU*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF"%lumi_scale
weightStringInv = "((%s)+(%s*%f*((nPhotonGoodInvLepIso>0)*(PhotonGoodInvLepIso0_photonCat==2))))"%(weightStringIL,weightStringIL,(misIDSF_val[args.year].val-1))
weightStringAR  = "((%s)+(%s*%f*((nPhotonGood>0)*(PhotonGood0_photonCat==2))))"%(weightString,weightString,(misIDSF_val[args.year].val-1))

filterCutData = getFilterCut( args.year, isData=True,  skipBadChargedCandidate=True )
filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )
tr            = TriggerSelector( args.year, singleLepton=True )
triggerCutMc  = tr.getSelection( "MC" )

data_sample.setSelectionString( filterCutData )
data_sample.setWeightString( "weight" )
if args.small:           
    data_sample.normalization = 1.
    data_sample.reduceFiles( factor=5 )
    data_sample.setWeightString( "weight*%f"%(1./data_sample.normalization) )

for s in mc:
    s.setSelectionString( [ filterCutMc, triggerCutMc, "overlapRemoval==1" ] )
    s.read_variables = read_variables_MC
    sampleWeight     = "1"
    if args.small:           
        s.normalization = 1.
        s.reduceFiles( factor=100 )
        sampleWeight = "%f"%(1./s.normalization)

replaceSelection = {
    "nLeptonVetoIsoCorr": "nLeptonVetoNoIso",
    "nLeptonTight":       "nLeptonTightInvIso",
    "nMuonTight":         "nMuonTightInvIso",
    "nElectronTight":     "nElectronTightInvIso",
    "mLtight0Gamma":      "mLinvtight0Gamma",
    "nPhotonGood":        "nPhotonGoodInvLepIso",
    "nJetGood":           "nJetGoodInvLepIso",
    "nBTagGood":          "nBTagGoodInvLepIso",
    "mT":                 "mTinv",
    "m3":                 "m3inv",
    "ht":                 "htinv",
    "LeptonTight0_eta":   "LeptonTightInvIso0_eta",
    "LeptonTight0_pt":    "LeptonTightInvIso0_pt",
}


if len(args.selection.split("-")) == 1 and args.selection in allRegions.keys():
    print( "Plotting region from SetupHelpers: %s"%args.selection )

    setup = Setup( year=args.year, photonSelection=False, checkOnly=False, runOnLxPlus=False ) #photonselection always false for qcd estimate
    setup = setup.sysClone( parameters=allRegions[args.selection]["parameters"] )

    allSelection  = setup.selection( "MC", channel="all", **setup.defaultParameters() )["prefix"]
    selection     = allSelection + "-" + args.mode
    selection     = cutInterpreter.cutString( selection )
    if args.addCut:
        selection += "&&" + cutInterpreter.cutString( args.addCut )
    print( "Using selection string: %s"%args.selection )

    preSelection  = setup.selection("MC",   channel="all", **setup.defaultParameters(update=QCD_updates))["prefix"]
    preSelection += "-" + args.mode + "Inv"
    preSelection  = cutInterpreter.cutString( preSelection )
    if args.addCut:
        addSel = cutInterpreter.cutString( args.addCut )
        for iso, invIso in replaceSelection.iteritems():
            addSel = addSel.replace(iso,invIso)
        preSelection += "&&" + addSel

#    if args.mode == "e":
#        preSelection += "&&LeptonTightInvIso0_pfRelIso03_all<0.2"
#    else:
#        preSelection += "&&LeptonTightInvIso0_pfRelIso04_all<0.4"

    preSelection_EC     = preSelection + "&&abs(LeptonTightInvIso0_eta)>1.479"
    preSelection_Barrel = preSelection + "&&abs(LeptonTightInvIso0_eta)<=1.479"

else:
    raise Exception("Region not implemented")

# get cached transferfactors
estimators = EstimatorList( setup, processes=["QCD-DD"] )
estimate   = getattr(estimators, "QCD-DD")
estimate.initCache(setup.defaultCacheDir())

qcdUpdates_EC      = { "CR":QCDTF_updates["CREC"],     "SR":QCDTF_updates["SREC"]     }
transferFac_EC     = estimate.cachedTransferFactor(args.mode, setup, qcdUpdates=qcdUpdates_EC,     save=True, overwrite=False, checkOnly=False)
qcdUpdates_Barrel  = { "CR":QCDTF_updates["CRBarrel"], "SR":QCDTF_updates["SRBarrel"] }
transferFac_Barrel = estimate.cachedTransferFactor(args.mode, setup, qcdUpdates=qcdUpdates_Barrel, save=True, overwrite=False, checkOnly=False)

print "Using QCD Transfer Factor Barrel: %f"%transferFac_Barrel.val
print "Using QCD Transfer Factor EC: %f"%transferFac_EC.val

replaceVariable = {
    "ltight0GammadR":     "linvtight0GammadR",
    "ltight0GammadPhi":   "linvtight0GammadPhi",
    "mT":                 "mTinv",
    "m3":                 "m3inv",
    "ht":                 "htinv",
    "lpTight":            "lpInvTight",
    "mLtight0Gamma":      "mLinvtight0Gamma",
    "LeptonTight0_phi":   "LeptonTightInvIso0_phi",
    "LeptonTight0_eta":   "LeptonTightInvIso0_eta",
    "LeptonTight0_pt":    "LeptonTightInvIso0_pt",
    "cos(LeptonTight0_phi-MET_phi)":         "cos(LeptonTightInvIso0_phi-MET_phi)",
    "cos(LeptonTight0_phi-JetGood0_phi)":    "cos(LeptonTightInvIso0_phi-JetGoodInvLepIso0_phi)",
    "cos(LeptonTight0_phi-JetGood1_phi)":    "cos(LeptonTightInvIso0_phi-JetGoodInvLepIso1_phi)",
    "cos(JetGood0_phi-MET_phi)":             "cos(JetGoodInvLepIso0_phi-MET_phi)",
    "cos(JetGood0_phi-JetGood1_phi)":        "cos(JetGoodInvLepIso0_phi-JetGoodInvLepIso1_phi)",
}

invVariable = replaceVariable[args.variable] if args.variable in replaceVariable.keys() else args.variable

# histos
key = (data_sample.name, "Binv", args.variable, "_".join(map(str,args.binning)), data_sample.weightString, data_sample.selectionString, preSelection_Barrel)
if dirDB.contains(key) and not args.overwrite:
    dataHistB_SB = dirDB.get(key)
else:
    dataHistB_SB = data_sample.get1DHistoFromDraw( invVariable, binning=args.binning, selectionString=preSelection_Barrel, addOverFlowBin="upper" )
    dirDB.add(key, dataHistB_SB)

key = (data_sample.name, "ECinv", args.variable, "_".join(map(str,args.binning)), data_sample.weightString, data_sample.selectionString, preSelection_EC)
if dirDB.contains(key) and not args.overwrite:
    dataHistEC_SB = dirDB.get(key)
else:
    dataHistEC_SB = data_sample.get1DHistoFromDraw( invVariable, binning=args.binning, selectionString=preSelection_EC, addOverFlowBin="upper" )
    dirDB.add(key, dataHistEC_SB)

key = (data_sample.name, "AR", args.variable, "_".join(map(str,args.binning)), data_sample.weightString, data_sample.selectionString, selection)
if dirDB.contains(key) and not args.overwrite:
    dataHist = dirDB.get(key)
else:
    dataHist = data_sample.get1DHistoFromDraw( args.variable, binning=args.binning, selectionString=selection, addOverFlowBin="upper" )
    dirDB.add(key, dataHist)

qcdHistB  = dataHistB_SB.Clone("QCDB")
qcdHistEC = dataHistEC_SB.Clone("QCDEC")

dataHist_SB = dataHistEC_SB.Clone("dataHist")
dataHist_SB.Add(dataHistB_SB)

dataHist_SB.style      = styles.errorStyle( ROOT.kBlack )
dataHist_SB.legendText = "data (%s)"%args.mode.replace("mu","#mu")
dataHist.style         = styles.errorStyle( ROOT.kBlack )
dataHist.legendText    = "data (%s)"%args.mode.replace("mu","#mu")

oneHist = dataHist.Clone("one")
oneHist.notInLegend = True
oneHist.style = styles.lineStyle( ROOT.kWhite, width=0 )
for i in range(oneHist.GetNbinsX()):
    oneHist.SetBinContent(i+1, 1)

histos     = [[], [dataHist]]
histos_SB  = [[], [dataHist_SB]]

for s in mc:
    s.setWeightString( weightStringInv + "*" + sampleWeight )
    key = (s.name, "Binv", args.variable, "_".join(map(str,args.binning)), s.weightString, s.selectionString, preSelection_Barrel)
    if dirDB.contains(key) and not args.overwrite:
        s.histB_SB = dirDB.get(key)
    else:
        s.histB_SB = s.get1DHistoFromDraw( invVariable, binning=args.binning, selectionString=preSelection_Barrel, addOverFlowBin="upper" )
        dirDB.add(key, s.histB_SB)

    s.setWeightString( weightStringInv + "*" + sampleWeight )
    key = (s.name, "ECinv", args.variable, "_".join(map(str,args.binning)), s.weightString, s.selectionString, preSelection_EC)
    if dirDB.contains(key) and not args.overwrite:
        s.histEC_SB = dirDB.get(key)
    else:
        s.histEC_SB = s.get1DHistoFromDraw( invVariable, binning=args.binning, selectionString=preSelection_EC, addOverFlowBin="upper" )
        dirDB.add(key, s.histEC_SB)

    s.setWeightString( weightStringAR + "*" + sampleWeight )
    key = (s.name, "AR", args.variable, "_".join(map(str,args.binning)), s.weightString, s.selectionString, selection)
    if dirDB.contains(key) and not args.overwrite:
        s.hist = dirDB.get(key)
    else:
        s.hist = s.get1DHistoFromDraw( args.variable, binning=args.binning, selectionString=selection, addOverFlowBin="upper" )
        dirDB.add(key, s.hist)

    # apply SF after histo caching
    if addSF:
        if "DY" in s.name:
            s.hist.Scale(DYSF_val[args.year].val)
            s.histB_SB.Scale(DYSF_val[args.year].val)
            s.histEC_SB.Scale(DYSF_val[args.year].val)
        elif "WJets" in s.name:
            s.hist.Scale(WJetsSF_val[args.year].val)
            s.histB_SB.Scale(WJetsSF_val[args.year].val)
            s.histEC_SB.Scale(WJetsSF_val[args.year].val)
        elif "TT_pow" in s.name:
            s.hist.Scale(TTSF_val[args.year].val)
            s.histB_SB.Scale(TTSF_val[args.year].val)
            s.histEC_SB.Scale(TTSF_val[args.year].val)
        elif "ZG" in s.name:# and njets < 4:
            s.hist.Scale(ZGSF_val[args.year].val)
            s.histB_SB.Scale(ZGSF_val[args.year].val)
            s.histEC_SB.Scale(ZGSF_val[args.year].val)
        elif "other" in s.name:# and njets < 4:
            s.hist.Scale(otherSF_val[args.year].val)
            s.histB_SB.Scale(otherSF_val[args.year].val)
            s.histEC_SB.Scale(otherSF_val[args.year].val)
        elif "WG" in s.name:# and njets > 3:
            s.hist.Scale(WGSF_val[args.year].val)
            s.histB_SB.Scale(WGSF_val[args.year].val)
            s.histEC_SB.Scale(WGSF_val[args.year].val)
        elif "TTG" in s.name:
            s.hist.Scale(SSMSF_val[args.year].val)
            s.histB_SB.Scale(SSMSF_val[args.year].val)
            s.histEC_SB.Scale(SSMSF_val[args.year].val)

    qcdHistB.Add( s.histB_SB, -1 )
    qcdHistEC.Add( s.histEC_SB, -1 )

    s.hist_SB = s.histB_SB.Clone(s.name)
    s.hist_SB.Add(s.histEC_SB)

    s.hist_SB.style      = styles.fillStyle( s.color )
    s.hist_SB.legendText = s.texName
    s.hist.style         = styles.fillStyle( s.color )
    s.hist.legendText    = s.texName

    histos[0].append( s.hist )
    histos_SB[0].append( s.hist_SB )

sbInt = qcdHistB.Integral() + qcdHistEC.Integral()
qcdHistB.Scale(   transferFac_Barrel.val )
qcdHistEC.Scale(  transferFac_EC.val )

qcdHist = qcdHistB.Clone("QCD")
qcdHist.Add(qcdHistEC)

# remove negative bins
for i in range(qcdHist.GetNbinsX()):
    if qcdHist.GetBinContent(i+1) < 0: qcdHist.SetBinContent(i+1, 0)

qcdHist.style          = styles.fillStyle( color.QCD )
qcdHist.legendText     = "QCD (%i)"%int(qcdHist.Integral())

histos[0].append( qcdHist )

qcdTemplate            = qcdHist.Clone("QCDTemplate")
qcdTemplate.style      = styles.fillStyle( color.QCD )
qcdTemplate.legendText = "QCD template (%i)"%int(sbInt)
qcdTemplate.Scale(1./ qcdTemplate.Integral() )
maxQCD = qcdTemplate.GetMaximum()

# for template ratio pattern
histos_SB.append( [qcdTemplate] )
histos_SB.append( [oneHist] )

Plot.setDefaults()

plots = []
plots.append( Plot.fromHisto( args.variable,             histos,        texX = args.variable,                   texY = "Number of Events" ) )
plots.append( Plot.fromHisto( args.variable+"_sideband", histos_SB,     texX = args.variable+" (QCD sideband)", texY = "Number of Events" ) )

for plot in plots:

    legend = [ (0.2,0.9-0.025*sum(map(len, plot.histos)),0.9,0.9), 3 ]

    for log in [True, False]:

        if "sideband" in plot.name:
            ratio = {'histos':[(2,3)], 'logY':log, 'texY': 'Template', 'yRange': (0.03, maxQCD*2) if log else (0.001, maxQCD*1.2)}
        else:
            ratio = {'yRange':(0.1,1.9)}
#            ratio = {'yRange':(0.65,1.35)}

        selDir = args.selection
        if args.addCut: selDir += "-" + args.addCut
        plot_directory_ = os.path.join( plot_directory, "qcdChecks", str(args.year), args.plot_directory, selDir, args.mode, "log" if log else "lin" )
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = log, sorting = True,#plot.name != "mT_fit",
                       yRange = (0.3, "auto"),
                       ratio = ratio,
                       drawObjects = drawObjects( lumi_scale ),
                       legend = legend,
                       copyIndexPHP = True,
                       )

