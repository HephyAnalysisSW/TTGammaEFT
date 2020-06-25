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
from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter, isoThresh, chgIsoThresh, lowSieieThresh, highSieieThresh
from TTGammaEFT.Tools.TriggerSelector import TriggerSelector
from TTGammaEFT.Tools.Variables       import NanoVariables
from TTGammaEFT.Tools.objectSelection import isBJet, photonSelector, vidNestedWPBitMapNamingListPhoton

from Analysis.Tools.metFilters        import getFilterCut
from Analysis.Tools.helpers           import getCollection, deltaR
from TTGammaEFT.Tools.overlapRemovalTTG import photonFromTopDecay, hasMesonMother, getParentIds, isIsolatedPhoton, getPhotonCategory, hasLeptonMother, getPhotonMother, getAdvancedPhotonCategory

# Default Parameter
loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                     help="Log level for logging")
argParser.add_argument('--plot_directory',     action='store',      default='102X_TTG_ppv28_v1')
argParser.add_argument('--selection',          action='store',      default='dilepOS-nLepVeto2-pTG20-nPhoton1p-offZSFllg-offZSFll-mll40')
argParser.add_argument('--small',              action='store_true',                                                                       help='Run only on a small subset of the data?', )
argParser.add_argument('--year',               action='store',      default="2016",      type=str,  choices=["2016","2017","2018","RunII"],                  help="Which year to plot?")
argParser.add_argument('--onlyTT',             action='store_true', default=False,                                                        help="Plot only tt sample")
argParser.add_argument('--onlyTTLep',          action='store_true', default=False,                                                        help="Plot only tt 2l sample")
argParser.add_argument('--onlyTTSemiLep',      action='store_true', default=False,                                                        help="Plot only tt 1l sample")
argParser.add_argument('--mode',               action='store',      default="None",    type=str, choices=["mu", "e", "mumu", "mue", "ee", "SF", "all", "SFtight", "eetight", "mumutight", "muetight"], help="plot lepton mode" )
argParser.add_argument('--nJobs',              action='store',      default=1,         type=int, choices=[1,2,3,4,5],                        help="Maximum number of simultaneous jobs.")
argParser.add_argument('--job',                action='store',      default=0,         type=int, choices=[0,1,2,3,4],                        help="Run only job i")
argParser.add_argument('--sideband',           action='store',      default="sieie",   type=str, choices=["chgIso", "sieie"],                help="which sideband to plot?")
args = argParser.parse_args()

if args.year != "RunII": args.year = int(args.year)

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small:           args.plot_directory += "_small"

photonVariable = "PhotonNoChgIsoNoSieie0"
# Samples
os.environ["gammaSkim"]="True"
if args.year == 2016:
    import TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed  as mc_samples
    from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import Run2016 as data_sample
elif args.year == 2017:
    import TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed    as mc_samples
    from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import Run2017 as data_sample
elif args.year == 2018:
    import TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed  as mc_samples
    from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import Run2018 as data_sample
elif args.year == "RunII":
    import TTGammaEFT.Samples.nanoTuples_RunII_postProcessed as mc_samples
    from TTGammaEFT.Samples.nanoTuples_RunII_postProcessed import RunII as data_sample

# Text on the plots
def drawObjects( plotData, lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS #bf{#it{Preliminary}}' if plotData else 'CMS #bf{#it{Simulation Preliminary}}'), 
      (0.65, 0.95, '%3.1f fb{}^{-1} (13 TeV)' % lumi_scale)
    ]
    return [tex.DrawLatex(*l) for l in lines] 

# Plotting
def drawPlots( plots, mode ):
    for log in [False, True]:
        sc = ""
        if args.onlyTTLep:     sc += "2l_"
        if args.onlyTTSemiLep: sc += "1l_"
        sc += args.sideband + "_"
        sc += "log" if log else "lin"
        plot_directory_ = os.path.join( plot_directory, 'shapePlots', str(args.year), args.plot_directory, args.selection, mode, sc )

        for plot in plots:
            if not max(l[0].GetMaximum() for l in plot.histos): 
                continue # Empty plot

            scaling = { 1:0, 2:0 }

            plot.histos[0][0].style        = styles.errorStyle( ROOT.kBlack )
            plot.histos[1][0].style        = styles.lineStyle( ROOT.kCyan+2, width = 2, dotted=False, dashed=False, errors = True )
            plot.histos[2][0].style        = styles.lineStyle( ROOT.kRed+2, width = 2, dotted=False, dashed=False, errors = True )

            plotting.draw( plot,
	                       plot_directory = plot_directory_,
                           ratio = {'histos':[(1,0),(2,0)], 'texY': 'Ratio', 'yRange':(0.1,1.9)},
	                       logX = False, logY = log, sorting = False,
	                       yRange = (0.03, "auto") if log else (0.001, "auto"),
	                       scaling = scaling,
	                       legend = [ (0.2,0.87-0.04*sum(map(len, plot.histos)),0.8,0.87), 1],
	                       drawObjects = drawObjects( True , lumi_scale ),
                           copyIndexPHP = True
                         )


