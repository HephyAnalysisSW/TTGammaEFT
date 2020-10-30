import ROOT
import os, sys
from math import sqrt

from Analysis.Tools.helpers import getObjFromFile

dataDir = "$CMSSW_BASE/src/Analysis/Tools/data/photonSFData/"
g_file = 'g2016_Fall17V2_2016_Medium_photons.root'
g_key   = "EGamma_SF2D"

sfmap = getObjFromFile( os.path.expandvars( os.path.join( dataDir, g_file ) ), g_key )

for i in range(sfmap.GetNbinsX()):
    for j in range(sfmap.GetNbinsY()):
        print sfmap.GetXaxis().GetBinLowEdge(i+1), sfmap.GetYaxis().GetBinLowEdge(j+1), sfmap.GetBinContent(i+1,j+1), sfmap.GetBinError(i+1,j+1)
    print


totalUnc  = sfmap.Clone()

for i in range(sfmap.GetNbinsX()):
    for j in range(sfmap.GetNbinsY()):
        totalUnc.SetBinContent(i+1, j+1, totalUnc.GetBinError(i+1, j+1))
        totalUnc.SetBinError(i+1, j+1, 0)

sfUnc     = totalUnc.Clone()
altSignal = totalUnc.Clone()

altSigVal = [
            [0.01, 0.001, 0.006, 0.012,0.096],
            [0.02, 0.002, 0.006, 0.006,0.003],
            [0.156, 0.01, 0.069, 0.002,0.133],
            [0.027, 0.002, 0.005, 0.154,0.004],
            [0.014, 0.001, 0.007, 0.003,0.004],
            [0.014, 0.001, 0.007, 0.003,0.004],
            [0.027, 0.002, 0.005, 0.154,0.004],
            [0.156, 0.01, 0.069, 0.002,0.133],
            [0.02, 0.002, 0.006, 0.006,0.003],
            [0.01, 0.001, 0.006, 0.012,0.096],
]

for i in range(sfmap.GetNbinsX()):
    for j in range(sfmap.GetNbinsY()):
        altSignal.SetBinContent(i+1, j+1, altSigVal[i][j])
        altSignal.SetBinError(i+1, j+1, 0)

qAltSignal = altSignal.Clone()
qAltSignal.Multiply(qAltSignal)

sfUnc.Multiply(sfUnc)
sfUnc.Add(qAltSignal, -1)
for i in range(sfmap.GetNbinsX()):
    for j in range(sfmap.GetNbinsY()):
        sfUnc.SetBinContent(i+1, j+1, sqrt(sfUnc.GetBinContent(i+1, j+1)))
        sfmap.SetBinError(i+1, j+1, sfUnc.GetBinContent(i+1, j+1))

for i in range(sfmap.GetNbinsX()):
    for j in range(sfmap.GetNbinsY()):
        altSignal.SetBinError(i+1, j+1, altSignal.GetBinContent(i+1,j+1))
        altSignal.SetBinContent(i+1, j+1, sfmap.GetBinContent(i+1,j+1))


print
print
print
print
print
for i in range(altSignal.GetNbinsX()):
    for j in range(altSignal.GetNbinsY()):
        print altSignal.GetXaxis().GetBinLowEdge(i+1), altSignal.GetYaxis().GetBinLowEdge(j+1), altSignal.GetBinContent(i+1,j+1), altSignal.GetBinError(i+1,j+1)
    print




tRootFile = ROOT.TFile( os.path.expandvars( os.path.join( dataDir, g_file.replace(".root","_private.root") ) ), "RECREATE" )
sfmap.SetTitle(g_key)
sfmap.SetName(g_key)
sfmap.Write()
altSignal.SetTitle(g_key+"_altSigModel")
altSignal.SetName(g_key+"_altSigModel")
altSignal.Write()
