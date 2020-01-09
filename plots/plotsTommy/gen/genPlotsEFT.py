#!/usr/bin/env python
''' Analysis script for standard plots
'''

# Standard imports
import ROOT, os, imp, sys, copy
ROOT.gROOT.SetBatch(True)
import itertools
import pickle
from math                               import isnan, ceil, pi

# RootTools
from RootTools.core.standard            import *

# Internal Imports
from TTGammaEFT.Tools.user              import plot_directory
from TTGammaEFT.Tools.genCutInterpreter import cutInterpreter

from Analysis.Tools.WeightInfo          import WeightInfo

# Default Parameter
loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                     help="Log level for logging")
argParser.add_argument('--selection',          action='store',      default='trilepTWZ')
argParser.add_argument('--small',              action='store_true',                                                                       help='Run only on a small subset of the data?', )
argParser.add_argument('--normalize',          action='store_true', default=False,                                                        help="Normalize yields" )
argParser.add_argument('--order',              action='store',      default=2,                                                             help='Polynomial order of weight string (e.g. 2)')
#argParser.add_argument('--parameters', action='store', default=['cu', '0.66666', 'cu', '1','cu', '2'], type=str, nargs='+', help = "argument parameters")
argParser.add_argument('--parameters',         action='store',      default=['cpt', '2', 'ctp', '2'], type=str, nargs='+', help = "argument parameters")

args = argParser.parse_args()

# Samples
from TTGammaEFT.Samples.genTuples_TWZ_postProcessed import *

#signalSample = tWZ0j_rwgt_dim6top_GEN
signalSample = tWZ01j_rwgt_dim6top_GEN
subdir       = signalSample.name

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if len(args.parameters) < 2: args.parameters = None

if args.small:           subdir += "_small"
if args.normalize:       subdir += "_normalize"


# Text on the plots
colors = [ ROOT.kRed+1, ROOT.kGreen+1, ROOT.kOrange+1, ROOT.kViolet+1, ROOT.kSpring-7, ROOT.kRed+7, ROOT.kGreen+3, ROOT.kOrange+2, ROOT.kViolet-1, ROOT.kAzure-4 ]

params = []
if args.parameters:
    coeffs = args.parameters[::2]
    str_vals = args.parameters[1::2]
    vals = list( map( float, str_vals ))
    for i_param, (coeff, val, str_val) in enumerate(zip(coeffs, vals, str_vals)):
        params.append( {
            #'legendText': ' = '.join([coeff,str_val]),
            'legendText': ' = '.join([coeff,str_val]).replace("c", "C_{").replace(" =", "} =").replace("I", "}^{[Im]"),
            'WC': { coeff:val },
            'color': colors[i_param],
            })

params.append( {'legendText':'SM', 'WC':{}, 'color':ROOT.kBlack} )

if args.parameters: wcString = "_".join(args.parameters).replace('.','p').replace('-','m')
else: wcString = "SM"

def checkReferencePoint( sample ):
    # check if sample is simulated with a reference point
    return pickle.load(file(sample.reweight_pkl))['ref_point'] != {}

# Text on the plots
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

if args.normalize:
    scaling = { i:len(params)-1 for i, _ in enumerate(params) }

