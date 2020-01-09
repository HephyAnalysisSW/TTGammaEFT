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
from Analysis.Tools.helpers           import getCollection

# Default Parameter
loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']
photonCatChoices = [ "None", "PhotonGood0", "PhotonGood1", "PhotonMVA0", "PhotonNoChgIso0", "PhotonNoChgIsoNoSieie0", "PhotonNoSieie0" ]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                     help="Log level for logging")
argParser.add_argument('--plot_directory',     action='store',      default='102X_TTG_ppv1_v1')
argParser.add_argument('--plotFile',           action='store',      default='all_noPhoton')
argParser.add_argument('--selection',          action='store',      default='dilepOS-nLepVeto2-pTG20-nPhoton1p-offZSFllg-offZSFll-mll40')
argParser.add_argument('--small',              action='store_true',                                                                       help='Run only on a small subset of the data?', )
argParser.add_argument('--noData',             action='store_true', default=False,                                                        help='also plot data?')
argParser.add_argument('--signal',             action='store',      default=None,   nargs='?', choices=[None],                            help="Add signal to plot")
argParser.add_argument('--year',               action='store',      default=None,   type=int,  choices=[2016,2017,2018],                  help="Which year to plot?")
argParser.add_argument('--onlyTTG',            action='store_true', default=False,                                                        help="Plot only ttG")
argParser.add_argument('--normalize',          action='store_true', default=False,                                                        help="Normalize yields" )
argParser.add_argument('--addOtherBg',         action='store_true', default=False,                                                        help="add others background" )
argParser.add_argument('--categoryPhoton',     action='store',      default="None", type=str, choices=photonCatChoices,                   help="plot in terms of photon category, choose which photon to categorize!" )
argParser.add_argument('--mode',               action='store',      default="None", type=str, choices=["mumu", "mue", "ee", "SF", "all"], help="plot lepton mode" )
argParser.add_argument('--nJobs',              action='store',      default=1,      type=int, choices=[1,2,3,4,5],                        help="Maximum number of simultaneous jobs.")
argParser.add_argument('--job',                action='store',      default=0,      type=int, choices=[0,1,2,3,4],                        help="Run only job i")
args = argParser.parse_args()

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

categoryPlot = args.categoryPhoton != "None"

if args.small:           args.plot_directory += "_small"
if args.noData:          args.plot_directory += "_noData"
if args.signal:          args.plot_directory += "_signal_"+args.signal
if args.onlyTTG:         args.plot_directory += "_onlyTTG"
if args.normalize:       args.plot_directory += "_normalize"

# Samples
#os.environ["gammaSkim"]="True" if "hoton" in args.selection or "pTG" in args.selection else "False"
os.environ["gammaSkim"]="False"
if args.year == 2016:
    from TTGammaEFT.Samples.nanoTuples_Summer16_private_postProcessed      import *
    if not args.noData:
        del postprocessing_directory
        from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_postProcessed import *

elif args.year == 2017:
    from TTGammaEFT.Samples.nanoTuples_Fall17_private_postProcessed        import *
    if not args.noData:
        del postprocessing_directory
        from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_postProcessed import *

elif args.year == 2018:
    from TTGammaEFT.Samples.nanoTuples_Autumn18_private_postProcessed      import *
    if not args.noData:
        del postprocessing_directory
        from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_postProcessed import *

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
    for log in [False, True]:
        sc  = "cat_" if categoryPlot else ""
        sc += "log" if log else "lin"
        plot_directory_ = os.path.join( plot_directory, 'analysisPlots', str(args.year), args.plot_directory, args.selection, mode, sc )

        for plot in plots:
            if not max(l[0].GetMaximum() for l in plot.histos): 
                continue # Empty plot
            postFix = " (legacy)"
            if not args.noData: 
                plot.histos[1][0].style          = styles.errorStyle( ROOT.kBlack )
                if mode == "all":
                    plot.histos[1][0].legendText = "data" + postFix
                if mode == "SF":
                    plot.histos[1][0].legendText = "data (SF)" + postFix
            extensions_ = ["pdf", "png", "root"] if mode in ['all', 'SF', 'mue'] else ['png']

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

