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

addSF = True

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                        help="Log level for logging")
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv26_v1",                                             help="plot sub-directory")
argParser.add_argument("--selection",          action="store",      default="WJets2",                                                        help="reco region")
argParser.add_argument("--year",               action="store",      default=2016,   type=int,  choices=[2016,2017,2018],                     help="Which year to plot?")
argParser.add_argument("--mode",               action="store",      default="all",  type=str,  choices=["mu", "e", "all"],                   help="lepton selection")
argParser.add_argument("--small",              action="store_true",                                                                          help="Run only on a small subset of the data?")
argParser.add_argument("--tfUpdate",           action="store_true",                                                                          help="update TF setup parameters?")
argParser.add_argument("--overwrite",          action="store_true",                                                                          help="overwrite cache?")
args = argParser.parse_args()

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

cache_dir = os.path.join(cache_directory, "qcdTFHistos", str(args.year), args.selection, args.mode)
dirDB = MergingDirDB(cache_dir)
if not dirDB: raise

cache_dir = os.path.join(cache_directory, "qcdTFHistosSF", str(args.year), args.selection)
dirDBSF = MergingDirDB(cache_dir)
if not dirDBSF: raise

if args.small:    args.plot_directory += "_small"
if args.tfUpdate: args.plot_directory += "_TF"

binning = [ 20, 0, 200 ]

# Sample definition
os.environ["gammaSkim"]="False" #always false for QCD estimate
if args.year == 2016:
    from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed  import *
    from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import *
    mc          = [ TTG_16, TT_pow_16, DY_LO_16, WJets_16, WG_16, ZG_16, rest_16 ]
    ttg         = TTG_16
    tt          = TT_pow_16
    wjets       = WJets_16
    ttg         = TTG_16
    wg          = WG_16
    other       = rest_16
    data_sample = Run2016
elif args.year == 2017:
    from TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed    import *
    from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import *
    mc          = [ TTG_17, TT_pow_17, DY_LO_17, WJets_17, WG_17, ZG_17, rest_17 ]
    ttg         = TTG_17
    tt          = TT_pow_17
    wjets       = WJets_17
    ttg         = TTG_17
    wg          = WG_17
    other       = rest_17
    data_sample = Run2017
elif args.year == 2018:
    from TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed  import *
    from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import *
    mc          = [ TTG_18, TT_pow_18, DY_LO_18, WJets_18, WG_18, ZG_18, rest_18 ]
    ttg         = TTG_18
    tt          = TT_pow_18
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
                     "reweightInvTrigger/F", "reweightInvTriggerUp/F", "reweightInvTriggerDown/F",
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
weightString    = "%f*weight*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF"%lumi_scale
weightStringIL  = "%f*weight*reweightInvTrigger*reweightL1Prefire*reweightPU*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF"%lumi_scale
weightStringInv  = "((%s)+(%s*%f*((nPhotonGoodInvLepIso>0)*(PhotonGoodInvLepIso0_photonCatMagic==2))))"%(weightStringIL,weightStringIL,(misIDSF_val[args.year].val-1))
weightStringAR = "((%s)+(%s*%f*((nPhotonGood>0)*(PhotonGood0_photonCatMagic==2))))"%(weightString,weightString,(misIDSF_val[args.year].val-1))

filterCutData = getFilterCut( args.year, isData=True,  skipBadChargedCandidate=True )
filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )
tr            = TriggerSelector( args.year, singleLepton=True )
triggerCutMc  = tr.getSelection( "MC" )

data_sample.setSelectionString( filterCutData )
data_sample.setWeightString( "weight" )
if args.small:           
    data_sample.normalization = 1.
    data_sample.reduceFiles( factor=5 )
    data_sample.setWeightString( "weight*%f"%(1./data_sample.normalization) )

for s in mc:
    s.setSelectionString( [ filterCutMc, triggerCutMc ] )#, "overlapRemoval==1" ] )
    s.read_variables = read_variables_MC
    sampleWeight     = "1"
    if args.small:           
        s.normalization = 1.
        s.reduceFiles( factor=100 )
        sampleWeight = "%f"%(1./s.normalization)

