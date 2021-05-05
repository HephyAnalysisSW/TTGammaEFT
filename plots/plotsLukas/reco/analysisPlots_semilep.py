#!/usr/bin/env python
''' Analysis script for standard plots
'''

# Standard imports
import ROOT, os, imp, sys, copy
ROOT.gROOT.SetBatch(True)
import itertools
from math                             import isnan, ceil, pi, sqrt

# RootTools
from RootTools.core.standard          import *

# Internal Imports
from TTGammaEFT.Tools.user            import plot_directory, cache_directory
from TTGammaEFT.Tools.helpers         import splitList
from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter
from TTGammaEFT.Tools.TriggerSelector import TriggerSelector
from TTGammaEFT.Tools.Variables       import NanoVariables
from TTGammaEFT.Tools.objectSelection import isBJet, photonSelector, vidNestedWPBitMapNamingListPhoton, muonSelector, eleSelector, filterGenElectrons, filterGenMuons, filterGenTaus

# Colors
from TTGammaEFT.Samples.color         import color

from Analysis.Tools.MergingDirDB      import MergingDirDB
from Analysis.Tools.metFilters        import getFilterCut
from Analysis.Tools.helpers           import getCollection, deltaR, mTg
from Analysis.Tools.u_float           import u_float
from Analysis.Tools.mt2Calculator     import mt2Calculator
from TTGammaEFT.Tools.overlapRemovalTTG import getParentIds
from Analysis.Tools.runUtils          import prepareTokens, useToken
import Analysis.Tools.syncer as syncer

from TTGammaEFT.Analysis.Setup        import Setup
from TTGammaEFT.Analysis.EstimatorList   import EstimatorList
from TTGammaEFT.Analysis.SetupHelpers import *
from TTGammaEFT.Analysis.regions      import *

# Default Parameter
loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']
photonCatChoices = [ "None", "PhotonGood0", "PhotonGood1", "PhotonMVA0", "PhotonNoChgIso0", "PhotonNoChgIsoNoSieie0", "PhotonNoSieie0" ]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                  help="Log level for logging")
argParser.add_argument('--plot_directory',     action='store',      default='102X_TTG_ppv1_v1')
argParser.add_argument('--plotFile',           action='store',      default='all_noPhoton')
argParser.add_argument('--selection',          action='store',      default='nLepTight1-nLepVeto1-nJet4p-nBTag1p-nPhoton1p')
argParser.add_argument('--small',              action='store_true',                                                                    help='Run only on a small subset of the data?', )
argParser.add_argument('--noData',             action='store_true', default=False,                                                     help='also plot data?')
#argParser.add_argument('--signal',             action='store',      default=None,   nargs='?', choices=[None],                         help="Add signal to plot")
argParser.add_argument('--year',               action='store',      default="2016",   type=str,  choices=["2016","2017","2018","RunII"],               help="Which year to plot?")
argParser.add_argument('--onlyTTG',            action='store_true', default=False,                                                     help="Plot only ttG")
argParser.add_argument('--normalize',          action='store_true', default=False,                                                     help="Normalize yields" )
argParser.add_argument('--addOtherBg',         action='store_true', default=False,                                                     help="add others background" )
argParser.add_argument('--categoryPhoton',     action='store',      default="None", type=str, choices=photonCatChoices,                help="plot in terms of photon category, choose which photon to categorize!" )
argParser.add_argument('--leptonCategory',     action='store_true', default=False,                                                     help="plot in terms of lepton category" )
argParser.add_argument('--invLeptonIso',       action='store_true', default=False,                                                     help="plot QCD estimation plots with inv lepton iso and nBTag==0" )
argParser.add_argument('--replaceZG',          action='store_true', default=False,                                                     help="Plot DY instead of ZGamma" )
argParser.add_argument('--mode',               action='store',      default="None", type=str, choices=["mu", "e", "all", "eetight", "mumutight", "SFtight", "muetight", "muInv", "eInv", "allNoIso", "muNoIso", "eNoIso"], help="plot lepton mode" )
argParser.add_argument('--nJobs',              action='store',      default=1,      type=int, choices=[1,2,3,4,5],                     help="Maximum number of simultaneous jobs.")
argParser.add_argument('--job',                action='store',      default=0,      type=int, choices=[0,1,2,3,4],                     help="Run only job i")
argParser.add_argument('--addBadEEJetVeto',    action='store_true', default=False,                                                     help="remove BadEEJetVeto" )
argParser.add_argument('--noQCDDD',            action='store_true', default=False,                                                     help="no data driven QCD" )
args = argParser.parse_args()

if args.year != "RunII": args.year = int(args.year)

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

ptSels    = ["lowPT", "medPT", "highPT"]
ptLabels  = {"lowPT":"20ptG120", "medPT":"120ptG220", "highPT":"220ptGinf"}
ptRegions = {"lowPT":regionsTTG20To120[0], "medPT":regionsTTG120To220[0], "highPT":regionsTTG220[0]}

categoryPlot = args.categoryPhoton != "None"

# Selection Manipulation
if args.year == 2017 and args.addBadEEJetVeto:
    args.selection += "-BadEEJetVeto"

addMisIDSF = args.invLeptonIso # always true for QCD plots
addDYSF    = args.invLeptonIso #always true for QCD plots
selDir     = args.selection
photonSel  = ("hoton" in args.selection or "pTG" in args.selection) and not "nPhoton0" in args.selection
if args.selection.count("addMisIDSF"):
    addMisIDSF = True
    args.selection = "-".join( [ item for item in args.selection.split("-") if item != "addMisIDSF" ] )
if args.selection.count("addDYSF"):
    addDYSF = True
    args.selection = "-".join( [ item for item in args.selection.split("-") if item != "addDYSF" ] )
regionPlot = False
if len(args.selection.split("-")) == 1 and args.selection in allRegions.keys():
    logger.info( "Plotting region from SetupHelpers: %s"%args.selection )

    regionPlot = True
    setup = Setup( year=args.year, photonSelection=False, checkOnly=True, runOnLxPlus=False ) #photonselection always false for qcd estimate
    setup = setup.sysClone( parameters=allRegions[args.selection]["parameters"] )

    selection      = setup.selection( "MC", channel="all", **setup.defaultParameters() )
    args.selection = selection["prefix"]
    selDir        += "-"+args.selection
    logger.info( "Using selection string: %s"%args.selection )
    photonSel = setup.isPhotonSelection

if args.small:           args.plot_directory += "_small"
if args.noData:          args.plot_directory += "_noData"
#if args.signal:          args.plot_directory += "_signal_"+args.signal
if args.onlyTTG:         args.plot_directory += "_onlyTTG"
if args.normalize:       args.plot_directory += "_normalize"

# Samples
os.environ["gammaSkim"]="True" if photonSel and not args.invLeptonIso and not "NoIso" in args.mode else "False"
if args.year == 2016:
    import TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed as mc_samples
    if not args.noData:
        from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import Run2016 as data_sample

elif args.year == 2017:
    import TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed as mc_samples
    if not args.noData:
        from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import Run2017 as data_sample

elif args.year == 2018:
    import TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed as mc_samples
    if not args.noData:
        from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import Run2018 as data_sample
elif args.year == "RunII":
    import TTGammaEFT.Samples.nanoTuples_RunII_postProcessed as mc_samples
    if not args.noData:
        from TTGammaEFT.Samples.nanoTuples_RunII_postProcessed import RunII as data_sample

cache_dir = os.path.join(cache_directory, "qcdHistos", str(args.year))
dirDB     = MergingDirDB(cache_dir)

