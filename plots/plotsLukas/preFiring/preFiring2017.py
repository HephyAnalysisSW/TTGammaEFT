#!/usr/bin/env python
''' Analysis script for standard plots
'''

# Standard imports
import ROOT, os, imp, sys, copy
ROOT.gROOT.SetBatch(True)
import itertools
from math                             import isnan, ceil, pi

# RootTools
from RootTools.core.standard          import *

# Internal Imports
from TTGammaEFT.Tools.user            import plot_directory
from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter
from TTGammaEFT.Tools.Variables       import NanoVariables
from TTGammaEFT.Tools.objectSelection import isBJet
from TTGammaEFT.Tools.TriggerSelector import TriggerSelector

from Analysis.Tools.metFilters        import getFilterCut
from Analysis.Tools.helpers           import getCollection

# Default Parameter
loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                  help="Log level for logging")
argParser.add_argument('--plot_directory',     action='store',      default='80X_TTG_ppv1_v1')
argParser.add_argument('--plotFile',           action='store',      default='all')
argParser.add_argument('--selection',          action='store',      default='dilepOS-nLepVeto2-pTG20-nPhoton1p-offZSFllg-offZSFll-mll40')
argParser.add_argument('--small',              action='store_true',                                                                    help='Run only on a small subset of the data?', )
argParser.add_argument('--noData',             action='store_true', default=False,                                                     help='also plot data?')
argParser.add_argument('--signal',             action='store',      default=None,   nargs='?', choices=[None],                         help="Add signal to plot")
argParser.add_argument('--onlyTTG',            action='store_true', default=False,                                                     help="Plot only ttG")
argParser.add_argument('--normalize',          action='store_true', default=False,                                                     help="Normalize yields" )
argParser.add_argument('--triggerSelection',   action='store_true', default=False,                                                     help="apply trigger selection?" )
args = argParser.parse_args()

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small:           args.plot_directory += "_small"
if args.noData:          args.plot_directory += "_noData"
if args.signal:          args.plot_directory += "_signal_"+args.signal
if args.onlyTTG:         args.plot_directory += "_onlyTTG"
if args.normalize:       args.plot_directory += "_normalize"

# 2017 Samples
from TTGammaEFT.Samples.nanoTuples_Run2017_preFiring_postProcessed import *

# Text on the plots
def drawObjects( lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS #bf{#it{Preliminary}}'),
      (0.65, 0.95, '%3.1f fb{}^{-1} (13 TeV)' % lumi_scale),
    ]
    return [tex.DrawLatex(*l) for l in lines] 

#scaling = { i+1:0 for i in range(len(signals)) }
#scaling = { 1:0 }
scaling = { 0:1 }

# Plotting
def drawPlots( plots, mode ):
    for log in [False, True]:
        plot_directory_ = os.path.join( plot_directory, 'prefiring2017', args.plot_directory, args.selection, mode, "log" if log else "lin" )

        for plot in plots:
            if not max(l[0].GetMaximum() for l in plot.histos): 
                continue # Empty plot
#            postFix = " (unprefirable)"
#            postFix = " (legacy)"
#            if not args.noData: 
            plot.histos[0][0].style          = styles.errorStyle( ROOT.kBlue )
            plot.histos[1][0].style          = styles.errorStyle( ROOT.kBlack )
#                if mode == "all":
#                    plot.histos[1][0].legendText = "Data" + postFix
#                    plot.histos[1][0].legendText = "data" + postFix
#                if mode == "SF":
#                    plot.histos[1][0].legendText = "data" + postFix
            extensions_ = ["pdf", "png", "root"] if mode == 'all' else ['png']

            plotting.draw( plot,
	                       plot_directory = plot_directory_,
                           extensions = extensions_,
	                       ratio = {'histos':[(0,1)], 'texY': 'data / unpref.', 'yRange':(0.5,1.5)} if not args.noData else None,
	                       logX = False, logY = log, sorting = True,
	                       yRange = (0.03, "auto") if log else (0.001, "auto"),
	                       scaling = scaling if args.normalize else {},
	                       legend = [ (0.15,0.9-0.03*sum(map(len, plot.histos)),0.9,0.9), 2],
	                       drawObjects = drawObjects( lumi_scale ),
                           copyIndexPHP = True,
                         )

