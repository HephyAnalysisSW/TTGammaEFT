import os, math
import copy
import ROOT
import array
from Analysis.Tools.MergingDirDB      import MergingDirDB

#from TTGammaEFT.Samples.nanoTuples_RunII_postProcessed import lumi_year
# hard coded to remove dependency
lumi_year = {2016: 35920.0, 2017: 41530.0, 2018: 59740.0}

jesSyst_all  = ['FlavorQCD', 'RelativeBal', 'HF', 'BBEC1', 'EC2', 'Absolute']
for y in ["2016","2017","2018"]:
    jesSyst_all += ['Absolute_%s'%y, 'HF_%s'%y, 'EC2_%s'%y, 'RelativeSample_%s'%y, 'BBEC1_%s'%y]

systematic_pairs  = [ ('photonSFUp',  'photonSFDown'), ('photonElectronVetoSFUp',  'photonElectronVetoSFDown'), ('eResUp', 'eResDown'), ('eScaleUp', 'eScaleDown'), ("jerUp","jerDown") ]
systematic_pairs += [ ("TuneUp","TuneDown") ]
systematic_pairs += [ ("TriggerUp", "TriggerDown"), ("BTag_SF_b_Up","BTag_SF_b_Down"), ("LeptonTrackingTightSFUp","LeptonTrackingTightSFDown") ]
systematic_pairs += [ ("LeptonTightSFUp","LeptonTightSFDown"), ("L1PrefireUp","L1PrefireDown"), ("PUUp","PUDown") ]
systematic_pairs += [ ("jes"+v+"Up","jes"+v+"Down") for v in jesSyst_all ]

systematic_pairs += [ ("ISRUp","ISRDown"), ("FSRUp","FSRDown") ]
all_systematics = ['nominal','reweightTopPt','erdOn','GluonMove','QCDbased','ScaleDownDown','ScaleDownNom','ScaleNomDown','ScaleNomUp','ScaleUpNom','ScaleUpUp'] + sum([list(p) for p in systematic_pairs],[])

additional_Matrix_uncertainties = [m for m in all_systematics if not "Down" in m and not m.startswith("Scale") ] # and not "201" in m]
additional_MatrixScale_uncertainties = ['ScaleDownDown','ScaleDownNom','ScaleNomDown','ScaleNomUp','ScaleUpNom','ScaleUpUp']

allUncertainties = [
    "DY_normalization", "EGammaResolution", "EGammaScale", "FSR", "GluonMove", "Gluon_splitting", "ISR", "Int_Luminosity_2016", "Int_Luminosity_2016_2017", "Int_Luminosity_2017",
    "Int_Luminosity_2017_2018", "Int_Luminosity_2018", "Int_Luminosity_corr", "JEC_Absolute", "JEC_Absolute_2016", "JEC_Absolute_2017", "JEC_Absolute_2018", "JEC_BBEC1", "JEC_BBEC1_2016",
    "JEC_BBEC1_2017", "JEC_BBEC1_2018", "JEC_EC2", "JEC_EC2_2016", "JEC_EC2_2017", "JEC_EC2_2018", "JEC_FlavorQCD", "JEC_HF", "JEC_HF_2016", "JEC_HF_2017", "JEC_HF_2018", "JEC_RelativeBal",
    "JEC_RelativeSample_2016", "JEC_RelativeSample_2017", "JEC_RelativeSample_2018",
    "JER_2016",
    "JER_2017", "JER_2018", "L1_Prefiring", "MisID_extrapolation_2016", "MisID_extrapolation_2017",
    "MisID_extrapolation_2018", "MisID_nJet_dependence_2016", "MisID_nJet_dependence_2017", "MisID_nJet_dependence_2018", "MisID_normalization_2016", "MisID_normalization_2017",
    "MisID_normalization_2018", "Other_normalization", "PDF", "PU", "QCD_0b_nJet_dependence", "QCD_0b_normalization", "QCD_1b_nJet_dependence", "QCD_1b_normalization", "QCD_normalization",
    "QCDbased", "Scale", "TT_normalization", "Trigger_electrons_2016", "Trigger_electrons_2017", "Trigger_electrons_2018", "Trigger_muons_2016", "Trigger_muons_2017", "Trigger_muons_2018",
    "Tune", "WGamma_nJet_dependence", "WGamma_normalization", "WGamma_pT_Bin1", "WGamma_pT_Bin2", "ZGamma_nJet_dependence", "ZGamma_normalization", "ZGamma_pT_Bin1", "ZGamma_pT_Bin2",
    "electron_ID", "electron_reco", "erdOn", "fake_photon_DD_normalization", "fake_photon_MC_normalization", "fake_photon_model_2017", "heavy_flavor_2016", "heavy_flavor_2017_2018",
    "light_flavor_2016", "light_flavor_2017_2018", "misID_pT_Bin1_2016", "misID_pT_Bin1_2017", "misID_pT_Bin1_2018", "misID_pT_Bin2_2016", "misID_pT_Bin2_2017", "misID_pT_Bin2_2018",
    "misID_pT_Bin3_2016", "misID_pT_Bin3_2017", "misID_pT_Bin3_2018", "misID_pT_Bin4_2016", "misID_pT_Bin4_2017", "misID_pT_Bin4_2018", "misID_pT_Bin5_2016", "misID_pT_Bin5_2017",
    "misID_pT_Bin5_2018", "misID_pT_Bin6_2016", "misID_pT_Bin6_2017", "misID_pT_Bin6_2018", "muon_ID_extrapolation", "muon_ID_sta_2016", "muon_ID_sta_2017", "muon_ID_sta_2018", "muon_ID_syst",
    "photon_ID", "pixelSeed_veto_2016", "pixelSeed_veto_2017", "pixelSeed_veto_2018", "top_pt_reweighting",
    "r",
    ]

