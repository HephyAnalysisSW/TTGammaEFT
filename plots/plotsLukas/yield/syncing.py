#!/usr/bin/env python
''' Analysis script for standard plots
'''

# Standard imports
import ROOT, os, imp, sys, copy
#ROOT.gROOT.SetBatch(True)
import itertools
from math                                import isnan, ceil, pi
from Analysis.Tools.metFilters           import getFilterCut

# RootTools
from RootTools.core.standard             import *
from Analysis.Tools.u_float import u_float
# Default Parameter
loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']

evtList = True

#from TTGammaEFT.Samples.nanoTuples_Sync_semilep_postProcessed      import TTG_sync_16 # as sample
#from TTGammaEFT.Samples.nanoTuples_Sync_semilep_postProcessed      import WJets_sync_16 # as sample
#from TTGammaEFT.Samples.nanoTuples_Sync_semilep_postProcessed      import QCD_e_sync_16 # as sample
#from TTGammaEFT.Samples.nanoTuples_Sync_semilep_postProcessed      import QCD_mu_sync_16 # as sample

#from TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed import QCD_mu80To120, QCD_e80To120
from TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed import QCD_mu80To120, QCD_e80To120

#allsamples = [QCD_mu_sync_16, QCD_e_sync_16, TTG_sync_16, WJets_sync_16]
allsamples = [QCD_mu80To120]
filterCutMc   = getFilterCut( 2016, isData=False, skipBadChargedCandidate=True, skipVertexFilter=False )

if not evtList:
#  for mode in ["e","mu"]:
  for nj in [">=4","==3","==2"]:
    lumi = 1

    mode = "mu"
    weightStrings   = ["1"]
#    weightStrings  += ["weight"]
#    weightStrings  += ["weight*reweightPU"]
#    weightStrings  += ["weight*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF"]
#    weightStrings  += ["weight*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightBTag_SF"]
#    weightStrings  += ["weight*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightBTag_SF*reweightL1Prefire"]

    invWeightStrings   = ["1"]
#    invWeightStrings  += ["weight"]
#    invWeightStrings  += ["weight*reweightPU"]
#    invWeightStrings  += ["weight*reweightPU*reweightLeptonTightSFInvIso*reweightLeptonTrackingTightSFInvIso"]
#    invWeightStrings  += ["weight*reweightPU*reweightLeptonTightSFInvIso*reweightLeptonTrackingTightSFInvIso*reweightBTag_SF"]
#    invWeightStrings  += ["weight*reweightPU*reweightLeptonTightSFInvIso*reweightLeptonTrackingTightSFInvIso*reweightBTag_SF*reweightL1Prefire"]

#    selection = "nLeptonTight==1&&nLeptonVetoIsoCorr==1&&nJetGood==2&&nBTagGood>=1&&nPhotonGood==0&&triggered==1"
    selection = "nLeptonTight==1&&nLeptonVetoIsoCorr==1&&nJetGood%s&&nBTagGood>=1&&nPhotonGood==0&&nPhotonNoChgIsoNoSieie==0&&triggered==1&&overlapRemoval==1"%nj
    if mode == "e":    selection += "&&nElectronTight==1"
    elif mode == "mu": selection += "&&nMuonTight==1"
    selection += "&&" + filterCutMc

#    invselection = "nLeptonTightInvIso==1&&nLeptonVetoIsoCorr==1&&nJetGoodInvLepIso==2&&nBTagGoodInvLepIso==0&&nPhotonGoodInvLepIso==0&&triggeredInvIso==1"
    invselection = "nLeptonTightInvIso==1&&nLeptonVetoIsoCorr==1&&nJetGoodInvLepIso%s&&nBTagGoodInvLepIso==0&&nPhotonGoodInvLepIso==0&&nPhotonNoChgIsoNoSieieInvLepIso==0&&triggeredInvIso==1&&overlapRemoval==1"%nj
    if mode == "e":    invselection += "&&nElectronTightInvIso==1"
    elif mode == "mu": invselection += "&&nMuonTightInvIso==1"
    invselection += "&&" + filterCutMc

    for sample in allsamples:
        for i, w in enumerate(weightStrings):
            print sample.name, nj, mode, "SR", str(u_float(sample.getYieldFromDraw(selectionString=selection, weightString=w))), "CR", str(u_float(sample.getYieldFromDraw(selectionString=invselection, weightString=invWeightStrings[i]))), "weight=%s"%w

else:
#    sample = QCD_e80To120
    sample = QCD_mu80To120
    selection = "nLeptonTight==1&&nLeptonVetoIsoCorr==1&&nJetGood==2&&nBTagGood>=1&&nPhotonGood==0&&nPhotonNoChgIsoNoSieie==0&&triggered==1&&overlapRemoval==1"
    selection += "&&nMuonTight==1"
#    selection += "&&nElectronTight==1"
#    selection = "nLeptonTightInvIso==1&&nLeptonVetoIsoCorr==1&&nJetGoodInvLepIso==2&&nBTagGoodInvLepIso==0&&nPhotonGoodInvLepIso==0&&nPhotonNoChgIsoNoSieieInvLepIso==0&&triggeredInvIso==1&&overlapRemoval==1"
#    selection += "&&nElectronTightInvIso==1"
#    selection += "&&nMuonTightInvIso==1"


    selection += "&&" + filterCutMc

#    weightStrings  += ["weight*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightBTag_SF*reweightL1Prefire"]
    # Define a reader
    r = sample.treeReader( \
        variables = [
                      TreeVariable.fromString("event/l"), TreeVariable.fromString('run/i'), TreeVariable.fromString('luminosityBlock/i'),
                      TreeVariable.fromString("reweightPU/F"), TreeVariable.fromString('weight/F'), TreeVariable.fromString('reweightLeptonTightSF/F'),
                      TreeVariable.fromString('reweightL1Prefire/F'), TreeVariable.fromString('reweightBTag_SF/F'),TreeVariable.fromString('reweightLeptonTrackingTightSF/F'),
                      TreeVariable.fromString('reweightLeptonTrackingTightSFInvIso/F'), TreeVariable.fromString('reweightLeptonTightSFInvIso/F'),
                      TreeVariable.fromString('reweightTrigger/F'),
                      TreeVariable.fromString('reweightInvIsoTrigger/F'),
                    ],
        selectionString = selection,
        )

    print "run", "luminosityBlock", "event", "lumiweight", "PileUp", "leptonEff", "Btag", "prefire"
    r.start()
    while r.run():

        run, lumi, evt = r.event.run, r.event.luminosityBlock, r.event.event
        weight, PU, lepID = r.event.weight, r.event.reweightPU, r.event.reweightLeptonTightSF
        lepIDInv =  r.event.reweightLeptonTightSFInvIso
        prefire, btag, lepReco = r.event.reweightL1Prefire, r.event.reweightBTag_SF, r.event.reweightLeptonTrackingTightSF
        lepRecoInv = r.event.reweightLeptonTrackingTightSFInvIso
        trig = r.event.reweightTrigger
        trigInv = r.event.reweightInvIsoTrigger
        lep = lepIDInv*lepRecoInv*trigInv if "InvIso" in selection else lepID*lepReco*trig
#        print lepIDInv, lepRecoInv, trigInv, lepID, lepReco, trig
        print run, lumi, evt, weight, PU, lep, btag, prefire







