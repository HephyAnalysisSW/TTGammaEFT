#!/usr/bin/env python
''' Analysis script for standard plots
'''

# Standard imports
import ROOT, os, imp, sys, copy
ROOT.gROOT.SetBatch(True)
import itertools
from math                             import isnan, ceil, pi

# RootTools
from RootTools.core.standard          import *

# Internal Imports
from TTGammaEFT.Tools.user            import plot_directory
from TTGammaEFT.Tools.helpers         import splitList
from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter
from TTGammaEFT.Tools.TriggerSelector import TriggerSelector
from TTGammaEFT.Tools.Variables       import NanoVariables
from TTGammaEFT.Tools.objectSelection import isBJet, photonSelector, vidNestedWPBitMapNamingListPhoton

from Analysis.Tools.metFilters        import getFilterCut
from Analysis.Tools.helpers           import getCollection, deltaR

# Default Parameter
loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']
photonCatChoices = [ "None", "PhotonGood0", "PhotonGood1", "PhotonMVA0", "PhotonNoChgIso0", "PhotonNoChgIsoNoSieie0", "PhotonNoSieie0" ]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                  help="Log level for logging")
argParser.add_argument('--plot_directory',     action='store',      default='102X_TTG_ppv1_v1')
argParser.add_argument('--plotFile',           action='store',      default='all_noPhoton')
argParser.add_argument('--selection',          action='store',      default='dilepOS-nLepVeto2-pTG20-nPhoton1p-offZSFllg-offZSFll-mll40')
argParser.add_argument('--small',              action='store_true',                                                                    help='Run only on a small subset of the data?', )
argParser.add_argument('--noData',             action='store_true', default=False,                                                     help='also plot data?')
argParser.add_argument('--signal',             action='store',      default=None,   nargs='?', choices=[None],                         help="Add signal to plot")
argParser.add_argument('--year',               action='store',      default=None,   type=int,  choices=[2016,2017,2018],               help="Which year to plot?")
argParser.add_argument('--onlyTTG',            action='store_true', default=False,                                                     help="Plot only ttG")
argParser.add_argument('--normalize',          action='store_true', default=False,                                                     help="Normalize yields" )
argParser.add_argument('--addOtherBg',         action='store_true', default=False,                                                     help="add others background" )
argParser.add_argument('--categoryPhoton',     action='store',      default="None", type=str, choices=photonCatChoices,                help="plot in terms of photon category, choose which photon to categorize!" )
argParser.add_argument('--mode',               action='store',      default="None", type=str, choices=["mu", "e", "all"],              help="plot lepton mode" )
argParser.add_argument('--nJobs',              action='store',      default=1,      type=int, choices=[1,2,3],                         help="Maximum number of simultaneous jobs.")
argParser.add_argument('--job',                action='store',      default=0,      type=int, choices=[0,1,2],                         help="Run only job i")
args = argParser.parse_args()

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

categoryPlot = args.categoryPhoton != "None"

addMissIDSF = False
selDir = args.selection
if args.selection.count("addMissIDSF"):
    addMissIDSF = True
    args.selection = args.selection.replace("-addMissIDSF", "").replace("addMissIDSF-", "")

if args.small:           args.plot_directory += "_small"
if args.noData:          args.plot_directory += "_noData"
if args.signal:          args.plot_directory += "_signal_"+args.signal
if args.onlyTTG:         args.plot_directory += "_onlyTTG"
if args.normalize:       args.plot_directory += "_normalize"

# Samples
os.environ["gammaSkim"]="True" if "hoton" in args.selection or "pTG" in args.selection else "False"
if args.year == 2016:
    from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed      import *
    if not args.noData:
        from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import *

elif args.year == 2017:
    from TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed        import *
    if not args.noData:
        from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import *

elif args.year == 2018:
    from TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed      import *
    if not args.noData:
        from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import *

# Text on the plots
def drawObjects( plotData, dataMCScale, lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS #bf{#it{Preliminary}}' if plotData else 'CMS #bf{#it{Simulation Preliminary}}'), 
      (0.45, 0.95, '%3.1f fb{}^{-1} (13 TeV) Scale %3.2f'% ( lumi_scale, dataMCScale ) ) if plotData else (0.65, 0.95, '%3.1f fb{}^{-1} (13 TeV)' % lumi_scale)
    ]
    return [tex.DrawLatex(*l) for l in lines] 

#scaling = { i+1:0 for i in range(len(signals)) }
scaling = { 1:0 }

