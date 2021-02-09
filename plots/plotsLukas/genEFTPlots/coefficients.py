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

# load and define the EFT sample
#from TTGammaEFT.Samples.genTuples_TTGamma_EFT_postProcessed  import TTG_2WC_ref as sample
#from TTGammaEFT.Samples.genTuples_TTGamma_EFT_postProcessed  import stg_tch_2WC_ref as sample
from TTGammaEFT.Samples.genTuples_TTGamma_EFT_postProcessed  import tWG_2WC_ref as sample
#sample = TTG_2WC_ref
sample.color = ROOT.kRed+1

# Text on the plots
def drawObjects( lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    line = (0.65, 0.95, '%3.1f fb{}^{-1} (13 TeV)' % lumi_scale)
    lines = [
      (0.15, 0.95, 'CMS #bf{#it{Simulation Preliminary}}'), 
      line
    ]
    return [tex.DrawLatex(*l) for l in lines] 


# Scale the histograms by the luminosity taken by CMS in each year
if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74

c = sample.chain 

w = WeightInfo(sample.reweight_pkl)
w.set_order( 2 )

h = ROOT.TH1F('h_weights','weights',5,1,6)
selection = "nLeptonTight==1&&nGenJetsCMSUnfold>=3&&nGenBJetCMSUnfold>=1" #&&nPhotonGood==1"
c.Draw('Iteration$>>h_weights','p_C/p_C[0]*(%s)'%selection)
#c.Draw('Iteration$>>h_weights','p_C*(Z_pt>300)')

hist = ROOT.h_weights

print w.weight_string_WC()

#labels = ["c_{0}", "ctZ", "ctZI", "ctZ^{2}", "ctZ*ctZI", "ctZI^{2}"]
labels = ["ctZ", "ctZI", "ctZ^{2}", "ctZ*ctZI", "ctZI^{2}"]

for i in range(1, hist.GetNbinsX()+1):
    hist.GetXaxis().SetBinLabel(i, labels[i-1])

hist.legendText = "#sum p_{C} weights (tt#gamma)"
hist.style = styles.lineStyle( sample.color, width = 3 )

histos     = [[hist]]
Plot.setDefaults()

#plot = Plot.fromHisto( "GenPhotonCMSUnfold0_pt", histos,texX = "gen p_{T}(#gamma) [GeV]", texY = "Number of Events" )
plot = Plot.fromHisto( "coefficients", histos,texX = "p_{C} index", texY = "Number of Events" )

legend = [ (0.2,0.85,0.9,0.9), 2 ]

for log in [True, False]:

    histModifications  = []
    histModifications += [lambda h: h.GetYaxis().SetTitleOffset(1.6 if log else 2.2)]
    histModifications += [lambda h: h.GetXaxis().SetTitleOffset(10)]

    plot_directory_ = os.path.join( plot_directory, "EFTcoefficients", str(args.year), args.plot_directory, args.mode, "log" if log else "lin" )
    plotting.draw( plot,
                   plot_directory = plot_directory_,
                   logX = False, logY = log, sorting = False,
                   yRange = (0.3, "auto"),
                   drawObjects = drawObjects( lumi_scale ),
                   legend = legend,
                   histModifications = histModifications,
                   copyIndexPHP = True,
                   )




