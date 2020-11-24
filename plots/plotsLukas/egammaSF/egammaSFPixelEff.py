# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy

# RootTools
from RootTools.core.standard           import *

# Analysis
import Analysis.Tools.syncer as syncer

# Internal Imports
from TTGammaEFT.Tools.user             import plot_directory
from TTGammaEFT.Tools.cutInterpreter   import cutInterpreter

from TTGammaEFT.Samples.color          import color

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                        help="Log level for logging")
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv26_v1",                                             help="plot sub-directory")
argParser.add_argument("--selection",          action="store",      default="WJets2", type=str,                                              help="reco region")
argParser.add_argument("--year",               action="store",      default=2016,   type=int,  choices=[2016,2017,2018],                     help="Which year to plot?")
argParser.add_argument('--useZG',              action='store_true',                                                                    help='Run on DY+ZG w overlap removal', )
args = argParser.parse_args()

#args.binning  = [19, 10, 200]
#args.binning  = [10,15,20,25,30,35,40,50,60,70,90,120,200]
args.binning  = [10,30,60,200]
explicitBinning = len(args.binning)>3

if "nTPhoton" in args.selection:
    photon = "PhotonTight"
elif "nMPhoton" in args.selection:
    photon = "PhotonMedium"
elif "nLPhoton" in args.selection:
    photon = "PhotonLoose"
elif "nMVAPhoton" in args.selection:
    photon = "PhotonMVA"

args.variable = "%s0_pt"%photon
binningSF  = [10,30,60,200]
binningIncl  = [10,200]

if args.useZG: args.plot_directory += "_ZG"
else:          args.plot_directory += "_DY"

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

# Sample definition
if args.year == 2016:
    import TTGammaEFT.Samples.nanoTuples_Summer16_private_diMuGamma_postProcessed as mc_samples
    from   TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_diMuGamma_postProcessed import Run2016 as data_sample
elif args.year == 2017:
    import TTGammaEFT.Samples.nanoTuples_Fall17_private_diMuGamma_postProcessed as mc_samples
    from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_diMuGamma_postProcessed import Run2017 as data_sample
elif args.year == 2018:
    import TTGammaEFT.Samples.nanoTuples_Autumn18_private_diMuGamma_postProcessed as mc_samples
    from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_diMuGamma_postProcessed import Run2018 as data_sample

mc  = [ mc_samples.TT_pow, mc_samples.WJets ]
if args.useZG: mc += [mc_samples.ZG_lowpt]
else:          mc += [mc_samples.DY_LO]

lumi_scale   = data_sample.lumi * 0.001

selection  = cutInterpreter.cutString( args.selection )
selection += "&&reweightPU<2&&jsonPassed==1"
#if args.useZG: selection += "&&overlapRemoval==1"

selection_wPixel = selection + "&&%s0_pixelSeed==0"%photon

weightString = "%f*weight*reweightPU"%lumi_scale

dataHist = data_sample.get1DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection, addOverFlowBin="upper" )
dataHistSF = data_sample.get1DHistoFromDraw( args.variable, binning=binningSF, binningIsExplicit=explicitBinning, selectionString=selection, addOverFlowBin="upper" )
dataHistIncl = data_sample.get1DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection, addOverFlowBin="upper" )
#for s in bkg:
#    dataHist.Add( s.get1DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection, addOverFlowBin="upper" ), -1 )
#    dataHistSF.Add( s.get1DHistoFromDraw( args.variable, binning=binningSF, binningIsExplicit=explicitBinning, selectionString=selection, addOverFlowBin="upper" ), -1 )

dataHist_wPixel = data_sample.get1DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, addOverFlowBin="upper" )
dataHistSF_wPixel = data_sample.get1DHistoFromDraw( args.variable, binning=binningSF, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, addOverFlowBin="upper" )
dataHistIncl_wPixel = data_sample.get1DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, addOverFlowBin="upper" )
#for s in bkg:
#    dataHist_wPixel.Add( s.get1DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, addOverFlowBin="upper" ), -1 )
#    dataHistSF_wPixel.Add( s.get1DHistoFromDraw( args.variable, binning=binningSF, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, addOverFlowBin="upper" ), -1 )

