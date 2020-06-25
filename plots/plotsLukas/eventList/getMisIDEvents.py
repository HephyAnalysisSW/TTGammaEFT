
# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   "INFO", logFile = None)
logger_rt = logger_rt.get_logger("INFO", logFile = None)

from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter

#from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed      import *
from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import *
#from TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed        import *
#from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import *
#from TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed import * 
#from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import *
data_sample = Run2016

#selectionString="nLepTight1-nLepVeto1-nJet4p-nBTag1p-nPhoton1p-mlgamma85to105-e"
#selectionString="nLepTight1-nLepVeto1-nJet4p-nBTag1p-nPhoton1p-mlgamma85to105-mu"
#selectionString="nLepTight1-nLepVeto1-nJet4p-nBTag1p-nPhoton1p-mlgamma85to105"

#selectionString="nLepTight1-nLepVeto1-nJet3p-nBTag0-nPhoton1p-mlgamma85to105-e"
#selectionString="nLepTight1-nLepVeto1-nJet3p-nBTag0-nPhoton1p-mlgamma85to105-mu"
#selectionString="nLepTight1-nLepVeto1-nJet3p-nBTag0-nPhoton1p-mlgamma85to105"

#selectionString="nLepTight1-nLepVeto1-nJet3p-nPhoton1p-mlgamma85to105-e"
selectionString="nLepTight1-nLepVeto1-nJet3p-nPhoton1p-mlgamma85to105-mu"
#selectionString="nLepTight1-nLepVeto1-nJet3p-nPhoton1p-mlgamma85to105"

eList = data_sample.getEventList(selectionString=cutInterpreter.cutString(selectionString))
data_sample.chain.SetEventList(eList)

with open("dat/"+selectionString+".dat", "w") as f:
    for i in range(eList.GetN()):
        data_sample.chain.GetEntry(i)
        f.write(str(data_sample.chain.run) + ":" + str(data_sample.chain.luminosityBlock) + ":" + str(data_sample.chain.event) + "\n")