# get nano variable lists
NanoVars         = NanoVariables( args.year )
jetVarString     = NanoVars.getVariableString(   "Jet",    postprocessed=True, data=False, plot=True )
jetVariableNames = NanoVars.getVariableNameList( "Jet",    postprocessed=True, data=False, plot=True )
jetVarList       = NanoVars.getVariableNameList( "Jet",    postprocessed=True, data=False, plot=True )
jetVariables     = NanoVars.getVariables(        "Jet",    postprocessed=True, data=False, plot=True )
bJetVariables    = NanoVars.getVariables(        "BJet",   postprocessed=True, data=False, plot=True )
leptonVariables  = NanoVars.getVariables(        "Lepton", postprocessed=True, data=False, plot=True )
leptonVarString  = NanoVars.getVariableString(   "Lepton", postprocessed=True, data=False, plot=True )
leptonVarList    = NanoVars.getVariableNameList( "Lepton", postprocessed=True, data=False, plot=True )
photonVariables  = NanoVars.getVariables(        "Photon", postprocessed=True, data=False, plot=True )
photonVarString  = NanoVars.getVariableString(   "Photon", postprocessed=True, data=False, plot=True )
photonVarList    = NanoVars.getVariableNameList( "Photon", postprocessed=True, data=False, plot=True )
genVariables     = NanoVars.getVariables(        "Gen",    postprocessed=True, data=False,             plot=True )
genVarString     = NanoVars.getVariableString(   "Gen",    postprocessed=True, data=False,             plot=True )
genVarList       = NanoVars.getVariableNameList( "Gen",    postprocessed=True, data=False,             plot=True )

# Read variables and sequences
read_variables  = ["weight/F",
                   'run/I', 'luminosityBlock/I', 'event/l',
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

read_variables_MC = ["isTTGamma/I", "isZWGamma/I", "isTGamma/I", "overlapRemoval/I",
                     "reweightPU/F", "reweightPUDown/F", "reweightPUUp/F", "reweightPUVDown/F", "reweightPUVUp/F",
                     "reweightLeptonTightSF/F", "reweightLeptonTightSFUp/F", "reweightLeptonTightSFDown/F",
                     "reweightLeptonTrackingTightSF/F",
                     "reweightLeptonMediumSF/F", "reweightLeptonMediumSFUp/F", "reweightLeptonMediumSFDown/F",
                     "reweightLeptonTracking2lSF/F",
                     "reweightTrigger/F", "reweightTriggerUp/F", "reweightTriggerDown/F",
                     "reweightInvTrigger/F", "reweightInvTriggerUp/F", "reweightInvTriggerDown/F",
                     "reweightPhotonSF/F", "reweightPhotonSFUp/F", "reweightPhotonSFDown/F",
                     "reweightPhotonElectronVetoSF/F",
                     "reweightBTag_SF/F", "reweightBTag_SF_b_Down/F", "reweightBTag_SF_b_Up/F", "reweightBTag_SF_l_Down/F", "reweightBTag_SF_l_Up/F",
                     'reweightL1Prefire/F', 'reweightL1PrefireUp/F', 'reweightL1PrefireDown/F',
                     "nGenPart/I",
                    ]

photonVariables += ["genPartIdx/I"]
photonVarList   += ["genPartIdx"]
read_variables_MC += map( lambda var: "PhotonGood0_"             + var, photonVariables )
read_variables    += map( lambda var: "JetGood0_"                + var, jetVariables )
read_variables    += map( lambda var: photonVariable + "_"  + var, photonVariables )
read_variables_MC += [ VectorTreeVariable.fromString('GenPart[%s]'%genVarString, nMax=1000) ]

recoPhotonSel_medium    = photonSelector( 'medium', year=args.year )

def checkParentList( event, sample ):
    if sample.name == "data": return

    reco  = {var:getattr(event,photonVariable+"_"+var) for var in photonVarList} 
    gPart = getCollection( event, 'GenPart', genVarList, 'nGenPart' )
    cat   = getAdvancedPhotonCategory( reco, gPart, coneSize=0.2, ptCut=5., excludedPdgIds=[ 12, -12, 14, -14, 16, -16 ] )
    setattr(event,photonVariable+"_photonCat", cat )

# Sequence
sequence = []

# Sample definition
if args.onlyTT: all = mc_samples.TT_pow
elif args.onlyTTLep: all = mc_samples.TT_Lep
elif args.onlyTTSemiLep: all = mc_samples.TT_SemiLep
else: all = mc_samples.all_noQCD

data_sample.scale = 1.

mc_sb = copy.deepcopy(all)
mc_sb.name = "sideband"
mc_sb.texName  = "tt " if args.onlyTT else "MC "
mc_sb.color   = ROOT.kRed+2

mc_fit = copy.deepcopy(all)
mc_fit.name = "fit"
mc_fit.texName  = "tt " if args.onlyTT else "MC "
mc_fit.color   = ROOT.kCyan+2


filterCutData = getFilterCut( args.year, isData=True, skipBadChargedCandidate=True )
filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )

