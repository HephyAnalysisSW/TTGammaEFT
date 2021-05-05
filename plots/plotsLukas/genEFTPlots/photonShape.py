#!/usr/bin/env python
''' Analysis script for plots with EFT reweighting
'''

# Standard imports
import ROOT, os, copy, pickle
ROOT.gROOT.SetBatch(True)
from math                               import pi, sqrt

# RootTools
from RootTools.core.standard            import *

# Internal Imports
from TTGammaEFT.Tools.user              import plot_directory, cache_directory

from Analysis.Tools.metFilters          import getFilterCut
from Analysis.Tools.helpers             import getCollection, deltaR

import Analysis.Tools.syncer as syncer

# EFT Reweighting
from Analysis.Tools.WeightInfo          import WeightInfo

# Default Parameter
loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                               help="Log level for logging")
argParser.add_argument('--plot_directory',     action='store',      default='ppv14')
argParser.add_argument('--year',               action='store',      default=2016,   type=int,  choices=[2016,2017,2018],                             help="Which year to plot?")
argParser.add_argument('--mode',               action='store',      default="all", type=str, choices=["genMu", "genE", "all"],                       help="plot lepton mode" )
argParser.add_argument('--normalize',          action='store_true', default=False,                                                                   help="Normalize yields" )
args = argParser.parse_args()

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.normalize:       args.plot_directory += "_normalize"

# load and define the sample
from TTGammaEFT.Samples.genTuples_TTGamma_EFT_postProcessed      import TTG_SemiLep_SM_v2
sample = TTG_SemiLep_SM_v2

# define some colors
colors = [ ROOT.kRed+1, ROOT.kGreen-2 ]

# Text on the plots
def drawObjects( lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    line = (0.68, 0.95, '%3.1f fb^{-1} (13 TeV)' % lumi_scale)
    lines = [
      (0.15, 0.95, 'CMS #bf{#it{Simulation Preliminary}}'), 
      line
    ]
    return [tex.DrawLatex(*l) for l in lines] 


# Scale the histograms by the luminosity taken by CMS in each year
if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74

# define your plot selection via the python option --selection
ebSelection = "nLeptonTight==1&&nGenJetsCMSUnfold>=3&&nGenBJetCMSUnfold>=1" #&&nPhotonGood==1"
eeSelection = "nLeptonTight==1&&nGenJetsEECMSUnfold>=3&&nGenBJetEECMSUnfold>=1" #&&nPhotonEEGood==1"

#pTG_thresh = [ 20, 35, 50, 65, 80, 120, 160, 200, 260, 320, 420 ]
#ptBins = Binning.fromThresholds( pTG_thresh )

#eeHist = sample.get1DHistoFromDraw( "PhotonGood0_pt", binning=[20,20,320], selectionString=eeSelection, weightString="weight*%f"%lumi_scale ) #, addOverFlowBin="upper" )
#ebHist = sample.get1DHistoFromDraw( "PhotonEEGood0_pt",   binning=[20,20,320], selectionString=ebSelection, weightString="weight*%f"%lumi_scale ) #, addOverFlowBin="upper" )

eeHist = sample.get1DHistoFromDraw( "PhotonGood0_eta", binning=[30,-2.4,2.4], selectionString=eeSelection, weightString="weight*%f"%lumi_scale ) #, addOverFlowBin="upper" )
ebHist = sample.get1DHistoFromDraw( "PhotonEEGood0_eta",   binning=[30,-2.4,2.4], selectionString=ebSelection, weightString="weight*%f"%lumi_scale ) #, addOverFlowBin="upper" )

ebHist.Add(eeHist)

#eeHist.legendText = "tt#gamma (EE)"
#eeHist.style = styles.lineStyle( ROOT.kRed, width = 3 )
#ebHist.legendText = "tt#gamma (EB)"
ebHist.legendText = "tt#gamma"
ebHist.style = styles.lineStyle( ROOT.kBlue, width = 3 )

#histos     = [[ebHist], [eeHist]]
histos     = [[ebHist]]
Plot.setDefaults()

#plot = Plot.fromHisto( "GenPhotonCMSUnfold0_pt", histos,texX = "gen p_{T}(#gamma) [GeV]", texY = "Number of Events" )
plot = Plot.fromHisto( "GenPhotonCMSUnfold0_eta", histos,texX = "gen #eta(#gamma)", texY = "Number of Events" )

legend = [ (0.2,0.85,0.9,0.9), 2 ]

for log in [True, False]:

    histModifications  = []
    histModifications += [lambda h: h.GetYaxis().SetTitleOffset(1.6 if log else 2.2)]

    ratioHistModifications  = []
    ratioHistModifications += [lambda h: h.GetYaxis().SetTitleOffset(1.6 if log else 2.2)]


    ratio = {'yRange':(0.1,1.9), "histModifications":ratioHistModifications, 'texY':"EE / EB"}

    scaling = { 0:1 }

    plot_directory_ = os.path.join( plot_directory, "photonShape", str(args.year), args.plot_directory, args.mode, "log" if log else "lin" )
    plotting.draw( plot,
                   plot_directory = plot_directory_,
                   logX = False, logY = log, sorting = False,
                   yRange = (0.3, "auto"),
#                   ratio = ratio,
#                   scaling = scaling,
                   drawObjects = drawObjects( lumi_scale ),
                   legend = legend,
                   histModifications = histModifications,
                   copyIndexPHP = True,
                   )




