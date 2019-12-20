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
#photonCatChoices = [ "None", "PhotonGood0", "PhotonGood1", "PhotonMVA0", "PhotonNoChgIso0", "PhotonNoSieie0", "PhotonNoChgIsoNoSieie0" ]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                     help="Log level for logging")
argParser.add_argument('--plot_directory',     action='store',      default='102X_TTG_ppv20_v1')
argParser.add_argument('--selection',          action='store',      default='nLepTight1-nLepVeto1-nJet4p-nBTag1p-NoChgIsoNoSieiePhoton')
argParser.add_argument('--small',              action='store_true',                                                                       help='Run only on a small subset of the data?', )
argParser.add_argument('--year',               action='store',      default=2016,   type=int,  choices=[2016,2017,2018],                  help="Which year to plot?")
argParser.add_argument('--mode',               action='store',      default="all", type=str, choices=["mu", "e", "mumu", "mue", "ee", "SF", "all"], help="plot lepton mode" )
argParser.add_argument('--nJobs',              action='store',      default=1,      type=int, choices=[1,2,3,4,5],                        help="Maximum number of simultaneous jobs.")
argParser.add_argument('--job',                action='store',      default=0,      type=int, choices=[0,1,2,3,4],                        help="Run only job i")
argParser.add_argument('--useEOS',             action='store_true', default=False,                                                        help="plot from lxplus using EOS" )
args = argParser.parse_args()

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small:           args.plot_directory += "_small"

# Samples
os.environ["gammaSkim"]="True" if ("hoton" in args.selection or "pTG" in args.selection) else "False"
#os.environ["gammaSkim"]="False"
if args.year == 2016:
    if args.useEOS: postprocessing_directory = "2016/MC_v20/semilep/"
    from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed      import *
elif args.year == 2017:
    if args.useEOS: postprocessing_directory = "2017/MC_v20/semilep/"
    from TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed        import *
elif args.year == 2018:
    if args.useEOS: postprocessing_directory = "2018/MC_v20/semilep/"
    from TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed      import *

# Text on the plots
def drawObjects( lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS #bf{#it{Simulation Preliminary}}'), 
      (0.65, 0.95, '%3.1f fb{}^{-1} (13 TeV)' % lumi_scale)
    ]
    return [tex.DrawLatex(*l) for l in lines] 

# Plotting
def drawPlots( plots, mode ):
    for log in [False, True]:
        sc = "log" if log else "lin"
        plot_directory_ = os.path.join( plot_directory, 'fakeRatio', str(args.year), args.plot_directory, args.selection, mode, sc )

        for plot in plots:
            if not max(l[0].GetMaximum() for l in plot.histos): 
                continue # Empty plot

            extensions_ = ["pdf", "png", "root"] if mode in ['all', 'SF', 'mue', "mu", "e"] else ['png']
            plotting.draw( plot,
	                       plot_directory = plot_directory_,
                           extensions = extensions_,
#                           ratio = {'histos':[(0,5),(1,5),(2,5),(3,5),(4,5)] if not args.noData else [(1,0),(2,0),(3,0),(4,0)], 'texY': 'Ratio', 'yRange':(0.1,1.9)},
	                       logX = False, logY = log, sorting = False,
	                       yRange = (0.03, "auto") if log else (0.001, "auto"),
#	                       scaling = scaling,
	                       legend = [ (0.2,0.87-0.04*sum(map(len, plot.histos)),0.8,0.87), 1],
	                       drawObjects = drawObjects( lumi_scale ),
                           copyIndexPHP = True,
                         )


def splitHistos( histo ):
    histList = []
    for i in range( histo.GetNbinsX() ):
        h = histo.Clone()
        for j in range( histo.GetNbinsX() ):
            if i != j: h.SetBinContent(j+1, 0)
        histList.append( h )
    return histList