photonRegion = False
bjetRegion   = False
# get selection cuts
regionPlot = False
if len(args.selection.split("-")) == 1 and args.selection in allRegions.keys():
    print( "Plotting region from SetupHelpers: %s"%args.selection )

    regionPlot = True
    setup = Setup( year=args.year, photonSelection=False, checkOnly=False, runOnLxPlus=False ) #photonselection always false for qcd estimate
    setup = setup.sysClone( parameters=allRegions[args.selection]["parameters"] )

    photonRegion = QCDTF_updates["SR"]["nPhoton"][0] > 0 if args.tfUpdate and "nPhoton" in QCDTF_updates["SR"].keys() else not allRegions[args.selection]["noPhotonCR"]
    bjetRegion   = QCDTF_updates["SR"]["nBTag"][0] > 0   if args.tfUpdate and "nBTag"   in QCDTF_updates["SR"].keys() else setup.parameters["nBTag"][0] > 0
    njets        = QCDTF_updates["SR"]["nJet"][0]        if args.tfUpdate and "nJet"    in QCDTF_updates["SR"].keys() else setup.parameters["nJet"][0]

    allSelection  = setup.selection( "MC", channel="all", **setup.defaultParameters(QCDTF_updates["SR"] if args.tfUpdate else {}) )["prefix"]
    selection     = allSelection + "-" + args.mode
    selection     = cutInterpreter.cutString( selection )
    print( "Using selection string: %s"%args.selection )

    preSelection  = setup.selection("MC",   channel="all", **setup.defaultParameters( update=QCDTF_updates["CR"] if args.tfUpdate else QCD_updates ))["prefix"]
    preSelection += "-" + args.mode + "Inv"
    preSelection  = cutInterpreter.cutString( preSelection )
else:
    raise Exception("Region not implemented")

key = (data_sample.name, "mTinv", "_".join(map(str,binning)), data_sample.weightString, data_sample.selectionString, preSelection)
if dirDB.contains(key) and not args.overwrite:
    dataHist_SB = dirDB.get(key)
else:
    dataHist_SB = data_sample.get1DHistoFromDraw( "mTinv", binning=binning, selectionString=preSelection, addOverFlowBin="upper" )
    dirDB.add(key, dataHist_SB)

key = (data_sample.name, "mT", "_".join(map(str,binning)), data_sample.weightString, data_sample.selectionString, selection)
if dirDB.contains(key) and not args.overwrite:
    dataHist = dirDB.get(key)
else:
    dataHist = data_sample.get1DHistoFromDraw( "mT",    binning=binning, selectionString=selection,    addOverFlowBin="upper" )
    dirDB.add(key, dataHist)

qcdHist     = dataHist_SB.Clone("QCD")

dataHist_SB.style      = styles.errorStyle( ROOT.kBlack )
dataHist_SB.legendText = "data (%s)"%args.mode.replace("mu","#mu")
dataHist.style         = styles.errorStyle( ROOT.kBlack )
dataHist.legendText    = "data (%s)"%args.mode.replace("mu","#mu")
qcdHist.style          = styles.fillStyle( color.QCD )
qcdHist.legendText     = "QCD"

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
        s.hist_SB = dirDB.get(key)
    else:
        s.hist_SB = s.get1DHistoFromDraw( "mTinv", binning=binning, selectionString=preSelection, addOverFlowBin="upper" )
        dirDB.add(key, s.hist_SB)

    s.setWeightString( weightStringAR + "*" + sampleWeight )
    key = (s.name, "mT", "_".join(map(str,binning)), s.weightString, s.selectionString, selection)
    if dirDB.contains(key) and not args.overwrite:
        s.hist = dirDB.get(key)
    else:
        s.hist = s.get1DHistoFromDraw( "mT", binning=binning, selectionString=selection, addOverFlowBin="upper" )
        dirDB.add(key, s.hist)

    print s.name, s.weightString
    print s.name, s.selectionString
    print s.name, s.hist.Integral()/lumi_scale
    print s.name, s.hist_SB.Integral()/lumi_scale

    # apply SF after histo caching
    if addSF:
        if "DY" in s.name:
            s.hist.Scale(DYSF_val[args.year].val)
            s.hist_SB.Scale(DYSF_val[args.year].val)
        elif "WJets" in s.name:
            s.hist.Scale(WJetsSF_val[args.year].val)
            s.hist_SB.Scale(WJetsSF_val[args.year].val)
        elif "TT_pow" in s.name:
            s.hist.Scale(TTSF_val[args.year].val)
            s.hist_SB.Scale(TTSF_val[args.year].val)
        elif "ZG" in s.name:# and njets < 4:
            s.hist.Scale(ZGSF_val[args.year].val)
            s.hist_SB.Scale(ZGSF_val[args.year].val)
        elif "other" in s.name:# and njets < 4:
            s.hist.Scale(otherSF_val[args.year].val)
            s.hist_SB.Scale(otherSF_val[args.year].val)
        elif "WG" in s.name:# and njets > 3:
            s.hist.Scale(WGSF_val[args.year].val)
            s.hist_SB.Scale(WGSF_val[args.year].val)
#        elif "WG" in s.name:
#            s.hist.Scale(WGSF_val[args.year].val*0.8)
#            s.hist_SB.Scale(WGSF_val[args.year].val*0.8)
        elif "TTG" in s.name:
            s.hist.Scale(SSMSF_val[args.year].val)
            s.hist_SB.Scale(SSMSF_val[args.year].val)

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
qcdTemplate.legendText = "QCD template"
qcdTemplate.Scale(1./ qcdTemplate.Integral() )
maxQCD = qcdTemplate.GetMaximum()

