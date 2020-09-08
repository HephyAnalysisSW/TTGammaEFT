#!/usr/bin/env python

# Standard imports
from operator                    import attrgetter
from math                        import pi, sqrt, cosh, cos
import ROOT

from TTGammaEFT.Tools.objectSelection   import jetSelector, getParticles 
from Analysis.Tools.helpers             import deltaPhi, deltaR2, deltaR

# Logger
import Analysis.Tools.logger as logger
logger = logger.get_logger("INFO", logFile = None )

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--variables',          action='store', type=str,   default='all')
argParser.add_argument('--overwrite',          action='store_true')
argParser.add_argument('--mva',                action='store', type=str,   default='mlp')
argParser.add_argument('--NTrees',             action='store', type=float, default=250)
argParser.add_argument('--maxdepth',           action='store', type=float, default=1)
argParser.add_argument('--ncuts',              action='store', type=float, default=50)

argParser.add_argument('--NLayers',            action='store', type=float, default=7)
argParser.add_argument('--LearningRate',       action='store', type=float, default=0.03)
argParser.add_argument('--Sampling',           action='store', type=float, default=0.3)
argParser.add_argument('--SamplingEpoch',      action='store', type=float, default=0.8)

args = argParser.parse_args()

# Training variables
read_variables = [\
    "year/I",
    "nBTagGood/I",
    "nJetGood/I", "ht/F", "mT/F","MET_pt/F",
    "LeptonTight0_pt/F","LeptonTight0_phi/F",
    "LeptonTight0_eta/F", "m3/F", 
    "Jet[pt/F,eta/F,phi/F,btagDeepB/F,jetId/I]",
    "PhotonGood0_mvaID/F",
    "PhotonGood0_pt/F", "PhotonGood0_eta/F","PhotonGood0_phi/F",
    "nJet/I",
    "JetGood0_eta/F","JetGood0_phi/F",
    "photonJetdR/F", "photonLepdR/F", "leptonJetdR/F", "tightLeptonJetdR/F",
    "ltight0GammadR/F", "ltight0GammadPhi/F", 
    "mLtight0Gamma/F",
    "nJet/I",
    "JetGood0_btagDeepB/F","JetGood1_btagDeepB/F",
    "JetGood0_neEmEF/F","JetGood0_chEmEF/F","JetGood0_neHEF/F","JetGood0_chHEF/F",
    "PhotonGood0_sieie/F","PhotonGood0_hoe/F","PhotonGood0_pfRelIso03_chg/F","PhotonGood0_pfRelIso03_all/F","PhotonGood0_r9/F",
       ]

# sequence 
sequence = []

recoJetSel = {key:jetSelector(key) for key in [2016, 2017, 2018]}

def makeGoodJets(event, sample=None):
    # read all jets
    allJets     = getParticles( event, collVars=["pt","eta","phi","jetId","btagDeepB"], coll="Jet" )
    # selection
    JetGood = list( filter( lambda j: recoJetSel[event.year](j), allJets ) )
    JetGood = filter( lambda j :deltaR(j, {'eta':event.PhotonGood0_eta, 'phi':event.PhotonGood0_phi})>0.4, JetGood )
    JetGood = filter( lambda j :deltaR(j, {'eta':event.LeptonTight0_eta, 'phi':event.LeptonTight0_phi})>0.4, JetGood )
    event.JetGood  = JetGood
    event.nJetGood = len(JetGood)

sequence.append( makeGoodJets )

