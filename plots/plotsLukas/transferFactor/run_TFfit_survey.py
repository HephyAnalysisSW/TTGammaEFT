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
import Analysis.Tools.syncer as syncer

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

addSF = True

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                        help="Log level for logging")
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv29_v1",                                             help="plot sub-directory")
argParser.add_argument("--selection",          action="store",      default="WJets2",                                                        help="reco region")
argParser.add_argument("--year",               action="store",      default="2016",   type=str,  choices=["2016","2017","2018","RunII"],                     help="Which year to plot?")
argParser.add_argument("--mode",               action="store",      default="e",    type=str,  choices=["mu", "e"],                          help="lepton selection")
argParser.add_argument("--addCut",             action="store",      default=None, type=str,                                                  help="additional cuts")
argParser.add_argument("--overwrite",          action="store_true",                                                                          help="overwrite cache?")
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
    line = (0.65, 0.95, "%3.1f fb{}^{-1} (13 TeV)" % lumi_scale)
    lines = [
      (0.15, 0.95, "CMS #bf{#it{Preliminary}} (%s)"%args.selection),
      line
    ]
    return [tex.DrawLatex(*l) for l in lines]

selDir = args.selection
if args.addCut: selDir += "-" + args.addCut

mTinv = "mTinv"
replaceSelection = {
#    "nLeptonVetoIsoCorr": "nLeptonVetoNoIso",
    "nLeptonTight":       "nLeptonTightInvIso",
    "nMuonTight":         "nMuonTightInvIso",
    "nElectronTight":     "nElectronTightInvIso",
    "mLtight0Gamma":      "mLinvtight0Gamma",
    "nPhotonGood":        "nPhotonGoodInvLepIso",
    "nJetGood":           "nJetGoodInvLepIso",
    "nBTagGood":          "nBTagGoodInvLepIso",
    "mT":                 "mTinv",
    "m3":                 "m3inv",
#    "ht":                 "htinv",
    "LeptonTight0":       "LeptonTightInvIso0",
}

cache_dir = os.path.join(cache_directory, "qcdTFHistos", str(args.year), args.selection, args.mode)
dirDB = MergingDirDB(cache_dir)
if not dirDB: raise

binning = [ 20, 0, 200 ]

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
elif args.year == "RunII":
    import TTGammaEFT.Samples.nanoTuples_RunII_postProcessed as mc_samples
    from TTGammaEFT.Samples.nanoTuples_RunII_postProcessed import RunII as data_sample

mc = [ mc_samples.TTG, mc_samples.Top, mc_samples.DY_LO, mc_samples.WJets, mc_samples.WG_NLO, mc_samples.ZG, mc_samples.rest ]

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
lumiString = "(35.92*(year==2016)+41.53*(year==2017)+59.74*(year==2018))"
ws   = "(%s*weight*reweightHEM*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF)"%lumiString
ws16 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2016))" %(ws, misIDSF_val[2016].val)
ws17 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2017))" %(ws, misIDSF_val[2017].val)
ws18 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2018))" %(ws, misIDSF_val[2018].val)
#weightStringAR = ws + ws16 + ws17 + ws18
weightStringAR  = ws

wsInv   = "(%s*weight*reweightHEM*reweightInvIsoTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSFInvIso*reweightLeptonTrackingTightSFInvIso*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF)"%lumiString
wsInv16 = "+(%s*(PhotonNoChgIsoNoSieieInvLepIso0_photonCatMagic==2)*(%f-1)*(year==2016))" %(wsInv, misIDSF_val[2016].val)
wsInv17 = "+(%s*(PhotonNoChgIsoNoSieieInvLepIso0_photonCatMagic==2)*(%f-1)*(year==2017))" %(wsInv, misIDSF_val[2017].val)
wsInv18 = "+(%s*(PhotonNoChgIsoNoSieieInvLepIso0_photonCatMagic==2)*(%f-1)*(year==2018))" %(wsInv, misIDSF_val[2018].val)
#weightStringInv = wsInv + wsInv16 + wsInv17 + wsInv18
weightStringInv = wsInv

filterCutData = getFilterCut( args.year, isData=True,  skipBadChargedCandidate=True )
filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )

data_sample.setSelectionString( [filterCutData, "reweightHEM>0"] )
data_sample.setWeightString( "weight" )

for s in mc:
    s.setSelectionString( [ filterCutMc, "pTStitching==1", "overlapRemoval==1" ] )
    s.read_variables = read_variables_MC
    sampleWeight     = "1"

