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
from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed      import *
sample = TTG_16
selectionString="all"#nLepTight1-nLepVeto1-nJet1-nBTag0-nPhoton1p-noGenMatch"
variables = [
             TreeVariable.fromString("event/l"), TreeVariable.fromString('run/i'), TreeVariable.fromString("luminosityBlock/i"),
             TreeVariable.fromString("nGenPhoton/I"),
            ]

# Define a reader
r = sample.treeReader( \
    variables = variables, 
    selectionString = cutInterpreter.cutString(selectionString),
)
r.start()

while r.run():
    run, evt, lumi = r.event.run, r.event.event, r.event.luminosityBlock
    print(r.event.nGenPhoton)

