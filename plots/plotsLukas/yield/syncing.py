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

from TTGammaEFT.Samples.nanoTuples_Sync_semilep_postProcessed      import TTG_sync_16 # as sample
from TTGammaEFT.Samples.nanoTuples_Sync_semilep_postProcessed      import WJets_sync_16 # as sample
from TTGammaEFT.Samples.nanoTuples_Sync_semilep_postProcessed      import QCD_e_sync_16 # as sample
from TTGammaEFT.Samples.nanoTuples_Sync_semilep_postProcessed      import QCD_mu_sync_16 # as sample
allsamples = [QCD_mu_sync_16, QCD_e_sync_16, TTG_sync_16, WJets_sync_16]
filterCutMc   = getFilterCut( 2016, isData=False, skipBadChargedCandidate=True, skipVertexFilter=False )

if not evtList:
  for mode in ["e","mu"]:
    lumi = 1

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

    selection = "nLeptonTight==1&&nLeptonVetoIsoCorr==1&&nJetGood==2&&nBTagGood>=1&&nPhotonGood==0&&triggered==1"
    if mode == "e":    selection += "&&nElectronTight==1"
    elif mode == "mu": selection += "&&nMuonTight==1"
    selection += "&&" + filterCutMc

    invselection = "nLeptonTightInvIso==1&&nLeptonVetoIsoCorr==1&&nJetGoodInvLepIso==2&&nBTagGoodInvLepIso==0&&nPhotonGoodInvLepIso==0&&triggeredInvIso==1"
    if mode == "e":    invselection += "&&nElectronTightInvIso==1"
    elif mode == "mu": invselection += "&&nMuonTightInvIso==1"
    invselection += "&&" + filterCutMc

    for sample in allsamples:
        for i, w in enumerate(weightStrings):
            print sample.name, mode, "SR", str(u_float(sample.getYieldFromDraw(selectionString=selection, weightString=w))), "CR", str(u_float(sample.getYieldFromDraw(selectionString=invselection, weightString=invWeightStrings[i]))), "weight=%s"%w

else:
    sample = WJets_sync_16
    selection = "nLeptonTight==1&&nLeptonVetoIsoCorr==1&&nJetGood==2&&nBTagGood>=1&&nPhotonGood==0&&triggered==1"
    selection += "&&nMuonTight==1"
    #selection += "&&nMuonTight==1"
    selection += "&&" + filterCutMc

    # Define a reader
    r = sample.treeReader( \
        variables = [ TreeVariable.fromString("event/l"), TreeVariable.fromString('run/i'), TreeVariable.fromString('luminosityBlock/i') ],
        selectionString = selection,
        )

    print "run", "luminosityBlock", "event"
    r.start()
    while r.run():
        run, lumi, evt = r.event.run, r.event.luminosityBlock, r.event.event
        print run, lumi, evt







