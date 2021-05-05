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

import Analysis.Tools.syncer as syncer

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
argParser.add_argument('--sample',             action='store',      default='TTG_Semilep_2WC_ref',   type=str,                                               help="Which sample to plot")
argParser.add_argument('--mode',               action='store',      default="all", type=str, choices=["genMu", "genE", "all"],                       help="plot lepton mode" )
argParser.add_argument('--normalize',          action='store_true', default=False,                                                                   help="Normalize yields" )
argParser.add_argument('--order',              action='store',      default=2, type=int,                                                             help='Polynomial order of weight string (e.g. 2)')
argParser.add_argument('--parameter',          action='store',      default='ctZ', type=str,                                                         help = "parameter to validate")
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
eftSample = eval(args.sample)

valSM = TTG_SemiLep_SM
if args.parameter == "ctZ":
    val2 = TTG_SemiLep_ctZ2
    valm1 = TTG_SemiLep_ctZm1
elif args.parameter == "ctZI":
    val2 = TTG_SemiLep_ctZI2
    valm1 = TTG_SemiLep_ctZIm1
elif args.parameter == "ctW":
    val2 = TTG_SemiLep_ctW2
    valm1 = TTG_SemiLep_ctWm1
elif args.parameter == "ctWI":
    val2 = TTG_SemiLep_ctWI2
    valm1 = TTG_SemiLep_ctWIm1



# define some colors
colors = [ ROOT.kRed+1, ROOT.kGreen-2 ]

# format the EFT parameter you want to plot
params = []
args.parameters = [args.parameter, "2", args.parameter, "-1"]
if args.parameter:
    coeffs = args.parameters[::2]
    str_vals = args.parameters[1::2]
    vals = list( map( float, str_vals ) )
    for i_param, (coeff, val, str_val) in enumerate(zip(coeffs, vals, str_vals)):
        params.append( {
            'legendText': "weighted (" + ' = '.join([coeff,str_val]).replace("c", "C_{").replace(" =", "} =").replace("I", "}^{[Im]") + ")",
            'WC' : { coeff:val },
            'color' : colors[i_param],
            })

params.append( {'legendText':'weighted (SM)', 'WC':{}, 'color':ROOT.kBlack} )

# for shape plots normalize each EFT shape to the SM shape
if args.normalize:
    scaling = { i:len(params)-1 for i, _ in enumerate(params) }

if args.parameters: wcString = "_".join(args.parameters).replace('.','p').replace('-','m')
else: wcString = "SM"

# settings for eft reweighting
w = WeightInfo( eftSample.reweight_pkl )
w.set_order( args.order )
variables = w.variables

print w.get_weight_string()

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
    line = (0.68, 0.95, '%3.1f fb^{-1} (13 TeV)' % lumi_scale)
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
            plot_directory_ = os.path.join( plot_directory, 'EFTvalidation', str(args.parameter), args.plot_directory, args.selection, args.sample, args.mode, "log" if log else "lin" )
            plotting.draw( plot,
                           plot_directory = plot_directory_,
                           ratio = {'yRange': (0.5, 1.5), 'histos':[(0,1),(2,3),(4,5)], 'texY':'weight./sim.'},
                           logX = False, logY = log, sorting = True,
                           yRange = (0.003, "auto"),
                           scaling = scaling if args.normalize else {},
                           legend = [ (0.2,0.74,0.9,0.9), 2],
                           drawObjects = drawObjects( lumi_scale ),
                           copyIndexPHP = True,
                          )


# add here variables that should be read by the samples
read_variablesEFT = [ "ref_weight/F", 
                  VectorTreeVariable.fromString('p[C/F]', nMax=100), 
                 ]

