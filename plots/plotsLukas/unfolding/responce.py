# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy

# RootTools
from RootTools.core.standard          import *

# Analysis
from Analysis.Tools.MergingDirDB      import MergingDirDB

# Internal Imports
from TTGammaEFT.Tools.user            import plot_directory, cache_directory
from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter

from TTGammaEFT.Analysis.SetupHelpers import *
from TTGammaEFT.Analysis.Setup        import Setup
from TTGammaEFT.Analysis.EstimatorList   import EstimatorList
from TTGammaEFT.Analysis.regions      import *

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                        help="Log level for logging")
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv1_v1",                                              help="plot sub-directory")
argParser.add_argument("--recoSelection",      action="store",      default="SR4p",                                                          help="reco region")
argParser.add_argument("--genSelection",       action="store",      default="nGenLepCMS1-nGenJetCMS4p-nGenBTagCMS1p-nGenPhotonCMS1",         help="gen selection string")
argParser.add_argument("--genPtVariable",      action="store",      default="GenPhotonCMSUnfold0_pt",                                        help="gen photon pt variable")
argParser.add_argument("--genBinning",         action="store",      default=[10,20,220], type=int, nargs=3,                                  help="binning gen: nBins, lowPt, highPt")
argParser.add_argument("--recoBinning",        action="store",      default=[30,20,220], type=int, nargs=3,                                  help="binning reco: nBins, lowPt, highPt")
argParser.add_argument("--year",               action="store",      default="2016",   type=str,  choices=["2016","2017","2018","RunII"],                     help="Which year to plot?")
argParser.add_argument("--mode",               action="store",      default="all",  type=str,  choices=["mu", "e", "all"],                   help="lepton selection")
argParser.add_argument("--ttgSingleLep",       action="store_true",                                                                          help="Run on ttg single lepton sample only?")
argParser.add_argument("--normalize",          action="store_true",                                                                          help="Scale to 1 fb-1?")
argParser.add_argument("--small",              action="store_true",                                                                          help="Run only on a small subset of the data?")
argParser.add_argument("--noData",             action="store_true",                                                                          help="also plot data?")
argParser.add_argument("--overwrite",          action="store_true",                                                                          help="overwrite cache?")
args = argParser.parse_args()

if args.year != "RunII": args.year = int(args.year)

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile=None )
logger_rt = logger_rt.get_logger( args.logLevel, logFile=None )

