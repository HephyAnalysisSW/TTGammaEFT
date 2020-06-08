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
argParser.add_argument("--year",               action="store",      default=2016,   type=int,  choices=[2016,2017,2018],                     help="Which year to plot?")
argParser.add_argument("--mode",               action="store",      default="None",  type=str,  choices=["mu", "e", "all", "None"],          help="lepton selection")
argParser.add_argument('--nJobs',              action='store',      default=1,         type=int, choices=[1,2,3],                            help="Maximum number of simultaneous jobs.")
argParser.add_argument('--job',                action='store',      default=0,         type=int, choices=[0,1,2],                            help="Run only job i")
argParser.add_argument("--small",              action="store_true",                                                                          help="Run only on a small subset of the data?")
argParser.add_argument("--overwrite",          action="store_true",                                                                          help="overwrite cache?")
argParser.add_argument("--survey",             action="store_true",                                                                          help="print all in one directory?")
args = argParser.parse_args()

args.binning[0] = int(args.binning[0])
addSF = True

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
    from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed  import *
    all = all_noQCD_16
elif args.year == 2017:
    from TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed    import *
    all = all_noQCD_16
elif args.year == 2018:
    from TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed  import *
    all = all_noQCD_18

slices = []
slices.append( {"color":ROOT.kBlue+2,   "sieie":"pSieie0To0.01015",   "chgIso":"pChgIso0To1.141"} )
slices.append( {"color":ROOT.kGreen-2,  "sieie":"pSieie0.011To0.013", "chgIso":"pChgIso1.141To6"} )
slices.append( {"color":ROOT.kOrange+2, "sieie":"pSieie0.013To0.015", "chgIso":"pChgIso6To12"} )
slices.append( {"color":ROOT.kRed-3,    "sieie":"pSieie0.015To0.017", "chgIso":"pChgIso12To18"} )
slices.append( {"color":ROOT.kAzure,    "sieie":"pSieie0.017",        "chgIso":"pChgIso18"} )

for i, dict in enumerate(slices):
    cut = dict["sieie" if "chg" in args.variable else "chgIso"]
    locals()["all_"+str(i)]         = copy.deepcopy(all)
    locals()["all_"+str(i)].color   = dict["color"]
    locals()["all_"+str(i)].setSelectionString( cutInterpreter.cutString( cut ) )
    locals()["all_"+str(i)].name    = "MC"+str(i)
    locals()["all_"+str(i)].texName = "MC "
    if "sieie" in args.variable:
        cutRange = cut.split("Iso")[1].lower()
        print cutRange
        low, high = map(float,cutRange.split("to")) if "to" in cutRange else ( float(cutRange), None )
        locals()["all_"+str(i)].texName += "%.2f #leq chg Iso < %.2f"%(low, high) if high else "chg Iso #geq %.2f"%(low)
    elif "chg" in args.variable:
        cutRange = cut.split("Sieie")[1].lower()
        print cutRange
        low, high = map(float,cutRange.split("to")) if "to" in cutRange else ( float(cutRange), None )
        locals()["all_"+str(i)].texName += "%.3f #leq #sigma_{i#etai#eta} < %.3f"%(low, high) if high else "#sigma_{i#etai#eta} #geq %.3f"%(low)

mc  = [ locals()["all_"+str(i)] for i in range(len(slices)) ]
print mc
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

for s in mc:
    s.addSelectionString( [ filterCutMc, "overlapRemoval==1", "triggered==1", selection ] )
    s.read_variables = read_variables

weightString       = "%f*weight*reweightHEM*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF"%lumi_scale
if not addSF:
    weightStringAR = weightString
else:
    weightStringAR = "( (%s) + ( %s*%f*( (nPhotonNoChgIsoNoSieie>0)*(PhotonNoChgIsoNoSieie0_photonCatMagic==2) ) ) )"%(weightString,weightString,(misIDSF_val[args.year].val-1))

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

plots = []
plots.append( Plot.fromHisto( args.variable + "_" + args.addCut if args.survey else args.variable, histos, texX = "chg.Iso(#gamma)" if "chg" in args.variable else "#sigma_{i#eta i#eta}", texY = "Number of Events" ) )

selDir = args.selection
if args.addCut and not args.survey: selDir += "-" + args.addCut

for plot in plots:

    legend = [ (0.2,0.8-0.025*sum(map(len, plot.histos)),0.9,0.9), 2 ]

    for log in [True, False]:
        plot_directory_ = os.path.join( plot_directory, "fakeRatio", str(args.year), args.plot_directory, selDir, args.mode, "log" if log else "lin" )
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = log, sorting = True,
                       yRange = (0.3, "auto"),
                       ratio = {'yRange':(0.1,1.9), 'histos':[(i+1,0) for i in range(len(slices)-1)], 'texY': 'SB/SR', 'yRange':(0.1,1.9)} if plot.name != "ratio" else None,
                       scaling = { i+1:0 for i in range(len(slices)-1)} if plot.name != "ratio" else {},
                       drawObjects = drawObjects( lumi_scale ),
                       legend = legend,
                       copyIndexPHP = True,
                       )