if args.variables == 'orig':

    mva_variables = {
#                "mva_year"                  :(lambda event, sample: event.year),
                "mva_PhotonGood0_mvaID"     :(lambda event, sample: event.PhotonGood0_mvaID),
                "mva_ht"                    :(lambda event, sample: event.ht),
                "mva_met_pt"                :(lambda event, sample: event.MET_pt), 
                "mva_nJetGood"              :(lambda event, sample: event.nJetGood),
                "mva_nBTag"                 :(lambda event, sample: event.nBTagGood),
                "mva_mT"                    :(lambda event, sample: event.mT),
                "mva_m3"                    :(lambda event, sample: event.m3),
                "mva_dRlg"                  :(lambda event, sample: deltaR({'eta':event.PhotonGood0_eta, 'phi':event.PhotonGood0_phi},{'eta':event.LeptonTight0_eta,'phi':event.LeptonTight0_phi})),    # other
                "mva_mlg"                   :(lambda event, sample: sqrt(2*event.LeptonTight0_pt*event.PhotonGood0_pt*(cosh(event.LeptonTight0_eta-event.PhotonGood0_eta)-cos(event.LeptonTight0_phi-event.PhotonGood0_phi)))),  # other

                "mva_jet0_pt"               :(lambda event, sample: event.JetGood[0]['pt']   if event.nJetGood >=1 else 0),
                "mva_jet0_eta"              :(lambda event, sample: event.JetGood[0]['eta']   if event.nJetGood >=1 else -10),
                "mva_jet0_btagDeepB"        :(lambda event, sample: event.JetGood[0]['btagDeepB'] if (event.nJetGood >=1 and event.JetGood[0]['btagDeepB']>-10) else -10),
                "mva_jet1_pt"               :(lambda event, sample: event.JetGood[1]['pt']   if event.nJetGood >=2 else 0),
                "mva_jet1_eta"              :(lambda event, sample: event.JetGood[1]['eta']   if event.nJetGood >=2 else -10),
                "mva_jet1_btagDeepB"        :(lambda event, sample: event.JetGood[1]['btagDeepB'] if (event.nJetGood >=2 and event.JetGood[1]['btagDeepB']>-10) else -10),
                "mva_jet2_pt"               :(lambda event, sample: event.JetGood[2]['pt']   if event.nJetGood >=3 else 0),
                "mva_jet2_eta"              :(lambda event, sample: event.JetGood[2]['eta']   if event.nJetGood >=3 else -10),
                "mva_jet2_btagDeepB"        :(lambda event, sample: event.JetGood[2]['btagDeepB']   if (event.nJetGood >=3 and event.JetGood[2]['btagDeepB']>-10) else -10),
                "mva_jet3_pt"               :(lambda event, sample: event.JetGood[3]['pt']   if event.nJetGood >=4 else 0),
                "mva_jet3_eta"              :(lambda event, sample: event.JetGood[3]['eta']   if event.nJetGood >=4 else -10),
                "mva_jet3_btagDeepB"        :(lambda event, sample: event.JetGood[3]['btagDeepB']   if (event.nJetGood >=4 and event.JetGood[3]['btagDeepB']>-10) else -10),

                 }


elif args.variables == 'varlist1':

    mva_variables = {
                "mva_PhotonGood0_mvaID"     :(lambda event, sample: event.PhotonGood0_mvaID),
                "mva_ht"                    :(lambda event, sample: event.ht),
                "mva_nBTag"                 :(lambda event, sample: event.nBTagGood),
                "mva_mT"                    :(lambda event, sample: event.mT),
                "mva_m3"                    :(lambda event, sample: event.m3),

                "mva_PhotonGood0_pt"        :(lambda event, sample: event.PhotonGood0_pt),
                "mva_leptonJetdR"           :(lambda event, sample: event.leptonJetdR),        
                "mva_ltight0GammadR"        :(lambda event, sample: event.ltight0GammadR),
                "mva_nBTagGood"             :(lambda event, sample: event.nBTagGood),
                "mva_nJetGood"              :(lambda event, sample: event.nJetGood),
                "mva_photonJetdR"           :(lambda event, sample: event.photonJetdR),        
                "mva_photonLepdR"           :(lambda event, sample: event.photonLepdR),
                "mva_ltight0GammadPhi"      :(lambda event, sample: event.ltight0GammadPhi),    
                "mva_PhotonGood0_eta"       :(lambda event, sample: event.PhotonGood0_eta),
                "mva_mlg"                   :(lambda event, sample: event.mLtight0Gamma),

# MP
#               "mva_ltight0GammadPhi"      :(lambda event, sample: deltaPhi(event.LeptonTight0_phi, event.PhotonGood0_phi)),
#               "mva_photonJetdR"           :(lambda event, sample: deltaR({'eta':event.PhotonGood0_eta, 'phi':event.PhotonGood0_phi},{'eta':event.JetGood[0]['eta'],'phi':event.JetGood[0]['phi']})),
#               "mva_tightLeptonJetdR"      :(lambda event, sample: deltaR({'eta':event.LeptonTight0_eta, 'phi':event.LeptonTight0_phi},{'eta':event.JetGood_eta[0],'phi':event.JetGood_phi[0]})),
    
                }


