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
#args.binning = [[10,30,60,200], [0, 1.4442, 1.566, 2.5]]
args.binning = [[10,30,60,200], [0, 1.4442, 1.566, 2.4]]
#args.binning = [[10,30,60,200], [1.566, 2.5]]
#args.binning = [[10,30,60,200], [0, 1.4442]]
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

mc  = [ mc_samples.TT_pow, mc_samples.WJets ]
if args.useZG: mc += [mc_samples.ZG_lowpt]
else: mc += [mc_samples.DY_LO]

lumi_scale   = data_sample.lumi * 0.001

selection  = cutInterpreter.cutString( args.selection )
selection += "&&reweightPU<2&&jsonPassed==1"
#if args.useZG: selection += "&&overlapRemoval==1"

selection_wPixel = selection + "&&%s0_pixelSeed==0"%photon

weightString = "%f*weight*reweightPU"%lumi_scale
#weightStringUp = "%f*weight*reweightPUUp"%lumi_scale
#weightStringDown = "%f*weight*reweightPUDown"%lumi_scale

dataHist = data_sample.get2DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection )
dataHistIncl = data_sample.get2DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection )

dataHist_wPixel = data_sample.get2DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection_wPixel )
dataHistIncl_wPixel = data_sample.get2DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection_wPixel )

print "data"
dataHist_teff = ROOT.TEfficiency( dataHist_wPixel, dataHist )
print "data incl"
dataHistIncl_teff = ROOT.TEfficiency( dataHistIncl_wPixel, dataHistIncl )

dataHist_eff = dataHist_teff.CreateHistogram()
dataHist_eff.style         = styles.errorStyle( ROOT.kBlack )
dataHist_eff.legendText    = "pixelSeed Efficiency Data (#mu#mu#gamma)"

dataHistIncl_eff = dataHistIncl_teff.CreateHistogram()
dataHistIncl_eff.style         = styles.errorStyle( ROOT.kBlack )
dataHistIncl_eff.legendText    = "pixelSeed Efficiency Data (#mu#mu#gamma)"

for i in range( dataHist_eff.GetNbinsX() ):
    for j in range( dataHist_eff.GetNbinsY() ):
        dataHist_eff.SetBinError(i+1,j+1, dataHist_teff.GetEfficiencyErrorLow(dataHist_teff.GetGlobalBin(i+1,j+1)))

for i in range( dataHistIncl_eff.GetNbinsX() ):
    for j in range( dataHistIncl_eff.GetNbinsY() ):
        dataHistIncl_eff.SetBinError(i+1,j+1, dataHistIncl_teff.GetEfficiencyErrorLow(dataHistIncl_teff.GetGlobalBin(i+1,j+1)))

mcHist = dataHist.Clone()
mcHist.Reset()

#mcHistUp = mcHist.Clone()
#mcHistUp.Reset()
#mcHistDown = mcHist.Clone()
#mcHistDown.Reset()

mcHistIncl = dataHistIncl.Clone()
mcHistIncl.Reset()

#mcHistInclUp = mcHistIncl.Clone()
#mcHistInclUp.Reset()
#mcHistInclDown = mcHistIncl.Clone()
#mcHistInclDown.Reset()

for s in mc:
    mcHist.Add( s.get2DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection, weightString=weightString ) )
#    mcHistUp.Add( s.get2DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection, weightString=weightStringUp ) )
#    mcHistDown.Add( s.get2DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection, weightString=weightStringDown ) )
    mcHistIncl.Add( s.get2DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection, weightString=weightString ) )
#    mcHistInclUp.Add( s.get2DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection, weightString=weightStringUp ) )
#    mcHistInclDown.Add( s.get2DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection, weightString=weightStringDown ) )

mcHist_wPixel = dataHist.Clone()
mcHist_wPixel.Reset()

#mcHistUp_wPixel = copy.deepcopy(dataHist.Clone())
#mcHistUp_wPixel.Reset()
#mcHistDown_wPixel = copy.deepcopy(dataHist.Clone())
#mcHistDown_wPixel.Reset()

mcHistIncl_wPixel = dataHistIncl.Clone()
mcHistIncl_wPixel.Reset()

#mcHistInclUp_wPixel = copy.deepcopy(dataHistIncl.Clone())
#mcHistInclUp_wPixel.Reset(
#mcHistInclDown_wPixel = copy.deepcopy(dataHistIncl.Clone())
#mcHistInclDown_wPixel.Reset()

for s in mc:
    mcHist_wPixel.Add( s.get2DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, weightString=weightString ) )
#    mcHistUp_wPixel.Add( s.get2DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, weightString=weightStringUp ) )
#    mcHistDown_wPixel.Add( s.get2DHistoFromDraw( args.variable, binning=args.binning, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, weightString=weightStringDown ) )
    mcHistIncl_wPixel.Add( s.get2DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, weightString=weightString ) )
