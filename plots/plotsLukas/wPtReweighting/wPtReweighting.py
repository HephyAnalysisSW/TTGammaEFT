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

ptBins  = [0, 45, 65, 80, 100, 120, -1]
etaBins = [0, 1.479, 1.7, 2.1, -1]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                        help="Log level for logging")
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv26_v1",                                             help="plot sub-directory")
argParser.add_argument("--selection",          action="store",      default="WJets2", type=str,                                              help="reco region")
argParser.add_argument("--addCut",             action="store",      default=None, type=str,                                                  help="additional cuts")
#argParser.add_argument("--variable",           action="store",      default="LeptonTight0_eta", type=str,                                    help="variable to plot")
argParser.add_argument("--binning",            action="store",      default=[20,-2.4,2.4],  type=float, nargs="*",                           help="binning of plots")
argParser.add_argument("--year",               action="store",      default="2016",   type=str,  choices=["2016","2017","2018","RunII"],                     help="Which year to plot?")
argParser.add_argument("--mode",               action="store",      default="all",  type=str,  choices=["mu", "e", "all"],                   help="lepton selection")
argParser.add_argument("--small",              action="store_true",                                                                          help="Run only on a small subset of the data?")
argParser.add_argument("--overwrite",          action="store_true",                                                                          help="overwrite cache?")
args = argParser.parse_args()

if args.year != "RunII": args.year = int(args.year)

args.binning[0] = int(args.binning[0])
variable    = "WPt"
invVariable = "WinvPt"
addSF = True

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

cache_dir = os.path.join(cache_directory, "WPtHistos", str(args.year), args.selection, args.mode)
dirDB = MergingDirDB(cache_dir)
if not dirDB: raise

# Sample definition
os.environ["gammaSkim"]="False" #always false for QCD estimate
if args.year == 2016:
    from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed  import *
    from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import *
    mc          = [ TTG_16, Top_16, DY_LO_16, WJets_16, WG_16, ZG_16, rest_16 ]
    ttg         = TTG_16
    tt          = Top_16
    wjets       = WJets_16
    ttg         = TTG_16
    wg          = WG_16
    other       = rest_16
    data_sample = Run2016
elif args.year == 2017:
    from TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed    import *
    from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import *
    mc          = [ TTG_17, Top_17, DY_LO_17, WJets_17, WG_17, ZG_17, rest_17 ]
    ttg         = TTG_17
    tt          = Top_17
    wjets       = WJets_17
    ttg         = TTG_17
    wg          = WG_17
    other       = rest_17
    data_sample = Run2017
elif args.year == 2018:
    from TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed  import *
    from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import *
    mc          = [ TTG_18, Top_18, DY_LO_18, WJets_18, WG_18, ZG_18, rest_18 ]
    ttg         = TTG_18
    tt          = Top_18
    wjets       = WJets_18
    ttg         = TTG_18
    wg          = WG_18
    other       = rest_18
    data_sample = Run2018

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

data_sample.setSelectionString( [filterCutData, "reweightHEM>0"] )
data_sample.setWeightString( "weight" )
if args.small:           
    data_sample.normalization = 1.
    data_sample.reduceFiles( factor=5 )
    data_sample.setWeightString( "weight*%f"%(1./data_sample.normalization) )

print data_sample.selectionString

for s in mc:
    s.setSelectionString( [ filterCutMc, "pTStitching==1", "overlapRemoval==1" ] )
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
weightStringIL  = "%f*weight*reweightHEM*reweightInvIsoTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSFInvIso*reweightLeptonTrackingTightSFInvIso*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF"%lumi_scale
weightStringInv = weightStringIL
weightStringAR  = weightString

# get cached transferfactors
estimators = EstimatorList( setup, processes=["QCD-DD"] )
estimate   = getattr(estimators, "QCD-DD")
estimate.initCache(setup.defaultCacheDir())

# Accounting for 
leptonPtCutVar = "LeptonTightInvIso0_pt"
if args.mode == "e":
    leptonEtaCutVar = "abs(LeptonTightInvIso0_eta+LeptonTightInvIso0_deltaEtaSC)"
else:
    leptonEtaCutVar = "abs(LeptonTightInvIso0_eta)"

QCDTF_updates_2J = copy.deepcopy(QCDTF_updates)

key = (data_sample.name, "AR", variable, "_".join(map(str,args.binning)), data_sample.weightString, data_sample.selectionString, selection)
if dirDB.contains(key) and not args.overwrite:
    dataHist = dirDB.get(key).Clone("dataAR")
else:
    dataHist = data_sample.get1DHistoFromDraw( variable, binning=args.binning, selectionString=selection, addOverFlowBin="upper" )
    dirDB.add(key, dataHist.Clone("dataAR"))

