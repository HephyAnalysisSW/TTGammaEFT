#!/usr/bin/env python
''' Analysis script for standard plots
'''

# Standard imports
import ROOT, os, copy, pickle
ROOT.gROOT.SetBatch(True)
from math                             import pi, sqrt

# RootTools
from RootTools.core.standard          import *

# Internal Imports
from TTGammaEFT.Tools.user            import plot_directory, cache_directory
from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter
from TTGammaEFT.Tools.TriggerSelector import TriggerSelector
from TTGammaEFT.Tools.objectSelection import photonSelector

from Analysis.Tools.metFilters        import getFilterCut
from Analysis.Tools.helpers           import getCollection, deltaR

# EFT Reweighting
from Analysis.Tools.WeightInfo          import WeightInfo

# Default Parameter
loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                  help="Log level for logging")
argParser.add_argument('--plot_directory',     action='store',      default='myFirstPlots')
argParser.add_argument('--selection',          action='store',      default='nLepTight1-nLepVeto1-nJet4p-nBTag1p-nPhoton1')
argParser.add_argument('--small',              action='store_true', default=False,                                                     help='Run only on a small subset of the data?', )
argParser.add_argument('--noData',             action='store_true', default=False,                                                     help='also plot data?')
argParser.add_argument('--year',               action='store',      default=2016,   type=int,  choices=[2016,2017,2018],               help="Which year to plot?")
argParser.add_argument('--mode',               action='store',      default="all", type=str, choices=["mu", "e", "all"],               help="plot lepton mode" )
argParser.add_argument('--normalize',          action='store_true', default=False,  help="Normalize yields" ) 
argParser.add_argument('--order',              action='store',      default=2, type=int,                                                             help='Polynomial order of weight string (e.g. 2)')
argParser.add_argument('--parameters',         action='store',      default=['ctZI', '2', 'ctWI', '2', 'ctZ', '2', 'ctW', '2'], type=str, nargs='+', help = "argument parameters")
args = argParser.parse_args()

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small:           args.plot_directory += "_small"
if args.noData:          args.plot_directory += "_noData"

# load and define the EFT sample
from TTGammaEFT.Samples.genTuples_TTGamma_EFT_postProcessed      import *
eftSample = TTG_4WC_ref

# load samples
# we have a photon skim (smaller samples if you plot a selection containing a photon)
# Set it to "True" if you want to use it, which will make the plot script much faster
# can only be used if you have a selection with at least one photon
os.environ["gammaSkim"]="True" if "hoton" in args.selection or "pTG" in args.selection else "False"
if args.year == 2016:
    from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed      import *
    if not args.noData:
        from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import *

elif args.year == 2017:
    from TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed        import *
    if not args.noData:
        from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import *

elif args.year == 2018:
    from TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed      import *
    if not args.noData:
        from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import *

