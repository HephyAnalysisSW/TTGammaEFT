import ROOT
from TTGammaEFT.Samples.nanoTuples_RunII_postProcessed import *
from TTGammaEFT.Tools.TriggerSelector import TriggerSelector
from TTGammaEFT.Tools.user            import plot_directory

#tt0l = Sample.fromDirectory("tt0l", directory = ["/scratch/robert.schoefbeck/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_2016_TTG_private_v47/inclusive/TTHad_pow_CP5/"])
#tt1l = Sample.fromDirectory("tt1l", directory = ["/scratch/robert.schoefbeck/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_2016_TTG_private_v47/inclusive/TTSingleLep_pow_CP5/"])
#tt2l = Sample.fromDirectory("tt2l", directory = ["/scratch/robert.schoefbeck/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_2016_TTG_private_v47/inclusive/TTLep_pow_CP5/"])

ttg0l = Sample.fromDirectory("ttg0l", directory = ["/scratch/robert.schoefbeck/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_2016_TTG_private_v47/inclusive/TTGHad_LO/"])
ttg1l = Sample.fromDirectory("ttg1l", directory = ["/scratch/robert.schoefbeck/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_2016_TTG_private_v47/inclusive/TTGSingleLep_LO/"])
ttg2l = Sample.fromDirectory("ttg2l", directory = ["/scratch/robert.schoefbeck/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_2016_TTG_private_v47/inclusive/TTGLep_LO/"])
ttg   = Sample.combine( "ttg", [ttg0l, ttg1l, ttg2l] )

## Missing: Add years

corr_factor = 1.

triggerSelector = TriggerSelector(2016)

lumi_weight_str = "(%f*(year==2016)+%f*(year==2017)+%f*(year==2018))"%(Run2016.lumi/1000,Run2017.lumi/1000,Run2018.lumi/1000)
weight = "%s*weight*reweightHEM*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF" % lumi_weight_str
reco_cut = "nLeptonTight==1&&nLeptonVetoIsoCorr==1&&nJetGood>=3&&nBTagGood>=1&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1&&triggered==1&&reweightHEM>0&&overlapRemoval==1&&(PhotonGood0_photonCatMagic==0||PhotonGood0_photonCatMagic==2)&&((year==2016&&Flag_goodVertices&&Flag_globalSuperTightHalo2016Filter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_BadPFMuonFilter&&PV_ndof>4&&sqrt(PV_x*PV_x+PV_y*PV_y)<=2&&abs(PV_z)<=24)||(year==2017&&Flag_goodVertices&&Flag_globalSuperTightHalo2016Filter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_BadPFMuonFilter&&PV_ndof>4&&sqrt(PV_x*PV_x+PV_y*PV_y)<=2&&abs(PV_z)<=24)||(year==2018&&Flag_goodVertices&&Flag_globalSuperTightHalo2016Filter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_BadPFMuonFilter&&PV_ndof>4&&sqrt(PV_x*PV_x+PV_y*PV_y)<=2&&abs(PV_z)<=24))"

fiducial_cut = "overlapRemoval==1&&nGenLeptonCMSUnfold==1&&nGenJetsCMSUnfold>=3&&nGenBJetCMSUnfold>=1&&nGenPhotonCMSUnfold==1"
MET_filter_cut   = "(year==2016&&Flag_goodVertices&&Flag_globalSuperTightHalo2016Filter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_BadPFMuonFilter&&PV_ndof>4&&sqrt(PV_x*PV_x+PV_y*PV_y)<=2&&abs(PV_z)<=24)"

gen_match_photon_cut = "sqrt(acos(cos(GenPhotonCMSUnfold0_phi-PhotonGood0_phi))**2+(GenPhotonCMSUnfold0_eta-PhotonGood0_eta)**2)<0.1"
weightString = "weight*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger*reweightHEM*reweightL1Prefire*reweightBTag_SF"
pt_thresholds = [20, 35, 50, 65, 80, 120, 160, 200, 260, 320, 520]

# completely inclusive xsec in fb:
# weight = w(gen) * sigma(pb) * 1000 pb^-1/fb^-1 / Sum(w(gen))