# for template ratio pattern
mTHistos_SB.append( [qcdTemplate] )
mTHistos_SB.append( [oneHist] )

if       photonRegion and not bjetRegion:                floatSample = wg
elif     photonRegion and     bjetRegion and njets == 2: floatSample = other
elif     photonRegion and     bjetRegion:                floatSample = ttg
elif not photonRegion and not bjetRegion:                floatSample = wjets
elif not photonRegion and     bjetRegion and njets == 2: floatSample = wjets
elif not photonRegion and     bjetRegion:                floatSample = tt

print("Using sample %s as free floating histogram!"%floatSample.name)

hist_float = floatSample.hist.Clone("ffit")
hist_qcd   = qcdHist.Clone("hist_qcd")

key = (floatSample.name, "mu", "mT", "_".join(map(str,binning)), floatSample.weightString, floatSample.selectionString, allSelection)
#if args.mode == "e" and dirDBSF.contains(key):
if photonRegion and args.mode == "e":
    if dirDBSF.contains(key):
    # fix electron channel floating sf to muon sf
        muonSF = dirDBSF.get(key)
        hist_float.Scale( muonSF )
        print("Scaling floating electron channel histogram by muon channel SF of %f"%muonSF)

hist_other            = floatSample.hist.Clone("other")
hist_other.style      = styles.fillStyle( ROOT.kGray )
hist_other.legendText = "other"
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
#fitter.SetRangeX(6,19)

tfitter = fitter.GetFitter()
tfitter.Config().ParSettings(0).Set("qcd",   nQCD*0.2/nTotal if bjetRegion else nQCD*1./nTotal, 0.01, 0.,               1.)
if photonRegion and not bjetRegion: #and args.mode == "e": # fix WGamma in photonRegions e-channel since mT is not a good handle
#if args.mode == "e": # fix WGamma in photonRegions e-channel since mT is not a good handle
#if photonRegion and args.mode == "e": # fix WGamma in photonRegions e-channel since mT is not a good handle
#    tfitter.Config().ParSettings(1).Set("float", nFloat/nTotal,   0.001, 0.,               1.)
    tfitter.Config().ParSettings(1).Set("float", nFloat/nTotal,   0.01, nFloat*0.999/nTotal, nFloat*1.001/nTotal)
#elif "EC" in args.selection: # fix WGamma in photonRegions e-channel since mT is not a good handle
##    tfitter.Config().ParSettings(1).Set("float", nFloat/nTotal,   0.001, 0.,               1.)
#    tfitter.Config().ParSettings(1).Set("float", nFloat/nTotal,   0.01, nFloat*0.999/nTotal, nFloat*1.001/nTotal)
else:
    tfitter.Config().ParSettings(1).Set("float", nFloat/nTotal,   0.01, 0.,               1.)
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

key = (floatSample.name, args.mode, "mT", "_".join(map(str,binning)), floatSample.weightString, floatSample.selectionString, allSelection)
print key
dirDBSF.add(key,floatSF.val, overwrite=True )
print("Storing floating SF of %f"%floatSF.val)

qcdHist.Scale(qcdTF.val)
hist_qcd.Scale(qcdTF.val)
hist_float.Scale(floatSF.val)

hist_qcd.legendText = "QCD" + " (TF %1.3f#pm %1.3f)"%(qcdTF.val, qcdTF.sigma)
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
plots.append( Plot.fromHisto( "mT",          mTHistos,        texX = "m_{T} [GeV]",                texY = "Number of Events" ) )
plots.append( Plot.fromHisto( "mT_fit",      mTHistos_fit,    texX = "m_{T} [GeV]",                texY = "Number of Events" ) )
plots.append( Plot.fromHisto( "mT_sideband", mTHistos_SB,     texX = "m_{T} (QCD sideband) [GeV]", texY = "Number of Events" ) )
#plots.append( Plot.fromHisto( "mT_template", [[qcdTemplate]], texX = "m_{T} [GeV]",                texY = "Number of Events" ) )

for plot in plots:

    if plot.name == "mT_fit":
        legend = [ (0.2, 0.70, 0.9, 0.9), 2 ]
    elif "template" in plot.name:
        legend = [ (0.2, 0.84, 0.9, 0.9), 1 ]
    else:
        legend = [ (0.2,0.9-0.025*sum(map(len, plot.histos)),0.9,0.9), 3 ]

    for log in [True, False]:

        if plot.name == "mT" or plot.name == "mT_fit":
            ratio = {'yRange':(0.65,1.35)}
        elif plot.name == "mT_sideband":
            ratio = {'histos':[(2,3)], 'logY':log, 'texY': 'Template', 'yRange': (0.03, maxQCD*2) if log else (0.001, maxQCD*1.2)}
        else:
            ratio = None

        plot_directory_ = os.path.join( plot_directory, "transferFactor", str(args.year), args.plot_directory, "qcdHistos",  args.selection, args.mode, "log" if log else "lin" )
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
