# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy

# RootTools
from RootTools.core.standard          import *

# Internal Imports
from TTGammaEFT.Tools.user            import plot_directory
from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter

#from TTGammaEFT.Analysis.SetupHelpers import *
#from TTGammaEFT.Analysis.Setup        import Setup
#from TTGammaEFT.Analysis.EstimatorList   import EstimatorList
#from TTGammaEFT.Analysis.regions      import *

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                        help="Log level for logging")
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv1_v1",                                              help="plot sub-directory")
#argParser.add_argument("--recoSelection",      action="store",      default="SR4p",                                                          help="reco region")
argParser.add_argument("--genSelection",       action="store",      default="nGenLepCMS1-nGenJetCMS4p-nGenBTagCMS1p-nGenPhotonCMS1",         help="gen selection string")
#argParser.add_argument("--genPtVariable",      action="store",      default="GenPhotonCMSUnfold0_pt",                                        help="gen photon pt variable")
argParser.add_argument("--year",               action="store",      default="2016",   type=str,  choices=["2016","2017","2018","RunII"],                     help="Which year to plot?")
argParser.add_argument("--mode",               action="store",      default="all",  type=str,  choices=["mu", "e", "all"],                   help="lepton selection")
argParser.add_argument("--ttgSingleLep",       action="store_true",                                                                          help="Run on ttg single lepton sample only?")
argParser.add_argument("--normalize",          action="store_true",                                                                          help="Scale to 1 fb-1?")
argParser.add_argument("--small",              action="store_true",                                                                          help="Run only on a small subset of the data?")
args = argParser.parse_args()

if args.year != "RunII": args.year = int(args.year)

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile=None )
logger_rt = logger_rt.get_logger( args.logLevel, logFile=None )

if args.small:        args.plot_directory += "_small"
if args.normalize:    args.plot_directory += "_normalized"
if args.ttgSingleLep: args.plot_directory += "_singleLep"

# get reco selection criteria lambda function
#selection     = signalRegions[args.recoSelection]["lambda"]
#setup         = Setup( year=args.year, photonSelection=False, checkOnly=True, runOnLxPlus=False ) #photonselection always false for qcd estimate
#setup         = setup.sysClone( parameters=allRegions[args.recoSelection]["parameters"] )
#recoselection = setup.selection( "MC", channel="all", **setup.defaultParameters() )
#recoSelection = recoselection["prefix"]

if   args.year == 2016: lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74
elif args.year == "RunII": lumi_scale = 35.92 + 41.53 + 59.74

if args.normalize:
    lumi_scale = 1.

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
    sample.reduceFiles( factor=20 )
    norm = 1./sample.normalization

read_variables = [ "weight/F",
                   "nPhotonGood/I", "nJetGood/I", "nBTagGood/I", "nLeptonTight/I", "nLeptonVetoIsoCorr/I",
                   "PhotonGood0_pt/F",
                   "GenPhotonATLASUnfold0_pt/F", "GenPhotonCMSUnfold0_pt/F",
                   "GenPhotonATLASUnfold0_eta/F", "GenPhotonCMSUnfold0_eta/F",
                   "nGenLeptonATLASUnfold/I", "nGenPhotonATLASUnfold/I", "nGenBJetATLASUnfold/I", "nGenJetsATLASUnfold/I",
                   "nGenLeptonCMSUnfold/I", "nGenPhotonCMSUnfold/I", "nGenBJetCMSUnfold/I", "nGenJetsCMSUnfold/I",
                 ]

weight_ = lambda event, sample: event.weight * norm * lumi_scale
Plot.setDefaults(   stack=Stack( [sample] ), weight=staticmethod( weight_ ), selectionString=cutInterpreter.cutString( args.genSelection ) )

plots = []

plots.append( Plot(
                   name      = "GenPhotonCMSUnfold0_pt",
                   texX      = "p^{gen}_{T}(#gamma_{0})",
                   attribute = lambda event, sample: event.GenPhotonCMSUnfold0_pt,
                   binning   = [20, 20, 220],
                  ) )

plots.append( Plot(
                   name      = "GenPhotonCMSUnfold0_eta",
                   texX      = "p^{gen}_{T}(#gamma_{0})",
                   attribute = lambda event, sample: event.GenPhotonCMSUnfold0_eta,
                   binning   = [10, -2, 2],
                  ) )

plots.append( Plot(
                   name      = "nGenPhotonCMSUnfold",
                   texX      = "N^{gen}_{#gamma}",
                   attribute = lambda event, sample: event.nGenPhotonCMSUnfold,
                   binning   = [5, 0, 5],
                  ) )

plots.append( Plot(
                   name      = "nGenJetsCMSUnfold",
                   texX      = "N^{gen}_{jets}",
                   attribute = lambda event, sample: event.nGenJetsCMSUnfold,
                   binning   = [10, 0, 10],
                  ) )

plots.append( Plot(
                   name      = "nGenBJetsCMSUnfold",
                   texX      = "N^{gen}_{b-jets}",
                   attribute = lambda event, sample: event.nGenBJetCMSUnfold,
                   binning   = [5, 0, 5],
                  ) )

plotting.fill( plots, read_variables=read_variables )

addons = []
if args.ttgSingleLep:  addons.append("tt#gamma 1l")
else:                  addons.append("tt#gamma")
if args.mode != "all": addons.append(args.mode.replace("mu","#mu"))

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

for plot in plots:

    for histos in plot.histos:
        for h in histos:
            h.style      = styles.lineStyle( ROOT.kBlue, width = 2 )
            h.legendText = "Generated Events (%s)"%", ".join(addons)

    for log in [True, False]:
        plot_directory_ = os.path.join( plot_directory, "unfolding", str(args.year), args.plot_directory, args.genSelection, "distributions", args.mode, "log" if log else "lin" )
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = log, sorting = False,
                       yRange = (0.001, "auto"),
                       drawObjects = drawObjects( False, lumi_scale ),
                       legend = [ (0.3,0.88-0.04*len(plot.histos),0.88,0.88), 1 ],
                       copyIndexPHP = True,
                       )


