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

from Analysis.Tools.WeightInfo           import WeightInfo

# Default Parameter
loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                                help="Log level for logging")
argParser.add_argument('--plotFile',           action='store',      default='all')
argParser.add_argument('--selection',          action='store',      default='dilepOS-pTG20-nPhoton1p-offZSFllg-offZSFll-mll40-nJet2p-nBTag1p')
argParser.add_argument('--small',              action='store_true',                                                                                  help='Run only on a small subset of the data?', )
argParser.add_argument('--normalize',          action='store_true', default=False,                                                                   help="Normalize yields" )
argParser.add_argument('--order',              action='store',      default=2,                                                                       help='Polynomial order of weight string (e.g. 2)')
argParser.add_argument('--parameters',         action='store',      default=['ctZI', '4', 'ctWI', '4', 'ctZ', '4', 'ctW', '4'], type=str, nargs='+', help = "argument parameters")
args = argParser.parse_args()

# Samples
from TTGammaEFT.Samples.genTuples_TTGamma_EFT_postProcessed      import *

#signalSample = TTG_SingleLeptFromT_1L_test_EFT
signalSample = TTG_SemiLep_4WC_ref
subdir       = signalSample.name

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if len(args.parameters) < 2: args.parameters = None

if args.small:     subdir += "_small"
if args.normalize: subdir += "_normalize"

# Text on the plots
colors = [ ROOT.kRed+1, ROOT.kGreen+2, ROOT.kOrange+1, ROOT.kViolet+9, ROOT.kSpring-7, ROOT.kRed+2 ]

params = []
if args.parameters:
    coeffs = args.parameters[::2]
    str_vals = args.parameters[1::2]
    vals = list( map( float, str_vals ) )
    for i_param, (coeff, val, str_val) in enumerate(zip(coeffs, vals, str_vals)):
        params.append( {
            'legendText': ' = '.join([coeff,str_val]).replace("c", "C_{").replace(" =", "} =").replace("I", "}^{[Im]"),
            'WC' : { coeff:val },
            'color' : colors[i_param],
            })

params.append( {'legendText':'SM', 'WC':{}, 'color':ROOT.kBlack} )

if args.parameters: wcString = "_".join(args.parameters).replace('.','p').replace('-','m')
else: wcString = "SM"