read_variables = [ "weight/F", "GenMET_pt/F", "GenMET_phi/F",  
                  'nGenElectronCMSUnfold/I', 'nGenMuonCMSUnfold/I', 'nGenLeptonCMSUnfold/I', 'nGenPhotonCMSUnfold/I', 'nGenBJetCMSUnfold/I', 'nGenJetsCMSUnfold/I',
                  'nGenJets/I', 'nGenBJet/I', 'nGenLepton/I', 'nGenMuon/I', 'nGenElectron/I', 'nGenPhoton/I', 
                  "dPhiLepGamma/F", "dPhiTopHadGamma/F", "dPhiWHadGamma/F", "dPhiTopLepGamma/F", "dPhiWLepGamma/F", "dPhiBHadGamma/F", "dPhiBLepGamma/F",
                  "dPhiBLepWLep/F", "dPhiWLepWHad/F", "dPhiBHadWHad/F", "dPhiBLepBHad/F", "dPhiTopLepTopHad/F", "dPhiLepMET/F",
                  "dRLepGamma/F", "dRTopHadGamma/F", "dRWHadGamma/F", "dRTopLepGamma/F", "dRWLepGamma/F", "dRBHadGamma/F", "dRBLepGamma/F",
                  "dRBLepWLep/F", "dRWLepWHad/F", "dRBHadWHad/F", "dRBLepBHad/F", "dRTopLepTopHad/F", "mT/F", "m3/F", "ht/F"
                 ]

genTopVarStringRead  = "pt/F,eta/F,phi/F,mass/F"
genTopVarStringWrite = genTopVarStringRead

genWVarStringRead  = "pt/F,eta/F,phi/F,mass/F,pdgId/I"
genWVarStringWrite = genWVarStringRead

genTopVarStringRead  = "pt/F,eta/F,phi/F,mass/F,pdgId/I"
genTopVarStringWrite = genTopVarStringRead

read_variables += [ VectorTreeVariable.fromString('GenTopLep[%s]'%genTopVarStringWrite, nMax=100) ]
read_variables += [ VectorTreeVariable.fromString('GenTop[%s]'%genTopVarStringWrite, nMax=100) ]
read_variables += [ VectorTreeVariable.fromString('GenTopHad[%s]'%genTopVarStringWrite, nMax=10) ]
read_variables += [ VectorTreeVariable.fromString('GenW[%s]'%genWVarStringWrite, nMax=10) ]
read_variables += [ VectorTreeVariable.fromString('GenWLep[%s]'%genWVarStringWrite, nMax=10) ]
read_variables += [ VectorTreeVariable.fromString('GenWHad[%s]'%genWVarStringWrite, nMax=10) ]
read_variables += [ VectorTreeVariable.fromString('GenBLep[%s]'%genWVarStringWrite, nMax=10) ]
read_variables += [ VectorTreeVariable.fromString('GenBHad[%s]'%genWVarStringWrite, nMax=10) ]

read_variables += map( lambda var: "GenPhotonCMSUnfold0_"  + var, ["pt/F","eta/F","phi/F"] )
read_variables += map( lambda var: "GenLeptonCMSUnfold0_"  + var, ["pt/F","eta/F","phi/F"] )
read_variables += map( lambda var: "GenJetsCMSUnfold0_"  + var, ["pt/F","eta/F","phi/F"] )
read_variables += map( lambda var: "GenJetsCMSUnfold1_"  + var, ["pt/F","eta/F","phi/F"] )
read_variables += map( lambda var: "GenJetsCMSUnfold2_"  + var, ["pt/F","eta/F","phi/F"] )
read_variables += map( lambda var: "GenBJetCMSUnfold0_"  + var, ["pt/F","eta/F","phi/F"] )
read_variables += map( lambda var: "GenBJetCMSUnfold1_" + var, ["pt/F","eta/F","phi/F"] )

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
    sample.style = styles.lineStyle( param["color"], width=3, dashed=True  ) # EFT histos be dashed and colored

    # add here the text in the legend
    sample.texName        = param["legendText"]
    # add the predefined weight to the samples
    sample.weight         = get_reweight( param, sample )
    # add here variables that should be read only for MC samples
    sample.read_variables = read_variables + read_variablesEFT
    # you can scale the histograms of each sample by defining sample.scale (don't scale data)
    # Scale the MC histograms by the luminosity taken by CMS in each year
    sample.scale          = lumi_scale
    signals.append( sample )