signal_uncertainty_ptG = ['Signal_mu_3_Bin6_2016', 'Signal_mu_3_Bin6_2017', 'Signal_mu_3_Bin6_2018', 'Signal_e_3_Bin9_2018', 'Signal_e_3_Bin6_2018', 'Signal_e_3_Bin0_2016', 'Signal_e_3_Bin0_2017', 'Signal_e_3_Bin0_2018', 'Signal_mu_4p_Bin5_2017', 'Signal_mu_4p_Bin5_2016', 'Signal_mu_3_Bin1_2018', 'Signal_mu_3_Bin1_2017', 'Signal_mu_3_Bin1_2016', 'Signal_mu_4p_Bin6_2016', 'Signal_mu_4p_Bin6_2017', 'Signal_mu_4p_Bin6_2018', 'Signal_mu_4p_Bin8_2018', 'Signal_mu_4p_Bin8_2016', 'Signal_mu_4p_Bin8_2017', 'Signal_mu_3_Bin9_2017', 'Signal_mu_3_Bin9_2016', 'Signal_mu_3_Bin9_2018', 'Signal_mu_4p_Bin3_2018', 'Signal_mu_4p_Bin3_2017', 'Signal_mu_4p_Bin3_2016', 'Signal_e_3_Bin10_2016', 'Signal_e_3_Bin10_2017', 'Signal_mu_3_Bin7_2018', 'Signal_mu_3_Bin7_2017', 'Signal_mu_3_Bin7_2016', 'Signal_e_3_Bin10_2018', 'Signal_mu_3_Bin0_2018', 'Signal_mu_3_Bin0_2016', 'Signal_mu_3_Bin0_2017', 'Signal_e_3_Bin6_2016', 'Signal_e_4p_Bin3_2018', 'Signal_e_4p_Bin3_2016', 'Signal_e_3_Bin1_2017', 'Signal_e_3_Bin1_2016', 'Signal_e_3_Bin1_2018', 'Signal_e_4p_Bin5_2018', 'Signal_e_4p_Bin5_2017', 'Signal_e_4p_Bin5_2016', 'Signal_mu_3_Bin4_2018', 'Signal_e_4p_Bin7_2018', 'Signal_e_4p_Bin1_2018', 'Signal_e_4p_Bin1_2017', 'Signal_e_4p_Bin1_2016', 'Signal_e_4p_Bin7_2017', 'Signal_e_4p_Bin7_2016', 'Signal_mu_3_Bin4_2016', 'Signal_mu_3_Bin4_2017', 'Signal_e_4p_Bin4_2018', 'Signal_e_4p_Bin4_2016', 'Signal_e_4p_Bin4_2017', 'Signal_mu_4p_Bin10_2018', 'Signal_e_3_Bin2_2016', 'Signal_e_3_Bin2_2017', 'Signal_e_3_Bin2_2018', 'Signal_mu_4p_Bin4_2016', 'Signal_mu_4p_Bin4_2017', 'Signal_mu_4p_Bin4_2018', 'Signal_mu_3_Bin8_2016', 'Signal_mu_3_Bin8_2017', 'Signal_e_4p_Bin2_2016', 'Signal_mu_3_Bin8_2018', 'Signal_e_4p_Bin6_2016', 'Signal_e_4p_Bin6_2017', 'Signal_e_3_Bin4_2016', 'Signal_e_3_Bin4_2017', 'Signal_e_3_Bin4_2018', 'Signal_e_4p_Bin6_2018', 'Signal_mu_3_Bin2_2016', 'Signal_mu_3_Bin2_2017', 'Signal_mu_4p_Bin2_2016', 'Signal_mu_4p_Bin2_2017', 'Signal_mu_4p_Bin2_2018', 'Signal_mu_3_Bin10_2018', 'Signal_mu_3_Bin10_2016', 'Signal_mu_3_Bin10_2017', 'Signal_mu_4p_Bin5_2018', 'Signal_mu_4p_Bin7_2017', 'Signal_mu_4p_Bin7_2016', 'Signal_mu_4p_Bin7_2018', 'Signal_mu_4p_Bin10_2016', 'Signal_e_3_Bin7_2017', 'Signal_e_3_Bin7_2016', 'Signal_mu_4p_Bin10_2017', 'Signal_e_3_Bin7_2018', 'Signal_mu_3_Bin3_2018', 'Signal_mu_3_Bin3_2017', 'Signal_mu_3_Bin3_2016', 'Signal_e_4p_Bin9_2017', 'Signal_e_4p_Bin9_2016', 'Signal_e_4p_Bin9_2018', 'Signal_e_3_Bin3_2017', 'Signal_e_3_Bin3_2016', 'Signal_e_4p_Bin10_2018', 'Signal_e_4p_Bin10_2016', 'Signal_e_4p_Bin10_2017', 'Signal_e_3_Bin3_2018', 'Signal_e_4p_Bin2_2017', 'Signal_e_3_Bin9_2016', 'Signal_mu_3_Bin5_2018', 'Signal_e_3_Bin8_2018', 'Signal_mu_3_Bin5_2017', 'Signal_mu_3_Bin5_2016', 'Signal_e_3_Bin9_2017', 'Signal_e_3_Bin8_2017', 'Signal_e_3_Bin6_2017', 'Signal_e_4p_Bin3_2017', 'Signal_e_3_Bin5_2018', 'Signal_e_3_Bin5_2017', 'Signal_e_3_Bin5_2016', 'Signal_e_4p_Bin8_2016', 'Signal_e_4p_Bin8_2017', 'Signal_mu_4p_Bin0_2016', 'Signal_mu_4p_Bin0_2017', 'Signal_mu_4p_Bin0_2018', 'Signal_e_4p_Bin8_2018', 'Signal_e_4p_Bin2_2018', 'Signal_mu_4p_Bin9_2018', 'Signal_mu_3_Bin2_2018', 'Signal_mu_4p_Bin9_2017', 'Signal_mu_4p_Bin9_2016', 'Signal_e_3_Bin8_2016', 'Signal_mu_4p_Bin1_2017', 'Signal_mu_4p_Bin1_2016', 'Signal_mu_4p_Bin1_2018']
signal_uncertainty_absEta = ['Signal_mu_3_Bin6_2016', 'Signal_mu_3_Bin6_2017', 'Signal_mu_3_Bin6_2018', 'Signal_e_3_Bin9_2018', 'Signal_e_3_Bin6_2018', 'Signal_e_3_Bin0_2016', 'Signal_e_3_Bin0_2017', 'Signal_e_3_Bin0_2018', 'Signal_mu_4p_Bin5_2018', 'Signal_mu_3_Bin1_2018', 'Signal_mu_3_Bin1_2016', 'Signal_mu_4p_Bin6_2016', 'Signal_mu_4p_Bin6_2017', 'Signal_mu_4p_Bin6_2018', 'Signal_mu_4p_Bin8_2018', 'Signal_mu_4p_Bin8_2016', 'Signal_mu_4p_Bin8_2017', 'Signal_mu_3_Bin9_2017', 'Signal_mu_3_Bin9_2016', 'Signal_mu_3_Bin9_2018', 'Signal_mu_4p_Bin3_2018', 'Signal_mu_4p_Bin3_2017', 'Signal_mu_4p_Bin3_2016', 'Signal_mu_3_Bin7_2018', 'Signal_mu_3_Bin7_2017', 'Signal_mu_3_Bin7_2016', 'Signal_mu_3_Bin0_2018', 'Signal_mu_3_Bin0_2016', 'Signal_mu_3_Bin0_2017', 'Signal_e_3_Bin6_2016', 'Signal_e_4p_Bin3_2018', 'Signal_e_4p_Bin3_2016', 'Signal_e_3_Bin1_2017', 'Signal_e_3_Bin1_2016', 'Signal_e_3_Bin1_2018', 'Signal_e_4p_Bin5_2018', 'Signal_e_4p_Bin5_2017', 'Signal_e_4p_Bin5_2016', 'Signal_mu_3_Bin4_2018', 'Signal_e_4p_Bin7_2018', 'Signal_e_4p_Bin1_2018', 'Signal_e_4p_Bin1_2017', 'Signal_e_4p_Bin1_2016', 'Signal_e_4p_Bin7_2017', 'Signal_e_4p_Bin7_2016', 'Signal_mu_3_Bin4_2016', 'Signal_mu_3_Bin4_2017', 'Signal_e_4p_Bin4_2018', 'Signal_e_4p_Bin4_2016', 'Signal_e_4p_Bin4_2017', 'Signal_e_3_Bin2_2016', 'Signal_e_3_Bin2_2017', 'Signal_e_3_Bin2_2018', 'Signal_mu_4p_Bin4_2016', 'Signal_mu_4p_Bin4_2017', 'Signal_mu_4p_Bin4_2018', 'Signal_mu_3_Bin8_2016', 'Signal_mu_3_Bin8_2017', 'Signal_e_4p_Bin2_2016', 'Signal_mu_3_Bin8_2018', 'Signal_e_4p_Bin6_2016', 'Signal_e_4p_Bin6_2017', 'Signal_e_3_Bin4_2016', 'Signal_e_3_Bin4_2017', 'Signal_e_3_Bin4_2018', 'Signal_e_4p_Bin6_2018', 'Signal_mu_3_Bin2_2016', 'Signal_mu_3_Bin2_2017', 'Signal_mu_4p_Bin5_2017', 'Signal_mu_4p_Bin5_2016', 'Signal_mu_4p_Bin2_2016', 'Signal_mu_4p_Bin2_2017', 'Signal_mu_4p_Bin2_2018', 'Signal_mu_4p_Bin7_2017', 'Signal_mu_4p_Bin7_2016', 'Signal_mu_4p_Bin7_2018', 'Signal_e_3_Bin7_2017', 'Signal_e_3_Bin7_2016', 'Signal_e_3_Bin7_2018', 'Signal_mu_3_Bin1_2017', 'Signal_mu_3_Bin3_2018', 'Signal_mu_3_Bin3_2017', 'Signal_mu_3_Bin3_2016', 'Signal_e_4p_Bin9_2017', 'Signal_e_4p_Bin9_2016', 'Signal_e_4p_Bin9_2018', 'Signal_e_3_Bin3_2017', 'Signal_e_3_Bin3_2016', 'Signal_e_3_Bin3_2018', 'Signal_mu_4p_Bin9_2017', 'Signal_e_4p_Bin2_2017', 'Signal_e_3_Bin9_2017', 'Signal_e_3_Bin9_2016', 'Signal_mu_3_Bin5_2018', 'Signal_e_3_Bin8_2018', 'Signal_mu_3_Bin5_2017', 'Signal_mu_3_Bin5_2016', 'Signal_e_3_Bin8_2017', 'Signal_e_3_Bin6_2017', 'Signal_e_4p_Bin3_2017', 'Signal_e_3_Bin5_2018', 'Signal_e_3_Bin5_2017', 'Signal_e_3_Bin5_2016', 'Signal_e_4p_Bin8_2016', 'Signal_e_4p_Bin8_2017', 'Signal_mu_4p_Bin0_2016', 'Signal_mu_4p_Bin0_2017', 'Signal_mu_4p_Bin0_2018', 'Signal_mu_4p_Bin1_2016', 'Signal_e_4p_Bin8_2018', 'Signal_e_4p_Bin2_2018', 'Signal_mu_4p_Bin9_2018', 'Signal_mu_3_Bin2_2018', 'Signal_mu_4p_Bin9_2016', 'Signal_e_3_Bin8_2016', 'Signal_mu_4p_Bin1_2017', 'Signal_mu_4p_Bin1_2018']
signal_uncertainty_dRlg = ['Signal_mu_3_Bin6_2016', 'Signal_mu_3_Bin6_2017', 'Signal_e_3_Bin6_2017', 'Signal_mu_4p_Bin11_2018', 'Signal_mu_3_Bin6_2018', 'Signal_e_3_Bin9_2018', 'Signal_e_3_Bin6_2018', 'Signal_e_3_Bin0_2016', 'Signal_e_3_Bin0_2017', 'Signal_mu_3_Bin5_2018', 'Signal_e_3_Bin0_2018', 'Signal_mu_4p_Bin5_2017', 'Signal_mu_4p_Bin5_2016', 'Signal_mu_4p_Bin5_2018', 'Signal_mu_3_Bin1_2018', 'Signal_mu_3_Bin1_2017', 'Signal_mu_3_Bin1_2016', 'Signal_mu_4p_Bin6_2016', 'Signal_mu_4p_Bin6_2017', 'Signal_mu_4p_Bin6_2018', 'Signal_e_3_Bin13_2017', 'Signal_e_3_Bin13_2016', 'Signal_e_3_Bin13_2018', 'Signal_mu_4p_Bin8_2018', 'Signal_mu_4p_Bin8_2016', 'Signal_mu_4p_Bin8_2017', 'Signal_e_4p_Bin12_2018', 'Signal_e_4p_Bin12_2016', 'Signal_e_4p_Bin12_2017', 'Signal_e_4p_Bin13_2017', 'Signal_e_4p_Bin13_2016', 'Signal_mu_3_Bin9_2017', 'Signal_mu_3_Bin9_2016', 'Signal_mu_3_Bin13_2016', 'Signal_mu_3_Bin9_2018', 'Signal_e_4p_Bin13_2018', 'Signal_mu_4p_Bin3_2018', 'Signal_mu_4p_Bin3_2017', 'Signal_mu_4p_Bin3_2016', 'Signal_e_3_Bin10_2016', 'Signal_e_3_Bin10_2017', 'Signal_mu_3_Bin7_2018', 'Signal_mu_3_Bin7_2017', 'Signal_mu_3_Bin7_2016', 'Signal_e_3_Bin10_2018', 'Signal_mu_3_Bin0_2018', 'Signal_mu_3_Bin0_2016', 'Signal_mu_3_Bin0_2017', 'Signal_mu_3_Bin2_2018', 'Signal_e_3_Bin6_2016', 'Signal_e_4p_Bin3_2016', 'Signal_e_3_Bin1_2017', 'Signal_e_3_Bin1_2016', 'Signal_e_3_Bin1_2018', 'Signal_e_4p_Bin5_2018', 'Signal_e_4p_Bin5_2017', 'Signal_e_4p_Bin5_2016', 'Signal_mu_3_Bin4_2018', 'Signal_e_4p_Bin7_2018', 'Signal_e_4p_Bin1_2018', 'Signal_e_4p_Bin1_2017', 'Signal_e_4p_Bin1_2016', 'Signal_e_4p_Bin7_2017', 'Signal_mu_3_Bin4_2017', 'Signal_mu_3_Bin4_2016', 'Signal_e_4p_Bin7_2016', 'Signal_e_4p_Bin4_2018', 'Signal_e_4p_Bin4_2016', 'Signal_e_4p_Bin4_2017', 'Signal_mu_4p_Bin10_2018', 'Signal_e_3_Bin2_2016', 'Signal_e_3_Bin2_2017', 'Signal_e_3_Bin2_2018', 'Signal_e_3_Bin12_2016', 'Signal_e_3_Bin12_2018', 'Signal_mu_4p_Bin4_2016', 'Signal_mu_4p_Bin4_2017', 'Signal_mu_4p_Bin4_2018', 'Signal_mu_3_Bin8_2016', 'Signal_mu_3_Bin8_2017', 'Signal_e_4p_Bin2_2016', 'Signal_mu_3_Bin8_2018', 'Signal_e_4p_Bin6_2016', 'Signal_e_4p_Bin6_2017', 'Signal_e_3_Bin4_2016', 'Signal_e_3_Bin4_2017', 'Signal_e_3_Bin4_2018', 'Signal_e_4p_Bin6_2018', 'Signal_mu_3_Bin2_2016', 'Signal_mu_3_Bin2_2017', 'Signal_e_4p_Bin11_2018', 'Signal_e_4p_Bin11_2017', 'Signal_e_4p_Bin11_2016', 'Signal_mu_4p_Bin2_2016', 'Signal_mu_4p_Bin2_2017', 'Signal_mu_4p_Bin2_2018', 'Signal_mu_3_Bin10_2018', 'Signal_mu_3_Bin10_2016', 'Signal_mu_3_Bin10_2017', 'Signal_mu_3_Bin12_2018', 'Signal_mu_4p_Bin7_2017', 'Signal_mu_4p_Bin7_2016', 'Signal_mu_4p_Bin7_2018', 'Signal_mu_3_Bin12_2016', 'Signal_mu_3_Bin12_2017', 'Signal_mu_3_Bin11_2018', 'Signal_e_3_Bin7_2017', 'Signal_e_3_Bin7_2016', 'Signal_mu_4p_Bin10_2017', 'Signal_e_3_Bin7_2018', 'Signal_mu_3_Bin11_2017', 'Signal_mu_3_Bin11_2016', 'Signal_mu_4p_Bin12_2016', 'Signal_mu_4p_Bin12_2017', 'Signal_mu_4p_Bin12_2018', 'Signal_e_3_Bin11_2017', 'Signal_e_3_Bin11_2016', 'Signal_mu_3_Bin3_2018', 'Signal_mu_3_Bin3_2017', 'Signal_mu_3_Bin3_2016', 'Signal_e_3_Bin11_2018', 'Signal_e_4p_Bin9_2017', 'Signal_e_4p_Bin9_2016', 'Signal_e_4p_Bin9_2018', 'Signal_e_3_Bin3_2017', 'Signal_e_3_Bin3_2016', 'Signal_e_4p_Bin10_2018', 'Signal_mu_4p_Bin13_2017', 'Signal_mu_4p_Bin13_2016', 'Signal_mu_4p_Bin13_2018', 'Signal_e_4p_Bin10_2016', 'Signal_e_4p_Bin10_2017', 'Signal_e_3_Bin3_2018', 'Signal_mu_3_Bin13_2017', 'Signal_e_4p_Bin2_2017', 'Signal_e_3_Bin9_2016', 'Signal_mu_4p_Bin11_2017', 'Signal_mu_4p_Bin11_2016', 'Signal_e_3_Bin12_2017', 'Signal_mu_3_Bin5_2017', 'Signal_mu_3_Bin5_2016', 'Signal_e_3_Bin9_2017', 'Signal_e_3_Bin8_2017', 'Signal_mu_3_Bin13_2018', 'Signal_e_4p_Bin3_2018', 'Signal_e_4p_Bin3_2017', 'Signal_e_3_Bin5_2018', 'Signal_e_3_Bin5_2017', 'Signal_e_3_Bin5_2016', 'Signal_e_4p_Bin8_2016', 'Signal_e_4p_Bin8_2017', 'Signal_mu_4p_Bin0_2016', 'Signal_mu_4p_Bin0_2017', 'Signal_mu_4p_Bin0_2018', 'Signal_e_4p_Bin8_2018', 'Signal_e_4p_Bin2_2018', 'Signal_mu_4p_Bin9_2018', 'Signal_mu_4p_Bin9_2017', 'Signal_mu_4p_Bin9_2016', 'Signal_mu_4p_Bin10_2016', 'Signal_e_3_Bin8_2018', 'Signal_e_3_Bin8_2016', 'Signal_mu_4p_Bin1_2017', 'Signal_mu_4p_Bin1_2016', 'Signal_mu_4p_Bin1_2018']

