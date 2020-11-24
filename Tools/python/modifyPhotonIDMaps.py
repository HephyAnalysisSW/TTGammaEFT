import ROOT
import os, sys

from Analysis.Tools.helpers import getObjFromFile

year = 2017

dataDir = "$CMSSW_BASE/src/Analysis/Tools/data/photonSFData/"
if year == 2016:
    g_file = "g2016_egammaPlots_MWP_PhoSFs_2016_LegacyReReco_New_private.root"
else:
    g_file  = 'g%i_PhotonsMedium_mod_private.root'%year
g_key   = "EGamma_SF2D"
gAS_key = "EGamma_SF2D_altModel"

sfmap = getObjFromFile( os.path.expandvars( os.path.join( dataDir, g_file ) ), g_key )
sfASmap = getObjFromFile( os.path.expandvars( os.path.join( dataDir, g_file ) ), gAS_key )

#for i in range(sfmap.GetNbinsX()):
#    for j in range(sfmap.GetNbinsY()):
#        print sfmap.GetXaxis().GetBinLowEdge(i+1), sfmap.GetYaxis().GetBinLowEdge(j+1), sfmap.GetBinContent(i+1,j+1), sfmap.GetBinError(i+1,j+1)
#    print


for i in range(sfmap.GetNbinsX()):
    if abs( sfmap.GetXaxis().GetBinLowEdge(i+1) ) > 1.5 or sfmap.GetXaxis().GetBinLowEdge(i+1) >= 1.444: continue
    for j in range(sfmap.GetNbinsY()):
        if (year == 2017 and sfmap.GetYaxis().GetBinLowEdge(j+1) >= 100) or (year == 2018 and sfmap.GetYaxis().GetBinLowEdge(j+1) >= 200) or (year == 2016 and sfmap.GetYaxis().GetBinLowEdge(j+1) >= 200):
#            print sfmap.GetYaxis().GetBinLowEdge(j+1), sfmap.GetBinError(i+1,j+1), "-> 0.02"
            sfmap.SetBinError(i+1,j+1, 0.02)
            if year == 2017:
                if sfmap.GetYaxis().GetBinLowEdge(j+1) >= 190:
                    if abs( sfmap.GetXaxis().GetBinLowEdge(i+1) ) > 0.8:
                        sfmap.SetBinContent(i+1,j+1, 1.015)
                    else:
                        sfmap.SetBinContent(i+1,j+1, 1.029)
                else:
                    if abs( sfmap.GetXaxis().GetBinLowEdge(i+1) ) > 0.8:
                        sfmap.SetBinContent(i+1,j+1, 1.015)
                        sfmap.SetBinError(i+1,j+1, 0.014)
                    else:
                        sfmap.SetBinContent(i+1,j+1, 1.029)
                        sfmap.SetBinError(i+1,j+1, 0.024)
            elif year == 2018 or year == 2016:
                if abs( sfmap.GetXaxis().GetBinLowEdge(i+1) ) > 0.8:
                    sfmap.SetBinContent(i+1,j+1, 1.019)
                else:
                    sfmap.SetBinContent(i+1,j+1, 1.022)

#print
#print
#print
#print

#for i in range(sfmap.GetNbinsX()):
#    for j in range(sfmap.GetNbinsY()):
#        print sfmap.GetXaxis().GetBinLowEdge(i+1), sfmap.GetYaxis().GetBinLowEdge(j+1), sfmap.GetBinContent(i+1,j+1), sfmap.GetBinError(i+1,j+1)
#    print




tRootFile = ROOT.TFile( os.path.expandvars( os.path.join( dataDir, g_file.replace(".root","_BostonAdded.root") ) ), "RECREATE" )
sfmap.SetTitle(g_key)
sfmap.SetName(g_key)
sfmap.Write()
sfASmap.Write()
