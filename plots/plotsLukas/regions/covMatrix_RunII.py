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
#    line = (0.65, 0.95, "%3.1f fb{}^{-1} (13 TeV)" % lumi_scale)
    line = (0.70, 0.95, "%i fb^{-1} (13 TeV)" % lumi_scale)
    lines = [
      (0.15, 0.95, "CMS #bf{#it{Preliminary}}"),
      line
    ]
    return [tex.DrawLatex(*l) for l in lines]


lumi_scale = 35.92 + 41.53 + 59.74

#rootfile = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/cardFiles/defaultSetup/observed/SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_incl_shapeCard_FD.root"

if args.distribution == "pT":
    rootfile = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/cardFiles/defaultSetup/observed/SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_freezeR_addPtBinnedUnc_shapeCard_FD.root"
#    rLab = "Signal_e_4p_Bin1_2016"
#    if args.plotYear: rLab = rLab.replace("2016", args.plotYear)
    nBins = 11
elif args.distribution == "dR":
    rootfile = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/cardFiles/defaultSetup/observed/SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_freezeR_addPtBinnedUnc_shapeCard_FD.root"
#    rLab = "Signal_e_4p_Bin1_2016"
#    if args.plotYear: rLab = rLab.replace("2016", args.plotYear)
    nBins = 14
elif args.distribution == "eta":
    rootfile = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/COMBINED/limits/cardFiles/defaultSetup/observed/SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_freezeR_addPtBinnedUnc_shapeCard_FD.root"
#    rLab = "Signal_e_4p_Bin1_2016"
#    if args.plotYear: rLab = rLab.replace("2016", args.plotYear)
    nBins = 10
#key      = "shapes_fit_s/overall_total_covar"
rootfile = ROOT.TFile( rootfile, "READ")

fitResult = rootfile.Get("fit_s")
covHist = fitResult.correlationHist()
covHist.GetZaxis().SetRangeUser(-1,1)
covHist.LabelsOption("v","X")

#covHist = getObjFromFile( rootfile, key )
#print covHist.GetNbinsX()
#axisRange = len( [ i for i in range( covHist.GetNbinsX() ) if not "prop" in covHist.GetXaxis().GetBinLabel(i+1) ] )
#axisRange = len( [ i for i in range( covHist.GetNbinsX() ) if (covHist.GetXaxis().GetBinLabel(i+1) == "r" or "Signal" in covHist.GetXaxis().GetBinLabel(i+1)) and (covHist.GetXaxis().GetBinLabel(i+1) =="r" or not args.plotYear or (args.plotYear and args.plotYear in covHist.GetXaxis().GetBinLabel(i+1))) ] )
axisRange = len( [ i for i in range( covHist.GetNbinsX() ) if ("Signal" in covHist.GetXaxis().GetBinLabel(i+1)) and (not args.plotYear or (args.plotYear and args.plotYear in covHist.GetXaxis().GetBinLabel(i+1))) ] )
#print axisRange
#axisRange += 2
covHist_red = ROOT.TH2F("cov","cov", axisRange, 0, axisRange, axisRange, 0, axisRange)

i_red = 0
for i in range( covHist.GetNbinsX() ):
#    if "prop" in covHist.GetXaxis().GetBinLabel(i+1): continue
#    print i+1,covHist.GetXaxis().GetBinLabel(i+1)
#    if covHist.GetXaxis().GetBinLabel(i+1) != "r":
    if not "Signal" in covHist.GetXaxis().GetBinLabel(i+1): continue
    if args.plotYear and not args.plotYear in covHist.GetXaxis().GetBinLabel(i+1): continue
#    if i > 9: continue
    j_red = 0
    for j in range( covHist.GetNbinsY() ):
#        if "prop" in covHist.GetYaxis().GetBinLabel(j+1): continue
#        if covHist.GetYaxis().GetBinLabel(j+1) != "r":
        if not "Signal" in covHist.GetYaxis().GetBinLabel(j+1): continue
        if args.plotYear and not args.plotYear in covHist.GetYaxis().GetBinLabel(j+1): continue
#        if j > 9: continue
        covHist_red.SetBinContent(i_red+1,j_red+1, float("%.3f"%covHist.GetBinContent(i+1,j+1)))
        lab = covHist.GetYaxis().GetBinLabel(j+1)