def add_sigmas( h, sigmas, ref = None):
    if not h: return None
    ref_ = ref if ref is not None else h
    res = copy.deepcopy(h.Clone())
    for i in range(0, h.GetNbinsX()+2):
        res.SetBinContent( i, ref_.GetBinContent( i ) + sigmas*h.GetBinError( i ) )
        res.SetBinError( i, ref_.GetBinError( i ) )
    return res

def replace_data_error( h ):
    return h
#    if not h: return None
#    res = copy.deepcopy(h.Clone())
#    for i in range(0, res.GetNbinsX()+2):
#        res.SetBinError( i, math.sqrt(res.GetBinContent( i )) )
#    return res

def add_error_from_Upvariation( h, ref ):
    if not h: return None
    res = copy.deepcopy(h.Clone())
    for i in range(0, h.GetNbinsX()+2):
        res.SetBinError( i, abs(h.GetBinContent( i ) - ref.GetBinContent( i )) )
        res.SetBinContent( i, ref.GetBinContent( i ) )
    return res

def thresholds_from_histo( histo ):
    last_bin        = histo.GetNbinsX()
    return tuple([histo.GetBinLowEdge(i) for i in range(1,last_bin+1)] + [ histo.GetBinLowEdge(last_bin) + histo.GetBinWidth(last_bin) ])

def merge_x( histos, bin_threshold_years):

    input_bins = []
    for i_year, bins_in_year in enumerate(map( lambda h: range(1, h.GetNbinsX()+1), histos )):
        for i_t, bin_in_year in enumerate(bins_in_year):
            input_bins.append( (i_year, bin_in_year) )

    assert len(input_bins) == len(bin_threshold_years)-1, "Inconsistent number of input thresholds!"

    output = ROOT.TH1D(histos[0].GetName(), histos[0].GetTitle(), len(bin_threshold_years)-1, array.array('d', bin_threshold_years))

    for i_bin_output, (i_year, bin_input) in enumerate(input_bins):
        output.SetBinContent( i_bin_output + 1, histos[i_year].GetBinContent(bin_input) )  
        output.SetBinError ( i_bin_output + 1, histos[i_year].GetBinError (bin_input) ) 

    # Note: Leave overflows empty 
    return output

default_cache_directory = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/"

class observed_ptG_2016:
#  if False:
    uncertainties = allUncertainties + signal_uncertainty_ptG
    expected        = False
    cache_directory = default_cache_directory 
    corr_key        = "bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_correlationFitObject"
    data_key        = "bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_data"
    signal_key      = "bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_total"
    uncertaintyUp_key = {u:"bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_%s_Up"%u for u in uncertainties if "2016" in u or ( not "2017" in u and not "2018" in u )}
    mcStatUp_key      = "bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_MCStat_Up"

    cache_dir       = os.path.join(cache_directory, "unfolding", "2016", "bkgSubstracted", "expected" if expected else "observed", "postFit", "noFreeze")
    dirDB           = MergingDirDB(cache_dir)

    data            = dirDB.get( data_key )
    signal          = dirDB.get( signal_key )

    corrFitObj      = dirDB.get( corr_key )
    signal_frozen   = dirDB.get( signal_key )
    uncertainties   = {}
    for u, k in uncertaintyUp_key.iteritems():
        uncertainties[u] = add_error_from_Upvariation( dirDB.get( k ), signal_frozen )
    mcStat        = add_error_from_Upvariation( dirDB.get( mcStatUp_key ), signal_frozen )

    years           = ["2016"]

    covZRange = (0.00099,750)
    reco_variable   = "PhotonGood0_pt"
    reco_selection  = "SR3p"
    
    reco_thresholds = thresholds_from_histo( data )

    # events not in the reco region are filled with this value
    reco_variable_underflow = -1

    fiducial_variable   = "GenPhotonCMSUnfold0_pt"
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds     = [20, 35, 50, 80, 120, 160, 200, 280, 360] 

    fiducial_overflow       = "upper"
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    # appending reco thresholds for multiple years
    reco_overflow        = "upper"
    max_reco_val         = reco_thresholds[-1]
    min_reco_val         = reco_thresholds[0]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    reco_thresholds_years = copy.deepcopy(reco_thresholds)

    tex_reco = "p^{reco}_{T}(#gamma) [GeV]"
    tex_gen  = "p^{gen}_{T}(#gamma) [GeV]"
    tex_unf  = "p^{fid.}_{T}(#gamma) [GeV]"
    tex_pur  = "p_{T}(#gamma) [GeV]"
    texY     = 'Fiducial cross section [fb]'    
    y_range         = (.7, "auto") #(0.9, 9000)
    y_range_ratio   = (0.19,1.81)
    data_legendText = "Data (36/fb)"
    signal_legendText = "Observation"

    lumi_factor               = lumi_year[2016]/1000.
    unfolding_data_input      = replace_data_error( data )
    unfolding_data_input_systematic_bands          = [
        ]
    unfolding_signal_input        = replace_data_error( data )
    unfolding_signal_input_systematic_bands          = [
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(signal, +1, ref = data),
        'down':add_sigmas(signal, -1, ref = data),
        'color':ROOT.kOrange-9,
        },
        ]
    unfolding_signal_input_systematics          = [
       {'name' : u,
        'label': "\pm 1\sigma (%s)"%u,
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(h, +1, ref = data),
        'down':add_sigmas(h, -1, ref = data),
        'color':ROOT.kOrange-9,
        } for u, h in uncertainties.iteritems()
        ]
    unfolding_signal_input_MCStat          = {
        'name' : "MCStat",
        'label': "\pm 1\sigma (MC stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(mcStat, +1, ref = data),
        'down':add_sigmas(mcStat, -1, ref = data),
        'color':ROOT.kOrange-9,
        }
    unfolding_data_input_systematic        = {
        'name' : "data",
        'label': "\pm 1\sigma",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue-10,
        }



class observed_ptG_2017:
#  if False:
    uncertainties = allUncertainties + signal_uncertainty_ptG
    expected        = False
    cache_directory = default_cache_directory 
    corr_key        = "bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_correlationFitObject"
    data_key        = "bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_data"
    signal_key      = "bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_total"
    uncertaintyUp_key = {u:"bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_%s_Up"%u for u in uncertainties if "2017" in u or ( not "2016" in u and not "2018" in u )}
    mcStatUp_key      = "bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_MCStat_Up"

    cache_dir       = os.path.join(cache_directory, "unfolding", "2017", "bkgSubstracted", "expected" if expected else "observed", "postFit", "noFreeze")
    dirDB           = MergingDirDB(cache_dir)

    data            = dirDB.get( data_key )
    signal          = dirDB.get( signal_key )

    corrFitObj      = dirDB.get( corr_key )
    signal_frozen   = dirDB.get( signal_key )
    uncertainties   = {}
    for u, k in uncertaintyUp_key.iteritems():
        uncertainties[u] = add_error_from_Upvariation( dirDB.get( k ), signal_frozen )
    mcStat          = add_error_from_Upvariation( dirDB.get( mcStatUp_key ), signal_frozen )

    years           = ["2017"]

    covZRange = (0.00099,750)
    reco_variable   = "PhotonGood0_pt"
    reco_selection  = "SR3p"
    
    reco_thresholds = thresholds_from_histo( data )

    # events not in the reco region are filled with this value
    reco_variable_underflow = -1

    fiducial_variable   = "GenPhotonCMSUnfold0_pt"
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds     = [20, 35, 50, 80, 120, 160, 200, 280, 360] 

    fiducial_overflow       = "upper"
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    # appending reco thresholds for multiple years
    reco_overflow        = "upper"
    max_reco_val         = reco_thresholds[-1]
    min_reco_val         = reco_thresholds[0]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    reco_thresholds_years = copy.deepcopy(reco_thresholds)

    tex_reco = "p^{reco}_{T}(#gamma) [GeV]"
    tex_gen  = "p^{gen}_{T}(#gamma) [GeV]"
    tex_unf  = "p^{fid.}_{T}(#gamma) [GeV]"
    tex_pur  = "p_{T}(#gamma) [GeV]"
    texY     = 'Fiducial cross section [fb]'    
    y_range         = (.7, "auto") #(0.9, 9000)
    y_range_ratio   = (0.19,1.81)
    data_legendText = "Data (36/fb)"
    signal_legendText = "Observation"

    lumi_factor               = lumi_year[2017]/1000.
    unfolding_data_input      = replace_data_error( data )
    unfolding_data_input_systematic_bands          = [
        ]
    unfolding_signal_input        = replace_data_error( data )
    unfolding_signal_input_systematic_bands          = [
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(signal, +1, ref = data),
        'down':add_sigmas(signal, -1, ref = data),
        'color':ROOT.kOrange-9,
        },
        ]
    unfolding_signal_input_systematics          = [
       {'name' : u,
        'label': "\pm 1\sigma (%s)"%u,
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(h, +1, ref = data),
        'down':add_sigmas(h, -1, ref = data),
        'color':ROOT.kOrange-9,
        } for u, h in uncertainties.iteritems()
        ]
    unfolding_signal_input_MCStat          = {
        'name' : "MCStat",
        'label': "\pm 1\sigma (MC stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(mcStat, +1, ref = data),
        'down':add_sigmas(mcStat, -1, ref = data),
        'color':ROOT.kOrange-9,
        }
    unfolding_data_input_systematic        = {
        'name' : "data",
        'label': "\pm 1\sigma",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue-10,
        }