def getYieldPlot( index ):
    return Plot(
                name      = 'yield',
                texX      = 'yield',
                texY      = 'Number of Events',
                attribute = lambda event, sample: 0.5 + index,
                binning   = [ 3, 0, 3 ],
                )

# get nano variable lists
NanoVars         = NanoVariables( 2017 )
jetVarString     = NanoVars.getVariableString(   "Jet",    postprocessed=True, data=True, plot=True )
jetVariableNames = NanoVars.getVariableNameList( "Jet",    postprocessed=True, data=True, plot=True )
bJetVariables    = NanoVars.getVariables(        "BJet",   postprocessed=True, data=True, plot=True )
leptonVariables  = NanoVars.getVariables(        "Lepton", postprocessed=True, data=True, plot=True )
photonVariables  = NanoVars.getVariables(        "Photon", postprocessed=True, data=True, plot=True )

# Read variables and sequences
read_variables  = ["weight/F", #"ref_weight/F",
                   "PV_npvs/I", "PV_npvsGood/I",
                   "nJet/I", "nBTag/I",
                   "nJetGood/I", "nBTagGood/I",
                   "Jet[%s]"         %jetVarString,
                   "JetGood[%s]"         %jetVarString,
                   "nLepton/I","nElectron/I", "nMuon/I",
                   "nLeptonGood/I","nElectronGood/I", "nMuonGood/I",
                   "nLeptonGoodLead/I","nElectronGoodLead/I", "nMuonGoodLead/I",
                   "nLeptonTight/I", "nElectronTight/I", "nMuonTight/I",
                   "nLeptonVeto/I", "nElectronVeto/I", "nMuonVeto/I",
                   "nPhoton/I",
                   "nPhotonGood/I",
                   "MET_pt/F", "MET_phi/F", "METSig/F", "ht/F",
                   "mll/F", "mllgamma/F",
                   "mlltight/F", "mllgammatight/F",
                   "mLtight0Gamma/F",
                   "ltight0GammadR/F", "ltight0GammadPhi/F",
                   "m3/F", "m3wBJet/F",
                   "lldR/F", "lldPhi/F", "bbdR/F", "bbdPhi/F",
                   "photonJetdR/F", "photonLepdR/F", "leptonJetdR/F", "tightLeptonJetdR/F",
                   "mL0Gamma/F",  "mL1Gamma/F",
                   "l0GammadR/F", "l0GammadPhi/F",
                   "l1GammadR/F", "l1GammadPhi/F",
                   "j0GammadR/F", "j0GammadPhi/F",
                   "j1GammadR/F", "j1GammadPhi/F",
                   "unPreFirableEvent/I",
                  ]


read_variables += map( lambda var: "PhotonGood0_"  + var, photonVariables )
read_variables += map( lambda var: "PhotonGood1_"  + var, photonVariables )
read_variables += map( lambda var: "LeptonGood0_"  + var, leptonVariables )
read_variables += map( lambda var: "LeptonGood1_"  + var, leptonVariables )
read_variables += map( lambda var: "LeptonTight0_" + var, leptonVariables )
read_variables += map( lambda var: "LeptonTight1_" + var, leptonVariables )
read_variables += map( lambda var: "Bj0_"          + var, bJetVariables )
read_variables += map( lambda var: "Bj1_"          + var, bJetVariables )

def clean_Jets( event, sample ):
    allJets    = getCollection( event, 'Jet', jetVariableNames, 'nJet' )
    allJets.sort( key = lambda j: -j['pt'] )
    allJets    = list( filter( lambda j: j['cleanmask'] and j['pt']>30, allJets ) )

    looseJets  = getCollection( event, 'JetGood', jetVariableNames, 'nJetGood' )
    looseJets.sort( key = lambda j: -j['pt'] )
    looseJets  = list( filter( lambda j: j['cleanmask'], looseJets ) )

    event.nJet      = len( allJets )
    event.nJetGood  = len( looseJets )
    event.nBTag     = len( filter( lambda j: isBJet( j, tagger='DeepCSV', year=2017 ), allJets ) )
    event.nBTagGood = len( filter( lambda j: isBJet( j, tagger='DeepCSV', year=2017 ), looseJets ) )

    for var in jetVariableNames:
        for i, jet in enumerate( allJets[:2] ):
            getattr( event, "Jet_" + var )[i] = jet[var]
        for i, jet in enumerate ( looseJets[:2] ):
            getattr( event, "JetGood_" + var )[i] = jet[var]