# Text on the plots
def drawObjects( plotData, lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    line = (0.68, 0.95, "%3.1f fb^{-1} (13 TeV)" % lumi_scale)
    lines = [
      (0.15, 0.95, "CMS #bf{#it{Preliminary}}" if plotData else "CMS #bf{#it{Simulation Preliminary}}"), 
      line
    ]
    return [tex.DrawLatex(*l) for l in lines]

if args.small:        args.plot_directory += "_small"
if args.noData:       args.plot_directory += "_noData"
if args.normalize:    args.plot_directory += "_normalized"
if args.ttgSingleLep: args.plot_directory += "_singleLep"

# get reco selection criteria lambda function
selection     = signalRegions[args.recoSelection]["lambda"]
setup         = Setup( year=args.year, photonSelection=False, checkOnly=True, runOnLxPlus=False ) #photonselection always false for qcd estimate
setup         = setup.sysClone( parameters=allRegions[args.recoSelection]["parameters"] )
recoselection = setup.selection( "MC", channel="all", **setup.defaultParameters() )
recoSelection = recoselection["prefix"]

nGen,  xminGen,  xmaxGen  = args.genBinning
nReco, xminReco, xmaxReco = args.recoBinning

if   args.year == 2016: lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74
elif args.year == "RunII": lumi_scale = 35.92 + 41.53 + 59.74

if args.normalize:
    lumi_scale = 1.

plot_directory_ = os.path.join( plot_directory, "unfolding", str(args.year), args.plot_directory, args.genSelection, args.recoSelection, args.mode )

reconstructionBinning = [ 50, 0.6, 2 ]

if args.year == 2016:
    from TTGammaEFT.Samples.nanoTuples_Summer16_private_incl_postProcessed         import TTGSemiLep, TTG
elif args.year == 2017:
    from TTGammaEFT.Samples.nanoTuples_Fall17_private_incl_postProcessed           import TTGSemiLep, TTG
elif args.year == 2018:
    from TTGammaEFT.Samples.nanoTuples_Autumn18_private_incl_postProcessed         import TTGSemiLep, TTG
elif args.year == "RunII":
    from TTGammaEFT.Samples.nanoTuples_RunII_postProcessed                         import TTGSemiLep, TTG
sample = TTGSemiLep if args.ttgSingleLep else TTG

norm = 1.
if args.small:           
    sample.normalization=1.
    sample.reduceFiles( factor=100 )
    norm = 1./sample.normalization

read_variables = [ "weight/F",
                   "nPhotonGood/I", "nJetGood/I", "nBTagGood/I", "nLeptonTight/I", "nLeptonVetoIsoCorr/I",
                   "PhotonGood0_pt/F",
                   "GenPhotonATLASUnfold0_pt/F", "GenPhotonCMSUnfold0_pt/F",
                   "nGenLeptonATLASUnfold/I", "nGenPhotonATLASUnfold/I", "nGenBJetATLASUnfold/I", "nGenJetsATLASUnfold/I",
                   "nGenLeptonCMSUnfold/I", "nGenPhotonCMSUnfold/I", "nGenBJetCMSUnfold/I", "nGenJetsCMSUnfold/I",
                 ]

# reconstruction pt binned plot
sample.color             = ROOT.kBlack
sample.texName           = "Inverse Response (p_{T}(#gamma^{gen}) #geq 20 GeV)"
sample.setSelectionString("%s>=20"%(args.genPtVariable))
sample_pt20to40          = copy.deepcopy(sample)
sample_pt20to40.texName  = "Inverse Response (20 #leq p_{T}(#gamma^{gen}) < 40 GeV)"
sample_pt20to40.color    = ROOT.kBlue
sample_pt20to40.setSelectionString("%s>=20&&%s<40"%(args.genPtVariable,args.genPtVariable))
sample_pt40to60          = copy.deepcopy(sample)
sample_pt40to60.color    = ROOT.kCyan+1
sample_pt40to60.texName  = "Inverse Response (40 #leq p_{T}(#gamma^{gen}) < 60 GeV)"
sample_pt40to60.setSelectionString("%s>=40&&%s<60"%(args.genPtVariable,args.genPtVariable))
sample_pt60to120         = copy.deepcopy(sample)
sample_pt60to120.color   = ROOT.kGreen-2
sample_pt60to120.texName = "Inverse Response (60 #leq p_{T}(#gamma^{gen}) < 120 GeV)"
sample_pt60to120.setSelectionString("%s>=60&&%s<120"%(args.genPtVariable,args.genPtVariable))
sample_pt120             = copy.deepcopy(sample)
sample_pt120.color       = ROOT.kRed-3
sample_pt120.texName     = "Inverse Response (p_{T}(#gamma^{gen}) #geq 120 GeV)"
sample_pt120.setSelectionString("%s>=120"%(args.genPtVariable))

reconstructionSamples = [sample_pt120, sample_pt60to120, sample_pt40to60, sample_pt20to40, sample]
stack                 = Stack( sample_pt120, sample_pt60to120, sample_pt40to60, sample_pt20to40, sample )
weight_               = lambda event, sample: event.weight * norm * lumi_scale

Plot.setDefaults( stack=stack, weight=staticmethod( weight_ ), selectionString=cutInterpreter.cutString( args.genSelection ) )

reconstruction = Plot(
                       name      = "reconstruction_pT",
                       texX      = "p^{gen}_{T}(#gamma) / p^{reco}_{T}(#gamma)",
                       texY      = "Number of Events",
                       attribute = lambda event, sample: getattr( event, args.genPtVariable ) / event.PhotonGood0_pt if selection( event, sample ) else -999,
                       binning   = reconstructionBinning,
                       read_variables = read_variables,
                      )

plotting.fill( [reconstruction], read_variables=read_variables )

for i_h, h in enumerate(reconstruction.histos):
    h[0].style = styles.errorStyle( reconstructionSamples[i_h].color )

plotting.draw( reconstruction,
               plot_directory = plot_directory_,
               logX = False, logY = True, sorting = False,
               scaling = { i:len(reconstructionSamples)-1 for i in range(len(reconstructionSamples)) },
               yRange = (0.01, "auto"),
               drawObjects = drawObjects( not args.noData, lumi_scale ),
               legend = [ (0.2,0.88-0.04*len(reconstruction.histos),0.88,0.88), 1 ],
               copyIndexPHP = True,
               )