def getYieldPlot( index ):
    return Plot(
                name      = 'yield',
                texX      = 'yield',
                texY      = 'Number of Events',
                attribute = lambda event, sample: event.nElectronGood,
                binning   = [ 3, 0, 3 ],
                )

# get nano variable lists
NanoVars         = NanoVariables( args.year )
jetVarString     = NanoVars.getVariableString(   "Jet",    postprocessed=True, data=(not args.noData), plot=True )
jetVariableNames = NanoVars.getVariableNameList( "Jet",    postprocessed=True, data=(not args.noData), plot=True )
bJetVariables    = NanoVars.getVariables(        "BJet",   postprocessed=True, data=(not args.noData), plot=True )
leptonVariables  = NanoVars.getVariables(        "Lepton", postprocessed=True, data=(not args.noData), plot=True )
leptonVarString  = NanoVars.getVariableString(   "Lepton", postprocessed=True, data=(not args.noData), plot=True )
photonVariables  = NanoVars.getVariables(        "Photon", postprocessed=True, data=(not args.noData), plot=True )
photonVarString  = NanoVars.getVariableString(   "Photon", postprocessed=True, data=(not args.noData), plot=True )
photonVarList    = NanoVars.getVariableNameList( "Photon", postprocessed=True, data=(not args.noData), plot=True )

# Read variables and sequences
read_variables  = ["weight/F",
                   "PV_npvsGood/I",
                   "Jet[%s]" %jetVarString,
                   "PV_npvs/I", "PV_npvsGood/I",
                   "nJetGood/I", "nBTagGood/I",
                   "nJet/I", "nBTag/I",
                   "nLepton/I","nElectron/I", "nMuon/I",
                   "nLeptonGood/I","nElectronGood/I", "nMuonGood/I",
                   "nLeptonGoodLead/I","nElectronGoodLead/I", "nMuonGoodLead/I",
                   "nLeptonTight/I", "nElectronTight/I", "nMuonTight/I",
                   "nLeptonVeto/I", "nElectronVeto/I", "nMuonVeto/I",
                   "Photon[%s]" %photonVarString,
                   "nPhoton/I",
                   "nPhotonGood/I",
                   "MET_pt/F", "MET_phi/F", "METSig/F", "ht/F",
                   "mll/F", "mllgamma/F",
                   "mlltight/F", "mllgammatight/F",
                   "mLtight0Gamma/F",
                   "ltight0GammadR/F", "ltight0GammadPhi/F",
                   "m3/F", "m3wBJet/F",
                   "lldR/F", "lldPhi/F", "bbdR/F", "bbdPhi/F",
                   "photonJetdR/F", "photonLepdR/F", "leptonJetdR/F", "tightLeptonJetdR/F",
                   "mL0Gamma/F",  "mL1Gamma/F",
                   "l0GammadR/F", "l0GammadPhi/F",
                   "l1GammadR/F", "l1GammadPhi/F",
                   "j0GammadR/F", "j0GammadPhi/F",
                   "j1GammadR/F", "j1GammadPhi/F",
                  ]

read_variables += [ "%s_photonCat/I"%item for item in photonCatChoices if item != "None" ]

#read_variables += [ VectorTreeVariable.fromString('Lepton[%s]'%leptonVarString, nMax=10) ]
#read_variables += [ VectorTreeVariable.fromString('Photon[%s]'%photonVarString, nMax=10) ]
#read_variables += [ VectorTreeVariable.fromString('Jet[%s]'%jetVarString, nMax=10) ]
#read_variables += [ VectorTreeVariable.fromString('JetGood[%s]'%jetVarString, nMax=10) ]

read_variables += map( lambda var: "PhotonMVA0_"   + var, photonVariables )
read_variables += map( lambda var: "PhotonNoChgIso0_"         + var, photonVariables )
read_variables += map( lambda var: "PhotonNoSieie0_"          + var, photonVariables )
read_variables += map( lambda var: "PhotonNoChgIsoNoSieie0_"  + var, photonVariables )
read_variables += map( lambda var: "PhotonGood0_"  + var, photonVariables )
read_variables += map( lambda var: "PhotonGood1_"  + var, photonVariables )
read_variables += map( lambda var: "LeptonGood0_"  + var, leptonVariables )
read_variables += map( lambda var: "LeptonGood1_"  + var, leptonVariables )
read_variables += map( lambda var: "LeptonTight0_" + var, leptonVariables )
read_variables += map( lambda var: "LeptonTight1_" + var, leptonVariables )
read_variables += map( lambda var: "Bj0_"          + var, bJetVariables )
read_variables += map( lambda var: "Bj1_"          + var, bJetVariables )