#EFT/SM Ratio
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
def drawObjects( plotData, lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    line = (0.65, 0.95, '%3.1f fb{}^{-1} (13 TeV)' % lumi_scale)
    lines = [
      (0.15, 0.95, 'CMS #bf{#it{Preliminary}}' if plotData else 'CMS #bf{#it{Simulation Preliminary}}'), 
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
            plot_directory_ = os.path.join( plot_directory, 'analysisPlots', str(args.year), args.plot_directory, args.selection, args.mode, "log" if log else "lin" )
            plotting.draw( plot,
                           plot_directory = plot_directory_,
                           ratio = {'yRange':(0.5,1.5)} if not args.noData else None,
                           logX = False, logY = log, sorting = True,
                           yRange = (0.001, "auto"),
                           legend = [ (0.2,0.9-0.025*sum(map(len, plot.histos)),0.9,0.9), 3],
                           drawObjects = drawObjects( not args.noData, lumi_scale ),
                           copyIndexPHP = True,
                          )


# add here variables that should be read by all samples
read_variables  = ["weight/F", "ref_weight/F",
                   VectorTreeVariable.fromString('p[C/F]', nMax=100),
                   "PV_npvsGood/I",
                   "PV_npvs/I", "PV_npvsGood/I",
                   "nJetGood/I", "nBTagGood/I",
                   "nLeptonTight/I", "nElectronTight/I", "nMuonTight/I",
                   "nPhotonGood/I",
                   "Photon[pt/F,eta/F,phi/F]",
                   "MET_pt/F", "MET_phi/F", "ht/F",
                   "mLtight0Gamma/F",
                   "m3/F", "mT/F",'nGenElectronCMSUnfold/I', 'nGenMuonCMSUnfold/I', 'nGenLeptonCMSUnfold/I', 'nGenPhotonCMSUnfold/I', 'nGenBJetCMSUnfold/I', 'nGenJetsCMSUnfold/I',
                   'nGenJets/I', 'nGenBJet/I', 'nGenLepton/I', 'nGenMuon/I', 'nGenElectron/I', 'nGenPhoton/I'
                  ]

variables = ["pt/F", "eta/F", "phi/F"]
read_variables += map( lambda var: "PhotonGood0_"  + var, variables )
read_variables += map( lambda var: "LeptonTight0_" + var, variables )
read_variables += map( lambda var: "LeptonTight1_" + var, variables )
read_variables += map( lambda var: "JetGood0_"     + var, variables )
read_variables += map( lambda var: "JetGood1_"     + var, variables )
read_variables += map( lambda var: "Bj0_"          + var, variables )
read_variables += map( lambda var: "Bj1_"          + var, variables )

#
#read_variables = ["weight/F", "ref_weight/F", "GenMET_pt/F", "GenMET_phi/F",
 #                 VectorTreeVariable.fromString('p[C/F]', nMax=100),
  #                'nGenElectronCMSUnfold/I', 'nGenMuonCMSUnfold/I', 'nGenLeptonCMSUnfold/I', 'nGenPhotonCMSUnfold/I', 'nGenBJetCMSUnfold/I', 'nGenJetsCMSUnfold/I',
   #               'nGenJets/I', 'nGenBJet/I', 'nGenLepton/I', 'nGenMuon/I', 'nGenElectron/I', 'nGenPhoton/I'
    #             ]

genJetVarStringRead  = "pt/F,eta/F,phi/F,isMuon/I,isElectron/I,isPhoton/I"
genJetVarStringWrite = "isBJet/I"
genJetVarStringWrite = genJetVarStringRead + "," + genJetVarStringWrite

genTopVarStringRead  = "pt/F,eta/F,phi/F,mass/F"
genTopVarStringWrite = genTopVarStringRead

genLeptonVarStringRead  = "pt/F,eta/F,phi/F,pdgId/I"
genLeptonVarStringWrite = "motherPdgId/I,grandmotherPdgId/I"
genLeptonVarStringWrite = genLeptonVarStringRead + "," + genLeptonVarStringWrite

genPhotonVarStringRead  = "pt/F,phi/F,eta/F,mass/F"
genPhotonVarStringWrite = "motherPdgId/I,grandmotherPdgId/I,relIso04_all/F,relIso03_all/F,photonLepdR/F,photonJetdR/F,photonAlldR/F,status/I"
genPhotonVarStringWrite = genPhotonVarStringRead + "," + genPhotonVarStringWrite

read_variables += [ VectorTreeVariable.fromString('GenLepton[%s]'%genLeptonVarStringWrite, nMax=100) ]
read_variables += [ VectorTreeVariable.fromString('GenPhoton[%s]'%genPhotonVarStringWrite, nMax=100) ]
read_variables += [ VectorTreeVariable.fromString('GenJet[%s]'%genJetVarStringWrite, nMax=10) ]
read_variables += [ VectorTreeVariable.fromString('GenBJet[%s]'%genJetVarStringWrite, nMax=10) ]
read_variables += [ VectorTreeVariable.fromString('GenTop[%s]'%genTopVarStringWrite, nMax=10) ]

read_variables += map( lambda var: "GenPhotonCMSUnfold0_"  + var, ["pt/F","eta/F","phi/F"] )


# add here variables that should be read only for MC samples
read_variables_MC = ["overlapRemoval/I",
                     'nGenElectronCMSUnfold/I', 'nGenMuonCMSUnfold/I', 'nGenLeptonCMSUnfold/I', 'nGenPhotonCMSUnfold/I', 'nGenBJetCMSUnfold/I', 'nGenJetsCMSUnfold/I',
                     "reweightPU/F", "reweightLeptonTightSF/F", "reweightLeptonTrackingTightSF/F", "reweightPhotonSF/F", "reweightPhotonElectronVetoSF/F", "reweightBTag_SF/F", 'reweightL1Prefire/F',
                    ]

read_variables_MC += map( lambda var: "GenPhotonCMSUnfold0_"  + var, variables )

# add here variables that should be read only for Data samples
read_variables_Data = [ "event/I", "run/I", "luminosityBlock/I" ]

# example of how to calculate your own variables
def sequenceExample( event, sample ):

    # get all photons
    allPhotons  = getCollection( event, 'Photon', ["pt/F","eta/F","phi/F"], 'nPhoton' )

    # additional filters according to your needs
    highPTPhotons = filter( lambda p: p['pt'] > 100, allPhotons )

    # this variable will be added for each event and can be plotted afterwards (event.yourVariable =)
    event.nHighPTPhotons = len(highPTPhotons)

# add functions to calculate your own variables here
# this is slow, use it only if needed
sequence = [ sequenceExample ]

# MC samples need to be corrected by certain scale factors to correct e.g. detector effects. Define the "weight" here:
mcWeight = lambda event, sample: event.reweightL1Prefire*event.reweightPU*event.reweightLeptonTightSF*event.reweightLeptonTrackingTightSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF
# a weight for all samples incluuding data is defined here
weight = lambda event, sample: event.weight

# get some additional cuts specific for MC and/or data
# MET Filter cut for data and MC
filterCutData = getFilterCut( args.year, isData=True, skipBadChargedCandidate=True )
filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )
# Trigger cuts for MC (already applied for Data)
tr            = TriggerSelector( args.year, singleLepton=True ) #single lepton trigger also for DY CR
triggerCutMc  = tr.getSelection( "MC" )

# Sample definition
if args.year == 2016:
    # mc samples are defined in TTGammaEFT/Samples/python/nanoTuples_Summer16_private_semilep_postProcessed.py
    mc = [ TTG_16, TT_pow_16, DY_LO_16, WJets_16, WG_16, ZG_16, rest_16 ]
elif args.year == 2017:
    # mc samples are defined in TTGammaEFT/Samples/python/nanoTuples_Fall17_private_semilep_postProcessed.py
        mc = [ TTG_17, TT_pow_17, DY_LO_17, WJets_17, WG_17, ZG_17, rest_17 ]
elif args.year == 2018:
    # mc samples are defined in TTGammaEFT/Samples/python/nanoTuples_Autumn18_private_semilep_postProcessed.py
    mc = [ TTG_18, TT_pow_18, DY_LO_18, WJets_18, WG_18, ZG_18, rest_18 ]

if args.noData:
    # Scale the histograms by the luminosity taken by CMS in each year
    if args.year == 2016:   lumi_scale = 35.92
    elif args.year == 2017: lumi_scale = 41.53
    elif args.year == 2018: lumi_scale = 59.74
    # add all samples to the Stack
    stack = Stack( mc )
else:
    # Data Sample definition
    # mc samples are defined in TTGammaEFT/Samples/python/nanoTuples_Run201X_14Dec2018_semilep_postProcessed.py
    if args.year == 2016:   data_sample = Run2016
    elif args.year == 2017: data_sample = Run2017
    elif args.year == 2018: data_sample = Run2018
    # define the name on the plot
    postFix = " (%s)"%args.mode.replace("mu","#mu").replace("all","e+#mu")
    data_sample.texName        = "data" + postFix
    data_sample.name           = "data"
    # add here variables that should be read only for Data samples
    data_sample.read_variables = read_variables_Data
    # set additional cuts specific for data
    data_sample.setSelectionString( [ filterCutData ] )
    # change the style of the data sample (dots with error bars)
    data_sample.style = styles.errorStyle( ROOT.kBlack )
    # you can scale the histograms of each sample by defining sample.scale (don't scale data)
    data_sample.scale          = 1
    # Scale the MC histograms by the luminosity taken by CMS in each year
    lumi_scale                 = data_sample.lumi * 0.001
    # add all samples to the Stack
    stack                      = Stack( mc, data_sample )

# settings for MC Samples
for sample in mc:
    # add here variables that should be read only for MC samples
    sample.read_variables = read_variables_MC
    # set additional cuts specific for MC
    # overlapremoval for separating samples with and without a photon (e.g. ttbar from ttgamma)
    sample.setSelectionString( [ filterCutMc, triggerCutMc, "overlapRemoval==1" ] )
    # you can scale the histograms of each sample by defining sample.scale (don't scale data)
    # Scale the MC histograms by the luminosity taken by CMS in each year
    sample.scale          = lumi_scale
    # change the style of the MC sample (filled histograms)
    # the color is defined where mc samples are defined
    sample.style          = styles.fillStyle( sample.color )
    # add the predefined weight to the samples
    sample.weight         = mcWeight

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

#Histograms 
def get_weight_string( param, **kwargs ):
    return w.get_weight_string( **param['WC'] )( event, sample ) * event.ref_weight

smweightString = get_weight_string({})
bsmweightString = get_weight_string({"ctZ":2})
selection = cutInterpreter.cutString( args.selection + "-" + args.mode )

print smweightString
print bsmweightString

smHisto = eftSample.get1DHistoFromDraw( "GenPhotonCMSUnfold0_pt", binning=[20, 20, 800], selectionString=selection, weightString=smweightString, addOverFlowBin="upper" )
bsmHisto = eftSample.get1DHistoFromDraw( "GenPhotonCMSUnfold0_pt", binning=[20, 20, 800], selectionString=selection, weightString=bsmweightString, addOverFlowBin="upper" )

#bsmHisto.Divide(smHisto) 

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
# set default settings for your plots (weight, selection, do you want an overflow bin?)
Plot.setDefaults(   stack=stack, weight=staticmethod( weight ), selectionString=preSelection, addOverFlowBin="upper" )

# define a list of plots here
plotList = []

plotList.append( Plot(
    name      = 'PhotonGood0_pt', # name of the plot file
    texX      = 'p_{T}(#gamma_{0}) (GeV)', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.PhotonGood0_pt, # variable to plot
    binning   = [ 20, 20, 120 ], # 20 bins from 20 to 120
))

plotList.append( Plot(
    name      = 'PhotonGood0_eta',
    texX      = '#eta(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.PhotonGood0_eta,
    binning   = [ 10, -1.5, 1.5 ],
))

plotList.append( Plot(
    name      = 'PhotonGood0_phi',
    texX      = '#phi(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.PhotonGood0_phi,
    binning   = [ 10, -pi, pi ],
))

#opt
plotList.append( Plot(
    name      = 'LeptonTight0_pt',
    texX      = '#p_{T}i(#gamma_{0}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.LeptonTight0_pt,
    binning   = [ 20, 20,200 ],
))

plotList.append( Plot(
    name      = 'LeptonTight0_eta',
    texX      = '#eta(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.LeptonTight0_eta,
    binning   = [ 10, -2, 2 ],
))

plotList.append( Plot(
    name      = 'LeptonThight0_phi',
    texX      = '#phi(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.LeptonTight0_phi,
    binning   = [ 10, -pi, pi ],
))

plotList.append( Plot(
    name      = 'JetGood0_pt',
    texX      = '#p_{T}i(#gamma_{0}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.JetGood0_pt,
    binning   = [ 20, 20, 320 ],
))

plotList.append( Plot(
    name      = 'JetGood0_eta',
    texX      = '#eta(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.JetGood0_eta,
    binning   = [ 10, -2, 2],
))

plotList.append( Plot(
    name      = 'JetGood0_phi',
    texX      = '#phi(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.JetGood0_phi,
    binning   = [ 10, -pi, pi ],
))

# plot with self-calculated variable
plotList.append( Plot(
    name      = 'nHighPTPhotons',
    texX      = 'N_{#gamma} (p_{T} > 100 GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.nHighPTPhotons,
    binning   = [ 3, 0, 3 ],
))

# fill the histograms here, depending on the selection this can take a while
# here you also say which plots you want to fill (plots), which variables they need (read_variables) and which additionl functions to call for each event (sequence)
plotting.fill( plotList, read_variables=read_variables, sequence=sequence )

# print the plots
drawPlots( plotList )

