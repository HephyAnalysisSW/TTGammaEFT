#!/usr/bin/env python
''' Analysis script for plots with EFT reweighting
'''

# Standard imports
import ROOT, os, copy, pickle
ROOT.gROOT.SetBatch(True)
from math                               import pi, sqrt

# RootTools
from RootTools.core.standard            import *

# Internal Imports
from TTGammaEFT.Tools.user              import plot_directory, cache_directory
from TTGammaEFT.Tools.cutInterpreter    import cutInterpreter
from TTGammaEFT.Tools.TriggerSelector   import TriggerSelector
from TTGammaEFT.Tools.objectSelection   import photonSelector

from Analysis.Tools.metFilters          import getFilterCut
from Analysis.Tools.helpers             import getCollection, deltaR

# EFT Reweighting
from Analysis.Tools.WeightInfo          import WeightInfo

# Default Parameter
loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                               help="Log level for logging")
argParser.add_argument('--plot_directory',     action='store',      default='myFirstEFTPlots')
argParser.add_argument('--selection',          action='store',      default='nLepTight1-nLepVeto1-nJet4p-nBTag1p-nPhoton1')
argParser.add_argument('--small',              action='store_true',                                                                                  help='Run only on a small subset of the data?', )
argParser.add_argument('--year',               action='store',      default=2016,   type=int,  choices=[2016,2017,2018],                             help="Which year to plot?")
argParser.add_argument('--mode',               action='store',      default="all", type=str, choices=["genMu", "genE", "all"],                       help="plot lepton mode" )
argParser.add_argument('--normalize',          action='store_true', default=False,                                                                   help="Normalize yields" )
argParser.add_argument('--order',              action='store',      default=2, type=int,                                                             help='Polynomial order of weight string (e.g. 2)')
argParser.add_argument('--parameters',         action='store',      default=['ctZI', '2', 'ctWI', '2', 'ctZ', '2', 'ctW', '2'], type=str, nargs='+', help = "argument parameters")
args = argParser.parse_args()

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small:           args.plot_directory += "_small"
if args.normalize:       args.plot_directory += "_normalize"


# load and define the EFT sample
from TTGammaEFT.Samples.genTuples_TTGamma_EFT_postProcessed      import *
eftSample = TTG_4WC_ref

# define some colors
colors = [ ROOT.kRed+1, ROOT.kGreen-2, ROOT.kOrange+1, ROOT.kAzure+4 ]

# format the EFT parameter you want to plot
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

# for shape plots normalize each EFT shape to the SM shape
if args.normalize:
    scaling = { i:len(params)-1 for i, _ in enumerate(params) }

if args.parameters: wcString = "_".join(args.parameters).replace('.','p').replace('-','m')
else: wcString = "SM"

# settings for eft reweighting
w = WeightInfo( eftSample.reweight_pkl )
w.set_order( args.order )
variables = w.variables

def checkReferencePoint( sample ):
    ''' check if sample is simulated with a reference point
    '''
    return pickle.load(file(sample.reweight_pkl))['ref_point'] != {}

# function to get the EFT weight with or without reference point
def get_reweight( param , sample_ ):
    def reweightRef( event, sample ):
        return w.get_weight_func( **param['WC'] )( event, sample ) * event.ref_weight
    def reweightNoRef( event, sample ):
        return event.weight
    return reweightRef if checkReferencePoint( sample_ ) else reweightNoRef

