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
from TTGammaEFT.Tools.helpers         import splitList
from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter, isoThresh, chgIsoThresh, lowSieieThresh, highSieieThresh
from TTGammaEFT.Tools.TriggerSelector import TriggerSelector
from TTGammaEFT.Tools.Variables       import NanoVariables
from TTGammaEFT.Tools.objectSelection import *

from Analysis.Tools.metFilters        import getFilterCut
from Analysis.Tools.helpers           import getCollection, deltaR
from TTGammaEFT.Tools.overlapRemovalTTG import *
import Analysis.Tools.syncer as syncer

# Default Parameter
loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                     help="Log level for logging")
argParser.add_argument('--plot_directory',     action='store',      default='102X_TTG_ppv47_v2')
argParser.add_argument('--small',              action='store_true',                                                                       help='Run only on a small subset of the data?', )
argParser.add_argument('--year',               action='store',      default="2016",      type=str,  choices=["2016","2017","2018","RunII"],                  help="Which year to plot?")
args = argParser.parse_args()

if args.year != "RunII": args.year = int(args.year)

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small:           args.plot_directory += "_small"

photonVariable = "PhotonNoChgIsoNoSieie0"
# Samples
os.environ["gammaSkim"]="True"
if args.year == 2016:
    import TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed  as mc_samples
    from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import Run2016 as data_sample
elif args.year == 2017:
    import TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed    as mc_samples
    from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import Run2017 as data_sample
elif args.year == 2018:
    import TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed  as mc_samples
    from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import Run2018 as data_sample
elif args.year == "RunII":
    import TTGammaEFT.Samples.nanoTuples_RunII_postProcessed as mc_samples
    from TTGammaEFT.Samples.nanoTuples_RunII_postProcessed import RunII as data_sample

# Text on the plots
def drawObjects( plotData, lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS #bf{#it{Preliminary}}' if plotData else 'CMS #bf{#it{Simulation Preliminary}}'), 
      (0.68, 0.95, '%3.1f fb^{-1} (13 TeV)' % lumi_scale)
    ]
    return [tex.DrawLatex(*l) for l in lines] 

# Plotting
def drawPlots( plots, mode ):
    for log in [True, False]:
        sc = "log" if log else "lin"
        plot_directory_ = os.path.join( plot_directory, 'WGChecks', str(args.year), args.plot_directory, "VG2p", "all", sc )

        for plot in plots:
            if not max(l[0].GetMaximum() for l in plot.histos): 
                continue # Empty plot

#            scaling = { 1:0, 2:0 }

#            plot.histos[0][0].style        = styles.errorStyle( ROOT.kBlack )
#            plot.histos[1][0].style        = styles.lineStyle( ROOT.kCyan+2, width = 2, dotted=False, dashed=False, errors = True )
#            plot.histos[2][0].style        = styles.lineStyle( ROOT.kRed+2, width = 2, dotted=False, dashed=False, errors = True )

            plotting.draw( plot,
	                       plot_directory = plot_directory_,
#                           ratio = {'histos':[(1,0),(2,0)], 'texY': 'Ratio', 'yRange':(0.1,1.9)},
	                       logX = False, logY = log, sorting = False,
	                       yRange = (0.03, "auto") if log else (0.001, "auto"),
#	                       scaling = scaling,
	                       legend = [ (0.2,0.87-0.04*sum(map(len, plot.histos)),0.8,0.87), 1],
	                       drawObjects = drawObjects( True , lumi_scale ),
                           copyIndexPHP = True
                         )


# Read variables and sequences
read_variables  = ["weight/F",
                   "nJetGood/I", "nBTagGood/I",
                  ]

read_variables_MC = ["isTTGamma/I", "isZWGamma/I", "isTGamma/I", "overlapRemoval/I",
                     "reweightPU/F", "reweightPUDown/F", "reweightPUUp/F", "reweightPUVDown/F", "reweightPUVUp/F",
                     "reweightLeptonTightSF/F", "reweightLeptonTightSFUp/F", "reweightLeptonTightSFDown/F",
                     "reweightLeptonTrackingTightSF/F",
                     "reweightTrigger/F", "reweightTriggerUp/F", "reweightTriggerDown/F",
                     "reweightPhotonSF/F", "reweightPhotonSFUp/F", "reweightPhotonSFDown/F",
                     "reweightPhotonElectronVetoSF/F",
                     "reweightBTag_SF/F", "reweightBTag_SF_b_Down/F", "reweightBTag_SF_b_Up/F", "reweightBTag_SF_l_Down/F", "reweightBTag_SF_l_Up/F",
                     'reweightL1Prefire/F', 'reweightL1PrefireUp/F', 'reweightL1PrefireDown/F',
                     "nGenPart/I",
                     "nGenJet/I",
                    ]