val2.style = styles.lineStyle( colors[0], width=3, dashed=False  ) # EFT histos be dashed and colored
val2.texName = "simulated (" + ' = '.join([args.parameter,"2"]).replace("c", "C_{").replace(" =", "} =").replace("I", "}^{[Im]") + ")"
val2.weight  = lambda event, sample: event.weight
val2.scale   = lumi_scale
val2.read_variables = read_variables
valm1.style = styles.lineStyle( colors[1], width=3, dashed=False  ) # EFT histos be dashed and colored
valm1.texName = "simulated (" + ' = '.join([args.parameter,"-1"]).replace("c", "C_{").replace(" =", "} =").replace("I", "}^{[Im]") + ")"
valm1.weight  = lambda event, sample: event.weight
valm1.scale   = lumi_scale
valm1.read_variables = read_variables
valSM.style = styles.lineStyle( ROOT.kBlack, width=3, dashed=False  ) # EFT histos be dashed and colored
valSM.texName = "simulated (SM)"
valSM.weight  = lambda event, sample: event.weight
valSM.scale   = lumi_scale
valSM.read_variables = read_variables

#define the Stack
stackList  = [ [signals[0]], [val2], [signals[1]], [valm1], [signals[2]], [valSM] ]
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
#preSelection += "&&abs(ref_weight)<100"
print preSelection
# set default settings for your plots (selection, do you want an overflow bin?)
Plot.setDefaults(   stack=stack, selectionString=preSelection )

# define a list of plots here
plotList = []

pTG_thresh = [ 20, 35, 50, 65, 80, 120, 160, 200, 260, 320, 420 ]

ptBins = Binning.fromThresholds( pTG_thresh )


#photon
plotList.append( Plot(
    name      = 'GenPhotonCMSUnfold0_pt_fit', # name of the plot file
    texX      = 'gen p_{T}(#gamma) [GeV]', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.GenPhotonCMSUnfold0_pt, # variable to plot
    binning   = ptBins,
))

