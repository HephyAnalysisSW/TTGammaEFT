# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy
import math

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
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv49_v1",                                             help="plot sub-directory")
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
    line = (0.68, 0.95, "%3.1f fb^{-1} (13 TeV)" % lumi_scale)
    lines = [
      (0.15, 0.95, "CMS #bf{#it{Preliminary}}"),
      line
    ]
    return [tex.DrawLatex(*l) for l in lines]


lumi_scale = 35.92 + 41.53 + 59.74

if args.distribution == "pT":
    rootfile = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/cardFiles/defaultSetup/observed/SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_freezeR_addPtBinnedUnc_shapeCard_FD.root"
    nBins = 11
    nMax = 4500
elif args.distribution == "dR":
    rootfile = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/cardFiles/defaultSetup/observed/SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_freezeR_addPtBinnedUnc_shapeCard_FD.root"
    nBins = 14
    nMax = 1300
elif args.distribution == "eta":
    rootfile = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/cardFiles/defaultSetup/observed/SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_freezeR_addPtBinnedUnc_shapeCard_FD.root"
    nBins = 10
    nMax = 1100
rootfile = ROOT.TFile( rootfile, "READ")

covHist = rootfile.Get("shapes_fit_s/overall_total_covar")
#covHist = fitResult.correlationHist()
#covHist.GetZaxis().SetRangeUser(-1,1)
covHist.LabelsOption("v","X")

axisRange = range( int(covHist.GetNbinsX()/3.) - nBins*4, int(covHist.GetNbinsX()/3.) )
covHist_red = ROOT.TH2F("cov","cov", nBins*12, 0, nBins*12, nBins*12, 0, nBins*12)

i_red = 0
for i in range( covHist.GetNbinsX() ):
    if not int(covHist.GetXaxis().GetBinLabel(i+1).split("_")[-1]) in axisRange: continue
    j_red = 0
    for j in range( covHist.GetNbinsY() ):
        if not int(covHist.GetXaxis().GetBinLabel(j+1).split("_")[-1]) in axisRange: continue
        covHist_red.SetBinContent(i_red+1,j_red+1, float("%.3f"%covHist.GetBinContent(i+1,j+1)))
        lab = covHist.GetYaxis().GetBinLabel(j+1)
        lab = lab.split("_")[1] + " Bin " + str(int(lab.split("_")[-1])-axisRange[0])
        covHist_red.GetYaxis().SetBinLabel(j_red+1, lab )
        j_red += 1

    lab = covHist.GetXaxis().GetBinLabel(i+1)
    lab = lab.split("_")[1] + " Bin " + str(int(lab.split("_")[-1])-axisRange[0])
    covHist_red.GetXaxis().SetBinLabel(i_red+1, lab )
    i_red += 1


dat = {}
for i in range( covHist_red.GetNbinsX() ):
    labX = covHist_red.GetXaxis().GetBinLabel(i+1)
    if int(labX.split(" ")[-1]) >= 2*nBins:
        labX = "#geq4 Jets, " + labX
    else:
        labX = "3 Jets, " + labX
    if int(labX.split(" ")[-1])%2:
        labX = "#mu, " + labX
    else:
        labX = "e, " + labX

    dat[labX] = {}
    for j in range( covHist_red.GetNbinsY() ):
        labY = covHist_red.GetYaxis().GetBinLabel(j+1)
        if int(labY.split(" ")[-1]) >= 2*nBins:
            labY = "#geq4 Jets, " + labY
        else:
            labY = "3 Jets, " + labY
        if int(labY.split(" ")[-1])%2:
            labY = "#mu, " + labY
        else:
            labY = "e, " + labY

        dat[labX][labY] = covHist_red.GetBinContent(i+1,j+1)


xLab = dat.keys()
#'#mu, 3 Jets, 2017 Bin 3'

xLab = sorted(xLab, key = lambda x: ( -int(x.split(" ")[3]), x.split(" ")[0], -int(x.split(" ")[1][-1]), -int(x.split(" ")[-1]) ) )
covHist_sorted_red = ROOT.TH2F("cov","cov", nBins*12, 0, nBins*12, nBins*12, 0, nBins*12)