read_variables_MC = ["isTTGamma/I", "isZWGamma/I", "isTGamma/I", "overlapRemoval/I",
                     "reweightPU/F", "reweightPUDown/F", "reweightPUUp/F", "reweightPUVDown/F", "reweightPUVUp/F",
                     "reweightLepton2lSF/F", "reweightLepton2lSFUp/F", "reweightLepton2lSFDown/F",
                     "reweightLeptonTracking2lSF/F",
                     "reweightDilepTrigger/F", "reweightDilepTriggerUp/F", "reweightDilepTriggerDown/F",
                     "reweightDilepTriggerBackup/F", "reweightDilepTriggerBackupUp/F", "reweightDilepTriggerBackupDown/F",
                     "reweightPhotonSF/F", "reweightPhotonSFUp/F", "reweightPhotonSFDown/F",
                     "reweightPhotonElectronVetoSF/F",
                     "reweightBTag_SF/F", "reweightBTag_SF_b_Down/F", "reweightBTag_SF_b_Up/F", "reweightBTag_SF_l_Down/F", "reweightBTag_SF_l_Up/F",
                     'reweightL1Prefire/F', 'reweightL1PrefireUp/F', 'reweightL1PrefireDown/F',
                    ]

recoPhotonSel_medium_noSieie = photonSelector( 'medium', year=args.year, removedCuts=["sieie"] )

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

def printWeight( event, sample ):
    print "pref", event.reweightL1Prefire
    print "PU", event.reweightPU
    print "Lep", event.reweightLepton2lSF
    print "LepT", event.reweightLeptonTracking2lSF
    print "PSF", event.reweightPhotonSF
    print "Veto", event.reweightPhotonElectronVetoSF
    print "Btag", event.reweightBTag_SF
    print

def make_Zpt( event, sample ):
    if event.nLeptonGood > 1:
        l0 = ROOT.TLorentzVector()
        l1 = ROOT.TLorentzVector()
        l0.SetPtEtaPhiM( event.LeptonGood0_pt, event.LeptonGood0_eta, event.LeptonGood0_phi, 0 )
        l1.SetPtEtaPhiM( event.LeptonGood1_pt, event.LeptonGood1_eta, event.LeptonGood1_phi, 0 )
        Z = l0 + l1
        event.Z_pt  = Z.Pt()
        event.Z_eta = Z.Eta()
        event.Z_phi = Z.Phi()

    else:
        event.Z_pt  = -999
        event.Z_eta = -999
        event.Z_phi = -999

def printJet(event, sample):
    print event.Jet_neHEF[0]
    print event.Jet_neHEF[1]

recoPhotonSel_mva                        = photonSelector( 'mva',    year=args.year )
def mvaPhotons( event, sample ):
    allPhotons = getCollection( event, 'Photon', photonVarList, 'nPhoton' )
    allPhotons.sort( key = lambda j: -j['pt'] )
    mvaPhotons = list( filter( lambda g: recoPhotonSel_mva(g) and g["mvaID_WP90"], allPhotons ) + [None])[0]

    if mvaPhotons:
        for var in photonVarList:
            setattr( event, "PhotonMVA0_" + var, mvaPhotons[var] )

# Sequence
sequence = [ ]#\
#            clean_Jets,
#            make_Zpt,
#           ]

# Sample definition
if args.year == 2016:
    if args.onlyTTG and not categoryPlot: mc = [ TTG_16 ]
    elif not categoryPlot:
        mc = [ TTG_16, DY_LO_16, TT_pow_16, singleTop_16, ZG_16 ]
        if args.addOtherBg: mc += [ other_16 ]
    elif categoryPlot:
        all = all_16 if args.addOtherBg else all_noOther_16