mcSelection = [ filterCutMc, "triggered==1" ]
if not (args.onlyTT or args.onlyTTLep or args.onlyTTSemiLep): mcSelection += [ "overlapRemoval==1" ]

if args.sideband == "chgIso":
    mc_fit.texName += "chg Iso fit region"
    mc_sb.texName += "chg Iso sideband"
elif args.sideband == "sieie":
    mc_fit.texName += "#sigma_{i#etai#eta} fit region"
    mc_sb.texName += "#sigma_{i#etai#eta} sideband"

mc  = [ mc_fit, mc_sb ]

if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74

for sample in mc:
    sample.read_variables = read_variables_MC
    sample.scale          = lumi_scale
    sample.weight         = lambda event, sample: event.reweightTrigger*event.reweightL1Prefire*event.reweightPU*event.reweightLeptonTightSF*event.reweightLeptonTrackingTightSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF

stackSamples  = [[data_sample], [mc_fit], [mc_sb]]
stack = Stack( *stackSamples )

if args.small:
    for sample in stack.samples:
        sample.normalization=1.
        sample.reduceFiles( factor=20 )
        sample.scale /= sample.normalization

weight_ = lambda event, sample: event.weight

# Use some defaults (set defaults before you create/import list of Plots!!)
sel = cutInterpreter.cutString( args.selection )
Plot.setDefaults( stack=stack, weight=staticmethod( weight_ ), selectionString=sel )

# plotList
addPlots = []
isoBinning    = Binning.fromThresholds([0, isoThresh, 20])
chgIsoBinning = Binning.fromThresholds([0, chgIsoThresh, 20])
sieieBinning  = Binning.fromThresholds([0, lowSieieThresh, highSieieThresh, 0.025])

if args.sideband == "chgIso":
  addPlots.append( Plot(
    name      = '%s_sieie_%s_coarse'%(photonVariable, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "%s_sieie/F"%photonVariable ),
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_20ptG120_%s_coarse'%(photonVariable, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, photonVariable + "_sieie" ) if getattr( event, photonVariable + "_pt" ) > 20 and getattr( event, photonVariable + "_pt" ) < 120 else -999,
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_120ptG220_%s_coarse'%(photonVariable, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, photonVariable + "_sieie" ) if getattr( event, photonVariable + "_pt" ) > 120 and getattr( event, photonVariable + "_pt" ) < 220 else -999,
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_220ptGinf_%s_coarse'%(photonVariable, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, photonVariable + "_sieie" ) if getattr( event, photonVariable + "_pt" ) > 220 else -999,
    binning   = sieieBinning,
  ))




if args.sideband == "sieie":
  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_%s_coarse'%(photonVariable, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, photonVariable + "_pfRelIso03_chg" ) * getattr( event, photonVariable + "_pt" ),
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_20ptG120_%s_coarse'%(photonVariable, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, photonVariable + "_pfRelIso03_chg" ) * getattr( event, photonVariable + "_pt" ) if getattr( event, photonVariable + "_pt" ) > 20 and getattr( event, photonVariable + "_pt" ) < 120 else -999,
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_120ptG220_%s_coarse'%(photonVariable, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, photonVariable + "_pfRelIso03_chg" ) * getattr( event, photonVariable + "_pt" ) if getattr( event, photonVariable + "_pt" ) > 120 and getattr( event, photonVariable + "_pt" ) < 220 else -999,
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_220ptGinf_%s_coarse'%(photonVariable, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, photonVariable + "_pfRelIso03_chg" ) * getattr( event, photonVariable + "_pt" ) if getattr( event, photonVariable + "_pt" ) > 220 else -999,
    binning   = chgIsoBinning,
  ))


