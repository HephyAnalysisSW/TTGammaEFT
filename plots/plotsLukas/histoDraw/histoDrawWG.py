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
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv47_v4WG",                                             help="plot sub-directory")
argParser.add_argument("--selection",          action="store",      default="VG2p", type=str,                                              help="reco region")
argParser.add_argument("--addCut",             action="store",      default=None, type=str,                                                  help="additional cuts")
argParser.add_argument("--variable",           action="store",      default="nJetGood", type=str,                                    help="variable to plot")
argParser.add_argument("--binning",            action="store",      default=[5,2,7],  type=float, nargs="*",                           help="binning of plots")
argParser.add_argument("--year",               action="store",      default="2016",   type=str,  choices=["2016","2017","2018","RunII"],                     help="Which year to plot?")
argParser.add_argument("--mode",               action="store",      default="all",  type=str,  choices=["mu", "e", "all"],                   help="lepton selection")
argParser.add_argument("--small",              action="store_true",                                                                          help="Run only on a small subset of the data?")
argParser.add_argument("--overwrite",          action="store_true",                                                                          help="overwrite cache?")
argParser.add_argument("--postfit",            action="store_true",                                                                          help="overwrite cache?")
args = argParser.parse_args()

args.binning[0] = int(args.binning[0])
addSF = args.postfit
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
    line = (0.65, 0.95, "%3.1f fb{}^{-1} (13 TeV)" % lumi_scale)
    lines = [
      (0.15, 0.95, "CMS #bf{#it{Preliminary}}"),
      line
    ]
    return [tex.DrawLatex(*l) for l in lines]

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

mc = mc_samples.WG
#mc = mc_samples.WJets

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

filterCutData = getFilterCut( args.year, isData=True,  skipBadChargedCandidate=True )#, skipVertexFilter=True )
filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )#, skipVertexFilter=True )
#tr            = TriggerSelector( args.year, singleLepton=True )
#triggerCutMc  = tr.getSelection( "MC" )

mc.setSelectionString( [ filterCutMc, "pTStitching==1" ] ) #, "overlapRemoval==1" ] )
mc.read_variables = read_variables_MC

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


lumiString = "(35.92*(year==2016)+41.53*(year==2017)+59.74*(year==2018))"
ws   = "(%s*weight*reweightHEM*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF)"%lumiString
ws16 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2016))" %(ws, misIDSF_val[2016].val)
ws17 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2017))" %(ws, misIDSF_val[2017].val)
ws18 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2018))" %(ws, misIDSF_val[2018].val)
if not addSF:
    weightStringAR  = ws
else:
    weightStringAR = ws + ws16 + ws17 + ws18

print selection
print weightStringAR
mc.setWeightString( weightStringAR )
hist = mc.get1DHistoFromDraw( "nJetGood", binning=[5,2,7], selectionString=selection, addOverFlowBin="upper" )
#histdR = mc.get1DHistoFromDraw( "nJetGood", binning=[5,2,7], selectionString=selection+"&&genJetCMSGammadR>0.7", addOverFlowBin="upper" )
#histdR = mc.get1DHistoFromDraw( "nJetGood", binning=[5,2,7], selectionString=selection+"&&photonJetdR<0.7", addOverFlowBin="upper" )
#histdR = mc.get1DHistoFromDraw( "nJetGood", binning=[5,2,7], selectionString=selection+"&&Min$(sqrt((GenJet_eta-GenPhoton_eta)**2+acos(cos(GenJet_phi-GenPhoton_phi))**2))<0.7", addOverFlowBin="upper" )
histdR05 = mc.get1DHistoFromDraw( "nJetGood", binning=[5,2,7], selectionString=selection+"&&Min$(sqrt((GenJet_eta-GenPhoton_eta[0])**2+acos(cos(GenJet_phi-GenPhoton_phi[0]))**2))>0.05", addOverFlowBin="upper" )
histdR1 = mc.get1DHistoFromDraw( "nJetGood", binning=[5,2,7], selectionString=selection+"&&Min$(sqrt((GenJet_eta-GenPhoton_eta[0])**2+acos(cos(GenJet_phi-GenPhoton_phi[0]))**2))>0.1", addOverFlowBin="upper" )
histdR2 = mc.get1DHistoFromDraw( "nJetGood", binning=[5,2,7], selectionString=selection+"&&Min$(sqrt((GenJet_eta-GenPhoton_eta[0])**2+acos(cos(GenJet_phi-GenPhoton_phi[0]))**2))>0.2", addOverFlowBin="upper" )
histdR3 = mc.get1DHistoFromDraw( "nJetGood", binning=[5,2,7], selectionString=selection+"&&Min$(sqrt((GenJet_eta-GenPhoton_eta[0])**2+acos(cos(GenJet_phi-GenPhoton_phi[0]))**2))>0.3", addOverFlowBin="upper" )
histdR4 = mc.get1DHistoFromDraw( "nJetGood", binning=[5,2,7], selectionString=selection+"&&Min$(sqrt((GenJet_eta-GenPhoton_eta[0])**2+acos(cos(GenJet_phi-GenPhoton_phi[0]))**2))>0.4", addOverFlowBin="upper" )
histdR5 = mc.get1DHistoFromDraw( "nJetGood", binning=[5,2,7], selectionString=selection+"&&Min$(sqrt((GenJet_eta-GenPhoton_eta[0])**2+acos(cos(GenJet_phi-GenPhoton_phi[0]))**2))>0.5", addOverFlowBin="upper" )

