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
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv49_vdiss",                                             help="plot sub-directory")
argParser.add_argument("--selection",          action="store",      default="SR3p", type=str,                                              help="reco region")
argParser.add_argument("--addCut",             action="store",      default=None, type=str,                                                  help="additional cuts")
argParser.add_argument("--variable",           action="store",      default="PhotonGood0_pt", type=str,                                    help="variable to plot")
argParser.add_argument("--binning",            action="store",      default=[20,20,320],  type=float, nargs="*",                           help="binning of plots")
argParser.add_argument("--year",               action="store",      default="RunII",   type=str,  choices=["2016","2017","2018","RunII"],                     help="Which year to plot?")
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
def drawObjects( lumi_scale, log=False ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right

    tex2 = ROOT.TLatex()
    tex2.SetNDC()
#    tex2.SetTextSize(0.058)
    tex2.SetTextSize(0.05)
    tex2.SetTextAlign(11) # align right
#    line = (0.65, 0.95, "%3.1f fb^{-1} (13 TeV)" % lumi_scale)
    line = (0.68, 0.95, "%i fb^{-1} (13 TeV)" % lumi_scale)
    line2 = (0.15, 0.95, "Private Work")
    line3 = (0.42, 0.95, "#bf{#it{Simulation}}")

#    lines2 = (0.235 if not log and (args.selection.startswith("WJets") or args.selection.startswith("TT")) else 0.15, 0.95, "CMS #bf{#it{Preliminary}}%s"%(" (%s)"%(replaceRegionNaming[args.selection.repl$
#    line2 = (0.235 if not log and (args.selection.startswith("WJets") or args.selection.startswith("TT")) else 0.15, 0.95, "CMS%s"%(" (%s)"%(replaceRegionNaming[args.selection.replace("fake","SR")] if ar$
    return [tex2.DrawLatex(*line2), tex.DrawLatex(*line3), tex.DrawLatex(*line)]

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

mc = [ [mc_samples.TTG], [mc_samples.TTG_NLO, mc_samples.TT_pow] ]
#mc = [ [mc_samples.TTG], [mc_samples.TT_pow] ]

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

for mcl in mc:
  for s in mcl:
    if "NLO" in s.name:
        s.setSelectionString( [ filterCutMc, "(abs(PhotonGood0_mother)==21||abs(PhotonGood0_mother)<=6)","PhotonGood0_photonCatMagic==0" ] )
#        s.setSelectionString( [ filterCutMc, "(abs(PhotonGood0_mother)==21||abs(PhotonGood0_mother)==6)","PhotonGood0_photonCatMagic==0" ] )
    elif "TT_pow" in s.name:
        s.setSelectionString( [ filterCutMc, "!(abs(PhotonGood0_mother)==21||abs(PhotonGood0_mother)<=6)","PhotonGood0_photonCatMagic==0" ] )
#        s.setSelectionString( [ filterCutMc, "!(abs(PhotonGood0_mother)==21||abs(PhotonGood0_mother)==6)","PhotonGood0_photonCatMagic==0" ] )
    else:
        s.setSelectionString( [ filterCutMc, "pTStitching==1","PhotonGood0_photonCatMagic==0" ] )

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

colors = [[ROOT.kGreen-2], [ROOT.kBlue, ROOT.kRed]]

for i_m, mcl in enumerate(mc):
  for i,s in enumerate(mcl):
    s.setWeightString( weightStringAR + "*" + sampleWeight )
    s.hist = s.get1DHistoFromDraw( args.variable, binning=args.binning, selectionString=selection, addOverFlowBin="upper" )

    print s.name
    for j in range(s.hist.GetNbinsX()):
        print i+1, s.hist.GetBinContent(j+1)
    print

    s.hist.style         = styles.lineStyle( colors[i_m][i], width=3, errors=True )
#    s.hist.Scale(1./137.2)
    if "TT_pow" in s.name:
        s.hist.legendText    = "t#bar{t}#gamma (NLO)"
    elif not "NLO" in s.name:
        s.hist.legendText    = s.texName + " (LO)"
    else:
        s.hist.legendText    = None

histos     = [[s.hist for s in mcl][::-1] for mcl in mc][::-1]


m = "l" if args.mode == "all" else args.mode
replaceLabel = {
    "nBTagGood":           "N_{b}",
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
    "abs(PhotonGood0_eta)": "|#eta(#gamma)|",
    "PhotonGood0_phi": "#phi(#gamma)",
    "ltight0GammadPhi": "#Delta#phi(%s,#gamma)"%m,
    "ltight0GammadR": "#DeltaR(%s,#gamma)"%m,
    "photonJetdR": "min #Delta#phi(j,#gamma)",
}

Plot.setDefaults()

lower = 15
#lower = 501
#lower = 1001

plots = []
if "PhotonGood0_pt" in args.variable:
    units = " / 20 GeV"
elif "PhotonGood0_eta" in args.variable:
    units = " / 0.15 units"
elif "ltight0GammadR" in args.variable:
    units = " / 0.2 units"
else:
    units = ""
plots.append( Plot.fromHisto( args.variable,             histos,        texX = replaceLabel[args.variable],                   texY = "Events"+units ) )

for plot in plots:

    legend = [ (0.2,0.75,0.8,0.86), 1 ]

    for log in [True, False]:

        histModifications  = []
        histModifications += [lambda h: h.GetYaxis().SetTitleOffset(1.8 if log else 2.1)]

        ratioHistModifications  = []
        ratioHistModifications += [lambda h: h.GetYaxis().SetTitleOffset(1.8 if log else 2.1)]

        ratio = {'yRange':(0.76,1.24), "texY":"NLO / LO", "histModifications":ratioHistModifications, 'histos':[(0,1)]}

        selDir = args.selection
        if args.addCut: selDir += "-" + args.addCut
        plot_directory_ = os.path.join( plot_directory, "ttgNLO", str(args.year), args.plot_directory+"_wttbar", selDir, args.mode, "log" if log else "lin" )
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = log, sorting = True,
#                       yRange = (lower, "auto"),
                       yRange = (lower, 90000),
                       ratio = ratio,
                       scaling = {0:1} if args.normalize else {0:1},
                       drawObjects = drawObjects( lumi_scale ),
                       legend = legend,
                       histModifications = histModifications,
                       copyIndexPHP = True,
                       )

