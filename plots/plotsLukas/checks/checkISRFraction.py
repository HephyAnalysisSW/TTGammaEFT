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

# Samples
if args.year == 2016:
    import TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed as mc_samples
elif args.year == 2017:
    import TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed as mc_samples
elif args.year == 2018:
    import TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed as mc_samples
elif args.year == "RunII":
    import TTGammaEFT.Samples.nanoTuples_RunII_postProcessed as mc_samples

# Text on the plots
def drawObjects( lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    line = (0.68, 0.95, '%3.1f fb^{-1} (13 TeV)' % lumi_scale)
    lines = [
      (0.15, 0.95, 'CMS #bf{#it{Simulation Preliminary}}'),
      line
    ]
    return [tex.DrawLatex(*l) for l in lines] 

# Plotting
def drawPlots( plots, mode, dataMCScale ):

    logger.info( "Plotting mode: %s"%mode )

    for log in [False, True]:
        plot_directory_ = os.path.join( plot_directory, 'isrChecks', str(args.year), args.plot_directory )

        for plot in plots:
            postFix = " (%s)"%mode.replace("mu","#mu").replace("all","e+#mu")
            extensions_ = ["pdf", "png", "root"]

            logger.info( "Plotting..." )

            if isinstance( plot, Plot):
                plotting.draw( plot,
	                           plot_directory = plot_directory_,
                               extensions = extensions_,
	                           logX = False, logY = log, sorting = False,
	                           yRange = (0.03, "auto") if log else (0.001, "auto"),
	                           legend = [ (0.15,0.9-0.03*sum(map(len, plot.histos)),0.9,0.9), 2 ],
	                           drawObjects = drawObjects( lumi_scale ),
                               copyIndexPHP = True,
                             )


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


def calcISRPhotons( event, sample ):
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

sequence = [calcISRPhotons]
mc = [ mc_samples.TTG ]

if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74
elif args.year == "RunII": lumi_scale = 35.92 + 41.53 + 59.74
stack = Stack( mc )

lumiString = "(35.92*(year==2016)+41.53*(year==2017)+59.74*(year==2018))"
ws   = "(%s*weight*reweightHEM*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF)"%lumiString
ws16 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2016))" %(ws, misIDSF_val[2016].val)
ws17 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2017))" %(ws, misIDSF_val[2017].val)
ws18 = "+(%s*(PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(%f-1)*(year==2018))" %(ws, misIDSF_val[2018].val)
weightString = ws + ws16 + ws17 + ws18

for sample in mc:# + signals:
    sample.read_variables = read_variables_MC
    sample.scale          = lumi_scale
    sample.style          = styles.fillStyle( sample.color )
    sample.setWeightString( weightString )

weight_ = lambda event, sample: event.weight*event.reweightHEM
preSelection = cutInterpreter.cutString( args.selection )
filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )
triggerCut   = "triggered==1"
print preSelection

Plot.setDefaults(   stack=stack, weight=staticmethod( weight_ ), selectionString=preSelection, addOverFlowBin=None )

# plotList
addPlots = []

addPlots.append( Plot(
    name      = 'misIDElectron0_pt',
    texX      = 'p_{T}(e_{misID}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.MisIDElectron0_pt,
    binning   = [ 20, 0, 120 ],
))


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