#    mcHistInclUp_wPixel.Add( s.get2DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, weightString=weightStringUp ) )
#    mcHistInclDown_wPixel.Add( s.get2DHistoFromDraw( args.variable, binning=binningIncl, binningIsExplicit=explicitBinning, selectionString=selection_wPixel, weightString=weightStringDown ) )

#for i in range( mcHist.GetNbinsX() ):
#    mcHist.SetBinContent(i+1, 2, 1)
#    mcHist_wPixel.SetBinContent(i+1, 2, .1)
#for i in range( mcHistIncl.GetNbinsX() ):
#    mcHistIncl.SetBinContent(i+1, 2, 1)
#    mcHistIncl_wPixel.SetBinContent(i+1, 2, .1)

#PU uncertainty
#print "puUp"
#mcHist_PUup = ROOT.TEfficiency( mcHistUp_wPixel, mcHistUp )
#mcHist_PUup = mcHist_PUup.CreateHistogram()
#print "puUp"
#mcHistIncl_PUup = ROOT.TEfficiency( mcHistInclUp_wPixel, mcHistInclUp )
#mcHistIncl_PUup = mcHistIncl_PUup.CreateHistogram()

#print "pudown"
#mcHist_PUdown = ROOT.TEfficiency( mcHistDown_wPixel, mcHistDown )
#mcHist_PUdown = mcHist_PUdown.CreateHistogram()
#print "pudown"
#mcHistIncl_PUdown = ROOT.TEfficiency( mcHistInclDown_wPixel, mcHistInclDown )
#mcHistIncl_PUdown = mcHistIncl_PUdown.CreateHistogram()

#mcHist_PUup.Add(mcHist_PUdown, -1)
#mcHistIncl_PUup.Add(mcHistIncl_PUdown, -1)
#mcHist_PUup.Scale(0.5)
#mcHistIncl_PUup.Scale(0.5)

#for i in range( mcHist_PUup.GetNbinsX() ):
#    for j in range( mcHist_PUup.GetNbinsY() ):
#        mcHist_PUup.SetBinError(i+1, j+1, abs(mcHist_PUup.GetBinContent(i+1, j+1)))
#        mcHist_PUup.SetBinContent(i+1, j+1, 0)

#for i in range( mcHistIncl_PUup.GetNbinsX() ):
#    for j in range( mcHistIncl_PUup.GetNbinsY() ):
#        mcHistIncl_PUup.SetBinError(i+1, j+1, abs(mcHistIncl_PUup.GetBinContent(i+1, j+1)))
#        mcHistIncl_PUup.SetBinContent(i+1, j+1, 0)

print "mc"
#for i in range( mcHist_wPixel.GetNbinsX() ):
#    for j in range( mcHist_wPixel.GetNbinsY() ):
#        mcHist_wPixel.SetBinContent(i+1,j+1,int(mcHist_wPixel.GetBinContent(i+1,j+1)))
#        mcHist.SetBinContent(i+1,j+1,int(mcHist.GetBinContent(i+1,j+1)))

#for i in range( mcHistIncl_wPixel.GetNbinsX() ):
#    for j in range( mcHistIncl_wPixel.GetNbinsY() ):
#        mcHistIncl_wPixel.SetBinContent(i+1,j+1,int(mcHistIncl_wPixel.GetBinContent(i+1,j+1)))
#        mcHistIncl.SetBinContent(i+1,j+1,int(mcHistIncl.GetBinContent(i+1,j+1)))

mcHist_teff = ROOT.TEfficiency( mcHist_wPixel, mcHist )
print "mcincl"
mcHistIncl_teff = ROOT.TEfficiency( mcHistIncl_wPixel, mcHistIncl )

mcHistIncl_eff = mcHistIncl_teff.CreateHistogram()
mcHist_eff = mcHist_teff.CreateHistogram()

for i in range( mcHist_eff.GetNbinsX() ):
    for j in range( mcHist_eff.GetNbinsY() ):
        mcHist_eff.SetBinError(i+1,j+1, mcHist_teff.GetEfficiencyErrorLow(mcHist_teff.GetGlobalBin(i+1,j+1)))

for i in range( mcHistIncl_eff.GetNbinsX() ):
    for j in range( mcHistIncl_eff.GetNbinsY() ):
        mcHistIncl_eff.SetBinError(i+1,j+1, mcHistIncl_teff.GetEfficiencyErrorLow(mcHistIncl_teff.GetGlobalBin(i+1,j+1)))

#mcHist_eff.Add(mcHist_PUup) #add PU uncertainty
#mcHistIncl_eff.Add(mcHistIncl_PUup) #add PU uncertainty

