#!/usr/bin/env python

""" 
Get cardfile result plots
"""

# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.LoadMacro('$CMSSW_BASE/src/Analysis/Tools/scripts/tdrstyle.C')
ROOT.setTDRStyle()
import os, sys, copy, math

import numpy as np
# Helpers
from plotHelpers                      import *
import array
# Analysis
from Analysis.Tools.cardFileWriter.CombineResults    import CombineResults
import Analysis.Tools.syncer as syncer

# TTGammaEFT
from TTGammaEFT.Tools.user            import plot_directory, cache_directory
from TTGammaEFT.Analysis.SetupHelpers import *

# RootTools
from RootTools.core.standard          import *

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",             action="store",                default="INFO",  help="log level?", choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"])
args = argParser.parse_args()

# logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile = None )
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

plotDirectory = "/mnt/hephy/cms/lukas.lechner/www/TTGammaEFT/pullPlot/combined/v1/"

cardFile      = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/cardFiles/defaultSetup/observed/SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_incl_splitScale.txt"
Results = CombineResults( cardFile=cardFile, plotDirectory=plotDirectory, year="combined", bkgOnly=False, isSearch=False )

pulls = Results.getPulls(postFit=True)

print pulls["JEC_FlavorQCD"]
print pulls["ISR"]
print pulls["FSR"]
#sys.exit()
print pulls["WGamma_normalization"]
print 1+pulls["ZGamma_normalization"]
print pulls["MisID_normalization_2016"]
print pulls["MisID_normalization_2017"]
print pulls["MisID_normalization_2018"]
#sys.exit()
nuisances = [
    {"tWgamma_normalization":"W#gamma normalization"},
    {"fake_photon_DD_normalization":"Nonprompt photon background"},
    {"Int_Luminosity_corr":"Integrated luminosity (correlated)"},
    {"JEC_FlavorQCD":"JES (Flavor QCD)"},
    {"tWgamma_normalization":"tW#gamma modeling"},
    {"FSR":"FSR"},
    {"Int_Luminosity_2016":"Integrated luminosity (2016)"},
    {"Int_Luminosity_2017":"Integrated luminosity (2017)"},
    {"photon_ID":"Photon reconstruction and identification"},
    {"DY_normalization":"DY normalization"},
    {"heavy_flavor_2017_2018":"b tagging"},
    {"ISR":"ISR"},
    {"JEC_Absolute":"JES (Absolute)"},
    {"TT_normalization":"t/t#bar{t} normalization"},
    {"tWgamma_normalization":"Misidentified e (2018)"},
    {"Int_Luminosity_2016_2017":"Integrated luminosity (correlated, 2016-17)"},
    {"muon_ID_extrapolation":"Muon reconstruction and identification"},
    {"QCD_0b_normalization":"Multijet normalization"},
    {"Int_Luminosity_2018":"Integrated luminosity (2018)"},
    {"tWgamma_normalization":"Misidentified e normalization (2016)"},
    {"tWgamma_normalization":"Misidentified e normalization (2017)"},
]


def drawObjects():
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.045)
    tex.SetTextAlign(11) # align right

    tex2 = ROOT.TLatex()
    tex2.SetNDC()
    tex2.SetTextSize(0.06)
    tex2.SetTextAlign(11) # align right

    line2 = (0.1, 0.915, "CMS")

    line = (0.755, 0.915, "137 fb^{-1} (13 TeV)")
    return [tex2.DrawLatex(*line2), tex.DrawLatex(*line)]


histModifications  = []
histModifications += [lambda h: h.GetXaxis().SetTickSize(0.02)]
histModifications += [lambda h: h.GetYaxis().SetTickSize(0.03)]
histModifications += [lambda h: h.GetYaxis().SetTitleSize(22)]
histModifications += [lambda h: h.GetYaxis().SetLabelSize(18)]
histModifications += [lambda h: h.GetYaxis().SetTitleOffset(0.5)]
histModifications += [lambda h: h.GetXaxis().SetLabelOffset(0.015)]
histModifications += [lambda h: h.GetXaxis().SetTitleSize(15)]
histModifications += [lambda h: h.GetXaxis().SetLabelSize(15)]
histModifications += [lambda h: h.GetYaxis().SetNdivisions(5, 5, 0, ROOT.kTRUE)]

canvasModifications  = []
canvasModifications += [lambda c:c.SetLeftMargin(0.1)]
canvasModifications += [lambda c:c.SetRightMargin(0.02)]
canvasModifications += [lambda c:c.SetBottomMargin(0.45)]
canvasModifications += [lambda c:c.SetTopMargin(0.1)]

line = ROOT.TH1F("line","line",len(nuisances), 0, len(nuisances))
linep1 = ROOT.TH1F("linep1","linep1",len(nuisances), 0, len(nuisances))
linem1 = ROOT.TH1F("linem1","linem1",len(nuisances), 0, len(nuisances))
linep2 = ROOT.TH1F("linep2","linep2",len(nuisances), 0, len(nuisances))
linem2 = ROOT.TH1F("linem2","linem2",len(nuisances), 0, len(nuisances))

hist = ROOT.TH1F("pulls","pulls",len(nuisances), 0, len(nuisances))
for i_n, n in enumerate(nuisances):
    nuis = n.keys()[0]
    hist.SetBinContent( i_n+1, pulls[nuis].val )
    hist.SetBinError( i_n+1, pulls[nuis].sigma )
    line.GetXaxis().SetBinLabel( i_n+1, n[nuis] )
    line.SetBinContent( i_n+1, 0 )
    line.SetBinError( i_n+1, 0 )
    linep1.SetBinContent( i_n+1, 1 )
    linep1.SetBinError( i_n+1, 0 )
    linem1.SetBinContent( i_n+1, -1 )
    linem1.SetBinError( i_n+1, 0 )
    linep2.SetBinContent( i_n+1, 2 )
    linep2.SetBinError( i_n+1, 0 )
    linem2.SetBinContent( i_n+1, -2 )
    linem2.SetBinError( i_n+1, 0 )

hist.style = styles.errorStyle( ROOT.kBlack, markerSize = 1 )
hist.legendText = ""
line.LabelsOption("v","X") #"vu" for 45 degree labels
line.style = styles.lineStyle( ROOT.kBlack, width=1 )
line.legendText = ""
linep1.style = styles.lineStyle( ROOT.kGray+1, width=1, dashed = True )
linep1.legendText = ""
linem1.style = styles.lineStyle( ROOT.kGray+1, width=1, dashed = True )
linem1.legendText = ""
linep2.style = styles.lineStyle( ROOT.kGray+1, width=1, dashed = True )
linep2.legendText = ""
linem2.style = styles.lineStyle( ROOT.kGray+1, width=1, dashed = True )
linem2.legendText = ""

plotting.draw(
        Plot.fromHisto( "pulls",
                [[line],[linep1],[linem1],[linep2],[linem2],[hist]],
                texX = "",
                texY = "(#theta-#theta_{0})/#Delta#theta",
        ),
        logX = False, logY = False, sorting = False,
        plot_directory    = plotDirectory,
        widths            = { "x_width":600, "y_width":650 },
        yRange            = (-2.5,2.5),
        drawObjects       = drawObjects(),
        copyIndexPHP      = True,
        extensions        = ["png", "pdf", "root"],
        histModifications = histModifications,
        canvasModifications = canvasModifications,
)
