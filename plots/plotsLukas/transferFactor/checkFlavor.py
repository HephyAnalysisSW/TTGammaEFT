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
import Analysis.Tools.syncer as syncer

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

addSF = True

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                        help="Log level for logging")
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv49_v1",                                             help="plot sub-directory")
argParser.add_argument("--selection",          action="store",      default="WJets2",                                                        help="reco region")
argParser.add_argument("--year",               action="store",      default="2016",   type=str,  choices=["2016","2017","2018","RunII"],                     help="Which year to plot?")
argParser.add_argument("--mode",               action="store",      default="e",    type=str,  choices=["mu", "e"],                          help="lepton selection")
argParser.add_argument("--addCut",             action="store",      default=None, type=str,                                                  help="additional cuts")
argParser.add_argument("--overwrite",          action="store_true",                                                                          help="overwrite cache?")
argParser.add_argument("--bTagSideband",       action="store_true",                                                                          help="use btagged sideband")
args = argParser.parse_args()

if args.year != "RunII": args.year = int(args.year)

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
    line = (0.68, 0.95, "%3.1f fb^{-1} (13 TeV)" % lumi_scale)
    lines = [
      (0.15, 0.95, "CMS #bf{#it{Preliminary}} (%s)"%args.selection),
      line
    ]
    return [tex.DrawLatex(*l) for l in lines]

selDir = args.selection
if args.addCut: selDir += "-" + args.addCut

if args.bTagSideband: args.plot_directory += "_bTag"

flavInv = "LeptonTightInvIso0_genPartFlav"
replaceSelection = {
#    "nLeptonVetoIsoCorr": "nLeptonVetoNoIso",

    "nLeptonTight":       "Sum$(Lepton_pt>35&&abs(Lepton_eta)<2.4&&abs(Lepton_dxy)<0.1&&abs(Lepton_dz)<0.2&&(Lepton_pfRelIso03_all>(0.0445+0.963/Lepton_pt))&&Lepton_cutBased<4&&Lepton_cutBased>0&&Lepton_lostHits<2&&abs(Lepton_eInvMinusPInv)<0.0197&&Lepton_sieie<0.0353)",
    "nElectronTight":     "Sum$(abs(Lepton_pdgId)==11&&Lepton_pt>35&&abs(Lepton_eta)<2.4&&abs(Lepton_dxy)<0.1&&abs(Lepton_dz)<0.2&&(Lepton_pfRelIso03_all>(0.0445+0.963/Lepton_pt))&&Lepton_cutBased<4&&Lepton_cutBased>0&&Lepton_lostHits<2&&abs(Lepton_eInvMinusPInv)<0.0197&&Lepton_sieie<0.0353)",
    "nMuonTight":         "nMuonTightInvIso",
#    "nElectronTight":     "nElectronTightInvIso",

#    "nLeptonTight":       "nLeptonTightInvIso",
#    "nMuonTight":         "nMuonTightInvIso",
#    "nElectronTight":     "nElectronTightInvIso",
    "mLtight0Gamma":      "mLinvtight0Gamma",
    "nPhotonGood":        "nPhotonGoodInvLepIso",
    "nJetGood":           "nJetGoodInvLepIso",
    "nBTagGood":          "nBTagGoodInvLepIso",
    "mT":                 "sqrt(2*Lepton_pt[0]*MET_pt*(1-cos(Lepton_phi[0]-MET_phi)))",
#    "mT":                 "mTinv",
    "m3":                 "m3inv",
#    "ht":                 "htinv",
#    "LeptonTight0":       "LeptonTightInvIso0",
    "LeptonTight0_eta":       "Lepton_eta[0]",
    "LeptonTight0_pt":       "Lepton_pt[0]",
}

cache_dir = os.path.join(cache_directory, "qcdTFHistos", str(args.year), args.selection, args.mode)
dirDB = MergingDirDB(cache_dir)
if not dirDB: raise

binning = [ 23, 0, 23 ]

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
elif args.year == "RunII":
    import TTGammaEFT.Samples.nanoTuples_RunII_postProcessed as mc_samples
    from TTGammaEFT.Samples.nanoTuples_RunII_postProcessed import RunII as data_sample

mc = [ mc_samples.TTG, mc_samples.Top, mc_samples.DY_LO, mc_samples.WJets, mc_samples.WG_NLO, mc_samples.ZG, mc_samples.rest ]

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
lumiString = "(35.92*(year==2016)+41.53*(year==2017)+59.74*(year==2018))"

wsInv   = "(%s*weight*reweightHEM*reweightInvIsoTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSFInvIso*reweightLeptonTrackingTightSFInvIso*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF)"%lumiString
wsInv16 = "+(%s*(PhotonNoChgIsoNoSieieInvLepIso0_photonCatMagic==2)*(%f-1)*(year==2016))" %(wsInv, misIDSF_val[2016].val)
wsInv17 = "+(%s*(PhotonNoChgIsoNoSieieInvLepIso0_photonCatMagic==2)*(%f-1)*(year==2017))" %(wsInv, misIDSF_val[2017].val)
wsInv18 = "+(%s*(PhotonNoChgIsoNoSieieInvLepIso0_photonCatMagic==2)*(%f-1)*(year==2018))" %(wsInv, misIDSF_val[2018].val)
weightStringInv = wsInv + wsInv16 + wsInv17 + wsInv18

filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )
#tr            = TriggerSelector( args.year, singleLepton=True )
#triggerCutMc  = tr.getSelection( "MC" )

for s in mc:
    s.setSelectionString( [ filterCutMc, "pTStitching==1", "overlapRemoval==1", "reweightHEM>0" ] )
    s.read_variables = read_variables_MC
    sampleWeight     = "1"

photonRegion = False
bjetRegion   = False
# get selection cuts
regionPlot = False
if len(args.selection.split("-")) == 1 and args.selection in allRegions.keys():
    print( "Plotting region from SetupHelpers: %s"%args.selection )

    regionPlot = True
    setup = Setup( year=args.year, photonSelection=False, checkOnly=False, runOnLxPlus=False ) #photonselection always false for qcd estimate
    setup = setup.sysClone( parameters=allRegions[args.selection]["parameters"] )

    photonRegion = not allRegions[args.selection]["noPhotonCR"]
    bjetRegion   = setup.parameters["nBTag"][0] > 0
    njets        = setup.parameters["nJet"][0]

    selection  = setup.selection( "DataMC", channel=args.mode )["prefix"]
    selection     = cutInterpreter.cutString( selection )
    selection += "&&triggered==1"
    if args.addCut:
        print cutInterpreter.cutString( args.addCut )
        selection += "&&" + cutInterpreter.cutString( args.addCut )
    print( "Using selection string: %s"%args.selection )
    print "sel", selection

    preSelection  = setup.selection("DataMC",   channel=args.mode, **setup.defaultParameters( update=QCD_updates ))["prefix"]
    preSelection  = cutInterpreter.cutString( preSelection )
    preSelection += "&&triggeredInvIso==1"
    if args.bTagSideband:
        preSelection = preSelection.replace("nBTagGoodInvLepIso==0","nBTagGoodInvLepIso>=1")
    print "inv sel", preSelection
    if args.addCut:
        addSel = cutInterpreter.cutString( args.addCut )
        for iso, invIso in replaceSelection.iteritems():
            preSelection = preSelection.replace(iso,invIso)
            addSel = addSel.replace(iso,invIso)
        preSelection += "&&" + addSel
else:
    raise Exception("Region not implemented")

mTHistos_SB  = [[]]

for s in mc:
    s.setWeightString( weightStringInv + "*" + sampleWeight )
    key = (s.name, "flavInv", "_".join(map(str,binning)), s.weightString, s.selectionString, preSelection)
    if dirDB.contains(key) and not args.overwrite:
        s.hist_SB = dirDB.get(key)
    else:
        s.hist_SB = s.get1DHistoFromDraw( flavInv, binning=binning, selectionString=preSelection, addOverFlowBin="upper" )
        dirDB.add(key, s.hist_SB)

    # apply SF after histo caching
    if addSF:
        if "DY" in s.name:
            s.hist_SB.Scale(DYSF_val[args.year].val)
        elif "WJets" in s.name:
            s.hist_SB.Scale(WJetsSF_val[args.year].val)
        elif "ZG" in s.name:
            s.hist_SB.Scale(ZGSF_val[args.year].val)
        elif "WG" in s.name:
            s.hist_SB.Scale(WGSF_val[args.year].val)
        elif "TTG" in s.name:
            s.hist_SB.Scale(SSMSF_val[args.year].val)

    s.hist_SB.style      = styles.fillStyle( s.color )
    s.hist_SB.legendText = s.texName

    mTHistos_SB[0].append( s.hist_SB )


Plot.setDefaults()

plots = []
plots.append( Plot.fromHisto( "genPartFlav_sideband", mTHistos_SB,     texX = "genPartFlav (QCD sideband)", texY = "Number of Events" ) )

for plot in plots:

    legend = [ (0.2, 0.70, 0.9, 0.9), 2 ]
    for log in [True, False]:

        histModifications  = []
        histModifications += [lambda h: h.GetYaxis().SetTitleOffset(1.6 if log else 2.2)]

        ratioHistModifications  = []
        ratioHistModifications += [lambda h: h.GetYaxis().SetTitleOffset(1.6 if log else 2.2)]

        ratio = {'yRange':(0.1,1.9), "histModifications":ratioHistModifications}

        plot_directory_ = os.path.join( plot_directory, "transferFactor", str(args.year), args.plot_directory, "qcdHistos",  selDir, args.mode, "log" if log else "lin" )
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = log, sorting = True,#plot.name != "mT_fit",
                       yRange = (0.3, "auto") if not "template" in plot.name else "auto",
#                       ratio = ratio,
                       drawObjects = drawObjects( lumi_scale ),
                       legend = legend,
                       histModifications = histModifications,
                       copyIndexPHP = True,
                       )