dataHist_SB  = dataHist.Clone("data_SB")
dataHist_SB.Scale(0)

qcdHist = dataHist.Clone("qcd")
qcdHist.Scale(0)

for s in mc:
    s.setWeightString( weightStringAR + "*" + sampleWeight )
    key = (s.name, "AR", variable, "_".join(map(str,args.binning)), s.weightString, s.selectionString, selection)
    if dirDB.contains(key) and not args.overwrite:
        s.hist = copy.deepcopy(dirDB.get(key).Clone(s.name+"AR"))
    else:
        s.hist = s.get1DHistoFromDraw( variable, binning=args.binning, selectionString=selection, addOverFlowBin="upper" )
        dirDB.add(key, s.hist.Clone("%s_AR"%s.name))

    if addSF:
            if "DY" in s.name:
                s.hist.Scale(DYSF_val[args.year].val)
            elif "WJets" in s.name:
                s.hist.Scale(WJetsSF_val[args.year].val)

    s.hist_SB = copy.deepcopy(dataHist.Clone(s.name+"_SB"))
    s.hist_SB.Scale(0)

    s.hist_SB.style      = styles.fillStyle( s.color )
    s.hist_SB.legendText = s.texName
    s.hist.style         = styles.fillStyle( s.color )
    s.hist.legendText    = s.texName

dataHist_SB.style      = styles.errorStyle( ROOT.kBlack )
dataHist_SB.legendText = "data (%s)"%args.mode.replace("mu","#mu")
dataHist.style         = styles.errorStyle( ROOT.kBlack )
dataHist.legendText    = "data (%s)"%args.mode.replace("mu","#mu")

#oneHist = dataHist.Clone("one")
#oneHist.notInLegend = True
#oneHist.style = styles.lineStyle( ROOT.kWhite, width=0 )
#for i in range(oneHist.GetNbinsX()):
#    oneHist.SetBinContent(i+1, 1)



for i_pt, pt in enumerate(ptBins[:-1]):
    for i_eta, eta in enumerate(etaBins[:-1]):
        etaLow, etaHigh = eta, etaBins[i_eta+1]
        ptLow, ptHigh   = pt,  ptBins[i_pt+1]

        # Remove that for now
        # define the 2016 e-channel QCD sideband in barrel only (bad mT fit in EC)
        if False and args.mode == "e" and args.year == 2016 and (etaHigh > 1.479 or etaHigh < 0):
            leptonPtEtaCut  = [ leptonEtaCutVar + ">=0", leptonPtCutVar + ">=" + str(ptLow) ]
            leptonPtEtaCut += [ leptonEtaCutVar + "<1.479" ]
            if ptHigh > 0:  leptonPtEtaCut += [ leptonPtCutVar + "<" + str(ptHigh) ]
        else:
            leptonPtEtaCut = [ leptonEtaCutVar + ">=" + str(etaLow), leptonPtCutVar + ">=" + str(ptLow) ]
            if etaHigh > 0: leptonPtEtaCut += [ leptonEtaCutVar + "<" + str(etaHigh) ]
            if ptHigh > 0:  leptonPtEtaCut += [ leptonPtCutVar + "<" + str(ptHigh) ]

        leptonPtEtaCut = "&&".join( [preSelection] + leptonPtEtaCut )

        print "Running histograms for qcd selection:"
        print leptonPtEtaCut

        # histos
        key = (data_sample.name, "SB", variable, "_".join(map(str,args.binning)), data_sample.weightString, data_sample.selectionString, leptonPtEtaCut)
        if dirDB.contains(key) and not args.overwrite:
            dataHist_SB_tmp = dirDB.get(key).Clone("dataSB")
        else:
            dataHist_SB_tmp = data_sample.get1DHistoFromDraw( invVariable, binning=args.binning, selectionString=leptonPtEtaCut, addOverFlowBin="upper" )
            dirDB.add(key, dataHist_SB_tmp.Clone("dataSB"))

        dataHist_SB.Add(dataHist_SB_tmp)
        qcdHist_tmp = dataHist_SB_tmp.Clone("qcdtmp_%i_%i"%(i_pt,i_eta))

        for s in mc:
            s.setWeightString( weightStringInv + "*" + sampleWeight )
            key = (s.name, "SB", variable, "_".join(map(str,args.binning)), s.weightString, s.selectionString, leptonPtEtaCut)
            if dirDB.contains(key) and not args.overwrite:
                s.hist_SB_tmp = dirDB.get(key).Clone(s.name+"SB")
            else:
                s.hist_SB_tmp = s.get1DHistoFromDraw( invVariable, binning=args.binning, selectionString=leptonPtEtaCut, addOverFlowBin="upper" )
                dirDB.add(key, s.hist_SB_tmp.Clone("%s_SB"%s.name))

            # apply SF after histo caching
            if True: #addSF:
                    if "DY" in s.name:
                        s.hist_SB_tmp.Scale(DYSF_val[args.year].val)
                    elif "WJets" in s.name:
                        s.hist_SB_tmp.Scale(WJetsSF_val[args.year].val)

            s.hist_SB.Add(s.hist_SB_tmp)
            qcdHist_tmp.Add(s.hist_SB_tmp, -1)


        # Transfer Factor, get the QCD histograms always in barrel regions
        QCDTF_updates_2J["CR"]["leptonEta"] = ( etaLow, etaHigh )
        QCDTF_updates_2J["CR"]["leptonPt"]  = ( ptLow,  ptHigh   )
        QCDTF_updates_2J["SR"]["leptonEta"] = ( etaLow, etaHigh )
        QCDTF_updates_2J["SR"]["leptonPt"]  = ( ptLow,  ptHigh   )

        # REMOVE THAT FOR NOW
        # define the 2016 e-channel QCD sideband in barrel only (bad mT fit in EC)
        if False and args.mode == "e" and args.year == 2016 and (etaHigh > 1.479 or etaHigh < 0):
            QCDTF_updates_2J["CR"]["leptonEta"] = ( 0, 1.479 )

        qcdUpdates  = { "CR":QCDTF_updates_2J["CR"], "SR":QCDTF_updates_2J["SR"] }
        transferFac = estimate.cachedTransferFactor( args.mode, setup, qcdUpdates=qcdUpdates, overwrite=False, checkOnly=False )

        print "pt", ptLow, ptHigh, "eta", etaLow, etaHigh, "TF:", transferFac

        # remove negative bins
        for i in range(qcdHist_tmp.GetNbinsX()):
            if qcdHist_tmp.GetBinContent(i+1) < 0: qcdHist_tmp.SetBinContent(i+1, 0)

        qcdHist_tmp.Scale(transferFac.val)
        qcdHist.Add(qcdHist_tmp)


