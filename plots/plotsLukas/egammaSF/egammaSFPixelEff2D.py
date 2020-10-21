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
args.binning = [[10,30,60,200], [0, 1.4442, 1.566, 2.5]]
#args.binning = [[10,30,70,100, 110, 120,140, 200], [0, 1.4442, 1.566, 2.5]]
binningIncl = [[10,200], [0, 1.4442, 1.566, 2.5]]
explicitBinning = True

if "nTPhoton" in args.selection:
    photon = "PhotonTight"
elif "nMPhoton" in args.selection:
    photon = "PhotonMedium"
elif "nLPhoton" in args.selection:
    photon = "PhotonLoose"
elif "nMVAPhoton" in args.selection:
    photon = "PhotonMVA"

# histos
args.variable = "abs(%s0_eta):%s0_pt"%(photon,photon)

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

bkg  = []
mc  = [ mc_samples.DY_LO, mc_samples.TT_pow, mc_samples.WJets ]
if args.useZG: mc += [mc_samples.ZG_lowpt]

lumi_scale   = data_sample.lumi * 0.001

selection  = cutInterpreter.cutString( args.selection )
selection += "&&reweightPU<2&&jsonPassed==1"
if args.useZG: selection += "&&overlapRemoval==1"

selection_wPixel = selection + "&&%s0_pixelSeed==0"%photon

weightString = "%f*weight*reweightPU"%lumi_scale
weightStringUp = "%f*weight*reweightPUUp"%lumi_scale
weightStringDown = "%f*weight*reweightPUDown"%lumi_scale

dataHist = data_sample.get2DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection )
dataHistIncl = data_sample.get2DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection )

dataHist_wPixel = data_sample.get2DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection_wPixel )
dataHistIncl_wPixel = data_sample.get2DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection_wPixel )


dataHist_eff = dataHist_wPixel.Clone("dataratio")
dataHist_eff.Divide(dataHist)
dataHist_eff.style         = styles.errorStyle( ROOT.kBlack )
dataHist_eff.legendText    = "pixelSeed Efficiency Data (#mu#mu#gamma)"

dataHistIncl_eff = dataHistIncl_wPixel.Clone("dataratioIncl")
dataHistIncl_eff.Divide(dataHistIncl)
dataHistIncl_eff.style         = styles.errorStyle( ROOT.kBlack )
dataHistIncl_eff.legendText    = "pixelSeed Efficiency Data (#mu#mu#gamma)"


mcHist = dataHist.Clone("mc")
mcHist.Reset()
mcHistBkg = dataHist.Clone("mcU")
mcHistBkg.Reset()

mcHistUp = mcHist.Clone("mcup")
mcHistDown = mcHist.Clone("mcdown")

mcHistIncl = dataHistIncl.Clone("mcIncl")
mcHistIncl.Reset()
mcHistInclBkg = dataHistIncl.Clone("mcInclBkg")
mcHistInclBkg.Reset()

mcHistInclUp = mcHistIncl.Clone("mcInclup")
mcHistInclDown = mcHistIncl.Clone("mcIncldown")

for s in mc:
    mcHist.Add( s.get2DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection, weightString=weightString ) )
    mcHistBkg.Add( s.get2DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection, weightString=weightString ) )
    mcHistUp.Add( s.get2DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection, weightString=weightStringUp ) )
    mcHistDown.Add( s.get2DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection, weightString=weightStringDown ) )
    mcHistIncl.Add( s.get2DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection, weightString=weightString ) )
    mcHistInclBkg.Add( s.get2DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection, weightString=weightString ) )
    mcHistInclUp.Add( s.get2DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection, weightString=weightStringUp ) )
    mcHistInclDown.Add( s.get2DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection, weightString=weightStringDown ) )

for s in bkg:
    mcHistBkg.Add( s.get2DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection, weightString=weightString ) )
    mcHistInclBkg.Add( s.get2DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection, weightString=weightString ) )

mcHist_wPixel = dataHist.Clone("mcP")
mcHist_wPixel.Reset()
mcHistBkg_wPixel = dataHist.Clone("mcPU")
mcHistBkg_wPixel.Reset()

mcHistUp_wPixel = mcHist_wPixel.Clone("mcPUp")
mcHistDown_wPixel = mcHist_wPixel.Clone("mcPDown")

