## Standard imports
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
from TTGammaEFT.Tools.cutInterpreter   import cutInterpreter, chgIsoThresh, lowSieieThresh, highSieieThresh

#from TTGammaEFT.Tools.TriggerSelector  import TriggerSelector

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
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv26_v1",                                             help="plot sub-directory")
argParser.add_argument("--selection",          action="store",      default="WJets2", type=str,                                              help="reco region")
argParser.add_argument("--addCut",             action="store",      default=None, type=str,                                                  help="additional cuts")
argParser.add_argument("--variable",           action="store",      default="LeptonTight0_eta", type=str,                                    help="variable to plot")
#argParser.add_argument("--binning",            action="store",      default=[20,-2.4,2.4],  type=float, nargs="*",                           help="binning of plots")
argParser.add_argument("--year",               action="store",      default=2016,   type=int,  choices=[2016,2017,2018],                     help="Which year to plot?")
argParser.add_argument("--mode",               action="store",      default="all",  type=str,  choices=["mu", "e", "all"],                   help="lepton selection")
argParser.add_argument("--small",              action="store_true",                                                                          help="Run only on a small subset of the data?")
argParser.add_argument("--survey",             action="store_true",                                                                          help="all plots in one directory?")
argParser.add_argument("--photonCat",          action="store_true",                                                                          help="all plots in one directory?")
argParser.add_argument("--overwrite",          action="store_true",                                                                          help="overwrite cache?")
args = argParser.parse_args()

#binning[0] = int(args.binning[0])

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
    line = (0.65, 0.95, "%3.1f fb{}^{-1} (13 TeV)" % lumi_scale)
    lines = [
      (0.15, 0.95, "CMS #bf{#it{Preliminary}}"),
      line
    ]
    return [tex.DrawLatex(*l) for l in lines]

cache_dir = os.path.join(cache_directory, "drawHistos", str(args.year), args.selection, args.mode)
dirDB = MergingDirDB(cache_dir)
if not dirDB: raise

# Sample definition
os.environ["gammaSkim"]="True" #always false for QCD estimate
if args.year == 2016:
    from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed  import *
    from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import *
    mc          = all_mc
    data_sample = Run2016
elif args.year == 2017:
    from TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed    import *
    from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import *
    mc          = all_mc
    data_sample = Run2017
elif args.year == 2018:
    from TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed  import *
    from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import *
    mc          = all_mc
    data_sample = Run2018

lumi_scale   = data_sample.lumi * 0.001

filterCutMC = getFilterCut( args.year, isData=False,  skipBadChargedCandidate=True )
filterCutData = getFilterCut( args.year, isData=True,  skipBadChargedCandidate=True )

mc_high = copy.deepcopy(mc)
mc_low  = copy.deepcopy(mc)

data_high = copy.deepcopy(data_sample)
data_low  = copy.deepcopy(data_sample)

setup = Setup( year=args.year, photonSelection=False, checkOnly=False, runOnLxPlus=False ) #photonselection always false for qcd estimate
setup = setup.sysClone( parameters=allRegions[args.selection]["parameters"] )

selection = setup.selection( "MC", channel="all", **setup.defaultParameters() )["cut"]
selection += "&&pTStitching==1&&triggered==1"
if args.addCut:
    selection += "&&" + cutInterpreter.cutString( args.addCut )

dataselection = setup.selection( "Data", channel="all", **setup.defaultParameters() )["cut"]
dataselection += "&&triggered==1"
if args.addCut:
    dataselection += "&&" + cutInterpreter.cutString( args.addCut )
print( "Using selection string: %s"%selection )

if "2" in args.selection and not "2p" in args.selection:
    misIDSF_val = misID2SF_val
elif "3" in args.selection and not "3p" in args.selection:
    misIDSF_val = misID3SF_val
elif "4" in args.selection and not "4p" in args.selection:
    misIDSF_val = misID4SF_val
elif "5" in args.selection:
    misIDSF_val = misID5SF_val
elif "2p" in args.selection:
    misIDSF_val = misID2pSF_val
elif "3p" in args.selection:
    misIDSF_val = misID3pSF_val
elif "4p" in args.selection:
    misIDSF_val = misID4pSF_val

if args.variable.endswith("_sieie"):
    low = "lowChgIsoNoSieie"
    high = "highChgIsoNoSieie"
#    if args.year == 2016: bins = [0, lowSieieThresh]
#    else:                 bins = []
    bins = []
    bins += [highSieieThresh, 0.014, 0.018, 0.022, 0.026]
else:
    low = "lowSieieNoChgIso"
    high = "highSieieNoChgIso"
#    if args.year == 2016: bins = [0]
#    else:                 bins = []
    bins = []
    bins += [chgIsoThresh, 2+chgIsoThresh, 4+chgIsoThresh, 6+chgIsoThresh, 8+chgIsoThresh, 10+chgIsoThresh, 12+chgIsoThresh, 14+chgIsoThresh, 16+chgIsoThresh, 18+chgIsoThresh]



weightString    = "%f*weight*reweightHEM*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF"%lumi_scale
weightStringAR  = "((%s)+(%s*%f*((nPhotonNoChgIsoNoSieie>0)*(PhotonNoChgIsoNoSieie0_photonCatMagic==2))))"%(weightString,weightString,(misIDSF_val[args.year].val-1))
mc_high.setSelectionString( [filterCutMC, "reweightHEM>0", cutInterpreter.cutString( high+"-"+args.mode ), copy.deepcopy(selection)] )
mc_high.setWeightString( weightStringAR )

mc_low.setSelectionString( [filterCutMC, "reweightHEM>0", cutInterpreter.cutString( low+"-"+args.mode ), copy.deepcopy(selection)] )
mc_low.setWeightString( weightStringAR )

