# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy

# RootTools
from RootTools.core.standard          import *

# Analysis
from Analysis.Tools.MergingDirDB      import MergingDirDB

# Internal Imports
from TTGammaEFT.Tools.user            import plot_directory, cache_directory
from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter

from TTGammaEFT.Analysis.SetupHelpers import *
from TTGammaEFT.Analysis.Setup        import Setup
from TTGammaEFT.Analysis.EstimatorList   import EstimatorList
from TTGammaEFT.Analysis.regions      import *

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                        help="Log level for logging")
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv1_v1",                                              help="plot sub-directory")
argParser.add_argument("--recoSelection",      action="store",      default="SR4p",                                                          help="reco region")
argParser.add_argument("--genSelection",       action="store",      default="nGenLepCMS1-nGenJetCMS4p-nGenBTagCMS1p-nGenPhotonCMS1",         help="gen selection string")
argParser.add_argument("--genPtVariable",      action="store",      default="GenPhotonCMSUnfold0_pt",                                        help="gen photon pt variable")
argParser.add_argument("--genBinning",         action="store",      default=[10,20,220], type=int, nargs=3,                                  help="binning gen: nBins, lowPt, highPt")
argParser.add_argument("--recoBinning",        action="store",      default=[30,20,220], type=int, nargs=3,                                  help="binning reco: nBins, lowPt, highPt")
argParser.add_argument("--year",               action="store",      default=2016,   type=int,  choices=[2016,2017,2018],                     help="Which year to plot?")
argParser.add_argument("--mode",               action="store",      default="all",  type=str,  choices=["mu", "e", "all"],                   help="lepton selection")
argParser.add_argument("--ttgSingleLep",       action="store_true",                                                                          help="Run on ttg single lepton sample only?")
argParser.add_argument("--normalize",          action="store_true",                                                                          help="Scale to 1 fb-1?")
argParser.add_argument("--small",              action="store_true",                                                                          help="Run only on a small subset of the data?")
argParser.add_argument("--noData",             action="store_true",                                                                          help="also plot data?")
argParser.add_argument("--overwrite",          action="store_true",                                                                          help="overwrite cache?")
args = argParser.parse_args()

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile=None )
logger_rt = logger_rt.get_logger( args.logLevel, logFile=None )

