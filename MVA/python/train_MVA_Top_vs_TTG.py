#!/usr/bin/env python

# Analysis
from Analysis.TMVA.Trainer       import Trainer
from Analysis.TMVA.Reader        import Reader
from Analysis.TMVA.defaults      import default_methods, default_factory_settings 

import Analysis.Tools.syncer

from RootTools.plot.helpers    import copyIndexPHP

# TTGammaEFT
from TTGammaEFT.Tools.user           import plot_directory, mva_directory
from TTGammaEFT.Tools.cutInterpreter import cutInterpreter

# MVA configuration
#from TTGammaEFT.MVA.MVA_Top_vs_TTG import mlp1, bdt1, sequence, read_variables, mva_variables
from TTGammaEFT.MVA.MVA_Top_vs_TTG import sequence, read_variables, mva_variables, Bezeichnung


# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--plot_directory',     action='store',             default=None)
argParser.add_argument('--selection',          action='store', type=str,   default='nLepTight1-nLepVeto1-nJet3p-nBTag1p-nPhoton1')
argParser.add_argument('--trainingFraction',   action='store', type=float, default=0.5)
argParser.add_argument('--small',              action='store_true')
argParser.add_argument('--overwrite',          action='store_true')

argParser.add_argument('--variables',          action='store', type=str,   default='all')
argParser.add_argument('--mva',                action='store', type=str,   default='all')
argParser.add_argument('--NTrees',             action='store', type=float, default=250)
argParser.add_argument('--maxdepth',           action='store', type=float, default=1)
argParser.add_argument('--ncuts',              action='store', type=float, default=50)

argParser.add_argument('--NLayers',            action='store', type=float, default=7)
argParser.add_argument('--LearningRate',       action='store', type=float, default=0.03)
argParser.add_argument('--Sampling',           action='store', type=float, default=0.3)
argParser.add_argument('--SamplingEpoch',      action='store', type=float, default=0.8)

args = argParser.parse_args()

#Logger
import Analysis.Tools.logger as logger
logger = logger.get_logger("INFO", logFile = None )

if args.plot_directory == None:
    args.plot_directory = plot_directory

if args.selection == None:
    selectionString = "(1)"
else:
    selectionString = cutInterpreter.cutString( args.selection )



if args.variables: 
   x = args.variables 
   plot_directory += "_"+str(x)



# Samples
from TTGammaEFT.Samples.nanoTuples_RunII_postProcessed import TTG, Top

signal = TTG 

# TTZ
backgrounds = [ Top ]

samples = backgrounds + [signal]
for sample in samples:
    sample.setSelectionString( selectionString )
    if args.small:
        sample.reduceFiles(to = 1)

# old part
# mvas = [ bdt1, mlp1]


mvas = [Bezeichnung]


## TMVA Trainer instance
trainer = Trainer( 
    signal = signal, 
    backgrounds = backgrounds, 
    output_directory = mva_directory, 
    plot_directory   = plot_directory, 
    mva_variables    = mva_variables,
    label            = "MVA_TopVsTTG", 
    fractionTraining = args.trainingFraction, 
    )

weightString = "(1)"
trainer.createTestAndTrainingSample( 
    read_variables   = read_variables,   
    sequence         = sequence,
    weightString     = weightString,
    overwrite        = args.overwrite, 
    )

for mva in mvas:
    trainer.addMethod(method = mva)

trainer.trainMVA( factory_settings = default_factory_settings )
trainer.plotEvaluation()
copyIndexPHP(plot_directory)