# Sequence
sequence = [ clean_Jets ]

Run2017_noPreFiring = copy.deepcopy( Run2017 )
Run2017_noPreFiring.texName = "data (unprefirable)"
Run2017_noPreFiring.name    = "data"
Run2017_noPreFiring.scale   = 1

lumi_scale = Run2017.lumi * 0.001
stack      = Stack( [ Run2017 ], Run2017_noPreFiring )

Run2017.texName = "data"
Run2017.name    = "data"
Run2017.style = styles.errorStyle( ROOT.kBlue )#styles.fillStyle( ROOT.kOrange-3 )
Run2017.scale = 1

if args.small:
    for sample in stack.samples:
        sample.normalization=1.
        sample.reduceFiles( factor=50 )
        sample.scale /= sample.normalization

weight_ = lambda event, sample: event.weight
tr          = TriggerSelector( 2017, singleLepton=True )
triggerCond = tr.getSelection( "SingleMuon" )

# Use some defaults (set defaults before you create/import list of Plots!!)
Plot.setDefaults( stack=stack, weight=staticmethod( weight_ ), selectionString=cutInterpreter.cutString( args.selection ), addOverFlowBin='upper' )

# Import plots list (AFTER setDefaults!!)
plotListFile = os.path.join( os.path.dirname( os.path.realpath( __file__ ) ), 'plotLists', args.plotFile + '.py' )
if not os.path.isfile( plotListFile ):
    logger.info( "Plot file not found: %s", plotListFile )
    sys.exit(1)

plotModule = imp.load_source( "plotLists", os.path.expandvars( plotListFile ) )
if args.noData: from plotLists import plotListDataMC as plotList
else:           from plotLists import plotListData   as plotList

# Loop over channels
yields   = {}
allPlots = {}
allModes = [ 'mumu', 'mue', 'ee' ]

for index, mode in enumerate( allModes ):
    logger.info( "Computing plots for mode %s", mode )

    yields[mode] = {}

    # always initialize with [], elso you get in trouble with pythons references!
    plots  = []
    plots += plotList
    if mode in [ 'mumu', 'mue', 'ee']: plots += [ getYieldPlot( index ) ]

    # Define 2l selections
    leptonSelection = cutInterpreter.cutString( mode )

    Run2017_noPreFiring.setSelectionString( [ getFilterCut( 2017, isData=True, skipBadChargedCandidate=True ),  leptonSelection, "unPreFirableEvent==1"] )
    Run2017.setSelectionString( [ getFilterCut( 2017, isData=True, skipBadChargedCandidate=True ), leptonSelection ] )

    if args.triggerSelection:
        Run2017_noPreFiring.addSelectionString( triggerCond )
        Run2017.addSelectionString( triggerCond )

    plotting.fill( plots, read_variables=read_variables, sequence=sequence )

    # Get normalization yields from yield histogram
    for plot in plots:
        if plot.name != "yield": continue
        for i, l in enumerate( plot.histos ):
            for j, h in enumerate( l ):
                yields[mode][plot.stack[i][j].name] = h.GetBinContent( h.FindBin( 0.5+index ) )
                h.GetXaxis().SetBinLabel( 1, "#mu#mu" )
                h.GetXaxis().SetBinLabel( 2, "#mue" )
                h.GetXaxis().SetBinLabel( 3, "ee" )

    logger.info( "Plotting mode %s", mode )
    allPlots[mode] = copy.deepcopy(plots) # deep copy for creating SF/all plots afterwards!
    drawPlots( allPlots[mode], mode )


# Add the different channels into SF and all
for mode in [ "SF", "all" ]:
    yields[mode] = {}

    for plot in allPlots['mumu']:
        for pl in ( p for p in ( allPlots['ee'] if mode=="SF" else allPlots["mue"] ) if p.name == plot.name ):  #For SF add EE, second round add EMu for all
            for i, j in enumerate( list( itertools.chain.from_iterable( plot.histos ) ) ):
                j.Add( list( itertools.chain.from_iterable( pl.histos ) )[i] )

    drawPlots( allPlots['mumu'], mode )