# Text on the plots
def drawObjects( plotData, dataMCScale, lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    if plotData and args.invLeptonIso:
        line = (0.42, 0.95, '%3.1f fb^{-1} (13 TeV) TF %3.3f #pm %3.3f'% ( lumi_scale, dataMCScale.val, dataMCScale.sigma ) )
    elif plotData and not args.invLeptonIso:
        line = (0.45, 0.95, '%3.1f fb^{-1} (13 TeV) Scale %3.2f'% ( lumi_scale, dataMCScale ) )
    else:
        line = (0.65, 0.95, '%3.1f fb^{-1} (13 TeV)' % lumi_scale)
    lines = [
      (0.15, 0.95, 'CMS #bf{#it{Preliminary}}' if plotData else 'CMS #bf{#it{Simulation Preliminary}}'), 
      line
    ]
    return [tex.DrawLatex(*l) for l in lines] 

#scaling = { i+1:0 for i in range(len(signals)) }
scaling = { 1:0 }

# Plotting
def drawPlots( plots, mode, dataMCScale ):

    logger.info( "Plotting mode: %s"%mode )

    for log in [False, True]:
        if categoryPlot:
            sc = "cat_"
        elif args.leptonCategory:
            sc = "lep_"
        elif args.invLeptonIso:
            sc = "invIso_"
        elif "NoIso" in args.mode:
            sc = "noIso_"
        elif args.replaceZG:
            sc = "dy_"
        else:
            sc = ""
        sc += "log" if log else "lin"
        plot_directory_ = os.path.join( plot_directory, 'analysisPlots', str(args.year), args.plot_directory, selDir, mode.replace("NoIso",""), sc )

        for plot in plots:
            # get the right labeling on the plots
            if   "20ptG120"  in plot.name: dMCScale = dataMCScale["20ptG120"]
            elif "120ptG220" in plot.name: dMCScale = dataMCScale["120ptG220"]
            elif "220ptGinf" in plot.name: dMCScale = dataMCScale["220ptGinf"]
            else:                          dMCScale = dataMCScale["incl"]

            if not max(l[0].GetMaximum() for l in plot.histos):
                logger.info( "Empty plot!" )
                continue # Empty plot

            if not args.noQCDDD and not args.leptonCategory and not categoryPlot and not args.invLeptonIso and plot.name not in invPlotNames.keys():
                for h in plot.histos[0]:
                    if not "datadrivenQCD" in h.GetName(): continue
                    h.style      = styles.fillStyle( color.QCD )
                    h.legendText = "Multijet"

            postFix = " (%s)"%mode.replace("mu","#mu").replace("all","e+#mu")
            if not args.noData: 
                plot.histos[1][0].style = styles.errorStyle( ROOT.kBlack )
                plot.histos[1][0].legendText = "data" + postFix
            extensions_ = ["pdf", "png", "root"]

            logger.info( "Plotting..." )

            if isinstance( plot, Plot):
                plotting.draw( plot,
	                           plot_directory = plot_directory_,
                               extensions = extensions_,
	                           ratio = {'yRange':(0.1,1.9)} if not args.noData and not "_category" in plot.name else None,
	                           logX = False, logY = log, sorting = not categoryPlot and not args.leptonCategory,
	                           yRange = (0.03, "auto") if log else (0.001, "auto"),
    	                       scaling = scaling if args.normalize else {},
	                           legend = [ (0.15,0.9-0.03*sum(map(len, plot.histos)),0.9,0.9), 2 if args.leptonCategory or categoryPlot else 3],
	                           drawObjects = drawObjects( not args.noData, dMCScale , lumi_scale ) if not args.normalize else drawObjects( not args.noData, 1.0 , lumi_scale ),
                               copyIndexPHP = True,
                             )

            elif isinstance( plot, Plot2D ):
                p_mc = Plot2D.fromHisto( plot.name+'_mc', plot.histos[:1], texX = plot.texX, texY = plot.texY )
                plotting.draw2D( p_mc,
                    plot_directory = plot_directory_,
                    extensions = extensions_,
                    #ratio = {'yRange':(0.1,1.9)},
                    logX = False, logY = False, logZ = log, #sorting = True,
                    zRange = (0.03, "auto") if log else (0.001, "auto"),
                    #scaling = {},
                    #legend = (0.50,0.88-0.04*sum(map(len, plot.histos)),0.9,0.88),
                    drawObjects = drawObjects( not args.noData, dMCScale , lumi_scale ),
                    copyIndexPHP = True,
                )
                p_data = Plot2D.fromHisto( plot.name+'_data', plot.histos[1:], texX = plot.texX, texY = plot.texY )
                plotting.draw2D(p_data,
                    plot_directory = plot_directory_,
                    extensions = extensions_,
                    #ratio = {'yRange':(0.1,1.9)},
                    logX = False, logY = False, logZ = log, #sorting = True,
                    zRange = (0.03, "auto") if log else (0.001, "auto"),
                    #scaling = {},
                    #legend = (0.50,0.88-0.04*sum(map(len, plot.histos)),0.9,0.88),
                    drawObjects = drawObjects( not args.noData, dMCScale , lumi_scale ),
                    copyIndexPHP = True,
                )


def getYieldPlots( index ):
    yieldPlots = []
    yieldPlots.append( Plot(
                name      = 'yield',
                texX      = 'yield',
                texY      = 'Number of Events',
                attribute = lambda event, sample: event.nElectronTight,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )
    yieldPlots.append( Plot(
                name      = 'yield_20ptG120',
                texX      = 'yield',
                texY      = 'Number of Events',
                attribute = lambda event, sample: event.nElectronTight if event.PhotonGood0_pt >= 20 and event.PhotonGood0_pt < 120 else -999,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )
    yieldPlots.append( Plot(
                name      = 'yield_120ptG220',
                texX      = 'yield',
                texY      = 'Number of Events',
                attribute = lambda event, sample: event.nElectronTight if event.PhotonGood0_pt >= 120 and event.PhotonGood0_pt < 220 else -999,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )
    yieldPlots.append( Plot(
                name      = 'yield_220ptGinf',
                texX      = 'yield',
                texY      = 'Number of Events',
                attribute = lambda event, sample: event.nElectronTight if event.PhotonGood0_pt >= 220 else -999,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )

    return yieldPlots



def getInvYieldPlots( index ):
    yieldPlots = []
    yieldPlots.append( Plot(
                name      = 'yield',
                texX      = 'yield',
                texY      = 'Number of Events',
                attribute = lambda event, sample: event.nElectronTightInvIso,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )
    yieldPlots.append( Plot(
                name      = 'yield_20ptG120',
                texX      = 'yield',
                texY      = 'Number of Events',
                attribute = lambda event, sample: event.nElectronTightInvIso if event.PhotonGood0_pt >= 20 and event.PhotonGood0_pt < 120 else -999,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )
    yieldPlots.append( Plot(
                name      = 'yield_120ptG220',
                texX      = 'yield',
                texY      = 'Number of Events',
                attribute = lambda event, sample: event.nElectronTightInvIso if event.PhotonGood0_pt >= 120 and event.PhotonGood0_pt < 220 else -999,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )
    yieldPlots.append( Plot(
                name      = 'yield_220ptGinf',
                texX      = 'yield',
                texY      = 'Number of Events',
                attribute = lambda event, sample: event.nElectronTightInvIso if event.PhotonGood0_pt >= 220 else -999,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                ) )

    return yieldPlots

# get nano variable lists
NanoVars        = NanoVariables( args.year )

jetVarString     = NanoVars.getVariableString(   "Jet",    postprocessed=True, data=(not args.noData), plot=True )
jetVariableNames = NanoVars.getVariableNameList( "Jet",    postprocessed=True, data=(not args.noData), plot=True )
bJetVariables    = NanoVars.getVariables(        "BJet",   postprocessed=True, data=(not args.noData), plot=True )
leptonVarString  = NanoVars.getVariableString(   "Lepton", postprocessed=True, data=(not args.noData), plot=True )
leptonVariables  = NanoVars.getVariables(        "Lepton", postprocessed=True, data=(not args.noData), plot=True )
leptonVarList    = NanoVars.getVariableNameList( "Lepton", postprocessed=True, data=(not args.noData), plot=True )
photonVariables  = NanoVars.getVariables(        "Photon", postprocessed=True, data=(not args.noData), plot=True )
photonVarList    = NanoVars.getVariableNameList( "Photon", postprocessed=True, data=(not args.noData), plot=True )
photonVarString  = NanoVars.getVariableString(   "Photon", postprocessed=True, data=(not args.noData), plot=True )
genVariables     = NanoVars.getVariables(        "Gen",    postprocessed=True, data=False,             plot=True )
genVarString     = NanoVars.getVariableString(   "Gen",    postprocessed=True, data=False,             plot=True )
genVarList       = NanoVars.getVariableNameList( "Gen",    postprocessed=True, data=False,             plot=True )

# Read variables and sequences
read_variables  = ["weight/F",
                   "PV_npvsGood/I",
                   "PV_npvs/I", "PV_npvsGood/I",
                   "nJetGood/I", "nBTagGood/I",
                   "nJetGoodInvLepIso/I", "nBTagGoodInvLepIso/I",
                   "lpTight/F", "lpInvTight/F",
                   "nJet/I", "nBTag/I",
                   "Jet[%s]" %jetVarString,
                   "nLepton/I", "nElectron/I", "nMuon/I",
                   "nLeptonGood/I", "nElectronGood/I", "nMuonGood/I",
                   "nLeptonTight/I", "nElectronTight/I", "nMuonTight/I",
                   "nLeptonTightNoIso/I", "nElectronTightNoIso/I", "nMuonTightNoIso/I",
                   "nLeptonTightInvIso/I", "nElectronTightInvIso/I", "nMuonTightInvIso/I",
                   "nLeptonVetoNoIso/I", "nElectronVetoNoIso/I", "nMuonVetoNoIso/I",
                   "nLeptonVeto/I", "nElectronVeto/I", "nMuonVeto/I",
                   "Photon[%s]" %photonVarString,
                   "nPhoton/I",
                   "nPhotonGood/I",
                   "MET_pt/F", "MET_phi/F", "METSig/F", "ht/F",
                   "mlltight/F", "mllgammatight/F",
                   "mLtight0Gamma/F",
                   "mLinvtight0Gamma/F",
                   "ltight0GammadR/F", "ltight0GammadPhi/F",
                   "linvtight0GammadR/F", "linvtight0GammadPhi/F",
                   "m3/F", "m3wBJet/F",
                   "ht/F", "htinv/F",
                   "m3inv/F", "m3wBJetinv/F",
                   "mT/F", "mT2lg/F", "mTinv/F", "mT2linvg/F",
                   "photonJetdR/F", "tightLeptonJetdR/F",
                   "invtightLeptonJetdR/F",
                   "reweightHEM/F",
                  ]

read_variables += [ "%s_photonCat/I"%item for item in photonCatChoices if item != "None" ]
read_variables += [ "%s_photonCatMagic/I"%item for item in photonCatChoices if item != "None" ]

read_variables += [ VectorTreeVariable.fromString('Lepton[%s]'%leptonVarString, nMax=100) ]
read_variables += [ VectorTreeVariable.fromString('Photon[%s]'%photonVarString, nMax=100) ]
#read_variables += [ VectorTreeVariable.fromString('Jet[%s]'%jetVarString, nMax=10) ]
#read_variables += [ VectorTreeVariable.fromString('JetGood[%s]'%jetVarString, nMax=10) ]

#read_variables += map( lambda var: "PhotonMVA0_"              + var, photonVariables )
read_variables += map( lambda var: "PhotonGood0_"             + var, photonVariables )
read_variables += map( lambda var: "PhotonGoodInvLepIso0_"    + var, photonVariables )
read_variables += map( lambda var: "PhotonNoChgIso0_"         + var, photonVariables )
read_variables += map( lambda var: "PhotonNoSieie0_"          + var, photonVariables )
read_variables += map( lambda var: "PhotonNoChgIsoNoSieie0_"  + var, photonVariables )

read_variables += map( lambda var: "MisIDElectron0_"          + var, leptonVariables )

read_variables += map( lambda var: "LeptonGood0_"             + var, leptonVariables )
read_variables += map( lambda var: "LeptonGood1_"             + var, leptonVariables )
read_variables += map( lambda var: "LeptonTight0_"            + var, leptonVariables )
read_variables += map( lambda var: "LeptonTight1_"            + var, leptonVariables )
read_variables += map( lambda var: "LeptonTightNoIso0_"       + var, leptonVariables )
read_variables += map( lambda var: "Bj0_"                     + var, bJetVariables )
read_variables += map( lambda var: "Bj1_"                     + var, bJetVariables )

read_variables_MC = ["isTTGamma/I", "isZWGamma/I", "isTGamma/I", "overlapRemoval/I",
                     "nGenWElectron/I", "nGenWMuon/I", "nGenWTau/I", "nGenW/I", "nGenWJets/I", "nGenWTauElectron/I", "nGenWTauMuon/I", "nGenWTauJets/I",
                     "nGenElectron/I",
                     "nGenMuon/I",
                     "nGenPhoton/I",
                     "nGenBJet/I",
                     "nGenTop/I",
                     "nGenJet/I",
                     "nGenPart/I",
                     "reweightPU/F", "reweightPUDown/F", "reweightPUUp/F", "reweightPUVDown/F", "reweightPUVUp/F",
                     "reweightLeptonTightSF/F", "reweightLeptonTightSFUp/F", "reweightLeptonTightSFDown/F",
                     "reweightLeptonTrackingTightSF/F",
                     "reweightLeptonTightSFInvIso/F", "reweightLeptonTightSFInvIsoUp/F", "reweightLeptonTightSFInvIsoDown/F",
                     "reweightLeptonTrackingTightSFInvIso/F",
                     "reweightTrigger/F", "reweightTriggerUp/F", "reweightTriggerDown/F",
                     "reweightInvIsoTrigger/F", "reweightInvIsoTriggerUp/F", "reweightInvIsoTriggerDown/F",
                     "reweightPhotonSF/F", "reweightPhotonSFUp/F", "reweightPhotonSFDown/F",
                     "reweightPhotonElectronVetoSF/F",
                     "reweightBTag_SF/F", "reweightBTag_SF_b_Down/F", "reweightBTag_SF_b_Up/F", "reweightBTag_SF_l_Down/F", "reweightBTag_SF_l_Up/F",
                     'reweightL1Prefire/F', 'reweightL1PrefireUp/F', 'reweightL1PrefireDown/F',
                    ]

read_variables_MC += [ VectorTreeVariable.fromString('GenPart[%s]'%genVarString, nMax=1000) ]

#recoPhotonSel_medium_noSieie = photonSelector( 'medium', year=args.year, removedCuts=["sieie"] )
recoPhotonSel_medium         = photonSelector( 'medium', year=args.year )
recoEleSel_veto              = eleSelector( 'veto' )
recoElectronSel_tight        = eleSelector( "tight" )
recoMuonSel_tight            = muonSelector( "tight" )

recoElectronSel_veto        = eleSelector( "veto" )
recoMuonSel_veto            = muonSelector( "veto" )


def calcGenWdecays( event, sample ):
    if sample.name == "data": return

    gPart = getCollection( event, 'GenPart', genVarList, 'nGenPart' )
    # get Ws from top or MG matrix element (from gluon)
    GenW        = filter( lambda l: abs(l['pdgId']) == 24 and l["genPartIdxMother"] >= 0 and l["genPartIdxMother"] < len(gPart), gPart )
    GenW        = filter( lambda l: abs(gPart[l["genPartIdxMother"]]["pdgId"]) in [6,21], GenW )
    # e/mu/tau with W mother
    GenLepWMother    = filter( lambda l: abs(l['pdgId']) in [11,13,15] and l["genPartIdxMother"] >= 0 and l["genPartIdxMother"] < len(gPart), gPart )
    GenLepWMother    = filter( lambda l: abs(gPart[l["genPartIdxMother"]]["pdgId"])==24, GenLepWMother )
    # e/mu with tau mother and tau has a W in parentsList
    GenLepTauMother  = filter( lambda l: abs(l['pdgId']) in [11,13] and l["genPartIdxMother"] >= 0 and l["genPartIdxMother"] < len(gPart), gPart )
    GenLepTauMother  = filter( lambda l: abs(gPart[l["genPartIdxMother"]]["pdgId"])==15 and 24 in map( abs, getParentIds( gPart[l["genPartIdxMother"]], gPart)), GenLepTauMother )

    GenElectron = filter( lambda l: abs(l['pdgId']) == 11, GenLepWMother )
    GenMuon     = filter( lambda l: abs(l['pdgId']) == 13, GenLepWMother )
    GenTau      = filter( lambda l: abs(l['pdgId']) == 15, GenLepWMother )

    GenTauElectron = filter( lambda l: abs(l['pdgId']) == 11, GenLepTauMother )
    GenTauMuon     = filter( lambda l: abs(l['pdgId']) == 13, GenLepTauMother )

    # can't find jets from W in gParts, so assume non-Leptonic W decays are hadronic W decays
    event.nGenWElectron    = len(GenElectron) # W -> e nu
    event.nGenWMuon        = len(GenMuon) # W -> mu nu
    event.nGenWTau         = len(GenTau) # W -> tau nu
    event.nGenW            = len(GenW) # all W from tops
    event.nGenWJets        = len(GenW)-len(GenLepWMother) # W -> q q
    event.nGenWTauElectron = len(GenTauElectron) # W -> tau nu, tau -> e nu nu
    event.nGenWTauMuon     = len(GenTauMuon) # W -> tau nu, tau -> mu nu nu
    event.nGenWTauJets     = len(GenTau)-len(GenLepTauMother) # W -> tau nu, tau -> q q nu

    event.cat_gen2L    = int( (event.nGenWElectron + event.nGenWMuon + event.nGenWTau) == 2 )
    event.cat_genHad   = int( (event.nGenWElectron + event.nGenWMuon + event.nGenWTau) == 0 )
    event.cat_genL     = int( (event.nGenWElectron + event.nGenWMuon) == 1 and not event.cat_gen2L )
    event.cat_genTau_l = int( event.nGenWTau==1 and event.nGenWTauJets==0 and not event.cat_gen2L )
    event.cat_genTau_q = int( event.nGenWTau==1 and event.nGenWTauJets==1 and not event.cat_gen2L )

def getmTg( event, sample ):
    if event.nLeptonTight == 0 or event.nPhotonGood == 0:
        event.mTg = -999
        return
    l   = {"pt":event.LeptonTight0_pt, "phi":event.LeptonTight0_phi}
    p   = {"pt":event.PhotonGood0_pt, "phi":event.PhotonGood0_phi}
    met = {"pt":event.MET_pt, "phi":event.MET_phi}
    event.mTg = mTg(l,p,met)

mt2Calculator = mt2Calculator()
def mt2lg( event, sample ):
    mt2Calculator.reset()
    mt2Calculator.setMet( event.MET_pt, event.MET_phi )
    mt2Calculator.setLepton1( event.LeptonTight0_pt, event.LeptonTight0_eta, event.LeptonTight0_phi )
    mt2Calculator.setLepton2( event.PhotonGood0_pt, event.PhotonGood0_eta, event.PhotonGood0_phi )
    event.mT2lg = mt2Calculator.mt2ll()

def calcVetoElectrons( event, sample ):
    allPhotons = getCollection( event, 'Photon', photonVarList, 'nPhoton' )
    allPhotons.sort( key = lambda j: -j['pt'] )
    goodPhotons = filter( lambda g: recoPhotonSel_medium(g), allPhotons )

    allLeptons = getCollection( event, 'Lepton', leptonVarList, 'nLepton' )
    allLeptons.sort( key = lambda j: -j['pt'] )
    allElectrons = filter( lambda l: abs(l["pdgId"])==11, allLeptons )
#    vetoElectrons = filter( lambda l: recoEleSel_veto(l), allElectrons )
    vetoNoIsoElectrons = filter( lambda l: recoEleSel_veto(l,removedCuts=["pfRelIso03_all"]), allElectrons )

    if event.nElectronVeto != len(vetoNoIsoElectrons):
        for ele in vetoNoIsoElectrons:
#          for g in goodPhotons:
          for g in allPhotons:
            if ele["index"]==g["electronIdx"]:
                ele["pfRelIso03_all"] = min( ele["pfRelIso03_all"], g["pfRelIso03_all"] )
        vetoNewElectrons = filter( lambda l: (l["pfRelIso03_all"]<0.198+0.506/l["pt"] and l["eta"]+l["deltaEtaSC"]<=1.479) or (l["pfRelIso03_all"]<0.203+0.963/l["pt"] and l["eta"]+l["deltaEtaSC"]>1.479), vetoNoIsoElectrons )
        event.weight *= int( len(vetoNewElectrons)+event.nMuonVeto==1 )

def calcNoIsoLeptons( event, sample ):

    allLeptons = getCollection( event, 'Lepton', leptonVarList, 'nLepton' )
    allLeptons.sort( key = lambda j: -j['pt'] )
    allElectrons = filter( lambda l: abs(l["pdgId"])==11, allLeptons )
    allMuons     = filter( lambda l: abs(l["pdgId"])==13, allLeptons )

    tightNoIsoElectrons = list( filter( lambda l: recoElectronSel_tight(l, removedCuts=["pfRelIso03_all"]), allElectrons ) )
    tightNoIsoMuons     = list( filter( lambda l: recoMuonSel_tight(l,     removedCuts=["pfRelIso04_all"]), allMuons ) )
    tightNoIsoLeptons   = tightNoIsoElectrons + tightNoIsoMuons
    tightNoIsoLeptons.sort( key = lambda l: -l['pt'] )

    tightNoIsoLepton = ( tightNoIsoLeptons + [None] )[0]

    vetoNoIsoElectrons = list( filter( lambda l: recoElectronSel_veto(l, removedCuts=["pfRelIso03_all"]), allElectrons ) )
    vetoNoIsoMuons     = list( filter( lambda l: recoMuonSel_veto(l,     removedCuts=["pfRelIso04_all"]), allMuons ) )
    vetoNoIsoLeptons   = vetoNoIsoElectrons + vetoNoIsoMuons
    vetoNoIsoLeptons.sort( key = lambda l: -l['pt'] )

    if "NoIso" in args.mode:
        event.weight *= int( len(vetoNoIsoLeptons)==1 )

    for var in leptonVarList:
        if tightNoIsoLepton:
            setattr( event, "LeptonTightNoIso0_" + var, tightNoIsoLepton[var] )
        else:
            try:
                setattr( event, "LeptonTightNoIso0_" + var, -999 )
            except:
                setattr( event, "LeptonTightNoIso0_" + var, 0 )

def vetoNoIsoLeptons( event, sample ):

    allLeptons = getCollection( event, 'Lepton', leptonVarList, 'nLepton' )
    allLeptons.sort( key = lambda j: -j['pt'] )
    allElectrons = filter( lambda l: abs(l["pdgId"])==11, allLeptons )
    allMuons     = filter( lambda l: abs(l["pdgId"])==13, allLeptons )

    vetoNoIsoElectrons = list( filter( lambda l: recoElectronSel_veto(l, removedCuts=["pfRelIso03_all"]), allElectrons ) )
    vetoNoIsoMuons     = list( filter( lambda l: recoMuonSel_veto(l,     removedCuts=["pfRelIso04_all"]), allMuons ) )
    vetoNoIsoLeptons   = vetoNoIsoElectrons + vetoNoIsoMuons
    vetoNoIsoLeptons.sort( key = lambda l: -l['pt'] )

    if "NoIso" in args.mode:
        event.weight *= int( len(vetoNoIsoLeptons)==1 )

def printGen( event, sample ):
    if sample.name != "data":
        print sample.name, "e", event.nGenWElectron, "mu", event.nGenWMuon, "tau", event.nGenWTau, "W", event.nGenW


def printmisIDelectrons( event, sample ):
    allPhotons = getCollection( event, 'Photon', photonVarList, 'nPhoton' )
    allLeptons = getCollection( event, 'Lepton', leptonVarList, 'nLepton' )
    allLeptons = filter( lambda l: abs(l["pdgId"])==11, allLeptons )


    for photon in allPhotons:
        leptons = filter( lambda l: l["index"]==photon["electronIdx"], allLeptons )
        leptons.sort( key = lambda j: -j['pt'] )
        misID = leptons[:1]
        if misID:
            if sample.name == "data":
                    print "run", event.run, "lumi", event.luminosityBlock, "event", event.event
            print "electron", misID[0]
            print "photon", photon
            print


def misIDelectrons( event, sample ):
#    photonGood = getCollection( event, 'P', leptonVarList, 'nLepton' )
    allLeptons = getCollection( event, 'Lepton', leptonVarList, 'nLepton' )
    allLeptons.sort( key = lambda j: -j['pt'] )
    misID = filter( lambda l: l["index"]==event.PhotonGood0_electronIdx and abs(l["pdgId"])==11, allLeptons )[:1]
    if misID and recoEleSel_veto(misID[0],removedCuts=["pfRelIso03_all"]):
        misID[0]["pfRelIso03_all"] = min( misID[0]["pfRelIso03_all"], event.PhotonGood0_pfRelIso03_all )

    for var in leptonVarList:
        if misID:
            setattr( event, "misIDElectron0_" + var, misID[0][var] )
        else:
            try:
                setattr( event, "misIDElectron0_" + var, -999 )
            except:
                setattr( event, "misIDElectron0_" + var, 0 )

def allmisIDelectrons( event, sample ):
#    photonGood = getCollection( event, 'P', leptonVarList, 'nLepton' )
    allLeptons = getCollection( event, 'Lepton', leptonVarList, 'nLepton' )
    allLeptons.sort( key = lambda j: -j['pt'] )
    allElectrons = filter( lambda l: abs(l["pdgId"])==11, allLeptons )
    allPhotons = getCollection( event, 'Photon', photonVarList, 'nPhoton' )
    allElectrons = filter( lambda l: abs(l["pdgId"])==11, allLeptons )
    allPhotons.sort( key = lambda j: -j['pt'] )
#    misID = filter( lambda l: l["index"]==event.PhotonGood0_electronIdx and abs(l["pdgId"])==11, allLeptons )[:1]

    misID = []
    for ele in allElectrons:
        for g in allPhotons:
            if ele["index"]==g["electronIdx"]:
                misID.append(ele)
                break
    misID.sort( key = lambda j: -j['pt'] )

    if misID and recoEleSel_veto(misID[0],removedCuts=["pfRelIso03_all"]):
        misID[0]["pfRelIso03_all"] = min( misID[0]["pfRelIso03_all"], event.PhotonGood0_pfRelIso03_all )

    for var in leptonVarList:
        if misID:
            setattr( event, "allmisIDElectron0_" + var, misID[0][var] )
        else:
            try:
                setattr( event, "allmisIDElectron0_" + var, -999 )
            except:
                setattr( event, "allmisIDElectron0_" + var, 0 )

def printEventList( event, sample ):
    if sample.name == "data":
        print str(event.run) + ":" + str(event.luminosityBlock) + ":" + str(event.event)

def makePhotons( event, sample ):
    allPhotons = getCollection( event, 'Photon', photonVarList, 'nPhoton' )
    allPhotons.sort( key = lambda j: -j['pt'] )
    mediumPhotonsNoSieie = list( filter( lambda g: recoPhotonSel_medium(g, removedCuts=["sieie"]), allPhotons ) + [None])[0]

    for var in photonVarList:
        if mediumPhotonsNoSieie:
            setattr( event, "PhotonNoSieie0_" + var, mediumPhotonsNoSieie[var] )
        else:
            try:
                setattr( event, "PhotonNoSieie0_" + var, float("nan") )
            except:
                setattr( event, "PhotonNoSieie0_" + var, 0 )

def mvaPhotons( event, sample ):
    allPhotons = getCollection( event, 'Photon', photonVarList, 'nPhoton' )
    allPhotons.sort( key = lambda j: -j['pt'] )
    mvaPhotons = list( filter( lambda g: recoPhotonSel_mva(g) and g["mvaID_WP90"], allPhotons ) + [None])[0]

    if mvaPhotons:
        for var in photonVarList:
            setattr( event, "PhotonMVA0_" + var, mvaPhotons[var] )

def clean_Jets( event, sample ):
    allJets    = getCollection( event, 'Jet', jetVariableNames, 'nJet' )
    allJets.sort( key = lambda j: -j['pt'] )
    allJets    = list( filter( lambda j: j['cleanmask'] and j['pt']>30, allJets ) )

    looseJets  = getCollection( event, 'JetGood', jetVariableNames, 'nJetGood' )
    looseJets.sort( key = lambda j: -j['pt'] )
    looseJets  = list( filter( lambda j: j['cleanmask'], looseJets ) )

    event.nJet      = len( allJets )
    event.nJetGood  = len( looseJets )
    event.nBTag     = len( filter( lambda j: isBJet( j, tagger='DeepCSV', year=args.year ), allJets ) )
    event.nBTagGood = len( filter( lambda j: isBJet( j, tagger='DeepCSV', year=args.year ), looseJets ) )

    for var in jetVariableNames:
        for i, jet in enumerate( allJets[:2] ):
            getattr( event, "Jet_" + var )[i] = jet[var]
        for i, jet in enumerate ( looseJets[:2] ):
            getattr( event, "JetGood_" + var )[i] = jet[var]
# Sequence
def printWeight( event, sample ):
    print event.weight

#sequence = [calcGenWdecays]# printWeight ]#clean_Jets ]
#sequence = [calcGenWdecays, calcVetoElectrons, misIDelectrons, allmisIDelectrons, mt2lg ]# printWeight ]#clean_Jets ]
#sequence = [misIDelectrons]# printWeight ]#clean_Jets ]
#sequence += [calcNoIsoLeptons]
sequence = []

# Sample definition
if args.onlyTTG and not categoryPlot and not args.leptonCategory:
    mc = [ mc_samples.TTG, mc_samples.QCD ]
elif categoryPlot:
    all = mc_samples.all_noQCD #all_mc if args.addOtherBg else all_noOther
elif args.leptonCategory:
    all_noTT = mc_samples.all_noTT# if args.addOtherBg else all_noOther_noTT
    TTbar    = mc_samples.Top
    TTG      = mc_samples.TTG
else:
    if args.replaceZG:
        mc = [ mc_samples.TTG, mc_samples.Top, mc_samples.DY_LO, mc_samples.WJets, mc_samples.WG_NLO, mc_samples.rest ]
    else:
        mc = [ mc_samples.TTG, mc_samples.Top, mc_samples.DY_LO, mc_samples.WJets, mc_samples.WG_NLO, mc_samples.ZG, mc_samples.rest ]
    if not (args.invLeptonIso):
        mc += [ mc_samples.QCD ]
        if args.noQCDDD or "NoIso" in args.mode: mc += [ mc_samples.GJets ]
    mc += [ mc_samples.QCD, mc_samples.GJets ]

if categoryPlot:
    all_cat0 = all
    all_cat0.name = "cat0"
    all_cat0.texName = "Genuine Photons"
    all_cat0.color   = ROOT.kOrange

    all_cat1 = copy.deepcopy(all)
    all_cat1.name    = "cat1"
    all_cat1.texName = "Hadronic Photons"
    all_cat1.color   = ROOT.kBlue+2

    all_cat2 = copy.deepcopy(all)
    all_cat2.name    = "cat2"
    all_cat2.texName = "MisId Electrons"
    all_cat2.color   = ROOT.kCyan+2
    
    all_cat3 = copy.deepcopy(all)
    all_cat3.name    = "cat3"
    all_cat3.texName = "Hadronic Fakes"
    all_cat3.color   = ROOT.kRed+1
    mc  = [ all_cat0, all_cat1, all_cat2, all_cat3 ]

elif args.leptonCategory:

    tt_2l         = TTbar
    tt_2l.name    = "ttll"
    tt_2l.texName = "tt (2l)"
    tt_2l.color   = ROOT.kAzure+6

    tt_tau_q         = copy.deepcopy(TTbar)
    tt_tau_q.name    = "tttauq"
    tt_tau_q.texName = "tt (#tau to had)"
    tt_tau_q.color   = ROOT.kAzure-1

    tt_tau_l         = copy.deepcopy(TTbar)
    tt_tau_l.name    = "tttaul"
    tt_tau_l.texName = "tt (#tau to e/#mu)"
    tt_tau_l.color   = ROOT.kAzure+2

    tt_l         = copy.deepcopy(TTbar)
    tt_l.name    = "ttl"
    tt_l.texName = "tt (e/#mu)"
    tt_l.color   = ROOT.kAzure+1

    tt_had         = copy.deepcopy(TTbar)
    tt_had.name    = "tthad"
    tt_had.texName = "tt (had)"
    tt_had.color   = ROOT.kAzure+3

    ttg_2l         = TTG
    ttg_2l.name    = "ttgll"
    ttg_2l.texName = "tt#gamma (2l)"
    ttg_2l.color   = ROOT.kOrange

    ttg_tau_q         = copy.deepcopy(TTG)
    ttg_tau_q.name    = "ttgtauq"
    ttg_tau_q.texName = "tt#gamma (#tau to had)"
    ttg_tau_q.color   = ROOT.kOrange+2

    ttg_tau_l         = copy.deepcopy(TTG)
    ttg_tau_l.name    = "ttgtaul"
    ttg_tau_l.texName = "tt#gamma (#tau to e/#mu)"
    ttg_tau_l.color   = ROOT.kOrange+7

    ttg_l         = copy.deepcopy(TTG)
    ttg_l.name    = "ttgl"
    ttg_l.texName = "tt#gamma (e/#mu)"
    ttg_l.color   = ROOT.kOrange+1

    ttg_had         = copy.deepcopy(TTG)
    ttg_had.name    = "ttghad"
    ttg_had.texName = "tt#gamma (had)"
    ttg_had.color   = ROOT.kOrange+4

    all_noTT.name    = "other"
    all_noTT.texName = "other"
    all_noTT.color   = ROOT.kGray
    mc  = [ ttg_2l, tt_2l, ttg_l, tt_l, ttg_tau_l, tt_tau_l, ttg_tau_q, tt_tau_q, ttg_had, tt_had, all_noTT ]


if args.noData:
    if args.year == 2016:   lumi_scale = 35.92
    elif args.year == 2017: lumi_scale = 41.53
    elif args.year == 2018: lumi_scale = 59.74
    elif args.year == "RunII": lumi_scale = 35.92 + 41.53 + 59.74
    stack = Stack( mc )
else:
    data_sample.texName        = "data" # (legacy)"
    data_sample.name           = "data"
    data_sample.read_variables = [ "event/I", "run/I", "luminosityBlock/I" ]
    data_sample.scale          = 1
    lumi_scale                 = data_sample.lumi * 0.001
    stack                      = Stack( mc, data_sample )

#stack.extend( [ [s] for s in signals ] )

# huge fix needed!
if addMisIDSF and addDYSF and not args.invLeptonIso:
    sampleWeight = lambda event, sample: (misIDSF_val[args.year].val if event.nPhotonGood>0 and event.PhotonGood0_photonCatMagic==2 else 1.)*(DYSF_val[args.year].val if "DY" in sample.name else 1.)*event.reweightL1Prefire*event.reweightHEM*event.reweightPU*event.reweightTrigger*event.reweightLeptonTightSF*event.reweightLeptonTrackingTightSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF
elif addDYSF and not args.invLeptonIso:
    sampleWeight = lambda event, sample: (DYSF_val[args.year].val if "DY" in sample.name else 1.)*event.reweightL1Prefire*event.reweightHEM*event.reweightPU*event.reweightTrigger*event.reweightLeptonTightSF*event.reweightLeptonTrackingTightSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF
elif addMisIDSF and not args.invLeptonIso:
    sampleWeight = lambda event, sample: (misIDSF_val[args.year].val if event.nPhotonGood>0 and event.PhotonGood0_photonCatMagic==2 else 1.)*event.reweightL1Prefire*event.reweightPU*event.reweightTrigger*event.reweightLeptonTightSF*event.reweightLeptonTrackingTightSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF
elif addMisIDSF and addDYSF and args.invLeptonIso:
    sampleWeight = lambda event, sample: (misIDSF_val[args.year].val if event.nPhotonGoodInvLepIso>0 and event.PhotonGoodInvLepIso0_photonCatMagic==2 else 1.)*(DYSF_val[args.year].val if "DY" in sample.name else 1.)*event.reweightL1Prefire*event.reweightHEM*event.reweightPU*event.reweightTrigger*event.reweightLeptonTightSF*event.reweightLeptonTrackingTightSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF
elif addDYSF and args.invLeptonIso:
    sampleWeight = lambda event, sample: (DYSF_val[args.year].val if "DY" in sample.name else 1.)*event.reweightL1Prefire*event.reweightHEM*event.reweightPU*event.reweightInvIsoTrigger*event.reweightLeptonTightSFInvIso*event.reweightLeptonTrackingTightSFInvIso*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF
elif addMisIDSF and args.invLeptonIso:
    sampleWeight = lambda event, sample: (misIDSF_val[args.year].val if event.nPhotonGoodInvLepIso>0 and event.PhotonGoodInvLepIso0_photonCatMagic==2 else 1.)*event.reweightL1Prefire*event.reweightHEM*event.reweightPU*event.reweightInvIsoTrigger*event.reweightLeptonTightSFInvIso*event.reweightLeptonTrackingTightSFInvIso*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF
elif args.invLeptonIso:
    sampleWeight = lambda event, sample: event.reweightL1Prefire*event.reweightHEM*event.reweightPU*event.reweightInvIsoTrigger*event.reweightLeptonTightSFInvIso*event.reweightLeptonTrackingTightSFInvIso*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF
else:
    sampleWeight = lambda event, sample: event.reweightL1Prefire*event.reweightPU*event.reweightHEM*event.reweightTrigger*event.reweightLeptonTightSF*event.reweightLeptonTrackingTightSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF

lumiString = "(35.92*(year==2016)+41.53*(year==2017)+59.74*(year==2018))"
ws   = "(%s*weight*reweightHEM*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF)"%lumiString
ws16 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2016))" %(ws, misIDSF_val[2016].val)
ws17 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2017))" %(ws, misIDSF_val[2017].val)
ws18 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2018))" %(ws, misIDSF_val[2018].val)
weightString = ws + ws16 + ws17 + ws18

for sample in mc:# + signals:
    sample.read_variables = read_variables_MC
    sample.scale          = lumi_scale
    if "qcd" in sample.name.lower() and photonSel and not args.noQCDDD: sample.scale = 0.
    sample.style          = styles.fillStyle( sample.color )
    sample.weight         = sampleWeight
#event.reweightDilepTriggerBackup

if args.small:
    for sample in stack.samples:
        sample.normalization=1.
        sample.reduceFiles( factor=20 )
        sample.scale /= sample.normalization

weight_ = lambda event, sample: event.weight*event.reweightHEM

replaceSelection = {
    "nLeptonVetoIsoCorr": "nLeptonVetoNoIso",
    "nLeptonTight":       "nLeptonTightInvIso",
    "nMuonTight":         "nMuonTightInvIso",
    "nElectronTight":     "nElectronTightInvIso",
    "mLtight0Gamma":      "mLinvtight0Gamma",
    "nPhotonGood":        "nPhotonGoodInvLepIso",
    "nJetGood":           "nJetGoodInvLepIso",
    "nBTagGood":          "nBTagGoodInvLepIso",
    "LeptonTight0_eta":   "LeptonTightInvIso0_eta",
    "LeptonTight0_pt":    "LeptonTightInvIso0_pt",
}

replaceNoIsoSelection = {
    "nLeptonVetoIsoCorr": "nLeptonVetoNoIso",
    "nLeptonTight":       "nLeptonTightNoIso",
    "nMuonTight":         "nMuonTightNoIso",
    "nElectronTight":     "nElectronTightNoIso",
    "nPhotonGood":        "nPhotonGoodNoLepIso",
    "nJetGood":           "nJetGoodNoLepIso",
    "nBTagGood":          "nBTagGoodNoLepIso",
    "LeptonTight0_eta":   "LeptonTightNoIso0_eta",
    "LeptonTight0_pt":    "LeptonTightNoIso0_pt",
}

if args.invLeptonIso and regionPlot:
    selection_CR = setup.selection("DataMC",   channel="all", **setup.defaultParameters( update=QCD_updates ))
    preSelection = selection_CR["cut"]

elif args.invLeptonIso:
    preSelection = cutInterpreter.cutString( "-".join([ item if not "nBTag" in item else "nBTag0" for item in args.selection.split("-") ]) )
    for key, val in replaceSelection.items():
        preSelection = preSelection.replace( key, val )
elif "NoIso" in args.mode:
    preSelection = cutInterpreter.cutString( args.selection )
#    preSelection = "&&".join( [ item for item in preSelection.split("&&") if not "nLeptonVeto" in item ] )
    for key, val in replaceNoIsoSelection.items():
        preSelection = preSelection.replace( key, val )
else:
    preSelection = cutInterpreter.cutString( args.selection )

print preSelection

Plot2D.setDefaults( stack=stack, weight=staticmethod( weight_ ), selectionString=preSelection )
Plot.setDefaults(   stack=stack, weight=staticmethod( weight_ ), selectionString=preSelection, addOverFlowBin=None if args.invLeptonIso else "upper" )

# Import plots list (AFTER setDefaults!!)
plotListFile = os.path.join( os.path.dirname( os.path.realpath( __file__ ) ), 'plotLists', args.plotFile + '.py' )
if not os.path.isfile( plotListFile ):
    logger.info( "Plot file not found: %s", plotListFile )
    sys.exit(1)

plotModule = imp.load_source( "plotLists", os.path.expandvars( plotListFile ) )
if args.noData: from plotLists import plotListDataMC as plotList
else:           from plotLists import plotListData   as plotList

# plotList
add2DPlots = []

add2DPlots.append( Plot2D(
    name      = 'photonGood0_eta_phi',
    texX      = '#eta(#gamma_{0})',
    texY      = '#phi(#gamma_{0})',
    attribute = (
      TreeVariable.fromString( "PhotonGood0_eta/F" ),
      TreeVariable.fromString( "PhotonGood0_phi/F" ),
    ),
    binning   = [10, -1.5, 1.5, 20, -pi, pi],
    read_variables = read_variables,
))

add2DPlots.append( Plot2D(
    name      = 'misIDElectron0_eta_phi',
    texX      = '#eta(#gamma_{0})',
    texY      = '#phi(#gamma_{0})',
    attribute = (
      lambda event, sample: event.MisIDElectron0_eta,
      lambda event, sample: event.MisIDElectron0_phi,
    ),
    binning   = [10, -1.5, 1.5, 20, -pi, pi],
    read_variables = read_variables,
))

add2DPlots.append( Plot2D(
    name      = 'misIDElectron0_eta_phi_misIDlostHits3',
    texX      = '#eta(#gamma_{0})',
    texY      = '#phi(#gamma_{0})',
    attribute = (
      lambda event, sample: event.MisIDElectron0_eta if event.MisIDElectron0_lostHits==3 else -999,
      lambda event, sample: event.MisIDElectron0_phi if event.MisIDElectron0_lostHits==3 else -999,
    ),
    binning   = [10, -1.5, 1.5, 20, -pi, pi],
    read_variables = read_variables,
))

add2DPlots.append( Plot2D(
    name      = 'photonGood0_eta_phi_misIDlostHits3',
    texX      = '#eta(#gamma_{0})',
    texY      = '#phi(#gamma_{0})',
    attribute = (
      lambda event, sample: event.PhotonGood0_eta if event.MisIDElectron0_lostHits==3 else -999,
      lambda event, sample: event.PhotonGood0_phi if event.MisIDElectron0_lostHits==3 else -999,
    ),
    binning   = [10, -1.5, 1.5, 20, -pi, pi],
    read_variables = read_variables,
))

add2DPlots.append( Plot2D(
    name      = 'misIDElectron0_eta_phi_misIDlostHitsleq2',
    texX      = '#eta(#gamma_{0})',
    texY      = '#phi(#gamma_{0})',
    attribute = (
      lambda event, sample: event.MisIDElectron0_eta if event.MisIDElectron0_lostHits<=2 else -999,
      lambda event, sample: event.MisIDElectron0_phi if event.MisIDElectron0_lostHits<=2 else -999,
    ),
    binning   = [10, -1.5, 1.5, 20, -pi, pi],
    read_variables = read_variables,
))

add2DPlots.append( Plot2D(
    name      = 'photonGood0_eta_phi_misIDlostHitsleq2',
    texX      = '#eta(#gamma_{0})',
    texY      = '#phi(#gamma_{0})',
    attribute = (
      lambda event, sample: event.PhotonGood0_eta if event.MisIDElectron0_lostHits<=2 else -999,
      lambda event, sample: event.PhotonGood0_phi if event.MisIDElectron0_lostHits<=2 else -999,
    ),
    binning   = [10, -1.5, 1.5, 20, -pi, pi],
    read_variables = read_variables,
))

# plotList
noIsoPlots = []

noIsoPlots.append( Plot(
    name      = "LeptonTightNoIso0_dxy",
    texX      = "dxy (l_{noIso})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTightNoIso0_dxy/F" ),
    binning   = [ 20, 0, 0.15 ],
))

noIsoPlots.append( Plot(
    name      = "LeptonTightNoIso0_dz",
    texX      = "dz (l_{noIso})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTightNoIso0_dz/F" ),
    binning   = [ 20, 0, 0.3 ],
))