plotList.append( Plot(
    name      = 'GenPhotonCMSUnfold0_pt_low', # name of the plot file
    texX      = 'gen p_{T}(#gamma) [GeV]', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.GenPhotonCMSUnfold0_pt, # variable to plot
    binning   = [ 20, 20, 120 ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'GenPhotonCMSUnfold0_pt', # name of the plot file
    texX      = 'gen p_{T}(#gamma) [GeV]', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.GenPhotonCMSUnfold0_pt, # variable to plot
    binning   = [ 20, 20, 520 ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'GenPhotonCMSUnfold0_eta',
    texX      = 'gen #eta(#gamma)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenPhotonCMSUnfold0_eta,
    binning   = [ 10, -1.5 , 1.5 ],
))

plotList.append( Plot(
    name      = 'GenPhotonCMSUnfold0_phi',
    texX      = 'gen #phi(#gamma)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenPhotonCMSUnfold0_phi,
    binning   = [ 10, -pi, pi ],
))

#Lepton
plotList.append( Plot(
    name      = 'GenLeptonCMSUnfold0_pt', # name of the plot file
    texX      = 'gen p_{T}(l) [GeV]', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.GenLeptonCMSUnfold0_pt, # variable to plot
    binning   = [ 20, 20, 600 ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'GenLeptonCMSUnfold0_eta',
    texX      = 'gen #eta(l)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenLeptonCMSUnfold0_eta,
    binning   = [ 10, -2.4, 2.4 ],
))

plotList.append( Plot(
    name      = 'GenLeptonCMSUnfold0_phi',
    texX      = 'gen #phi(l)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenLeptonCMSUnfold0_phi,
    binning   = [ 10, -pi, pi ],
))

#Jets
plotList.append( Plot(
    name      = 'GenJetsCMSUnfold0_pt', # name of the plot file
    texX      = 'gen p_{T}(j_{0}) [GeV]', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.GenJetsCMSUnfold0_pt, # variable to plot
    binning   = [ 20, 20, 1100 ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'GenJetsCMSUnfold0_eta',
    texX      = 'gen #eta(j_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenJetsCMSUnfold0_eta,
    binning   = [ 10, -2.4, 2.4 ],
))

plotList.append( Plot(
    name      = 'GenJetsCMSUnfold0_phi',
    texX      = 'gen #phi(j_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenJetsCMSUnfold0_phi,
    binning   = [ 10, -pi, pi ],
))

plotList.append( Plot(
    name      = 'GenJetsCMSUnfold1_pt', # name of the plot file
    texX      = 'gen p_{T}(j_{1}) [GeV]', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.GenJetsCMSUnfold1_pt, # variable to plot
    binning   = [ 20, 20, 700 ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'GenJetsCMSUnfold1_eta',
    texX      = 'gen #eta(j_{1})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenJetsCMSUnfold1_eta,
    binning   = [ 10, -2.4, 2.4 ],
))

plotList.append( Plot(
    name      = 'GenJetsCMSUnfold1_phi',
    texX      = 'gen #phi(j_{1})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenJetsCMSUnfold1_phi,
    binning   = [ 10, -pi, pi ],
))

plotList.append( Plot(
    name      = 'GenJetsCMSUnfold2_pt', # name of the plot file
    texX      = 'gen p_{T}(j_{2}) [GeV]', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.GenJetsCMSUnfold2_pt, # variable to plot
    binning   = [ 20, 20, 500 ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'GenJetsCMSUnfold2_eta',
    texX      = 'gen #eta(j_{2})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenJetsCMSUnfold2_eta,
    binning   = [ 10, -2.4, 2.4 ],
))

plotList.append( Plot(
    name      = 'GenJetsCMSUnfold2_phi',
    texX      = 'gen #phi(j_{2})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenJetsCMSUnfold2_phi,
    binning   = [ 10, -pi, pi ],
))

#BJets
plotList.append( Plot(
    name      = 'GenBJetCMSUnfold0_pt', # name of the plot file
    texX      = 'gen p_{T}(b_{0}) [GeV]', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.GenBJetCMSUnfold0_pt, # variable to plot
    binning   = [ 20, 20, 520 ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'GenBJetCMSUnfold0_eta',
    texX      = 'gen #eta(b_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenBJetCMSUnfold0_eta,
    binning   = [ 10, -2.4, 2.4 ],
))

plotList.append( Plot(
    name      = 'GenBJetCMSUnfold0_phi',
    texX      = 'gen #phi(b_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenBJetCMSUnfold0_phi,
    binning   = [ 10, -pi, pi ],
))

plotList.append( Plot(
    name      = 'GenBJetCMSUnfold1_pt', # name of the plot file
    texX      = 'gen p_{T}(b_{1}) [GeV]', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.GenBJetCMSUnfold1_pt, # variable to plot
    binning   = [ 20, 20, 650 ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'GenBJetCMSUnfold1_eta',
    texX      = 'gen #eta(#b_{1})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenBJetCMSUnfold1_eta if event.nGenBJetCMSUnfold > 1 else -999 ,
    binning   = [ 10, -2.4, 2.4 ],
))

plotList.append( Plot(
    name      = 'GenBJetCMSUnfold1_phi',
    texX      = 'gen #phi(b_{1})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenBJetCMSUnfold1_phi if event.nGenBJetCMSUnfold > 1 else -999 ,
    binning   = [ 10, -pi, pi ],
))

#Gen
#GenTop
plotList.append( Plot(
    name      = 'GenTop_pt[0]', # name of the plot file
    texX      = 'gen p_{T}(top_{0}) [GeV]', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.GenTop_pt[0], # variable to plot
    binning   = [ 20, 20, 900 ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'GenTop_eta',
    texX      = 'gen #eta(top_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenTop_eta[0],
    binning   = [ 10, -2.4, 2.4 ],
))

plotList.append( Plot(
    name      = 'GenTop_phi',
    texX      = 'gen #phi(top_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenTop_phi[0],
    binning   = [ 10, -pi, pi ],
))

plotList.append( Plot(
    name      = 'GenTopLep_pt[0]', # name of the plot file
    texX      = 'gen p_{T}(lept. top) [GeV]', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.GenTopLep_pt[0], # variable to plot
    binning   = [ 20, 20, 900 ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'GenTopLep_eta',
    texX      = 'gen #eta(lept. top)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenTopLep_eta[0],
    binning   = [ 20, -6, 6 ],
))

plotList.append( Plot(
    name      = 'GenTopLep_phi',
    texX      = 'gen #phi(lept. top)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenTopLep_phi[0],
    binning   = [ 15, -pi, pi ],
))

plotList.append( Plot(
    name      = 'GenTopHad_pt[0]', # name of the plot file
    texX      = 'gen p_{T}(hadr. top_{0}) [GeV]', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.GenTopHad_pt[0], # variable to plot
    binning   = [ 20, 20, 1100 ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'GenTopHad_eta[0]',
    texX      = 'gen #eta(hadr. top_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenTopHad_eta[0],
    binning   = [ 20, -5, 5 ],
))

plotList.append( Plot(
    name      = 'GenTopHad_phi[0]',
    texX      = 'gen #phi(hadr. top_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenTopHad_phi[0],
    binning   = [ 15, -pi, pi ],
))

plotList.append( Plot(
    name      = 'GenW_pt[0]', # name of the plot file
    texX      = 'gen p_{T}(W_{0}) [GeV]', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.GenW_pt[0], # variable to plot
    binning   = [ 20, 20, 520 ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'GenW_eta[0]',
    texX      = 'gen #eta(W_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenW_eta[0],
    binning   = [ 20, -5, 5 ],
))

plotList.append( Plot(
    name      = 'GenW_phi[0]',
    texX      = 'gen #phi(W_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenW_phi[0],
    binning   = [ 10, -pi, pi ],
))

plotList.append( Plot(
    name      = 'GenW_pt[1]', # name of the plot file
    texX      = 'gen p_{T}(W_{1}) [GeV]', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.GenW_pt[1], # variable to plot
    binning   = [ 20, 20, 700 ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'GenW_eta[1]',
    texX      = 'gen #eta(W_{1})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenW_eta[1],
    binning   = [ 20, -5, 5 ],
))

plotList.append( Plot(
    name      = 'GenW_phi[1]',
    texX      = 'gen #phi(W_{1})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenW_phi[1],
    binning   = [ 10, -pi, pi ],
))

plotList.append( Plot(
    name      = 'GenWLep_pt[0]', # name of the plot file
    texX      = 'gen p_{T}(lept. W) [GeV]', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.GenWLep_pt[0], # variable to plot
    binning   = [ 20, 20, 520 ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'GenWLep_eta[0]',
    texX      = 'gen #eta(lept. W)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenWLep_eta[0],
    binning   = [ 20, -5, 5 ],
))

plotList.append( Plot(
    name      = 'GenWLep_phi[0]',
    texX      = 'gen #phi(lept. W)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenWLep_phi[0],
    binning   = [ 10, -pi, pi ],
))

plotList.append( Plot(
    name      = 'GenWHad_pt[0]', # name of the plot file
    texX      = 'gen p_{T}(hadr. W) [GeV]', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.GenWHad_pt[0], # variable to plot
    binning   = [ 20, 20, 520 ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'GenWHad_eta[0]',
    texX      = 'gen #eta(hadr. W)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenWHad_eta[0],
    binning   = [ 20, -5, 5 ],
))

plotList.append( Plot(
    name      = 'GenWHad_phi[0]',
    texX      = 'gen #phi(hadr. W)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenWHad_phi[0],
    binning   = [ 15, -pi, pi ],
))

plotList.append( Plot(
    name      = 'GenBLep_pt[0]', # name of the plot file
    texX      = 'gen p_{T}(lept. b) [GeV]', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.GenBLep_pt[0], # variable to plot
    binning   = [ 20, 20, 600 ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'GenBLep_eta[0]',
    texX      = 'gen #eta(lept. b)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenBLep_eta[0],
    binning   = [ 20, -5, 5 ],
))

plotList.append( Plot(
    name      = 'GenBLep_phi[0]',
    texX      = 'gen #phi(lept. b)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenBLep_phi[0],
    binning   = [ 15, -pi, pi ],
))

plotList.append( Plot(
    name      = 'GenBHad_pt[0]', # name of the plot file
    texX      = 'gen p_{T}(hadr. b) [GeV]', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.GenBHad_pt[0], # variable to plot
    binning   = [ 20, 20, 600 ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'GenBHad_eta[0]',
    texX      = 'gen #eta(hadr. b)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenBHad_eta[0],
    binning   = [ 20, -5, 5 ],
))

plotList.append( Plot(
    name      = 'GenBHad_phi[0]',
    texX      = 'gen #phi(hadr. b)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenBHad_phi[0],
    binning   = [ 10, -pi, pi ],
))

#missing E 
#"GenMET_pt/F", "GenMET_phi/F"
plotList.append( Plot(
    name      = 'GenMET_pt', # name of the plot file
    texX      = 'gen E_{T}^{miss} [GeV]', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.GenMET_pt, # variable to plot
    binning   = [ 20, 20, 520 ], # 20 bins from 20 to 120
))
  
plotList.append( Plot(
    name      = 'GenMET_phi', # name of the plot file
    texX      = 'gen #phi(MET)', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.GenMET_phi, # variable to plot
    binning   = [ 10, -pi, pi ], # 20 bins from 20 to 120
))

#other
plotList.append( Plot(
    name      = 'mT', # name of the plot file
    texX      = 'M_{T} [GeV]', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.mT, # variable to plot
    binning   = [ 20, 20, 300 ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'm3', # name of the plot file
    texX      = 'M_{3} [GeV]', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.m3, # variable to plot
    binning   = [ 20, 20, 400 ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'ht', # name of the plot file
    texX      = 'H_{T} [GeV]', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.ht, # variable to plot
    binning   = [ 20, 20, 500 ], # 20 bins from 20 to 120
))

#DELTA
#phi
plotList.append( Plot(
    name      = 'dPhiLepGamma', # name of the plot file
    texX      = '#Delta#phi(l,#gamma)', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.dPhiLepGamma, # variable to plot
    binning   = [ 20, 0, pi ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'dPhiTopHadGamma', # name of the plot file
    texX      = '#Delta#phi(hadr. top, #gamma)', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.dPhiTopHadGamma, 
    binning   = [ 20, 0, pi ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'dPhiWHadGamma', # name of the plot file
    texX      = '#Delta#phi(hadr. W, #gamma)', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.dPhiWHadGamma, 
    binning   = [ 20, 0, pi ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'dPhiTopLepGamma', # name of the plot file
    texX      = '#Delta#phi(lept. top, #gamma)', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.dPhiTopLepGamma, # variable to plot
    binning   = [ 20, 0, pi ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'dPhiWLepGamma', # name of the plot file
    texX      = '#Delta#phi(lept. W, #gamma)', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.dPhiWLepGamma, # variable to plot
    binning   = [ 20, 0, pi ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'dPhiBHadGamma', # name of the plot file
    texX      = '#Delta#phi(hadr. b, #gamma)', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.dPhiBHadGamma, 
    binning   = [ 20, 0, pi ], # 20 bins from 20 to 120
))
plotList.append( Plot(
    name      = 'dPhiBLepGamma', # name of the plot file
    texX      = '#Delta#phi(lept. b, #gamma)', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.dPhiBLepGamma, 
    binning   = [ 20, 0, pi ], # 20 bins from 20 to 120
))
plotList.append( Plot(
    name      = 'dPhiBLepWLep', # name of the plot file
    texX      = '#Delta#phi(lept. b, lept. W)', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.dPhiBLepWLep, 
    binning   = [ 20, 0, pi ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'dPhiWLepWHad', # name of the plot file
    texX      = '#Delta#phi(W,W)', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.dPhiWLepWHad,
    binning   = [ 20, 0, pi ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'dPhiBHadWHad', # name of the plot file
    texX      = '#Delta#phi(hadr. b, hadr. W)', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.dPhiBHadWHad,
    binning   = [ 20, 0, pi ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'dPhiBLepBHad', # name of the plot file
    texX      = '#Delat#phi(b, b)', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.dPhiBLepBHad, 
    binning   = [ 20, 0, pi ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'dPhiTopLepTopHad', # name of the plot file
    texX      = '#Delta#phi(top, top)', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.dPhiTopLepTopHad, 
    binning   = [ 20, 0, pi ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'dPhiLepMET', # name of the plot file
    texX      = '#Delta#phi(l, MET)', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.dPhiLepMET, # variable to plot
    binning   = [ 20, 0, pi ], # 20 bins from 20 to 120
))

#R

plotList.append( Plot(
    name      = 'dRLepGamma',
    texX      = '#Delta R(l, #gamma)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.dRLepGamma,
    binning   = [ 20, 0, 4.5 ],
))

plotList.append( Plot(
    name      = 'dRTopHadGamma',
    texX      = '#Delta R(hadr. top, #gamma)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.dRTopHadGamma,
    binning   = [ 20, 0, 8 ],
))

plotList.append( Plot(
    name      = 'dRWHadGamma',
    texX      = '#Delta R(hadr. W, #gamma)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.dRWHadGamma,
    binning   = [ 20, 0, 8 ],
))

plotList.append( Plot(
    name      = 'dRTopLepGamma',
    texX      = '#Delta R(lept. top, #gamma)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.dRTopLepGamma,
    binning   = [ 20, 0, 8 ],
))

plotList.append( Plot(
    name      = 'dRWLepGamma',
    texX      = '#Delta R(lept. W, #gamma)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.dRWLepGamma,
    binning   = [ 20, 0, 7 ],
))

plotList.append( Plot(
    name      = 'dRBHadGamma',
    texX      = '#Delta R(hadr. b, #gamma)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.dRBHadGamma,
    binning   = [ 20, 0, 7 ],
))

plotList.append( Plot(
    name      = 'dRBLepGamma',
    texX      = '#Delta R(lept. b, #gamma)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.dRBLepGamma,
    binning   = [ 20, 0, 7 ],
))

plotList.append( Plot(
    name      = 'dRBLepWLep',
    texX      = '#Delta R(lept. b, lept. W)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.dRBLepWLep,
    binning   = [ 20, 0, 7 ],
))

plotList.append( Plot(
    name      = 'dRWLepWHad',
    texX      = '#Delta R(W, W)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.dRWLepWHad,
    binning   = [ 20, 0, 8 ],
))

plotList.append( Plot(
    name      = 'dRBHadWHad',
    texX      = '#Delta R(hadr. b, hadr. W)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.dRBHadWHad,
    binning   = [ 20, 0, 7 ],
))

plotList.append( Plot(
    name      = 'dRBLepBHad',
    texX      = '#Delta R(b, b)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.dRBLepBHad,
    binning   = [ 20, 0, 8 ],
))

plotList.append( Plot(
    name      = 'dRTopLepTopHad',
    texX      = '#Delta R(top, top)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.dRTopLepTopHad,
    binning   = [ 20, 0, 8 ],
))

plotList.append( Plot(
    name      = 'nGenJetsCMSUnfold', # name of the plot file
    texX      = 'N_{jets}', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.nGenJetsCMSUnfold, # variable to plot
    binning   = [ 10, 0, 10 ],
))
plotList.append( Plot(
    name      = 'nGenBJetCMSUnfold', # name of the plot file
    texX      = 'N_{b}', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.nGenBJetCMSUnfold, # variable to plot
    binning   = [ 4, 0, 4 ],
))
plotList.append( Plot(
    name      = 'nGenLeptonCMSUnfold', # name of the plot file
    texX      = 'N_{l}', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.nGenLeptonCMSUnfold, # variable to plot
    binning   = [ 4, 0, 4 ],
))
plotList.append( Plot(
    name      = 'nGenPhotonCMSUnfold', # name of the plot file
    texX      = 'N_{#gamma}', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.nGenPhotonCMSUnfold, # variable to plot
    binning   = [ 4, 0, 4 ],
))

# fill the histograms here, depending on the selection this can take a while
# here you also say which plots you want to fill (plots), which variables they need (read_variables) and which additionl functions to call for each event (sequence)
plotting.fill( plotList, read_variables=read_variables )

# print the plots
drawPlots( plotList )

