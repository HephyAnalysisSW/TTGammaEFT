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
argParser.add_argument('--plot_directory',     action='store',      default='102X_TTG_ppv1_v7')
argParser.add_argument('--selection',          action='store',      default='dilepOS-nLepVeto2')
argParser.add_argument('--small',              action='store_true',                                                                                  help='Run only on a small subset of the data?', )
args = argParser.parse_args()

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small:     args.plot_directory += "_small"

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
        plot_directory_ = os.path.join( plot_directory, 'prefiring2017', args.plot_directory, args.selection, mode, "lin" )

        print plots
        for plot in plots:
            print plot
            extensions_ = ["pdf", "png", "root"] if mode == 'all' else ['png']
            plotting.draw( plot,
                           plot_directory = plot_directory_,
                           extensions = extensions_,
#                           ratio = {'histos':[(0,1)], 'texY': 'data / unpref.', 'yRange':(0.5,1.5)} if not args.noData else None,
                           logX = False, logY = False, sorting = False,
#                           yRange = (0.001, "auto"),
#                           scaling = scaling if args.normalize else {},
                           legend = [ (0.15,0.9-0.03*sum(map(len, plot.histos)),0.9,0.9), 2],
                           drawObjects = drawObjects( 41.9 ),
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
from TTGammaEFT.Analysis.regions import preFiringSumJetPtLog
from TTGammaEFT.Analysis.Region  import texString

allRegions = [\
              ( preFiringSumJetEta, -5, 5 ), 
              ( preFiringSumJetPtLog,  30, 1000 ), 
             ]


allModes = [ 'all', 'mumu', 'mue', 'ee', 'SF' ]

selection    = cutInterpreter.cutString( args.selection )
addSelection = "Jet_pt<500&&Jet_pt>30&&Jet_cleanmask&&abs(Jet_eta)<3.5"
metFilter    = getFilterCut( 2017, isData=True, skipBadChargedCandidate=True )

ptMinVal  = 30
ptMaxVal  = 1000
etaMinVal = -5
etaMaxVal = 5

variableString = "Jet_pt:Jet_eta"
ptBinning  = [ val0 for region in preFiringSumJetPtLog for val0, val1 in region.vals.values() ] + [ptMaxVal]
etaBinning = [ val0 for region in preFiringSumJetEta   for val0, val1 in region.vals.values() ] + [etaMaxVal]
binning = (etaBinning, ptBinning)

for mode in allModes:
    leptonSelection = cutInterpreter.cutString( mode )
    totalSelection  = [ metFilter, leptonSelection, selection, addSelection ]
    
    Run2017_noPreFiring.setSelectionString( totalSelection + [ "unPreFirableEvent==1"] )
    Run2017.setSelectionString( totalSelection )

    npfHist = Run2017_noPreFiring.get2DHistoFromDraw( variableString, binning, weightString=str(eventNorm), binningIsExplicit = True )
    hist    = Run2017.get2DHistoFromDraw(             variableString, binning, weightString=str(eventNorm), binningIsExplicit = True )

#    hist.Scale(    1./hist.Integral() )
#    npfHist.Scale( 1./npfHist.Integral() )

    npfHist.Divide(hist)
#    npfHist = hist
#    npfHist.Scale( 1./npfHist.Integral() )

#    npfHist.GetZaxis().SetRangeUser( 0, 1 )
    npfHist.GetXaxis().SetRangeUser( -3.5, 3.5 )
    npfHist.GetYaxis().SetRangeUser( 0, 500 )

#    plot2D = Plot.fromHisto("preFiring_Ratio2D", npfHist, texX = "#eta(jets)", texY = "p_{T}(jets)")
#    drawPlots( [plot2D], mode )

#    continue

    npfHist.SetStats(False)

    cans = ROOT.TCanvas("can","",500,500)

    pads = ROOT.TPad("pad","",0.,0.,1.,1.)
    pads.SetRightMargin(0.20)
    pads.SetLeftMargin(0.14)
    pads.SetTopMargin(0.11)
    pads.SetLogy()
    pads.Draw()
    pads.cd()

    npfHist.Draw("colz")

    latex1 = ROOT.TLatex()
    latex1.SetNDC()
    latex1.SetTextSize(0.032)
    latex1.SetTextFont(42)
    latex1.SetTextAlign(11)

    latex1.DrawLatex(0.15, 0.92, '#bf{CMS} #it{Preliminary} (SingleMuon Run2017B-H)'),
#    latex1.DrawLatex(0.70, 0.92, '#bf{%3.1f fb{}^{-1} (13 TeV)}' % 41.9)


    xTitle = "#eta(jets)"
    yTitle = "p_{T}(jets)"
    zTitle = "Ratio unprefirable events / full dataset"
    npfHist.SetTitle( "" )
    npfHist.GetXaxis().SetTitle( xTitle )
    npfHist.GetYaxis().SetTitle( yTitle )
    npfHist.GetZaxis().SetTitle( zTitle )

    npfHist.SetTitleFont(42)
    npfHist.GetXaxis().SetTitleFont(42)
    npfHist.GetYaxis().SetTitleFont(42)
    npfHist.GetZaxis().SetTitleFont(42)
    npfHist.GetXaxis().SetLabelFont(42)
    npfHist.GetYaxis().SetLabelFont(42)
    npfHist.GetZaxis().SetLabelFont(42)

    npfHist.GetXaxis().SetTitleOffset(1.0)
    npfHist.GetYaxis().SetTitleOffset(1.25)
    npfHist.GetZaxis().SetTitleOffset(1.5)
    
    npfHist.SetTitleSize(0.035)
    npfHist.GetXaxis().SetTitleSize(0.045)
    npfHist.GetYaxis().SetTitleSize(0.045)
    npfHist.GetZaxis().SetTitleSize(0.042)
    npfHist.GetXaxis().SetLabelSize(0.04)
    npfHist.GetYaxis().SetLabelSize(0.04)
    npfHist.GetZaxis().SetLabelSize(0.04)

    plot_directory_ = os.path.join( plot_directory, 'prefiring2017', args.plot_directory, args.selection, mode, "lin" )
#    plot_directory_ = os.path.join( plot_directory, "prefiring2017%s"%("_small" if args.small else "") )
    if not os.path.isdir(plot_directory_): os.makedirs(plot_directory_)
    plotname = "preFiring_ratio2D"
    for e in [".png",".pdf",".root"]:
        cans.Print( plot_directory_ + "/%s%s"%(plotname, e) )