noIsoPlots.append( Plot(
    name      = "LeptonTightNoIso0_ip3d",
    texX      = "ip3d (l_{noIso})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTightNoIso0_ip3d/F" ),
    binning   = [ 20, 0, 0.1 ],
))

noIsoPlots.append( Plot(
    name      = "LeptonTightNoIso0_r9",
    texX      = "R9 (l_{noIso})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTightNoIso0_r9/F" ),
    binning   = [ 20, 0, 1 ],
))

noIsoPlots.append( Plot(
    name      = "LeptonTightNoIso0_sip3d",
    texX      = "SIP3D(l_{noIso})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTightNoIso0_sip3d/F" ),
    binning   = [ 20, 0, 6 ],
))

noIsoPlots.append( Plot(
    name      = "LeptonTightNoIso0_lostHits",
    texX      = "lost hits (l_{noIso})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTightNoIso0_lostHits/I" ),
    binning   = [ 4, 0, 4 ],
))

noIsoPlots.append( Plot(
    name      = "LeptonTightNoIso0_dr03EcalRecHitSumEt",
    texX      = "dr03EcalRecHitSumEt (l_{noIso})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTightNoIso0_dr03EcalRecHitSumEt/F" ),
    binning   = [ 20, 0, 3 ],
))

noIsoPlots.append( Plot(
    name      = "LeptonTightNoIso0_dr03HcalDepth1TowerSumEt",
    texX      = "dr03HcalDepth1TowerSumEt (l_{noIso})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTightNoIso0_dr03HcalDepth1TowerSumEt/F" ),
    binning   = [ 20, 0, 3 ],
))

