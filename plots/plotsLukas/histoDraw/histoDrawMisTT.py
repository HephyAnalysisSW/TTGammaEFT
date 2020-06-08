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
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv26_v1",                                             help="plot sub-directory")
argParser.add_argument("--selection",          action="store",      default="WJets2", type=str,                                              help="reco region")
argParser.add_argument("--addCut",             action="store",      default=None, type=str,                                                  help="additional cuts")
argParser.add_argument("--variable",           action="store",      default="LeptonTight0_eta", type=str,                                    help="variable to plot")
argParser.add_argument("--binning",            action="store",      default=[20,-2.4,2.4],  type=float, nargs="*",                           help="binning of plots")
argParser.add_argument("--year",               action="store",      default=2016,   type=int,  choices=[2016,2017,2018],                     help="Which year to plot?")
argParser.add_argument("--mode",               action="store",      default="all",  type=str,  choices=["mu", "e", "all"],                   help="lepton selection")
argParser.add_argument("--small",              action="store_true",                                                                          help="Run only on a small subset of the data?")
argParser.add_argument("--overwrite",          action="store_true",                                                                          help="overwrite cache?")
argParser.add_argument("--postfit",            action="store_true",                                                                          help="overwrite cache?")
args = argParser.parse_args()

args.binning[0] = int(args.binning[0])
addSF = args.postfit

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
os.environ["gammaSkim"]="False" #always false for QCD estimate
if args.year == 2016:
    import TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed as mc_samples
    from   TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import Run2016 as data_sample
elif args.year == 2017:
    import TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed as mc_samples
    from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import Run2017 as data_sample
elif args.year == 2018:
    import TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed as mc_samples
    from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import Run2018 as data_sample

mc = [ mc_samples.TTG, mc_samples.Top, mc_samples.DY_LO, mc_samples.WJets, mc_samples.WG, mc_samples.ZG, mc_samples.rest ]

read_variables_MC = ["isTTGamma/I", "isZWGamma/I", "isTGamma/I", "overlapRemoval/I",
                     "reweightPU/F", "reweightPUDown/F", "reweightPUUp/F", "reweightPUVDown/F", "reweightPUVUp/F",
                     "reweightLeptonTightSF/F", "reweightLeptonTightSFUp/F", "reweightLeptonTightSFDown/F",
                     "reweightLeptonTrackingTightSF/F",
                     "reweightTrigger/F", "reweightTriggerUp/F", "reweightTriggerDown/F",
                     "reweightInvIsoTrigger/F", "reweightInvIsoTriggerUp/F", "reweightInvIsoTriggerDown/F",
                     "reweightPhotonSF/F", "reweightPhotonSFUp/F", "reweightPhotonSFDown/F",
                     "reweightPhotonElectronVetoSF/F",
                     "reweightBTag_SF/F", "reweightBTag_SF_b_Down/F", "reweightBTag_SF_b_Up/F", "reweightBTag_SF_l_Down/F", "reweightBTag_SF_l_Up/F",
                     'reweightL1Prefire/F', 'reweightL1PrefireUp/F', 'reweightL1PrefireDown/F',
                    ]
read_variables = [ "weight/F",
                   "mT/F",
                   "mTinv/F",
                 ]

lumi_scale   = data_sample.lumi * 0.001

if "2" in args.selection and not "2p" in args.selection:
    DYSF_val    = DY2SF_val
    misIDSF_val = misID2SF_val
    WGSF_val    = WG2SF_val
    ZGSF_val    = ZG2SF_val
    QCDSF_val   = QCD2SF_val
elif "3" in args.selection and not "3p" in args.selection:
    DYSF_val    = DY3SF_val
    misIDSF_val = misID3SF_val
    WGSF_val    = WG3SF_val
    ZGSF_val    = ZG3SF_val
    QCDSF_val   = QCD3SF_val
elif "4" in args.selection and not "4p" in args.selection:
    DYSF_val    = DY4SF_val
    misIDSF_val = misID4SF_val
    WGSF_val    = WG4SF_val
    ZGSF_val    = ZG4SF_val
    QCDSF_val   = QCD4SF_val
elif "5" in args.selection:
    DYSF_val    = DY5SF_val
    misIDSF_val = misID5SF_val
    WGSF_val    = WG5SF_val
    ZGSF_val    = ZG5SF_val
    QCDSF_val   = QCD5SF_val
elif "2p" in args.selection:
    DYSF_val    = DY2pSF_val
    misIDSF_val = misID2pSF_val
    WGSF_val    = WG2pSF_val
    ZGSF_val    = ZG2pSF_val
    QCDSF_val   = QCD2pSF_val
elif "3p" in args.selection:
    DYSF_val    = DY3pSF_val
    misIDSF_val = misID3pSF_val
    WGSF_val    = WG3pSF_val
    ZGSF_val    = ZG3pSF_val
    QCDSF_val   = QCD3pSF_val
elif "4p" in args.selection:
    DYSF_val    = DY4pSF_val
    misIDSF_val = misID4pSF_val
    WGSF_val    = WG4pSF_val
    ZGSF_val    = ZG4pSF_val
    QCDSF_val   = QCD4pSF_val

print misIDSF_val

filterCutData = getFilterCut( args.year, isData=True,  skipBadChargedCandidate=True )#, skipVertexFilter=True )
filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )#, skipVertexFilter=True )
#tr            = TriggerSelector( args.year, singleLepton=True )
#triggerCutMc  = tr.getSelection( "MC" )