photonRegion = False
bjetRegion   = False
# get selection cuts
regionPlot = False
if len(args.selection.split("-")) == 1 and args.selection in allRegions.keys():
    print( "Plotting region from SetupHelpers: %s"%args.selection )

    regionPlot = True
    setup = Setup( year=args.year, photonSelection=False, checkOnly=False, runOnLxPlus=False ) #photonselection always false for qcd estimate
    setup = setup.sysClone( parameters=allRegions[args.selection]["parameters"] )

    photonRegion = not allRegions[args.selection]["noPhotonCR"]
    bjetRegion   = setup.parameters["nBTag"][0] > 0
    njets        = setup.parameters["nJet"][0]

    selection  = setup.selection( "DataMC", channel=args.mode )["prefix"]
#    selection     = allSelection + "-" + args.mode
    selection     = cutInterpreter.cutString( selection )
    selection += "&&triggered==1"
    print selection
    if args.addCut:
        print cutInterpreter.cutString( args.addCut )
        selection += "&&" + cutInterpreter.cutString( args.addCut )
    print( "Using selection string: %s"%args.selection )
    print selection

    preSelection  = setup.selection("DataMC",   channel=args.mode, **setup.defaultParameters( update=QCD_updates ))["prefix"]
    print preSelection
    preSelection  = cutInterpreter.cutString( preSelection )
    preSelection += "&&triggeredInvIso==1"
    print preSelection
    print args.addCut

    if args.year == 2016 and args.mode == "e" and not "etal0" in args.addCut:
        preSelection += "&&abs(LeptonTightInvIso0_eta)<1.479"

    if args.addCut:
#        addSel = args.addCut #"-".join([ item for item in args.addCut.split("-") if not item.startswith("etal")])
        if args.year == 2016 and args.mode == "e":
            addSel = "-".join([ item for item in args.addCut.split("-") if not item.startswith("etal") or "etal0" in item ])
        else:
            addSel = args.addCut
        if addSel:
            addSel = cutInterpreter.cutString( addSel )
            print addSel
            for iso, invIso in replaceSelection.iteritems():
                addSel = addSel.replace(iso,invIso)
            print preSelection
            print addSel
            preSelection += "&&" + addSel
else:
    raise Exception("Region not implemented")

key = (data_sample.name, "mTinv", "_".join(map(str,binning)), data_sample.weightString, data_sample.selectionString, preSelection)
if dirDB.contains(key) and not args.overwrite:
    dataHist_SB = dirDB.get(key).Clone("mTinv")
else:
    dataHist_SB = data_sample.get1DHistoFromDraw( mTinv, binning=binning, selectionString=preSelection, addOverFlowBin="upper" )
    dirDB.add(key, dataHist_SB.Clone("mTinv"), overwrite=True)

key = (data_sample.name, "mT", "_".join(map(str,binning)), data_sample.weightString, data_sample.selectionString, selection)
if dirDB.contains(key) and not args.overwrite:
    dataHist = dirDB.get(key).Clone("mT")
else:
    dataHist = data_sample.get1DHistoFromDraw( "mT",    binning=binning, selectionString=selection,    addOverFlowBin="upper" )
    dirDB.add(key, dataHist.Clone("mT"), overwrite=True)

qcdHist     = dataHist_SB.Clone("QCD")

dataHist_SB.style      = styles.errorStyle( ROOT.kBlack )
dataHist_SB.legendText = "Observed (%s)"%args.mode.replace("mu","#mu")
dataHist.style         = styles.errorStyle( ROOT.kBlack )
dataHist.legendText    = "Observed (%s)"%args.mode.replace("mu","#mu")
qcdHist.style          = styles.fillStyle( color.QCD )
qcdHist.legendText     = "Multijet"

oneHist = dataHist.Clone("one")
oneHist.notInLegend = True
oneHist.style = styles.lineStyle( ROOT.kWhite, width=0 )
for i in range(oneHist.GetNbinsX()):
    oneHist.SetBinContent(i+1, 1)

mTHistos     = [[], [dataHist]]
mTHistos_fit = [[], [dataHist]]
mTHistos_SB  = [[], [dataHist_SB]]

