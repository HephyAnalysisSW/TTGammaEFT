#!/usr/bin/env python
''' Analysis script for standard plots
'''

# Standard imports
import ROOT, os, imp, sys, copy
ROOT.gROOT.SetBatch(True)

import itertools
import pickle
from math                                import isnan, ceil, pi

# RootTools
from RootTools.core.standard             import *

# Internal Imports
from TTGammaEFT.Tools.user               import plot_directory
from TTGammaEFT.Tools.genCutInterpreter  import cutInterpreter

from Analysis.Tools.helpers              import getCollection, deltaR, deltaR2
from Analysis.Tools.overlapRemovalTTG import getParentIds

# Default Parameter
loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                                help="Log level for logging")
argParser.add_argument('--plot_directory',     action='store',      default='gen')
argParser.add_argument('--plotFile',           action='store',      default='all')
argParser.add_argument('--selection',          action='store',      default='all')
argParser.add_argument('--version',            action='store',      default='v2')
argParser.add_argument('--small',              action='store_true',                                                                                  help='Run only on a small subset of the data?', )
argParser.add_argument('--normalize',          action='store_true', default=False,                                                                   help="Normalize yields" )
args = argParser.parse_args()


def printGDirectory():
    print ">>> gDirectory.GetName()\n%s" % ROOT.gDirectory.GetName()
    print ">>> gDirectory.pwd()"
    ROOT.gDirectory.pwd()
    print ">>> gDirectory.ls()"
    ROOT.gDirectory.ls()
    print

#topDir = ROOT.gDirectory.GetDirectory( ROOT.gDirectory.GetPath() )
#print topDir.ls()
#exit()

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

# Samples
#from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed      import ZG_16
#from Samples.nanoAOD.Summer16_private_legacy_v1 import ZGToLLG as ZG_16
#from Samples.nanoAOD.Summer16_private_legacy_v1 import ZGTo2LG_ext as ZG_16
#from Samples.nanoAOD.Summer16_private_legacy_v1 import ZGToLLG_lowMLL as ZG_16
from Samples.nanoAOD.Fall17_private_legacy_v1 import ZGToLLG_lowMLL as ZG_16

def drawObjects( lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS #bf{#it{Simulation Preliminary}}'), 
      (0.65, 0.95, '%3.1f fb{}^{-1} (13 TeV)' % lumi_scale)
    ]
    return [tex.DrawLatex(*l) for l in lines] 

# Read variables and sequences
read_variables  = [
#                   "weight/F",
                   "nGenPart/I",
                   "GenPart[pt/F,pdgId/I,genPartIdxMother/I]",
                  ]


def getGenLeps( event, sample ):
    gPart  = getCollection( event, 'GenPart', ["pt","pdgId","genPartIdxMother"], 'nGenPart' )
    GenPhoton  = filter( lambda l: abs(l['pdgId']) == 22 and l["genPartIdxMother"] >= 0 and l["genPartIdxMother"] < len(gPart), gPart )
    GenPhoton  = filter( lambda l: not 11 in map( abs, getParentIds( gPart[l["genPartIdxMother"]], gPart)) and not 13 in map( abs, getParentIds( gPart[l["genPartIdxMother"]], gPart)), GenPhoton )

    GenLep     = filter( lambda l: abs(l['pdgId']) in [11,13] and l["genPartIdxMother"] >= 0 and l["genPartIdxMother"] < len(gPart), gPart )
    GenLep     = filter( lambda l: not 15 in map( abs, getParentIds( gPart[l["genPartIdxMother"]], gPart)), GenLep )
    GenLep     = filter( lambda l: l["pt"] > 2, GenLep )
    GenLep.sort( key=lambda l: -l["pt"] )

    event.weight = len(GenLep) > 1# and len(GenPhoton) > 1
    event.genL0_pt = GenLep[0]["pt"] if len(GenLep) > 0 else -999
    event.genL1_pt = GenLep[1]["pt"] if len(GenLep) > 1 else -999

#    if event.genL0_pt < 5 and event.weight:
#        print event.genL0_pt, event.genL1_pt

sequence = [getGenLeps]

lumi_scale = 35.92

comparisonSamples = [ [ZG_16] ]


# Plotting
def drawPlots( plots ):
    for log in [True]:
        print log
        printGDirectory()
        plot_directory_ = os.path.join( plot_directory, 'comparisonPlots', "VGamma_%s"%args.version )

        for plot in plots:
            if not max(l[0].GetMaximum() for l in plot.histos): 
                continue # Empty plot
            postFix = " (legacy)"
            extensions_ = ["pdf", "png", "root"] 

            plotting.draw2D( plot,
                    plot_directory = plot_directory_,
                    extensions = extensions_,
                    #ratio = {'yRange':(0.1,1.9)},
                    logX = False, logY = False, logZ = log, #sorting = True,
                    zRange = (10, "auto"),
                    #scaling = {},
                    #legend = (0.50,0.88-0.04*sum(map(len, plot.histos)),0.9,0.88),
                    drawObjects = drawObjects( lumi_scale ),
                    copyIndexPHP = True,
            )

stack      = Stack( *comparisonSamples )

for sample in stack.samples:
    sample.scale = lumi_scale

if args.small:
    for sample in stack.samples:
        sample.normalization=1.
        sample.reduceFiles( factor=10 )
        sample.scale /= sample.normalization

weight_ = lambda event, sample: event.weight

# Use some defaults (set defaults before you create/import list of Plots!!)
Plot2D.setDefaults( stack=stack, weight=staticmethod( weight_ ), selectionString="1", histo_class = ROOT.TH2D )

allplots = []
allplots.append( Plot2D(
    name      = 'lepton_pt',
    texX      = 'p_{T}(l_{0} = e/#mu, no #tau mother)',
    texY      = 'p_{T}(l_{1} = e/#mu, no #tau mother)',
    attribute = (
      lambda event, sample: event.genL1_pt,
      lambda event, sample: event.genL0_pt,
    ),
    binning   = [20, 0, 100, 20, 0, 100],
    read_variables = read_variables,
))

plotting.fill( allplots, read_variables=read_variables, sequence=sequence, max_events=200000 )

drawPlots( allplots )
