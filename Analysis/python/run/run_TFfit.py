# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy

# RootTools
from RootTools.core.standard           import *

# Analysis
from Analysis.Tools.metFilters         import getFilterCut

# Internal Imports
from TTGammaEFT.Tools.user             import plot_directory
from TTGammaEFT.Tools.cutInterpreter   import cutInterpreter
from TTGammaEFT.Tools.TriggerSelector  import TriggerSelector

from TTGammaEFT.Analysis.SetupHelpers  import *
from TTGammaEFT.Analysis.Setup         import Setup
from TTGammaEFT.Analysis.EstimatorList import EstimatorList

from TTGammaEFT.Samples.color          import color

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
argParser.add_argument("--tfUpdate",           action="store_true",                                                                          help="overwrite cache?")
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

if args.small:    args.plot_directory += "_small"
if args.tfUpdate: args.plot_directory += "_TF"

binning = [ 20, 0, 200 ]

# Sample definition
os.environ["gammaSkim"]="False" #always false for QCD estimate
if args.year == 2016:
    from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed  import *
    from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import *
    mc          = [ TTG_16, TT_pow_16, DY_LO_16, WJets_16, WG_16, ZG_16, rest_16 ]
    wjets       = WJets_16
    wg          = WG_16
    data_sample = Run2016
elif args.year == 2017:
    from TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed    import *
    from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import *
    mc          = [ TTG_17, TT_pow_17, DY_LO_17, WJets_17, WG_17, ZG_17, rest_17 ]
    wjets       = WJets_17
    wg          = WG_17
    data_sample = Run2017
elif args.year == 2018:
    from TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed  import *
    from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import *
    mc          = [ TTG_18, TT_pow_18, DY_LO_18, WJets_18, WG_18, ZG_18, rest_18 ]
    wjets       = WJets_18
    wg          = WG_18
    data_sample = Run2018

