# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy, math

# RootTools
from RootTools.core.standard           import *

# Analysis
from Analysis.Tools.metFilters         import getFilterCut
import Analysis.Tools.syncer as syncer

# Internal Imports
from TTGammaEFT.Tools.user               import plot_directory
from TTGammaEFT.Tools.cutInterpreter     import cutInterpreter
from TTGammaEFT.Tools.objectSelection    import deltaRCleaning

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                        help="Log level for logging")
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv44_v2",                                             help="plot sub-directory")
argParser.add_argument("--object",             action="store",      default="photon",   type=str, choices=["photon","electron"],             help="which object")
argParser.add_argument("--uncertainty",        action="store",      default="Scale",    type=str, choices=["Scale","Res"],                   help="Scale or Resolution?")
argParser.add_argument("--storeHistos",        action="store_true",                                                                          help="Store 2D maps?")
argParser.add_argument("--year",               action="store",      default=2016,       type=int, choices=[2016,2017,2018],                  help="Which year to plot?")
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

# Sample definition
import TTGammaEFT.Samples.nanoTuples_Ghent_semilep as mc_samples
if args.year == 2016:
    lumi_scale   = 35.92
    sample       = mc_samples.TTG_16
elif args.year == 2017:
    lumi_scale   = 41.53
    sample       = mc_samples.TTG_17
elif args.year == 2018:
    lumi_scale   = 59.74
    sample       = mc_samples.TTG_18


#sample.files = sample.files[:1]


if args.object=="photon":
    binning            = [ 10, 10, 310, 5, 0, 1.4442]
    latexObject        = "#gamma"

elif args.object=="electron":
    binning            = [ 10, 10, 310, 5, 0, 2.4]
    latexObject        = "e"

rangeX              = 0.012 if args.uncertainty == "Scale" else 0.000005

singlePhoton       = "Sum$(_phCutBasedMedium&&_phPtCorr>10&&abs(_phEta)<1.4442&&!_phHasPixelSeed)==1"
singleElectron     = "Sum$(_lFlavor==0&&_lPOGTight&&_lPtCorr>15&&abs(_lEta)<2.4&&(abs(_lEta)<1.4442||abs(_lEta)>1.566))"
singleMuon         = "Sum$(_lFlavor==1&&_lPOGTight&&_relIso0p4<0.15&&_lPtCorr>15&&abs(_lEta)<2.4)"

selectionString    = "(%s+%s)==1&&%s"%(singleElectron,singleMuon,singlePhoton)


def createObjects( event, sample ):

    allPhotons    = [ {"ptCorr":event._phPtCorr[i], "ptResUp":event._phPtResUp[i], "ptResDown":event._phPtResDown[i], "ptScaleUp":event._phPtScaleUp[i], "ptScaleDown":event._phPtScaleDown[i], "pt":event._phPt[i], "phi":event._phPhi[i], "eta":event._phEta[i], "id":event._phCutBasedMedium[i], "pixelSeed":event._phHasPixelSeed[i]} for i in range(event._nPh) ]
    allLeptons    = [ {"ptCorr":event._lPtCorr[i],  "ptResUp":event._lPtResUp[i],  "ptResDown":event._lPtResDown[i],  "ptScaleUp":event._lPtScaleUp[i],  "ptScaleDown":event._lPtScaleDown[i],  "pt":event._lPt[i],  "phi":event._lPhi[i],  "eta":event._lEta[i],  "id":event._lPOGTight[i],        "flavor":event._lFlavor[i], "relIso":event._relIso0p4} for i in range(event._nL) ]

    tightElectrons = filter( lambda l: l['flavor'] == 0 and l['id'] and l['ptCorr']>15 and abs(l['eta']) < 2.4 and (abs(l['eta']) < 1.4442 or abs(l['eta']) > 1.566), allLeptons )
    tightMuons     = filter( lambda l: l['flavor'] == 1 and l['id'] and l['ptCorr']>15 and abs(l['eta']) < 2.4 and l["relIso"]<0.15, allLeptons )
    mediumPhotons  = filter( lambda l: l['id'] and l['ptCorr']>10 and abs(l['eta']) < 1.4442 and not l["pixelSeed"], allPhotons )

    mediumPhotons = deltaRCleaning( mediumPhotons, tightElectrons+tightMuons, dRCut=0.4 )

    event.weight     = 0
    event.weightUp   = 0
    event.weightDown = 0
    event.p_pt       = -999
    event.p_eta      = -999

    if len(tightMuons) + len(tightElectrons) != 1 or len(mediumPhotons) != 1 or (args.object == "electron" and len(tightElectrons) != 1): return

    if   args.object == "photon":   object = mediumPhotons[0]
    elif args.object == "electron": object = tightElectrons[0]

    if object["pt%sUp"%args.uncertainty] < 0 or object["pt%sDown"%args.uncertainty] < 0: return

    event.weight     = 1
    event.weightUp   = object["pt%sUp"%args.uncertainty]   / object["ptCorr"]
    event.weightDown = object["pt%sDown"%args.uncertainty] / object["ptCorr"]
    event.p_pt       = object["ptCorr"]
    event.p_eta      = abs(object["eta"])