for s in mc:
    s.setWeightString( weightStringInv + "*" + sampleWeight )
    key = (s.name, "mTinv", "_".join(map(str,binning)), s.weightString, s.selectionString, preSelection)
    if dirDB.contains(key) and not args.overwrite:
        s.hist_SB = dirDB.get(key).Clone(s.name+"mTinv")
    else:
        s.hist_SB = s.get1DHistoFromDraw( mTinv, binning=binning, selectionString=preSelection, addOverFlowBin="upper" )
        dirDB.add(key, s.hist_SB.Clone(s.name+"mTinv"), overwrite=True)

    s.setWeightString( weightStringAR + "*" + sampleWeight )
    key = (s.name, "mT", "_".join(map(str,binning)), s.weightString, s.selectionString, selection)
    if dirDB.contains(key) and not args.overwrite:
        s.hist = dirDB.get(key).Clone(s.name+"mT")
    else:
        s.hist = s.get1DHistoFromDraw( "mT", binning=binning, selectionString=selection, addOverFlowBin="upper" )
        dirDB.add(key, s.hist.Clone(s.name+"mT"), overwrite=True)

    print s.name, s.weightString
    print s.name, s.selectionString
    print s.name, s.hist.Integral()/lumi_scale
    print s.name, s.hist_SB.Integral()/lumi_scale

    # apply SF after histo caching
    if addSF:
        if "WJets" in s.name:
            s.hist.Scale(WJetsSF_val[args.year].val)
            s.hist_SB.Scale(WJetsSF_val[args.year].val)

    qcdHist.Add( s.hist_SB, -1 )

    s.hist_SB.style      = styles.fillStyle( s.color )
    s.hist_SB.legendText = s.texName
    s.hist.style         = styles.fillStyle( s.color )
    s.hist.legendText    = s.texName



    mTHistos[0].append( s.hist )
    mTHistos_SB[0].append( s.hist_SB )

# remove negative bins
for i in range(qcdHist.GetNbinsX()):
    if qcdHist.GetBinContent(i+1) < 0: qcdHist.SetBinContent(i+1, 0)

# copy template
qcdTemplate            = qcdHist.Clone("QCDTemplate")
qcdTemplate.style      = styles.fillStyle( color.QCD )
qcdTemplate.legendText = "Template"
qcdTemplate.Scale(1./ qcdTemplate.Integral() )
maxQCD = qcdTemplate.GetMaximum()

# for template ratio pattern
mTHistos_SB.append( [qcdTemplate] )
mTHistos_SB.append( [oneHist] )

if       photonRegion and not bjetRegion:                floatSample = mc_samples.WG
elif     photonRegion and     bjetRegion and njets == 2: floatSample = mc_samples.rest
elif     photonRegion and     bjetRegion:                floatSample = mc_samples.TTG
elif not photonRegion and not bjetRegion:                floatSample = mc_samples.WJets
elif not photonRegion and     bjetRegion and njets == 2: floatSample = mc_samples.WJets
elif not photonRegion and     bjetRegion:                floatSample = mc_samples.Top

print("Using sample %s as free floating histogram!"%floatSample.name)

hist_float = floatSample.hist.Clone("ffit")
hist_qcd   = qcdHist.Clone("hist_qcd")

hist_other            = floatSample.hist.Clone("other")
hist_other.style      = styles.fillStyle( ROOT.kGray )
hist_other.legendText = "Other"
hist_other.Scale(0.)

for s in mc:
    if s.name == floatSample.name: continue
    hist_other.Add(s.hist)

nTotal = dataHist.Integral()
nFloat = hist_float.Integral()
nFix   = hist_other.Integral()
nQCD   = hist_qcd.Integral()

tarray = ROOT.TObjArray(3)
tarray.Add( hist_qcd )
tarray.Add( hist_float )
tarray.Add( hist_other )

fitter = ROOT.TFractionFitter( dataHist, tarray )
fitter.SetRangeX(1,12)

tfitter = fitter.GetFitter()
tfitter.Config().ParSettings(0).Set("qcd",   nQCD*0.2/nTotal if bjetRegion else nQCD*1./nTotal, 0.01, 0.,               1.)
#if photonRegion and not bjetRegion: #and args.mode == "e": # fix WGamma in photonRegions e-channel since mT is not a good handle
#if args.mode == "e": # fix WGamma in photonRegions e-channel since mT is not a good handle
#if photonRegion and args.mode == "e": # fix WGamma in photonRegions e-channel since mT is not a good handle
#tfitter.Config().ParSettings(1).Set("float", nFloat/nTotal,   0.001, 0.,               1.)
#tfitter.Config().ParSettings(1).Set("float", nFloat/nTotal,   0.01, nFloat*0.999/nTotal, nFloat*1.001/nTotal)
#tfitter.Config().ParSettings(1).Set("float", nFloat/nTotal,   0.01, nFloat*0.5/nTotal, nFloat*1.5/nTotal)
tfitter.Config().ParSettings(1).Set("float", nFloat/nTotal,   0.01, nFloat*0.8/nTotal, nFloat*1.2/nTotal)
#elif "EC" in args.selection: # fix WGamma in photonRegions e-channel since mT is not a good handle
#tfitter.Config().ParSettings(1).Set("float", nFloat/nTotal,   0.01, 0.,               1.)
#    tfitter.Config().ParSettings(1).Set("float", nFloat/nTotal,   0.01, nFloat*0.999/nTotal, nFloat*1.001/nTotal)
#else:
#    tfitter.Config().ParSettings(1).Set("float", nFloat/nTotal,   0.01, 0.,               1.)
tfitter.Config().ParSettings(2).Set("fixed", nFix/nTotal,     0.0,   nFix*0.999/nTotal, nFix*1.001/nTotal)
tfitter.Config().ParSettings(2).Fix()