class observed_ptG_2018:
#  if False:
    uncertainties = allUncertainties + signal_uncertainty_ptG
    expected        = False
    cache_directory = default_cache_directory 
    corr_key        = "bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_correlationFitObject"
    data_key        = "bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_data"
    signal_key      = "bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_total"
    uncertaintyUp_key = {u:"bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_%s_Up"%u for u in uncertainties if not "L1_Prefiring" in u and ("2018" in u or ( not "2017" in u and not "2016" in u ))}
    mcStatUp_key      = "bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_MCStat_Up"

    cache_dir       = os.path.join(cache_directory, "unfolding", "2018", "bkgSubstracted", "expected" if expected else "observed", "postFit", "noFreeze")
    dirDB           = MergingDirDB(cache_dir)

    data            = dirDB.get( data_key )
    signal          = dirDB.get( signal_key )

    corrFitObj      = dirDB.get( corr_key )
    signal_frozen   = dirDB.get( signal_key )
    uncertainties   = {}
    for u, k in uncertaintyUp_key.iteritems():
        uncertainties[u] = add_error_from_Upvariation( dirDB.get( k ), signal_frozen )
    mcStat          = add_error_from_Upvariation( dirDB.get( mcStatUp_key ), signal_frozen )

    years           = ["2018"]

    covZRange = (0.00099,750)
    reco_variable   = "PhotonGood0_pt"
    reco_selection  = "SR3p"
    
    reco_thresholds = thresholds_from_histo( data )

    # events not in the reco region are filled with this value
    reco_variable_underflow = -1

    fiducial_variable   = "GenPhotonCMSUnfold0_pt"
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds     = [20, 35, 50, 80, 120, 160, 200, 280, 360] 

    fiducial_overflow       = "upper"
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    # appending reco thresholds for multiple years
    reco_overflow        = "upper"
    max_reco_val         = reco_thresholds[-1]
    min_reco_val         = reco_thresholds[0]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    reco_thresholds_years = copy.deepcopy(reco_thresholds)

    tex_reco = "p^{reco}_{T}(#gamma) [GeV]"
    tex_gen  = "p^{gen}_{T}(#gamma) [GeV]"
    tex_unf  = "p^{fid.}_{T}(#gamma) [GeV]"
    tex_pur  = "p_{T}(#gamma) [GeV]"
    texY     = 'Fiducial cross section [fb]'    
    y_range         = (.7, "auto") #(0.9, 9000)
    y_range_ratio   = (0.19,1.81)
    data_legendText = "Data (36/fb)"
    signal_legendText = "Observation"

    lumi_factor               = lumi_year[2018]/1000.
    unfolding_data_input      = replace_data_error( data )
    unfolding_data_input_systematic_bands          = [
        ]
    unfolding_signal_input        = replace_data_error( data )
    unfolding_signal_input_systematic_bands          = [
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(signal, +1, ref = data),
        'down':add_sigmas(signal, -1, ref = data),
        'color':ROOT.kOrange-9,
        },
        ]
    unfolding_signal_input_systematics          = [
       {'name' : u,
        'label': "\pm 1\sigma (%s)"%u,
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(h, +1, ref = data),
        'down':add_sigmas(h, -1, ref = data),
        'color':ROOT.kOrange-9,
        } for u, h in uncertainties.iteritems()
        ]
    unfolding_signal_input_MCStat          = {
        'name' : "MCStat",
        'label': "\pm 1\sigma (MC stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(mcStat, +1, ref = data),
        'down':add_sigmas(mcStat, -1, ref = data),
        'color':ROOT.kOrange-9,
        }
    unfolding_data_input_systematic        = {
        'name' : "data",
        'label': "\pm 1\sigma",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue-10,
        }



class expected_ptG_RunII:
  if False:
    uncertainties = allUncertainties + signal_uncertainty_ptG
    cache_directory = default_cache_directory 
    corr_key        = "bkgSubtracted_SR3pPtUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_correlationFitObject"
    data_key        = "bkgSubtracted_SR3pPtUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_data_%s"
    signal_key      = "bkgSubtracted_SR3pPtUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_total_%s"
    uncertaintyUp_key = {u:"bkgSubtracted_SR3pPtUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_%s_Up"%u for u in uncertainties}
    mcStatUp_key      = "bkgSubtracted_SR3pPtUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_MCStat_Up_%s"

    cache_dir       = os.path.join(cache_directory, "unfolding", "combined", "bkgSubstracted", "expected", "postFit", "noFreeze")
    dirDB           = MergingDirDB(cache_dir)

    years           = ["2016", "2017", "2018"]

    data_histos     =  [ dirDB.get( data_key%year ) for year in years ]
    signal_histos   =  [ dirDB.get( signal_key%year ) for year in years ]

    corrFitObj      = dirDB.get( corr_key )
    signal_frozen_histos   =  [ dirDB.get( signal_key%year ) for year in years ]
    uncertainties_histos   = {}
    for u, k in uncertaintyUp_key.iteritems():
        uncertainties_histos[u] = [add_error_from_Upvariation( dirDB.get( k+"_"+year ), signal_frozen_histos[i] ) for i,year in enumerate(years)]
    mcStatUp_histos   =  [ add_error_from_Upvariation( dirDB.get( mcStatUp_key%year ), signal_frozen_histos[i] ) for i,year in enumerate(years) ]

    covZRange = (0.00099,750)
    reco_variable   = "PhotonGood0_pt"
    reco_selection  = "SR3p"
    
    assert len(set( map( thresholds_from_histo, data_histos)))==1, "Not all data histos have the same x-axis binning!"
    assert len(set( map( thresholds_from_histo, signal_histos)))==1, "Not all signal histos have the same x-axis binning!"

    reco_thresholds = thresholds_from_histo( data_histos[0] )

    # appending reco thresholds for multiple years
    reco_overflow        = "upper"
    max_reco_val         = reco_thresholds[-1]
    min_reco_val         = reco_thresholds[0]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    # events not in the reco region are filled with this value
    reco_variable_underflow = -1

    # make reco_thresholds for all years
    reco_thresholds_years = list(copy.deepcopy(reco_thresholds))
    for i_year in range(1, len(years)):
        reco_thresholds_years +=  [ x + (max_reco_val-min_reco_val)*i_year for x in reco_thresholds[1:] ]

    data        = merge_x( data_histos, reco_thresholds_years )
    signal      = merge_x( signal_histos, reco_thresholds_years )
    mcStat      = merge_x( mcStatUp_histos, reco_thresholds_years )
    uncertainties   = {}
    for u, histlist in uncertainties_histos.iteritems():
        uncertainties[u] = merge_x( histlist, reco_thresholds_years )

    fiducial_variable   = "GenPhotonCMSUnfold0_pt"
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds     = [20, 35, 50, 80, 120, 160, 200, 280, 360]

    fiducial_overflow       = "upper"
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    tex_reco = "p^{reco}_{T}(#gamma) [GeV]"
    tex_gen  = "p^{gen}_{T}(#gamma) [GeV]"
    tex_unf  = "p^{fid.}_{T}(#gamma) [GeV]"
    tex_pur  = "p_{T}(#gamma) [GeV]"
    texY     = 'Fiducial cross section [fb]'    
    y_range         = (9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.39,1.61)
    data_legendText = "Data (137/fb)"
    signal_legendText = "Observation"

    lumi_factor               = (lumi_year[2016]+lumi_year[2017]+lumi_year[2018])/1000.
    unfolding_data_input      = replace_data_error( data )
    unfolding_data_input_systematic_bands          = [
        ]

    unfolding_signal_input        = replace_data_error( data )
    unfolding_signal_input_systematic_bands          = [
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(signal, +1, ref = data),
        'down':add_sigmas(signal, -1, ref = data),
        'color':ROOT.kOrange-9,
        },
        ]
    unfolding_signal_input_systematics          = [
       {'name' : u,
        'label': "\pm 1\sigma (%s)"%u,
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(h, +1, ref = data),
        'down':add_sigmas(h, -1, ref = data),
        'color':ROOT.kOrange-9,
        } for u, h in uncertainties.iteritems()
        ]
    unfolding_signal_input_MCStat          = {
        'name' : "MCStat",
        'label': "\pm 1\sigma (MC stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(mcStat, +1, ref = data),
        'down':add_sigmas(mcStat, -1, ref = data),
        'color':ROOT.kOrange-9,
        }
    unfolding_data_input_systematic        = {
        'name' : "data",
        'label': "\pm 1\sigma",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue-10,
        }



class observed_ptG_RunII:
#  if False:
    uncertainties = allUncertainties + signal_uncertainty_ptG
    cache_directory = default_cache_directory 
    corr_key        = "bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_correlationFitObject"
    data_key        = "bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_data_%s"
    signal_key      = "bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_total_%s"
    uncertaintyUp_key = {u:"bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_%s_Up"%u for u in uncertainties}
    mcStatUp_key      = "bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_MCStat_Up_%s"

    years           = ["2016", "2017", "2018"]

    cache_dir       = os.path.join(cache_directory, "unfolding", "combined", "bkgSubstracted", "observed", "postFit", "noFreeze")
    dirDB           = MergingDirDB(cache_dir)
    data_histos     =  [ dirDB.get( data_key%year ) for year in years ]
    signal_histos   =  [ dirDB.get( signal_key%year ) for year in years ]

    dirDB           = MergingDirDB(cache_dir)
    corrFitObj      =  dirDB.get( corr_key )

    signal_frozen_histos  =  [ dirDB.get( signal_key%year ) for year in years ]
    uncertainties_histos   = {}
    for u, k in uncertaintyUp_key.iteritems():
        uncertainties_histos[u] = [add_error_from_Upvariation( dirDB.get( k+"_"+year ), signal_frozen_histos[i] ) for i,year in enumerate(years)]
    mcStatUp_histos   =  [ add_error_from_Upvariation( dirDB.get( mcStatUp_key%year ), signal_frozen_histos[i] ) for i,year in enumerate(years) ]

    uncertaintyStatUp_key = {u:"bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_%s_Up"%u for u in signal_uncertainty_ptG + ["r"]}
    cache_dir       = os.path.join(cache_directory, "unfolding", "combined", "bkgSubstracted", "observed", "postFit", "freezeSyst")
    dirDB           = MergingDirDB(cache_dir)
    corrFitObjStat  =  dirDB.get( corr_key )
    signalStat_frozen_histos  =  [ dirDB.get( signal_key%year ) for year in years ]
    uncertaintiesStat_histos   = {}
    for u, k in uncertaintyStatUp_key.iteritems():
        uncertaintiesStat_histos[u] = [add_error_from_Upvariation( dirDB.get( k+"_"+year ), signalStat_frozen_histos[i] ) for i,year in enumerate(years)]
    mcStatStatUp_histos   =  [ add_error_from_Upvariation( dirDB.get( mcStatUp_key%year ), signalStat_frozen_histos[i] ) for i,year in enumerate(years) ]


    covZRange = (0.00099,750)
    reco_variable   = "PhotonGood0_pt"
    reco_selection  = "SR3p"

    assert len(set( map( thresholds_from_histo, data_histos)))==1, "Not all data histos have the same x-axis binning!"
    assert len(set( map( thresholds_from_histo, signal_histos)))==1, "Not all signal histos have the same x-axis binning!"

    reco_thresholds = thresholds_from_histo( data_histos[0] )

    # appending reco thresholds for multiple years
    reco_overflow        = "upper"
    max_reco_val         = reco_thresholds[-1]
    min_reco_val         = reco_thresholds[0]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    # events not in the reco region are filled with this value
    reco_variable_underflow = -1

    # make reco_thresholds for all years
    reco_thresholds_years = list(copy.deepcopy(reco_thresholds))
    for i_year in range(1, len(years)):
        reco_thresholds_years +=  [ x + (max_reco_val-min_reco_val)*i_year for x in reco_thresholds[1:] ]

    data        = merge_x( data_histos, reco_thresholds_years )
    signal      = merge_x( signal_histos, reco_thresholds_years )
    mcStat      = merge_x( mcStatUp_histos, reco_thresholds_years )
    mcStatStat  = merge_x( mcStatStatUp_histos, reco_thresholds_years )

    uncertainties   = {}
    for u, histlist in uncertainties_histos.iteritems():
        uncertainties[u] =  merge_x( histlist, reco_thresholds_years )

    uncertaintiesStat   = {}
    for u, histlist in uncertaintiesStat_histos.iteritems():
        uncertaintiesStat[u] =  merge_x( histlist, reco_thresholds_years )

    fiducial_variable   = "GenPhotonCMSUnfold0_pt"
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds     = [20, 35, 50, 80, 120, 160, 200, 280, 360]

    fiducial_overflow       = "upper"
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    tex_reco = "p^{reco}_{T}(#gamma) [GeV]"
    tex_gen  = "p^{gen}_{T}(#gamma) [GeV]"
    tex_unf  = "p^{fid.}_{T}(#gamma) [GeV]"
    tex_pur  = "p_{T}(#gamma) [GeV]"
    texY     = 'Fiducial cross section [fb]'
    y_range         = (.7, "auto") #(0.9, 9000)
    y_range_ratio   = (0.69,1.31)
    data_legendText = "Data (137/fb)"
    signal_legendText = "Observation"

    lumi_factor               = (lumi_year[2016]+lumi_year[2017]+lumi_year[2018])/1000.
    unfolding_data_input      = replace_data_error( data )
    unfolding_signal_input        = replace_data_error( data )

    unfolding_data_input_systematic_bands          = [
        ]

    unfolding_signal_input_systematic_bands          = [
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'matrix': "nominal",
        'ref':  replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'matrix': "nominal",
        'ref':  replace_data_error( data ),
        'up':  add_sigmas(signal, +1, ref = data),
        'down':add_sigmas(signal, -1, ref = data),
        'color':ROOT.kOrange-9,
        },
        ]
    unfolding_signal_input_systematics          = [
       {'name' : u,
        'label': "\pm 1\sigma (%s)"%u,
        'matrix': "nominal",
        'ref':  replace_data_error( data ),
        'up':  add_sigmas(h, +1, ref = data),
        'down':add_sigmas(h, -1, ref = data),
        'color':ROOT.kOrange-9,
        } for u, h in uncertainties.iteritems()
        ]
    unfolding_signal_input_MCStat          = {
        'name' : "MCStat",
        'label': "\pm 1\sigma (MC stat.)",
        'matrix': "nominal",
        'ref':  replace_data_error( data ),
        'up':  add_sigmas(mcStat, +1, ref = data),
        'down':add_sigmas(mcStat, -1, ref = data),
        'color':ROOT.kOrange-9,
        }
    unfolding_data_input_systematic        = {
        'name' : "data",
        'label': "\pm 1\sigma",
        'matrix': "nominal",
        'ref':  replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue-10,
        }
    unfolding_signalStat_input_systematics          = [
       {'name' : u,
        'label': "\pm 1\sigma (%s)"%u,
        'matrix': "nominal",
        'ref':  replace_data_error( data ),
        'up':  add_sigmas(h, +1, ref = data),
        'down':add_sigmas(h, -1, ref = data),
        'color':ROOT.kOrange-9,
        } for u, h in uncertaintiesStat.iteritems()
        ]
    unfolding_signalStat_input_MCStat          = {
        'name' : "MCStat",
        'label': "\pm 1\sigma (MC stat.)",
        'matrix': "nominal",
        'ref':  replace_data_error( data ),
        'up':  add_sigmas(mcStatStat, +1, ref = data),
        'down':add_sigmas(mcStatStat, -1, ref = data),
        'color':ROOT.kOrange-9,
        }


