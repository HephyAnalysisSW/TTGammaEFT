from TTGammaEFT.Samples.nanoTuples_RunII_postProcessed import *

from TTGammaEFT.Tools.TriggerSelector import TriggerSelector

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

# completely inclusive xsec in fb:
# weight = w(gen) * sigma(pb) * 1000 pb^-1/fb^-1 / Sum(w(gen))

entries = [ 
# parton level
    { 'name':"total",                         'selectionString':"(1)", "weightString":"weight"},
    { 'name':"overlap",                       'selectionString':"overlapRemoval==1", "weightString":"weight"},
# particle level
    { 'name':"fiducial ==1 photon > 20 GeV",  'selectionString':"overlapRemoval==1&&nGenPhotonCMSUnfold==1",    "weightString":"weight"},
    { 'name':"fiducial ==1 Lep",              'selectionString':"overlapRemoval==1&&nGenPhotonCMSUnfold==1&&nGenLeptonCMSUnfold==1", "weightString":"weight"},
    { 'name':"fiducial ==1 Ele, ==0 Mu",      'selectionString':"overlapRemoval==1&&nGenPhotonCMSUnfold==1&&nGenElectronCMSUnfold==1&&nGenMuonCMSUnfold==0", "weightString":"weight", 'prefix' : "  "},
    { 'name':"fiducial ==1 Mu, ==0 Ele",      'selectionString':"overlapRemoval==1&&nGenPhotonCMSUnfold==1&&nGenMuonCMSUnfold==1&&nGenElectronCMSUnfold==0", "weightString":"weight", 'prefix' : "  "},
    { 'name':"fiducial >=1 Jets",             'selectionString':"overlapRemoval==1&&nGenJetsCMSUnfold>=1&&nGenPhotonCMSUnfold==1&&nGenLeptonCMSUnfold==1", "weightString":"weight"},
    { 'name':"fiducial >=2 Jets",             'selectionString':"overlapRemoval==1&&nGenJetsCMSUnfold>=2&&nGenPhotonCMSUnfold==1&&nGenLeptonCMSUnfold==1", "weightString":"weight"},
    { 'name':"fiducial >=3 Jets",             'selectionString':"overlapRemoval==1&&nGenJetsCMSUnfold>=3&&nGenPhotonCMSUnfold==1&&nGenLeptonCMSUnfold==1", "weightString":"weight"},
    { 'name':"fiducial >=1 b-Jets",           'selectionString':"overlapRemoval==1&&nGenBJetCMSUnfold>=1&&nGenJetsCMSUnfold>=3&&nGenPhotonCMSUnfold==1&&nGenLeptonCMSUnfold==1", "weightString":"weight"},
    ] 

fiducial_cut = "overlapRemoval==1&&nGenLeptonCMSUnfold==1&&nGenJetsCMSUnfold>=3&&nGenBJetCMSUnfold>=1&&nGenPhotonCMSUnfold==1"
MET_filter_cut   = "(year==2016&&Flag_goodVertices&&Flag_globalSuperTightHalo2016Filter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_BadPFMuonFilter&&PV_ndof>4&&sqrt(PV_x*PV_x+PV_y*PV_y)<=2&&abs(PV_z)<=24)"

