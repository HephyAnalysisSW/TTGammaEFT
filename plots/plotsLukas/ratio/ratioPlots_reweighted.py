# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy

# RootTools
from RootTools.core.standard           import *

# Analysis
from Analysis.Tools.metFilters         import getFilterCut

# Internal Imports
from TTGammaEFT.Tools.user             import plot_directory, cache_directory
from TTGammaEFT.Tools.helpers         import splitList
from TTGammaEFT.Tools.cutInterpreter   import cutInterpreter
from TTGammaEFT.Tools.TriggerSelector  import TriggerSelector

from TTGammaEFT.Tools.Variables       import NanoVariables
from TTGammaEFT.Analysis.SetupHelpers  import *
from TTGammaEFT.Analysis.Setup         import Setup
from TTGammaEFT.Analysis.EstimatorList import EstimatorList

from TTGammaEFT.Samples.color          import color
import Analysis.Tools.syncer as syncer
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
argParser.add_argument("--binning",            action="store",      default=[20,-2.4,2.4],  type=float, nargs="*",                           help="binning of plots")
argParser.add_argument("--year",               action="store",      default="2016",   type=str,  choices=["2016","2017","2018","RunII"],                     help="Which year to plot?")
argParser.add_argument("--mode",               action="store",      default="None",  type=str,  choices=["mu", "e", "all", "None"],          help="lepton selection")
argParser.add_argument('--nJobs',              action='store',      default=1,         type=int, choices=[1,2,3],                            help="Maximum number of simultaneous jobs.")
argParser.add_argument('--job',                action='store',      default=0,         type=int, choices=[0,1,2],                            help="Run only job i")
argParser.add_argument("--small",              action="store_true",                                                                          help="Run only on a small subset of the data?")
argParser.add_argument("--overwrite",          action="store_true",                                                                          help="overwrite cache?")
argParser.add_argument("--survey",             action="store_true",                                                                          help="print all in one directory?")
argParser.add_argument("--reweight",           action="store_true",                                                                          help="reweight histos?")
args = argParser.parse_args()

args.binning[0] = int(args.binning[0])
addSF = True
if args.year != "RunII": args.year = int(args.year)

if args.mode == "None":
    allModes = [ "mu", "e", "all" ]
    args.mode = allModes[args.job]

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile=None )
logger_rt = logger_rt.get_logger( args.logLevel, logFile=None )

if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74
elif args.year == "RunII": lumi_scale = 35.92 + 41.53 + 59.74

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
os.environ["gammaSkim"]="False" #always false for QCD estimate
if args.year == 2016:
    import TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed as mc_samples
elif args.year == 2017:
    import TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed as mc_samples
elif args.year == 2018:
    import TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed  as mc_samples
elif args.year == "RunII":
    import TTGammaEFT.Samples.nanoTuples_RunII_postProcessed as mc_samples

all = mc_samples.all_noQCD

all_sb = copy.deepcopy(all)
all_sb.name = "sb"
all_sb.texName  = "MC "
if "sieie" in args.variable:
    all_sb.texName += "high chg Iso"
elif "chg" in args.variable:
    all_sb.texName += "high #sigma_{i#etai#eta}"
all_sb.color   = ROOT.kRed+2

all_fit = copy.deepcopy(all)
all_fit.name = "fit"
all_fit.texName  = "MC "
if "sieie" in args.variable:
    all_fit.texName += "low chg Iso"
elif "chg" in args.variable:
    all_fit.texName += "low #sigma_{i#etai#eta}"
all_fit.color   = ROOT.kCyan+2

mc  = [ all_fit, all_sb ]
stackSamples  = [ [s] for s in mc ]

NanoVars         = NanoVariables( args.year )
photonVariables  = NanoVars.getVariables( "Photon", postprocessed=True, data=False, plot=True )

read_variables = [ "weight/F",
                   "isTTGamma/I", "isZWGamma/I", "isTGamma/I", "overlapRemoval/I",
                   "reweightPU/F", "reweightPUDown/F", "reweightPUUp/F", "reweightPUVDown/F", "reweightPUVUp/F",
                   "reweightLeptonTightSF/F", "reweightLeptonTightSFUp/F", "reweightLeptonTightSFDown/F",
                   "reweightLeptonTrackingTightSF/F",
                   "reweightLeptonMediumSF/F", "reweightLeptonMediumSFUp/F", "reweightLeptonMediumSFDown/F",
                   "reweightLeptonTracking2lSF/F",
                   "reweightTrigger/F", "reweightTriggerUp/F", "reweightTriggerDown/F",
                   "reweightInvIsoTrigger/F", "reweightInvIsoTriggerUp/F", "reweightInvIsoTriggerDown/F",
                   "reweightPhotonSF/F", "reweightPhotonSFUp/F", "reweightPhotonSFDown/F",
                   "reweightPhotonElectronVetoSF/F",
                   "reweightBTag_SF/F", "reweightBTag_SF_b_Down/F", "reweightBTag_SF_b_Up/F", "reweightBTag_SF_l_Down/F", "reweightBTag_SF_l_Up/F",
                   'reweightL1Prefire/F', 'reweightL1PrefireUp/F', 'reweightL1PrefireDown/F',
                   "reweightHEM/F",
                  ]