# get nano variable lists
NanoVars         = NanoVariables( args.year )
jetVarString     = NanoVars.getVariableString(   "Jet",    postprocessed=True, data=False, plot=True )
jetVariableNames = NanoVars.getVariableNameList( "Jet",    postprocessed=True, data=False, plot=True )
bJetVariables    = NanoVars.getVariables(        "BJet",   postprocessed=True, data=False, plot=True )
leptonVariables  = NanoVars.getVariables(        "Lepton", postprocessed=True, data=False, plot=True )
leptonVarString  = NanoVars.getVariableString(   "Lepton", postprocessed=True, data=False, plot=True )
photonVariables  = NanoVars.getVariables(        "Photon", postprocessed=True, data=False, plot=True )
photonVarString  = NanoVars.getVariableString(   "Photon", postprocessed=True, data=False, plot=True )
photonVarList    = NanoVars.getVariableNameList( "Photon", postprocessed=True, data=False, plot=True )

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
                   "reweightHEM/F",
                  ]

read_variables += [ "PhotonNoChgIsoNoSieie0_photonCat/I" ]
read_variables += [ "PhotonGood0_photonCat/I" ]

#read_variables += [ VectorTreeVariable.fromString('Lepton[%s]'%leptonVarString, nMax=10) ]
#read_variables += [ VectorTreeVariable.fromString('Photon[%s]'%photonVarString, nMax=10) ]
#read_variables += [ VectorTreeVariable.fromString('Photon[%s]'%photonVarString, nMax=10) ]
#read_variables += [ VectorTreeVariable.fromString('Jet[%s]'%jetVarString, nMax=10) ]
#read_variables += [ VectorTreeVariable.fromString('JetGood[%s]'%jetVarString, nMax=10) ]

read_variables += map( lambda var: "PhotonNoChgIsoNoSieie0_"  + var, photonVariables )

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
                     "reweightDilepTrigger/F", "reweightDilepTriggerUp/F", "reweightDilepTriggerDown/F",
                     "reweightDilepTriggerBackup/F", "reweightDilepTriggerBackupUp/F", "reweightDilepTriggerBackupDown/F",
                     "reweightPhotonSF/F", "reweightPhotonSFUp/F", "reweightPhotonSFDown/F",
                     "reweightPhotonElectronVetoSF/F",
                     "reweightBTag_SF/F", "reweightBTag_SF_b_Down/F", "reweightBTag_SF_b_Up/F", "reweightBTag_SF_l_Down/F", "reweightBTag_SF_l_Up/F",
                     'reweightL1Prefire/F', 'reweightL1PrefireUp/F', 'reweightL1PrefireDown/F',
                    ]

# Sequence
sequence = [ ]# makePhotons ]#\
#            clean_Jets,
#            make_Zpt,
#           ]

# Sample definition
if args.year == 2016:
    tt = TT_pow_16
    lumi_scale = 35.92
elif args.year == 2017:
    tt = TT_pow_17
    lumi_scale = 41.53
elif args.year == 2018:
    tt = TT_pow_18
    lumi_scale = 59.74

mc = []

pSel = [
    "lowChgIsolowSieie",
    "highChgIsolowSieie",
    "lowChgIsohighSieie",
    "highChgIsohighSieie",
]

colors = [ROOT.kCyan+2, ROOT.kCyan+2, ROOT.kRed+2, ROOT.kRed+2]

for i_var, var in enumerate(pSel):
    locals()["tt_"+var]                = copy.deepcopy(tt)
    locals()["tt_"+var].name           = var
    locals()["tt_"+var].texName        = var.split("ChgIso")[1]
    locals()["tt_"+var].read_variables = read_variables_MC
    locals()["tt_"+var].scale          = lumi_scale
    locals()["tt_"+var].style          = styles.lineStyle( colors[i_var], width=2 )
    locals()["tt_"+var].weight         = lambda event, sample: event.reweightL1Prefire*event.reweightPU*event.reweightLeptonTightSF*event.reweightLeptonTrackingTightSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF
    mc.append( locals()["tt_"+var] )

