# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy

# RootTools
from RootTools.core.standard           import *

# Analysis
from Analysis.Tools.metFilters         import getFilterCut
import Analysis.Tools.syncer as syncer

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

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                        help="Log level for logging")
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv49_v1",                                             help="plot sub-directory")
argParser.add_argument("--selection",          action="store",      default="SR3p", type=str,                                              help="reco region")
argParser.add_argument("--addCut",             action="store",      default=None, type=str,                                                  help="additional cuts")
argParser.add_argument("--variable",           action="store",      default="PhotonGood0_pt", type=str,                                    help="variable to plot")
argParser.add_argument("--binning",            action="store",      default=[20,0,320],  type=float, nargs="*",                           help="binning of plots")
argParser.add_argument("--year",               action="store",      default="2016",   type=str,  choices=["2016","2017","2018","RunII"],                     help="Which year to plot?")
argParser.add_argument("--mode",               action="store",      default="all",  type=str,  choices=["mu", "e", "all"],                   help="lepton selection")
argParser.add_argument("--small",              action="store_true",                                                                          help="Run only on a small subset of the data?")
argParser.add_argument("--normalize",          action="store_true",                                                                          help="overwrite cache?")
args = argParser.parse_args()

args.binning[0] = int(args.binning[0])
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
      (0.15, 0.95, "CMS #bf{#it{Simulation Preliminary}}"),
      line
    ]
    return [tex.DrawLatex(*l) for l in lines]


if args.normalize: args.plot_directory += "_normalize"

# Sample definition
os.environ["gammaSkim"]="True" #always false for QCD estimate
if args.year == 2016:
    import TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed as mc_samples
elif args.year == 2017:
    import TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed as mc_samples
elif args.year == 2018:
    import TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed as mc_samples
elif args.year == "RunII":
    import TTGammaEFT.Samples.nanoTuples_RunII_postProcessed as mc_samples

mc = [ mc_samples.TTG, mc_samples.TTG_NLO ]

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

filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )#, skipVertexFilter=True )

for s in mc:
    s.setSelectionString( [ filterCutMc, "pTStitching==1" if not "NLO" in s.name else "1", "overlapRemoval==1" ] )
    s.read_variables = read_variables_MC
    sampleWeight     = "1"
    if args.small:           
        s.normalization = 1.
        s.reduceFiles( factor=100 )
        sampleWeight = "%f"%(1./s.normalization)

if len(args.selection.split("-")) == 1 and args.selection in allRegions.keys():
    print( "Plotting region from SetupHelpers: %s"%args.selection )

    setup = Setup( year=args.year, photonSelection=False, checkOnly=False, runOnLxPlus=False ) #photonselection always false for qcd estimate
    setup = setup.sysClone( parameters=allRegions[args.selection]["parameters"] )

    selection = setup.selection( "MC", channel=args.mode, **setup.defaultParameters() )["prefix"]
    selection = cutInterpreter.cutString( selection )
    selection += "&&triggered==1"
    if args.addCut:
        print cutInterpreter.cutString( args.addCut )
        selection += "&&" + cutInterpreter.cutString( args.addCut )
    print( "Using selection string: %s"%args.selection )

else:
    raise Exception("Region not implemented")

if args.year == 2016:
    lumi_scale = 35.92
elif args.year == 2017:
    lumi_scale = 41.53
elif args.year == 2018:
    lumi_scale = 59.74
else:
    lumi_scale = 35.92+41.53+59.74

lumiString = "(35.92*(year==2016)+41.53*(year==2017)+59.74*(year==2018))"
ws   = "(%s*weight*reweightHEM*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF)"%lumiString
ws16 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2016))" %(ws, misIDSF_val[2016].val)
ws17 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2017))" %(ws, misIDSF_val[2017].val)
ws18 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2018))" %(ws, misIDSF_val[2018].val)
weightStringAR  = ws

colors = [ROOT.kOrange, ROOT.kRed]

