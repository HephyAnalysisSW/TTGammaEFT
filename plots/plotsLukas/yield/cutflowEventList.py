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
argParser.add_argument('--logLevel',            action='store',      default='INFO', nargs='?', choices=loggerChoices,                  help="Log level for logging")
argParser.add_argument('--selection',           action='store',      default='nLepTight1-mu-nLepVeto1-nJet4p-nBTag1p-nPhoton1')
argParser.add_argument('--sample',              action='store',      default='ttg')
argParser.add_argument('--small',               action='store_true',                                                                    help='Run only on a small subset of the data?', )
argParser.add_argument('--noOverlap',           action='store_true',                                                                    help='Run only on a small subset of the data?', )
argParser.add_argument('--year',                action='store',      default="2016",   type=str,  choices=["2016","2017","2018","RunII"],               help="which year?")
args = argParser.parse_args()

if args.year != "RunII": args.year = int(args.year)

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.sample == "ttg":
    from TTGammaEFT.Samples.nanoTuples_Sync_semilep_postProcessed      import TTG_sync_16 as sample
elif args.sample == "ttbar":
    from TTGammaEFT.Samples.nanoTuples_Sync_semilep_postProcessed      import TT_sync_16  as sample
elif args.sample == "dy":
    from TTGammaEFT.Samples.nanoTuples_Sync_semilep_postProcessed      import DY_LO_sync_16  as sample

category = {
    "photonCatMagic0":"genuine",
    "photonCatMagic1":"hadronic",
    "photonCatMagic2":"misID",
    "photonCatMagic3":"fake",
    "photonCatMagic4":"PU",
}

filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True, skipVertexFilter=False )

if "invl" in args.selection.lower(): trigger = "triggeredInvIso==1"
else:                                trigger = "triggered==1"

if args.noOverlap:
    selection = "&&".join( [ cutInterpreter.cutString( args.selection ), filterCutMc, trigger, "pTStitching==1" ] )
else:
    selection = "&&".join( [ cutInterpreter.cutString( args.selection ), filterCutMc, trigger, "pTStitching==1", "overlapRemoval==1" ] )
print selection
    
# Define a reader
r = sample.treeReader( \
    variables = [ TreeVariable.fromString("event/l"), TreeVariable.fromString('run/i'), TreeVariable.fromString('luminosityBlock/i') ],
    selectionString = selection,
    )

r.start()
    
selection = args.selection
for key, value in category.items():
    selection = selection.replace(key, value)

filepath = "logs/%i_%s_EventList_%s%s.dat"%(args.year,sample.name,selection, "_noOR" if args.noOverlap else "")
filepath = filepath.replace("photonAdvcat0","genuine")
filepath = filepath.replace("photonAdvcat1","hadronics")
filepath = filepath.replace("photonAdvcat2","misID")
filepath = filepath.replace("photonAdvcat3","fakes")
filepath = filepath.replace("photonAdvcat4","PUphotons")

with open(filepath, "w") as f:
    while r.run():
        run, lumi, evt = r.event.run, r.event.luminosityBlock, r.event.event
        f.write(str(run) + "," + str(lumi) + "," + str(evt) + "\n")