# Sequence
sequence = [ createObjects ]

sampleUp   = copy.deepcopy(sample)
sampleDown = copy.deepcopy(sample)

sample.weight     = lambda event, sample: event.weight
sampleUp.weight   = lambda event, sample: event.weightUp
sampleDown.weight = lambda event, sample: event.weightDown

stack = Stack( [sample], [sampleUp], [sampleDown] )
read_variables  = [ "_nPh/i", "_nL/i" ]
read_variables += [ '[phPtCorr/D,phPtScaleUp/D,phPtScaleDown/D,phPtResUp/D,phPtResDown/D,lPtCorr/D,lPtScaleUp/D,lPtScaleDown/D,lPtResUp/D,lPtResDown/D,phCutBasedMedium/O,phPt/D,phPhi/D,phEta/D,phHasPixelSeed/O,lFlavor/i,lPOGTight/O,lPt/D,lEta/D,lPhi/D,relIso0p4/D]' ]

Plot2D.setDefaults( stack=stack, selectionString=selectionString )

plots = []

plots.append( Plot2D(
    name      = '%s_eta_pt'%object,
    texX      = '#p_{T}(%s)'%latexObject,
    texY      = '|#eta(%s)|'%latexObject,
    attribute = (
      lambda event, sample: event.p_pt,
      lambda event, sample: event.p_eta,
    ),
    binning   = binning,
    read_variables = read_variables,
))

plotting.fill( plots, read_variables=read_variables, sequence=sequence )


histXY     = plots[0].histos[0][0]
histUpXY   = plots[0].histos[1][0]
histDownXY = plots[0].histos[2][0]

histX  = histXY.ProjectionX()
histY  = histXY.ProjectionY()

histUpX  = histUpXY.ProjectionX()
histUpY  = histUpXY.ProjectionY()

histDownX  = histDownXY.ProjectionX()
histDownY  = histDownXY.ProjectionY()

histUpX.Divide(histX)
histUpY.Divide(histY)
histUpXY.Divide(histXY)

histDownX.Divide(histX)
histDownY.Divide(histY)
histDownXY.Divide(histXY)

#histUpXY.GetZaxis().SetTitle( "p_{T}(%s up) / p_{T}"%args.uncertainty )
#histDownXY.GetZaxis().SetTitle( "p_{T}(%s down) / p_{T}"%args.uncertainty )

histUpX.legendText = "p_{T}(%s) %s up"%(latexObject, args.uncertainty)
histUpY.legendText = "p_{T}(%s) %s up"%(latexObject, args.uncertainty)
histDownX.legendText = "p_{T}(%s) %s down"%(latexObject, args.uncertainty)
histDownY.legendText = "p_{T}(%s) %s down"%(latexObject, args.uncertainty)

histUpX.style = styles.lineStyle( ROOT.kBlue, width=3 )
histUpY.style = styles.lineStyle( ROOT.kBlue, width=3 )
histDownX.style = styles.lineStyle( ROOT.kRed, width=3 )
histDownY.style = styles.lineStyle( ROOT.kRed, width=3 )

if args.storeHistos:
    tRootFile = ROOT.TFile( "%s_%i_%s.root"%(args.object,args.year,args.uncertainty), "RECREATE" )

    storeHistUp = histUpXY.Clone("Up")
    storeHistUp.SetName("pt_eta_%sUp"%args.uncertainty)
    storeHistUp.SetTitle("pt_eta_%sUp"%args.uncertainty)
    storeHistUp.Write()

    storeHistDown = histDownXY.Clone("Down")
    storeHistDown.SetName("pt_eta_%sDown"%args.uncertainty)
    storeHistDown.SetTitle("pt_eta_%sDown"%args.uncertainty)
    storeHistDown.Write()

    tRootFile.Close()

