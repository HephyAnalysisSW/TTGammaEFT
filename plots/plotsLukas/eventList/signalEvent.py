# Standard imports
import ROOT, os, imp, sys, copy
# RootTools
from RootTools.core.standard             import *
import Analysis.Tools.syncer as syncer

# Internal Imports
from TTGammaEFT.Tools.cutInterpreter     import cutInterpreter

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   "INFO", logFile = None)
logger_rt = logger_rt.get_logger("INFO", logFile = None)


os.environ["gammaSkim"]="True"
from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import *
sample = Run2018

#selectionString  = "ltight0GammadR>0.8&&photonJetdR>0.8&&LeptonTight0_pt>50&&PhotonGood0_pt<70&&JetGood0_pt<70&&nLeptonTight==1&&nMuonTight==1&&nLeptonVetoIsoCorr==1&&nJetGood>=4&&nBTagGood==2&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1&&triggered==1"
#selectionString  = "ltight0GammadR>0.8&&photonJetdR>0.8&&LeptonTight0_pt>50&&PhotonGood0_pt>70&&JetGood0_pt>70&&JetGood1_pt>70&&nLeptonTight==1&&nMuonTight==1&&nLeptonVetoIsoCorr==1&&nJetGood>=4&&nBTagGood==2&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1&&triggered==1"
selectionString  = "ltight0GammadR>0.8&&photonJetdR>0.8&&LeptonTight0_pt>50&&PhotonGood0_pt<70&&JetGood0_pt>70&&JetGood1_pt>70&&nLeptonTight==1&&nMuonTight==1&&nLeptonVetoIsoCorr==1&&nJetGood>=4&&nBTagGood==2&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1&&triggered==1"
selectionString += "&&weight>0&&reweightHEM>0&&Flag_goodVertices&&Flag_globalSuperTightHalo2016Filter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_BadPFMuonFilter&&PV_ndof>4&&sqrt(PV_x*PV_x+PV_y*PV_y)<=2&&abs(PV_z)<=24"
selName = "2018-Muon-nJet4p-nBTag2-lowPt"
# Define a reader
r = sample.treeReader( \
    variables = [ TreeVariable.fromString("event/l"), TreeVariable.fromString('run/i'), TreeVariable.fromString("luminosityBlock/i") ],
    selectionString = selectionString,
)
r.start()

#eList = sample.getEventList( selectionString=cutInterpreter.cutString(selectionString) )
#sample.chain.SetEventList(eList)

with open("dat/"+selName+".dat", "w") as f:
#    for i in range(eList.GetN()):
#        sample.chain.GetEntry(i)
#        f.write(str(sample.chain.run) + ":" + str(sample.chain.luminosityBlock) + ":" + str(sample.chain.event) + "\n")




#    r.activateAllBranches()
#    event_list = ttg.getEventList( ttg.selectionString )
#    r.SetEventList( event_list )

#    logger.info( "Found %i events in sample %s", event_list.GetN(), ttg.name )


#    selection = args.selection
#    for key, value in category.items():
#        selection = selection.replace(key, value)

    while r.run():
        run, evt, lumi = r.event.run, r.event.event, r.event.luminosityBlock
        print run, evt, lumi
        f.write(":".join( [str(run), str(lumi), str(evt)] ) + "\n")

#    del r