# Plotting
def drawPlots( plots, mode, dataMCScale ):

    logger.info( "Plotting mode: %s"%mode )

    for log in [False, True]:
        sc  = "cat_" if categoryPlot else ""
        sc += "log" if log else "lin"
        plot_directory_ = os.path.join( plot_directory, 'analysisPlots', str(args.year), args.plot_directory, selDir, mode, sc )

        for plot in plots:
            if not max(l[0].GetMaximum() for l in plot.histos):
                logger.info( "Empty plot!" )
                continue # Empty plot
            postFix = " (legacy)"
            if not args.noData: 
                plot.histos[1][0].style = styles.errorStyle( ROOT.kBlack )
                if mode == "all":
                    plot.histos[1][0].legendText = "data" + postFix
            extensions_ = ["pdf", "png", "root"]

            logger.info( "Plotting..." )

            if isinstance( plot, Plot):
                plotting.draw( plot,
	                           plot_directory = plot_directory_,
                               extensions = extensions_,
	                           ratio = {'yRange':(0.1,1.9)} if not args.noData else None,
	                           logX = False, logY = log, sorting = not categoryPlot,
	                           yRange = (0.03, "auto") if log else (0.001, "auto"),
    	                       scaling = scaling if args.normalize else {},
	                           legend = [ (0.15,0.9-0.03*sum(map(len, plot.histos)),0.9,0.9), 2],
	                           drawObjects = drawObjects( not args.noData, dataMCScale , lumi_scale ) if not args.normalize else drawObjects( not args.noData, 1.0 , lumi_scale ),
                               copyIndexPHP = True,
                             )

            elif isinstance( plot, Plot2D ):
                p_mc = Plot2D.fromHisto( plot.name+'_mc', plot.histos[:1], texX = plot.texX, texY = plot.texY )
                plotting.draw2D( p_mc,
                    plot_directory = plot_directory_,
                    extensions = extensions_,
                    #ratio = {'yRange':(0.1,1.9)},
                    logX = False, logY = False, logZ = log, #sorting = True,
                    #yRange = (0.03, "auto") if log else (0.001, "auto"),
                    #scaling = {},
                    #legend = (0.50,0.88-0.04*sum(map(len, plot.histos)),0.9,0.88),
                    drawObjects = drawObjects( not args.noData, dataMCScale , lumi_scale ),
                    copyIndexPHP = True,
                )
                p_data = Plot2D.fromHisto( plot.name+'_data', plot.histos[1:], texX = plot.texX, texY = plot.texY )
                plotting.draw2D(p_data,
                    plot_directory = plot_directory_,
                    extensions = extensions_,
                    #ratio = {'yRange':(0.1,1.9)},
                    logX = False, logY = False, logZ = log, #sorting = True,
                    #yRange = (0.03, "auto") if log else (0.001, "auto"),
                    #scaling = {},
                    #legend = (0.50,0.88-0.04*sum(map(len, plot.histos)),0.9,0.88),
                    drawObjects = drawObjects( not args.noData, dataMCScale , lumi_scale ),
                    copyIndexPHP = True,
                )


def getYieldPlot( index ):
    return Plot(
                name      = 'yield',
                texX      = 'yield',
                texY      = 'Number of Events',
                attribute = lambda event, sample: event.nElectronTight,
                binning   = [ 2, 0, 2 ] if not args.selection.count("nLepTight2") else [ 3, 0, 3 ],
                )

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

# Read variables and sequences
read_variables  = ["weight/F",
                   "PV_npvsGood/I",
                   "PV_npvs/I", "PV_npvsGood/I",
                   "nJetGood/I", "nBTagGood/I",
                   "nJet/I", "nBTag/I",
                   "Jet[%s]" %jetVarString,
                   "nLepton/I", "nElectron/I", "nMuon/I",
                   "nLeptonGood/I", "nElectronGood/I", "nMuonGood/I",
                   "nLeptonTight/I", "nElectronTight/I", "nMuonTight/I",
                   "nLeptonVeto/I", "nElectronVeto/I", "nMuonVeto/I",
                   "Photon[%s]" %photonVarString,
                   "nPhoton/I",
                   "nPhotonGood/I",
                   "MET_pt/F", "MET_phi/F", "METSig/F", "ht/F",
                   "mlltight/F", "mllgammatight/F",
                   "mLtight0Gamma/F",
                   "ltight0GammadR/F", "ltight0GammadPhi/F",
                   "m3/F", "m3wBJet/F",
                   "photonJetdR/F", "tightLeptonJetdR/F",
                  ]