stackSamples  = [ [s] for s in mc ]
stack = Stack( *stackSamples )

if args.small:
    for sample in stack.samples:
        sample.normalization=1.
        sample.reduceFiles( factor=200 )
        sample.scale /= sample.normalization

weight_ = lambda event, sample: event.weight

preSelection = "&&".join( [ cutInterpreter.cutString( args.selection ) ] )
Plot.setDefaults( stack=stack, weight=staticmethod( weight_ ), selectionString=preSelection )#, addOverFlowBin='upper' )

# plotList
addPlots = []

addPlots.append( Plot(
    name      = 'PhotonNoChgIsoNoSieie00_pt',
    texX      = 'p_{T}(#gamma_{0}) (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "PhotonNoChgIsoNoSieie0_pt/F" ),
    binning   = [ 19, 20, 115 ],
))

addPlots.append( Plot(
    name      = 'nElectronTight',
    texX      = 'N_{e}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nElectronTight/I" ),
    binning   = [ 4, 0, 4 ],
))

addPlots.append( Plot(
    name      = 'nJetGood',
    texX      = 'N_{jet}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nJetGood/I" ),
    binning   = [ 6, 0, 6 ],
))

addPlots.append( Plot(
    name      = 'nBJetGood',
    texX      = 'N_{bJet}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nBTagGood/I" ),
    binning   = [ 4, 0, 4 ],
))


# Loop over channels
if args.mode != "None":
    allModes = [ args.mode ]
elif args.nJobs != 1:
    allModes = [ 'mumu', 'mue', 'ee', 'SF', 'all'] if "dilep" in args.selection else [ "mu", "e", "all" ]
    allModes = splitList( allModes, args.nJobs)[args.job]
else:
    allModes = [ 'mumu', 'mue', 'ee' ] if "dilep" in args.selection else [ "mu", "e" ]

filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )
tr            = TriggerSelector( args.year, singleLepton=True )
triggerCutMc  = tr.getSelection( "MC" )


for index, mode in enumerate( allModes ):
    logger.info( "Computing plots for mode %s", mode )

    # always initialize with [], elso you get in trouble with pythons references!
    plots  = []
#    plots += plotList
#    plots += [ getYieldPlot( index ) ]
    plots += addPlots

    # Define lepton selections
    leptonSelection = cutInterpreter.cutString( mode )
    mcSelection = [ filterCutMc, leptonSelection, triggerCutMc, "overlapRemoval==1" ]

    for var in pSel:
        locals()["tt_"+var].setSelectionString( mcSelection + [cutInterpreter.cutString( var )] )

    plotting.fill( plots, read_variables=read_variables, sequence=sequence )

    for plot in plots:
        sample = plot.stack[0] 
        plot.stack = []
        histos = []
        for i_hist, hist in enumerate(plot.histos): histos.append( splitHistos( hist[0] ) )
        h_lowSieie  = []
        h_highSieie = []
        for i_low, low in enumerate(histos[0]): #lowSieie
            plot.stack.append(sample)
            integral = histos[1][i_low].Integral()
            if integral: low.Scale( 1./ integral )
            else:        low.Scale( 0. )
            low.style = stack.samples[0].style
            h_lowSieie.append( low )
        for i_low, low in enumerate(histos[2]): #lowSieie
            integral = histos[3][i_low].Integral()
            if integral: low.Scale( 1./ integral )
            else:        low.Scale( 0. )
            low.style = stack.samples[2].style
            h_highSieie.append( low )

        plot.histos   = [h_lowSieie, h_highSieie]
#        for i_ph, ph in enumerate(plot.histos):
#            for h in ph:
#                h.style = stack.samples[i_ph].style

#    del plots[0].stack[-1]
#    del plots[0].stack[1]
#    del stack.samples[-1]
#    del stack.samples[1]

    for plot in plots:
        print plot.stack
    logger.info( "Plotting mode %s", mode )
    drawPlots( copy.deepcopy(plots), mode )