#        if lab == "r":
#            lab = rLab
        newLab = lab.replace("_"," ").replace("Signal", "").replace("mu","#mu").replace(" 3 "," 3 jet ").replace("4p","#geq4 jet")
        covHist_red.GetYaxis().SetBinLabel(j_red+1, newLab )
        j_red += 1

    lab = covHist.GetXaxis().GetBinLabel(i+1)
#    if lab == "r":
#        lab = rLab
    newLab = lab.replace("_"," ").replace("Signal", "").replace("mu","#mu").replace(" 3 "," 3 jet ").replace("4p","#geq4 jet")
#    print lab, newLab
    covHist_red.GetXaxis().SetBinLabel(i_red+1, newLab )
    i_red += 1


dat = {}
for i in range( covHist_red.GetNbinsX() ):
    labX = covHist_red.GetXaxis().GetBinLabel(i+1)
    dat[labX] = {}
    for j in range( covHist_red.GetNbinsY() ):
        labY = covHist_red.GetYaxis().GetBinLabel(j+1)
        dat[labX][labY] = covHist_red.GetBinContent(i+1,j+1)

#if not args.plotYear:
#    newRLab = rLab.replace("_"," ").replace("Signal", "").replace("mu","#mu").replace(" 3 "," 3 jet ").replace("4p","#geq4 jet")
#    dat[newRLab.replace("2016","2017")] = {}
#    dat[newRLab.replace("2016","2018")] = {}
#    dat[newRLab.replace("2016","2017")][newRLab.replace("2016","2017")] = 1
#    dat[newRLab.replace("2016","2018")][newRLab.replace("2016","2018")] = 1
#    dat[newRLab.replace("2016","2018")][newRLab.replace("2016","2017")] = 1
#    dat[newRLab.replace("2016","2017")][newRLab.replace("2016","2018")] = 1
#    for x in dat.keys():
#        if x == newRLab.replace("2016","2017"): continue
#        if x == newRLab.replace("2016","2018"): continue
#        dat[newRLab.replace("2016","2017")][x] = dat[newRLab][x]
#        dat[newRLab.replace("2016","2018")][x] = dat[newRLab][x]
#        dat[x][newRLab.replace("2016","2017")] = dat[x][newRLab]
#        dat[x][newRLab.replace("2016","2018")] = dat[x][newRLab]

xLab = dat.keys()
#print xLab

xLab = sorted(xLab, key = lambda x: ( -int(x.split(" ")[-1]), x.split(" ")[1], -int(x.split(" ")[2][-1]), -int(x.split(" ")[-2].split("Bin")[1]) ) )

#[' #mu 3 jet Bin0 2016', ' e 3 jet Bin1 2016', ' #mu #geq4 jet Bin3 2016', ' e 3 jet Bin8 2016', ' #mu 3 jet Bin10 2016', ' #mu #geq4 jet Bin7 2016', ' e 3 jet Bin0 2016', ' e 3 jet Bin7 2016', ' e #geq4 jet Bin7 2016', ' #mu #geq4 jet Bin4 2016', ' e #geq4 jet Bin5 2016', ' #mu #geq4 jet Bin2 2016', ' #mu #geq4 jet Bin9 2016', ' #mu 3 jet Bin3 2016', ' e 3 jet Bin2 2016', ' #mu #geq4 jet Bin8 2016', ' e 3 jet Bin3 2016', ' #mu 3 jet Bin2 2016', ' #mu #geq4 jet Bin1 2016', ' #mu #geq4 jet Bin6 2016', ' e 3 jet Bin10 2016', ' e #geq4 jet Bin8 2016', ' e #geq4 jet Bin4 2016', ' #mu 3 jet Bin8 2016', ' #mu #geq4 jet Bin5 2016', ' e #geq4 jet Bin10 2016', ' #mu #geq4 jet Bin10 2016', ' #mu 3 jet Bin9 2016', ' e #geq4 jet Bin2 2016', ' e #geq4 jet Bin6 2016', ' #mu 3 jet Bin6 2016', ' e 3 jet Bin6 2016', ' e #geq4 jet Bin3 2016', ' #mu 3 jet Bin1 2016', ' e 3 jet Bin4 2016', ' #mu 3 jet Bin4 2016', ' #mu 3 jet Bin5 2016', ' e #geq4 jet Bin1 2016', ' e 3 jet Bin5 2016', ' #mu 3 jet Bin7 2016', ' e #geq4 jet Bin9 2016', ' e 3 jet Bin9 2016']