print "data"
for i in range(dataHist.GetNbinsX()):
    print i, dataHist.GetBinContent(i+1) 

dataHist_teff = ROOT.TEfficiency( dataHist_wPixel, dataHist )
dataHistSF_teff = ROOT.TEfficiency( dataHistSF_wPixel, dataHistSF )
dataHistIncl_teff = ROOT.TEfficiency( dataHistIncl_wPixel, dataHistIncl )

dataHist_eff = dataHist_wPixel.Clone("dataratio")
dataHist_eff.Divide(dataHist)
dataHist_eff.style         = styles.errorStyle( ROOT.kBlack )
dataHist_eff.legendText    = "pixelSeed Efficiency Data (#mu#mu#gamma)"

dataHistSF_eff = dataHistSF_wPixel.Clone("dataratioSF")
dataHistSF_eff.Divide(dataHistSF)
dataHistSF_eff.style         = styles.errorStyle( ROOT.kBlack )
dataHistSF_eff.legendText    = "pixelSeed Efficiency Data (#mu#mu#gamma)"

dataHistIncl_eff = dataHistIncl_wPixel.Clone("dataratioIncl")
dataHistIncl_eff.Divide(dataHistIncl)
dataHistIncl_eff.style         = styles.errorStyle( ROOT.kBlack )
dataHistIncl_eff.legendText    = "pixelSeed Efficiency Data (#mu#mu#gamma)"

for i in range(dataHist_eff.GetNbinsX()):
    dataHist_eff.SetBinError(i+1, dataHist_teff.GetEfficiencyErrorUp(i+1))

for i in range(dataHistSF_eff.GetNbinsX()):
    dataHistSF_eff.SetBinError(i+1, dataHistSF_teff.GetEfficiencyErrorUp(i+1))

for i in range(dataHistIncl_eff.GetNbinsX()):
    dataHistIncl_eff.SetBinError(i+1, dataHistIncl_teff.GetEfficiencyErrorUp(i+1))

mcHist = dataHist.Clone("mc")
mcHist.Scale(0)
mcHistSF = dataHistSF.Clone("mcSF")
mcHistSF.Scale(0)
mcHistIncl = dataHistIncl.Clone("mcIncl")
mcHistIncl.Scale(0)
for s in mc:
    mcHist.Add(s.get1DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection, addOverFlowBin="upper" ) )
    mcHistSF.Add(s.get1DHistoFromDraw( args.variable, binning=binningSF, binningIsExplicit=explicitBinning, selectionString=selection, addOverFlowBin="upper" ) )
    mcHistIncl.Add(s.get1DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection, addOverFlowBin="upper" ) )

print "MC"
for i in range(mcHist.GetNbinsX()):
    print i, mcHist.GetBinContent(i+1) 

mcHist_wPixel = dataHist.Clone("mcP")
mcHist_wPixel.Scale(0)
mcHistSF_wPixel = dataHistSF.Clone("mcPSF")
mcHistSF_wPixel.Scale(0)
mcHistIncl_wPixel = dataHistIncl.Clone("mcPIncl")
mcHistIncl_wPixel.Scale(0)
for s in mc:
    mcHist_wPixel.Add(s.get1DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, addOverFlowBin="upper" ) )
    mcHistSF_wPixel.Add(s.get1DHistoFromDraw( args.variable, binning=binningSF, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, addOverFlowBin="upper" ) )
    mcHistIncl_wPixel.Add(s.get1DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, addOverFlowBin="upper" ) )

mcHist_teff = ROOT.TEfficiency( mcHist_wPixel, mcHist )
mcHistSF_teff = ROOT.TEfficiency( mcHistSF_wPixel, mcHistSF )
mcHistIncl_teff = ROOT.TEfficiency( mcHistIncl_wPixel, mcHistIncl )