class expected_absEta_RunII:
  if False:
    uncertainties = allUncertainties + signal_uncertainty_absEta
    expected        = True
    cache_directory = default_cache_directory 
    corr_key        = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_correlationFitObject"
    data_key        = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_data_%s"
    signal_key      = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_total_%s"
    uncertaintyUp_key = {u:"bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_%s_Up"%u for u in uncertainties}
    mcStatUp_key      = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_MCStat_Up_%s"

    cache_dir       = os.path.join(cache_directory, "unfolding", "combined", "bkgSubstracted", "expected" if expected else "observed", "postFit", "noFreeze")
    dirDB           = MergingDirDB(cache_dir)

    years           = ["2016", "2017", "2018"]

    data_histos     =  [ dirDB.get( data_key%year ) for year in years ]
    signal_histos   =  [ dirDB.get( signal_key%year ) for year in years ]

    corrFitObj      = dirDB.get( corr_key )
    signal_frozen_histos   =  [ dirDB.get( signal_key%year ) for year in years ] 
    uncertainties_histos   = {}
    for u, k in uncertaintyUp_key.iteritems():
        uncertainties_histos[u] = [add_error_from_Upvariation( dirDB.get( k+"_"+year ), signal_frozen_histos[i] ) for i,year in enumerate(years)]
    mcStatUp_histos   =  [ add_error_from_Upvariation( dirDB.get( mcStatUp_key%year ), signal_frozen_histos[i] ) for i,year in enumerate(years) ] 

    covZRange = (0.099,161)
    reco_variable   = { "absEta_reco":"abs(PhotonGood0_eta)"}
    reco_selection  = "SR3p"

    assert len(set( map( thresholds_from_histo, data_histos)))==1, "Not all data histos have the same x-axis binning!"
    assert len(set( map( thresholds_from_histo, signal_histos)))==1, "Not all signal histos have the same x-axis binning!"

    reco_thresholds = thresholds_from_histo( data_histos[0] )
    # appending reco thresholds for multiple years
    reco_overflow        = None
    max_reco_val         = reco_thresholds[-1]
    min_reco_val         = reco_thresholds[0]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    # events not in the reco region are filled with this value
    reco_variable_underflow = reco_thresholds[0]-0.5

    # make reco_thresholds for all years
    reco_thresholds_years = list(copy.deepcopy(reco_thresholds))
    for i_year in range(1, len(years)):
        reco_thresholds_years +=  [ x + (max_reco_val-min_reco_val)*i_year for x in reco_thresholds[1:] ]

    data        = merge_x( data_histos, reco_thresholds_years )
    signal      = merge_x( signal_histos, reco_thresholds_years )
    mcStat      = merge_x( mcStatUp_histos, reco_thresholds_years )
    uncertainties   = {}
    for u, histlist in uncertainties_histos.iteritems():
        uncertainties[u] = merge_x( histlist, reco_thresholds_years )

    fiducial_variable   = {"absEta_fid":"abs(GenPhotonCMSUnfold0_eta)"}
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds = [0, 0.3, 0.6, 0.9, 1.2, 1.45]
    fiducial_overflow       = None

    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    tex_reco = "|#eta^{reco}(#gamma)|"
    tex_gen  = "|#eta^{gen}(#gamma)|"
    tex_unf  = "|#eta^{fid.}(#gamma)|"
    tex_pur  = "|#eta(#gamma)|"
    texY     = 'Fiducial cross section [fb]'    
    y_range         = (0.9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.39,1.61)
    data_legendText = "Data (137/fb)"
    signal_legendText = "Observation"

    lumi_factor               = (lumi_year[2016]+lumi_year[2017]+lumi_year[2018])/1000.
    unfolding_data_input      = replace_data_error( data )
    unfolding_data_input_systematic_bands          = [
        ]
    unfolding_signal_input        = replace_data_error( data )
    unfolding_signal_input_systematic_bands          = [
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(signal, +1, ref = data),
        'down':add_sigmas(signal, -1, ref = data),
        'color':ROOT.kOrange-9,
        },
        ]
    unfolding_signal_input_systematics          = [
       {'name' : u,
        'label': "\pm 1\sigma (%s)"%u,
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(h, +1, ref = data),
        'down':add_sigmas(h, -1, ref = data),
        'color':ROOT.kOrange-9,
        } for u, h in uncertainties.iteritems()
        ]
    unfolding_signal_input_MCStat          = {
        'name' : "MCStat",
        'label': "\pm 1\sigma (MC stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(mcStat, +1, ref = data),
        'down':add_sigmas(mcStat, -1, ref = data),
        'color':ROOT.kOrange-9,
        }
    unfolding_data_input_systematic        = {
        'name' : "data",
        'label': "\pm 1\sigma",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue-10,
        }



class observed_absEta_RunII:
#  if False:
    uncertainties = allUncertainties + signal_uncertainty_absEta
    expected        = False
    cache_directory = default_cache_directory 
    corr_key        = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_correlationFitObject"
    data_key        = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_data_%s"
    signal_key      = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_total_%s"
    uncertaintyUp_key = {u:"bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_%s_Up"%u for u in uncertainties}
    mcStatUp_key      = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_MCStat_Up_%s"

    cache_dir       = os.path.join(cache_directory, "unfolding", "combined", "bkgSubstracted", "expected" if expected else "observed", "postFit", "noFreeze")
    dirDB           = MergingDirDB(cache_dir)

    years           = ["2016", "2017", "2018"]

    data_histos     =  [ dirDB.get( data_key%year ) for year in years ]
    signal_histos   =  [ dirDB.get( signal_key%year ) for year in years ]

    corrFitObj      = dirDB.get( corr_key )
    signal_frozen_histos   =  [ dirDB.get( signal_key%year ) for year in years ] 
    uncertainties_histos   = {}
    for u, k in uncertaintyUp_key.iteritems():
        uncertainties_histos[u] = [add_error_from_Upvariation( dirDB.get( k+"_"+year ), signal_frozen_histos[i] ) for i,year in enumerate(years)]
    mcStatUp_histos   =  [ add_error_from_Upvariation( dirDB.get( mcStatUp_key%year ), signal_frozen_histos[i] ) for i,year in enumerate(years) ] 

    uncertaintyStatUp_key = {u:"bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_%s_Up"%u for u in signal_uncertainty_absEta + ["r"]}
    cache_dir       = os.path.join(cache_directory, "unfolding", "combined", "bkgSubstracted", "observed", "postFit", "freezeSyst")
    dirDB           = MergingDirDB(cache_dir)
    corrFitObjStat  =  dirDB.get( corr_key )
    signalStat_frozen_histos  =  [ dirDB.get( signal_key%year ) for year in years ]
    uncertaintiesStat_histos   = {}
    for u, k in uncertaintyStatUp_key.iteritems():
        uncertaintiesStat_histos[u] = [add_error_from_Upvariation( dirDB.get( k+"_"+year ), signalStat_frozen_histos[i] ) for i,year in enumerate(years)]
    mcStatStatUp_histos   =  [ add_error_from_Upvariation( dirDB.get( mcStatUp_key%year ), signalStat_frozen_histos[i] ) for i,year in enumerate(years) ]


    reco_variable   = { "absEta_reco":"abs(PhotonGood0_eta)"}
    reco_selection  = "SR3p"

    assert len(set( map( thresholds_from_histo, data_histos)))==1, "Not all data histos have the same x-axis binning!"
    assert len(set( map( thresholds_from_histo, signal_histos)))==1, "Not all signal histos have the same x-axis binning!"

    reco_thresholds = thresholds_from_histo( data_histos[0] )
    # appending reco thresholds for multiple years
    reco_overflow        = None
    max_reco_val         = reco_thresholds[-1]
    min_reco_val         = reco_thresholds[0]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    # events not in the reco region are filled with this value
    covZRange = (0.099,161)
    reco_variable_underflow = reco_thresholds[0]-0.5

    # make reco_thresholds for all years
    reco_thresholds_years = list(copy.deepcopy(reco_thresholds))
    for i_year in range(1, len(years)):
        reco_thresholds_years +=  [ x + (max_reco_val-min_reco_val)*i_year for x in reco_thresholds[1:] ]

    data        = merge_x( data_histos, reco_thresholds_years )
    signal      = merge_x( signal_histos, reco_thresholds_years )
    mcStat      = merge_x( mcStatUp_histos, reco_thresholds_years )
    uncertainties   = {}
    for u, histlist in uncertainties_histos.iteritems():
        uncertainties[u] = merge_x( histlist, reco_thresholds_years )

    uncertaintiesStat   = {}
    for u, histlist in uncertaintiesStat_histos.iteritems():
        uncertaintiesStat[u] =  merge_x( histlist, reco_thresholds_years )
    mcStatStat      = merge_x( mcStatStatUp_histos, reco_thresholds_years )


    fiducial_variable   = {"absEta_fid":"abs(GenPhotonCMSUnfold0_eta)"}
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds = [0, 0.3, 0.6, 0.9, 1.2, 1.45]
    fiducial_overflow       = None

    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    tex_reco = "|#eta^{reco}(#gamma)|"
    tex_gen  = "|#eta^{gen}(#gamma)|"
    tex_unf  = "|#eta^{fid.}(#gamma)|"
    tex_pur  = "|#eta(#gamma)|"
    texY     = 'Fiducial cross section [fb]'    
    y_range         = (0.9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.84, 1.16)
    data_legendText = "Data (137/fb)"
    signal_legendText = "Observation"

    lumi_factor               = (lumi_year[2016]+lumi_year[2017]+lumi_year[2018])/1000.
    unfolding_data_input      = replace_data_error( data )
    unfolding_data_input_systematic_bands          = [
        ]

    unfolding_signal_input        = replace_data_error( data )
    unfolding_signal_input_systematic_bands          = [
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(signal, +1, ref = data),
        'down':add_sigmas(signal, -1, ref = data),
        'color':ROOT.kOrange-9,
        },
        ]
    unfolding_signal_input_systematics          = [
       {'name' : u,
        'label': "\pm 1\sigma (%s)"%u,
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(h, +1, ref = data),
        'down':add_sigmas(h, -1, ref = data),
        'color':ROOT.kOrange-9,
        } for u, h in uncertainties.iteritems()
        ]
    unfolding_signal_input_MCStat          = {
        'name' : "MCStat",
        'label': "\pm 1\sigma (MC stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(mcStat, +1, ref = data),
        'down':add_sigmas(mcStat, -1, ref = data),
        'color':ROOT.kOrange-9,
        }
    unfolding_data_input_systematic        = {
        'name' : "data",
        'label': "\pm 1\sigma",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue-10,
        }
    unfolding_signalStat_input_systematics          = [
       {'name' : u,
        'label': "\pm 1\sigma (%s)"%u,
        'matrix': "nominal",
        'ref':  replace_data_error( data ),
        'up':  add_sigmas(h, +1, ref = data),
        'down':add_sigmas(h, -1, ref = data),
        'color':ROOT.kOrange-9,
        } for u, h in uncertaintiesStat.iteritems()
        ]
    unfolding_signalStat_input_MCStat          = {
        'name' : "MCStat",
        'label': "\pm 1\sigma (MC stat.)",
        'matrix': "nominal",
        'ref':  replace_data_error( data ),
        'up':  add_sigmas(mcStatStat, +1, ref = data),
        'down':add_sigmas(mcStatStat, -1, ref = data),
        'color':ROOT.kOrange-9,
        }