noIsoPlots.append( Plot(
    name      = "LeptonTightNoIso0_dr03TkSumPt",
    texX      = "dr03TkSumPt (l_{noIso})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTightNoIso0_dr03TkSumPt/F" ),
    binning   = [ 20, 0, 2.5 ],
))

noIsoPlots.append( Plot(
    name      = 'LeptonTightNoIso0_pt',
    texX      = 'p_{T}(l_{noIso}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.LeptonTightNoIso0_pt,
    binning   = [ 20, 0, 120 ],
))

noIsoPlots.append( Plot(
    name      = 'LeptonTightNoIso0_eta',
    texX      = '#eta(l_{noIso})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.LeptonTightNoIso0_eta,
    binning   = [ 30, -3, 3 ],
))

noIsoPlots.append( Plot(
    name      = 'LeptonTightNoIso0_phi',
    texX      = '#phi(l_{noIso})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.LeptonTightNoIso0_phi,
    binning   = [ 10, -pi, pi ],
))

noIsoPlots.append( Plot(
    name      = 'LeptonTightNoIso0_pfRelIso03_chg',
    texX      = 'charged relIso_{0.3}(l_{noIso})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.LeptonTightNoIso0_pfRelIso03_chg,
    binning   = [ 20, 0, 0.4 ],
))