read_variables_MC = ["isTTGamma/I", "isZWGamma/I", "isTGamma/I", "overlapRemoval/I",
                     "reweightPU/F", "reweightPUDown/F", "reweightPUUp/F", "reweightPUVDown/F", "reweightPUVUp/F",
                     "reweightLeptonTightSF/F", "reweightLeptonTightSFUp/F", "reweightLeptonTightSFDown/F",
                     "reweightLeptonTrackingTightSF/F",
                     "reweightDilepTrigger/F", "reweightDilepTriggerUp/F", "reweightDilepTriggerDown/F",
                     "reweightDilepTriggerBackup/F", "reweightDilepTriggerBackupUp/F", "reweightDilepTriggerBackupDown/F",
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
weightString = "%f*weight*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF"%lumi_scale
weightString = "(%s)+(%s*%f*((nPhotonGood>0)*(PhotonGood0_photonCat==2)))"%(weightString,weightString,(misIDSF_val[args.year].val-1))

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
    s.setSelectionString( [ filterCutMc, triggerCutMc, "overlapRemoval==1" ] )
    s.read_variables = read_variables_MC
    sampleWeight     = weightString

    if addSF:
        if "DY" in s.name:
            sampleWeight += "*%f"%DYSF_val[args.year].val
        elif "WJets" in s.name:
            sampleWeight += "*%f"%WJetsSF_val[args.year].val
        elif "TT_pow" in s.name:
            sampleWeight += "*%f"%TTSF_val[args.year].val
        elif "ZG" in s.name:
            sampleWeight += "*%f"%ZGSF_val[args.year].val
        elif "WG" in s.name:
            sampleWeight += "*%f"%WGSF_val[args.year].val
        elif "TTG" in s.name:
            sampleWeight += "*%f"%SSMSF_val[args.year].val

    if args.small:           
        s.normalization = 1.
        s.reduceFiles( factor=100 )
        sampleWeight += "*%f"%(1./s.normalization)

    s.setWeightString( sampleWeight )

replaceSelection = {
    "nLeptonVetoIsoCorr": "nLeptonVetoNoIsoTight",
    "nLeptonTight":       "nLeptonTightInvIso",
    "nMuonTight":         "nMuonTightInvIso",
    "nElectronTight":     "nElectronTightInvIso",
    "mLtight0Gamma":      "mLinvtight0Gamma",
}

photonRegion = False
# get selection cuts
regionPlot = False
if len(args.selection.split("-")) == 1 and args.selection in allRegions.keys():
    print( "Plotting region from SetupHelpers: %s"%args.selection )

    regionPlot = True
    setup = Setup( year=args.year, photonSelection=False, checkOnly=False, runOnLxPlus=False ) #photonselection always false for qcd estimate
    setup = setup.sysClone( parameters=allRegions[args.selection]["parameters"] )
    photonRegion = not allRegions[args.selection]["noPhotonCR"]

    selection     = setup.selection( "MC", channel="all", **setup.defaultParameters(QCDTF_updates["SR"] if args.tfUpdate else {}) )["prefix"]
    selection    += "-" + args.mode
    selection     = cutInterpreter.cutString( selection )
    print( "Using selection string: %s"%args.selection )

    preSelection  = setup.selection("MC",   channel="all", **setup.defaultParameters( update=QCDTF_updates["CR"] if args.tfUpdate else QCD_updates ))["prefix"]
    preSelection += "-" + args.mode + "Inv"
    preSelection  = cutInterpreter.cutString( preSelection )

else:
    raise Exception("Region not implemented")
#else:
#    selection     = args.selection
#    selection    += "-" + args.mode
#    selection     = cutInterpreter.cutString( selection )

#    preSelection  = [ item if not "nBTag" in item else "nBTag0" for item in args.selection.split("-") ]
#    preSelection += [ args.mode + "Inv" ]
#    preSelection  = cutInterpreter.cutString( "-".join(preSelection) )

#    for key, val in replaceSelection.items():
#        preSelection = preSelection.replace( key, val )


dataHist_SB = data_sample.get1DHistoFromDraw( "mTinv", binning=binning, selectionString=preSelection, addOverFlowBin="upper" )
dataHist    = data_sample.get1DHistoFromDraw( "mT",    binning=binning, selectionString=selection,    addOverFlowBin="upper" )
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
    s.hist_SB = s.get1DHistoFromDraw( "mTinv", binning=binning, selectionString=preSelection, addOverFlowBin="upper" )
    s.hist    = s.get1DHistoFromDraw( "mT",    binning=binning, selectionString=selection,    addOverFlowBin="upper" )
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
qcdTemplate.Scale(1./qcdTemplate.Integral())
maxQCD = qcdTemplate.GetMaximum()

# for template ratio pattern
mTHistos_SB.append( [qcdTemplate] )
mTHistos_SB.append( [oneHist] )

if photonRegion: floatSample = wg
else:            floatSample = wjets

print("Using sample %s as free floating histogram!"%floatSample.name)

hist_float = floatSample.hist.Clone("ffit")
hist_qcd   = qcdHist.Clone("hist_qcd")

hist_other            = floatSample.hist.Clone("other")
hist_other.style      = styles.fillStyle( ROOT.kGray )
hist_other.legendText = "other"
hist_other.Scale(0.)

for s in mc:
    if s.name == floatSample.name: continue
    hist_other.Add(s.hist)

print "data",  dataHist.Integral()
print "qcd",   hist_qcd.Integral()
print "float", hist_float.Integral()
print "fixed", hist_other.Integral()

dataHist.Add(hist_other, -1)

tarray = ROOT.TObjArray(3)
tarray.AddLast( hist_qcd   )
tarray.AddLast( hist_float )
#tarray.AddLast( hist_other )

fitter = ROOT.TFractionFitter(dataHist, tarray)
fitter.Constrain( 0, 0.000, 1.000 ) # qcd tf
fitter.Constrain( 1, 0.700, 1.300 ) # floating
#fitter.Constrain( 2, 0.99, 1.01 ) # fixed

fitter.SetRangeX(0,10)
fitter.SetRangeX(1,10)
#fitter.SetRangeX(2,10)

print("Performing Fit!")
status = fitter.Fit()           # perform the fit
print("Fit performed: status = %i"%status)

qcdTFVal,   qcdTFErr   = ROOT.Double(0), ROOT.Double(0)
floatSFVal, floatSFErr = ROOT.Double(0), ROOT.Double(0)
#otherSFVal, otherSFErr = ROOT.Double(0), ROOT.Double(0)

fitter.GetResult( 0, qcdTFVal,   qcdTFErr )
fitter.GetResult( 1, floatSFVal, floatSFErr )
#fitter.GetResult( 2, otherSFVal, otherSFErr )

qcdTF   = u_float( qcdTFVal,   qcdTFErr )
floatSF = u_float( floatSFVal, floatSFErr )
#otherSF = u_float( otherSFVal, otherSFErr )

dataHist.Add(hist_other)

print "qcdTF", qcdTF
print "floating SF", floatSF
#print "fixed SF", otherSF

qcdHist.Scale(qcdTF.val)
hist_qcd.Scale(qcdTF.val)
hist_float.Scale(floatSF.val)

hist_qcd.legendText = "QCD" + " (TF %1.2f#pm %1.2f)"%(qcdTF.val, qcdTF.sigma)
hist_qcd.style      = styles.fillStyle( color.QCD )

hist_float.legendText = floatSample.texName + " (SF %1.2f#pm %1.2f)"%(floatSF.val, floatSF.sigma)
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
plots.append( Plot.fromHisto( "mT_template", [[qcdTemplate]], texX = "m_{T} [GeV]",                texY = "Number of Events" ) )

for plot in plots:

    if plot.name == "mT_fit":
        legend = [ (0.2, 0.75, 0.9, 0.9), 2 ]
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
                       logX = False, logY = log, sorting = plot.name != "mT_fit",
                       yRange = (0.3, "auto"),
                       ratio = ratio,
                       drawObjects = drawObjects( lumi_scale ),
                       legend = legend,
                       copyIndexPHP = True,
                       )

del fitter
