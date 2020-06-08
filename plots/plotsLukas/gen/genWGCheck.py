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

# Colors
from TTGammaEFT.Samples.color         import color

# Internal Imports
from TTGammaEFT.Tools.user               import plot_directory
from TTGammaEFT.Tools.genCutInterpreter  import cutInterpreter

from Analysis.Tools.helpers              import getCollection, deltaR, deltaR2
from TTGammaEFT.Tools.overlapRemovalTTG import getParentIds

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
#from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed      import WG_16
#from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed      import WG_NLO_16
from Samples.nanoAOD.Summer16_private_legacy_v1 import WGToLNuG                as WG_16
from Samples.nanoAOD.Summer16_private_legacy_v1 import WGToLNuG_amcatnlo       as WG_NLO_16

WG_16.style = styles.lineStyle( color.WGamma, width=2 )
WG_16.texName = "W#gamma (LO)"
WG_16.reduceFiles( to=10 )
WG_16.name = "LO"

WG_NLO_16.style = styles.lineStyle( color.TT, width=2 )
WG_NLO_16.texName = "W#gamma (NLO)"
WG_NLO_16.reduceFiles( to=10 )
WG_NLO_16.name = "NLO"

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
                   "genWeight/F",
                   "nGenPart/I",
                   "GenPart[pt/F,pdgId/I,genPartIdxMother/I]",
                   "nGenJet/I",
                   "GenJet[pt/F]",
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

def getGenJets( event, sample ):
    GenJet  = getCollection( event, 'GenJet', ["pt"], 'nGenJet' )

    GenJet.sort( key=lambda l: -l["pt"] )
    GenJet_ptgt30     = filter( lambda j: j["pt"] >= 30, GenJet )
    GenJet_ptlt30     = filter( lambda j: j["pt"] < 30,  GenJet )

    event.nGenJet_ptgt30 = len(GenJet_ptgt30)
    event.nGenJet_ptlt30 = len(GenJet_ptlt30)
    event.nGenJet        = len(GenJet)

    event.GenJet0_pt = GenJet_ptgt30[0]["pt"] if len(GenJet_ptgt30) > 0 else -999
    event.GenJet1_pt = GenJet_ptgt30[1]["pt"] if len(GenJet_ptgt30) > 1 else -999

    event.ht_ptgt30 = sum( [ j["pt"] for j in GenJet_ptgt30 ] )
    event.ht_ptlt30 = sum( [ j["pt"] for j in GenJet_ptlt30 ] )
    event.ht        = sum( [ j["pt"] for j in GenJet ] )

    del GenJet

sequence = [getGenJets]

lumi_scale = 35.92

comparisonSamples = [ [WG_NLO_16], [WG_16] ]


# Plotting
def drawPlots( plots ):
    for log in [False, True]:
        plot_directory_ = os.path.join( plot_directory, 'genPlots', "WGamma_%s_normalized"%args.version, args.selection, "log" if log else "lin" )

        for plot in plots:
            if not max(l[0].GetMaximum() for l in plot.histos): 
                continue # Empty plot
            postFix = " (legacy)"
            extensions_ = ["pdf", "png", "root"] 

            plotting.draw( plot,
                    plot_directory = plot_directory_,
                    extensions = extensions_,
                    ratio = {'yRange': (0.1, 1.9), 'texY':'LO/NLO'},
                    logX = False, logY = log, #sorting = True,
                    scaling = { 1:0 },
                    legend = [ (0.15,0.9-0.03*sum(map(len, plot.histos)),0.9,0.9), 2 ],
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

weight_ = lambda event, sample: 0.001#event.genWeight

# Use some defaults (set defaults before you create/import list of Plots!!)
Plot.setDefaults( stack=stack, weight=staticmethod( weight_ ), selectionString=cutInterpreter.cutString(args.selection), histo_class = ROOT.TH1F )

allplots = []
allplots.append( Plot(
    name      = 'genJet0_pt',
    texX      = 'p_{T}(gen-jet_{0}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenJet0_pt,
    binning   = [ 10, 0, 300 ],
))

allplots.append( Plot(
    name      = 'genJet1_pt',
    texX      = 'p_{T}(gen-jet_{1}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenJet1_pt,
    binning   = [ 10, 0, 300 ],
))

allplots.append( Plot(
    name      = 'ht_ptgt30',
    texX      = 'gen H_{T} (p_{T} > 30 GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.ht_ptgt30,
    binning   = [ 10, 0, 300 ],
))

allplots.append( Plot(
    name      = 'ht_ptlt30',
    texX      = 'gen H_{T} (p_{T} < 30 GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.ht_ptlt30,
    binning   = [ 10, 0, 300 ],
))

allplots.append( Plot(
    name      = 'ht',
    texX      = 'gen H_{T}',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.ht,
    binning   = [ 10, 0, 300 ],
))

allplots.append( Plot(
    name      = 'nGenJet_ptgt30',
    texX      = 'N_{gen-jet} (p_{T} > 30 GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.nGenJet_ptgt30,
    binning   = [ 10, 0, 10 ],
))

allplots.append( Plot(
    name      = 'nGenJet_ptlt30',
    texX      = 'N_{gen-jet} (p_{T} < 30 GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.nGenJet_ptlt30,
    binning   = [ 10, 0, 10 ],
))

allplots.append( Plot(
    name      = 'nGenJet',
    texX      = 'N_{gen-jet}',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.nGenJet,
    binning   = [ 10, 0, 10 ],
))

plotting.fill( allplots, read_variables=read_variables, sequence=sequence, max_events=50000 )

drawPlots( allplots )