read_variables    += map( lambda var: "PhotonNoChgIsoNoSieie0_" + var, photonVariables )

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

print misIDSF_val

filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )#, skipVertexFilter=True )

if len(args.selection.split("-")) == 1 and args.selection in allRegions.keys():
    print( "Plotting region from SetupHelpers: %s"%args.selection )

    setup = Setup( year=args.year, photonSelection=False, checkOnly=False, runOnLxPlus=False ) #photonselection always false for qcd estimate
    setup = setup.sysClone( parameters=allRegions[args.selection]["parameters"] )

    selection = setup.selection( "MC", channel=args.mode, **setup.defaultParameters() )["prefix"]
    selection = cutInterpreter.cutString( selection )
    if args.addCut:
        print cutInterpreter.cutString( args.addCut )
        selection += "&&" + cutInterpreter.cutString( args.addCut )
    print( "Using selection string: %s"%args.selection )

else:
    raise Exception("Region not implemented")

selectionString = "&&".join( [ filterCutMc, "pTStitching==1", "overlapRemoval==1", "triggered==1", selection ] )
for s in mc:
    s.setSelectionString( selectionString )
    s.read_variables = read_variables

all_fit.addSelectionString( cutInterpreter.cutString( "lowSieieNoChgIso" if "chg" in args.variable else "lowChgIsoNoSieie"   ) )
all_sb.addSelectionString(  cutInterpreter.cutString( "highSieieNoChgIso" if "chg" in args.variable else "highChgIsoNoSieie" ) )

lumiString = "(35.92*(year==2016)+41.53*(year==2017)+59.74*(year==2018))"
ws = "(%s*weight*reweightHEM*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF)"%lumiString
if not addSF:
    weightStringAR  = ws
    sampleWeight = lambda event, sample: lumi_scale*event.reweightHEM*event.reweightTrigger*event.reweightL1Prefire*event.reweightPU*event.reweightLeptonTightSF*event.reweightLeptonTrackingTightSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF
else:
    ws16 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2016))" %(ws, misIDSF_val[2016].val)
    ws17 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2017))" %(ws, misIDSF_val[2017].val)
    ws18 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2018))" %(ws, misIDSF_val[2018].val)
    weightStringAR = ws + ws16 + ws17 + ws18
    sampleWeight = lambda event, sample: ((35.92*(event.year==2016)+41.53*(event.year==2017)+59.74*(event.year==2018))*event.reweightHEM*event.reweightTrigger*event.reweightL1Prefire*event.reweightPU*event.reweightLeptonTightSF*event.reweightLeptonTrackingTightSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF)*( misIDSF_val[2016].val if event.PhotonNoChgIsoNoSieie0_photonCatMagic==2 and event.year == 2016 else 1. )*( misIDSF_val[2017].val if event.PhotonNoChgIsoNoSieie0_photonCatMagic==2 and event.year == 2017 else 1. )*( misIDSF_val[2018].val if event.PhotonNoChgIsoNoSieie0_photonCatMagic==2 and event.year == 2018 else 1. )

for s in mc:
    s.setWeightString( weightStringAR )
    key = (s.name, "AR", args.variable, "_".join(map(str,args.binning)), s.weightString, s.selectionString, selection)
    if dirDB.contains(key) and not args.overwrite:
        s.hist = copy.deepcopy(dirDB.get(key).Clone(s.name+"AR"))
    else:
        s.hist = s.get1DHistoFromDraw( args.variable, binning=args.binning, selectionString=selection )#, addOverFlowBin="upper" )
        dirDB.add(key, s.hist.Clone("%s_AR"%s.name))

    s.style              = styles.lineStyle( s.color, width = 2, dotted=False, dashed=False, errors = True )
    s.hist.style         = styles.lineStyle( s.color, width = 2, dotted=False, dashed=False, errors = True )
    s.hist.legendText    = s.texName

histos     = [[s.hist]    for s in mc]

Plot.setDefaults()

weightHist = all_fit.hist.Clone("weight")
if all_fit.hist.Integral(): weightHist.Scale( all_sb.hist.Integral() / all_fit.hist.Integral() )
else: raise
weightHist.Divide( all_sb.hist )

plots = []
plots.append( Plot.fromHisto( args.variable + "_" + args.addCut if args.survey else args.variable, histos, texX = "chg.Iso(#gamma)" if "chg" in args.variable else "#sigma_{i#eta i#eta}", texY = "Number of Events" ) )
plots.append( Plot.fromHisto( "ratio_"+args.variable + "_" + args.addCut if args.survey else "ratio_"+args.variable, [[weightHist]], texX = "chg.Iso(#gamma)" if "chg" in args.variable else "#sigma_{i#eta i#eta}", texY = "Ratio" ) )