class observed_absEta_2016:
#  if False:
    uncertainties = allUncertainties + signal_uncertainty_absEta
    expected        = False
    cache_directory = default_cache_directory 
    corr_key        = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_correlationFitObject"
    data_key        = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_data"
    signal_key      = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_total"
    uncertaintyUp_key = {u:"bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_%s_Up"%u for u in uncertainties if "2016" in u or ( not "2017" in u and not "2018" in u )}
    mcStatUp_key      = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_MCStat_Up"

    cache_dir       = os.path.join(cache_directory, "unfolding", "2016", "bkgSubstracted", "expected" if expected else "observed", "postFit", "noFreeze")
    dirDB           = MergingDirDB(cache_dir)

    data            = dirDB.get( data_key )
    signal          = dirDB.get( signal_key )

    corrFitObj      = dirDB.get( corr_key )
    signal_frozen   = dirDB.get( signal_key )
    uncertainties   = {}
    for u, k in uncertaintyUp_key.iteritems():
        uncertainties[u] = add_error_from_Upvariation( dirDB.get( k ), signal_frozen )
    mcStat          = add_error_from_Upvariation( dirDB.get( mcStatUp_key ), signal_frozen )

    years           = ["2016"]

    covZRange = (0.099,161)
    reco_variable   = { "absEta_reco":"abs(PhotonGood0_eta)"}
    reco_selection  = "SR3p"
    
    reco_thresholds = thresholds_from_histo( data )

    # events not in the reco region are filled with this value
    reco_variable_underflow = -1

    fiducial_variable   = {"absEta_fid":"abs(GenPhotonCMSUnfold0_eta)"}
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds = [0, 0.3, 0.6, 0.9, 1.2, 1.45]
    
    fiducial_overflow       = None
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    # appending reco thresholds for multiple years
    reco_overflow        = None
    max_reco_val         = reco_thresholds[-1]
    min_reco_val         = reco_thresholds[0]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    reco_thresholds_years = copy.deepcopy(reco_thresholds)

    tex_reco = "|#eta^{reco}(#gamma)|"
    tex_gen  = "|#eta^{gen}(#gamma)|"
    tex_unf  = "|#eta^{fid.}(#gamma)|"
    tex_pur  = "|#eta(#gamma)|"
    texY     = 'Fiducial cross section [fb]'    
    y_range         = (0.9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.69,1.31)
    data_legendText = "Data (36/fb)"
    signal_legendText = "Observation"

    lumi_factor               = lumi_year[2016]/1000.
    unfolding_data_input      = replace_data_error( data )
    unfolding_data_input_systematic_bands          = [
        ]
    unfolding_signal_input        = replace_data_error( data )
    unfolding_signal_input_systematic_bands          = [
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(signal, +1, ref = data),
        'down':add_sigmas(signal, -1, ref = data),
        'color':ROOT.kOrange-9,
        },
        ]
    unfolding_signal_input_systematics          = [
       {'name' : u,
        'label': "\pm 1\sigma (%s)"%u,
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(h, +1, ref = data),
        'down':add_sigmas(h, -1, ref = data),
        'color':ROOT.kOrange-9,
        } for u, h in uncertainties.iteritems()
        ]
    unfolding_signal_input_MCStat          = {
        'name' : "MCStat",
        'label': "\pm 1\sigma (MC stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(mcStat, +1, ref = data),
        'down':add_sigmas(mcStat, -1, ref = data),
        'color':ROOT.kOrange-9,
        }
    unfolding_data_input_systematic        = {
        'name' : "data",
        'label': "\pm 1\sigma",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue-10,
        }



class observed_absEta_2017:
#  if False:
    uncertainties = allUncertainties + signal_uncertainty_absEta
    expected        = False
    cache_directory = default_cache_directory 
    corr_key        = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_correlationFitObject"
    data_key        = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_data"
    signal_key      = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_total"
    uncertaintyUp_key = {u:"bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_%s_Up"%u for u in uncertainties if "2017" in u or ( not "2016" in u and not "2018" in u )}
    mcStatUp_key      = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_MCStat_Up"

    cache_dir       = os.path.join(cache_directory, "unfolding", "2017", "bkgSubstracted", "expected" if expected else "observed", "postFit", "noFreeze")
    dirDB           = MergingDirDB(cache_dir)

    data            = dirDB.get( data_key )
    signal          = dirDB.get( signal_key )

    corrFitObj      = dirDB.get( corr_key )
    signal_frozen   = dirDB.get( signal_key )
    uncertainties   = {}
    for u, k in uncertaintyUp_key.iteritems():
        uncertainties[u] = add_error_from_Upvariation( dirDB.get( k ), signal_frozen )
    mcStat          = add_error_from_Upvariation( dirDB.get( mcStatUp_key ), signal_frozen )

    years           = ["2017"]

    covZRange = (0.099,161)
    reco_variable   = { "absEta_reco":"abs(PhotonGood0_eta)"}
    reco_selection  = "SR3p"
    
    reco_thresholds = thresholds_from_histo( data )

    # events not in the reco region are filled with this value
    reco_variable_underflow = -1

    fiducial_variable   = {"absEta_fid":"abs(GenPhotonCMSUnfold0_eta)"}
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds = [0, 0.3, 0.6, 0.9, 1.2, 1.45]
    
    fiducial_overflow       = None
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    # appending reco thresholds for multiple years
    reco_overflow        = None
    max_reco_val         = reco_thresholds[-1]
    min_reco_val         = reco_thresholds[0]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    reco_thresholds_years = copy.deepcopy(reco_thresholds)

    tex_reco = "|#eta^{reco}(#gamma)|"
    tex_gen  = "|#eta^{gen}(#gamma)|"
    tex_unf  = "|#eta^{fid.}(#gamma)|"
    tex_pur  = "|#eta(#gamma)|"
    texY     = 'Fiducial cross section [fb]'    
    y_range         = (0.9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.69,1.31)
    data_legendText = "Data (36/fb)"
    signal_legendText = "Observation"

    lumi_factor               = lumi_year[2017]/1000.
    unfolding_data_input      = replace_data_error( data )
    unfolding_data_input_systematic_bands          = [
        ]
    unfolding_signal_input        = replace_data_error( data )
    unfolding_signal_input_systematic_bands          = [
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(signal, +1, ref = data),
        'down':add_sigmas(signal, -1, ref = data),
        'color':ROOT.kOrange-9,
        },
        ]
    unfolding_signal_input_systematics          = [
       {'name' : u,
        'label': "\pm 1\sigma (%s)"%u,
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(h, +1, ref = data),
        'down':add_sigmas(h, -1, ref = data),
        'color':ROOT.kOrange-9,
        } for u, h in uncertainties.iteritems()
        ]
    unfolding_signal_input_MCStat          = {
        'name' : "MCStat",
        'label': "\pm 1\sigma (MC stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(mcStat, +1, ref = data),
        'down':add_sigmas(mcStat, -1, ref = data),
        'color':ROOT.kOrange-9,
        }
    unfolding_data_input_systematic        = {
        'name' : "data",
        'label': "\pm 1\sigma",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue-10,
        }



class observed_absEta_2018:
#  if False:
    uncertainties = allUncertainties + signal_uncertainty_absEta
    expected        = False
    cache_directory = default_cache_directory 
    corr_key        = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_correlationFitObject"
    data_key        = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_data"
    signal_key      = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_total"
    uncertaintyUp_key = {u:"bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_%s_Up"%u for u in uncertainties if not "L1_Prefiring" in u and ("2018" in u or ( not "2017" in u and not "2016" in u ))}
    mcStatUp_key      = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_MCStat_Up"

    cache_dir       = os.path.join(cache_directory, "unfolding", "2018", "bkgSubstracted", "expected" if expected else "observed", "postFit", "noFreeze")
    dirDB           = MergingDirDB(cache_dir)

    data            = dirDB.get( data_key )
    signal          = dirDB.get( signal_key )

    corrFitObj      = dirDB.get( corr_key )
    signal_frozen   = dirDB.get( signal_key )
    uncertainties   = {}
    for u, k in uncertaintyUp_key.iteritems():
        uncertainties[u] = add_error_from_Upvariation( dirDB.get( k ), signal_frozen )
    mcStat          = add_error_from_Upvariation( dirDB.get( mcStatUp_key ), signal_frozen )

    years           = ["2018"]

    covZRange = (0.099,161)
    reco_variable   = { "absEta_reco":"abs(PhotonGood0_eta)"}
    reco_selection  = "SR3p"
    
    reco_thresholds = thresholds_from_histo( data )

    # events not in the reco region are filled with this value
    reco_variable_underflow = -1

    fiducial_variable   = {"absEta_fid":"abs(GenPhotonCMSUnfold0_eta)"}
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds = [0, 0.3, 0.6, 0.9, 1.2, 1.45]
    
    fiducial_overflow       = None
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    # appending reco thresholds for multiple years
    reco_overflow        = None
    max_reco_val         = reco_thresholds[-1]
    min_reco_val         = reco_thresholds[0]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    reco_thresholds_years = copy.deepcopy(reco_thresholds)

    tex_reco = "|#eta^{reco}(#gamma)|"
    tex_gen  = "|#eta^{gen}(#gamma)|"
    tex_unf  = "|#eta^{fid.}(#gamma)|"
    tex_pur  = "|#eta(#gamma)|"
    texY     = 'Fiducial cross section [fb]'    
    y_range         = (0.9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.69,1.31)
    data_legendText = "Data (36/fb)"
    signal_legendText = "Observation"

    lumi_factor               = lumi_year[2018]/1000.
    unfolding_data_input      = replace_data_error( data )
    unfolding_data_input_systematic_bands          = [
        ]
    unfolding_signal_input        = replace_data_error( data )
    unfolding_signal_input_systematic_bands          = [
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(signal, +1, ref = data),
        'down':add_sigmas(signal, -1, ref = data),
        'color':ROOT.kOrange-9,
        },
        ]
    unfolding_signal_input_systematics          = [
       {'name' : u,
        'label': "\pm 1\sigma (%s)"%u,
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(h, +1, ref = data),
        'down':add_sigmas(h, -1, ref = data),
        'color':ROOT.kOrange-9,
        } for u, h in uncertainties.iteritems()
        ]
    unfolding_signal_input_MCStat          = {
        'name' : "MCStat",
        'label': "\pm 1\sigma (MC stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(mcStat, +1, ref = data),
        'down':add_sigmas(mcStat, -1, ref = data),
        'color':ROOT.kOrange-9,
        }
    unfolding_data_input_systematic        = {
        'name' : "data",
        'label': "\pm 1\sigma",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue-10,
        }