read_variables += [ "%s_photonCat/I"%item for item in photonCatChoices if item != "None" ]

read_variables += [ VectorTreeVariable.fromString('Lepton[%s]'%leptonVarString, nMax=10) ]
#read_variables += [ VectorTreeVariable.fromString('Photon[%s]'%photonVarString, nMax=10) ]
#read_variables += [ VectorTreeVariable.fromString('Jet[%s]'%jetVarString, nMax=10) ]
#read_variables += [ VectorTreeVariable.fromString('JetGood[%s]'%jetVarString, nMax=10) ]

read_variables += map( lambda var: "PhotonMVA0_"              + var, photonVariables )
read_variables += map( lambda var: "PhotonGood0_"             + var, photonVariables )
read_variables += map( lambda var: "PhotonNoChgIso0_"         + var, photonVariables )
read_variables += map( lambda var: "PhotonNoSieie0_"          + var, photonVariables )
read_variables += map( lambda var: "PhotonNoChgIsoNoSieie0_"  + var, photonVariables )

read_variables += map( lambda var: "LeptonGood0_"             + var, leptonVariables )
read_variables += map( lambda var: "LeptonGood1_"             + var, leptonVariables )
read_variables += map( lambda var: "LeptonTight0_"            + var, leptonVariables )
read_variables += map( lambda var: "LeptonTight1_"            + var, leptonVariables )
read_variables += map( lambda var: "Bj0_"                     + var, bJetVariables )
read_variables += map( lambda var: "Bj1_"                     + var, bJetVariables )

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

recoPhotonSel_medium_noSieie = photonSelector( 'medium', year=args.year, removedCuts=["sieie"] )

def missIDelectrons( event, sample ):
    allLeptons = getCollection( event, 'Lepton', leptonVarList, 'nLepton' )
    allLeptons = filter( lambda l: l["index"]==event.PhotonGood0_electronIdx and abs(l["pdgId"])==11, allLeptons )
    allLeptons.sort( key = lambda j: -j['pt'] )
    missID = allLeptons[:1]
    for var in leptonVarList:
        if missID:
            setattr( event, "missIDElectron0_" + var, missID[0][var] )
        else:
            try:
                setattr( event, "missIDElectron0_" + var, -999 )
            except:
                setattr( event, "missIDElectron0_" + var, 0 )

def makePhotons( event, sample ):
    allPhotons = getCollection( event, 'Photon', photonVarList, 'nPhoton' )
    allPhotons.sort( key = lambda j: -j['pt'] )
    mediumPhotonsNoSieie = list( filter( lambda g: recoPhotonSel_medium_noSieie(g), allPhotons ) + [None])[0]

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

sequence = [missIDelectrons ]# printWeight ]#clean_Jets ]

# Sample definition
if args.year == 2016:
    if args.onlyTTG and not categoryPlot: mc = [ TTG_priv_16 ]
    elif not categoryPlot:
#        mc = [ TTG_priv_16, TT_pow_16, DY_HT_16, singleTop_16, WJets_HT_16, TG_16, WG_16, ZG_16 ]
        mc = [ TTG_priv_16, TT_pow_16, DY_LO_16, singleTop_16, WJets_16, TG_16, WG_NLO_16, ZG_16 ]
#        mc = [ DY_LO_16 ]
        if args.addOtherBg: mc += [ other_16 ]
    elif categoryPlot:
        all = all_16 if args.addOtherBg else all_noOther_16
elif args.year == 2017:
    if args.onlyTTG and not categoryPlot: mc = [ TTG_priv_17 ]
    elif not categoryPlot:
        mc = [ TTG_priv_17, TT_pow_17, DY_LO_17, singleTop_17, WJets_17, TG_17, WG_17, ZG_17 ]
        if args.addOtherBg: mc += [ other_17 ]
    elif categoryPlot:
        all = all_17 if args.addOtherBg else all_noOther_17
elif args.year == 2018:
    if args.onlyTTG and not categoryPlot: mc = [ TTG_priv_18 ]
    elif not categoryPlot:
        mc = [ TTG_priv_18, TT_pow_18, DY_LO_18, singleTop_18, WJets_18, TG_18, WG_18, ZG_18 ]
        if args.addOtherBg: mc += [ other_18 ]
    elif categoryPlot:
        all = all_18 if args.addOtherBg else all_noOther_18

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