# Plotting
def drawPlots( plots, mode ):
    for log in [False, True]:
        plot_directory_ = os.path.join( plot_directory, 'analysisPlots', subdir, args.selection, wcString, mode, "log" if log else "lin" )
 
        for plot in plots:
            if not max(l[0].GetMaximum() for l in plot.histos): 
                continue # Empty plot
            postFix = " (legacy)"
            extensions_ = ["pdf", "png", "root"] if mode in ['all', 'SF', 'mue'] else ['png']

            plotting.draw( plot,
                           plot_directory = plot_directory_,
                           extensions = extensions_,
                           ratio = {'yRange': (0.3, 1.7), 'histos':[(i,len(params)-1) for i in range(0, len(params))], 'texY':'Ratio'},
                           logX = False, logY = log, sorting = True,
                           yRange = (0.03, "auto") if log else (0.001, "auto"),
                           scaling = scaling if args.normalize else {},
                           legend = [ (0.18,0.85-0.03*sum(map(len, plot.histos)),0.9,0.88), 2],
                           drawObjects = drawObjects( lumi_scale ) if not args.normalize else drawObjects( lumi_scale ),
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

def get_reweight( param, sample_ ):
    
    def reweightRef( event, sample ):
       # print param['WC'], w.get_weight_string( **param['WC'] )
        return w.get_weight_func( **param['WC'] )( event, sample ) * event.ref_weight
    
    def reweightNoRef( event, sample ):
        return event.weight
    
    return reweightRef if checkReferencePoint( sample_ ) else reweightNoRef


genLeptonVarString  = "pt/F,phi/F,eta/F,pdgId/I,motherPdgId/I,grandmotherPdgId/I"
genJetVarString     = "pt/F,phi/F,eta/F,isMuon/I,isElectron/I,matchBParton/I"

read_variables = ["weight/F",
                  "nGenBJet/I",
                  "nGenMuon/I",
                  "nGenElectron/I",
                  "GenMET_pt/F", "GenMET_phi/F",
                  "nGenLepton/I",
                  "GenLepton[%s]" %genLeptonVarString,                    
                  "nGenJet/I",
                  "GenJet[%s]"    %genJetVarString,                  
                  "mll/F", "ht/F",
                 ]

read_variables += [ "GenBj0_" + var for var in genJetVarString.split(",") ]
read_variables += [ "GenBj1_" + var for var in genJetVarString.split(",") ]

read_variables_EFT = [
                      "ref_weight/F",
                      VectorTreeVariable.fromString('p[C/F]', nMax=100)
                     ]

# Sequence
sequence = [ ]

w = WeightInfo( signalSample.reweight_pkl )
w.set_order( int(args.order) )
variables = w.variables

lumi_scale = 136.6


signals = []
# Signal definition
for i, param in enumerate( params ):
    sample                = copy.deepcopy( signalSample )
    sample.params         = param
    if param["legendText"] == "SM":
        sample.style = styles.lineStyle( param["color"], width=3 )
    else:
        sample.style = styles.lineStyle( param["color"], width=2, dashed=True )
    sample.texName        = param["legendText"]
    sample.weight         = get_reweight ( param, sample )
    sample.read_variables = read_variables_EFT
    sample.scale          = lumi_scale
    signals.append ( sample )

stackList = [ [s] for s in signals ]
stack     = Stack ( *stackList )

if args.small:
    for sample in stack.samples:
        sample.normalization=1.
        sample.reduceFiles( factor=20 )
        sample.scale /= sample.normalization

weight_ = lambda event, sample: 1

# Use some defaults (set defaults before you create/import list of Plots!!)
Plot.setDefaults( stack=stack, weight=staticmethod( weight_ ), selectionString=cutInterpreter.cutString( args.selection ), addOverFlowBin='upper' )

yields = {}
allPlots = {}
addPlots = []
allModes = [ 'all' ]

addPlots.append( Plot(
    name      = 'GenMET_pt',
    texX      = 'E^{T}_{miss} (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "GenMET_pt/F" ),
    binning   = [ 20, 0, 200 ],
))

addPlots.append( Plot(
    name      = 'genLepton0_pt',
    texX      = 'p_{T}(l_{0}) (GeV)',
    texY      = 'Number of Events', 
    attribute = lambda event, sample: event.GenLepton_pt[0],
    binning   = [ 20, 0 , 300 ], 
))

addPlots.append( Plot(
    name      = 'genLepton0_eta',
    texX      = '#eta(l_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenLepton_eta[0],
    binning   = [ 20, -6, 6 ],
))

addPlots.append( Plot(
    name      = 'genLepton0_pdgid',
    texX      = 'pdgId(l_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenLepton_pdgId[0],
    binning   = [ 30, -15, 15 ],
))

addPlots.append( Plot(
    name      = 'genLepton1_pt',
    texX      = 'p_{T}(l_{1}) (GeV)',
    texY      = 'Number of Events',  
    attribute = lambda event, sample: event.GenLepton_pt[1],
    binning   = [ 20, 0 , 300 ],              
))

addPlots.append( Plot(
    name      = 'genLepton1_eta',
    texX      = '#eta(l_{1})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenLepton_eta[1],
    binning   = [ 20, -6, 6 ],
))

addPlots.append( Plot(
    name      = 'genLepton1_pdgid',
    texX      = 'pdgId(l_{1})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenLepton_pdgId[1],
    binning   = [ 30, -15, 15 ],
))

addPlots.append( Plot(
    name      = 'genLepton2_pt',
    texX      = 'p_{T}(l_{2}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenLepton_pt[2],
    binning   = [ 20, 0 , 300 ],
))

addPlots.append( Plot(
    name      = 'genLepton2_eta',
    texX      = '#eta(l_{2})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenLepton_eta[2],
    binning   = [ 20, -6, 6 ],
))

addPlots.append( Plot(
    name      = 'genLepton2_pdgid',
    texX      = 'pdgId(l_{2})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenLepton_pdgId[2],
    binning   = [ 30, -15, 15 ],
))

addPlots.append( Plot(
    name      = 'genJet0_pt',
    texX      = 'p_{T}(j_{0}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenJet_pt[0],
    binning   = [ 20, 0, 600 ],
))

addPlots.append( Plot(
    name      = 'genJet0_eta',
    texX      = '#eta(l_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenJet_eta[0],
    binning   = [ 20, -6, 6 ],
))

addPlots.append( Plot(
    name      = 'genJet1_pt',
    texX      = 'p_{T}(j_{1}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenJet_pt[1],
    binning   = [ 20, 0, 600 ],
))

addPlots.append( Plot(
    name      = 'genJet1_eta',
    texX      = '#eta(l_{1})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenJet_eta[1],
    binning   = [ 20, -6, 6 ],
))
addPlots.append( Plot(
    name      = 'genJet2_pt',
    texX      = 'p_{T}(j_{2}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenJet_pt[2],
    binning   = [ 20, 0, 600 ],
))

addPlots.append( Plot(
    name      = 'genJet2_eta',
    texX      = '#eta(l_{2})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenJet_eta[2],
    binning   = [ 20, -6, 6 ],
))

addPlots.append( Plot(
    name      = 'genJet3_pt',
    texX      = 'p_{T}(j_{3}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenJet_pt[3],
    binning   = [ 20, 0, 600 ],
))

addPlots.append( Plot(
    name      = 'genJet3_eta',
    texX      = '#eta(l_{3})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenJet_eta[3],
    binning   = [ 20, -6, 6 ],
))

addPlots.append( Plot(
    name      = 'nGenJet',
    texX      = 'N_{jets}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nGenJet/I" ),
    binning   = [ 10, 0, 10 ],
))

addPlots.append( Plot(
    name      = 'nGenBJet',
    texX      = 'N_{bJet}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nGenBJet/I" ),
    binning   = [ 4, 0, 4 ],
))

addPlots.append( Plot(
    name      = 'ht',
    texX      = 'H_{T} (GeV)',
    texY      = 'Number of Events / 25 GeV',
    attribute = TreeVariable.fromString( "ht/F" ),
    binning   = [ 120, 0, 3000 ],
))

addPlots.append( Plot(
    name      = 'nGenLepton',
    texX      = 'N_{l}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nGenLepton/I" ),
    binning   = [ 4, 0, 4 ],
))

addPlots.append( Plot(
    name      = 'nGenElectron',
    texX      = 'N_{e}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nGenElectron/I" ),
    binning   = [ 4, 0, 4 ],
))

addPlots.append( Plot(
    name      = 'nGenMuon',
    texX      = 'N_{#mu}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nGenMuon/I" ),
    binning   = [ 4, 0, 4 ],
))


for index, mode in enumerate( allModes ):
    logger.info( "Computing plots for mode %s", mode )

    yields[mode] = {}

    # always initialize with [], elso you get in trouble with pythons references!
    plots  = []
    plots += addPlots
    if mode != 'all': plots += [getYieldPlot( index ) ]

    # Define 2l selections
    leptonSelection = cutInterpreter.cutString( mode )

    for sample in signals: sample.setSelectionString( [leptonSelection ] )

    plotting.fill( plots, read_variables=read_variables, sequence=sequence )

    # Get normalization yields from yield histogram
    for plot in plots:
        if plot.name != "yield": continue
        for i, l in enumerate( plot.histos ):
            for j, h in enumerate( l ):
                h.GetXaxis().SetBinLabel( 1, "#mu#mu" )
                h.GetXaxis().SetBinLabel( 2, "#mue" )
                h.GetXaxis().SetBinLabel( 3, "ee" )

    logger.info( "Plotting mode %s", mode )
    allPlots[mode] = copy.deepcopy(plots) # deep copy for creating SF/all plots afterwards!
    drawPlots( allPlots[mode], mode )
exit ()






    