for ix, x in enumerate(xLab[::-1]):
    for iy, y in enumerate(xLab):
        covHist_sorted_red.SetBinContent(ix+1,iy+1, dat[x][y])
        yL = y #.split(" ")[-1] + " " + " ".join( [item for item in y.split(" ") if item][:-1] )
        b = int(y.split(" ")[-1])
        if b not in [nBins-1, nBins, nBins*3, nBins*3-1]: yL = ""
#        if not "Bin %i"%(int(nBins*0.5)) in yL: yL = ""
        yL = " ".join(yL.split(" ")[:-2])
        covHist_sorted_red.GetYaxis().SetBinLabel(iy+1, yL )
    xL = x
    b = int(x.split(" ")[-1])
    if b not in [nBins-1, nBins, nBins*3, nBins*3-1]: xL = ""
    xL = " ".join(xL.split(" ")[:-2])
    covHist_sorted_red.GetXaxis().SetBinLabel(ix+1, xL )


covHist_sorted_red.LabelsOption("v","X")

corrHist = covHist_sorted_red.Clone()
nB = corrHist.GetNbinsX()
sigma = []
testUnc = [0]*nBins
testY = []
for i in range( nB ):
    print i, covHist_sorted_red.GetBinContent(i+1, nB-i), math.sqrt(covHist_sorted_red.GetBinContent(i+1, nB-i))
    testUnc[i%nBins] += covHist_sorted_red.GetBinContent(i+1, nB-i)
    sigma.append( math.sqrt(covHist_sorted_red.GetBinContent(i+1, nB-i)) )

print testUnc
print [math.sqrt(x) for x in testUnc]

for i in range( nB ):
    for j in range( nB ):
        cov = covHist_sorted_red.GetBinContent(i+1, nB-j)
        cov /= (sigma[i]*sigma[j])
        corrHist.SetBinContent(i+1, nB-j, cov)

corrHist.GetZaxis().SetRangeUser(-1,1)

#plot = Plot2D.fromHisto( "covMatrix", [[covHist_sorted_red]], texX="", texY="" ) 
plot = Plot2D.fromHisto( "corrMatrix", [[corrHist]], texX="", texY="" ) 
#plot = Plot2D.fromHisto( "covMatrix", [[covHist_red]], texX="", texY="" ) 
#plot = Plot2D.fromHisto( "covMatrix", [[covHist]], texX="", texY="" ) 

plot.drawOption = "COLZ"
#legend = (0.2,0.75,0.9,0.9)

histModifications  = []
histModifications += [lambda h: h.GetXaxis().SetLabelSize(45)]
histModifications += [lambda h: h.GetYaxis().SetLabelSize(45)]
histModifications += [lambda h: h.GetZaxis().SetLabelSize(0.02)]
histModifications += [lambda h: h.GetXaxis().SetTickSize(0)]
histModifications += [lambda h: h.GetYaxis().SetTickSize(0)]

l = ROOT.TLine()
l.SetLineWidth(1)
l.SetLineColor(ROOT.kBlack)
drawObjects_  = [l.DrawLine(0, nBins*i, nBins*12, nBins*i) for i in range(1,13)]
drawObjects_ += [l.DrawLine(nBins*i, 0, nBins*i, nBins*12) for i in range(1,13)]

l3 = ROOT.TLine()
l3.SetLineWidth(2)
l3.SetLineColor(ROOT.kBlack)
drawObjects_ += [l3.DrawLine(0, nBins*i, nBins*12, nBins*i) for i in range(2,11, 2)]
drawObjects_ += [l3.DrawLine(nBins*i, 0, nBins*i, nBins*12) for i in range(2,11, 2)]

l2 = ROOT.TLine()
l2.SetLineWidth(3)
l2.SetLineColor(ROOT.kBlack)
drawObjects_ += [l2.DrawLine(0, nBins*i, nBins*12, nBins*i) for i in range(4,9, 4)]
drawObjects_ += [l2.DrawLine(nBins*i, 0, nBins*i, nBins*12) for i in range(4,9, 4)]

plot_directory_ = os.path.join( plot_directory, "covariance", "RunII", args.plot_directory, args.distribution )

plotting.draw2D( plot,
    plot_directory = plot_directory_,
    widths            = { "x_width":3000, "y_width":3000 },
    logX = False, logY = False, logZ = False,
#    zRange = (0,nMax),
    drawObjects = drawObjects( lumi_scale ) + drawObjects_,
    histModifications = histModifications,
    copyIndexPHP = True,
)