dataHist_eff.Divide(mcHist_eff)
dataHist_unc = dataHist_eff.Clone()

dataHistIncl_eff.Divide(mcHistIncl_eff)
dataHistIncl_unc = dataHistIncl_eff.Clone()

mcHist_unc = mcHist_eff.Clone()
mcHistIncl_unc = mcHistIncl_eff.Clone()

for i in range( mcHist_eff.GetNbinsX() ):
    for j in range( mcHist_eff.GetNbinsY() ):
        print mcHist_eff.GetBinContent(i+1,j+1), mcHist_eff.GetBinError(i+1,j+1)

for i in range( mcHist_unc.GetNbinsX() ):
    for j in range( mcHist_unc.GetNbinsY() ):
        mcHist_unc.SetBinContent(i+1, j+1, mcHist_unc.GetBinError(i+1, j+1) )

for i in range( mcHistIncl_eff.GetNbinsX() ):
    for j in range( mcHistIncl_eff.GetNbinsY() ):
        mcHistIncl_eff.SetBinContent(i+1, j+1, mcHistIncl_eff.GetBinError(i+1, j+1) )

for i in range( dataHist_unc.GetNbinsX() ):
    for j in range( dataHist_unc.GetNbinsY() ):
        dataHist_unc.SetBinContent(i+1, j+1, dataHist_unc.GetBinError(i+1, j+1))

for i in range( dataHistIncl_unc.GetNbinsX() ):
    for j in range( dataHistIncl_unc.GetNbinsY() ):
        dataHistIncl_unc.SetBinContent(i+1, j+1, dataHistIncl_unc.GetBinError(i+1, j+1) )

for i in range( dataHist_unc.GetNbinsX() ):
    mcHist_unc.SetBinContent(i+1, 2, 0)
    dataHist_unc.SetBinContent(i+1, 2, 0)
    dataHist_eff.SetBinContent(i+1, 2, 0)
    for j in range( dataHist_unc.GetNbinsY() ):
        mcHist_unc.SetBinContent(i+1, j+1, round(mcHist_unc.GetBinContent(i+1,j+1), 4))
        dataHist_unc.SetBinContent(i+1, j+1, round(dataHist_unc.GetBinContent(i+1,j+1), 4))
        dataHist_eff.SetBinContent(i+1, j+1, round(dataHist_eff.GetBinContent(i+1,j+1), 4))

for i in range( dataHistIncl_unc.GetNbinsX() ):
    mcHistIncl_unc.SetBinContent(i+1, 2, 0)
    dataHistIncl_unc.SetBinContent(i+1, 2, 0)
    dataHistIncl_eff.SetBinContent(i+1, 2, 0)
    for j in range( dataHistIncl_unc.GetNbinsY() ):
        mcHistIncl_unc.SetBinContent(i+1, j+1, round(mcHistIncl_unc.GetBinContent(i+1,j+1), 4))
        dataHistIncl_unc.SetBinContent(i+1, j+1, round(dataHistIncl_unc.GetBinContent(i+1,j+1), 4))
        dataHistIncl_eff.SetBinContent(i+1, j+1, round(dataHistIncl_eff.GetBinContent(i+1,j+1), 4))


tRootFile = ROOT.TFile( "g2018_HasPix_private.root", "RECREATE" )
dataHist_eff.SetName("scalefactor")
dataHist_unc.SetName("uncertainty")
dataHist_eff.SetTitle("scalefactor")
dataHist_unc.SetTitle("uncertainty")
dataHist_eff.Write()
dataHist_unc.Write()
tRootFile.Close()


Plot2D.setDefaults()
plots = []
plots.append( Plot2D.fromHisto( "scaleFactor",           [[dataHist_eff]], texX="p_{T}(#gamma)", texY="|#eta(#gamma)|" ) )
plots.append( Plot2D.fromHisto( "uncertainty",           [[dataHist_unc]], texX="p_{T}(#gamma)", texY="|#eta(#gamma)|" ) )
plots.append( Plot2D.fromHisto( "uncertainty_MCeff",           [[mcHist_unc]], texX="p_{T}(#gamma)", texY="|#eta(#gamma)|" ) )
plots.append( Plot2D.fromHisto( "scaleFactor_incl",      [[dataHistIncl_eff]], texX="p_{T}(#gamma)", texY="|#eta(#gamma)|" ) )
plots.append( Plot2D.fromHisto( "uncertainty_incl",      [[dataHistIncl_unc]], texX="p_{T}(#gamma)", texY="|#eta(#gamma)|" ) )
plots.append( Plot2D.fromHisto( "uncertainty_MCeff_incl",      [[mcHistIncl_unc]], texX="p_{T}(#gamma)", texY="|#eta(#gamma)|" ) )

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