mcHist_teff.SetLineColor(ROOT.kRed)
mcHistSF_teff.SetLineColor(ROOT.kRed)
mcHistIncl_teff.SetLineColor(ROOT.kRed)
mcHist_teff.SetLineWidth(3)
mcHistSF_teff.SetLineWidth(3)
mcHistIncl_teff.SetLineWidth(3)

mcHist_eff = mcHist_wPixel.Clone("mcratio")
mcHist_eff.Divide(mcHist)
mcHist_eff.style         = styles.errorStyle( ROOT.kRed )
mcHist_eff.legendText    = "pixelSeed Efficiency MC"
if args.useZG: mcHist_eff.legendText += " (Z#gamma)"
else:          mcHist_eff.legendText += " (DY)"

mcHistSF_eff = mcHistSF_wPixel.Clone("mcratioSF")
mcHistSF_eff.Divide(mcHistSF)
mcHistSF_eff.style         = styles.errorStyle( ROOT.kRed )
mcHistSF_eff.legendText    = "pixelSeed Efficiency MC"
if args.useZG: mcHistSF_eff.legendText += " (Z#gamma)"
else:          mcHistSF_eff.legendText += " (DY)"

mcHistIncl_eff = mcHistIncl_wPixel.Clone("mcratioIncl")
mcHistIncl_eff.Divide(mcHistIncl)
mcHistIncl_eff.style         = styles.errorStyle( ROOT.kRed )
mcHistIncl_eff.legendText    = "pixelSeed Efficiency MC"
if args.useZG: mcHistIncl_eff.legendText += " (Z#gamma)"
else:          mcHistIncl_eff.legendText += " (DY)"

for i in range(mcHist_eff.GetNbinsX()):
    mcHist_eff.SetBinError(i+1, mcHist_teff.GetEfficiencyErrorUp(i+1))

for i in range(mcHistSF_eff.GetNbinsX()):
    mcHistSF_eff.SetBinError(i+1, mcHistSF_teff.GetEfficiencyErrorUp(i+1))

for i in range(mcHistIncl_eff.GetNbinsX()):
    mcHistIncl_eff.SetBinError(i+1, mcHistIncl_teff.GetEfficiencyErrorUp(i+1))

Plot.setDefaults()
plots = []
plots.append( Plot.fromHisto( args.variable,           [[mcHist_eff], [dataHist_eff]], texX="p_{T}(#gamma)", texY="Efficiency" ) )
plots.append( Plot.fromHisto( args.variable+"_coarse", [[mcHistSF_eff], [dataHistSF_eff]], texX="p_{T}(#gamma)", texY="Efficiency" ) )
plots.append( Plot.fromHisto( args.variable+"_incl", [[mcHistIncl_eff], [dataHistIncl_eff]], texX="p_{T}(#gamma)", texY="Efficiency" ) )

for plot in plots:

    legend = (0.2,0.75,0.9,0.9)

    for log in [True, False]:

#        ratio = {'yRange':(0.78,1.22),'texY': 'Scale factor'}
        if "coarse" in plot.name:
            ratio = {'yRange':(0.73,1.27),'texY': 'Scale factor', 'histos':[(0,0),(1,0)]}
            key = "SF"
        elif "incl" in plot.name:
            ratio = {'yRange':(0.93,1.07),'texY': 'Scale factor', 'histos':[(0,0),(1,0)]}
            key = "incl"
        else:
            ratio = {'yRange':(0.78,1.22),'texY': 'Scale factor', 'histos':[(0,0),(1,0)]}
            key = "nom"

        selDir = args.selection
        plot_directory_ = os.path.join( plot_directory, "EGammaEff", str(args.year), args.plot_directory, selDir, "log" if log else "lin" )
        plotting.draw( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = log, sorting = True,
                       yRange = (0.15, 1.3),
                       ratio = ratio,
                       drawObjects = drawObjects( lumi_scale ),
                       legend = legend,
                       copyIndexPHP = True,
                       )