print("Performing Fit!")
status = fitter.Fit()           # perform the fit
print("Fit performed: status = %i"%status)

qcdTFVal,   qcdTFErr   = ROOT.Double(0), ROOT.Double(0)
floatSFVal, floatSFErr = ROOT.Double(0), ROOT.Double(0)

fitter.GetResult( 0, qcdTFVal,   qcdTFErr )
fitter.GetResult( 1, floatSFVal, floatSFErr )

qcdTF   = u_float( qcdTFVal,   qcdTFErr )*nTotal/nQCD
floatSF = u_float( floatSFVal, floatSFErr )*nTotal/nFloat

print
print "qcdTF", qcdTF
print "floating SF", floatSF
print

qcdHist.Scale(qcdTF.val)
hist_qcd.Scale(qcdTF.val)
hist_float.Scale(floatSF.val)

hist_qcd.legendText = "Multijet" + " (TF %1.3f#pm %1.3f)"%(qcdTF.val, qcdTF.sigma)
hist_qcd.style      = styles.fillStyle( color.QCD )

#if args.mode == "e": # fix WGamma in photonRegions e-channel since mT is not a good handle
if photonRegion and args.mode == "e": # fix WGamma in photonRegions e-channel since mT is not a good handle
#    hist_float.legendText = floatSample.texName
    hist_float.legendText = floatSample.texName + " (SF %1.3f#pm %1.3f)"%(floatSF.val, floatSF.sigma)
else:
    hist_float.legendText = floatSample.texName + " (SF %1.3f#pm %1.3f)"%(floatSF.val, floatSF.sigma)
hist_float.style      = styles.fillStyle( floatSample.color )

mTHistos[0].append( qcdHist )
mTHistos_fit[0].append( hist_float )
mTHistos_fit[0].append( hist_qcd )
mTHistos_fit[0].append( hist_other )

Plot.setDefaults()

plots = []
#plots.append( Plot.fromHisto( "mT",          mTHistos,        texX = "m_{T} [GeV]",                texY = "Number of Events" ) )
plots.append( Plot.fromHisto( "mT_" + args.addCut + "_fit",      mTHistos_fit,    texX = "m_{T} [GeV]",                texY = "Number of Events" ) )
plots.append( Plot.fromHisto( "mT_" + args.addCut + "_sideband", mTHistos_SB,     texX = "m_{T} (QCD sideband) [GeV]", texY = "Number of Events" ) )
#plots.append( Plot.fromHisto( "mT_template", [[qcdTemplate]], texX = "m_{T} [GeV]",                texY = "Number of Events" ) )

for plot in plots:

    if "fit" in plot.name:
        legend = [ (0.2, 0.70, 0.9, 0.9), 2 ]
    else:
        legend = [ (0.2,0.9-0.025*sum(map(len, plot.histos)),0.9,0.9), 3 ]

    for log in [True, False]:

        if "fit" in plot.name:
            ratio = {'yRange':(0.1,1.9)}
        elif "sideband" in plot.name:
            ratio = {'histos':[(2,3)], 'logY':log, 'texY': 'Template', 'yRange': (0.03, maxQCD*2) if log else (0.001, maxQCD*1.2)}
        else:
            ratio = None

        plot_directory_ = os.path.join( plot_directory, "transferFactor", str(args.year), args.plot_directory, "qcdHistos_survey",  args.selection, args.mode, "log" if log else "lin" )
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = log, sorting = True,#plot.name != "mT_fit",
                       yRange = (0.3, "auto") if not "template" in plot.name else "auto",
                       ratio = ratio,
                       drawObjects = drawObjects( lumi_scale ),
                       legend = legend,
                       copyIndexPHP = True,
                       )

del fitter