read_variables_MC += [ VectorTreeVariable.fromString('GenJet[pt/F,eta/F,phi/F]', nMax=100) ]
read_variables_MC += [ VectorTreeVariable.fromString('GenPart[status/I,pt/F,eta/F,phi/F,pdgId/I]', nMax=100) ]

def calcdR( event, sample ):
#    if sample.name != "cut": event.genJetDR = 1.
    GenJets = getCollection( event, 'GenJet', ["pt","eta","phi"], 'nGenJet' )
    GenJets = filter( lambda p: p["pt"]>5, GenJets )
    GenParts = getCollection( event, 'GenPart', ["status","pt","eta","phi","pdgId"], 'nGenPart' )
    GenLeptons = filter( lambda p: (abs(p["pdgId"])==11 or abs(p["pdgId"]==13)) and p["pt"]>5 and p["status"]==1, GenParts )
#    print GenLeptons
    GenJets = deltaRCleaning( GenJets,    GenLeptons, dRCut=0.4 )

    GenPhotons = filter( lambda p: p["pdgId"]==22 and p["pt"]>10 and p["status"]==1, GenParts )
    GenPhotons.sort( key = lambda p: -p['pt'] )
    GenPhotons = deltaRCleaning( GenPhotons,    GenLeptons, dRCut=0.4 )
    GenJets = deltaRCleaning( GenJets,    GenPhotons, dRCut=0.05 )

#    print GenPhotons, GenJets
    if GenPhotons and GenJets:
        event.genJetDR = min( deltaR( GenPhotons[0], j ) for j in GenJets )
    else:
        event.genJetDR = -1
#    print event.genJetDR

# Sequence
sequence = [calcdR]

mc = mc_samples.WG_NLO

if args.small:
        mc.reduceFiles( factor=20 )

#mclow = copy.deepcopy(mc)

filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )
mcSelection = [ filterCutMc, "triggered==1", "pTStitching==1" ]

mc.texName = "W#gamma inclusive"
#mclow.texName = "W#gamma dR cut"
#mc.name = "NOcut"
#mclow.name = "cut"

if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74

mc.read_variables = read_variables_MC
mc.scale          = lumi_scale
mc.weight         = lambda event, sample: event.reweightTrigger*event.reweightL1Prefire*event.reweightPU*event.reweightLeptonTightSF*event.reweightLeptonTrackingTightSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF

stackSamples  = [[mc]]
stack = Stack( *stackSamples )

weight_ = lambda event, sample: event.weight

# Use some defaults (set defaults before you create/import list of Plots!!)
sel = "nLeptonTight==1&&(1)&&nLeptonVetoIsoCorr==1&&nJetGood>=2&&nBTagGood==0&&nPhotonGood==1&&nPhotonNoChgIsoNoSieie==1&&((abs(mLtight0Gamma-91.1876)>10&&nElectronTight==1)||(nElectronTight==0))&&triggered==1"
Plot.setDefaults( stack=stack, weight=staticmethod( weight_ ), selectionString=sel )

# plotList
plots = []
#plots.append( Plot(
#    name      = 'nJetGood',
#    texX      = 'N_{jet}',
#    texY      = 'Number of Events',
#    attribute = lambda event, sample: event.nJetGood if sample.name == "cut" and event.genJetDR >,
#    binning   = [ 5, 2, 7 ],
#))

plots.append( Plot(
    name      = 'photonJetDR',
    texX      = 'min #Delta R(gen-jet, gen-#gamma)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.genJetDR,
    binning   = [ 20, 0, 1 ],
))


plotting.fill( plots, read_variables=read_variables, sequence=sequence )
drawPlots( plots, "all" )