#    sys.exit(0)

Plot2D.setDefaults()
Plot.setDefaults()

plots = []
plots.append( Plot.fromHisto( "%s_pt"%(args.object),                            [[histX]],     texX = "p_{T}(%s)"%latexObject, texY = "Entries" ) )
plots.append( Plot.fromHisto( "%s_eta"%(args.object),                           [[histY]],     texX = "|#eta(%s)|"%latexObject,  texY = "Entries" ) )
plots.append( Plot.fromHisto( "%s_pt_%s"%(args.object,args.uncertainty),     [[histUpX], [histDownX]],   texX = "p_{T}(%s)"%latexObject, texY = "Projection p_{T}(up/down) / p_{T}" ) )
plots.append( Plot.fromHisto( "%s_eta_%s"%(args.object,args.uncertainty),    [[histUpY], [histDownY]],   texX = "|#eta(%s)|"%latexObject,  texY = "Projection p_{T}(up/down) / p_{T}" ) )

plots2d = []
plots2d.append( Plot2D.fromHisto( "%s_pt_eta_%s_up"%(args.object,args.uncertainty),    [[histUpXY]],   texX = "p_{T}(%s)"%latexObject, texY = "|#eta(%s)|"%(latexObject) ) )
plots2d.append( Plot2D.fromHisto( "%s_pt_eta_%s_down"%(args.object,args.uncertainty),  [[histDownXY]], texX = "p_{T}(%s)"%latexObject, texY = "|#eta(%s)|"%(latexObject) ) )


histModifications  = []
#histModifications += [lambda h: h.GetYaxis().SetTitleSize(20)]
#histModifications += [lambda h: h.GetYaxis().SetLabelSize(20)]
histModifications += [lambda h: h.GetYaxis().SetTitleOffset(1.6)]

#histModifications += [lambda h: h.GetXaxis().SetTitleSize(25)]
#histModifications += [lambda h: h.GetXaxis().SetLabelSize(20)]

#histModifications += [lambda h: h.GetZaxis().SetTitleSize(20)]
#histModifications += [lambda h: h.GetZaxis().SetLabelSize(20)]
#histModifications += [lambda h: h.GetZaxis().SetTitleOffset(1.3)]

canvasModifications  = []
canvasModifications += [lambda c:c.SetLeftMargin(0.18)]


histModifications2D  = []
#histModifications2D += [lambda h: h.GetYaxis().SetTitleSize(20)]
#histModifications2D += [lambda h: h.GetYaxis().SetLabelSize(20)]
#histModifications2D += [lambda h: h.GetYaxis().SetTitleOffset(1.3)]

#histModifications2D += [lambda h: h.GetXaxis().SetTitleSize(25)]
#histModifications2D += [lambda h: h.GetXaxis().SetLabelSize(20)]

#histModifications2D += [lambda h: h.GetZaxis().SetTitleSize(20)]
#histModifications2D += [lambda h: h.GetZaxis().SetLabelSize(15)]
#histModifications2D += [lambda h: h.GetZaxis().SetTitleOffset(1.7)]

canvasModifications2D  = []
canvasModifications2D += [lambda c:c.SetLeftMargin(0.15)]
#canvasModifications2D += [lambda c:c.SetRightMargin(1.4)]

for plot in plots2d:

    for log in [True, False]:

        plot_directory_ = os.path.join( plot_directory, "energyScale2D", str(args.year), args.plot_directory, "log" if log else "lin" )

        plotting.draw2D( plot,
                         plot_directory = plot_directory_,
                         logX = False, logY = False, logZ = log,
                         zRange = (1-rangeX,1+rangeX),
                         drawObjects = drawObjects( lumi_scale ),
                         copyIndexPHP = True,
                         canvasModifications   = canvasModifications2D,
                         histModifications   = histModifications2D,
                       )


for plot in plots:

    for log in [True, False]:

        plot_directory_ = os.path.join( plot_directory, "energyScale2D", str(args.year), args.plot_directory, "log" if log else "lin" )

        plotting.draw( plot,
                         plot_directory = plot_directory_,
                         logX = False, logY = log,
                         yRange = (1-rangeX, 1+rangeX) if args.uncertainty in plot.name else (0.03,"auto"),
                         drawObjects = drawObjects( lumi_scale ),
                         legend = (0.2,0.75,0.65,0.88),
                         copyIndexPHP = True,
                         canvasModifications   = canvasModifications,
                         histModifications   = histModifications,
                       )