# unit fb:
#weight_at_gen = "weight" 
# unit events:
weight_at_gen = "%s*weight" % lumi_weight_str

entries = [ 
# parton level
    { 'name':"total",                         'selectionString':"(1)", "weightString":weight_at_gen},
    { 'name':"overlap",                       'selectionString':"overlapRemoval==1", "weightString":weight_at_gen},
## particle level
#    { 'name':"fiducial ==1 photon > 20 GeV",  'selectionString':"overlapRemoval==1&&nGenPhotonCMSUnfold==1",    "weightString":weight_at_gen},
#    { 'name':"fiducial ==1 Lep",              'selectionString':"overlapRemoval==1&&nGenPhotonCMSUnfold==1&&nGenLeptonCMSUnfold==1", "weightString":weight_at_gen},
#    { 'name':"fiducial ==1 Ele, ==0 Mu",      'selectionString':"overlapRemoval==1&&nGenPhotonCMSUnfold==1&&nGenElectronCMSUnfold==1&&nGenMuonCMSUnfold==0", "weightString":weight_at_gen, 'prefix' : "  "},
#    { 'name':"fiducial ==1 Mu, ==0 Ele",      'selectionString':"overlapRemoval==1&&nGenPhotonCMSUnfold==1&&nGenMuonCMSUnfold==1&&nGenElectronCMSUnfold==0", "weightString":weight_at_gen, 'prefix' : "  "},
#    { 'name':"fiducial >=1 Jets",             'selectionString':"overlapRemoval==1&&nGenJetsCMSUnfold>=1&&nGenPhotonCMSUnfold==1&&nGenLeptonCMSUnfold==1", "weightString":weight_at_gen},
#    { 'name':"fiducial >=2 Jets",             'selectionString':"overlapRemoval==1&&nGenJetsCMSUnfold>=2&&nGenPhotonCMSUnfold==1&&nGenLeptonCMSUnfold==1", "weightString":weight_at_gen},
#    { 'name':"fiducial >=3 Jets",             'selectionString':"overlapRemoval==1&&nGenJetsCMSUnfold>=3&&nGenPhotonCMSUnfold==1&&nGenLeptonCMSUnfold==1", "weightString":weight_at_gen},
    { 'name':"fiducial >=1 b-Jets",           'selectionString':"overlapRemoval==1&&nGenBJetCMSUnfold>=1&&nGenJetsCMSUnfold>=3&&nGenPhotonCMSUnfold==1&&nGenLeptonCMSUnfold==1", "weightString":weight_at_gen},
#    { 'name':"fiducial >=4 Jets",             'selectionString':"overlapRemoval==1&&nGenJetsCMSUnfold>=4&&nGenPhotonCMSUnfold==1&&nGenLeptonCMSUnfold==1", "weightString":weight_at_gen},
    ] 