def checkReferencePoint( sample ):
    ''' check if sample is simulated with a reference point
    '''
    return pickle.load(file(sample.reweight_pkl))['ref_point'] != {}

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
        plot_directory_ = os.path.join( plot_directory, 'genPlots', subdir, args.selection, wcString, mode, "log" if log else "lin" )

        for plot in plots:
            if not max(l[0].GetMaximum() for l in plot.histos): 
                continue # Empty plot
            postFix = " (legacy)"
            extensions_ = ["pdf", "png", "root"] if mode in ['all', 'SF', 'mue'] else ['png']

            plotting.draw( plot,
	                       plot_directory = plot_directory_,
                           extensions = extensions_,
                           ratio = {'yRange': (0.3, 1.7), 'histos':[(i,len(params)-1) for i in range(0, len(params))], 'texY':'Ratio'},
#	                       ratio = None,
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

def get_reweight( param , sample_ ):

    def reweightRef( event, sample ):
        return w.get_weight_func( **param['WC'] )( event, sample ) * event.ref_weight

    def reweightNoRef( event, sample ):
        return event.weight

    return reweightRef if checkReferencePoint( sample_ ) else reweightNoRef

genJetVarString      = "pt/F,eta/F,phi/F,isMuon/I,isElectron/I,isPhoton/I,matchBParton/I"
genJetVars           = [ item.split("/")[0] for item in genJetVarString.split(",") ]

genTopVarString      = "pt/F,eta/F,phi/F,mass/F"
genTopVars           = [ item.split("/")[0] for item in genTopVarString.split(",") ]

genLeptonVarString   = "pt/F,eta/F,phi/F,pdgId/I,motherPdgId/I,grandmotherPdgId/I"
genLeptonVars        = [ item.split("/")[0] for item in genLeptonVarString.split(",") ]

genPhotonVarString   = "pt/F,phi/F,eta/F,mass/F,motherPdgId/I,relIso04_all/F,photonLepdR/F,photonJetdR/F"
genPhotonVars        = [ item.split("/")[0] for item in genPhotonVarString.split(",") ]

# Read variables and sequences
read_variables  = ["weight/F",
                   "nGenBJet/I",
                   "nGenMuon/I",
                   "nGenElectron/I",
                   "GenMET_pt/F", "GenMET_phi/F",
                   "nGenLepton/I",
                   "GenLepton[%s]"   %genLeptonVarString,
                   "nGenPhoton/I",
                   "GenPhoton[%s]"   %genPhotonVarString,
                   "nGenJet/I",
                   "GenJet[%s]"      %genJetVarString,
                   "nGenTop/I",
                   "GenTop[%s]"      %genTopVarString,
                   "mll/F", "mllgamma/F",
                  ]

read_variables += [ "GenBj0_" + var for var in genJetVarString.split(",") ]
read_variables += [ "GenBj1_" + var for var in genJetVarString.split(",") ]

read_variables_EFT = [
                      "ref_weight/F",
                      VectorTreeVariable.fromString('p[C/F]', nMax=100)
                     ]

# Sequence
sequence = []

w         = WeightInfo( signalSample.reweight_pkl )
w.set_order( int(args.order) )
variables = w.variables

lumi_scale = 136.6

signals = []
# Sample definition
for i, param in enumerate( params ):
    sample                = copy.deepcopy( signalSample )
    sample.params         = param
    if param["legendText"] == "SM":
        sample.style = styles.lineStyle( param["color"], width=3  )
    else:
        sample.style = styles.lineStyle( param["color"], width=2, dashed=True  )
    sample.texName        = param["legendText"]
    sample.weight         = get_reweight( param, sample )
    sample.read_variables = read_variables_EFT
    sample.scale          = lumi_scale
    signals.append( sample )

stackList  = [ [s] for s in signals ]
stack      = Stack( *stackList )

if args.small:
    for sample in stack.samples:
        sample.normalization=1.
        sample.reduceFiles( factor=10 )
        sample.scale /= sample.normalization

weight_ = lambda event, sample: 1

# Use some defaults (set defaults before you create/import list of Plots!!)
Plot.setDefaults( stack=stack, weight=staticmethod( weight_ ), selectionString=cutInterpreter.cutString( args.selection ), addOverFlowBin='upper' )

# Import plots list (AFTER setDefaults!!)
plotListFile = os.path.join( os.path.dirname( os.path.realpath( __file__ ) ), 'plotLists', args.plotFile + '.py' )
if not os.path.isfile( plotListFile ):
    logger.info( "Plot file not found: %s", plotListFile )
    sys.exit(1)

plotModule = imp.load_source( "plotLists", os.path.expandvars( plotListFile ) )
from plotLists import plotListDataMC as plotList

# Loop over channels
yields   = {}
allPlots = {}
#allModes = [ 'mumu', 'mue', 'ee' ]
allModes = [ 'all' ]

for index, mode in enumerate( allModes ):
    logger.info( "Computing plots for mode %s", mode )

    yields[mode] = {}

    # always initialize with [], elso you get in trouble with pythons references!
    plots  = []
    plots += plotList
    if mode != 'all': plots += [ getYieldPlot( index ) ]

    # Define 2l selections
    leptonSelection = cutInterpreter.cutString( mode )

    for sample in signals: sample.setSelectionString( [ leptonSelection ] )

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

exit()

# Add the different channels into SF and all
for mode in [ "SF", "all" ]:
    yields[mode] = {}

    for plot in allPlots['mumu']:
        for pl in ( p for p in ( allPlots['ee'] if mode=="SF" else allPlots["mue"] ) if p.name == plot.name ):  #For SF add EE, second round add EMu for all
            for i, j in enumerate( list( itertools.chain.from_iterable( plot.histos ) ) ):
                j.Add( list( itertools.chain.from_iterable( pl.histos ) )[i] )

    drawPlots( allPlots['mumu'], mode )

