''' Plot script pTG shape + WC
'''

# Standard imports 
import sys, os, pickle, copy, ROOT, itertools

from math import pi

# RootTools
from RootTools.core.standard   import *

# turn off graphics
ROOT.gROOT.SetBatch( True )

# TTGammaEFT
from TTGammaEFT.Tools.user              import plot_directory
from TTGammaEFT.Tools.cutInterpreter    import cutInterpreter

from Analysis.Tools.metFilters          import getFilterCut

# Default Parameter
loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                                help="Log level for logging")
argParser.add_argument('--plot_directory',     action='store',      default='80X_TTG_ppv1_v1')
argParser.add_argument('--selection',          action='store',      default='dilepOS-nLepVeto2-pTG20-nPhoton1p-offZSFllg-offZSFll-mll40-nJet2p-nBTag1p')
argParser.add_argument('--small',              action='store_true',                                                                                  help='Run only on a small subset of the data?', )
argParser.add_argument('--normalize',          action='store_true', default=False,                                                                   help="Normalize yields" )
args = argParser.parse_args()

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small:     args.plot_directory += "_small"
if args.normalize: args.plot_directory += "_normalize"

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

#scaling = { 1:0 }
scaling = { 0:1 }

# Plotting
def drawPlots( plots, mode ):
 
    extensions_ = ["pdf", "png", "root"] if mode == 'all' else ['png']

    for log in [False, True]:

        plot_directory_ = os.path.join( plot_directory, 'prefiring2017', args.plot_directory, args.selection, mode, "log" if log else "lin" )

        for plot in plots:
            if not max(l[0].GetMaximum() for l in plot.histos): 
                continue # Empty plot

            for i, sample in enumerate(allSamples):
                plot.histos[i][0].style      = sample.style
                plot.histos[i][0].legendText = sample.texName

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



# 2017 Samples
from TTGammaEFT.Samples.nanoTuples_Run2017_preFiring_postProcessed import *

Run2017.texName = "data"
Run2017.name    = "data"
Run2017.style   = styles.errorStyle( ROOT.kBlue )#styles.fillStyle( ROOT.kOrange-3 )

Run2017_noPreFiring = copy.deepcopy(Run2017)
Run2017_noPreFiring.texName = "data (unprefirable)"
Run2017_noPreFiring.name    = "data_unprefireable"
Run2017_noPreFiring.style   = styles.errorStyle( ROOT.kBlack )

lumi_scale = Run2017.lumi * 0.001
allSamples = [ Run2017, Run2017_noPreFiring ]

eventNorm = 1
if args.small:
    for sample in [ Run2017_noPreFiring, Run2017 ]:
        sample.normalization=1.
        sample.reduceFiles( factor=15 )
        eventNorm = 1./sample.normalization



from TTGammaEFT.Analysis.regions import preFiringSumJetEta
from TTGammaEFT.Analysis.regions import preFiringSumJetPt
from TTGammaEFT.Analysis.regions import preFiringSumJet
from TTGammaEFT.Analysis.Region  import texString

allRegions = [\
              ( preFiringSumJet,   -pi, pi ), 
              ( preFiringSumJetEta, -5, 5 ), 
              ( preFiringSumJetPt,  30, 200 ), 
             ]


allModes = [ 'mumu', 'mue', 'ee' ]
allPlots = {}

selection    = cutInterpreter.cutString( args.selection )
addSelection = "Jet_pt>30&&Jet_cleanmask"
#addSelection = "Jet_cleanmask"


for regions, minval, maxval in allRegions:

    Nbins = len(regions)
    rate = {}

    for index, mode in enumerate( allModes ):

        hists = {}
        for sample in allSamples:
            hists[sample.name] = ROOT.TH1F(sample.name+mode,"", Nbins, minval, maxval)

        # Define 2l selections
        leptonSelection = cutInterpreter.cutString( mode )
        totalSelection  = [ getFilterCut( 2017, isData=True, skipBadChargedCandidate=True ),  leptonSelection, selection, addSelection ]
    
        Run2017_noPreFiring.setSelectionString( totalSelection + [ "unPreFirableEvent==1"] )
        Run2017.setSelectionString( totalSelection )

        for i_region, region in enumerate(regions):
            # compute signal yield for this region (this is the final code)

            logger.info( "At region %s", region )
            logger.info( "Using region cut-string %s", region.cutString() )

            rate[region] = {}

            for i_sample, sample in enumerate( allSamples ):
                eventList = sample.getEventList( selectionString=region.cutString() )
                rate[region][sample.name] = eventList.GetN() * eventNorm

        for i_region, region in enumerate(regions):

            for i_sample, sample in enumerate( allSamples ):
                hists[sample.name].SetBinContent( i_region+1, rate[region][sample.name] )
#                hists[sample.name].SetBinError( i_region+1,0 )
                hists[sample.name].legendText = sample.texName
                hists[sample.name].style      = sample.style

        plots     = [ [hists[sample.name]] for sample in allSamples ]
        plot      = Plot.fromHisto( "sum" + regions[0].vals.keys()[0], plots, texX=texString[regions[0].vals.keys()[0]], texY="Number of Events" )

        logger.info( "Plotting mode %s", mode )
        allPlots[mode] = [ copy.deepcopy( plot ) ] # deep copy for creating SF/all plots afterwards!
        drawPlots( allPlots[mode], mode )


    # Add the different channels into SF and all
    for mode in [ "SF", "all" ]:
        for plot in allPlots['mumu']:
            for pl in ( p for p in ( allPlots['ee'] if mode=="SF" else allPlots["mue"] ) if p.name == plot.name ):  #For SF add EE, second round add EMu for all
                for i, j in enumerate( list( itertools.chain.from_iterable( plot.histos ) ) ):
                    j.Add( list( itertools.chain.from_iterable( pl.histos ) )[i] )

        drawPlots( allPlots['mumu'], mode )

