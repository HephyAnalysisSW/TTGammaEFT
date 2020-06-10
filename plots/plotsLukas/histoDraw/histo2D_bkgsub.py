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

addSF = True

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                        help="Log level for logging")
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv26_v1",                                             help="plot sub-directory")
argParser.add_argument("--selection",          action="store",      default="WJets2", type=str,                                              help="reco region")
argParser.add_argument("--addCut",             action="store",      default=None, type=str,                                                  help="additional cuts")
argParser.add_argument("--year",               action="store",      default=2016,   type=int,  choices=[2016,2017,2018],                     help="Which year to plot?")
argParser.add_argument("--mode",               action="store",      default="all",  type=str,  choices=["mu", "e", "all"],                   help="lepton selection")
args = argParser.parse_args()

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

lumi_scale   = data_sample.lumi * 0.001
weightString    = "%f*weight*reweightHEM*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF"%lumi_scale
weightStringIL  = "%f*weight*reweightHEM*reweightInvIsoTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSFInvIso*reweightLeptonTrackingTightSFInvIso*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF"%lumi_scale
weightStringInv = "((%s)+(%s*%f*((nPhotonGoodInvLepIso>0)*(PhotonGoodInvLepIso0_photonCatMagic==2))))"%(weightStringIL,weightStringIL,(misIDSF_val[args.year].val-1))
weightStringAR  = "((%s)+(%s*%f*((nPhotonGood>0)*(PhotonGood0_photonCatMagic==2))))"%(weightString,weightString,(misIDSF_val[args.year].val-1))

filterCutData = getFilterCut( args.year, isData=True,  skipBadChargedCandidate=True )
filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )
#tr            = TriggerSelector( args.year, singleLepton=True )
#triggerCutMc  = tr.getSelection( "MC" )

data_sample.setSelectionString( filterCutData )
data_sample.setWeightString( "weight*reweightHEM" )

for s in mc:
    s.setSelectionString( [ filterCutMc, "overlapRemoval==1" ] )
    sampleWeight     = "1"

replaceSelection = {
#    "nLeptonVetoIsoCorr": "nLeptonVetoNoIso",
    "nLeptonTight":       "nLeptonTightInvIso",
    "nMuonTight":         "nMuonTightInvIso",
    "nElectronTight":     "nElectronTightInvIso",
    "mLtight0Gamma":      "mLinvtight0Gamma",
    "nPhotonGood":        "nPhotonGoodInvLepIso",
    "nJetGood":           "nJetGoodInvLepIso",
    "nBTagGood":          "nBTagGoodInvLepIso",
    "mT":                 "mTinv",
    "m3":                 "m3inv",
    "LeptonTight0":       "LeptonTightInvIso0",
    "JetGood0":           "JetGoodInvLepIso0",
    "JetGood1":           "JetGoodInvLepIso1",
}


if len(args.selection.split("-")) == 1 and args.selection in allRegions.keys():
    print( "Plotting region from SetupHelpers: %s"%args.selection )

    setup = Setup( year=args.year, photonSelection=False, checkOnly=False, runOnLxPlus=False ) #photonselection always false for qcd estimate
    setup = setup.sysClone( parameters=allRegions[args.selection]["parameters"] )

    selection  = setup.selection( "MC", channel=args.mode, **setup.defaultParameters() )["prefix"]
    selection     = cutInterpreter.cutString( selection )
    selection += "&&triggered==1"
    if args.addCut:
        selection += "&&" + cutInterpreter.cutString( args.addCut )
    print( "Using selection string: %s"%args.selection )

    preSelection  = setup.selection("MC",   channel=args.mode, **setup.defaultParameters(update=QCD_updates))["prefix"]
    preSelection  = cutInterpreter.cutString( preSelection )
    preSelection += "&&triggeredInvIso==1"
    if args.addCut:
        addSel = cutInterpreter.cutString( args.addCut )
        for iso, invIso in replaceSelection.iteritems():
            addSel = addSel.replace(iso,invIso)
        preSelection += "&&" + addSel

else:
    raise Exception("Region not implemented")

# histos
binning = [12, 30, 150, 16, -2.4, 2.4]
var     = "LeptonTight0_eta:LeptonTight0_pt"
invVar  = "LeptonTightInvIso0_eta:LeptonTightInvIso0_pt"

dataHist_SB = data_sample.get2DHistoFromDraw( invVar, binning=binning, selectionString=preSelection )
dataHist    = data_sample.get2DHistoFromDraw( var,    binning=binning, selectionString=selection    )

for s in mc:
    s.setWeightString( weightStringInv + "*" + sampleWeight )
    s.hist_SB = s.get2DHistoFromDraw( invVar, binning=binning, selectionString=preSelection )

    s.setWeightString( weightStringAR + "*" + sampleWeight )
    s.hist = s.get2DHistoFromDraw( var, binning=binning, selectionString=selection )
    # apply SF after histo caching
    if addSF:
        if "DY" in s.name:
            s.hist.Scale(DYSF_val[args.year].val)
            s.hist_SB.Scale(DYSF_val[args.year].val)
        elif "WJets" in s.name:
            s.hist.Scale(WJetsSF_val[args.year].val)
            s.hist_SB.Scale(WJetsSF_val[args.year].val)

    dataHist_SB.Add( s.hist_SB, -1 )
    dataHist.Add( s.hist, -1 )

divHist = dataHist.Clone("div")
divHist.Divide(dataHist_SB)

dataHist.GetZaxis().SetTitle( "Number of Events (bkg sub)" )
dataHist_SB.GetZaxis().SetTitle( "Number of Events (bkg sub)" )
divHist.GetZaxis().SetTitle( "QCD Transfer Factor" )

Plot2D.setDefaults()

mode = args.mode.replace("mu","#mu")
plots = []
plots.append( Plot2D.fromHisto( "data_eta_pt_bkgsub",          [[dataHist]],    texX = "p_{T}(%s)"%mode,                texY = "#eta(%s)"%mode ) )
plots.append( Plot2D.fromHisto( "data_eta_pt_bkgsub_sideband", [[dataHist_SB]], texX = "p_{T}(%s) (QCD sideband)"%mode, texY = "#eta(%s) (QCD sideband)"%mode ) )
plots.append( Plot2D.fromHisto( "data_eta_pt_bkgsub_ratio",    [[divHist]], texX = "p_{T}(%s)"%mode, texY = "#eta(%s)"%mode ) )

for plot in plots:

    for log in [True, False]:

        selDir = args.selection
        if args.addCut: selDir += "-" + args.addCut
        plot_directory_ = os.path.join( plot_directory, "qcdChecks", str(args.year), args.plot_directory, selDir, args.mode, "log" if log else "lin" )

        if not "ratio" in plot.name:
            zRange = (0.1 if log else 0., "auto")
        elif args.mode == "e" and "WJets" in args.selection:
            zRange = (0.1 if log else 0., 6)
        elif args.mode == "mu" and "WJets" in args.selection:
            zRange = (0.1 if log else 0., 12)
        elif args.mode == "e" and "TT" in args.selection:
            zRange = (0.1 if log else 0., 0.6)
        elif args.mode == "mu" and "TT" in args.selection:
            zRange = (0.1 if log else 0., 2)
        
        plotting.draw2D( plot,
                         plot_directory = plot_directory_,
                         logX = False, logY = False, logZ = log,
                         zRange = zRange,
                         drawObjects = drawObjects( lumi_scale ),
                         copyIndexPHP = True,
                       )