noIsoPlots.append( Plot(
    name      = 'LeptonTightNoIso0_pfRelIso03_all',
    texX      = 'relIso_{0.3}(l_{noIso})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.LeptonTightNoIso0_pfRelIso03_all,
    binning   = [ 20, 0, 1.4 ],
))

noIsoPlots.append( Plot(
    name      = 'LeptonTightNoIso0_pfRelIso03_n',
    texX      = 'neutral relIso_{0.3}(l_{noIso})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.LeptonTightNoIso0_pfRelIso03_all - event.LeptonTightNoIso0_pfRelIso03_chg,
    binning   = [ 20, 0, 1.4 ],
))

noIsoPlots.append( Plot(
    name      = 'LeptonTightNoIso0_pfIso03_chg',
    texX      = 'charged Iso_{0.3}(l_{noIso})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.LeptonTightNoIso0_pfRelIso03_chg * event.LeptonTightNoIso0_pt,
    binning   = [ 20, 0, 20 ],
))

noIsoPlots.append( Plot(
    name      = 'LeptonTightNoIso0_pfIso03_all',
    texX      = 'Iso_{0.3}(l_{noIso})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.LeptonTightNoIso0_pfRelIso03_all * event.LeptonTightNoIso0_pt,
    binning   = [ 20, 0, 20 ],
))