mcHistIncl_wPixel = dataHistIncl.Clone("mcPIncl")
mcHistIncl_wPixel.Reset()
mcHistInclBkg_wPixel = dataHistIncl.Clone("mcPInclBkg")
mcHistInclBkg_wPixel.Reset()

mcHistInclUp_wPixel = mcHistIncl_wPixel.Clone("mcPInclUp")
mcHistInclDown_wPixel = mcHistIncl_wPixel.Clone("mcPInclDown")
for s in mc:
    mcHist_wPixel.Add( s.get2DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, weightString=weightString ) )
    mcHistBkg_wPixel.Add( s.get2DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, weightString=weightString ) )
    mcHistUp_wPixel.Add( s.get2DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, weightString=weightStringUp ) )
    mcHistDown_wPixel.Add( s.get2DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, weightString=weightStringDown ) )
    mcHistIncl_wPixel.Add( s.get2DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, weightString=weightString ) )
    mcHistInclBkg_wPixel.Add( s.get2DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, weightString=weightString ) )
    mcHistInclUp_wPixel.Add( s.get2DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, weightString=weightStringUp ) )
    mcHistInclDown_wPixel.Add( s.get2DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, weightString=weightStringDown ) )

for s in bkg:
    mcHistBkg_wPixel.Add( s.get2DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, weightString=weightString ) )
    mcHistInclBkg_wPixel.Add( s.get2DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, weightString=weightString ) )

#PU uncertainty
mcHistUp_wPixel.Divide(mcHistUp)
mcHistDown_wPixel.Divide(mcHistDown)
mcHistInclUp_wPixel.Divide(mcHistInclUp)
mcHistInclDown_wPixel.Divide(mcHistInclDown)

mcHistUp_wPixel.Add(mcHistDown_wPixel, -1)
mcHistInclUp_wPixel.Add(mcHistInclDown_wPixel, -1)
mcHistUp_wPixel.Scale(0.5)
mcHistInclUp_wPixel.Scale(0.5)

mcHistIncl_eff = mcHistIncl_wPixel.Clone("mcratioIncl")
mcHistIncl_eff.Divide(mcHistIncl)
mcHistIncl_eff.style         = styles.errorStyle( ROOT.kRed )
mcHistIncl_eff.legendText    = "pixelSeed Efficiency MC"
if args.useZG: mcHistIncl_eff.legendText += " (DY+Z#gamma)"
else:          mcHistIncl_eff.legendText += " (DY)"

mcHist_eff = mcHist_wPixel.Clone("mcratio")
mcHist_eff.Divide(mcHist)
mcHist_eff.style         = styles.errorStyle( ROOT.kRed )
mcHist_eff.legendText    = "pixelSeed Efficiency MC"
if args.useZG: mcHist_eff.legendText += " (DY+Z#gamma)"
else:          mcHist_eff.legendText += " (DY)"

mcHistInclBkg_eff = mcHistInclBkg_wPixel.Clone("mcratioInclBkg")
mcHistInclBkg_eff.Divide(mcHistInclBkg)
mcHistInclBkg_eff.style         = styles.errorStyle( ROOT.kRed )
mcHistInclBkg_eff.legendText    = "pixelSeed Efficiency MC"
if args.useZG: mcHistInclBkg_eff.legendText += " (DY+Z#gamma)"
else:          mcHistInclBkg_eff.legendText += " (DY)"

mcHistBkg_eff = mcHistBkg_wPixel.Clone("mcratio")
mcHistBkg_eff.Divide(mcHistBkg)
mcHistBkg_eff.style         = styles.errorStyle( ROOT.kRed )
mcHistBkg_eff.legendText    = "pixelSeed Efficiency MC"
if args.useZG: mcHistBkg_eff.legendText += " (DY+Z#gamma)"
else:          mcHistBkg_eff.legendText += " (DY)"


for i in range( mcHistUp.GetNbinsX() ):
    for j in range( mcHistUp.GetNbinsY() ):
        print abs(mcHistUp_wPixel.GetBinContent(i+1, j+1))

        mcHistUp_wPixel.SetBinError(i+1, j+1, abs(mcHistUp_wPixel.GetBinContent(i+1, j+1)))
        mcHistUp_wPixel.SetBinContent(i+1, j+1, 0)

