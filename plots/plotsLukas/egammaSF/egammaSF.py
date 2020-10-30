# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy

# RootTools
from RootTools.core.standard           import *

# Analysis
#import Analysis.Tools.syncer as syncer

# Internal Imports
from TTGammaEFT.Tools.user             import plot_directory
from TTGammaEFT.Tools.cutInterpreter   import cutInterpreter

from TTGammaEFT.Samples.color          import color

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                        help="Log level for logging")
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv26_v1",                                             help="plot sub-directory")
argParser.add_argument("--selection",          action="store",      default="WJets2", type=str,                                              help="reco region")
argParser.add_argument("--variable",           action="store",      default="LeptonTight0_eta", type=str,                                    help="variable to plot")
argParser.add_argument("--binning",            action="store",      default=[20,-2.4,2.4],  type=float, nargs="*",                           help="binning of plots")
argParser.add_argument("--year",               action="store",      default=2016,   type=int,  choices=[2016,2017,2018],                     help="Which year to plot?")
argParser.add_argument('--useZG',              action='store_true',                                                                    help='Run on DY+ZG w overlap removal', )
args = argParser.parse_args()

args.binning[0] = int(args.binning[0])

if args.useZG: args.plot_directory += "_ZG"
else:          args.plot_directory += "_DY"

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
if args.year == 2016:
    import TTGammaEFT.Samples.nanoTuples_Summer16_private_diMuGamma_postProcessed as mc_samples
    from   TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_diMuGamma_postProcessed import Run2016 as data_sample
elif args.year == 2017:
    import TTGammaEFT.Samples.nanoTuples_Fall17_private_diMuGamma_postProcessed as mc_samples
    from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_diMuGamma_postProcessed import Run2017 as data_sample
elif args.year == 2018:
    import TTGammaEFT.Samples.nanoTuples_Autumn18_private_diMuGamma_postProcessed as mc_samples
    from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_diMuGamma_postProcessed import Run2018 as data_sample

mc = [ mc_samples.TT_pow, mc_samples.DY_LO, mc_samples.WJets ]
#if args.useZG: mc += [mc_samples.ZG]
if args.useZG: mc += [mc_samples.ZG_lowpt]

mc_samples.ZG_lowpt.setWeightString("0.8")

lumi_scale   = data_sample.lumi * 0.001

selection  = cutInterpreter.cutString( args.selection )
selection += "&&reweightPU<2&&jsonPassed==1"
if args.useZG: selection += "&&overlapRemoval==1"

weightString = "%f*weight*reweightPU"%lumi_scale

dataHist = data_sample.get1DHistoFromDraw( args.variable, binning=args.binning, selectionString=selection, addOverFlowBin="upper" )
for s in mc:
    s.hist = s.get1DHistoFromDraw( args.variable, binning=args.binning, selectionString=selection, weightString=weightString, addOverFlowBin="upper" )
    s.hist.style         = styles.fillStyle( s.color )
    s.hist.legendText    = s.texName

dataHist.style         = styles.errorStyle( ROOT.kBlack )
dataHist.legendText    = "data (#mu#mu#gamma)"