elif args.year == 2017:
    if args.onlyTTG and not categoryPlot: mc = [ TTG_priv_17 ]
    elif not categoryPlot:
        mc = [ TTG_priv_17, DY_LO_17, TT_pow_17, singleTop_17, ZG_17 ]
        if args.addOtherBg: mc += [ other_17 ]
    elif categoryPlot:
        all = all_17 if args.addOtherBg else all_noOther_17
elif args.year == 2018:
    if args.onlyTTG and not categoryPlot: mc = [ TTG_priv_18 ]
    elif not categoryPlot:
        mc = [ TTG_priv_18, DY_LO_18, TT_pow_18, singleTop_18, ZG_18 ]
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
    elif args.year == 2017: lumi_scale = 41.53
    elif args.year == 2018: lumi_scale = 59.74
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
    sample.weight         = lambda event, sample: event.reweightL1Prefire*event.reweightPU*event.reweightLepton2lSF*event.reweightLeptonTracking2lSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF

if args.small:
    for sample in stack.samples:
        sample.normalization=1.
        sample.reduceFiles( factor=20 )
        sample.scale /= sample.normalization

weight_ = lambda event, sample: event.weight

# Use some defaults (set defaults before you create/import list of Plots!!)
#preSelection = "&&".join( [ cutInterpreter.cutString( args.selection ), "overlapRemoval==1"] )
preSelection = "&&".join( [ cutInterpreter.cutString( args.selection ) ] )
Plot.setDefaults( stack=stack, weight=staticmethod( weight_ ), selectionString=preSelection )#, addOverFlowBin='upper' )

# Import plots list (AFTER setDefaults!!)
plotListFile = os.path.join( os.path.dirname( os.path.realpath( __file__ ) ), 'plotLists', args.plotFile + '.py' )
if not os.path.isfile( plotListFile ):
    logger.info( "Plot file not found: %s", plotListFile )
    sys.exit(1)

plotModule = imp.load_source( "plotLists", os.path.expandvars( plotListFile ) )
if args.noData: from plotLists import plotListDataMC as plotList
else:           from plotLists import plotListData   as plotList

# plotList
addPlots = []

addPlots.append( Plot(
    name      = 'jetGood0_Z_pTRatio_wide',
    texX      = 'p_{T}(jet_{0})/p_{T}(Z)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.JetGood_pt[0] / event.Z_pt if event.nJetGood > 0 and event.Z_pt != -999 else -999,
    binning   = [ 20, 0, 20 ],
))

addPlots.append( Plot(
    name      = 'jetGood0_Z_pTRatio',
    texX      = 'p_{T}(jet_{0})/p_{T}(Z)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.JetGood_pt[0] / event.Z_pt if event.nJetGood > 0 and event.Z_pt != -999 else -999,
    binning   = [ 20, 0, 2 ],
))

addPlots.append( Plot(
    name      = 'jet0_Z_pTRatio_wide',
    texX      = 'p_{T}(jet_{0})/p_{T}(Z)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.Jet_pt[0] / event.Z_pt if event.nJet > 0 and event.Z_pt != -999 else -999,
    binning   = [ 20, 0, 20 ],
))

addPlots.append( Plot(
    name      = 'jet0_Z_pTRatio',
    texX      = 'p_{T}(jet_{0})/p_{T}(Z)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.Jet_pt[0] / event.Z_pt if event.nJet > 0 and event.Z_pt != -999 else -999,
    binning   = [ 20, 0, 2 ],
))

addPlots.append( Plot(
    name      = 'Z_pt',
    texX      = 'p_{T}(Z) (GeV)',
    texY      = 'Number of Events / 20 GeV',
    attribute = lambda event, sample: event.Z_pt,
    binning   = [ 20, 0, 400 ],
))

addPlots.append( Plot(
    name      = 'Z_phi',
    texX      = '#phi(Z)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.Z_phi,
    binning   = [ 10, -pi, pi ],
))

addPlots.append( Plot(
    name      = 'Z_eta',
    texX      = '#eta(Z)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.Z_eta,
    binning   = [ 20, -3, 3 ],
))

# Loop over channels
yields   = {}
allPlots = {}
if args.mode != "None":
    allModes = [ args.mode ]
