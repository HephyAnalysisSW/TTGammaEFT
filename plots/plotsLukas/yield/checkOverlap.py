#!/usr/bin/env python
''' Analysis script for standard plots
'''

# Standard imports
import ROOT, os, imp, sys, copy
#ROOT.gROOT.SetBatch(True)
import itertools
from math                                import isnan, ceil, pi

# RootTools
from RootTools.core.standard             import *

# Internal Imports
from TTGammaEFT.Tools.user               import plot_directory
from TTGammaEFT.Tools.cutInterpreter     import cutInterpreter
from TTGammaEFT.Tools.TriggerSelector_postprocessed    import TriggerSelector

from Analysis.Tools.metFilters           import getFilterCut
from Analysis.Tools.u_float              import u_float

# Default Parameter
loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                  help="Log level for logging")
argParser.add_argument('--selection',          action='store',      default='dilepOS-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1p')
argParser.add_argument('--year',               action='store',      type=str, default="2018" )
args = argParser.parse_args()

if args.year != "RunII": args.year = int(args.year)

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)


os.environ["gammaSkim"]="True"
if args.year == 2016:
    from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import Run2016 as sample
elif args.year == 2017:
    from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import Run2017 as sample
elif args.year == 2018:
    from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import Run2018 as sample
elif args.year == "RunII":
    from TTGammaEFT.Samples.nanoTuples_RunII_postProcessed import RunII as sample

if True:

    filterCut   = getFilterCut( args.year, isData=True, skipBadChargedCandidate=True, skipVertexFilter=False )

    selection = "&&".join( [ cutInterpreter.cutString( args.selection ), filterCut, "triggered==1" ] )

    print selection
    
    # Define a reader
    r = sample.treeReader( \
        variables = [ TreeVariable.fromString("event/l"), TreeVariable.fromString('run/i'), TreeVariable.fromString('luminosityBlock/i') ],
        selectionString = selection,
        )

    r.start()
    
    selection = args.selection

    allEvents = []
    while r.run():
        run, lumi, evt = r.event.run, r.event.luminosityBlock, r.event.event
        allEvents += [(run,lumi,evt)]

    filepath = "logs/overlapCheck_%i_EventList_%s.dat"%(args.year,selection)

    with open(filepath, "w") as f:
        for run, lumi, evt in allEvents:
            f.write(str(run) + "," + str(lumi) + "," + str(evt) + "\n")

all    = len(allEvents)
unique = len(set(allEvents))
print "year", args.year
print "all", all
print "unique", unique
print "double", all - unique
