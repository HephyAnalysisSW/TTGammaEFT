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
argParser.add_argument('--plot_directory',     action='store',      default='102X_TTG_ppv49_v3')
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

# Sample definition
os.environ["gammaSkim"]="False" #always false for QCD estimate
if args.year == 2016:
    import TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed as mc_samples
elif args.year == 2017:
    import TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed as mc_samples
elif args.year == 2018:
    import TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed as mc_samples
elif args.year == "RunII":
    import TTGammaEFT.Samples.nanoTuples_RunII_postProcessed as mc_samples

sample = mc_samples.TTG
sample.color = ROOT.kRed+1

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
else: lumi_scale = 35.92 + 41.53 + 59.74

#selection = "PhotonGood0_photonCatMagic==0&&nPhotonGood==1" #nLeptonTight==2&&(1)&&nLeptonVetoIsoCorr==2&&nJetGood>=1&&nBTagGood>=1&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1&&triggered==1&&pTStitching==1&&PhotonGood0_photonCatMagic==0"
selection = "nLeptonTight==1&&(1)&&nLeptonVetoIsoCorr==1&&nJetGood>=3&&nBTagGood>=1&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1&&triggered==1&&pTStitching==1&&PhotonGood0_photonCatMagic==0"
selection += "&&Flag_goodVertices&&Flag_globalSuperTightHalo2016Filter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_BadPFMuonFilter&&PV_ndof>4&&sqrt(PV_x*PV_x+PV_y*PV_y)<=2&&abs(PV_z)<=24"
selection += "&&overlapRemoval==1"
weight = "(35.92*weight*reweightHEM*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF)"

sample.setSelectionString(selection)
sample.setWeightString(weight)

hist = sample.get1DHistoFromDraw( "PhotonGood0_mother", binning=[51,-25.5,25.5] )

total = hist.Integral()
for i in range(1,hist.GetNbinsX()+1):
    evt = hist.GetBinContent(i)
    if evt == 0: continue
    print "pdgId", i-26, evt, "%.2f%s"%(evt*100./total, "%")

hist.legendText = "tt#gamma (total)"
hist.style = styles.lineStyle( sample.color, width = 3 )

histos     = [[hist]]
Plot.setDefaults()

#plot = Plot.fromHisto( "GenPhotonCMSUnfold0_pt", histos,texX = "gen p_{T}(#gamma) [GeV]", texY = "Number of Events" )
plot = Plot.fromHisto( "PhotonGood0_mother", histos,texX = "mother pdgID (#gamma)", texY = "Number of Events" )

legend = [ (0.2,0.85,0.9,0.9), 2 ]

for log in [True, False]:

    histModifications  = []
    histModifications += [lambda h: h.GetYaxis().SetTitleOffset(1.6 if log else 2.2)]

    ratioHistModifications  = []
    ratioHistModifications += [lambda h: h.GetYaxis().SetTitleOffset(1.6 if log else 2.2)]


    ratio = {'yRange':(0.1,1.9), "histModifications":ratioHistModifications, 'texY':"EE / EB"}

    scaling = { 0:1 }

    plot_directory_ = os.path.join( plot_directory, "photonMother", str(args.year), args.plot_directory, args.mode, "log" if log else "lin" )
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




