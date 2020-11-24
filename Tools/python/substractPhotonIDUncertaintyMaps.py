import ROOT
import os, sys
from math import sqrt

from Analysis.Tools.helpers import getObjFromFile

dataDir = "$CMSSW_BASE/src/Analysis/Tools/data/photonSFData/"
year = 2018

if year == 2016:
    g_file = 'g2016_egammaPlots_MWP_PhoSFs_2016_LegacyReReco_New.root'
else:
    g_file = 'g%i_PhotonsMedium_mod.root'%year

g_key   = "EGamma_SF2D"
gAS_key   = "altSignalModel"
gAB_key   = "altBkgModel"
gAEff_key   = "altMCEff"

sfmap = getObjFromFile( os.path.expandvars( os.path.join( dataDir, g_file ) ), g_key )
sfASmap = getObjFromFile( os.path.expandvars( os.path.join( dataDir, g_file ) ), gAS_key )
sfABmap = getObjFromFile( os.path.expandvars( os.path.join( dataDir, g_file ) ), gAB_key )
sfAEffmap = getObjFromFile( os.path.expandvars( os.path.join( dataDir, g_file ) ), gAEff_key )

for i in range(sfmap.GetNbinsX()):
    for j in range(sfmap.GetNbinsY()):
        print sfmap.GetXaxis().GetBinLowEdge(i+1), sfmap.GetYaxis().GetBinLowEdge(j+1), sfmap.GetBinContent(i+1,j+1), sfmap.GetBinError(i+1,j+1), "unc", sfASmap.GetBinContent(i+1,j+1), sfABmap.GetBinContent(i+1,j+1), sfAEffmap.GetBinContent(i+1,j+1)
    print

totalUnc  = sfmap.Clone()

for i in range(sfmap.GetNbinsX()):
    for j in range(sfmap.GetNbinsY()):
        totalUnc.SetBinContent(i+1, j+1, totalUnc.GetBinError(i+1, j+1))
        totalUnc.SetBinError(i+1, j+1, 0)

sfUnc     = totalUnc.Clone()
altSignal = sfASmap.Clone()
altBkg = sfABmap.Clone()
altEff = sfAEffmap.Clone()

qAltSignal = altSignal.Clone()
qAltSignal.Multiply(qAltSignal)
qAltBkg = altBkg.Clone()
qAltBkg.Multiply(qAltBkg)
qAltEff = altEff.Clone()
qAltEff.Multiply(qAltEff)

sfUnc.Multiply(sfUnc)
sfUnc.Add(qAltSignal, -1)
sfUnc.Add(qAltBkg, -1)
sfUnc.Add(qAltEff, -1)

qAlt = qAltSignal.Clone()
qAlt.Add(qAltBkg)
qAlt.Add(qAltEff)

for i in range(sfmap.GetNbinsX()):
    for j in range(sfmap.GetNbinsY()):
        qunc = sfUnc.GetBinContent(i+1, j+1)
        if qunc < 0 and qunc > -0.0001:
            qunc = 0.001
        else:
            qunc = sqrt(qunc)
        sfmap.SetBinError(i+1, j+1, qunc)

for i in range(sfmap.GetNbinsX()):
    for j in range(sfmap.GetNbinsY()):
        altSignal.SetBinError(i+1, j+1, sqrt(qAlt.GetBinContent(i+1,j+1)))
        altSignal.SetBinContent(i+1, j+1, sfmap.GetBinContent(i+1,j+1))


print
print
print
print
print
for i in range(sfmap.GetNbinsX()):
    for j in range(sfmap.GetNbinsY()):
        print sfmap.GetXaxis().GetBinLowEdge(i+1), sfmap.GetYaxis().GetBinLowEdge(j+1), sfmap.GetBinContent(i+1,j+1), sfmap.GetBinError(i+1,j+1)
    print

print
print
print
print
print
#for i in range(altSignal.GetNbinsX()):
#    for j in range(altSignal.GetNbinsY()):
#        print altSignal.GetXaxis().GetBinLowEdge(i+1), altSignal.GetYaxis().GetBinLowEdge(j+1), altSignal.GetBinContent(i+1,j+1), altSignal.GetBinError(i+1,j+1)
#    print




#tRootFile = ROOT.TFile( os.path.expandvars( os.path.join( dataDir, g_file.replace(".root","_private.root") ) ), "RECREATE" )
#sfmap.SetTitle(g_key)
#sfmap.SetName(g_key)
#sfmap.Write()
#altSignal.SetTitle(g_key+"_altModel")
#altSignal.SetName(g_key+"_altModel")
#altSignal.Write()