for i in range( mcHistInclUp.GetNbinsX() ):
    for j in range( mcHistInclUp.GetNbinsY() ):
        print abs(mcHistInclUp_wPixel.GetBinContent(i+1, j+1))

        mcHistInclUp_wPixel.SetBinError(i+1, j+1, abs(mcHistInclUp_wPixel.GetBinContent(i+1, j+1)))
        mcHistInclUp_wPixel.SetBinContent(i+1, j+1, 0)

mcHist_eff.Add(mcHistUp_wPixel) #add PU uncertainty
mcHistIncl_eff.Add(mcHistInclUp_wPixel) #add PU uncertainty
mcHistBkg_eff.Add(mcHistUp_wPixel) #add PU uncertainty
mcHistInclBkg_eff.Add(mcHistInclUp_wPixel) #add PU uncertainty

dataHist_unc = dataHist_eff.Clone()
dataHist_eff.Divide(mcHistBkg_eff)
dataHist_unc.Divide(mcHist_eff)

dataHistIncl_unc = dataHistIncl_eff.Clone()
dataHistIncl_eff.Divide(mcHistInclBkg_eff)
dataHistIncl_unc.Divide(mcHistIncl_eff)

for i in range( dataHist_unc.GetNbinsX() ):
    for j in range( dataHist_unc.GetNbinsY() ):
        dataHist_unc.SetBinContent(i+1, j+1, mcHistBkg_eff.GetBinError(i+1, j+1)-mcHistBkg_eff.GetBinContent(i+1, j+1) )

for i in range( dataHistIncl_unc.GetNbinsX() ):
    for j in range( dataHistIncl_unc.GetNbinsY() ):
        dataHistIncl_unc.SetBinContent(i+1, j+1, mcHistIncl_eff.GetBinError(i+1, j+1)-mcHistIncl_eff.GetBinContent(i+1, j+1) )

for i in range( dataHist_unc.GetNbinsX() ):
    dataHist_unc.SetBinContent(i+1, 2, 0)
    dataHist_eff.SetBinContent(i+1, 2, 0)
    for j in range( dataHist_unc.GetNbinsY() ):
        dataHist_unc.SetBinContent(i+1, j+1, round(dataHist_unc.GetBinContent(i+1,j+1), 4))
        dataHist_eff.SetBinContent(i+1, j+1, round(dataHist_eff.GetBinContent(i+1,j+1), 4))

for i in range( dataHistIncl_unc.GetNbinsX() ):
    dataHistIncl_unc.SetBinContent(i+1, 2, 0)
    dataHistIncl_eff.SetBinContent(i+1, 2, 0)
    for j in range( dataHistIncl_unc.GetNbinsY() ):
        dataHistIncl_unc.SetBinContent(i+1, j+1, round(dataHistIncl_unc.GetBinContent(i+1,j+1), 4))
        dataHistIncl_eff.SetBinContent(i+1, j+1, round(dataHistIncl_eff.GetBinContent(i+1,j+1), 4))

Plot2D.setDefaults()
plots = []
plots.append( Plot2D.fromHisto( "scaleFactor",           [[dataHist_eff]], texX="p_{T}(#gamma)", texY="|#eta(#gamma)|" ) )
plots.append( Plot2D.fromHisto( "uncertainty",           [[dataHist_unc]], texX="p_{T}(#gamma)", texY="|#eta(#gamma)|" ) )
plots.append( Plot2D.fromHisto( "scaleFactor_incl",      [[dataHistIncl_eff]], texX="p_{T}(#gamma)", texY="|#eta(#gamma)|" ) )
plots.append( Plot2D.fromHisto( "uncertainty_incl",      [[dataHistIncl_unc]], texX="p_{T}(#gamma)", texY="|#eta(#gamma)|" ) )

for plot in plots:

    plot.drawOption = "COLZTEXT"
    legend = (0.2,0.75,0.9,0.9)

    for log in [True, False]:

        selDir = args.selection
        plot_directory_ = os.path.join( plot_directory, "EGammaEff", str(args.year), args.plot_directory, selDir, "log" if log else "lin" )

        plotting.draw2D( plot,
                       plot_directory = plot_directory_,
                       logX = False, logY = False, logZ = log,
                       zRange = (0.85,1.1) if "scaleFactor" in plot.name else (0,0.1),
                       drawObjects = drawObjects( lumi_scale ),
                       copyIndexPHP = True,
                       oldColors = True,
                       )

