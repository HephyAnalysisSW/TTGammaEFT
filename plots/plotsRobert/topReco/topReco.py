#!/usr/bin/env python
''' Analysis script for standard plots
'''

# Standard imports
import ROOT, os, operator
ROOT.gROOT.SetBatch(True)
from math                             import pi, sqrt, copysign, isnan

# RootTools
from RootTools.core.standard          import *

# Internal Imports
from TTGammaEFT.Tools.user            import plot_directory, cache_directory
from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter
#from TTGammaEFT.Tools.TriggerSelector import TriggerSelector
from TTGammaEFT.Tools.objectSelection import photonSelector

from Analysis.Tools.metFilters        import getFilterCut
from Analysis.Tools.helpers           import getCollection, deltaR
import Analysis.Tools.syncer          as syncer


# Default Parameter
loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                  help="Log level for logging")
argParser.add_argument('--plot_directory',     action='store',      default='topReco')
argParser.add_argument('--selection',          action='store',      default='nLepTight1-nLepVeto1-nJet3p-nBTag1p-nPhoton1')
argParser.add_argument('--small',              action='store_true',                                                                    help='Run only on a small subset of the data?', )
argParser.add_argument('--year',               action='store',      default=2016,   type=int,  choices=[2016,2017,2018],               help="Which year to plot?")
argParser.add_argument('--mode',               action='store',      default="all", type=str, choices=["mu", "e", "all"],               help="plot lepton mode" )
argParser.add_argument('--sample',             action='store',      default="TTG", type=str,                                           help="Which sample?" )
args = argParser.parse_args()

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small:           args.plot_directory += "_small"

os.environ["gammaSkim"]="True" if "hoton" in args.selection or "pTG" in args.selection else "False"
if args.year == 2016:
    import TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed as mc_samples
elif args.year == 2017:
    import TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed as mc_samples
elif args.year == 2018:
    import TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed as mc_samples

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
            plot_directory_ = os.path.join( plot_directory, 'analysisPlots', str(args.year), args.plot_directory, args.sample, args.selection, args.mode, "log" if log else "lin" )
            plotting.draw( plot,
                           plot_directory = plot_directory_,
                           #ratio = {'yRange':(0.5,1.5)} ,
                           logX = False, logY = log, sorting = True,
                           yRange = (0.9, "auto"),
                           legend = [ (0.2,0.9-0.025*sum(map(len, plot.histos)),0.9,0.9), 2],
                           drawObjects = drawObjects( False, lumi_scale ),
                           copyIndexPHP = True,
                          )


# add here variables that should be read by all samples
read_variables  = ["weight/F",
                   "PV_npvsGood/I",
                   "PV_npvs/I", "PV_npvsGood/I",
                   "nJetGood/I", "nBTagGood/I",
                   "nLeptonTight/I", "nElectronTight/I", "nMuonTight/I",
                   "nPhotonGood/I",
                   "Photon[pt/F,eta/F,phi/F]",
                   "MET_pt/F", "MET_phi/F", "ht/F",
                   "mLtight0Gamma/F",
                   "m3/F", "mT/F", 
                   "nJet/I", "Jet[partonFlavour/I]",
                   "nGenPart/I", "GenPart[statusFlags/I]",
                  ]

variables = ["pt/F", "eta/F", "phi/F"]
read_variables += map( lambda var: "PhotonGood0_"  + var, variables )
read_variables += map( lambda var: "LeptonTight0_" + var, variables + ["pdgId/I", "genPartIdx/I"] )
read_variables += map( lambda var: "LeptonTight1_" + var, variables )
read_variables += map( lambda var: "JetGood0_"     + var, variables )
read_variables += map( lambda var: "JetGood1_"     + var, variables )
read_variables += map( lambda var: "Bj0_"          + var, variables )
read_variables += map( lambda var: "Bj1_"          + var, variables )

# add here variables that should be read only for MC samples
read_variables_MC = ["overlapRemoval/I",
                     'nGenElectronCMSUnfold/I', 'nGenMuonCMSUnfold/I', 'nGenLeptonCMSUnfold/I', 'nGenPhotonCMSUnfold/I', 'nGenBJetCMSUnfold/I', 'nGenJetsCMSUnfold/I',
                     "reweightTrigger/F", "reweightPU/F", "reweightLeptonTightSF/F", "reweightLeptonTrackingTightSF/F", "reweightPhotonSF/F", "reweightPhotonElectronVetoSF/F", "reweightBTag_SF/F", 'reweightL1Prefire/F',
                    ]

read_variables_MC += map( lambda var: "GenPhotonCMSUnfold0_"  + var, variables )

read_variables_MC += [ "event/I", "run/I", "luminosityBlock/I" ]