class observed_dRlg_2016:
#  if False:
    uncertainties = allUncertainties + signal_uncertainty_dRlg
    expected        = False
    cache_directory = default_cache_directory 
    corr_key        = "bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_correlationFitObject"
    data_key        = "bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_data"
    signal_key      = "bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_total"
    uncertaintyUp_key = {u:"bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_%s_Up"%u for u in uncertainties if "2016" in u or ( not "2017" in u and not "2018" in u )}
    mcStatUp_key      = "bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_MCStat_Up"

    cache_dir       = os.path.join(cache_directory, "unfolding", "2016", "bkgSubstracted", "expected" if expected else "observed", "postFit", "noFreeze")
    dirDB           = MergingDirDB(cache_dir)

    data            = dirDB.get( data_key )
    signal          = dirDB.get( signal_key )

    corrFitObj      = dirDB.get( corr_key )
    signal_frozen   = dirDB.get( signal_key )
    uncertainties   = {}
    for u, k in uncertaintyUp_key.iteritems():
        uncertainties[u] = add_error_from_Upvariation( dirDB.get( k ), signal_frozen )
    mcStat          = add_error_from_Upvariation( dirDB.get( mcStatUp_key ), signal_frozen )

    years           = ["2016"]

    covZRange = (0.0099,191)
    reco_variable   = { "dRlg_reco":"sqrt((PhotonGood0_eta-LeptonTight0_eta)**2+acos(cos(PhotonGood0_phi-LeptonTight0_phi))**2)"}
    reco_selection  = "SR3p"
    
    reco_thresholds = thresholds_from_histo( data )

    # events not in the reco region are filled with this value
    reco_variable_underflow = -1

    fiducial_variable   = "genLCMStight0GammadR"
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds     = (0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.4)
    
    fiducial_overflow       = "upper"
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    # appending reco thresholds for multiple years
    reco_overflow        = "upper"
    max_reco_val         = reco_thresholds[-1]
    min_reco_val         = reco_thresholds[0]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    reco_thresholds_years = copy.deepcopy(reco_thresholds)

    tex_reco = "#Delta R(#gamma, l)^{reco}"
    tex_gen  = "#Delta R(#gamma, l)^{gen}"
    tex_unf  = "#Delta R(#gamma, l)^{fid.}"
    tex_pur  = "#Delta R(#gamma, l)"
    texY     = 'Fiducial cross section [fb]'    
    y_range         = (0.9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.69,1.31)
    data_legendText = "Data (36/fb)"
    signal_legendText =   "Observation"

    lumi_factor               = lumi_year[2016]/1000.
    unfolding_data_input      = replace_data_error( data )
    unfolding_data_input_systematic_bands          = [
        ]
    unfolding_signal_input        = replace_data_error( data )
    unfolding_signal_input_systematic_bands          = [
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(signal, +1, ref = data),
        'down':add_sigmas(signal, -1, ref = data),
        'color':ROOT.kOrange-9,
        },
        ]
    unfolding_signal_input_systematics          = [
       {'name' : u,
        'label': "\pm 1\sigma (%s)"%u,
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(h, +1, ref = data),
        'down':add_sigmas(h, -1, ref = data),
        'color':ROOT.kOrange-9,
        } for u, h in uncertainties.iteritems()
        ]
    unfolding_signal_input_MCStat          = {
        'name' : "MCStat",
        'label': "\pm 1\sigma (MC stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(mcStat, +1, ref = data),
        'down':add_sigmas(mcStat, -1, ref = data),
        'color':ROOT.kOrange-9,
        }
    unfolding_data_input_systematic        = {
        'name' : "data",
        'label': "\pm 1\sigma",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue-10,
        }


class observed_dRlg_2017:
#  if False:
    uncertainties = allUncertainties + signal_uncertainty_dRlg
    expected        = False
    cache_directory = default_cache_directory 
    corr_key        = "bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_correlationFitObject"
    data_key        = "bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_data"
    signal_key      = "bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_total"
    uncertaintyUp_key = {u:"bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_%s_Up"%u for u in uncertainties if "2017" in u or ( not "2016" in u and not "2018" in u )}
    mcStatUp_key      = "bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_MCStat_Up"

    cache_dir       = os.path.join(cache_directory, "unfolding", "2017", "bkgSubstracted", "expected" if expected else "observed", "postFit", "noFreeze")
    dirDB           = MergingDirDB(cache_dir)

    data            = dirDB.get( data_key )
    signal          = dirDB.get( signal_key )

    corrFitObj      = dirDB.get( corr_key )
    signal_frozen   = dirDB.get( signal_key )
    uncertainties   = {}
    for u, k in uncertaintyUp_key.iteritems():
        uncertainties[u] = add_error_from_Upvariation( dirDB.get( k ), signal_frozen )
    mcStat          = add_error_from_Upvariation( dirDB.get( mcStatUp_key ), signal_frozen )

    years           = ["2017"]

    reco_variable   = { "dRlg_reco":"sqrt((PhotonGood0_eta-LeptonTight0_eta)**2+acos(cos(PhotonGood0_phi-LeptonTight0_phi))**2)"}
    reco_selection  = "SR3p"
    
    reco_thresholds = thresholds_from_histo( data )

    # events not in the reco region are filled with this value
    reco_variable_underflow = -1

    fiducial_variable   = "genLCMStight0GammadR"
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds     = (0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.4)
    
    fiducial_overflow       = "upper"
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    # appending reco thresholds for multiple years
    covZRange = (0.0099,191)
    reco_overflow        = "upper"
    max_reco_val         = reco_thresholds[-1]
    min_reco_val         = reco_thresholds[0]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    reco_thresholds_years = copy.deepcopy(reco_thresholds)

    tex_reco = "#Delta R(#gamma, l)^{reco}"
    tex_gen  = "#Delta R(#gamma, l)^{gen}"
    tex_unf  = "#Delta R(#gamma, l)^{fid.}"
    tex_pur  = "#Delta R(#gamma, l)"
    texY     = 'Fiducial cross section [fb]'    
    y_range         = (0.9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.69,1.31)
    data_legendText = "Data (36/fb)"
    signal_legendText =   "Observation"

    lumi_factor               = lumi_year[2017]/1000.
    unfolding_data_input      = replace_data_error( data )
    unfolding_data_input_systematic_bands          = [
        ]
    unfolding_signal_input        = replace_data_error( data )
    unfolding_signal_input_systematic_bands          = [
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(signal, +1, ref = data),
        'down':add_sigmas(signal, -1, ref = data),
        'color':ROOT.kOrange-9,
        },
        ]
    unfolding_signal_input_systematics          = [
       {'name' : u,
        'label': "\pm 1\sigma (%s)"%u,
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(h, +1, ref = data),
        'down':add_sigmas(h, -1, ref = data),
        'color':ROOT.kOrange-9,
        } for u, h in uncertainties.iteritems()
        ]

    unfolding_signal_input_MCStat          = {
        'name' : "MCStat",
        'label': "\pm 1\sigma (MC stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(mcStat, +1, ref = data),
        'down':add_sigmas(mcStat, -1, ref = data),
        'color':ROOT.kOrange-9,
        }
    unfolding_data_input_systematic        = {
        'name' : "data",
        'label': "\pm 1\sigma",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue-10,
        }



class observed_dRlg_2018:
#  if False:
    uncertainties = allUncertainties + signal_uncertainty_dRlg
    expected        = False
    cache_directory = default_cache_directory 
    corr_key        = "bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_correlationFitObject"
    data_key        = "bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_data"
    signal_key      = "bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_total"
    uncertaintyUp_key = {u:"bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_%s_Up"%u for u in uncertainties if not "L1_Prefiring" in u and ("2018" in u or ( not "2017" in u and not "2016" in u ))}
    mcStatUp_key      = "bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_MCStat_Up"

    cache_dir       = os.path.join(cache_directory, "unfolding", "2018", "bkgSubstracted", "expected" if expected else "observed", "postFit", "noFreeze")
    dirDB           = MergingDirDB(cache_dir)

    data            = dirDB.get( data_key )
    signal          = dirDB.get( signal_key )

    corrFitObj      = dirDB.get( corr_key )
    signal_frozen   = dirDB.get( signal_key )
    uncertainties   = {}
    for u, k in uncertaintyUp_key.iteritems():
        uncertainties[u] = add_error_from_Upvariation( dirDB.get( k ), signal_frozen )
    mcStat          = add_error_from_Upvariation( dirDB.get( mcStatUp_key ), signal_frozen )

    years           = ["2018"]

    covZRange = (0.0099,191)
    reco_variable   = { "dRlg_reco":"sqrt((PhotonGood0_eta-LeptonTight0_eta)**2+acos(cos(PhotonGood0_phi-LeptonTight0_phi))**2)"}
    reco_selection  = "SR3p"
    
    reco_thresholds = thresholds_from_histo( data )

    # events not in the reco region are filled with this value
    reco_variable_underflow = -1

    fiducial_variable   = "genLCMStight0GammadR"
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds     = (0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.4)
    
    fiducial_overflow       = "upper"
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    # appending reco thresholds for multiple years
    reco_overflow        = "upper"
    max_reco_val         = reco_thresholds[-1]
    min_reco_val         = reco_thresholds[0]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    reco_thresholds_years = copy.deepcopy(reco_thresholds)

    tex_reco = "#Delta R(#gamma, l)^{reco}"
    tex_gen  = "#Delta R(#gamma, l)^{gen}"
    tex_unf  = "#Delta R(#gamma, l)^{fid.}"
    tex_pur  = "#Delta R(#gamma, l)"
    texY     = 'Fiducial cross section [fb]'    
    y_range         = (0.9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.69,1.31)
    data_legendText = "Data (36/fb)"
    signal_legendText =   "Observation"

    lumi_factor               = lumi_year[2018]/1000.
    unfolding_data_input      = replace_data_error( data )
    unfolding_data_input_systematic_bands          = [
        ]
    unfolding_signal_input        = replace_data_error( data )
    unfolding_signal_input_systematic_bands          = [
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(signal, +1, ref = data),
        'down':add_sigmas(signal, -1, ref = data),
        'color':ROOT.kOrange-9,
        },
        ]
    unfolding_signal_input_systematics          = [
       {'name' : u,
        'label': "\pm 1\sigma (%s)"%u,
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(h, +1, ref = data),
        'down':add_sigmas(h, -1, ref = data),
        'color':ROOT.kOrange-9,
        } for u, h in uncertainties.iteritems()
        ]
    unfolding_signal_input_MCStat          = {
        'name' : "MCStat",
        'label': "\pm 1\sigma (MC stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(mcStat, +1, ref = data),
        'down':add_sigmas(mcStat, -1, ref = data),
        'color':ROOT.kOrange-9,
        }
    unfolding_data_input_systematic        = {
        'name' : "data",
        'label': "\pm 1\sigma",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue-10,
        }