# Text on the plots
def drawObjects( plotData, lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    line = (0.65, 0.95, "%3.1f fb{}^{-1} (13 TeV)" % lumi_scale)
    lines = [
      (0.15, 0.95, "CMS #bf{#it{Preliminary}}" if plotData else "CMS #bf{#it{Simulation Preliminary}}"), 
      line
    ]
    return [tex.DrawLatex(*l) for l in lines]

if args.small:        args.plot_directory += "_small"
if args.noData:       args.plot_directory += "_noData"
if args.normalize:    args.plot_directory += "_normalized"
if args.ttgSingleLep: args.plot_directory += "_singleLep"

# get reco selection criteria lambda function
selection     = signalRegions[args.recoSelection]["lambda"]
setup         = Setup( year=args.year, photonSelection=False, checkOnly=True, runOnLxPlus=False ) #photonselection always false for qcd estimate
setup         = setup.sysClone( parameters=allRegions[args.recoSelection]["parameters"] )
recoselection = setup.selection( "MC", channel="all", **setup.defaultParameters() )
recoSelection = recoselection["prefix"]

nGen,  xminGen,  xmaxGen  = args.genBinning
nReco, xminReco, xmaxReco = args.recoBinning

cache_dir = os.path.join(cache_directory, "unfolding", str(args.year), "matrix")
dirDB     = MergingDirDB(cache_dir)

if   args.year == 2016: lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74

if args.normalize:
    lumi_scale = 1.

plot_directory_ = os.path.join( plot_directory, "unfolding", str(args.year), args.plot_directory, args.genSelection, args.recoSelection, args.mode )

reconstructionBinning = [ 50, 0.6, 2 ]
dresMatrix = { "name":"UnfoldingMatrix", "year":str(args.year), "mode":args.mode, "MCOnly":str(args.noData), "selection":args.recoSelection, "genSelection":args.genSelection, "genBin":"_".join(map(str,args.genBinning)),   "recoBin":"_".join(map(str,args.recoBinning)), "ttgSingleLepton":str(args.ttgSingleLep), "small":str(args.small) }
resMatrix  = "_".join( [ "_".join([k, v]) for k, v in dresMatrix.iteritems() ] )
dresRes    = { "name":"Reconstruction",      "year":str(args.year), "mode":args.mode, "MCOnly":str(args.noData), "selection":args.recoSelection, "genSelection":args.genSelection, "binning":"_".join(map(str,reconstructionBinning)), "ttgSingleLepton":str(args.ttgSingleLep), "small":str(args.small) }
resRes     = "_".join( [ "_".join([k, v]) for k, v in dresRes.iteritems() ] )
dresData   = { "name":"DataHistogram",   "year":str(args.year), "mode":args.mode, "selection":args.recoSelection, "recoBin":"_".join(map(str,args.recoBinning)) }
resData    = "_".join( [ "_".join([k, v]) for k, v in dresData.iteritems() ] )

if dirDB.contains(resData) and not args.noData:
    dataHist = dirDB.get( resData )
    logger.info("Getting cached data histograms!")
elif not args.noData:
    raise Exception( "No input data histogram found!" )

if dirDB.contains(resMatrix) and dirDB.contains(resRes) and not args.overwrite:
    matrix   = dirDB.get( resMatrix )
    resHisto = dirDB.get( resRes )
    logger.info("Re-using cached histograms!")

else:
    if args.year == 2016:
        from TTGammaEFT.Samples.nanoTuples_Summer16_private_incl_postProcessed         import TTGSemiLep_16, TTG_16
        sample = TTGSemiLep_16 if args.ttgSingleLep else TTG_16

    elif args.year == 2017:
        from TTGammaEFT.Samples.nanoTuples_Fall17_private_incl_postProcessed           import TTGSemiLep_17, TTG_17
        sample = TTGSemiLep_17 if args.ttgSingleLep else TTG_17

    elif args.year == 2018:
        from TTGammaEFT.Samples.nanoTuples_Autumn18_private_incl_postProcessed         import TTGSemiLep_18, TTG_18
        sample = TTGSemiLep_18 if args.ttgSingleLep else TTG_18

    norm = 1.
    if args.small:           
        sample.normalization=1.
        sample.reduceFiles( factor=100 )
        norm = 1./sample.normalization

    read_variables = [ "weight/F",
                       "nPhotonGood/I", "nJetGood/I", "nBTagGood/I", "nLeptonTight/I", "nLeptonVetoIsoCorr/I",
                       "PhotonGood0_pt/F",
                       "GenPhotonATLASUnfold0_pt/F", "GenPhotonCMSUnfold0_pt/F",
                       "nGenLeptonATLASUnfold/I", "nGenPhotonATLASUnfold/I", "nGenBJetATLASUnfold/I", "nGenJetsATLASUnfold/I",
                       "nGenLeptonCMSUnfold/I", "nGenPhotonCMSUnfold/I", "nGenBJetCMSUnfold/I", "nGenJetsCMSUnfold/I",
                     ]

    weight_    = lambda event, sample: event.weight * norm
    Plot.setDefaults(   stack=Stack( [sample] ), weight=staticmethod( weight_ ), selectionString=cutInterpreter.cutString( args.genSelection ) )
    Plot2D.setDefaults( stack=Stack( [sample] ), weight=staticmethod( weight_ ), selectionString=cutInterpreter.cutString( args.genSelection ) )

    unfold2D = Plot2D(
                       name      = "unfoldingMatrix",
                       texX      = "p^{gen}_{T}(#gamma) [GeV]",
                       texY      = "p^{reco}_{T}(#gamma) [GeV]",
                       attribute = (
                                     TreeVariable.fromString( args.genPtVariable + "/F" ),
                                     lambda event, sample: event.PhotonGood0_pt if selection( event, sample ) else 0.,
                                   ),
                       binning   = args.genBinning + args.recoBinning,
                       read_variables = read_variables,
                      )

    reconstruction = Plot(
                       name      = "reconstruction",
                       texX      = "p^{gen}_{T}(#gamma) / p^{reco}_{T}(#gamma)",
                       attribute = lambda event, sample: getattr( event, args.genPtVariable ) / event.PhotonGood0_pt if selection( event, sample ) else -999,
                       binning   = reconstructionBinning,
                       read_variables = read_variables,
                      )

    plotting.fill( [unfold2D, reconstruction], read_variables=read_variables )

    matrix   = unfold2D.histos[0][0]
    resHisto = reconstruction.histos[0][0]

    dirDB.add( resMatrix, matrix, overwrite=True )
    dirDB.add( resRes,    resHisto, overwrite=True )

matrix.Scale(lumi_scale)
resHisto.Scale(lumi_scale)

histos               = {}
histos["gen"]        = matrix.ProjectionX("gen")
histos["efficiency"] = ROOT.TH1D( "efficiency", "efficiency", nGen,  xminGen,  xmaxGen  )
histos["purity"]     = ROOT.TH1D( "purity",     "purity",     nReco, xminReco, xmaxReco )
histos["recoMC"]     = matrix.ProjectionY("reco")
histos["reconstruction"] = resHisto
if args.noData: histos["reco"] = histos["recoMC"]
else:           histos["reco"] = dataHisto

for i in range( nGen+1 ):
    genPt   = histos["gen"].GetBinCenter( i+1 )
    recoBin = histos["recoMC"].FindBin( genPt )
    gen     = histos["gen"].GetBinContent( i+1 )
    eff     = matrix.GetBinContent( i+1, recoBin ) / gen if gen else 0.
    histos["efficiency"].SetBinContent( i+1, eff )

for i in range( nReco+1 ):
    recoPt = histos["recoMC"].GetBinCenter( i+1 )
    genBin = histos["gen"].FindBin( recoPt )
    reco   = histos["recoMC"].GetBinContent( i+1 )
    pur    = matrix.GetBinContent( genBin, i+1 ) / reco if reco else 0.
    histos["purity"].SetBinContent( i+1, pur )


# UNFOLDING

# regularization
#regMode = ROOT.TUnfold.kRegModeNone
#regMode = ROOT.TUnfold.kRegModeSize
#regMode = ROOT.TUnfold.kRegModeDerivative
regMode = ROOT.TUnfold.kRegModeCurvature
#regMode = ROOT.TUnfold.kRegModeMixed

# extra contrains
#constraintMode = ROOT.TUnfold.kEConstraintNone
constraintMode = ROOT.TUnfold.kEConstraintArea

#mapping = ROOT.TUnfold.kHistMapOutputVert
mapping = ROOT.TUnfold.kHistMapOutputHoriz

#densityFlags = ROOT.TUnfoldDensity.kDensityModeNone
densityFlags = ROOT.TUnfoldDensity.kDensityModeUser
#densityFlags = ROOT.TUnfoldDensity.kDensityModeBinWidth
#densityFlags = ROOT.TUnfoldDensity.kDensityModeBinWidthAndUser

unfold = ROOT.TUnfoldDensity( matrix, mapping, regMode, constraintMode, densityFlags )
unfold.SetInput( histos["reco"] )

# add systematic error
#unfold.AddSysError(histUnfoldMatrixSys,"signalshape_SYS",ROOT.TUnfold.kHistMapOutputHoriz,ROOT.TUnfoldSys.kSysErrModeMatrix)

logTauX = ROOT.TSpline3()
logTauY = ROOT.TSpline3()
lCurve  = ROOT.TGraph()

# Here work needs to be done! Did not work in the tutorial! FIXME
iBest   = unfold.ScanLcurve(30,0,0,lCurve,logTauX,logTauY)
histos["unfolded"] = unfold.GetOutput("unfolded")

# reco unfolding
unfold.SetInput( histos["recoMC"] )
# add systematic error
#unfold.AddSysError(histUnfoldMatrixSys,"signalshape_SYS",ROOT.TUnfold.kHistMapOutputHoriz,ROOT.TUnfoldSys.kSysErrModeMatrix)
# Here work needs to be done! Did not work in the tutorial! FIXME
iBest   = unfold.ScanLcurve(30,0,0,lCurve,logTauX,logTauY)
histos["unfoldedMC"] = unfold.GetOutput("unfoldedMC")


# PLOT 

histos["gen"].style        = styles.lineStyle( ROOT.kBlack, width = 2 )
histos["efficiency"].style = styles.lineStyle( ROOT.kBlue, width = 2 )
histos["purity"].style     = styles.lineStyle( ROOT.kRed, width = 2 )
histos["reco"].style       = styles.errorStyle( ROOT.kBlack, width = 2 )
histos["recoMC"].style     = styles.errorStyle( ROOT.kBlack, width = 2 )
histos["unfolded"].style   = styles.errorStyle( ROOT.kBlack, width = 2 )
histos["unfoldedMC"].style = styles.errorStyle( ROOT.kBlack, width = 2 )
histos["reconstruction"].style = styles.errorStyle( ROOT.kBlack, width = 2 )

addons = []
if args.ttgSingleLep:  addons.append("tt#gamma 1l")
else:                  addons.append("tt#gamma")
if args.noData:        addons.append("MC")
else:                  addons.append("Data")
if args.mode != "all": addons.append(args.mode.replace("mu","#mu"))

histos["gen"].legendText        = "Generated Events (%s)"%", ".join(addons).replace(", Data",", MC")
histos["unfolded"].legendText   = "Particle Level (%s)"%", ".join(addons)
histos["unfoldedMC"].legendText = "Particle Level (%s)"%", ".join(addons).replace(", Data",", MC")
histos["efficiency"].legendText = "Efficiency"
histos["purity"].legendText     = "Purity"
histos["reco"].legendText       = "Detector Level (%s)"%", ".join(addons)
histos["recoMC"].legendText     = "Detector Level (%s)"%", ".join(addons).replace(", Data",", MC")
histos["reconstruction"].legendText = "Inverse Responce (%s)"%", ".join(addons).replace(", Data",", MC")

# remove the defaults again
Plot.setDefaults()
Plot2D.setDefaults()

# Unfolding matrix
unfold2D = Plot2D.fromHisto( "unfoldingMatrix", [[matrix]], texX = "p^{gen}_{T}(#gamma) [GeV]", texY = "p^{reco}_{T}(#gamma) [GeV]" )
plotting.draw2D( unfold2D,
                 plot_directory = plot_directory_,
                 logX = False, logY = False, logZ = True,
                 zRange = "auto",
                 drawObjects = drawObjects( not args.noData, lumi_scale ),
                 copyIndexPHP = True,
                )

plots = []
# gen pt
plots.append( Plot.fromHisto( args.genPtVariable, [[histos["gen"]]], texX = "p^{gen}_{T}(#gamma) [GeV]", texY = "Number of Events" ) )
# reco pt
plots.append( Plot.fromHisto( "PhotonGood0_pt", [[histos["reco"]]], texX = "p^{reco}_{T}(#gamma) [GeV]", texY = "Number of Events" ) )
# reco MC pt
plots.append( Plot.fromHisto( "PhotonGood0_pt_MC", [[histos["recoMC"]]], texX = "p^{reco}_{T}(#gamma) [GeV]", texY = "Number of Events" ) )
# unfolded pt
plots.append( Plot.fromHisto( "unfolded_pt", [[histos["unfolded"]]], texX = "p^{unfolded}_{T}(#gamma) [GeV]", texY = "Number of Events" ) )
# unfolded MC pt
plots.append( Plot.fromHisto( "unfolded_pt_MC", [[histos["unfoldedMC"]]], texX = "p^{unfolded}_{T}(#gamma) [GeV]", texY = "Number of Events" ) )
# unfolded pt + gen
plots.append( Plot.fromHisto( "closure", [[histos["unfoldedMC"]],[histos["gen"]]], texX = "p^{gen,unfolded}_{T}(#gamma) [GeV]", texY = "Number of Events" ) )
# efficiency
plots.append( Plot.fromHisto( "efficiency", [[histos["efficiency"]]], texX = "p^{reco}_{T}(#gamma) [GeV]", texY = "Efficiency" ) )
# purity
plots.append( Plot.fromHisto( "purity", [[histos["purity"]]], texX = "p^{gen}_{T}(#gamma) [GeV]", texY = "Purity" ) )
# purity and efficiency
plots.append( Plot.fromHisto( "purity_efficiency", [[histos["purity"]],[histos["efficiency"]]], texX = "p^{gen,reco}_{T}(#gamma) [GeV]", texY = "Purity, Efficiency" ) )
# reconstruction
plots.append( Plot.fromHisto( "reconstruction", [[histos["reconstruction"]]], texX = "p^{gen}_{T}(#gamma) / p^{reco}_{T}(#gamma)", texY = "Number of Events" ) )

for plot in plots:
    xShift = plot.name in ["efficiency","purity","purity_efficiency"]
    plotting.draw( plot,
                   plot_directory = plot_directory_,
                   logX = False, logY = plot.name=="reconstruction", sorting = False,
                   yRange = (0.01, "auto"),
                   drawObjects = drawObjects( not args.noData, lumi_scale ),
                   legend = [ (0.3+0.3*xShift,0.88-0.04*len(plot.histos),0.88,0.88), 1 ],
                   copyIndexPHP = True,
                   )