noIsoPlots.append( Plot(
    name      = 'LeptonTightNoIso0_pfIso03_n',
    texX      = 'neutral Iso_{0.3}(l_{noIso})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: (event.LeptonTightNoIso0_pfRelIso03_all - event.LeptonTightNoIso0_pfRelIso03_chg) * event.LeptonTightNoIso0_pt,
    binning   = [ 20, 0, 20 ],
))

noIsoPlots.append( Plot(
    name      = 'LeptonTightNoIso0_pfRelIso04_all',
    texX      = 'relIso_{0.4}(l_{noIso})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.LeptonTightNoIso0_pfRelIso04_all,
    binning   = [ 20, 0, 1.4 ],
))

noIsoPlots.append( Plot(
    name      = 'LeptonTightNoIso0_pfIso04_all',
    texX      = 'Iso_{0.4}(l_{noIso})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.LeptonTightNoIso0_pfRelIso04_all * event.LeptonTightNoIso0_pt,
    binning   = [ 20, 0, 20 ],
))


# plotList
addPlots = []

addPlots.append( Plot(
    name      = 'misIDElectron0_pt',
    texX      = 'p_{T}(e_{misID}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.MisIDElectron0_pt,
    binning   = [ 20, 0, 120 ],
))

addPlots.append( Plot(
    name      = 'misIDElectron0_eta',
    texX      = '#eta(e_{misID})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.MisIDElectron0_eta,
    binning   = [ 30, -3, 3 ],
))

addPlots.append( Plot(
    name      = 'misIDElectron0_phi',
    texX      = '#phi(e_{misID})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.MisIDElectron0_phi,
    binning   = [ 10, -pi, pi ],
))

addPlots.append( Plot(
    name      = 'misIDElectron0_lostHits',
    texX      = 'lost hits(e_{misID})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.MisIDElectron0_lostHits,
    binning   = [ 4, 0, 4 ],
))

addPlots.append( Plot(
    name      = 'misIDElectron0_dr03EcalRecHitSumEt',
    texX      = '#DeltaR_{0.3} EcalRecHitSumEt (e_{misID})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.MisIDElectron0_dr03EcalRecHitSumEt,
    binning   = [ 20, 0, 4 ],
))

addPlots.append( Plot(
    name      = 'misIDElectron0_dr03HcalDepth1TowerSumEt',
    texX      = '#DeltaR_{0.3} HcalDepth1TowerSumEt (e_{misID})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.MisIDElectron0_dr03HcalDepth1TowerSumEt,
    binning   = [ 20, 0, 4 ],
))

addPlots.append( Plot(
    name      = 'misIDElectron0_dr03TkSumPt',
    texX      = '#DeltaR_{0.3} TkSumPt (e_{misID})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.MisIDElectron0_dr03TkSumPt,
    binning   = [ 20, 0, 4 ],
))

addPlots.append( Plot(
    name      = 'misIDElectron0_r9',
    texX      = 'R9(e_{misID})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.MisIDElectron0_r9,
    binning   = [ 20, 0, 1 ],
))

addPlots.append( Plot(
    name      = 'misIDElectron0_hoe',
    texX      = 'H/E(e_{misID})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.MisIDElectron0_hoe,
    binning   = [ 20, 0, 0.2 ],
))

addPlots.append( Plot(
    name      = 'misIDElectron0_eInvMinusPInv',
    texX      = '1/E - 1/p (e_{misID})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.MisIDElectron0_eInvMinusPInv,
    binning   = [ 50, -0.3, 0.3 ],
))

addPlots.append( Plot(
    name      = 'misIDElectron0_sieie',
    texX      = '#sigma_{i#etai#eta}(e_{misID})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.MisIDElectron0_sieie,
    binning   = [ 20, 0, 0.02 ],
))

addPlots.append( Plot(
    name      = 'misIDElectron0_pfRelIso03_chg',
    texX      = 'charged relIso_{0.3}(e_{misID})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.MisIDElectron0_pfRelIso03_chg,
    binning   = [ 20, 0, 0.4 ],
))

addPlots.append( Plot(
    name      = 'misIDElectron0_pfRelIso03_all',
    texX      = 'relIso_{0.3}(e_{misID})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.MisIDElectron0_pfRelIso03_all,
    binning   = [ 20, 0, 1.4 ],
))

addPlots.append( Plot(
    name      = 'misIDElectron0_pfRelIso03_n',
    texX      = 'neutral relIso_{0.3}(e_{misID})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.MisIDElectron0_pfRelIso03_all - event.MisIDElectron0_pfRelIso03_chg,
    binning   = [ 20, 0, 1.4 ],
))

# Loop over channels
yields   = {}
allPlots = {}
if args.mode != "None":
    allModes = [ args.mode ]
elif args.nJobs != 1:
    allModes = [ 'mu', 'e', 'all'] if not args.selection.count("nLepTight2") else ["mumutight","muetight","eetight","SFtight","all"]
    allModes = splitList( allModes, args.nJobs)[args.job]
else:
    allModes = [ 'mu', 'e' ] if not args.selection.count("nLepTight2") else ["mumutight","muetight","eetight","SFtight","all"]


filterCutData = getFilterCut( args.year, isData=True, skipBadChargedCandidate=True )
filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )
#tr            = TriggerSelector( args.year, singleLepton=True ) #single lepton trigger also for DY CR
#triggerCutMc  = tr.getSelection( "MC" )

cat_sel0 = [ "%s_photonCatMagic==0"%args.categoryPhoton ]
cat_sel1 = [ "%s_photonCatMagic==1"%args.categoryPhoton ]
cat_sel2 = [ "%s_photonCatMagic==2"%args.categoryPhoton ]
cat_sel3 = [ "%s_photonCatMagic==3"%args.categoryPhoton ]

if "NoChgIso" in args.selection or "NoSieie" in args.selection or "nHadPhoton" in args.selection:
    photonCats = ["-photonhadcat0", "-photonhadcat1", "-photonhadcat2", "-photonhadcat3"]
else:
    photonCats = ["-photoncat0", "-photoncat1", "-photoncat2", "-photoncat3"]