hist.style         = styles.lineStyle( ROOT.kRed, width=2 )
hist.legendText    = "W#gamma inclusive"
#hist.legendText    = "W+Jets inclusive"
histdR05.style         = styles.lineStyle( ROOT.kBlue, width=2 )
histdR05.legendText    = "W#gamma min #DeltaR(gen-jet,#gamma)#geq 0.05"
#histdR05.legendText    = "W+Jets min #DeltaR(gen-jet,#gamma)#leq 0.05"

histdR1.style         = styles.lineStyle( ROOT.kGreen, width=2 )
histdR1.legendText    = "W#gamma min #DeltaR(gen-jet,#gamma)#geq 0.1"
#histdR1.legendText    = "W+Jets min #DeltaR(gen-jet,#gamma)#leq 0.1"

histdR2.style         = styles.lineStyle( ROOT.kAzure, width=2 )
histdR2.legendText    = "W#gamma min #DeltaR(gen-jet,#gamma)#geq 0.2"
#histdR1.legendText    = "W+Jets min #DeltaR(gen-jet,#gamma)#leq 0.2"

histdR3.style         = styles.lineStyle( ROOT.kOrange, width=2 )
histdR3.legendText    = "W#gamma min #DeltaR(gen-jet,#gamma)#geq 0.3"
#histdR3.legendText    = "W+Jets min #DeltaR(gen-jet,#gamma)#leq 0.3"

histdR4.style         = styles.lineStyle( ROOT.kSpring, width=2 )
histdR4.legendText    = "W#gamma min #DeltaR(gen-jet,#gamma)#geq 0.4"
#histdR4.legendText    = "W+Jets min #DeltaR(gen-jet,#gamma)#leq 0.4"

histdR5.style         = styles.lineStyle( ROOT.kBlack, width=2 )
histdR5.legendText    = "W#gamma min #DeltaR(gen-jet,#gamma)#geq 0.5"
#histdR5.legendText    = "W+Jets min #DeltaR(gen-jet,#gamma)#leq 0.5"

histos     = [[hist], [histdR05], [histdR1], [histdR2], [histdR3], [histdR4], [histdR5]]

Plot.setDefaults()

plots = []
plots.append( Plot.fromHisto( "nJetGood", histos,        texX = "N_{jet}",                   texY = "Number of Events" ) )

for plot in plots:

    legend = [ (0.2,0.9-0.025*sum(map(len, plot.histos)),0.9,0.9), 2 ]

    for log in [True, False]:

        ratio = {'histos':[(1,0),(2,0),(3,0),(4,0),(5,0),(6,0)],'yRange':(0.1,1.9), 'logY':True }

        selDir = args.selection
        if args.addCut: selDir += "-" + args.addCut
        plot_directory_ = os.path.join( plot_directory, "WGChecks", str(args.year), args.plot_directory, selDir, "postfit" if addSF else "prefit", args.mode, "log" if log else "lin" )
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = log, sorting = True,
                       yRange = (0.3, "auto"),
                       ratio = ratio,
#                       scaling={1:0,2:0,3:0,4:0,5:0,6:0},
                       drawObjects = drawObjects( lumi_scale ),
                       legend = legend,
                       copyIndexPHP = True,
                       )