if args.sideband == "chgIso":
  addPlots.append( Plot(
    name      = '%s_sieie_%s'%(photonVariable, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "%s_sieie/F"%photonVariable ),
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_20ptG120_%s'%(photonVariable, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, photonVariable + "_sieie" ) if getattr( event, photonVariable + "_pt" ) > 20 and getattr( event, photonVariable + "_pt" ) < 120 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_120ptG220_%s'%(photonVariable, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, photonVariable + "_sieie" ) if getattr( event, photonVariable + "_pt" ) > 120 and getattr( event, photonVariable + "_pt" ) < 220 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_220ptGinf_%s'%(photonVariable, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, photonVariable + "_sieie" ) if getattr( event, photonVariable + "_pt" ) > 220 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))




if args.sideband == "sieie":
  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_%s'%(photonVariable, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, photonVariable + "_pfRelIso03_chg" ) * getattr( event, photonVariable + "_pt" ),
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_20ptG120_%s'%(photonVariable, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, photonVariable + "_pfRelIso03_chg" ) * getattr( event, photonVariable + "_pt" ) if getattr( event, photonVariable + "_pt" ) > 20 and getattr( event, photonVariable + "_pt" ) < 120 else -999,
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_120ptG220_%s'%(photonVariable, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, photonVariable + "_pfRelIso03_chg" ) * getattr( event, photonVariable + "_pt" ) if getattr( event, photonVariable + "_pt" ) > 120 and getattr( event, photonVariable + "_pt" ) < 220 else -999,
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_220ptGinf_%s'%(photonVariable, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, photonVariable + "_pfRelIso03_chg" ) * getattr( event, photonVariable + "_pt" ) if getattr( event, photonVariable + "_pt" ) > 220 else -999,
    binning   = [ 20, 0, 20 ],
  ))


# Loop over channels
yields   = {}
allPlots = {}
if args.mode != "None":
    allModes = [ args.mode ]
elif args.nJobs != 1:
    allModes = [ "mu", "e", "all" ]
    allModes = splitList( allModes, args.nJobs)[args.job]
else:
    allModes = [ "mu", "e" ]

for index, mode in enumerate( allModes ):
    logger.info( "Computing plots for mode %s", mode )

    yields[mode] = {}

    # always initialize with [], elso you get in trouble with pythons references!
    plots  = []
    plots += addPlots

    # Define 2l selections
    leptonSelection = cutInterpreter.cutString( mode )

    if args.sideband == "chgIso":
        data_sample.texName = "data (%s) chg Iso fit region"%mode.replace("mu","#mu").replace("all","e+#mu")
        data_sample.setSelectionString( [cutInterpreter.cutString("lowChgIsoNoSieie"), filterCutData, leptonSelection, "triggered==1"] )
        mc_fit.setSelectionString( [cutInterpreter.cutString("lowChgIsoNoSieie"), leptonSelection] + mcSelection )
        mc_sb.setSelectionString( [cutInterpreter.cutString("highChgIsoNoSieie"), leptonSelection] + mcSelection )
    elif args.sideband == "sieie":
        data_sample.texName = "data (%s) #sigma_{i#eta i#eta} fit region"%mode.replace("mu","#mu").replace("all","e+#mu")
        data_sample.setSelectionString( [cutInterpreter.cutString("lowSieieNoChgIso"), filterCutData, leptonSelection, "triggered==1"] )
        mc_fit.setSelectionString( [cutInterpreter.cutString("lowSieieNoChgIso"), leptonSelection] + mcSelection )
        mc_sb.setSelectionString( [cutInterpreter.cutString("highSieieNoChgIso"), leptonSelection] + mcSelection )

    plotting.fill( plots, read_variables=read_variables, sequence=sequence )

    logger.info( "Plotting mode %s", mode )
    allPlots[mode] = copy.deepcopy(plots) # deep copy for creating SF/all plots afterwards!
    drawPlots( allPlots[mode], mode )

if args.mode != "None" or args.nJobs != 1:
    sys.exit(0)

# Add the different channels into SF and all
if "nLepTight2" in args.selection:
    for mode in [ "SF", "all" ]:
        for plot in allPlots['mumu']:
            for pl in ( p for p in ( allPlots['ee'] if mode=="SF" else allPlots["mue"] ) if p.name == plot.name ):  #For SF add EE, second round add EMu for all
                for i, j in enumerate( list( itertools.chain.from_iterable( plot.histos ) ) ):
                    j.Add( list( itertools.chain.from_iterable( pl.histos ) )[i] )

        drawPlots( allPlots['mumu'], mode )

else:
    for plot in allPlots['mu']:
        for pl in ( p for p in allPlots['e'] if p.name == plot.name ):
            for i, j in enumerate( list( itertools.chain.from_iterable( plot.histos ) ) ):
                j.Add( list( itertools.chain.from_iterable( pl.histos ) )[i] )

    drawPlots( allPlots['mu'], "all" )


