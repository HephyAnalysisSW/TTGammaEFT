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
#from TTGammaEFT.Tools.TriggerSelector  import TriggerSelector

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
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv26_v1",                                             help="plot sub-directory")
argParser.add_argument("--selection",          action="store",      default="WJets2", type=str,                                              help="reco region")
argParser.add_argument("--addCut",             action="store",      default=None, type=str,                                                  help="additional cuts")
argParser.add_argument("--variable",           action="store",      default="LeptonTight0_eta", type=str,                                    help="variable to plot")
argParser.add_argument("--binning",            action="store",      default=[20,-2.4,2.4],  type=float, nargs="*",                           help="binning of plots")
argParser.add_argument("--year",               action="store",      default=2016,   type=int,  choices=[2016,2017,2018],                     help="Which year to plot?")
argParser.add_argument("--mode",               action="store",      default="all",  type=str,  choices=["mu", "e", "all"],                   help="lepton selection")
argParser.add_argument("--small",              action="store_true",                                                                          help="Run only on a small subset of the data?")
argParser.add_argument("--survey",             action="store_true",                                                                          help="all plots in one directory?")
argParser.add_argument("--photonCat",          action="store_true",                                                                          help="all plots in one directory?")
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

cache_dir = os.path.join(cache_directory, "drawHistos", "all", args.selection, args.mode)
dirDB = MergingDirDB(cache_dir)
if not dirDB: raise

# Sample definition
os.environ["gammaSkim"]="False" #always false for QCD estimate
from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed  import *
from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import *
mc16   = all_noQCD_16
data16 = Run2016
from TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed    import *
from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import *
mc17   = all_noQCD_17
data17 = Run2017
from TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed  import *
from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import *
mc18   = all_noQCD_18
data18 = Run2018

lumi_scale   = (data16.lumi + data17.lumi + data18.lumi) * 0.001

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


filterCutMC = getFilterCut( 2016, isData=False,  skipBadChargedCandidate=True )
weightString    = "%f*weight*reweightHEM*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF"%lumi_scale
weightStringAR  = "((%s)+(%s*%f*((nPhotonNoChgIsoNoSieie>0)*(PhotonNoChgIsoNoSieie0_photonCatMagic==2))))"%(weightString,weightString,(misIDSF_val[2016].val-1))
mc16.setSelectionString( [filterCutMC, "pTStitching==1", "reweightHEM>0", cutInterpreter.cutString( args.mode )] )
mc16.setWeightString( weightStringAR )

filterCutMC = getFilterCut( 2017, isData=False,  skipBadChargedCandidate=True )
weightString    = "%f*weight*reweightHEM*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF"%lumi_scale
weightStringAR  = "((%s)+(%s*%f*((nPhotonNoChgIsoNoSieie>0)*(PhotonNoChgIsoNoSieie0_photonCatMagic==2))))"%(weightString,weightString,(misIDSF_val[2017].val-1))
mc17.setSelectionString( [filterCutMC, "pTStitching==1", "reweightHEM>0", cutInterpreter.cutString( args.mode )] )
mc17.setWeightString( weightStringAR )

filterCutMC = getFilterCut( 2018, isData=False,  skipBadChargedCandidate=True )
weightString    = "%f*weight*reweightHEM*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF"%lumi_scale
weightStringAR  = "((%s)+(%s*%f*((nPhotonNoChgIsoNoSieie>0)*(PhotonNoChgIsoNoSieie0_photonCatMagic==2))))"%(weightString,weightString,(misIDSF_val[2018].val-1))
mc18.setSelectionString( [filterCutMC, "pTStitching==1", "reweightHEM>0", cutInterpreter.cutString( args.mode )] )
mc18.setWeightString( weightStringAR )

setup = Setup( year=2016, photonSelection=False, checkOnly=False, runOnLxPlus=False ) #photonselection always false for qcd estimate
setup = setup.sysClone( parameters=allRegions[args.selection]["parameters"] )

selection = setup.selection( "MC", channel="all", **setup.defaultParameters() )["prefix"]
selection = cutInterpreter.cutString( selection )
selection += "&&pTStitching==1&&triggered==1"
print selection
if args.addCut:
    selection += "&&" + cutInterpreter.cutString( args.addCut )
print( "Using selection string: %s"%selection )


key = (mc18.name, "18", args.variable, "_".join(map(str,args.binning)), mc18.weightString, mc18.selectionString, selection)
if dirDB.contains(key) and not args.overwrite:
    mcHist18 = dirDB.get(key).Clone("18")
else:
    mcHist18 = mc18.get1DHistoFromDraw( args.variable, binning=args.binning, selectionString=selection )
    dirDB.add(key, mcHist18.Clone("18"), overwrite=True)

key = (mc17.name, "17", args.variable, "_".join(map(str,args.binning)), mc17.weightString, mc17.selectionString, selection)
if dirDB.contains(key) and not args.overwrite:
    mcHist17 = dirDB.get(key).Clone("17")
else:
    mcHist17 = mc17.get1DHistoFromDraw( args.variable, binning=args.binning, selectionString=selection )
    dirDB.add(key, mcHist17.Clone("17"), overwrite=True)

key = (mc16.name, "16", args.variable, "_".join(map(str,args.binning)), mc16.weightString, mc16.selectionString, selection)
if dirDB.contains(key) and not args.overwrite:
    mcHist16 = dirDB.get(key).Clone("16")
else:
    mcHist16 = mc16.get1DHistoFromDraw( args.variable, binning=args.binning, selectionString=selection )
    dirDB.add(key, mcHist16.Clone("16"), overwrite=True)

mcHist16.style         = styles.lineStyle( ROOT.kBlack, width=2, errors=True )
mcHist16.legendText    = "MC (2016)"

mcHist17.style         = styles.lineStyle( ROOT.kRed, width=2, errors=True )
mcHist17.legendText    = "MC (2017)"

mcHist18.style         = styles.lineStyle( ROOT.kBlue, width=2, errors=True )
mcHist18.legendText    = "MC (2018)"

histos     = [[mcHist16], [mcHist17], [mcHist18]]

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

        ratio = {'yRange':(0.1,1.9), 'histos':[(0,1),(2,1)], 'texY': 'MC/MC'}

        selDir = args.selection
        if args.addCut and not args.survey: selDir += "-" + args.addCut
        plot_directory_ = os.path.join( plot_directory, "fakeMcHistos", "all", args.plot_directory, selDir, args.mode, "log" if log else "lin" )
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = log, #sorting = True,#plot.name != "mT_fit",
                       yRange = (0.3, "auto"),
                       ratio = ratio,
                       drawObjects = drawObjects( lumi_scale ),
                       scaling = { 1:0, 2:0 },
                       legend = legend,
                       copyIndexPHP = True,
                       )

