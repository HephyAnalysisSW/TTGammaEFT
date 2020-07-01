from TTGammaEFT.Samples.nanoTuples_RunII_postProcessed import *

fiducial_cut = "nGenLeptonCMSUnfold==1&&nGenJetsCMSUnfold>=3&&nGenBJetCMSUnfold>=1&&nGenPhotonCMSUnfold==1"

reco_cut = "nLeptonTight==1&&nLeptonVetoIsoCorr==1&&nJetGood>=3&&nBTagGood>=1&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1&&triggered==1&&reweightHEM>0&&overlapRemoval==1&&(PhotonGood0_photonCatMagic==0||PhotonGood0_photonCatMagic==2)&&((year==2016&&Flag_goodVertices&&Flag_globalSuperTightHalo2016Filter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_BadPFMuonFilter&&PV_ndof>4&&sqrt(PV_x*PV_x+PV_y*PV_y)<=2&&abs(PV_z)<=24)||(year==2017&&Flag_goodVertices&&Flag_globalSuperTightHalo2016Filter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_BadPFMuonFilter&&PV_ndof>4&&sqrt(PV_x*PV_x+PV_y*PV_y)<=2&&abs(PV_z)<=24)||(year==2018&&Flag_goodVertices&&Flag_globalSuperTightHalo2016Filter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_BadPFMuonFilter&&PV_ndof>4&&sqrt(PV_x*PV_x+PV_y*PV_y)<=2&&abs(PV_z)<=24))"

#lumi_weight_str = "(%f*(year==2016)+%f*(year==2017)+%f*(year==2018))"%(Run2016.lumi/1000,Run2017.lumi/1000,Run2018.lumi/1000)

weight = "%s*weight*reweightHEM*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF" % lumi_weight_str


#sigma_fiducial_fb = Summer16.TTG.getYieldFromDraw(fiducial, "weight")['val']
sigma_fiducial_fb = 984.7595363975266

#sigma_reco        = Summer16.TTG.getYieldFromDraw("("+fiducial+")*("+reco+")", "weight")['val']
sigma_reco_fb     = 241.11019826708844

sigma_reco_fb_scale = {}
#sigma_fiducial_fb_scale = {}
for i in range(44):
    print "At", i
#    sigma_fiducial_fb_scale[i] = Summer16.TTG.getYieldFromDraw(fiducial, "weight*LHEScaleWeight[%i]"%i)['val'] 
    sigma_reco_fb_scale[i] = Summer16.TTG.getYieldFromDraw("("+fiducial+")*("+reco+")", "weight*LHEScaleWeight[%i]"%i)['val'] 

sigma_fiducial_fb_scale =  {0: 1270.7440078175757,
 1: 1043.8907244334152,
 2: 1043.8880889820168,
 3: 1352.6458210245125,
 4: 941.6889908079887,
 5: 1190.3193368796121,
 6: 978.8442992144011,
 7: 978.8418328499976,
 8: 1267.313246930657,
 9: 884.4440859011354,
 10: 1116.4052122996482,
 11: 919.3605554770089,
 12: 919.3582475569109,
 13: 1188.4938999706342,
 14: 832.0528529339463,
 15: 1051.4328549645277,
 16: 875.4043251485714,
 17: 875.4022774714103,
 18: 1114.347544442174,
 19: 794.6999897635031,
 20: 820.7716311382767,
 21: 820.7697110294814,
 22: 1043.8880889820168,
 23: 746.2947454608061,
 24: 923.5101872064142,
 25: 770.8271573126665,
 26: 770.8253589823062,
 27: 978.8418328499976,
 28: 702.0102594464723,
 29: 884.9803229030302,
 30: 745.0797407352995,
 31: 745.0780970257979,
 32: 934.6078812692773,
 33: 679.9778823374996,
 34: 828.77230620438,
 35: 698.5196899063993,
 36: 698.5181536942422,
 37: 875.4022774714103,
 38: 638.4911876201054,
 39: 777.1554063367956,
 40: 655.9666267699122,
 41: 655.9651910951202,
 42: 820.7697110294814,
 43: 600.5482335862893}
