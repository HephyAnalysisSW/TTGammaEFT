# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy

# RootTools
from RootTools.core.standard           import *

# Analysis
import Analysis.Tools.syncer as syncer
from Analysis.Tools.helpers import getObjFromFile

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
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv49_v2",                                             help="plot sub-directory")
argParser.add_argument("--distribution",       action="store",      default="pT", choices=["pT","dR","eta"],                                                           help="plot sub-directory")
argParser.add_argument("--plotYear",           action="store",      default=None,                                                            help="plot sub-directory")
args = argParser.parse_args()

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile=None )
logger_rt = logger_rt.get_logger( args.logLevel, logFile=None )

# Text on the plots
def drawObjects( lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.03)
    tex.SetTextAlign(11) # align right
    line = (0.67, 0.95, "%i fb{}^{-1} (13 TeV)" % lumi_scale)
    lines = [
      (0.15, 0.95, "CMS #bf{#it{Preliminary}}"),
      line
    ]
    return [tex.DrawLatex(*l) for l in lines]


lumi_scale = 35.92 + 41.53 + 59.74

#rootfile = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/cardFiles/defaultSetup/observed/SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_incl_shapeCard_FD.root"
rootfile = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/cardFiles/defaultSetup/observed/SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_freezeR_addPtBinnedUnc_shapeCard_FD.root"
rootfile = ROOT.TFile( rootfile, "READ")

fitResult = rootfile.Get("fit_s")
covHist = fitResult.correlationHist()
covHist.GetZaxis().SetRangeUser(-1,1)
covHist.LabelsOption("v","X")

axisRange =  covHist.GetNbinsX() #len( [ i for i in range( covHist.GetNbinsX() ) if not "prop" in covHist.GetXaxis().GetBinLabel(i+1) ] )
covHist_red = ROOT.TH2F("cov","cov", axisRange, 0, axisRange, axisRange, 0, axisRange)

i_red = 0
for i in range( covHist.GetNbinsX() ):
#    if "prop" in covHist.GetXaxis().GetBinLabel(i+1): continue
    j_red = 0
    for j in range( covHist.GetNbinsY() ):
#        if "prop" in covHist.GetYaxis().GetBinLabel(j+1): continue
        covHist_red.SetBinContent(i_red+1,j_red+1, float("%.3f"%covHist.GetBinContent(i+1,j+1)))
        lab = covHist.GetYaxis().GetBinLabel(j+1)
        covHist_red.GetYaxis().SetBinLabel(j_red+1, lab )
        j_red += 1

    lab = covHist.GetXaxis().GetBinLabel(i+1)
    covHist_red.GetXaxis().SetBinLabel(i_red+1, lab )
    i_red += 1


dat = {}
for i in range( covHist_red.GetNbinsX() ):
    labX = covHist_red.GetXaxis().GetBinLabel(i+1)
    dat[labX] = {}
    for j in range( covHist_red.GetNbinsY() ):
        labY = covHist_red.GetYaxis().GetBinLabel(j+1)
        dat[labX][labY] = covHist_red.GetBinContent(i+1,j+1)

plot = Plot2D.fromHisto( "covMatrix", [[covHist_red]], texX="", texY="" ) 

plot.drawOption = "COLZ"
legend = (0.2,0.75,0.9,0.9)

histModifications  = []
#histModifications += [lambda h: h.GetXaxis().SetLabelSize(60)]
#histModifications += [lambda h: h.GetYaxis().SetLabelSize(60)]
histModifications += [lambda h: h.GetZaxis().SetLabelSize(0.03)]
histModifications += [lambda h: h.GetXaxis().SetTickSize(0)]
histModifications += [lambda h: h.GetYaxis().SetTickSize(0)]

plot_directory_ = os.path.join( plot_directory, "corrMatrix", "RunII", args.plot_directory, "pT" )

plotting.draw2D( plot,
    plot_directory = plot_directory_,
    widths            = { "x_width":3000, "y_width":3000 },
    logX = False, logY = False, logZ = False,
    zRange = (-1,1),
    drawObjects = drawObjects( lumi_scale ),
    histModifications = histModifications,
    copyIndexPHP = True,
)

