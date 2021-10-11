import os, sys

os.environ["gammaSkim"] = "True"

#import TTGammaEFT.Samples.nanoTuples_RunII_private_postProcessed as mc_samples
#import TTGammaEFT.Samples.nanoTuples_Summer16_private_v6_semilep_postProcessed as mc_samples
#import TTGammaEFT.Samples.nanoTuples_Fall17_private_v6_semilep_postProcessed as mc_samples
import TTGammaEFT.Samples.nanoTuples_Autumn18_private_v6_semilep_postProcessed as mc_samples
#import TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed as mc_samples
#import TTGammaEFT.Samples.nanoTuples_RunII_postProcessed as mc_samples

#selectionString = "nLeptonTight==1&&nLeptonVetoIsoCorr==1&&nJetGood>=3&&nBTagGood>=1&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1&&triggered==1&&reweightHEM>0&&overlapRemoval==1&&pTStitching==1&&Flag_goodVertices&&Flag_globalSuperTightHalo2016Filter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_BadPFMuonFilter&&PV_ndof>4&&sqrt(PV_x*PV_x+PV_y*PV_y)<=2&&abs(PV_z)<=24"
selectionString = "nLeptonTight==1&&nLeptonVeto==1&&nJetGood>=3&&nBTagGood>=1&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1&&triggered==1&&reweightHEM>0&&overlapRemoval==1&&pTStitching==1&&Flag_goodVertices&&Flag_globalSuperTightHalo2016Filter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_BadPFMuonFilter&&PV_ndof>4&&sqrt(PV_x*PV_x+PV_y*PV_y)<=2&&abs(PV_z)<=24"
#selectionString += "&&PhotonGood0_pt>100"
dlString = "&&!(nLeptonMVA2llead>=1&&nLeptonMVA2l==2)"
weightString = "weight*reweightHEM*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF*(35.92*(year==2016)+41.53*(year==2017)+59.74*(year==2018))"

print selectionString+dlString
#lumi = 137 #35.92+41.53+59.74
#lumi = 35.9
#lumi = 41.53
lumi = 59.74
y1   = mc_samples.TTGSemiLep.getYieldFromDraw(selectionString=selectionString, weightString=weightString)["val"]
y2   = mc_samples.TTGLep.getYieldFromDraw(selectionString=selectionString, weightString=weightString)["val"]

print "1l", y1, y1/lumi
print "2l", y2, y2/lumi

y12l   = mc_samples.TTGSemiLep.getYieldFromDraw(selectionString=selectionString+dlString, weightString=weightString)["val"]
y22l   = mc_samples.TTGLep.getYieldFromDraw(selectionString=selectionString+dlString, weightString=weightString)["val"]

print "1l 2lveto", y12l, y12l/lumi
print "2l 2lveto", y22l, y22l/lumi

print
print "1l ratio", (y1-y12l)/y1
print "2l ratio", (y2-y22l)/y2
print "comb ratio", (y1+y2-y12l-y22l)/(y1+y2)