data_low.setSelectionString( [filterCutData, "reweightHEM>0", cutInterpreter.cutString( low+"-"+args.mode ), copy.deepcopy(dataselection)] )
data_low.setWeightString( "weight" )

data_high.setSelectionString( [filterCutData, "reweightHEM>0", cutInterpreter.cutString( high+"-"+args.mode ), copy.deepcopy(dataselection)] )
data_high.setWeightString( "weight" )


key = (mc_high.name, "high", args.variable, "_".join(map(str,bins)), mc_high.weightString, mc_high.selectionString)
if dirDB.contains(key) and not args.overwrite:
    mcHist_high = dirDB.get(key).Clone("high")
else:
    mcHist_high = mc_high.get1DHistoFromDraw( args.variable, binning=bins, binningIsExplicit=True, addOverFlowBin="upper" )
    dirDB.add(key, mcHist_high.Clone("high"), overwrite=True)

key = (mc_low.name, "low", args.variable, "_".join(map(str,bins)), mc_low.weightString, mc_low.selectionString)
if dirDB.contains(key) and not args.overwrite:
    mcHist_low = dirDB.get(key).Clone("low")
else:
    mcHist_low = mc_low.get1DHistoFromDraw( args.variable, binning=bins, binningIsExplicit=True, addOverFlowBin="upper" )
    dirDB.add(key, mcHist_low.Clone("low"), overwrite=True)

key = (data_high.name, "high", args.variable, "_".join(map(str,bins)), data_high.weightString, data_high.selectionString)
if dirDB.contains(key) and not args.overwrite:
    dataHist_high = dirDB.get(key).Clone("high")
else:
    dataHist_high = data_high.get1DHistoFromDraw( args.variable, binning=bins, binningIsExplicit=True, addOverFlowBin="upper" )
    dirDB.add(key, dataHist_high.Clone("high"), overwrite=True)

key = (data_low.name, "low", args.variable, "_".join(map(str,bins)), data_low.weightString, data_low.selectionString)
if dirDB.contains(key) and not args.overwrite:
    dataHist_low = dirDB.get(key).Clone("low")
else:
    dataHist_low = data_low.get1DHistoFromDraw( args.variable, binning=bins, binningIsExplicit=True, addOverFlowBin="upper" )
    dirDB.add(key, dataHist_low.Clone("low"), overwrite=True)

replaceLabel = {
    "PhotonNoChgIsoNoSieie0_sieie": "#sigma_{i#eta i#eta}(#gamma)",
    "PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt": "chg.Iso(#gamma) [GeV]"
}
replaceLegendLabel = {
    "PhotonNoChgIsoNoSieie0_sieie": "chg.Iso(#gamma)",
    "PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt": "#sigma_{i#eta i#eta}(#gamma)",
}

mcHist_low.style         = styles.lineStyle( ROOT.kRed, width=3, errors=True )
mcHist_low.legendText    = "MC (low %s)"%replaceLegendLabel[args.variable]

mcHist_high.style         = styles.lineStyle( ROOT.kRed, width=3, errors=True )
mcHist_high.legendText    = "MC (high %s)"%replaceLegendLabel[args.variable]

dataHist_low.style         = styles.errorStyle( ROOT.kBlack )
dataHist_low.legendText    = "data (low %s)"%replaceLegendLabel[args.variable]

dataHist_high.style         = styles.errorStyle( ROOT.kBlack )
dataHist_high.legendText    = "data (high %s)"%replaceLegendLabel[args.variable]

ratioHist_low = dataHist_low.Clone("ratio_low")
ratioHist_low.style         = styles.lineStyle( ROOT.kBlack, width=3, errors=True )
ratioHist_low.legendText    = "data / MC (low %s)"%replaceLegendLabel[args.variable]
ratioHist_low.Divide(mcHist_low)

ratioHist_high = dataHist_high.Clone("ratio_high")
ratioHist_high.style         = styles.lineStyle( ROOT.kRed, width=3, errors=True )
ratioHist_high.legendText    = "data / MC (high %s)"%replaceLegendLabel[args.variable]
ratioHist_high.Divide(mcHist_high)

lowhistos   = [[mcHist_low],    [dataHist_low]   ]
highhistos  = [[mcHist_high],   [dataHist_high] ]
ratiohistos = [[ratioHist_low], [ratioHist_high]]



Plot.setDefaults()
plots = []
plots.append( Plot.fromHisto( args.variable + "_low",   lowhistos,   texX = replaceLabel[args.variable], texY = "Number of Events" ) )
plots.append( Plot.fromHisto( args.variable + "_high",  highhistos,  texX = replaceLabel[args.variable], texY = "Number of Events" ) )
plots.append( Plot.fromHisto( args.variable + "_ratio", ratiohistos, texX = replaceLabel[args.variable], texY = "Data / MC" ) )

for plot in plots:

    legend = (0.2,0.8,0.9,0.9)

    for log in [True, False]:

        ratio = {'yRange':(0.7,1.3), 'histos':[(1,0)], 'texY': 'Ratio' if "ratio" in plot.name else "Data / MC"}

        selDir = args.selection
        if args.addCut: selDir += "-" + args.addCut
        plot_directory_ = os.path.join( plot_directory, "fakeDoubleRatio", str(args.year), args.plot_directory, selDir, args.mode, "log" if log else "lin" )
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = log,
                       yRange = (0.3, "auto"),
                       ratio = ratio,
                       drawObjects = drawObjects( lumi_scale ),
                       scaling = { 0:1 },
                       legend = legend,
                       copyIndexPHP = True,
                       )