selDir = args.selection
if args.addCut and not args.survey: selDir += "-" + args.addCut

for plot in plots:

    legend = [ (0.2,0.9-0.025*sum(map(len, plot.histos)),0.9,0.9), 3 ]

    for log in [True, False]:
        plot_directory_ = os.path.join( plot_directory, "fakeRatio", str(args.year), args.plot_directory, selDir, args.mode, "log" if log else "lin" )
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = log, sorting = True,
                       yRange = (0.3, "auto"),
                       ratio = {'yRange':(0.1,1.9), 'histos':[(0,1)], 'texY': 'low/high', 'yRange':(0.1,1.9)} if plot.name != "ratio" else None,
                       scaling = { 0:1 } if plot.name != "ratio" else {},
                       drawObjects = drawObjects( lumi_scale ),
                       legend = legend,
                       copyIndexPHP = True,
                       )

if not args.reweight: sys.exit(0)

all_fit.setSelectionString( [selectionString, cutInterpreter.cutString( "lowChgIsoNoSieie" if "chg" in args.variable else "lowSieieNoChgIso" )] )
all_sb.setSelectionString(  [selectionString, cutInterpreter.cutString( "highChgIsoNoSieie" if "chg" in args.variable else "highSieieNoChgIso" )] )
all_fit.setWeightString( "1" )
all_sb.setWeightString( "1" )
all_fit.weight = sampleWeight
all_sb.weight  = sampleWeight

all_fit.texName  = "MC "
all_sb.texName  = "MC "
if "chg" in args.variable:
    all_fit.texName += "low chg Iso"
    all_sb.texName += "high chg Iso"
else:
    all_fit.texName += "low #sigma_{i#eta i#eta}"
    all_sb.texName += "high #sigma_{i#eta i#eta}"

# Use some defaults (set defaults before you create/import list of Plots!!)
stack = Stack( *stackSamples )
weight_ = lambda event, sample: event.weight
Plot.setDefaults( stack=stack, weight=staticmethod(weight_), selectionString=selectionString )#, addOverFlowBin="upper" )

plots = []
if "sieie" in args.variable:
    plots.append( Plot(
        name      = 'PhotonNoChgIsoNoSieie0_chgIso' + "_" + args.addCut + "_weighted" if args.survey else 'PhotonNoChgIsoNoSieie0_chgIso_weighted',
        texX      = 'chg.Iso(#gamma)',
        texY      = 'Number of Events',
        attribute = lambda event, sample: event.PhotonNoChgIsoNoSieie0_pfRelIso03_chg*event.PhotonNoChgIsoNoSieie0_pt,
        binning   = [20, 0, 22.82],
    ))
elif "chg" in args.variable:
    plots.append( Plot(
        name      = 'PhotonNoChgIsoNoSieie0_sieie' + "_" + args.addCut + "_weighted" if args.survey else 'PhotonNoChgIsoNoSieie0_sieie_weighted',
        texX      = '#sigma_{i#etai#eta}(#gamma)',
        texY      = 'Number of Events',
        attribute = TreeVariable.fromString( "PhotonNoChgIsoNoSieie0_sieie/F" ),
        binning   = [20, 0.005, 0.025],
    ))

weightHist = all_fit.hist.Clone("weight")
if all_fit.hist.Integral(): weightHist.Scale( all_sb.hist.Integral() / all_fit.hist.Integral() )
else: raise
weightHist.Divide( all_sb.hist )

def reweight( event, sample ):
    if sample.name == "fit": return
    if "sieie" in args.variable:
        binx = weightHist.FindBin( event.PhotonNoChgIsoNoSieie0_sieie )
    elif "chg" in args.variable:
        binx = weightHist.FindBin( event.PhotonNoChgIsoNoSieie0_pfRelIso03_chg*event.PhotonNoChgIsoNoSieie0_pt )
    reweight = weightHist.GetBinContent( binx )
    event.weight *= reweight

# Sequence
sequence = [ reweight ]

plotting.fill( plots, read_variables=read_variables, sequence=sequence )

# Plotting
for log in [False, True]:
    plot_directory_ = os.path.join( plot_directory, "fakeRatio", str(args.year), args.plot_directory, selDir, args.mode, "log" if log else "lin" )

    for plot in plots:
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       ratio = {'yRange':(0.1,1.9), 'histos':[(0,1)], 'texY': 'low/high', 'yRange':(0.1,1.9)},
                       logX = False, logY = log, sorting = False,
                       yRange = (0.03, "auto") if log else (0.001, "auto"),
                       scaling = { 0:1 },
                       legend = [ (0.2,0.87-0.04*sum(map(len, plot.histos)),0.8,0.87), 1],
                       drawObjects = drawObjects( lumi_scale ),
                       copyIndexPHP = True
                     )

