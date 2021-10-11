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
    file = "efficiency_observed_ptG_RunII.root"
    key = "observed_ptG_RunII"
    texX = "p_{T}(#gamma) [GeV]"
elif args.settings == "absEta":
    file = "efficiency_observed_absEta_RunII.root"
    key = "observed_absEta_RunII"
    texX = "|#eta(#gamma)|"
elif args.settings == "dRlg":
    file = "efficiency_observed_dRlg_RunII.root"
    texX = "#DeltaR(l,#gamma)"
    key = "observed_dRlg_RunII"

keyEff = "efficiency"
keyPur = "purity"
keyReco = "reco"
keyFout = "fout"
keySub = "foutSubtracted"

lumi_scale = 137
settings = getattr( settings_module, key )
rootfile = ROOT.TFile(directory+file,"READ")
eff = rootfile.Get("efficiency")
pur = rootfile.Get("purity")
reco = rootfile.Get("reco")
fout = rootfile.Get("fout")
sub = rootfile.Get("foutSubtracted")

#yBins = matrix
fidThresh = list(settings.fiducial_thresholds)
recoThresh = list(settings.reco_thresholds)
recoThresh[-1] = fidThresh[-1]
purComb = ROOT.TH1D("pur", "pur", len(recoThresh)-1, array.array('d', recoThresh) )
recoComb = ROOT.TH1D("reco", "reco", len(recoThresh)-1, array.array('d', recoThresh) )
foutComb = ROOT.TH1D("fout", "fout", len(recoThresh)-1, array.array('d', recoThresh) )
subComb = ROOT.TH1D("sub", "sub", len(recoThresh)-1, array.array('d', recoThresh) )

for offset in range(3):
    for x in range(purComb.GetNbinsX()):
        purComb.SetBinContent(x+1, 1)

        mx = recoComb.GetNbinsX()*offset+x
        m = reco.GetBinContent(mx+1)
        recoComb.SetBinContent(x+1, recoComb.GetBinContent(x+1) + m)

        mx = foutComb.GetNbinsX()*offset+x
        m = fout.GetBinContent(mx+1)
        foutComb.SetBinContent(x+1, foutComb.GetBinContent(x+1) + m)

        mx = subComb.GetNbinsX()*offset+x
        m = sub.GetBinContent(mx+1)
        subComb.SetBinContent(x+1, subComb.GetBinContent(x+1) + m)


print eff.GetNbinsX()
print purComb.GetNbinsX()
print recoComb.GetNbinsX()
print foutComb.GetNbinsX()
print subComb.GetNbinsX()

foutComb.Divide(recoComb)

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
    line = (0.69, 0.95, "%i fb^{-1} (13 TeV)" % lumi_scale)
    line2 = (0.15, 0.95, "Private Work")
    line3 = (0.42, 0.95, "#bf{#it{Simulation}}")

#    lines2 = (0.235 if not log and (args.selection.startswith("WJets") or args.selection.startswith("TT")) else 0.15, 0.95, "CMS #bf{#it{Preliminary}}%s"%(" (%s)"%(replaceRegionNaming[args.selection.repl$
#    line2 = (0.235 if not log and (args.selection.startswith("WJets") or args.selection.startswith("TT")) else 0.15, 0.95, "CMS%s"%(" (%s)"%(replaceRegionNaming[args.selection.replace("fake","SR")] if ar$
    return [tex2.DrawLatex(*line2), tex.DrawLatex(*line3), tex.DrawLatex(*line)]

#combinedMatrix.SetMarkerSize(1.8)
#combinedMatrix.GetZaxis().SetTitleOffset( 0.9 )

#Plot2D.setDefaults()
#plot = Plot2D.fromHisto( "matrix_%s"%args.settings,           [[combinedMatrix]], texX=texX, texY=texY, texZ="Events [fb]" )

#for log in [True,False]:
#    plot_directory_ = os.path.join( plot_directory, "matrix", args.plot_directory, "log" if log else "lin" )
#    plotting.draw( plot,
#                       plot_directory = plot_directory_,
#                       logX = False, logY = False,
#                       drawObjects = drawObjects( lumi_scale ),
#                       copyIndexPHP = True,
#                       )


purComb. style = styles.lineStyle( ROOT.kRed+1, width = 2, errors=False)
purComb.legendText = "Purity"
eff.style = styles.lineStyle( ROOT.kBlue, width = 2, errors=True)
eff.legendText = "Efficiency"
foutComb. style = styles.lineStyle( ROOT.kGreen+2, width = 2, errors=False)
foutComb.legendText = "f_{out} fraction" 

purComb.Scale(100)
eff.Scale(100)
foutComb.Scale(100)

purComb.Add(foutComb, -1)

print purComb.GetBinContent(1)

plot_directory_ = os.path.join( plot_directory, "matrix", args.plot_directory, "lin" )
plot = Plot.fromHisto( name = 'fout_%s'%args.settings,  histos = [[ h ] for h in [eff, purComb,foutComb]], texX = texX, texY = "Fraction [%]" )
#plot.stack = None
plotting.draw(plot,
        plot_directory = plot_directory_,
        logX = False, logY = False, sorting = False,
        yRange         = (0, 140) ,
        legend         = (0.20,0.7,0.9,0.87),
        drawObjects    = drawObjects(lumi_scale),
        copyIndexPHP   = True,
)