#sbInt = qcdHist.Integral()

qcdHist.style          = styles.fillStyle( color.QCD )
qcdHist.legendText     = "QCD (data)"

#qcdTemplate            = qcdHist.Clone("QCDTemplate")
#qcdTemplate.style      = styles.fillStyle( color.QCD )
#qcdTemplate.legendText = "QCD template (%i)"%int(sbInt)
#qcdTemplate.Scale(1./ qcdTemplate.Integral() )
#maxQCD = qcdTemplate.GetMaximum()

wPtWeightHist = dataHist.Clone(variable)
wPtWeightHist.Add( qcdHist, -1 )
for s in mc:
    if s.name == wjets.name: continue
    wPtWeightHist.Add( s.hist, -1 )
wPtWeightHist.Divide(wjets.hist)

wpt_cache_dir = os.path.join(cache_directory, "WPtHistos", str(args.year), "weight", args.mode)
dirDB_weight = MergingDirDB(wpt_cache_dir)
if not dirDB_weight: raise
key = args.selection
if args.addCut: key += "-" + args.addCut
dirDB_weight.add(key, wPtWeightHist.Clone("weight"))

histos     = [[s.hist    for s in mc] + [qcdHist], [dataHist]]
#histos_SB  = [[s.hist_SB for s in mc],             [dataHist_SB], [qcdTemplate], [oneHist]]

Plot.setDefaults()

plots = []
plots.append( Plot.fromHisto( variable,           histos,            texX = "p_{T}(W)",        texY = "Number of Events" ) )
plots.append( Plot.fromHisto( variable+"_weight", wPtWeightHist,     texX = "p_{T}(W) weight", texY = "Number of Events" ) )

for plot in plots:

    legend = [ (0.2,0.9-0.025*sum(map(len, plot.histos)),0.9,0.9), 3 ]

    for log in [True, False]:

#        if "sideband" in plot.name:
#            ratio = {'histos':[(2,3)], 'logY':log, 'texY': 'Template', 'yRange': (0.03, maxQCD*2) if log else (0.001, maxQCD*1.2)}
#        else:
        ratio = {'yRange':(0.1,1.9)}
#            ratio = {'yRange':(0.65,1.35)}

        selDir = args.selection
        if args.addCut: selDir += "-" + args.addCut
        plot_directory_ = os.path.join( plot_directory, "WPtReweighting", str(args.year), args.plot_directory, selDir, args.mode, "log" if log else "lin" )
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = log, sorting = True,#plot.name != "mT_fit",
                       yRange = (0.3, "auto"),
                       ratio = ratio,
                       drawObjects = drawObjects( lumi_scale ),
                       legend = legend,
                       copyIndexPHP = True,
                       )