if args.noData:
    if args.year == 2016:   lumi_scale = 35.92
    elif args.year == 2017: lumi_scale = 41.86
    elif args.year == 2018: lumi_scale = 58.83
    stack = Stack( mc )
else:
    if args.year == 2016:   data_sample = Run2016
    elif args.year == 2017: data_sample = Run2017
    elif args.year == 2018: data_sample = Run2018
    data_sample.texName        = "data (legacy)"
    data_sample.name           = "data"
    data_sample.read_variables = [ "event/I", "run/I" ]
    data_sample.scale          = 1
    lumi_scale                 = data_sample.lumi * 0.001
    stack                      = Stack( mc, data_sample )

stack.extend( [ [s] for s in signals ] )

for sample in mc + signals:
    sample.read_variables = read_variables_MC
    sample.scale          = lumi_scale
    sample.style          = styles.fillStyle( sample.color )
    sample.weight         = lambda event, sample: (2.25 if event.nPhotonGood>0 and event.PhotonGood0_photonCat==2 and addMissIDSF else 1.)*event.reweightL1Prefire*event.reweightPU*event.reweightLeptonTightSF*event.reweightLeptonTrackingTightSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF
#event.reweightDilepTriggerBackup

if args.small:
    for sample in stack.samples:
        sample.normalization=1.
        sample.reduceFiles( factor=20 )
        sample.scale /= sample.normalization

weight_ = lambda event, sample: event.weight
tr = TriggerSelector( args.year, singleLepton=True )

# Use some defaults (set defaults before you create/import list of Plots!!)
#preSelection = "&&".join( [ cutInterpreter.cutString( args.selection ), "overlapRemoval==1"] )
preSelection = "&&".join( [ cutInterpreter.cutString( args.selection ) ] )
#Plot.setDefaults(   stack=stack, weight=staticmethod( weight_ ), selectionString=preSelection, addOverFlowBin='upper' )
#Plot2D.setDefaults( stack=stack, weight=staticmethod( weight_ ), selectionString=preSelection )
Plot.setDefaults(   stack=stack, weight="weight", selectionString=preSelection, addOverFlowBin='upper' )
Plot2D.setDefaults( stack=stack, weight="weight", selectionString=preSelection )

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
    name      = 'photonGood0_phi_eta_dataOnly',
    texX      = '#eta(#gamma_{0})',
    texY      = '#phi(#gamma_{0})',
    attribute = (
      TreeVariable.fromString( "PhotonGood0_eta/F" ),
      TreeVariable.fromString( "PhotonGood0_phi/F" ),
    ),
    binning   = [20, -1.5, 1.5, 20, -pi, pi],
))

# plotList
addPlots = []

addPlots.append( Plot(
    name      = 'missIDElectron0_pt',
    texX      = 'p_{T}(e_{miss}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.missIDElectron0_pt,
    binning   = [ 20, 0, 120 ],
))

addPlots.append( Plot(
    name      = 'missIDElectron0_eta',
    texX      = '#eta(e_{miss})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.missIDElectron0_eta,
    binning   = [ 30, -3, 3 ],
))

addPlots.append( Plot(
    name      = 'missIDElectron0_phi',
    texX      = '#phi(e_{miss})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.missIDElectron0_phi,
    binning   = [ 10, -pi, pi ],
))

addPlots.append( Plot(
    name      = 'missIDElectron0_lostHits',
    texX      = 'lost hits(e_{miss})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.missIDElectron0_lostHits,
    binning   = [ 6, 0, 6 ],
))

addPlots.append( Plot(
    name      = 'missIDElectron0_dr03EcalRecHitSumEt',
    texX      = '#DeltaR_{0.3} EcalRecHitSumEt (e_{miss})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.missIDElectron0_dr03EcalRecHitSumEt,
    binning   = [ 20, 0, 4 ],
))

addPlots.append( Plot(
    name      = 'missIDElectron0_dr03HcalDepth1TowerSumEt',
    texX      = '#DeltaR_{0.3} HcalDepth1TowerSumEt (e_{miss})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.missIDElectron0_dr03HcalDepth1TowerSumEt,
    binning   = [ 20, 0, 4 ],
))

addPlots.append( Plot(
    name      = 'missIDElectron0_dr03TkSumPt',
    texX      = '#DeltaR_{0.3} TkSumPt (e_{miss})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.missIDElectron0_dr03TkSumPt,
    binning   = [ 20, 0, 4 ],
))

