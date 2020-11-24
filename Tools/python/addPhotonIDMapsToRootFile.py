import ROOT
import os, sys
from math import sqrt

from Analysis.Tools.helpers import getObjFromFile

year    = 2018
dataDir = "$CMSSW_BASE/src/Analysis/Tools/data/photonSFData/"
g_file  = 'g%i_PhotonsMedium.root'%year
g_key   = "EGamma_SF2D"

if year == 2017:
    altSigVal = [
            [0.028,0.023,0.000,0.006,0.014,0.014,0.006,0.000,0.023,0.028],
            [0.019,0.009,0.000,0.008,0.003,0.003,0.008,0.000,0.009,0.019],
            [0.008,0.010,0.000,0.022,0.014,0.014,0.022,0.000,0.010,0.008],
            [0.004,0.001,0.000,0.001,0.000,0.000,0.001,0.000,0.001,0.004],
            [0.035,0.003,0.000,0.001,0.010,0.010,0.001,0.000,0.003,0.035],
        ]
    altBkgVal = [
            [0.015,0.012,0.000,0.018,0.012,0.012,0.018,0.000,0.012,0.015],
            [0.008,0.004,0.000,0.003,0.002,0.002,0.003,0.000,0.004,0.008],
            [0.011,0.007,0.000,0.004,0.001,0.001,0.004,0.000,0.007,0.011],
            [0.009,0.004,0.000,0.009,0.022,0.022,0.009,0.000,0.004,0.009],
            [0.008,0.020,0.000,0.066,0.054,0.054,0.066,0.000,0.020,0.008],
        ]
    altEffVal = [
            [0.027,0.017,0.000,0.005,0.005,0.005,0.005,0.000,0.017,0.027],
            [0.012,0.020,0.000,0.017,0.021,0.021,0.017,0.000,0.020,0.012],
            [0.009,0.002,0.000,0.014,0.013,0.013,0.014,0.000,0.002,0.009],
            [0.087,0.007,0.000,0.069,0.047,0.047,0.069,0.000,0.007,0.087],
            [0.174,0.076,0.000,0.130,0.050,0.050,0.130,0.000,0.076,0.174],
        ]

elif year == 2018:
    altSigVal = [
            [0.021,0.032,0.000,0.050,0.027,0.027,0.050,0.000,0.032,0.021],
            [0.001,0.003,0.000,0.001,0.000,0.000,0.001,0.000,0.003,0.001],
            [0.031,0.016,0.000,0.012,0.008,0.008,0.012,0.000,0.016,0.031],
            [0.004,0.004,0.000,0.003,0.011,0.011,0.003,0.000,0.004,0.004],
            [0.028,0.001,0.000,0.021,0.050,0.050,0.021,0.000,0.001,0.028],
        ]
    altBkgVal = [
            [0.018,0.016,0.000,0.014,0.009,0.009,0.014,0.000,0.016,0.018],
            [0.001,0.001,0.000,0.001,0.001,0.001,0.001,0.000,0.001,0.001],
            [0.006,0.003,0.000,0.002,0.001,0.001,0.002,0.000,0.003,0.006],
            [0.012,0.001,0.000,0.003,0.004,0.004,0.003,0.000,0.001,0.012],
            [0.014,0.001,0.000,0.045,0.002,0.002,0.045,0.000,0.001,0.014],
        ]
    altEffVal = [
            [0.035,0.008,0.000,0.009,0.004,0.004,0.009,0.000,0.008,0.035],
            [0.020,0.003,0.000,0.003,0.002,0.002,0.003,0.000,0.003,0.020],
            [0.023,0.014,0.000,0.011,0.009,0.009,0.011,0.000,0.014,0.023],
            [0.007,0.001,0.000,0.027,0.026,0.026,0.027,0.000,0.001,0.007],
            [0.034,0.037,0.000,0.050,0.025,0.025,0.050,0.000,0.037,0.034],
        ]


sfmap = getObjFromFile( os.path.expandvars( os.path.join( dataDir, g_file ) ), g_key )

altSignal = sfmap.Clone()
altBkg    = sfmap.Clone()
altEff    = sfmap.Clone()

for i in range(sfmap.GetNbinsX()):
    for j in range(sfmap.GetNbinsY()):
        altSignal.SetBinContent(i+1, j+1, altSigVal[j][i])
        altSignal.SetBinError(i+1, j+1, 0)

        altBkg.SetBinContent(i+1, j+1, altBkgVal[j][i])
        altBkg.SetBinError(i+1, j+1, 0)

        altEff.SetBinContent(i+1, j+1, altEffVal[j][i])
        altEff.SetBinError(i+1, j+1, 0)

print
print
print
for i in range(altSignal.GetNbinsX()):
    for j in range(altSignal.GetNbinsY()):
        print altSignal.GetXaxis().GetBinLowEdge(i+1), altSignal.GetYaxis().GetBinLowEdge(j+1), altSignal.GetBinContent(i+1,j+1), altSignal.GetBinError(i+1,j+1)
    print

print
print
print
for i in range(altBkg.GetNbinsX()):
    for j in range(altBkg.GetNbinsY()):
        print altBkg.GetXaxis().GetBinLowEdge(i+1), altBkg.GetYaxis().GetBinLowEdge(j+1), altBkg.GetBinContent(i+1,j+1), altBkg.GetBinError(i+1,j+1)
    print

print
print
print
for i in range(altEff.GetNbinsX()):
    for j in range(altEff.GetNbinsY()):
        print altEff.GetXaxis().GetBinLowEdge(i+1), altEff.GetYaxis().GetBinLowEdge(j+1), altEff.GetBinContent(i+1,j+1), altEff.GetBinError(i+1,j+1)
    print




tRootFile = ROOT.TFile( os.path.expandvars( os.path.join( dataDir, g_file.replace(".root","_mod.root") ) ), "RECREATE" )
sfmap.SetTitle(g_key)
sfmap.SetName(g_key)
sfmap.Write()
altSignal.SetTitle("altSignalModel")
altSignal.SetName("altSignalModel")
altSignal.Write()
altBkg.SetTitle("altBkgModel")
altBkg.SetName("altBkgModel")
altBkg.Write()
altEff.SetTitle("altMCEff")
altEff.SetName("altMCEff")
altEff.Write()