print xLab
#if not args.plotYear:
#    axisRange += 2
covHist_sorted_red = ROOT.TH2F("cov","cov", axisRange, 0, axisRange, axisRange, 0, axisRange)

#print dat.keys()
#print dat[dat.keys()[0]].keys()
for ix, x in enumerate(xLab[::-1]):
    for iy, y in enumerate(xLab):
        covHist_sorted_red.SetBinContent(ix+1,iy+1, dat[x][y])
        yL = y.split(" ")[-1] + " " + " ".join( [item for item in y.split(" ") if item][:-1] )
        if args.plotYear:
            if not "Bin0" in yL: yL = yL.split(" ")[4]
        else:
            if not "Bin%i"%(int(nBins*0.5)) in yL: yL = ""
            yL = " ".join(yL.split(" ")[:-1])
        covHist_sorted_red.GetYaxis().SetBinLabel(iy+1, yL )
    xL = x.split(" ")[-1] + " " + " ".join( [item for item in x.split(" ") if item][:-1] )
    if args.plotYear:
        if not "Bin0" in xL: xL = xL.split(" ")[4]
    else:
        if not "Bin%i"%(int(nBins*0.5)) in xL: xL = ""
        xL = " ".join(xL.split(" ")[:-1])
    covHist_sorted_red.GetXaxis().SetBinLabel(ix+1, xL )


covHist_sorted_red.LabelsOption("v","X")
#nDiv = -504 if args.plotYear else -504
#covHist_sorted_red.GetXaxis().SetNdivisions(-2)
#covHist_sorted_red.GetYaxis().SetNdivisions(-2)

addon = ""
if args.plotYear:
    addon = "_%s"%args.plotYear

plot = Plot2D.fromHisto( "covMatrix%s"%addon, [[covHist_sorted_red]], texX="", texY="" ) 

histModifications  = []
if args.plotYear:
    histModifications += [lambda h: h.GetXaxis().SetLabelSize(40)]
    histModifications += [lambda h: h.GetYaxis().SetLabelSize(40)]
else:
    histModifications += [lambda h: h.GetXaxis().SetLabelSize(60)]
    histModifications += [lambda h: h.GetYaxis().SetLabelSize(60)]
histModifications += [lambda h: h.GetZaxis().SetLabelSize(0.03)]
#histModifications += [lambda h: h.GetXaxis().SetNdivisions(-1701)]
#histModifications += [lambda h: h.GetYaxis().SetNdivisions(-1501)]
histModifications += [lambda h: h.GetXaxis().SetTickSize(0)]
histModifications += [lambda h: h.GetYaxis().SetTickSize(0)]


l = ROOT.TLine()
l.SetLineWidth(1)
l.SetLineColor(ROOT.kBlack)
drawObjects_  = [l.DrawLine(0, nBins*i, axisRange, nBins*i) for i in range(1,5 if args.plotYear else 13)]
drawObjects_ += [l.DrawLine(nBins*i, 0, nBins*i, axisRange) for i in range(1,5 if args.plotYear else 13)]

l3 = ROOT.TLine()
l3.SetLineWidth(2)
l3.SetLineColor(ROOT.kBlack)
drawObjects_ += [l3.DrawLine(0, nBins*i, axisRange, nBins*i) for i in range(2,3 if args.plotYear else 11, 2)]
drawObjects_ += [l3.DrawLine(nBins*i, 0, nBins*i, axisRange) for i in range(2,3 if args.plotYear else 11, 2)]

if not args.plotYear:
    l2 = ROOT.TLine()
    l2.SetLineWidth(3)
    l2.SetLineColor(ROOT.kBlack)
    drawObjects_ += [l2.DrawLine(0, nBins*i, axisRange, nBins*i) for i in range(4,9, 4)]
    drawObjects_ += [l2.DrawLine(nBins*i, 0, nBins*i, axisRange) for i in range(4,9, 4)]

plot.drawOption = "COLZ"
legend = (0.2,0.75,0.9,0.9)

plot_directory_ = os.path.join( plot_directory, "covMatrix", "RunII", args.plot_directory, args.distribution )

plotting.draw2D( plot,
    plot_directory = plot_directory_,
    widths            = { "x_width":3000, "y_width":3000 },
    logX = False, logY = False, logZ = False,
    zRange = (-1,1),
    drawObjects = drawObjects( lumi_scale ) + drawObjects_,
    histModifications = histModifications,
    copyIndexPHP = True,
)