class expected_dRlg_RunII:
  if False:
    uncertainties = allUncertainties + signal_uncertainty_dRlg
    expected        = True
    cache_directory = default_cache_directory 
    corr_key        = "bkgSubtracted_SR3pdRUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_correlationFitObject"
    data_key        = "bkgSubtracted_SR3pdRUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_data_%s"
    signal_key      = "bkgSubtracted_SR3pdRUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_total_%s"
    uncertaintyUp_key = {u:"bkgSubtracted_SR3pdRUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_%s_Up"%u for u in uncertainties}
    mcStatUp_key      = "bkgSubtracted_SR3pdRUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_MCStat_Up_%s"

    cache_dir       = os.path.join(cache_directory, "unfolding", "combined", "bkgSubstracted", "expected" if expected else "observed", "postFit", "noFreeze")
    dirDB           = MergingDirDB(cache_dir)

    years           = ["2016", "2017", "2018"]

    data_histos     =  [ dirDB.get( data_key%year ) for year in years ]
    signal_histos   =  [ dirDB.get( signal_key%year ) for year in years ]

    corrFitObj      = dirDB.get( corr_key )
    signal_frozen_histos   =  [ dirDB.get( signal_key%year ) for year in years ] 
    uncertainties_histos   = {}
    for u, k in uncertaintyUp_key.iteritems():
        uncertainties_histos[u] = [add_error_from_Upvariation( dirDB.get( k+"_"+year ), signal_frozen_histos[i] ) for i,year in enumerate(years)]
    mcStatUp_histos   =  [ add_error_from_Upvariation( dirDB.get( mcStatUp_key%year ), signal_frozen_histos[i] ) for i,year in enumerate(years) ] 

    reco_variable   = { "dRlg_reco":"sqrt((PhotonGood0_eta-LeptonTight0_eta)**2+acos(cos(PhotonGood0_phi-LeptonTight0_phi))**2)"}
    reco_selection  = "SR3p"
    
    reco_thresholds = thresholds_from_histo( data_histos[0] )

    # events not in the reco region are filled with this value
    covZRange = (0.0099,191)
    reco_variable_underflow = -1
    # appending reco thresholds for multiple years
    reco_overflow        = "upper"
    max_reco_val         = reco_thresholds[-1]
    min_reco_val         = reco_thresholds[0]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    # events not in the reco region are filled with this value
    reco_variable_underflow = reco_thresholds[0]-0.5

    # make reco_thresholds for all years
    reco_thresholds_years = list(copy.deepcopy(reco_thresholds))
    for i_year in range(1, len(years)):
        reco_thresholds_years +=  [ x + (max_reco_val-min_reco_val)*i_year for x in reco_thresholds[1:] ]

    data        = merge_x( data_histos, reco_thresholds_years )
    signal      = merge_x( signal_histos, reco_thresholds_years )
    mcStat      = merge_x( mcStatUp_histos, reco_thresholds_years )
    uncertainties   = {}
    for u, histlist in uncertainties_histos.iteritems():
        uncertainties[u] = merge_x( histlist, reco_thresholds_years )

    fiducial_variable   = "genLCMStight0GammadR"
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds     = (0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.4)

    fiducial_overflow       = "upper"
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    tex_reco = "#Delta R(#gamma, l)^{reco}"
    tex_gen  = "#Delta R(#gamma, l)^{gen}"
    tex_unf  = "#Delta R(#gamma, l)^{fid.}"
    tex_pur  = "#Delta R(#gamma, l)"
    texY     = 'Fiducial cross section [fb]'    
    y_range         = (0.9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.39,1.61)
    data_legendText = "Data (137/fb)"
    signal_legendText =  "Observation"

    lumi_factor               = (lumi_year[2016]+lumi_year[2017]+lumi_year[2018])/1000.
    unfolding_data_input      = replace_data_error( data )
    unfolding_data_input_systematic_bands          = [
        ]
    unfolding_signal_input        = replace_data_error( data )
    unfolding_signal_input_systematic_bands          = [
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(signal, +1, ref = data),
        'down':add_sigmas(signal, -1, ref = data),
        'color':ROOT.kOrange-9,
        },
        ]
    unfolding_signal_input_systematics          = [
       {'name' : u,
        'label': "\pm 1\sigma (%s)"%u,
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(h, +1, ref = data),
        'down':add_sigmas(h, -1, ref = data),
        'color':ROOT.kOrange-9,
        } for u, h in uncertainties.iteritems()
        ]
    unfolding_signal_input_MCStat          = {
        'name' : "MCStat",
        'label': "\pm 1\sigma (MC stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(mcStat, +1, ref = data),
        'down':add_sigmas(mcStat, -1, ref = data),
        'color':ROOT.kOrange-9,
        }
    unfolding_data_input_systematic        = {
        'name' : "data",
        'label': "\pm 1\sigma",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue-10,
        }



class observed_dRlg_RunII:
#  if False:
    uncertainties = allUncertainties + signal_uncertainty_dRlg
    expected        = False
    cache_directory = default_cache_directory 
    corr_key        = "bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_correlationFitObject"
    data_key        = "bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_data_%s"
    signal_key      = "bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_total_%s"
    uncertaintyUp_key = {u:"bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_%s_Up"%u for u in uncertainties}
    mcStatUp_key      = "bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_MCStat_Up_%s"

    cache_dir       = os.path.join(cache_directory, "unfolding", "combined", "bkgSubstracted", "expected" if expected else "observed", "postFit", "noFreeze")
    dirDB           = MergingDirDB(cache_dir)

    years           = ["2016", "2017", "2018"]

    data_histos     =  [ dirDB.get( data_key%year ) for year in years ]
    signal_histos   =  [ dirDB.get( signal_key%year ) for year in years ]

    corrFitObj      = dirDB.get( corr_key )
    signal_frozen_histos   =  [ dirDB.get( signal_key%year ) for year in years ] 
    uncertainties_histos   = {}
    for u, k in uncertaintyUp_key.iteritems():
        uncertainties_histos[u] = [add_error_from_Upvariation( dirDB.get( k+"_"+year ), signal_frozen_histos[i] ) for i,year in enumerate(years)]
    mcStatUp_histos   =  [ add_error_from_Upvariation( dirDB.get( mcStatUp_key%year ), signal_frozen_histos[i] ) for i,year in enumerate(years) ] 

    uncertaintyStatUp_key = {u:"bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_%s_Up"%u for u in signal_uncertainty_dRlg + ["r"]}
    cache_dir       = os.path.join(cache_directory, "unfolding", "combined", "bkgSubstracted", "observed", "postFit", "freezeSyst")
    dirDB           = MergingDirDB(cache_dir)
    corrFitObjStat  =  dirDB.get( corr_key )
    signalStat_frozen_histos  =  [ dirDB.get( signal_key%year ) for year in years ]
    uncertaintiesStat_histos   = {}
    for u, k in uncertaintyStatUp_key.iteritems():
        uncertaintiesStat_histos[u] = [add_error_from_Upvariation( dirDB.get( k+"_"+year ), signalStat_frozen_histos[i] ) for i,year in enumerate(years)]
    mcStatStatUp_histos   =  [ add_error_from_Upvariation( dirDB.get( mcStatUp_key%year ), signalStat_frozen_histos[i] ) for i,year in enumerate(years) ]


    reco_variable   = { "dRlg_reco":"sqrt((PhotonGood0_eta-LeptonTight0_eta)**2+acos(cos(PhotonGood0_phi-LeptonTight0_phi))**2)"}
    reco_selection  = "SR3p"
    
    reco_thresholds = thresholds_from_histo( data_histos[0] )

    # events not in the reco region are filled with this value
    covZRange = (0.0099,191)
    reco_variable_underflow = -1
    # appending reco thresholds for multiple years
    reco_overflow        = "upper"
    max_reco_val         = reco_thresholds[-1]
    min_reco_val         = reco_thresholds[0]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    # events not in the reco region are filled with this value
    reco_variable_underflow = reco_thresholds[0]-0.5

    # make reco_thresholds for all years
    reco_thresholds_years = list(copy.deepcopy(reco_thresholds))
    for i_year in range(1, len(years)):
        reco_thresholds_years +=  [ x + (max_reco_val-min_reco_val)*i_year for x in reco_thresholds[1:] ]

    data        = merge_x( data_histos, reco_thresholds_years )
    signal      = merge_x( signal_histos, reco_thresholds_years )
    mcStat      = merge_x( mcStatUp_histos, reco_thresholds_years )
    mcStatStat  = merge_x( mcStatStatUp_histos, reco_thresholds_years )
    uncertainties   = {}
    for u, histlist in uncertainties_histos.iteritems():
        uncertainties[u] = merge_x( histlist, reco_thresholds_years )

    uncertaintiesStat   = {}
    for u, histlist in uncertaintiesStat_histos.iteritems():
        uncertaintiesStat[u] = merge_x( histlist, reco_thresholds_years )


    fiducial_variable   = "genLCMStight0GammadR"
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds     = (0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.4)
    
    fiducial_overflow       = "upper"
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    tex_reco = "#Delta R(#gamma, l)^{reco}"
    tex_gen  = "#Delta R(#gamma, l)^{gen}"
    tex_unf  = "#Delta R(#gamma, l)^{fid.}"
    tex_pur  = "#Delta R(#gamma, l)"
    texY     = 'Fiducial cross section [fb]'    
    y_range         = (0.9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.84, 1.16)
    data_legendText = "Data (137/fb)"
    signal_legendText =  "Observation"

    lumi_factor               = (lumi_year[2016]+lumi_year[2017]+lumi_year[2018])/1000.
    unfolding_data_input      = replace_data_error( data )
    unfolding_data_input_systematic_bands          = [
        ]

    unfolding_signal_input        = replace_data_error( data )
    unfolding_signal_input_systematic_bands          = [
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(signal, +1, ref = data),
        'down':add_sigmas(signal, -1, ref = data),
        'color':ROOT.kOrange-9,
        },
        ]
    unfolding_signal_input_systematics          = [
       {'name' : u,
        'label': "\pm 1\sigma (%s)"%u,
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(h, +1, ref = data),
        'down':add_sigmas(h, -1, ref = data),
        'color':ROOT.kOrange-9,
        } for u, h in uncertainties.iteritems()
        ]
    unfolding_signal_input_MCStat          = {
        'name' : "MCStat",
        'label': "\pm 1\sigma (MC stat.)",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(mcStat, +1, ref = data),
        'down':add_sigmas(mcStat, -1, ref = data),
        'color':ROOT.kOrange-9,
        }
    unfolding_data_input_systematic        = {
        'name' : "data",
        'label': "\pm 1\sigma",
        'matrix': "nominal",
        'ref': replace_data_error( data ),
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue-10,
        }

    unfolding_signalStat_input_systematics          = [
       {'name' : u,
        'label': "\pm 1\sigma (%s)"%u,
        'matrix': "nominal",
        'ref':  replace_data_error( data ),
        'up':  add_sigmas(h, +1, ref = data),
        'down':add_sigmas(h, -1, ref = data),
        'color':ROOT.kOrange-9,
        } for u, h in uncertaintiesStat.iteritems()
        ]
    unfolding_signalStat_input_MCStat          = {
        'name' : "MCStat",
        'label': "\pm 1\sigma (MC stat.)",
        'matrix': "nominal",
        'ref':  replace_data_error( data ),
        'up':  add_sigmas(mcStatStat, +1, ref = data),
        'down':add_sigmas(mcStatStat, -1, ref = data),
        'color':ROOT.kOrange-9,
        }