for i,s in enumerate(mc):
    s.setWeightString( weightStringAR + "*" + sampleWeight )
    s.hist = s.get1DHistoFromDraw( args.variable, binning=args.binning, selectionString=selection, addOverFlowBin="upper" )

    s.hist.style         = styles.lineStyle( colors[i], width=2, errors=True )
    s.hist.legendText    = s.texName

histos     = [[s.hist]    for s in mc]


m = "l" if args.mode == "all" else args.mode
replaceLabel = {
    "nJetGood":           "N_{jet}",
    "PhotonNoChgIsoNoSieie0_r9": "R9(#gamma)",
    "PhotonNoChgIsoNoSieie0_sieie": "#sigma_{i#eta i#eta}(#gamma)",
    "MET_pt": "E^{miss}_{T} [GeV]",
    "mT": "M_{T} [GeV]",
    "mLtight0Gamma": "M(#gamma,%s) [GeV]"%m,
    "LeptonTight0_eta": "#eta(%s)"%m,
    "LeptonTight0_phi": "#phi(%s)"%m,
    "LeptonTight0_pt": "p_{T}(%s) [GeV]"%m,
    "m3": "M_{3} [GeV]",
    "ht": "H_{T} [GeV]",
    "lpTight": "L_{p}",
    "JetGood0_eta": "#eta(j_{0})",
    "JetGood0_phi": "#phi(j_{0})",
    "JetGood0_pt": "p_{T}(j_{0}) [GeV]",
    "JetGood1_eta": "#eta(j_{1})",
    "JetGood1_phi": "#phi(j_{1})",
    "JetGood1_pt": "p_{T}(j_{1}) [GeV]",
    "PhotonNoChgIsoNoSieie0_pt": "p_{T}(#gamma) [GeV]",
    "PhotonNoChgIsoNoSieie0_eta": "#eta(#gamma)",
    "PhotonNoChgIsoNoSieie0_phi": "#phi(#gamma)",
    "PhotonGood0_mother": "mother pdgID (#gamma)",
    "PhotonGood0_leptonMother": "has lepton mother (#gamma)",
    "PhotonGood0_photonCatMagic": "#gamma category",
    "PhotonGood0_pt": "p_{T}(#gamma) [GeV]",
    "PhotonGood0_eta": "#eta(#gamma)",
    "PhotonGood0_phi": "#phi(#gamma)",
    "ltight0GammadPhi": "#Delta#phi(%s,#gamma)"%m,
    "ltight0GammadR": "#DeltaR(%s,#gamma)"%m,
    "photonJetdR": "min #Delta#phi(j,#gamma)",
}

Plot.setDefaults()

plots = []
plots.append( Plot.fromHisto( args.variable,             histos,        texX = replaceLabel[args.variable],                   texY = "Number of Events" ) )

for plot in plots:

    legend = [ (0.2,0.9-0.025*sum(map(len, plot.histos)),0.9,0.9), 3 ]

    for log in [True, False]:

        histModifications  = []
        histModifications += [lambda h: h.GetYaxis().SetTitleOffset(1.8 if log else 2.1)]

        ratioHistModifications  = []
        ratioHistModifications += [lambda h: h.GetYaxis().SetTitleOffset(1.8 if log else 2.1)]

        ratio = {'yRange':(0.51,1.49), "texY":"NLO/LO", "histModifications":ratioHistModifications}

        selDir = args.selection
        if args.addCut: selDir += "-" + args.addCut
        plot_directory_ = os.path.join( plot_directory, "ttgNLO", str(args.year), args.plot_directory, selDir, args.mode, "log" if log else "lin" )
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = log, sorting = True,
                       yRange = (0.3, "auto"),
                       ratio = ratio,
                       scaling = {1:0} if args.normalize else {},
                       drawObjects = drawObjects( lumi_scale ),
                       legend = legend,
                       histModifications = histModifications,
                       copyIndexPHP = True,
                       )