elif args.nJobs != 1:
    allModes = [ 'mumu', 'mue', 'ee', 'SF', 'all']
    allModes = splitList( allModes, args.nJobs)[args.job]
else:
    allModes = [ 'mumu', 'mue', 'ee' ]

filterCutData = getFilterCut( args.year, isData=True, skipBadChargedCandidate=True )
filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )
tr            = TriggerSelector( args.year, singleLepton="nLepTight1" in args.selection )
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
    plots += plotList
    plots += [ getYieldPlot( index ) ]
#    plots += addPlots

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

    # Overlap removal
#    if any( x.name == "TTG" for x in mc ) and any( x.name == "TT_pow" for x in mc ):
#        eval('TTG_priv_'    + str(args.year)[-2:]).addSelectionString( "isTTGamma==1" )
#        eval('TT_pow_' + str(args.year)[-2:]).addSelectionString( "isTTGamma==0" )

#    if any( x.name == "ZG" for x in mc ) and any( x.name == "DY_LO" for x in mc ):
#        eval('ZG_'    + str(args.year)[-2:]).addSelectionString( "isZWGamma==1" )
#        eval('DY_LO_' + str(args.year)[-2:]).addSelectionString( "isZWGamma==0" )

#    if any( x.name == "WG" for x in mc ) and any( x.name == "WJets" for x in mc ):
#        eval('WG_'    + str(args.year)[-2:]).addSelectionString( "isZWGamma==1" )
#        eval('WJets_' + str(args.year)[-2:]).addSelectionString( "isZWGamma==0" )

#    if any( x.name == "TG" for x in mc ) and any( x.name == "singleTop" for x in mc ):
#        eval('TG_'        + str(args.year)[-2:]).addSelectionString( "isTGamma==1" )
#        eval('singleTop_' + str(args.year)[-2:]).addSelectionString( "isTGamma==0" ) #ONLY IN THE T-channel!!!

    plotting.fill( plots, read_variables=read_variables, sequence=sequence )

    # Get normalization yields from yield histogram
    for plot in plots:
        if plot.name != "yield": continue
        for i, l in enumerate( plot.histos ):
            for j, h in enumerate( l ):
                if mode == "mumu":
                    yields[mode][plot.stack[i][j].name] = h.GetBinContent( h.FindBin( 0.5 ) )
                elif mode == "mue":
                    yields[mode][plot.stack[i][j].name] = h.GetBinContent( h.FindBin( 1.5 ) )
                elif mode == "ee":
                    yields[mode][plot.stack[i][j].name] = h.GetBinContent( h.FindBin( 2.5 ) )
                elif mode == "SF":
                    yields[mode][plot.stack[i][j].name]  = h.GetBinContent( h.FindBin( 0.5 ) )
                    yields[mode][plot.stack[i][j].name] += h.GetBinContent( h.FindBin( 2.5 ) )
                elif mode == "all":
                    yields[mode][plot.stack[i][j].name]  = h.GetBinContent( h.FindBin( 0.5 ) )
                    yields[mode][plot.stack[i][j].name] += h.GetBinContent( h.FindBin( 1.5 ) )
                    yields[mode][plot.stack[i][j].name] += h.GetBinContent( h.FindBin( 2.5 ) )
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

# Add the different channels into SF and all
for mode in [ "SF", "all" ]:
    yields[mode] = {}

    for y in yields[allModes[0]]:
        try:    yields[mode][y] = sum( yields[c][y] for c in ( ['ee','mumu'] if mode=="SF" else ['ee','mumu','mue'] ) )
        except: yields[mode][y] = 0

    dataMCScale = yields[mode]["data"] / yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')

    for plot in allPlots['mumu']:
        for pl in ( p for p in ( allPlots['ee'] if mode=="SF" else allPlots["mue"] ) if p.name == plot.name ):  #For SF add EE, second round add EMu for all
            for i, j in enumerate( list( itertools.chain.from_iterable( plot.histos ) ) ):
                j.Add( list( itertools.chain.from_iterable( pl.histos ) )[i] )

    drawPlots( allPlots['mumu'], mode, dataMCScale )