# Text on the plots
def drawObjects( lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    line = (0.65, 0.95, '%3.1f fb{}^{-1} (13 TeV)' % lumi_scale)
    lines = [
      (0.15, 0.95, 'CMS #bf{#it{Simulation Preliminary}}'), 
      line
    ]
    return [tex.DrawLatex(*l) for l in lines] 


# Default plotting function
def drawPlots( plots ):
    logger.info( "Plotting mode: %s"%args.mode )
    for plot in plots:

        # check if the plot is filled
        if not max(l[0].GetMaximum() for l in plot.histos):
            logger.info( "Empty plot!" )
            continue # Empty plot

        # plot in log scale and linear scale
        for log in [True, False]:
            plot_directory_ = os.path.join( plot_directory, 'genPlotsEFT', str(args.year), args.plot_directory, args.selection, args.mode, "log" if log else "lin" )
            plotting.draw( plot,
                           plot_directory = plot_directory_,
                           ratio = {'yRange': (0.5, 1.5), 'histos':[(i,len(params)-1) for i in range(0, len(params))], 'texY':'EFT/SM'},
                           logX = False, logY = log, sorting = True,
                           yRange = (0.001, "auto"),
                           scaling = scaling if args.normalize else {},
                           legend = [ (0.2,0.88-0.025*sum(map(len, plot.histos)),0.9,0.88), 4],
                           drawObjects = drawObjects( lumi_scale ),
                           copyIndexPHP = True,
                          )


# add here variables that should be read by the samples
read_variables = ["weight/F", "ref_weight/F",
                  VectorTreeVariable.fromString('p[C/F]', nMax=100),
                  'nGenElectronCMSUnfold/I', 'nGenMuonCMSUnfold/I', 'nGenLeptonCMSUnfold/I', 'nGenPhotonCMSUnfold/I', 'nGenBJetCMSUnfold/I', 'nGenJetsCMSUnfold/I',
                 ]

read_variables += map( lambda var: "GenPhotonCMSUnfold0_"  + var, ["pt/F","eta/F","phi/F"] )

def sequenceExample( event, sample ):
    # example of how to calculate your own variables
    event.myVariable = 1


# add functions to calculate your own variables here
# this is slow, use it only if needed
sequence = [ sequenceExample ]

# MC samples need to be corrected by certain scale factors to correct e.g. detector effects. Define the "weight" here:
mcWeight = lambda event, sample: event.reweightL1Prefire*event.reweightPU*event.reweightLeptonTightSF*event.reweightLeptonTrackingTightSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF
# a weight for all samples incluuding data is defined here
weight = lambda event, sample: event.weight

# Scale the histograms by the luminosity taken by CMS in each year
if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74

# settings for MC Samples
signals = []
# Sample definition
for i, param in enumerate( params ):
    # copy the sample for each EFT parameter
    sample                = copy.deepcopy( eftSample )
    sample.params         = param

    # change the style of the MC sample
    if param["legendText"] == "SM":
        sample.style = styles.lineStyle( param["color"], width=3  ) # let the standard model histo be black and solid
    else:
        sample.style = styles.lineStyle( param["color"], width=3, dashed=True  ) # EFT histos be dashed and colored

    # add here the text in the legend
    sample.texName        = param["legendText"]
    # add the predefined weight to the samples
    sample.weight         = get_reweight( param, sample )
    # add here variables that should be read only for MC samples
    sample.read_variables = read_variables
    # you can scale the histograms of each sample by defining sample.scale (don't scale data)
    # Scale the MC histograms by the luminosity taken by CMS in each year
    sample.scale          = lumi_scale
    signals.append( sample )

#define the Stack
stackList  = [ [s] for s in signals ]
stack      = Stack( *stackList )

# if you want to check your plots you can run only on a sub-set of events, we reduce the number of events here
# this gives you a wrong plot, but you can check if everything looks ok and works
if args.small:
    for sample in stack.samples:
        sample.normalization=1.
        sample.reduceFiles( factor=20 )
        sample.scale /= sample.normalization

# define your plot selection via the python option --selection
preSelection = cutInterpreter.cutString( args.selection + "-" + args.mode )
# set default settings for your plots (selection, do you want an overflow bin?)
Plot.setDefaults(   stack=stack, selectionString=preSelection, addOverFlowBin="upper" )

# define a list of plots here
plotList = []

plotList.append( Plot(
    name      = 'GenPhotonCMSUnfold0_pt', # name of the plot file
    texX      = 'gen p_{T}(#gamma_{0}) (GeV)', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.GenPhotonCMSUnfold0_pt, # variable to plot
    binning   = [ 20, 20, 120 ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'GenPhotonCMSUnfold0_eta',
    texX      = 'gen #eta(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenPhotonCMSUnfold0_eta,
    binning   = [ 10, -1.5, 1.5 ],
))

plotList.append( Plot(
    name      = 'GenPhotonCMSUnfold0_phi',
    texX      = 'gen #phi(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenPhotonCMSUnfold0_phi,
    binning   = [ 10, -pi, pi ],
))

# plot with self-calculated variable
plotList.append( Plot(
    name      = 'myVariable',
    texX      = 'myVariable',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.myVariable,
    binning   = [ 1, 0, 1 ],
))

# fill the histograms here, depending on the selection this can take a while
# here you also say which plots you want to fill (plots), which variables they need (read_variables) and which additionl functions to call for each event (sequence)
plotting.fill( plotList, read_variables=read_variables, sequence=sequence )

# print the plots
drawPlots( plotList )

