# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy

# RootTools
from RootTools.core.standard           import *

# Analysis
from Analysis.Tools.metFilters         import getFilterCut
import Analysis.Tools.syncer as syncer

# Internal Imports
from TTGammaEFT.Tools.user             import plot_directory, cache_directory
from TTGammaEFT.Tools.cutInterpreter   import cutInterpreter
from TTGammaEFT.Tools.TriggerSelector  import TriggerSelector

from TTGammaEFT.Analysis.SetupHelpers  import *
from TTGammaEFT.Analysis.Setup         import Setup
from TTGammaEFT.Analysis.EstimatorList import EstimatorList

from TTGammaEFT.Samples.color          import color
from Analysis.Tools.MergingDirDB      import MergingDirDB

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                        help="Log level for logging")
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv47_v2",                                             help="plot sub-directory")
argParser.add_argument("--year",               action="store",      default="2016",   type=str,  choices=["2016","2017","2018","RunII"],                     help="Which year to plot?")
argParser.add_argument("--selection",          action="store",      default="SR3p", type=str,                                              help="reco region")
argParser.add_argument("--addCut",             action="store",      default=None, type=str,                                                  help="additional cuts")
argParser.add_argument("--mode",               action="store",      default="all",  type=str,  choices=["mu", "eetight", "mumutight", "e", "all"],                   help="lepton selection")
args = argParser.parse_args()

if args.year != "RunII": args.year = int(args.year)

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile=None )
logger_rt = logger_rt.get_logger( args.logLevel, logFile=None )

# Text on the plots
def drawObjects( lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    line = (0.68, 0.95, "%3.1f fb^{-1} (13 TeV)" % lumi_scale)
    lines = [
      (0.15, 0.95, "CMS #bf{#it{Preliminary}}"),
      line
    ]
    return [tex.DrawLatex(*l) for l in lines]

# Sample definition
os.environ["gammaSkim"]="False" #always false for QCD estimate
if args.year == 2016:
    import TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed as mc_samples
    lumi_scale   = 35.92
elif args.year == 2017:
    import TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed as mc_samples
    lumi_scale   = 41.53
elif args.year == 2018:
    import TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed as mc_samples
    lumi_scale   = 59.74
elif args.year == "RunII":
    import TTGammaEFT.Samples.nanoTuples_RunII_postProcessed as mc_samples
    lumi_scale   = 137.2

sample = mc_samples.WG_NLO
#sample = mc_samples.ZG

if len(args.selection.split("-")) == 1 and args.selection in allRegions.keys():
    print( "Plotting region from SetupHelpers: %s"%args.selection )

    channels = allRegions[args.selection]["channels"]
    parameters = allRegions[args.selection]["parameters"]
    parameters["nBTag"] = (0,-1)
    setup = Setup( year=args.year, photonSelection=False, checkOnly=False, runOnLxPlus=False ) #photonselection always false for qcd estimate
    setup = setup.sysClone( parameters=allRegions[args.selection]["parameters"] )

    selection = setup.selection( "MC", channel=args.mode, **setup.defaultParameters() )["prefix"]
    selection = cutInterpreter.cutString( selection )
    selection += "&&triggered==1"
    if args.addCut:
        selection += "&&" + cutInterpreter.cutString( args.addCut )

else:
    raise Exception("Region not implemented")

lumiString = "(35.92*(year==2016)+41.53*(year==2017)+59.74*(year==2018))"
ws   = "(%s*weight*reweightHEM*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF)"%lumiString
ws16 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2016))" %(ws, misIDSF_val[2016].val)
ws17 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2017))" %(ws, misIDSF_val[2017].val)
ws18 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2018))" %(ws, misIDSF_val[2018].val)

weightString  = ws # ws16 + ws17 +ws18

filterCutMc = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )#, skipVertexFilter=True )

sample0b  = copy.deepcopy(sample)
sample1b  = copy.deepcopy(sample)
sample2pb = copy.deepcopy(sample)

sample0b.setSelectionString( [ filterCutMc, "pTStitching==1", "overlapRemoval==1", "nGenBJet==0" ] )
sample0b.setWeightString( weightString )

sample1b.setSelectionString( [ filterCutMc, "pTStitching==1", "overlapRemoval==1", "nGenBJet==1" ] )
sample1b.setWeightString( weightString )

sample2pb.setSelectionString( [ filterCutMc, "pTStitching==1", "overlapRemoval==1", "nGenBJet>=2" ] )
sample2pb.setWeightString( weightString )

#variable = "GenPhotonCMSUnfold0_pt"
variable = "nBTagGood"
binning = [3, 0, 3]

sample0b.hist = sample0b.get1DHistoFromDraw( variable, binning=binning, selectionString=selection )
sample1b.hist = sample1b.get1DHistoFromDraw( variable, binning=binning, selectionString=selection )
sample2pb.hist = sample2pb.get1DHistoFromDraw( variable, binning=binning, selectionString=selection )

sample0b.hist.style         = styles.fillStyle( ROOT.kBlue+2 )
sample0b.hist.legendText    = sample.texName + " (0 gen-b)"

sample1b.hist.style         = styles.fillStyle( ROOT.kOrange+1 )
sample1b.hist.legendText    = sample.texName + " (1 gen-b)"

sample2pb.hist.style         = styles.fillStyle( ROOT.kRed-2 )
sample2pb.hist.legendText    = sample.texName + " (#geq 2 gen-b)"

histos     = [[sample0b.hist, sample1b.hist, sample2pb.hist][::-1]]

for h in histos[0]:
    h.GetXaxis().SetBinLabel( 1, "0" )
    h.GetXaxis().SetBinLabel( 2, "1" )
    h.GetXaxis().SetBinLabel( 3, "2" )

Plot.setDefaults()

plots = []
plots.append( Plot.fromHisto( sample.name + "_" + variable,             histos,        texX = "N_{b-tag}",                   texY = "Number of Events" ) )

selDir = args.selection
if args.addCut: selDir += "-" + args.addCut

for plot in plots:

    legend = [ (0.2,0.9-0.025*sum(map(len, plot.histos)),0.9,0.9), 3 ]

    for log in [True, False]:

        histModifications  = []
        histModifications += [lambda h: h.GetYaxis().SetTitleOffset(1.6)]

        plot_directory_ = os.path.join( plot_directory, "gluonSplitting", str(args.year), args.plot_directory, selDir, args.mode, "log" if log else "lin" )
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = log, sorting = False,
                       yRange = (0.3, "auto"),
#                       ratio = {'histos':[(2,1)], 'texY': 'stitched/incl'},
                       drawObjects = drawObjects( lumi_scale ),
                       legend = legend,
                       histModifications = histModifications,
                       copyIndexPHP = True,
                       )