addPlots.append( Plot(
    name      = 'missIDElectron0_r9',
    texX      = 'R9(e_{miss})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.missIDElectron0_r9,
    binning   = [ 20, 0, 1 ],
))

addPlots.append( Plot(
    name      = 'missIDElectron0_hoe',
    texX      = 'H/E(e_{miss})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.missIDElectron0_hoe,
    binning   = [ 20, 0, 0.2 ],
))

addPlots.append( Plot(
    name      = 'missIDElectron0_eInvMinusPInv',
    texX      = '1/E - 1/p (e_{miss})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.missIDElectron0_eInvMinusPInv,
    binning   = [ 50, -0.3, 0.3 ],
))

addPlots.append( Plot(
    name      = 'missIDElectron0_convVeto',
    texX      = 'conversion veto (e_{miss})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.missIDElectron0_convVeto,
    binning   = [ 3, 0, 3 ],
))

addPlots.append( Plot(
    name      = 'missIDElectron0_sieie',
    texX      = '#sigma_{i#etai#eta}(e_{miss})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.missIDElectron0_sieie,
    binning   = [ 20, 0, 0.02 ],
))

addPlots.append( Plot(
    name      = 'missIDElectron0_pfRelIso03_chg',
    texX      = 'charged relIso_{0.3}(e_{miss})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.missIDElectron0_pfRelIso03_chg,
    binning   = [ 20, 0, 0.2 ],
))

addPlots.append( Plot(
    name      = 'missIDElectron0_pfRelIso03_all',
    texX      = 'relIso_{0.3}(e_{miss})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.missIDElectron0_pfRelIso03_all,
    binning   = [ 20, 0, 1.2 ],
))

