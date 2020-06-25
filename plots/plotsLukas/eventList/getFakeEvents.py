# Standard imports
import ROOT, os, imp, sys, copy
# RootTools
from RootTools.core.standard             import *

# Internal Imports
from TTGammaEFT.Tools.cutInterpreter     import cutInterpreter

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   "INFO", logFile = None)
logger_rt = logger_rt.get_logger("INFO", logFile = None)


os.environ["gammaSkim"]="True"
#postprocessing_directory = "TTGammaEFT_PP_2016_TTG_private_v22/semilep/"
from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed      import *
#from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed_test      import *
#from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import *
#from TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed        import *
#from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import *
#from TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed import * 
#from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import *
#sample = TT_SemiLep_16 #TT_pow_16 #Run2016
sample = TT_Lep_16 #TT_pow_16 #Run2016
#sample.files = sample.files[:1]
#print sample.files
#selectionString="nLepTight1-nLepVeto1-nJet4p-nBTag1p-nPhoton1p-mlgamma85to105-e"
#selectionString="nLepTight1-nLepVeto1-nJet4p-nBTag1p-nPhoton1p-mlgamma85to105-mu"
#selectionString="nLepTight1-nLepVeto1-nJet4p-nBTag1p-nPhoton1p-mlgamma85to105"

#selectionString="nLepTight1-nLepVeto1-nJet3p-nBTag0-nPhoton1p-mlgamma85to105-e"
#selectionString="nLepTight1-nLepVeto1-nJet3p-nBTag0-nPhoton1p-mlgamma85to105-mu"
#selectionString="nLepTight1-nLepVeto1-nJet3p-nBTag0-nPhoton1p-mlgamma85to105"

#selectionString="nLepTight1-nLepVeto1-nJet3p-nPhoton1p-mlgamma85to105-e"
selectionString="nLepTight1-nLepVeto1-nJet1-nBTag0-nPhoton1p-noGenMatch"
#selectionString="nLepTight1-nLepVeto1-nJet3p-nPhoton1p-mlgamma85to105"

# Define a reader
r = sample.treeReader( \
    variables = [ TreeVariable.fromString("event/l"), TreeVariable.fromString('run/i'), TreeVariable.fromString("luminosityBlock/i") ],
    selectionString = cutInterpreter.cutString(selectionString),
)
r.start()

#eList = sample.getEventList( selectionString=cutInterpreter.cutString(selectionString) )
#sample.chain.SetEventList(eList)

with open("dat/"+selectionString+".dat", "w") as f:
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