entries += [
    { 'name':"reco trigger 1e||1mu",       'selectionString':fiducial_cut+"&&("+triggerSelector.SingleMuon+"||"+triggerSelector.SingleElectron+")", "weightString":"weight*reweightPU*reweightTrigger"},
    { 'name':"reco trigger 1 e",           'selectionString':fiducial_cut+"&&"+triggerSelector.SingleElectron, "weightString":"weight*reweightPU*reweightTrigger", 'prefix' : "  "},
    { 'name':"reco trigger 1 mu",          'selectionString':fiducial_cut+"&&"+triggerSelector.SingleMuon, "weightString":"weight*reweightPU*reweightTrigger", 'prefix' : "  "},
    { 'name':"reco == 1 tight lep",        'selectionString':fiducial_cut+"&&nLeptonTight==1&&triggered", "weightString":"weight*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger"},
    { 'name':"reco == 1 tight mu",         'selectionString':fiducial_cut+"&&nLeptonTight==1&&triggered&&abs(LeptonTight0_pdgId)==13", "weightString":"weight*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger", 'prefix' : "  "},
    { 'name':"reco == 1 tight e",          'selectionString':fiducial_cut+"&&nLeptonTight==1&&triggered&&abs(LeptonTight0_pdgId)==11", "weightString":"weight*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger", 'prefix' : "  "},
    { 'name':"reco extra leptonVeto",      'selectionString':fiducial_cut+"&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1", "weightString":"weight*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger"},
    { 'name':"reco MET filters",           'selectionString':fiducial_cut+"&&"+MET_filter_cut+"&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1", "weightString":"weight*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger"},
    { 'name':"reco HEM",                   'selectionString':fiducial_cut+"&&"+MET_filter_cut+"&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1", "weightString":"weight*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger*reweightHEM"},
    { 'name':"reco L1Prefire",             'selectionString':fiducial_cut+"&&"+MET_filter_cut+"&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1", "weightString":"weight*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger*reweightHEM*reweightL1Prefire"},
    { 'name':"reco ==1 photon > 20 GeV",   'selectionString':fiducial_cut+"&&"+MET_filter_cut+"&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1&&nPhotonGood==1", "weightString":"weight*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger*reweightHEM*reweightL1Prefire"},
    { 'name':"reco photon veto",           'selectionString':fiducial_cut+"&&"+MET_filter_cut+"&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1", "weightString":"weight*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger*reweightHEM*reweightL1Prefire"},
    { 'name':"reco >=3 Jets",              'selectionString':fiducial_cut+"&&"+MET_filter_cut+"&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1&&nJetGood>=3", "weightString":"weight*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger*reweightHEM*reweightL1Prefire"},
    { 'name':"reco >=1 b-Jets",              'selectionString':fiducial_cut+"&&"+MET_filter_cut+"&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1&&nJetGood>=3&&nBTagGood>=1", "weightString":"weight*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger*reweightHEM*reweightL1Prefire*reweightBTag_SF"},
]

result = []
samples = [ttg, ttg0l, ttg1l, ttg2l, tt0l, tt1l, tt2l ]

print " "*32 +"".join( ["{:10s}".format(s.name) for s in samples ] )

for i_entry, entry in enumerate(entries):
    result.append( [ s.getYieldFromDraw( selectionString = entry['selectionString'], weightString = entry['weightString'] ) for s in samples] )

    p_string = "{name:34s}" + "".join( [" {r[%i][val]:8.2f}"%i for i in range(len(samples)) ] )

    print p_string.format( r = result[i_entry], name=entry['prefix']+entry['name'] if entry.has_key('prefix') else entry['name'])

#weight = "%s*weight*reweightHEM*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF" % lumi_weight_str

#
#reco_cut = "nLeptonTight==1&&nLeptonVetoIsoCorr==1&&nJetGood>=3&&nBTagGood>=1&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1&&triggered==1&&reweightHEM>0&&overlapRemoval==1&&(PhotonGood0_photonCatMagic==0||PhotonGood0_photonCatMagic==2)&&((year==2016&&Flag_goodVertices&&Flag_globalSuperTightHalo2016Filter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_BadPFMuonFilter&&PV_ndof>4&&sqrt(PV_x*PV_x+PV_y*PV_y)<=2&&abs(PV_z)<=24)||(year==2017&&Flag_goodVertices&&Flag_globalSuperTightHalo2016Filter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_BadPFMuonFilter&&PV_ndof>4&&sqrt(PV_x*PV_x+PV_y*PV_y)<=2&&abs(PV_z)<=24)||(year==2018&&Flag_goodVertices&&Flag_globalSuperTightHalo2016Filter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_BadPFMuonFilter&&PV_ndof>4&&sqrt(PV_x*PV_x+PV_y*PV_y)<=2&&abs(PV_z)<=24))"
#
##lumi_weight_str = "(%f*(year==2016)+%f*(year==2017)+%f*(year==2018))"%(Run2016.lumi/1000,Run2017.lumi/1000,Run2018.lumi/1000)
#
#
#
##sigma_fiducial_fb = Summer16.TTG.getYieldFromDraw(fiducial, "weight")['val']
#sigma_fiducial_fb = 984.7595363975266
#
##sigma_reco        = Summer16.TTG.getYieldFromDraw("("+fiducial+")*("+reco+")", "weight")['val']
#sigma_reco_fb     = 241.11019826708844
#
#sigma_reco_fb_scale = {}
##sigma_fiducial_fb_scale = {}
#for i in range(44):
#    print "At", i
##    sigma_fiducial_fb_scale[i] = Summer16.TTG.getYieldFromDraw(fiducial, "weight*LHEScaleWeight[%i]"%i)['val'] 
#    sigma_reco_fb_scale[i] = Summer16.TTG.getYieldFromDraw("("+fiducial+")*("+reco+")", "weight*LHEScaleWeight[%i]"%i)['val'] 
#