entries += [
#    { 'name':"reco trigger 1e||1mu",       'selectionString':fiducial_cut+"&&("+triggerSelector.SingleMuon+"||"+triggerSelector.SingleElectron+")", "weightString":weight_at_gen+"*reweightPU*reweightTrigger"},
#    { 'name':"reco trigger 1 e",           'selectionString':fiducial_cut+"&&"+triggerSelector.SingleElectron, "weightString":weight_at_gen+"*reweightPU*reweightTrigger", 'prefix' : "  "},
#    { 'name':"reco trigger 1 mu",          'selectionString':fiducial_cut+"&&"+triggerSelector.SingleMuon, "weightString":weight_at_gen+"*reweightPU*reweightTrigger", 'prefix' : "  "},
#    { 'name':"reco == 1 tight lep",        'selectionString':fiducial_cut+"&&nLeptonTight==1&&triggered", "weightString":weight_at_gen+"*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger"},
#    { 'name':"reco == 1 tight mu",         'selectionString':fiducial_cut+"&&nLeptonTight==1&&triggered&&abs(LeptonTight0_pdgId)==13", "weightString":weight_at_gen+"*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger", 'prefix' : "  "},
#    { 'name':"reco == 1 tight e",          'selectionString':fiducial_cut+"&&nLeptonTight==1&&triggered&&abs(LeptonTight0_pdgId)==11", "weightString":weight_at_gen+"*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger", 'prefix' : "  "},
#    { 'name':"reco extra leptonVeto",      'selectionString':fiducial_cut+"&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1", "weightString":weight_at_gen+"*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger"},
#    { 'name':"reco MET filters",           'selectionString':fiducial_cut+"&&"+MET_filter_cut+"&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1", "weightString":weight_at_gen+"*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger"},
#    { 'name':"reco HEM",                   'selectionString':fiducial_cut+"&&"+MET_filter_cut+"&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1", "weightString":weight_at_gen+"*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger*reweightHEM"},
#    { 'name':"reco L1Prefire",             'selectionString':fiducial_cut+"&&"+MET_filter_cut+"&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1", "weightString":weight_at_gen+"*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger*reweightHEM*reweightL1Prefire"},
#    { 'name':"reco ==1 photon > 20 GeV",   'selectionString':fiducial_cut+"&&"+MET_filter_cut+"&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1&&nPhotonGood==1", "weightString":weight_at_gen+"*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger*reweightHEM*reweightL1Prefire"},
#    { 'name':"reco photon veto",           'selectionString':fiducial_cut+"&&"+MET_filter_cut+"&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1", "weightString":weight_at_gen+"*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger*reweightHEM*reweightL1Prefire"},
#    { 'name':"reco >=3 Jets",              'selectionString':fiducial_cut+"&&"+MET_filter_cut+"&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1&&nJetGood>=3", "weightString":weight_at_gen+"*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger*reweightHEM*reweightL1Prefire"},
    { 'name':"(fid.) reco >=1 b-Jets",            'selectionString':fiducial_cut+"&&"+MET_filter_cut+"&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1&&nJetGood>=3&&nBTagGood>=1", "weightString":weight_at_gen+"*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger*reweightHEM*reweightL1Prefire*reweightBTag_SF"},
    { 'name':"(fid., no weight) reco >=1 b-Jets",            'selectionString':fiducial_cut+"&&"+MET_filter_cut+"&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1&&nJetGood>=3&&nBTagGood>=1", "weightString":"(1)"},
#    { 'name':"gamma gen-matched",           'selectionString':fiducial_cut+"&&"+MET_filter_cut+"&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1&&nJetGood>=3&&nBTagGood>=1&&sqrt(acos(cos(GenPhotonCMSUnfold0_phi-PhotonGood0_phi))**2+(GenPhotonCMSUnfold0_eta-PhotonGood0_eta)**2)<0.1", "weightString":weight_at_gen+"*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger*reweightHEM*reweightL1Prefire*reweightBTag_SF", "prefix":"  "},
#    { 'name':"reco >=4 Jets",              'selectionString':fiducial_cut+"&&"+MET_filter_cut+"&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1&&nJetGood>=4&&nBTagGood>=1", "weightString":weight_at_gen+"*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger*reweightHEM*reweightL1Prefire*reweightBTag_SF", 'prefix':"  "},
]
entries += [
#    { 'name':"(no fid.) reco trigger 1e||1mu",       'selectionString':"overlapRemoval==1&&("+triggerSelector.SingleMuon+"||"+triggerSelector.SingleElectron+")", "weightString":weight_at_gen+"*reweightPU*reweightTrigger"},
#    { 'name':"(no fid.) reco trigger 1e||1mu",       'selectionString':"overlapRemoval==1&&("+triggerSelector.SingleMuon+"||"+triggerSelector.SingleElectron+")", "weightString":weight_at_gen+"*reweightPU*reweightTrigger"},
#    { 'name':"(no fid.) reco trigger 1 e",           'selectionString':overlapRemoval==1&&"+triggerSelector.SingleElectron, "weightString":weight_at_gen+"*reweightPU*reweightTrigger", 'prefix' : "  "},
#    { 'name':"(no fid.) reco trigger 1 mu",          'selectionString':overlapRemoval==1&&triggerSelector.SingleMuon, "weightString":weight_at_gen+"*reweightPU*reweightTrigger", 'prefix' : "  "},
#    { 'name':"(no fid.) reco == 1 tight lep",        'selectionString':"overlapRemoval==1&&nLeptonTight==1&&triggered", "weightString":weight_at_gen+"*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger"},
#    { 'name':"(no fid.) reco == 1 tight mu",         'selectionString':"overlapRemoval==1&&nLeptonTight==1&&triggered&&abs(LeptonTight0_pdgId)==13", "weightString":weight_at_gen+"*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger", 'prefix' : "  "},
#    { 'name':"(no fid.) reco == 1 tight e",          'selectionString':"overlapRemoval==1&&nLeptonTight==1&&triggered&&abs(LeptonTight0_pdgId)==11", "weightString":weight_at_gen+"*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger", 'prefix' : "  "},
#    { 'name':"(no fid.) reco extra leptonVeto",      'selectionString':"overlapRemoval==1&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1", "weightString":weight_at_gen+"*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger"},
#    { 'name':"(no fid.) reco MET filters",           'selectionString':MET_filter_cut+"&&overlapRemoval==1&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1", "weightString":weight_at_gen+"*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger"},
#    { 'name':"(no fid.) reco HEM",                   'selectionString':MET_filter_cut+"&&overlapRemoval==1&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1", "weightString":weight_at_gen+"*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger*reweightHEM"},
#    { 'name':"(no fid.) reco L1Prefire",             'selectionString':MET_filter_cut+"&&overlapRemoval==1&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1", "weightString":weight_at_gen+"*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger*reweightHEM*reweightL1Prefire"},
#    { 'name':"(no fid.) reco ==1 photon",   'selectionString':MET_filter_cut+"&&overlapRemoval==1&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1&&nPhotonGood==1", "weightString":weight_at_gen+"*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger*reweightHEM*reweightL1Prefire"},
#    { 'name':"(no fid.) reco photon veto",           'selectionString':MET_filter_cut+"&&overlapRemoval==1&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1", "weightString":weight_at_gen+"*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger*reweightHEM*reweightL1Prefire"},
#    { 'name':"(no fid.) reco >=3 Jets",              'selectionString':MET_filter_cut+"&&overlapRemoval==1&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1&&nJetGood>=3", "weightString":weight_at_gen+"*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger*reweightHEM*reweightL1Prefire"},
    { 'name':"(no fid.) reco >=1 b-Jets",            'selectionString':MET_filter_cut+"&&overlapRemoval==1&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1&&nJetGood>=3&&nBTagGood>=1", "weightString":weight_at_gen+"*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger*reweightHEM*reweightL1Prefire*reweightBTag_SF"},
    { 'name':"(no fid., no weights) reco >=1 b-Jets",            'selectionString':MET_filter_cut+"&&overlapRemoval==1&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1&&nJetGood>=3&&nBTagGood>=1", "weightString":"(1)"},
#    { 'name':"(no fid.) reco >=4 Jets",              'selectionString':MET_filter_cut+"&&overlapRemoval==1&&nLeptonTight==1&&triggered&&nLeptonVetoIsoCorr==1&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1&&nJetGood>=4&&nBTagGood>=1", "weightString":weight_at_gen+"*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPU*reweightTrigger*reweightHEM*reweightL1Prefire*reweightBTag_SF"},
]

result = []
samples = [ttg, ttg0l, ttg1l, ttg2l]#, tt0l, tt1l, tt2l ]

print " "*39 +"".join( ["{:9s}".format(s.name) for s in samples ] )

for i_entry, entry in enumerate(entries):
    result.append( [ s.getYieldFromDraw( selectionString = entry['selectionString'], weightString = entry['weightString'] ) for s in samples] )
    result[-1][2]['val']*=corr_factor

    p_string = "{i_entry:02d} {name:31s}" + "".join( [" {r[%i][val]:8.2f}"%i for i in range(len(samples)) ] )

    print p_string.format( i_entry=i_entry, r=result[i_entry], name=entry['prefix']+entry['name'] if entry.has_key('prefix') else entry['name'])

#
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