strategies = ["BsPlusHardestTwo", "BsPlusHardestThree", "onlyBs", "allJets", "twoBestBs"]
read_variables.extend( [ ("topReco_%s"%strategy + "_%s")%var for var in ["neuPt/F",  "neuPz/F", "topMass/F", "WMass/F", "WPt/F", "topPt/F", "Jet_index/I"] for strategy in strategies] )

# example of how to calculate your own variables
def mc_match( event, sample ):

    # lepton
    if event.LeptonTight0_genPartIdx>=0:    
        l_idx       = event.LeptonTight0_genPartIdx
        l_pdgId     = event.LeptonTight0_pdgId
        # nAOD gen flags

        #print l_idx, event.nGenPart
        if l_idx<event.nGenPart and l_idx<100:
            #print l_idx, event.nGenPart, event.event, event.run, event.luminosityBlock
            event.l_isPrompt           = event.GenPart_statusFlags[l_idx]&1
            event.l_isTauDecayProduct  = (event.GenPart_statusFlags[l_idx]>>2)&1
            #print event.GenPart_statusFlags[l_idx], event.l_isPrompt, event.l_isTauDecayProduct
        else:
            event.l_isPrompt           = False
            event.l_isTauDecayProduct  = False
    else:
        l_idx       = None 
        l_pdgId     = 0
        # nAOD gen flags
        event.l_isPrompt           = False 
        event.l_isTauDecayProduct  = False


    event.prompt_and_not_tau = event.l_isPrompt and not event.l_isTauDecayProduct
    event.non_prompt_or_tau  = not event.prompt_and_not_tau

    # bjet
    for strategy in strategies:
        topReco_Jet_index     = getattr( event, "topReco_%s_Jet_index"%strategy )
        b_matched = False
        if topReco_Jet_index>=0:
            jet_partonFlavour = event.Jet_partonFlavour[topReco_Jet_index]
            if abs(jet_partonFlavour)==5:
                b_matched = True
                l_b_charge_consistency = (jet_partonFlavour*l_pdgId<0) 
            else:
                l_b_charge_consistency = False
        else:
            jet_partonFlavour  = 0
            l_b_charge_consistency     = False

        setattr(event, "non_prompt_or_tau_%s"%strategy, event.non_prompt_or_tau )
        setattr(event, "not_b_matched_%s"%strategy, event.prompt_and_not_tau and not b_matched )
        setattr(event, "ch_inconsistent_%s"%strategy, event.prompt_and_not_tau and b_matched and not l_b_charge_consistency)
        setattr(event, "ch_consistent_%s"%strategy, event.prompt_and_not_tau and b_matched and l_b_charge_consistency)
        

        #print strategy, l_isPrompt, l_isTauDecayProduct, 'b', l_b_charge_consistency, jet_partonFlavour, l_pdgId

    #print

#        is_  = 
#        is_matched = ( l_isPrompt is not None) and l_b_charge_consistency

sequence = [ mc_match ]

weight = lambda event, sample: event.weight*event.reweightTrigger*event.reweightL1Prefire*event.reweightPU*event.reweightLeptonTightSF*event.reweightLeptonTrackingTightSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF

# get some additional cuts specific for MC and/or data
# MET Filter cut for data and MC
filterCutData = getFilterCut( args.year, isData=True, skipBadChargedCandidate=True )
filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )
# Trigger cuts for MC (already applied for Data)
#tr            = TriggerSelector( args.year, singleLepton=True ) #single lepton trigger also for DY CR

# Sample definition

sample = getattr( mc_samples, args.sample )

# Scale the histograms by the luminosity taken by CMS in each year
if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74

# add here variables that should be read only for MC samples
sample.read_variables = read_variables_MC
sample.setSelectionString( [ filterCutMc, "triggered", "overlapRemoval==1" ] )
sample.scale          = lumi_scale
sample.weight         = [weight]

components = [ 
    {'texName':'all',           'flag':'true', 'color':ROOT.kBlack},
    {'texName':'NP l or #tau',  'flag':'non_prompt_or_tau', 'color':ROOT.kRed},
    {'texName':'b not matched', 'flag':'not_b_matched', 'color':ROOT.kMagenta},
    {'texName':'ch incons.',    'flag':'ch_inconsistent', 'color':ROOT.kGreen},
    {'texName':'consistent',    'flag':'ch_consistent', 'color':ROOT.kBlue},
]

say_yes = lambda event, sample: True

def get_flaggers(strategy):
    '''Note to future self: Sorry.
    '''
    def _get_flagger(strategy, flag):
        if flag == 'true':
            return say_yes
        else:
            def _f(event, sample):
                return operator.attrgetter(flag+'_'+strategy)(event)
            return _f
    return [ [_get_flagger(strategy, c['flag'])] for c in components] 

h_styles   = [ [styles.lineStyle(c['color'])] for c in components ]
h_texNames = [ [c['texName']] for c in components ]


stack      = Stack( *list([ sample ]  for c in components) )