addPlots.append( Plot(
    name      = 'missIDElectron0_pfRelIso03_n',
    texX      = 'neutral relIso_{0.3}(e_{miss})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.missIDElectron0_pfRelIso03_all - event.missIDElectron0_pfRelIso03_chg,
    binning   = [ 20, 0, 1.2 ],
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


filterCutData = getFilterCut( args.year, isData=True )
filterCutMc   = getFilterCut( args.year, isData=False )
tr            = TriggerSelector( args.year )
triggerCutMc  = tr.getSelection( "MC" )

cat_sel0 = [ "%s_photonCat==0"%args.categoryPhoton ]
cat_sel1 = [ "%s_photonCat==1"%args.categoryPhoton ]
cat_sel2 = [ "%s_photonCat==2"%args.categoryPhoton ]
cat_sel3 = [ "%s_photonCat==3"%args.categoryPhoton ]

for index, mode in enumerate( allModes ):
    logger.info( "Computing plots for mode %s", mode )

    yields[mode] = {}

    # always initialize with [], elso you get in trouble with pythons references!
    plots  = []
#    plots += plotList
#    plots += [ getYieldPlot( index ) ]
#    plots += addPlots
    plots += add2DPlots

    # Define 2l selections
    leptonSelection = cutInterpreter.cutString( mode )
    if not args.noData:    data_sample.setSelectionString( [ filterCutData, leptonSelection ] )
    if categoryPlot:
        all_cat0.setSelectionString(  [ filterCutMc, leptonSelection, triggerCutMc, "overlapRemoval==1" ] + cat_sel0 )
        all_cat1.setSelectionString(  [ filterCutMc, leptonSelection, triggerCutMc, "overlapRemoval==1" ] + cat_sel1 )
        all_cat2.setSelectionString(  [ filterCutMc, leptonSelection, triggerCutMc, "overlapRemoval==1" ] + cat_sel2 )
        all_cat3.setSelectionString(  [ filterCutMc, leptonSelection, triggerCutMc, "overlapRemoval==1" ] + cat_sel3 )
    else:
        for sample in mc + signals: sample.setSelectionString( [ filterCutMc, leptonSelection, triggerCutMc, "overlapRemoval==1" ] )
#        for sample in mc + signals: sample.setSelectionString( [ filterCutMc, leptonSelection, triggerCutMc ] )

    # Overlap removal
#    if any( x.name == "TTG" for x in mc ) and any( x.name == "TT_pow" for x in mc ):
#        print "overlap removal TTgamma"
#        eval('TTG_priv_'    + str(args.year)[-2:]).addSelectionString( "isTTGamma==1" )
#        eval('TT_pow_' + str(args.year)[-2:]).addSelectionString( "isTTGamma==0" )

#    if any( x.name == "ZG" for x in mc ) and any( x.name == "DY_LO" for x in mc ):
#        print "overlap removal Zgamma"
#        eval('ZG_'    + str(args.year)[-2:]).addSelectionString( "isZWGamma==1" )
#        eval('DY_LO_' + str(args.year)[-2:]).addSelectionString( "isZWGamma==0" )

#    if any( x.name == "WG" for x in mc ) and any( x.name == "WJets" for x in mc ):
#        print "overlap removal Wgamma"
#        eval('WG_'    + str(args.year)[-2:]).addSelectionString( "isZWGamma==1" )
#        eval('WJets_' + str(args.year)[-2:]).addSelectionString( "isZWGamma==0" )

#    if any( x.name == "TG" for x in mc ) and any( x.name == "singleTop" for x in mc ):
#        print "overlap removal singleTop"
#        eval('TG_'        + str(args.year)[-2:]).addSelectionString( "isTGamma==1" )
#        eval('singleTop_' + str(args.year)[-2:]).addSelectionString( "isTGamma==0" ) #ONLY IN THE T-channel!!!

    plotting.fill( plots, read_variables=read_variables, sequence=sequence )

    # Get normalization yields from yield histogram
    for plot in plots:
        if plot.name != "yield": continue
        for i, l in enumerate( plot.histos ):
            for j, h in enumerate( l ):
                if mode == "mu" or mode == "mumutight":
                    yields[mode][plot.stack[i][j].name] = h.GetBinContent( h.FindBin( 0.5 ) )
                elif mode == "e" or mode == "muetight":
                    yields[mode][plot.stack[i][j].name] = h.GetBinContent( h.FindBin( 1.5 ) )
                elif mode == "eetight":
                    yields[mode][plot.stack[i][j].name] = h.GetBinContent( h.FindBin( 2.5 ) )
                elif mode == "SFtight":
                    yields[mode][plot.stack[i][j].name]  = h.GetBinContent( h.FindBin( 0.5 ) )
                    yields[mode][plot.stack[i][j].name] += h.GetBinContent( h.FindBin( 2.5 ) )
                elif mode == "all" and args.selection.count("nLepTight2"):
                    yields[mode][plot.stack[i][j].name]  = h.GetBinContent( h.FindBin( 0.5 ) )
                    yields[mode][plot.stack[i][j].name] += h.GetBinContent( h.FindBin( 1.5 ) )
                    yields[mode][plot.stack[i][j].name] += h.GetBinContent( h.FindBin( 2.5 ) )
                elif mode == "all" and not args.selection.count("nLepTight2"):
                    yields[mode][plot.stack[i][j].name]  = h.GetBinContent( h.FindBin( 0.5 ) )
                    yields[mode][plot.stack[i][j].name] += h.GetBinContent( h.FindBin( 1.5 ) )
                if not args.selection.count("nLepTight2"):
                    h.GetXaxis().SetBinLabel( 1, "#mu" )
                    h.GetXaxis().SetBinLabel( 2, "e" )
                else:
                    h.GetXaxis().SetBinLabel( 1, "#mu#mu" )
                    h.GetXaxis().SetBinLabel( 2, "#mue" )
                    h.GetXaxis().SetBinLabel( 3, "ee" )

    if args.noData: yields[mode]["data"] = 0

    yields[mode]["MC"] = sum( yields[mode][s.name] for s in mc )
    dataMCScale        = yields[mode]["data"] / yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')

    logger.info( "Plotting mode %s", mode )
    allPlots[mode] = copy.deepcopy(plots) # deep copy for creating SF/all plots afterwards!
    drawPlots( allPlots[mode], mode, dataMCScale )

if args.mode != "None" or args.nJobs != 1:
    sys.exit(0)

# Add the different channels into all
yields["all"] = {}

for y in yields["mu"]:
    try:    yields["all"][y] = sum( yields[c][y] for c in ['mu','e'] )
    except: yields["all"][y] = 0

dataMCScale = yields["all"]["data"] / yields["all"]["MC"] if yields["all"]["MC"] != 0 else float('nan')

for plot in allPlots['mu']:
    for pl in ( p for p in allPlots['e'] if p.name == plot.name ):  
        for i, j in enumerate( list( itertools.chain.from_iterable( plot.histos ) ) ):
            j.Add( list( itertools.chain.from_iterable( pl.histos ) )[i] )

drawPlots( allPlots['mu'], "all", dataMCScale )