replaceLabel = {
    "PV_npvsGood": "N_{vertex}",
    "nPhotonMVA": "N_{#gamma}",
    "nPhotonLoose": "N_{#gamma}",
    "nPhotonMedium": "N_{#gamma}",
    "nPhotonTight": "N_{#gamma}",
    "nMuonTight": "N_{#mu}",
    "nJetGood": "N_{jet}",
    "nBTagGood": "N_{b-jet}",
    "MET_pt": "E^{miss}_{T} (GeV)",
    "MuonTight0_eta": "#eta(#mu_{0})",
    "MuonTight0_phi": "#phi(#mu_{0})",
    "MuonTight0_pt": "p_{T}(#mu_{0}) (GeV)",
    "MuonTight1_eta": "#eta(#mu_{1})",
    "MuonTight1_phi": "#phi(#mu_{1})",
    "MuonTight1_pt": "p_{T}(#mu_{1}) (GeV)",
    "mll": "m(#mu,#mu) (GeV)",
    "mllgL": "m(#mu,#mu,#gamma) (GeV)",
    "mllgM": "m(#mu,#mu,#gamma) (GeV)",
    "mllgT": "m(#mu,#mu,#gamma) (GeV)",
    "mllgMVA": "m(#mu,#mu,#gamma) (GeV)",
    "lldR":   "#DeltaR(#mu,#mu)",
    "lldPhi": "#Delta#phi(#mu,#mu)",
    "ht": "H_{T} (GeV)",
    "JetGood0_eta": "#eta(jet_{0})",
    "JetGood0_phi": "#phi(jet_{0})",
    "JetGood0_pt": "p_{T}(jet_{0})",
    "JetGood1_eta": "#eta(jet_{1})",
    "JetGood1_phi": "#phi(jet_{1})",
    "JetGood1_pt": "p_{T}(jet_{1})",
    "Bj0_eta": "#eta(b-jet_{0})",
    "Bj0_phi": "#phi(b-jet_{0})",
    "Bj0_pt": "p_{T}(b-jet_{0})",
    "Bj1_eta": "#eta(b-jet_{1})",
    "Bj1_phi": "#phi(b-jet_{1})",
    "Bj1_pt": "p_{T}(b-jet_{1})",
    "PhotonLoose0_pixelSeed": "pixelSeed(#gamma)",
    "PhotonLoose0_pt": "p_{T}(#gamma)",
    "PhotonLoose0_eta": "#eta(#gamma)",
    "PhotonLoose0_phi": "#phi(#gamma)",
    "PhotonMedium0_pixelSeed": "pixelSeed(#gamma)",
    "PhotonMedium0_pt": "p_{T}(#gamma)",
    "PhotonMedium0_eta": "#eta(#gamma)",
    "PhotonMedium0_phi": "#phi(#gamma)",
    "PhotonTight0_pixelSeed": "pixelSeed(#gamma)",
    "PhotonTight0_pt": "p_{T}(#gamma)",
    "PhotonTight0_eta": "#eta(#gamma)",
    "PhotonTight0_phi": "#phi(#gamma)",
    "PhotonMVA0_pixelSeed": "pixelSeed(#gamma)",
    "PhotonMVA0_pt": "p_{T}(#gamma)",
    "PhotonMVA0_eta": "#eta(#gamma)",
    "PhotonMVA0_phi": "#phi(#gamma)",
    "minGLJetdR": "min #DeltaR(jet,#gamma)",
    "minGLLepdR": "min #DeltaR(#mu,#gamma)",
    "minGMJetdR": "min #DeltaR(jet,#gamma)",
    "minGMLepdR": "min #DeltaR(#mu,#gamma)",
    "minGTJetdR": "min #DeltaR(jet,#gamma)",
    "minGTLepdR": "min #DeltaR(#mu,#gamma)",
    "minGMVAJetdR": "min #DeltaR(jet,#gamma)",
    "minGMVALepdR": "min #DeltaR(#mu,#gamma)",
    "minLepJetdR": "min #DeltaR(#mu,jet)",
}


histos = [[s.hist for s in mc], [dataHist]]

Plot.setDefaults()
plots = []
plots.append( Plot.fromHisto( args.variable, histos, texX=replaceLabel[args.variable], texY="Number of Events" ) )

for plot in plots:

    legend = [ (0.2,0.9-0.025*sum(map(len, plot.histos)),0.9,0.9), 3 ]

    for log in [True, False]:

#        ratio = {'yRange':(0.5,1.5)}
        ratio = {'yRange':(0.0,2.0)}

        selDir = args.selection
        plot_directory_ = os.path.join( plot_directory, "EGamma", str(args.year), args.plot_directory, selDir, "log" if log else "lin" )
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = log, sorting = True,
                       yRange = (0.3, "auto"),
                       ratio = ratio,
                       drawObjects = drawObjects( lumi_scale ),
                       legend = legend,
                       copyIndexPHP = True,
                       )