cat_gen2L    = [ "(nGenWElectron+nGenWMuon+nGenWTau)==2" ]
cat_genHad   = [ "(nGenWElectron+nGenWMuon+nGenWTau)==0" ]
cat_genL     = [ "(nGenWElectron+nGenWMuon+nGenWTau)==1&&(nGenWElectron+nGenWMuon)==1" ]
cat_genTau_l = [ "(nGenWElectron+nGenWMuon+nGenWTau)==1&&nGenWTau==1&&nGenWTauJets==0" ]
cat_genTau_q = [ "(nGenWElectron+nGenWMuon+nGenWTau)==1&&nGenWTau==1&&nGenWTauJets==1" ]

if args.invLeptonIso and not regionPlot:
    if args.year == 2016:
        qcd   = QCD_16
        gjets = GJets_16
    elif args.year == 2017:
        qcd   = QCD_17
        gjets = GJets_17
    elif args.year == 2018:
        qcd   = QCD_18
        gjets = GJets_18

invPlotNames = {
                "leptonTightInvIso0_pt":                 "leptonTight0_pt",
                "leptonTightInvIso0_eta":                "leptonTight0_eta",
                "leptonTightInvIso0_phi":                "leptonTight0_phi",
                "mLinv0PhotonTight":                     "mL0PhotonTight",
                "mLinv0PhotonTight_20ptG120":            "mL0PhotonTight_20ptG120",
                "mLinv0PhotonTight_120ptG220":           "mL0PhotonTight_120ptG220",
                "mLinv0PhotonTight_220ptGinf":           "mL0PhotonTight_220ptGinf",
                "mLinv0PhotonTight_coarse":              "mL0PhotonTight_coarse",
                "mLinv0PhotonTight_20ptG120_coarse":     "mL0PhotonTight_20ptG120_coarse",
                "mLinv0PhotonTight_120ptG220_coarse":    "mL0PhotonTight_120ptG220_coarse",
                "mLinv0PhotonTight_220ptGinf_coarse":    "mL0PhotonTight_220ptGinf_coarse",
                "mTinv":                                 "mT",
                "mTinv_20ptG120":                        "mT_20ptG120",
                "mTinv_120ptG220":                       "mT_120ptG220",
                "mTinv_220ptGinf":                       "mT_220ptGinf",
                "mT2lginv":                              "mT2lg",
                "mT2lginv_20ptG120":                     "mT2lg_20ptG120",
                "mT2lginv_120ptG220":                    "mT2lg_120ptG220",
                "mT2lginv_220ptGinf":                    "mT2lg_220ptGinf",
                "Lpinv":                                 "Lp",
                "nElectronGoodInvIso":                   "nElectronGood",
                "nMuonGoodInvIso":                       "nMuonGood",
                "nLeptonGoodInvIso":                     "nLeptonGood",
                "nElectronTightInvIso":                  "nElectronTight",
                "nMuonTightInvIso":                      "nMuonTight",
                "nLeptonTightInvIso":                    "nLeptonTight",
                'nPhotonGoodInvIso':                     "nPhotonGood",
                'nJetGoodInvIso':                        "nJetGood",
                'nJetGoodInvIso_wide':                   "nJetGood_wide",
                'nJetGoodInvIso_semi':                   "nJetGood_semi",
                'nJetGoodInvIso_semi2':                  "nJetGood_semi2",
                'nJetGoodInvIso_semi3':                  "nJetGood_semi3",
                'nJetGoodInvIso_20ptG120':               "nJetGood_20ptG120",
                'nJetGoodInvIso_120ptG220':              "nJetGood_120ptG220",
                'nJetGoodInvIso_220ptGinf':              "nJetGood_220ptGinf",
                'nBJetGoodInvIso':                       "nBJetGood",
                'nBJetGoodInvIso_20ptG120':              "nBJetGood_20ptG120",
                'nBJetGoodInvIso_120ptG220':             "nBJetGood_120ptG220",
                'nBJetGoodInvIso_220ptGinf':             "nBJetGood_220ptGinf",
                'htinv':                                 "ht",
                'm3inv':                                 "m3",
                'm3inv_coarse':                          "m3_coarse",
                'm3inv_20ptG120':                        "m3_20ptG120",
                'm3inv_120ptG220':                       "m3_120ptG220",
                'm3inv_220ptGinf':                       "m3_220ptGinf",
                'm3inv_20ptG120_coarse':                 "m3_20ptG120_coarse",
                'm3inv_120ptG220_coarse':                "m3_120ptG220_coarse",
                'm3inv_220ptGinf_coarse':                "m3_220ptGinf_coarse",
                "jetGoodinv0_pt":                        "jetGood0_pt",
                "jetGoodinv0_pt_wide":                   "jetGood0_pt_wide",
                "jetGoodinv0_eta":                       "jetGood0_eta",
                "jetGoodinv0_phi":                       "jetGood0_phi",
                "jetGoodinv0_neHEF":                     "jetGood0_neHEF",
                "jetGoodinv0_neEmEF":                    "jetGood0_neEmEF",
                "jetGoodinv0_chEmHEF":                   "jetGood0_chEmHEF",
                "jetGoodinv0_chHEF":                     "jetGood0_chHEF",
                "jetGoodinv1_pt_wide":                   "jetGood1_pt_wide",
                "jetGoodinv1_pt":                        "jetGood1_pt",
                "jetGoodinv1_eta":                       "jetGood1_eta",
                "jetGoodinv1_phi":                       "jetGood1_phi",
                "jetGoodinv1_neHEF":                     "jetGood1_neHEF",
                "jetGoodinv1_neEmEF":                    "jetGood1_neEmEF",
                "jetGoodinv1_chEmHEF":                   "jetGood1_chEmHEF",
                "jetGoodinv1_chHEF":                     "jetGood1_chHEF",
                "leptonTightinv0_hoe":                   "leptonTight0_hoe",
                "leptonTightinv0_eInvMinusPInv":         "leptonTight0_eInvMinusPInv",
                "leptonTightinv0_convVeto":              "leptonTight0_convVeto",
                "leptonTightinv0_sieie":                 "leptonTight0_sieie",
                "leptonTightinv0_sip3d":                    "leptonTight0_sip3d",
                "leptonTightinv0_lostHits":                 "leptonTight0_lostHits",
                "leptonTightinv0_dr03EcalRecHitSumEt":      "leptonTight0_dr03EcalRecHitSumEt",
                "leptonTightinv0_dr03HcalDepth1TowerSumEt": "leptonTight0_dr03HcalDepth1TowerSumEt",
                "leptonTightinv0_dr03TkSumPt":              "leptonTight0_dr03TkSumPt",
                "leptonTightinv0_dxy":                      "leptonTight0_dxy",
                "leptonTightinv0_dz":                       "leptonTight0_dz",
                "leptonTightinv0_ip3d":                     "leptonTight0_ip3d",
                "leptonTightinv0_r9":                       "leptonTight0_r9",
                "mindRJetTightLeptoninv":                "mindRJetTightLepton",
                "dRLTight0PhotonGood0inv":               "dRLTight0PhotonGood0",
                "dPhiLTight0PhotonGood0inv":             "dPhiLTight0PhotonGood0",
 }


for index, mode in enumerate( allModes ):
    logger.info( "Computing plots for mode %s", mode )

    yields = {}
    dataMCScale = {}
    for m in ["incl", "20ptG120", "120ptG220", "220ptGinf"]:
        yields[m] = {}
        yields[m][mode] = {}

    # always initialize with [], elso you get in trouble with pythons references!
    plots  = []
    plots += plotList
    if args.invLeptonIso:
        plots += getInvYieldPlots( index ) 
    else:
        plots += getYieldPlots( index ) 
    plots += addPlots
    if "NoIso" in args.mode:
        plots += noIsoPlots
    if not "NoChgIso" in args.selection and not "NoSieie" in args.selection and not "nHadPhoton" in args.selection:
        plots = [ plot for plot in plots if not "NoChgIso" in plot.name and not "NoSieie" in plot.name ]
    if args.invLeptonIso:
        plots = [ plot for plot in plots if plot.name not in invPlotNames.values() ]
    else:
        plots = [ plot for plot in plots if plot.name not in invPlotNames.keys() ]

    # Define 2l selections
    isoleptonSelection    = cutInterpreter.cutString( mode )
    if args.invLeptonIso:
        invIsoleptonSelection = cutInterpreter.cutString( mode + "Inv" )
    leptonSelection       = invIsoleptonSelection if args.invLeptonIso and not categoryPlot and not args.leptonCategory else isoleptonSelection

    if not args.noData:
        data_sample.setSelectionString( [ filterCutData, leptonSelection, "triggered==1" ] )
        print data_sample.selectionString
    if args.invLeptonIso:
        data_sample.setSelectionString( [ filterCutData, leptonSelection, "triggeredInvIso==1" ] )
        print data_sample.selectionString
    if categoryPlot:
        all_cat0.setSelectionString(  [ filterCutMc, leptonSelection, "triggered==1", "pTStitching==1", "overlapRemoval==1" ] + cat_sel0 )
        all_cat1.setSelectionString(  [ filterCutMc, leptonSelection, "triggered==1", "pTStitching==1", "overlapRemoval==1" ] + cat_sel1 )
        all_cat2.setSelectionString(  [ filterCutMc, leptonSelection, "triggered==1", "pTStitching==1", "overlapRemoval==1" ] + cat_sel2 )
        all_cat3.setSelectionString(  [ filterCutMc, leptonSelection, "triggered==1", "pTStitching==1", "overlapRemoval==1" ] + cat_sel3 )
    elif args.leptonCategory:
        ttg_2l.setSelectionString(    [ filterCutMc, leptonSelection, "triggered==1", "pTStitching==1", "overlapRemoval==1" ] + cat_gen2L )
        ttg_l.setSelectionString(     [ filterCutMc, leptonSelection, "triggered==1", "pTStitching==1", "overlapRemoval==1" ] + cat_genL )
        ttg_tau_l.setSelectionString( [ filterCutMc, leptonSelection, "triggered==1", "pTStitching==1", "overlapRemoval==1" ] + cat_genTau_l )
        ttg_tau_q.setSelectionString( [ filterCutMc, leptonSelection, "triggered==1", "pTStitching==1", "overlapRemoval==1" ] + cat_genTau_q )
        ttg_had.setSelectionString(   [ filterCutMc, leptonSelection, "triggered==1", "pTStitching==1", "overlapRemoval==1" ] + cat_genHad )

        tt_2l.setSelectionString(     [ filterCutMc, leptonSelection, "triggered==1", "pTStitching==1", "overlapRemoval==1" ] + cat_gen2L )
        tt_l.setSelectionString(      [ filterCutMc, leptonSelection, "triggered==1", "pTStitching==1", "overlapRemoval==1" ] + cat_genL )
        tt_tau_l.setSelectionString(  [ filterCutMc, leptonSelection, "triggered==1", "pTStitching==1", "overlapRemoval==1" ] + cat_genTau_l )
        tt_tau_q.setSelectionString(  [ filterCutMc, leptonSelection, "triggered==1", "pTStitching==1", "overlapRemoval==1" ] + cat_genTau_q )
        tt_had.setSelectionString(    [ filterCutMc, leptonSelection, "triggered==1", "pTStitching==1", "overlapRemoval==1" ] + cat_genHad )

        all_noTT.setSelectionString(  [ filterCutMc, leptonSelection, "triggered==1", "pTStitching==1", "overlapRemoval==1" ] )
    else:
        for sample in mc:# + signals:
            if (sample.name.startswith("DY") and args.replaceZG): #no ZG sample
                sample.setSelectionString( [ filterCutMc, leptonSelection, "triggered==1", "pTStitching==1" ] )
            else:
                sample.setSelectionString( [ filterCutMc, leptonSelection, "triggered==1", "pTStitching==1", "overlapRemoval==1" ] )

    if args.invLeptonIso and not regionPlot:
        preSelectionSR = "&&".join( [ cutInterpreter.cutString( args.selection ), filterCutMc, isoleptonSelection,    "triggeredInvIso==1", "pTStitching==1", "overlapRemoval==1"  ] )
        preSelectionCR = "&&".join( [ preSelection,                               filterCutMc, invIsoleptonSelection, "triggeredInvIso==1", "pTStitching==1", "overlapRemoval==1"  ] )

        yield_QCD_CR  = u_float( qcd.getYieldFromDraw(   selectionString=preSelectionCR, weightString="weight*%f*%s"%(lumi_scale,weightString) ) )
        yield_QCD_SR  = u_float( qcd.getYieldFromDraw(   selectionString=preSelectionSR, weightString="weight*%f*%s"%(lumi_scale,weightString) ) )

        transFacQCD = {}
        transFacQCD["incl"] = yield_QCD_SR / yield_QCD_CR if yield_QCD_CR.val != 0 else u_float({"val":0, "sigma":0})
