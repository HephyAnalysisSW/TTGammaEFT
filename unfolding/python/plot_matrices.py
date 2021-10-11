import ROOT, os
ROOT.gROOT.SetBatch(True)
import array
import TTGammaEFT.unfolding.settings_uncertainty as settings_module

from RootTools.core.standard           import *
import Analysis.Tools.syncer as syncer
from TTGammaEFT.Tools.user             import plot_directory

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv49_vdiss",                                             help="plot sub-directory")
argParser.add_argument("--settings",           action="store",      type=str, choices = ["ptG","absEta","dRlg"])
args = argParser.parse_args()

directory = "../../hepData/unfolding/"
if args.settings == "ptG":
    file = "unfoldingMatrix_observed_ptG_RunII.root"
    key = "observed_ptG_RunII"
    texX = "p_{T}(#gamma^{reco}) [GeV]"
    texY = "p_{T}(#gamma^{gen}) [GeV]"
elif args.settings == "absEta":
    file = "unfoldingMatrix_observed_absEta_RunII.root"
    key = "observed_absEta_RunII"
    texX = "|#eta(#gamma^{reco})|"
    texY = "|#eta(#gamma^{gen})|"
elif args.settings == "dRlg":
    file = "unfoldingMatrix_observed_dRlg_RunII.root"
    key = "observed_dRlg_RunII"
    texX = "#DeltaR(l^{reco},#gamma^{reco})"
    texY = "#DeltaR^{fid}(l^{gen},#gamma^{gen})"

lumi_scale = 137
settings = getattr( settings_module, key )
rootfile = ROOT.TFile(directory+file,"READ")
matrix = rootfile.Get("matrix")

yBins = matrix
fidThresh = list(settings.fiducial_thresholds)
recoThresh = list(settings.reco_thresholds)
recoThresh[-1] = fidThresh[-1]
combinedMatrix = ROOT.TH2D("unfolding_matrix", "unfolding_matrix", len(recoThresh)-1, array.array('d', recoThresh), len(fidThresh)-1, array.array('d', fidThresh) )
combinedMatrix.Scale(0)

for offset in range(3):
    for x in range(combinedMatrix.GetNbinsX()):
        for y in range(combinedMatrix.GetNbinsY()):
            mx = combinedMatrix.GetNbinsX()*offset+x
            m = matrix.GetBinContent(mx+1, y+1)
            combinedMatrix.SetBinContent(x+1, y+1, combinedMatrix.GetBinContent(x+1, y+1) + m)

combinedMatrix.Scale(1./lumi_scale)

for x in range(combinedMatrix.GetNbinsX()):
    for y in range(combinedMatrix.GetNbinsY()):
        if combinedMatrix.GetBinContent(x+1, y+1) < 0.01:
            combinedMatrix.SetBinContent(x+1, y+1, 0.01 )


# Text on the plots
def drawObjects( lumi_scale, log=False ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.038)
    tex.SetTextAlign(11) # align right

    tex2 = ROOT.TLatex()
    tex2.SetNDC()
#    tex2.SetTextSize(0.058)
    tex2.SetTextSize(0.048)
    tex2.SetTextAlign(11) # align right
#    line = (0.65, 0.95, "%3.1f fb^{-1} (13 TeV)" % lumi_scale)
    line = (0.595, 0.95, "%i fb^{-1} (13 TeV)" % lumi_scale)
    line2 = (0.15, 0.95, "Private Work")
    line3 = (0.42, 0.95, "#bf{#it{Simulation}}")

#    lines2 = (0.235 if not log and (args.selection.startswith("WJets") or args.selection.startswith("TT")) else 0.15, 0.95, "CMS #bf{#it{Preliminary}}%s"%(" (%s)"%(replaceRegionNaming[args.selection.repl$
#    line2 = (0.235 if not log and (args.selection.startswith("WJets") or args.selection.startswith("TT")) else 0.15, 0.95, "CMS%s"%(" (%s)"%(replaceRegionNaming[args.selection.replace("fake","SR")] if ar$
    return [tex2.DrawLatex(*line2), tex.DrawLatex(*line3), tex.DrawLatex(*line)]

combinedMatrix.SetMarkerSize(1.8)
combinedMatrix.GetZaxis().SetTitleOffset( 0.9 )

Plot2D.setDefaults()
plot = Plot2D.fromHisto( "matrix_%s"%args.settings,           [[combinedMatrix]], texX=texX, texY=texY, texZ="Cross section [fb]" )

for log in [True,False]:

    plot.drawOption = "COLZ"

    plot_directory_ = os.path.join( plot_directory, "matrix", args.plot_directory, "log" if log else "lin" )

    plotting.draw2D( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = False, logZ = log,
                       zRange = (0.009 if log else 0,combinedMatrix.GetMaximum()),
                       drawObjects = drawObjects( lumi_scale ),
                       copyIndexPHP = True,
                       )

