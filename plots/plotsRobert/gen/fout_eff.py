import ROOT
from TTGammaEFT.Samples.nanoTuples_RunII_postProcessed import *
from TTGammaEFT.Tools.TriggerSelector import TriggerSelector
from TTGammaEFT.Tools.user            import plot_directory

tt0l = Sample.fromDirectory("tt0l", directory = ["/scratch/robert.schoefbeck/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_2016_TTG_private_v45/inclusive/TTHad_pow_CP5/"])
tt1l = Sample.fromDirectory("tt1l", directory = ["/scratch/robert.schoefbeck/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_2016_TTG_private_v45/inclusive/TTSingleLep_pow_CP5/"])
tt2l = Sample.fromDirectory("tt2l", directory = ["/scratch/robert.schoefbeck/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_2016_TTG_private_v45/inclusive/TTLep_pow_CP5/"])

ttg0l = Sample.fromDirectory("ttg0l", directory = ["/scratch/robert.schoefbeck/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_2016_TTG_private_v45/inclusive/TTGHad_LO/"])
ttg1l = Sample.fromDirectory("ttg1l", directory = ["/scratch/robert.schoefbeck/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_2016_TTG_private_v45/inclusive/TTGSingleLep_LO/"])
ttg2l = Sample.fromDirectory("ttg2l", directory = ["/scratch/robert.schoefbeck/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_2016_TTG_private_v45/inclusive/TTGLep_LO/"])
ttg   = Sample.combine( "ttg", [ttg0l, ttg1l, ttg2l] )

## Missing: Add TT contribution + 'overlapremoval'
## Missing: Add years


triggerSelector = TriggerSelector(2016)

lumi_weight_str = "(%f*(year==2016)+%f*(year==2017)+%f*(year==2018))"%(Run2016.lumi/1000,Run2017.lumi/1000,Run2018.lumi/1000)
weight = "%s*weight*reweightHEM*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF" % lumi_weight_str
reco_cut = "nLeptonTight==1&&nLeptonVetoIsoCorr==1&&nJetGood>=3&&nBTagGood>=1&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1&&triggered==1&&reweightHEM>0&&overlapRemoval==1&&(PhotonGood0_photonCatMagic==0||PhotonGood0_photonCatMagic==2)&&((year==2016&&Flag_goodVertices&&Flag_globalSuperTightHalo2016Filter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_BadPFMuonFilter&&PV_ndof>4&&sqrt(PV_x*PV_x+PV_y*PV_y)<=2&&abs(PV_z)<=24)||(year==2017&&Flag_goodVertices&&Flag_globalSuperTightHalo2016Filter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_BadPFMuonFilter&&PV_ndof>4&&sqrt(PV_x*PV_x+PV_y*PV_y)<=2&&abs(PV_z)<=24)||(year==2018&&Flag_goodVertices&&Flag_globalSuperTightHalo2016Filter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_BadPFMuonFilter&&PV_ndof>4&&sqrt(PV_x*PV_x+PV_y*PV_y)<=2&&abs(PV_z)<=24))"

fiducial_cut = "overlapRemoval==1&&nGenLeptonCMSUnfold==1&&nGenJetsCMSUnfold>=3&&nGenBJetCMSUnfold>=1&&nGenPhotonCMSUnfold==1"
MET_filter_cut   = "(year==2016&&Flag_goodVertices&&Flag_globalSuperTightHalo2016Filter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_BadPFMuonFilter&&PV_ndof>4&&sqrt(PV_x*PV_x+PV_y*PV_y)<=2&&abs(PV_z)<=24)"

gen_match_photon_cut = "sqrt(acos(cos(GenPhotonCMSUnfold0_phi-PhotonGood0_phi))**2+(GenPhotonCMSUnfold0_eta-PhotonGood0_eta)**2)<0.1"
weightString = "weight*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger*reweightHEM*reweightL1Prefire*reweightBTag_SF"
pt_thresholds = [20, 35, 50, 65, 80, 120, 160, 200, 260, 320, 520]

ROOT.TH1.SetDefaultSumw2(0)

f_out_ref = ttg.get1DHistoFromDraw("PhotonGood0_pt", selectionString = reco_cut, weightString = weightString, binning = pt_thresholds, binningIsExplicit = True)
f_out     = ttg.get1DHistoFromDraw("PhotonGood0_pt", selectionString = reco_cut+"&&"+gen_match_photon_cut+"&&"+fiducial_cut, weightString = weightString, binning = pt_thresholds, binningIsExplicit = True)
f_out.Divide( f_out_ref )

eff_ref = ttg.get1DHistoFromDraw("GenPhotonCMSUnfold0_pt", selectionString = fiducial_cut, weightString = weightString, binning = pt_thresholds, binningIsExplicit = True)
eff = ttg.get1DHistoFromDraw(    "GenPhotonCMSUnfold0_pt", selectionString = fiducial_cut+"&&"+gen_match_photon_cut+"&&"+reco_cut, weightString = weightString, binning = pt_thresholds, binningIsExplicit = True)
eff.Divide( eff_ref )

f_out_ref.Scale(1./f_out_ref.Integral())

f_out_ref.style = styles.lineStyle( ROOT.kGray, errors = False)
f_out_ref.legendText = "spectrum (normalized)"

f_out.style = styles.lineStyle( ROOT.kBlue, errors = True)
f_out.legendText = "1-f_{out}"
eff.style = styles.lineStyle( ROOT.kRed, errors = True)
eff.legendText = "efficiency"
histos = [ [f_out_ref], [f_out], [eff]]

plot = Plot.fromHisto(name = "correction", histos = histos, texX = "p_{T} (GeV)", texY = "Correction" )
plotting.draw(plot, plot_directory = plot_directory+'/unfolding', ratio = None, logY = False, logX = False, yRange=(0,1), legend = (0.45,0.7-0.05*len(histos),0.95,0.70))