#        transFacQCD["incl"] = transFacQCD["incl"].val

        if not "nPhoton0" in args.selection and transFacQCD["incl"].val > 0:
            for pt in ptSels:
                yield_QCD_CR  = u_float( qcd.getYieldFromDraw(   selectionString=preSelectionCR + "&&" + cutInterpreter.cutString( pt ), weightString="weight*%f*%s"%(lumi_scale,weightString) ) )
                yield_QCD_CR += u_float( gjets.getYieldFromDraw( selectionString=preSelectionCR + "&&" + cutInterpreter.cutString( pt ), weightString="weight*%f*%s"%(lumi_scale,weightString) ) )
                yield_QCD_SR  = u_float( qcd.getYieldFromDraw(   selectionString=preSelectionSR + "&&" + cutInterpreter.cutString( pt ), weightString="weight*%f*%s"%(lumi_scale,weightString) ) )
                yield_QCD_SR += u_float( gjets.getYieldFromDraw( selectionString=preSelectionSR + "&&" + cutInterpreter.cutString( pt ), weightString="weight*%f*%s"%(lumi_scale,weightString) ) )

                transFacQCD[ptLabels[pt]] = yield_QCD_SR / yield_QCD_CR if yield_QCD_CR.val != 0 else u_float({"val":0, "sigma":0})
#                transFacQCD[ptLabels[pt]] = transFacQCD[ptLabels[pt]].val
        else:
            for pt in ptSels:
                transFacQCD[ptLabels[pt]] = transFacQCD["incl"]

    elif args.invLeptonIso:
        # get cached transferfactors
        estimators      = EstimatorList( setup, processes=["QCD-DD"] )
        estimate        = getattr(estimators, "QCD-DD")
        estimate.isData = False
        estimate.initCache(setup.defaultCacheDir())

        transFacQCD = {}
        transFacQCD["incl"] = estimate.cachedTransferFactor( mode, setup, checkOnly=True)
        transFacQCD["incl"] = estimate.cachedTransferFactor( mode, setup, checkOnly=True)
#        transFacQCD["incl"] = transFacQCD["incl"].val
        for pt in ptSels:
            transFacQCD[ptLabels[pt]] = transFacQCD["incl"]

    plotting.fill( plots, read_variables=read_variables, sequence=sequence )

    if mode == "all" and args.selection.count("nLepTight2"):
        qcdModes = ["eetight", "mumutight", "muetight"]
    elif mode == "SFtight" and args.selection.count("nLepTight2"):
        qcdModes = ["eetight", "mumutight"]
    elif mode == "all" and args.selection.count("nLepTight1"):
        qcdModes = ["e", "mu"]
    else:
        qcdModes = [mode]

    if not args.invLeptonIso and not args.noQCDDD:
        for plot in plots:
#            if "nBJet" in plot.name or "nElectron" in plot.name or "nMuon" in plot.name or "yield" in plot.name: continue
#            if "nBJet" in plot.name: continue
            if plot.name in invPlotNames.keys(): continue
            if "category" in plot.name: continue

            for i_m, m in enumerate(qcdModes):
                res = "_".join( ["qcdHisto", args.selection, plot.name, str(args.year), m, "small" if args.small else "full"] + map( str, plot.binning ) )

                if dirDB.contains(res) and not args.noQCDDD:
                    logger.info( "Adding QCD histogram from cache for plot %s"%plot.name )
                    if i_m == 0:
                        qcdHist = copy.deepcopy(dirDB.get(res))
                    else:
                        qcdHist.Add( copy.deepcopy(dirDB.get(res)) )
                else:
                    logger.info( "No QCD histogram found for plot %s"%plot.name )
                    qcdHist = None
            if qcdHist:
                if args.leptonCategory:
                    for h in plot.histos[0]:
                        if all_noTT.name in h.GetName():
                            h.Add(qcdHist)
                else:
                    qcdHist.SetName( "datadrivenQCD_" + qcdHist.GetName() )
                    plot.histos[0] = [ h if not "QCD" in h.GetName() else qcdHist for h in plot.histos[0] ]
    # Get normalization yields from yield histogram
    for plot in plots:
        if "yield" in plot.name:
            for i, l in enumerate( plot.histos ):
                for j, h in enumerate( l ):
                    if not args.selection.count("nLepTight2"):
                        h.GetXaxis().SetBinLabel( 1, "#mu" )
                        h.GetXaxis().SetBinLabel( 2, "e" )
                    else:
                        h.GetXaxis().SetBinLabel( 1, "#mu#mu" )
                        h.GetXaxis().SetBinLabel( 2, "#mue" )
                        h.GetXaxis().SetBinLabel( 3, "ee" )
                    yields["incl" if plot.name == "yield" else plot.name.split("_")[1]][mode][plot.stack[i][j].name] = h.Integral()
#                    if plot.name == "yield":
#                        if mode == "mu" or mode == "mumutight":
#                            yields[mode][plot.stack[i][j].name] = h.GetBinContent( h.FindBin( 0.5 ) )
#                        elif mode == "e" or mode == "muetight":
#                            yields[mode][plot.stack[i][j].name] = h.GetBinContent( h.FindBin( 1.5 ) )
#                        elif mode == "eetight":
#                            yields[mode][plot.stack[i][j].name] = h.GetBinContent( h.FindBin( 2.5 ) )
#                        elif mode == "SFtight":
#                            yields[mode][plot.stack[i][j].name]  = h.GetBinContent( h.FindBin( 0.5 ) )
#                            yields[mode][plot.stack[i][j].name] += h.GetBinContent( h.FindBin( 2.5 ) )
#                        elif mode == "all" and args.selection.count("nLepTight2"):
#                            yields[mode][plot.stack[i][j].name]  = h.GetBinContent( h.FindBin( 0.5 ) )
#                            yields[mode][plot.stack[i][j].name] += h.GetBinContent( h.FindBin( 1.5 ) )
#                            yields[mode][plot.stack[i][j].name] += h.GetBinContent( h.FindBin( 2.5 ) )
#                        elif mode == "all" and not args.selection.count("nLepTight2"):
#                            yields[mode][plot.stack[i][j].name]  = h.GetBinContent( h.FindBin( 0.5 ) )
#                            yields[mode][plot.stack[i][j].name] += h.GetBinContent( h.FindBin( 1.5 ) )
        elif "category" in plot.name:
            for i, l in enumerate( plot.histos ):
                for j, h in enumerate( l ):
                     h.GetXaxis().SetBinLabel( 1, "genuine #gamma" )
                     h.GetXaxis().SetBinLabel( 2, "had. #gamma" )
                     h.GetXaxis().SetBinLabel( 3, "misID e" )
                     h.GetXaxis().SetBinLabel( 4, "had. fake" )

    for m in ["incl", "20ptG120", "120ptG220", "220ptGinf"]:
        if args.noData: yields[m][mode]["data"] = 0
        yields[m][mode]["MC"] = sum( yields[m][mode][s.name] for s in mc )
        dataMCScale[m]        = yields[m][mode]["data"] / yields[m][mode]["MC"] if yields[m][mode]["MC"] != 0 else float('nan')

    logger.info( "Plotting mode %s", mode )
    allPlots[mode] = copy.deepcopy(plots) # deep copy for creating SF/all plots afterwards!
    drawPlots( allPlots[mode], mode, transFacQCD if args.invLeptonIso else dataMCScale )

if args.mode != "None" or args.nJobs != 1:
    sys.exit(0)

# Add the different channels into all
yields["all"] = {}

for m in ["incl", "20ptG120", "120ptG220", "220ptGinf"]:
    for y in yields["mu"]:
        try:    yields[m]["all"][y] = sum( yields[m][c][y] for c in ['mu','e'] )
        except: yields[m]["all"][y] = 0
    dataMCScale[m] = yields[m]["all"]["data"] / yields[m]["all"]["MC"] if yields[m]["all"]["MC"] != 0 else float('nan')

allPlots['mu'] = filter( lambda plot: "_ratio" not in plot.name, allPlots['mu'] )
for plot in allPlots['mu']:
    for pl in ( p for p in allPlots['e'] if p.name == plot.name ):  
        for i, j in enumerate( list( itertools.chain.from_iterable( plot.histos ) ) ):
            j.Add( list( itertools.chain.from_iterable( pl.histos ) )[i] )

drawPlots( allPlots['mu'], "all", transFacQCD if args.invLeptonIso else dataMCScale )