if args.small:
    for sample in stack.samples:
        sample.normalization=1.
        sample.reduceFiles( factor=30 )
        #sample.reduceFiles( to=1 )
        sample.scale /= sample.normalization

preSelection = cutInterpreter.cutString( args.selection + "-" + args.mode )
Plot.setDefaults(   stack=stack, weight=None, selectionString=preSelection, addOverFlowBin=None )

# define a list of plots here
plotList = []

#plotList.append( Plot(
#    name      = 'PhotonGood0_pt', # name of the plot file
#    texX      = 'p_{T}(#gamma_{0}) (GeV)', # x axis label
#    texY      = 'Number of Events', # y axis label
#    attribute = lambda event, sample: event.PhotonGood0_pt, # variable to plot
#    binning   = [ 20, 20, 120 ], # 20 bins from 20 to 120
#))
#
#plotList.append( Plot(
#    name      = 'PhotonGood0_eta',
#    texX      = '#eta(#gamma_{0})',
#    texY      = 'Number of Events',
#    attribute = lambda event, sample: event.PhotonGood0_eta,
#    binning   = [ 10, -1.5, 1.5 ],
#))
#
#plotList.append( Plot(
#    name      = 'PhotonGood0_phi',
#    texX      = '#phi(#gamma_{0})',
#    texY      = 'Number of Events',
#    attribute = lambda event, sample: event.PhotonGood0_phi,
#    binning   = [ 10, -pi, pi ],
#))
#
#plotList.append( Plot(
#    name      = 'mT',
#    texX      = 'm_{T}',
#    texY      = 'Number of Events',
#    attribute = lambda event, sample: event.mT,
#    binning   = [ 40,0,400 ],
#))

def getter( strategy, variable ):
    _var = "topReco_%s_%s"%(strategy,variable)
    def _getter(event, sample):
        return getattr(event, _var)
    return _getter

for strategy in strategies: 

    sample_flags = get_flaggers(strategy)

    plotList.append( Plot(
        name      = strategy+'_yield',
        texX      = 'yield for '+strategy,
        texY      = 'Number of Events',
        attribute = lambda event, sample: .5,
        weight    = sample_flags,
        binning   = [1,0,1],
    ))

    plotList.append( Plot(
        name      = strategy+'_neuPt',
        texX      = 'p_{T}(#nu) for '+strategy,
        texY      = 'Number of Events',
        attribute = getter( strategy, 'neuPt' ),
        weight    = sample_flags,
        binning   = [ 30,0,600 ],
    ))
    plotList.append( Plot(
        name      = strategy+'_neuPz',
        texX      = 'p_{z}(#nu) for '+strategy,
        texY      = 'Number of Events',
        attribute = getter( strategy, 'neuPz' ),
        weight    = sample_flags,
        binning   = [ 40,-600,600 ],
    ))
    plotList.append( Plot(
        name      = strategy+'_topMass',
        texX      = 'topMass for '+strategy,
        texY      = 'Number of Events',
        attribute = getter( strategy, 'topMass' ),
        weight    = sample_flags,
        binning   = [ 30,0,600 ],
    ))
    plotList.append( Plot(
        name      = strategy+'_WMass',
        texX      = 'WMass for '+strategy,
        texY      = 'Number of Events',
        attribute = getter( strategy, 'WMass' ),
        weight    = sample_flags,
        binning   = [ 30,0,600 ],
    ))
    plotList.append( Plot(
        name      = strategy+'_WPt',
        texX      = 'WPt for '+strategy,
        texY      = 'Number of Events',
        attribute = getter( strategy, 'WPt' ),
        weight    = sample_flags,
        binning   = [ 30,0,600 ],
    ))
    plotList.append( Plot(
        name      = strategy+'_topPt',
        texX      = 'topPt for '+strategy,
        texY      = 'Number of Events',
        attribute = getter( strategy, 'topPt' ),
        weight    = sample_flags,
        binning   = [ 30,0,600 ],
    ))

# fill the histograms here, depending on the selection this can take a while
# here you also say which plots you want to fill (plots), which variables they need (read_variables) and which additionl functions to call for each event (sequence)
plotting.fill( plotList, read_variables=read_variables, sequence=sequence )

for plot in plotList:
    #histos = [h[0] for h in plot.histos_added]
    h_added = plot.histos_added
    total  = h_added[0][0].Integral()
    extra  = total - sum( [ h_added[i][0].Integral() for i in range(1, len(plot.histos))] )
    for i_hs, hs in enumerate(plot.histos):
        for i_h, h in enumerate(hs):
            h.style   = h_styles[i_hs][i_h]
            h.texName = h_texNames[i_hs][i_h]
            h.texName += ": %5.1f (%4.1f"%(plot.histos[i_hs][0].Integral(), (100*plot.histos[i_hs][0].Integral()/total if total>0 else 0.))+'%)'

# print the plots
drawPlots( plotList )