data_sample.setSelectionString( [filterCutData, "reweightHEM>0.1"] )
data_sample.setWeightString( "weight" )
if args.small:           
    data_sample.normalization = 1.
    data_sample.reduceFiles( factor=5 )
    data_sample.setWeightString( "weight*%f"%(1./data_sample.normalization) )

print data_sample.selectionString

for s in mc:
    s.setSelectionString( [ filterCutMc, "overlapRemoval==1" ] )
    s.read_variables = read_variables_MC
    sampleWeight     = "1"
    if args.small:           
        s.normalization = 1.
        s.reduceFiles( factor=100 )
        sampleWeight = "%f"%(1./s.normalization)

if len(args.selection.split("-")) == 1 and args.selection in allRegions.keys():
    print( "Plotting region from SetupHelpers: %s"%args.selection )

    setup = Setup( year=args.year, photonSelection=False, checkOnly=False, runOnLxPlus=False ) #photonselection always false for qcd estimate
    setup = setup.sysClone( parameters=allRegions[args.selection]["parameters"] )

    selection = setup.selection( "MC", channel=args.mode, **setup.defaultParameters() )["prefix"]
    selection = cutInterpreter.cutString( selection )
    selection += "&&triggered==1"
    if args.addCut:
        print cutInterpreter.cutString( args.addCut )
        selection += "&&" + cutInterpreter.cutString( args.addCut )
    print( "Using selection string: %s"%args.selection )

    preSelection  = setup.selection("MC",   channel=args.mode, **setup.defaultParameters(update=QCD_updates))["prefix"]
    preSelection  = cutInterpreter.cutString( preSelection )
    preSelection += "&&triggeredInvIso==1"
    if args.addCut:
        addSel = cutInterpreter.cutString( args.addCut )
        for iso, invIso in replaceSelection.iteritems():
            addSel = addSel.replace(iso,invIso)
        preSelection += "&&" + addSel

else:
    raise Exception("Region not implemented")

weightString    = "%f*weight*reweightHEM*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF"%lumi_scale
if not addSF:
    weightStringAR  = weightString
else:
    weightStringAR  = "((%s)+(%s*%f*((nPhotonGood>0)*(PhotonGood0_photonCatMagic==2))))"%(weightString,weightString,(misIDSF_val[args.year].val-1))

key = (data_sample.name, "AR", args.variable, "_".join(map(str,args.binning)), data_sample.weightString, data_sample.selectionString, selection)
if dirDB.contains(key) and not args.overwrite:
    dataHist = dirDB.get(key).Clone("dataAR")
else:
    dataHist = data_sample.get1DHistoFromDraw( args.variable, binning=args.binning, selectionString=selection, addOverFlowBin="upper" )
    dirDB.add(key, dataHist.Clone("dataAR"), overwrite=True)

for s in mc:
    s.setWeightString( weightStringAR + "*" + sampleWeight )
    key = (s.name, "AR", args.variable, "_".join(map(str,args.binning)), s.weightString, s.selectionString, selection)
    if dirDB.contains(key) and not args.overwrite:
        s.hist = copy.deepcopy(dirDB.get(key).Clone(s.name+"AR"))
    else:
        s.hist = s.get1DHistoFromDraw( args.variable, binning=args.binning, selectionString=selection, addOverFlowBin="upper" )
        dirDB.add(key, s.hist.Clone("%s_AR"%s.name), overwrite=True)

    if addSF:
            if "DY" in s.name:
                s.hist.Scale(DYSF_val[args.year].val)
            elif "ZG" in s.name:# and njets < 4:
                s.hist.Scale(ZGSF_val[args.year].val)
            elif "WG" in s.name:# and njets > 3:
                s.hist.Scale(WGSF_val[args.year].val)
            elif "TTG" in s.name:
                s.hist.Scale(SSMSF_val[args.year].val)

    s.hist.style         = styles.fillStyle( s.color )
    s.hist.legendText    = s.texName
    s.hist.GetXaxis().SetBinLabel( 1, "#mu" )
    s.hist.GetXaxis().SetBinLabel( 2, "e" )

dataHist.style         = styles.errorStyle( ROOT.kBlack )
dataHist.legendText    = "data (%s)"%args.mode.replace("mu","#mu")
dataHist.GetXaxis().SetBinLabel( 1, "#mu" )
dataHist.GetXaxis().SetBinLabel( 2, "e" )

histos     = [[s.hist    for s in mc], [dataHist]]

Plot.setDefaults()

plots = []
plots.append( Plot.fromHisto( args.variable,             histos,        texX = "yield",                   texY = "Number of Events" ) )

for plot in plots:

    legend = [ (0.2,0.9-0.025*sum(map(len, plot.histos)),0.9,0.9), 3 ]

    for log in [True, False]:

        ratio = {'yRange':(0.1,1.9)}

        selDir = args.selection
        if args.addCut: selDir += "-" + args.addCut
        plot_directory_ = os.path.join( plot_directory, "misTTChecks", str(args.year), args.plot_directory, selDir, "postfit" if addSF else "prefit", args.mode, "log" if log else "lin" )
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = log, sorting = True,
                       yRange = (0.3, "auto"),
                       ratio = ratio,
                       drawObjects = drawObjects( lumi_scale ),
                       legend = legend,
                       copyIndexPHP = True,
                       )