elif args.variables == 'varlist2':

    mva_variables = {
                "mva_PhotonGood0_mvaID"     :(lambda event, sample: event.PhotonGood0_mvaID),
                "mva_ht"                    :(lambda event, sample: event.ht),
                "mva_nBTag"                 :(lambda event, sample: event.nBTagGood),
                "mva_mT"                    :(lambda event, sample: event.mT),
                "mva_m3"                    :(lambda event, sample: event.m3),

                "mva_PhotonGood0_pt"        :(lambda event, sample: event.PhotonGood0_pt),
                "mva_leptonJetdR"           :(lambda event, sample: event.leptonJetdR),
                "mva_ltight0GammadR"        :(lambda event, sample: event.ltight0GammadR),
                "mva_nBTagGood"             :(lambda event, sample: event.nBTagGood),
                "mva_nJetGood"              :(lambda event, sample: event.nJetGood),
                "mva_photonJetdR"           :(lambda event, sample: event.photonJetdR),
                "mva_photonLepdR"           :(lambda event, sample: event.photonLepdR),
                "mva_ltight0GammadPhi"      :(lambda event, sample: event.ltight0GammadPhi),
                "mva_PhotonGood0_eta"       :(lambda event, sample: event.PhotonGood0_eta),
                "mva_mlg"                   :(lambda event, sample: event.mLtight0Gamma),

                "mva_PhotonGood0_sieie"     :(lambda event, sample: event.PhotonGood0_sieie),
                "mva_PhotonGood0_hoe"       :(lambda event, sample: event.PhotonGood0_hoe),
                "mva_PhotonGood0_pfRelIso03_ne":(lambda event, sample: event.PhotonGood0_pfRelIso03_all-event.PhotonGood0_pfRelIso03_chg),
                "mva_PhotonGood0_r9"        :(lambda event, sample: event.PhotonGood0_r9),


# MP
#               "mva_ltight0GammadPhi"      :(lambda event, sample: deltaPhi(event.LeptonTight0_phi, event.PhotonGood0_phi)),
#               "mva_photonJetdR"           :(lambda event, sample: deltaR({'eta':event.PhotonGood0_eta, 'phi':event.PhotonGood0_phi},{'eta':event.JetGood[0]['eta'],'phi':event.Jet$
#               "mva_tightLeptonJetdR"      :(lambda event, sample: deltaR({'eta':event.LeptonTight0_eta, 'phi':event.LeptonTight0_phi},{'eta':event.JetGood_eta[0],'phi':event.JetG$

                }




#bdt1 = {
#"type"                : ROOT.TMVA.Types.kBDT,
#"name"                : "bdt1",
#"color"               : ROOT.kGreen,
#"options"             : ["!H","!V","NTrees=250","BoostType=Grad","Shrinkage=0.20","UseBaggedBoost","GradBaggingFraction=0.5","SeparationType=GiniIndex","nCuts=50","PruneMethod=NoPruning","MaxDepth=1"],
#}

#mlp1 = {
#"type"                : ROOT.TMVA.Types.kMLP,
#"name"                : "mlp1",
#"layers"              : "N+7",
#"color"               : ROOT.kRed+5,
#"options"             : ["!H","!V","VarTransform=Norm,Deco","NeuronType=sigmoid","NCycles=10000","TrainingMethod=BP","LearningRate=0.03", "DecayRate=0.01","Sampling=0.3","SamplingEpoch=0.8","ConvergenceTests=1","CreateMVAPdfs=True","TestRate=10" ],
#}



Bezeichnung = args.mva+"_NTrees"+str(args.NTrees)+"_maxDepth"+str(args.maxdepth)+"_nCuts"+str(args.ncuts)
NTrees      = args.NTrees
MaxDepth    = args.maxdepth
nCuts       = args.ncuts 

Bezeichnung = {
"type"                : ROOT.TMVA.Types.kBDT,
"name"                : str(Bezeichnung),
"color"               : ROOT.kGreen,
"options"             : ["!H","!V","NTrees="+str(NTrees),"BoostType=Grad","Shrinkage=0.20","UseBaggedBoost","GradBaggingFraction=0.5","SeparationType=GiniIndex","nCuts="+str(nCuts),"PruneMethod=NoPruning","MaxDepth="+str(MaxDepth)],
}


#Bezeichnung = args.mva+"_NLayers"+str(args.NLayers)+"_LR"+str(args.LearningRate)+"_Sampl"+str(args.Sampling)+"_SEpoch"+str(args.SamplingEpoch)
#NLayers       = args.NLayers
#LearningRate  = args.LearningRate
#Sampling      = args.Sampling
#SamplingEpoch = args.SamplingEpoch


#Bezeichnung = {
#"type"                : ROOT.TMVA.Types.kMLP,
#"name"                : str(Bezeichnung),
#"layers"              : "N+"+str(NLayers),
#"color"               : ROOT.kGreen,
#"options"             : ["!H","!V","VarTransform=Norm,Deco","NeuronType=sigmoid","NCycles=10000","TrainingMethod=BP","LearningRate="+str(LearningRate), "DecayRate=0.01","Sampling="+str(Sampling),"SamplingEpoch="+str(SamplingEpoch), "ConvergenceTests=1", "CreateMVAPdfs=True","TestRate=10" ]
#}

