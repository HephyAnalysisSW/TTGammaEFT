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
from TTGammaEFT.Analysis.SetupHelpers  import *

from Analysis.Tools.metFilters        import getFilterCut
from Analysis.Tools.helpers           import getCollection, deltaR
from Analysis.Tools.overlapRemovalTTG import photonFromTopDecay, hasMesonMother, getParentIds, isIsolatedPhoton, getPhotonCategory, hasLeptonMother, getPhotonMother, getAdvancedPhotonCategory
import Analysis.Tools.syncer as syncer

# Default Parameter
loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']
photonCatChoices = [ "None", "PhotonGood0", "PhotonGood1", "PhotonMVA0", "PhotonNoChgIso0", "PhotonNoSieie0", "PhotonNoChgIsoNoSieie0" ]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                     help="Log level for logging")
argParser.add_argument('--plot_directory',     action='store',      default='102X_TTG_ppv21_v1')
argParser.add_argument('--selection',          action='store',      default='dilepOS-nLepVeto2-pTG20-nPhoton1p-offZSFllg-offZSFll-mll40')
argParser.add_argument('--small',              action='store_true',                                                                       help='Run only on a small subset of the data?', )
argParser.add_argument('--noData',             action='store_true', default=False,                                                        help='also plot data?')
argParser.add_argument('--year',               action='store',      default=None,      type=int,  choices=[2016,2017,2018],                  help="Which year to plot?")
argParser.add_argument('--onlyTT',             action='store_true', default=False,                                                        help="Plot only tt sample")
argParser.add_argument('--onlyTTLep',          action='store_true', default=False,                                                        help="Plot only tt 2l sample")
argParser.add_argument('--onlyTTSemiLep',      action='store_true', default=False,                                                        help="Plot only tt 1l sample")
argParser.add_argument('--normalize',          action='store_true', default=False,                                                        help="normalize shapes")
argParser.add_argument('--categoryPhoton',     action='store',      default="PhotonNoChgIsoNoSieie0", type=str, choices=photonCatChoices,                   help="plot in terms of photon category, choose which photon to categorize!" )
argParser.add_argument('--mode',               action='store',      default="None",    type=str, choices=["mu", "e", "mumu", "mue", "ee", "SF", "all", "SFtight", "eetight", "mumutight", "muetight"], help="plot lepton mode" )
argParser.add_argument('--nJobs',              action='store',      default=1,         type=int, choices=[1,2,3,4,5],                        help="Maximum number of simultaneous jobs.")
argParser.add_argument('--job',                action='store',      default=0,         type=int, choices=[0,1,2,3,4],                        help="Run only job i")
argParser.add_argument('--sideband',           action='store',      default="sieie",   type=str, choices=["iso", "chgIso", "sieie"],                help="which sideband to plot?")
args = argParser.parse_args()

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small:           args.plot_directory += "_small"
if args.noData:          args.plot_directory += "_noData"
if args.normalize:       args.plot_directory += "_normalize"

# Samples
os.environ["gammaSkim"]="True"
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
        plot_directory_ = os.path.join( plot_directory, 'ratioPlots', str(args.year), args.plot_directory, args.selection, mode, sc )

        for plot in plots:
            if not max(l[0].GetMaximum() for l in plot.histos): 
                continue # Empty plot
            postFix = ""
            if args.sideband == "sieie":
                postFix = " (high #sigma_{i#etai#eta})"
            elif args.sideband == "chgIso":
                postFix = " (high chg Iso)"
            plot.histos[0][0].style          = styles.lineStyle( ROOT.kCyan+2, width = 2, dotted=False, dashed=False, errors = True )
            plot.histos[1][0].style          = styles.lineStyle( ROOT.kRed+2, width = 2, dotted=False, dashed=False, errors = True )
            if not args.noData: 
                plot.histos[2][0].style          = styles.errorStyle( ROOT.kBlack )
                if mode == "all":
                    plot.histos[2][0].legendText = "data" + postFix
                if mode == "SF":
                    plot.histos[2][0].legendText = "data (SF)" + postFix
            extensions_ = ["pdf", "png", "root"] if mode in ['all', 'SF', 'mue', "mu", "e"] else ['png']

            scaling = { 0:1 } if args.noData or "_cat" in plot.name else { 0:2, 1:2 } 

            if "_cat" in plot.name:
                pf = plot.name.split("_cat")[1].split("_")[0]
                plot.histos[0][0].legendText     = mc[0].texName + " (%s)"%pf
                plot.histos[1][0].legendText     = mc[1].texName + " (%s)"%pf

            plotting.draw( plot,
	                       plot_directory = plot_directory_,
                           extensions = extensions_,
                           ratio = {'histos':[(0,2), (1,2)] if not args.noData else [(0,1)], 'texY': 'Sig/SB', 'yRange':(0.1,1.9)},
	                       logX = False, logY = log, sorting = False,
	                       yRange = (0.03, "auto") if log else (0.001, "auto"),
	                       scaling = scaling if args.normalize else {},
	                       legend = [ (0.2,0.87-0.04*sum(map(len, plot.histos)),0.8,0.87), 1],
	                       drawObjects = drawObjects( not args.noData , lumi_scale ),
                           copyIndexPHP = True
                         )


# get nano variable lists
NanoVars         = NanoVariables( args.year )
jetVarString     = NanoVars.getVariableString(   "Jet",    postprocessed=True, data=(not args.noData), plot=True )
jetVariableNames = NanoVars.getVariableNameList( "Jet",    postprocessed=True, data=(not args.noData), plot=True )
jetVarList       = NanoVars.getVariableNameList( "Jet",    postprocessed=True, data=(not args.noData), plot=True )
jetVariables     = NanoVars.getVariables(        "Jet",    postprocessed=True, data=(not args.noData), plot=True )
bJetVariables    = NanoVars.getVariables(        "BJet",   postprocessed=True, data=(not args.noData), plot=True )
leptonVariables  = NanoVars.getVariables(        "Lepton", postprocessed=True, data=(not args.noData), plot=True )
leptonVarString  = NanoVars.getVariableString(   "Lepton", postprocessed=True, data=(not args.noData), plot=True )
leptonVarList    = NanoVars.getVariableNameList( "Lepton", postprocessed=True, data=(not args.noData), plot=True )
photonVariables  = NanoVars.getVariables(        "Photon", postprocessed=True, data=(not args.noData), plot=True )
photonVarString  = NanoVars.getVariableString(   "Photon", postprocessed=True, data=(not args.noData), plot=True )
photonVarList    = NanoVars.getVariableNameList( "Photon", postprocessed=True, data=(not args.noData), plot=True )
genVariables     = NanoVars.getVariables(        "Gen",    postprocessed=True, data=False,             plot=True )
genVarString     = NanoVars.getVariableString(   "Gen",    postprocessed=True, data=False,             plot=True )
genVarList       = NanoVars.getVariableNameList( "Gen",    postprocessed=True, data=False,             plot=True )

# Read variables and sequences
read_variables  = ["weight/F",
                   'run/I', 'luminosityBlock/I', 'event/l',
#                   "fixedGridRhoFastjetAll/F",
#                   "fixedGridRhoFastjetCentralChargedPileUp/F",
                   "PV_npvsGood/I",
#                   "Jet[%s]" %jetVarString,
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
                   "nPhotonNoChgIsoNoSieie/I",
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

read_variables += [ "%s_photonCat/I"%item for item in photonCatChoices if item != "None" ]
read_variables += [ "%s_photonCatMagic/I"%item for item in photonCatChoices if item != "None" ]

read_variables_MC = ["isTTGamma/I", "isZWGamma/I", "isTGamma/I", "overlapRemoval/I",
                     "reweightPU/F", "reweightPUDown/F", "reweightPUUp/F", "reweightPUVDown/F", "reweightPUVUp/F",
                     "reweightLeptonTightSF/F", "reweightLeptonTightSFUp/F", "reweightLeptonTightSFDown/F",
                     "reweightLeptonTrackingTightSF/F",
                     "reweightLeptonMediumSF/F", "reweightLeptonMediumSFUp/F", "reweightLeptonMediumSFDown/F",
                     "reweightLeptonTracking2lSF/F",
                     "reweightTrigger/F", "reweightTriggerUp/F", "reweightTriggerDown/F",
                     "reweightInvIsoTrigger/F", "reweightInvIsoTriggerUp/F", "reweightInvIsoTriggerDown/F",
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
read_variables    += map( lambda var: args.categoryPhoton + "_"  + var, photonVariables )
#read_variables_MC += [ VectorTreeVariable.fromString('GenPart[%s]'%genVarString, nMax=1000) ]
recoPhotonSel_medium    = photonSelector( 'medium', year=args.year )

def getPhotons( event, sample ):
    allPhotons = getCollection( event, 'Photon', photonVarList, 'nPhoton' )
    mediumPhotonsNoIsoNoSieie = list( filter( lambda g: recoPhotonSel_medium(g, removedCuts=["pfRelIso03_chg", "pfRelIso03_all", "sieie"]), allPhotons ) )
    mediumPhotonsNoIsoNoSieie.sort( key=lambda x: -x["pt"] )
    for var in photonVarList:
        if mediumPhotonsNoIsoNoSieie:
            setattr( event, args.categoryPhoton+"_"+var, mediumPhotonsNoIsoNoSieie[0][var] )
        else:
            setattr( event, args.categoryPhoton+"_"+var, -999 )



def checkParentList( event, sample ):
    if sample.name == "data": return

    reco  = {var:getattr(event,args.categoryPhoton+"_"+var) for var in photonVarList} 
    gPart = getCollection( event, 'GenPart', genVarList, 'nGenPart' )
    cat   = getAdvancedPhotonCategory( reco, gPart, coneSize=0.2, ptCut=5., excludedPdgIds=[ 12, -12, 14, -14, 16, -16 ] )
    setattr(event,args.categoryPhoton+"_photonCat", cat )


def minDR( event, sample ):
    if sample.name == "data": return

    reco = {var:getattr(event,args.categoryPhoton+"_"+var) for var in photonVarList} 
    allLeptons = getCollection( event, 'Lepton', leptonVarList, 'nLepton' )
    allJets = getCollection( event, 'Jet', jetVarList, 'nJet' )

    event.photonJetdR = min( deltaR( reco, j ) if deltaR( reco, j ) > 0.0005 else 999 for j in allJets )    if allJets    else -1
    event.photonLepdR = min( deltaR( reco, j ) if deltaR( reco, j ) > 0.0005 else 999 for j in allLeptons ) if allLeptons else -1

# Sequence
sequence = []

# Sample definition
if args.onlyTT: all = mc_samples.TT_pow_16
elif args.onlyTTLep: all = mc_samples.TT_Lep_16
elif args.onlyTTSemiLep: all = mc_samples.TT_SemiLep_16
else: all = mc_samples.all_noQCD

all_sb = copy.deepcopy(all)
all_sb.name = "sb"
all_sb.texName  = "tt " if args.onlyTT else "MC "
if args.sideband == "chgIso":
    all_sb.texName += "high chg Iso"
elif args.sideband == "iso":
    all_sb.texName += "high Iso"
elif args.sideband == "sieie":
    all_sb.texName += "high #sigma_{i#etai#eta}"
all_sb.color   = ROOT.kRed+2

all_fit = copy.deepcopy(all_sb)
all_fit.name = "fit"
all_fit.texName  = "tt " if args.onlyTT else "MC "
if args.sideband == "chgIso":
    all_fit.texName += "low chg Iso"
elif args.sideband == "iso":
    all_fit.texName += "low Iso"
elif args.sideband == "sieie":
    all_fit.texName += "low #sigma_{i#etai#eta}"
all_fit.syles    = styles.lineStyle( ROOT.kOrange, width = 2, dotted=False, dashed=False, errors = True )
all_fit.color   = ROOT.kCyan+2

mc  = [ all_fit, all_sb ]
stackSamples  = [ [s] for s in mc ]

if args.noData:
    if args.year == 2016:   lumi_scale = 35.92
    elif args.year == 2017: lumi_scale = 41.53
    elif args.year == 2018: lumi_scale = 59.74
    elif args.year == "RunII": lumi_scale = 35.92 + 41.53 + 59.74
    stack = Stack( *stackSamples )
else:
    data_sample.texName        = "data (legacy)"
    data_sample.name           = "data"
    data_sample.read_variables = [ "event/I", "run/I" ]
    data_sample.scale          = 1
    lumi_scale                 = data_sample.lumi * 0.001
    stackSamples              += [data_sample]

stack = Stack( *stackSamples )

if "Jet2" in args.selection and not "Jet2p" in args.selection:
    misIDSF_val = misID2SF_val
elif "Jet3" in args.selection and not "Jet3p" in args.selection:
    misIDSF_val = misID3SF_val
elif "Jet4" in args.selection and not "Jet4p" in args.selection:
    misIDSF_val = misID4SF_val
elif "Jet5" in args.selection:
    misIDSF_val = misID5SF_val
elif "Jet2p" in args.selection:
    misIDSF_val = misID2pSF_val
elif "Jet3p" in args.selection:
    misIDSF_val = misID3pSF_val
elif "Jet4p" in args.selection:
    misIDSF_val = misID4pSF_val

for sample in mc:
    sample.read_variables = read_variables_MC
    sample.style          = styles.fillStyle( sample.color )
    sample.weight         = lambda event, sample: ((35.92*(event.year==2016)+41.53*(event.year==2017)+59.74*(event.year==2018))*event.reweightHEM*event.reweightTrigger*event.reweightL1Prefire*event.reweightPU*event.reweightLeptonTightSF*event.reweightLeptonTrackingTightSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF)+((event.year==2016)*(event.PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(misIDSF_val[2016].val-1)*(35.92*(event.year==2016)+41.53*(event.year==2017)+59.74*(event.year==2018))*event.reweightHEM*event.reweightTrigger*event.reweightL1Prefire*event.reweightPU*event.reweightLeptonTightSF*event.reweightLeptonTrackingTightSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF)+((event.year==2017)*(event.PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(misIDSF_val[2017].val-1)*(35.92*(event.year==2016)+41.53*(event.year==2017)+59.74*(event.year==2018))*event.reweightHEM*event.reweightTrigger*event.reweightL1Prefire*event.reweightPU*event.reweightLeptonTightSF*event.reweightLeptonTrackingTightSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF)+((event.year==2018)*(event.PhotonNoChgIsoNoSieie0_photonCatMagic==2)*(misIDSF_val[2018].val-1)*(35.92*(event.year==2016)+41.53*(event.year==2017)+59.74*(event.year==2018))*event.reweightHEM*event.reweightTrigger*event.reweightL1Prefire*event.reweightPU*event.reweightLeptonTightSF*event.reweightLeptonTrackingTightSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF)

if args.small:
    for sample in stack.samples:
        sample.normalization=1.
        sample.reduceFiles( factor=20 )
        sample.scale /= sample.normalization

weight_ = lambda event, sample: event.weight

# Use some defaults (set defaults before you create/import list of Plots!!)
preSelection = "&&".join( [ cutInterpreter.cutString( args.selection ) ] )
Plot.setDefaults( stack=stack, weight=staticmethod( weight_ ), selectionString=preSelection )#, addOverFlowBin='upper' )

# plotList
addPlots = []
isoBinning    = Binning.fromThresholds([0, isoThresh, 20])
chgIsoBinning = Binning.fromThresholds([0, chgIsoThresh, 20])
sieieBinning  = Binning.fromThresholds([0, lowSieieThresh, highSieieThresh, 0.025])


if args.sideband == "chgIso" or args.sideband == "iso":
  addPlots.append( Plot(
    name      = '%s_sieie_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "%s_sieie/F"%args.categoryPhoton ),
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_20ptG120_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 else -999,
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_120ptG220_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 else -999,
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_220ptGinf_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 else -999,
    binning   = sieieBinning,
  ))




if args.sideband == "sieie":
  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ),
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_20ptG120_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 else -999,
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_120ptG220_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 else -999,
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_220ptGinf_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 else -999,
    binning   = chgIsoBinning,
  ))




if args.sideband == "chgIso":
  addPlots.append( Plot(
    name      = '%s_sieie_catHad_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 1 else -999,
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catHad_20ptG120_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 1 else -999,
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catHad_120ptG220_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 1 else -999,
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catHad_220ptGinf_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 1 else -999,
    binning   = sieieBinning,
  ))



  addPlots.append( Plot(
    name      = '%s_sieie_catMagic_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 4 else -999,
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catMagic_20ptG120_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 4 else -999,
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catMagic_120ptG220_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 4 else -999,
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catMagic_220ptGinf_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 4 else -999,
    binning   = sieieBinning,
  ))



  addPlots.append( Plot(
    name      = '%s_sieie_catFake_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 3 else -999,
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catFake_20ptG120_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 3 else -999,
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catFake_120ptG220_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 3 else -999,
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catFake_220ptGinf_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 3 else -999,
    binning   = sieieBinning,
  ))



if args.sideband == "sieie":
  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catHad_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 1 else -999,
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catHad_20ptG120_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 1 else -999,
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catHad_120ptG220_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 1 else -999,
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catHad_220ptGinf_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 1 else -999,
    binning   = chgIsoBinning,
  ))


  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catMagic_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 4 else -999,
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catMagic_20ptG120_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 4 else -999,
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catMagic_120ptG220_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 4 else -999,
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catMagic_220ptGinf_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 4 else -999,
    binning   = chgIsoBinning,
  ))


  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catFake_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 3 else -999,
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catFake_20ptG120_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 3 else -999,
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catFake_120ptG220_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 3 else -999,
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catFake_220ptGinf_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 3 else -999,
    binning   = chgIsoBinning,
  ))



if args.sideband == "chgIso" or args.sideband == "iso":
  addPlots.append( Plot(
    name      = '%s_sieie_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "%s_sieie/F"%args.categoryPhoton ),
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_20ptG120_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_120ptG220_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_220ptGinf_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))




if args.sideband == "sieie":
  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ),
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_20ptG120_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 else -999,
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_120ptG220_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 else -999,
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_220ptGinf_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 else -999,
    binning   = [ 20, 0, 20 ],
  ))




if args.sideband == "chgIso" or args.sideband == "iso":
  addPlots.append( Plot(
    name      = '%s_sieie_catHad_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 1 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catHad_20ptG120_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 1 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catHad_120ptG220_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 1 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catHad_220ptGinf_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 1 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))



  addPlots.append( Plot(
    name      = '%s_sieie_catMagic_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 4 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catMagic_20ptG120_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 4 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catMagic_120ptG220_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 4 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catMagic_220ptGinf_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 4 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))




  addPlots.append( Plot(
    name      = '%s_sieie_catFake_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 3 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catFake_20ptG120_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 3 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catFake_120ptG220_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 3 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catFake_220ptGinf_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 3 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))


if args.sideband == "sieie":
  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catHad_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 1 else -999,
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catHad_20ptG120_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 1 else -999,
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catHad_120ptG220_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 1 else -999,
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catHad_220ptGinf_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 1 else -999,
    binning   = [ 20, 0, 20 ],
  ))


  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catMagic_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 4 else -999,
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catMagic_20ptG120_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 4 else -999,
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catMagic_120ptG220_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 4 else -999,
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catMagic_220ptGinf_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 4 else -999,
    binning   = [ 20, 0, 20 ],
  ))


  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catFake_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 3 else -999,
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catFake_20ptG120_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 3 else -999,
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catFake_120ptG220_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 3 else -999,
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catFake_220ptGinf_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCatMagic" ) == 3 else -999,
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

filterCutData = getFilterCut( args.year, isData=True, skipBadChargedCandidate=True )
filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )

if args.sideband == "sieie":
    sb_sel  = ["%s_sieie>%f"%(args.categoryPhoton, highSieieThresh) ] #, "%s_sieie<0.02"%(args.categoryPhoton) ]
    fit_sel = ["%s_sieie<%f"%(args.categoryPhoton, lowSieieThresh)]
elif args.sideband == "chgIso":
    sb_sel  = ["(%s_pfRelIso03_chg*%s_pt)>=%f"%(args.categoryPhoton, args.categoryPhoton, chgIsoThresh)]
    fit_sel = ["(%s_pfRelIso03_chg*%s_pt)<%f"%(args.categoryPhoton, args.categoryPhoton, chgIsoThresh)]
elif args.sideband == "iso":
    sb_sel  = ["(%s_pfRelIso03_all*%s_pt)>=%f"%(args.categoryPhoton, args.categoryPhoton, isoThresh)]
    fit_sel = ["(%s_pfRelIso03_all*%s_pt)<%f"%(args.categoryPhoton, args.categoryPhoton, isoThresh)]

for index, mode in enumerate( allModes ):
    logger.info( "Computing plots for mode %s", mode )

    yields[mode] = {}

    # always initialize with [], elso you get in trouble with pythons references!
    plots  = []
    plots += addPlots

    # Define 2l selections
    leptonSelection = cutInterpreter.cutString( mode )
    mcSelection = [ filterCutMc, leptonSelection, "triggered==1", "pTStitching==1", "overlapRemoval==1" ]

    # sideband/fit region cuts
    if not args.noData: data_sample.setSelectionString( [filterCutData, "triggered==1", leptonSelection, "reweightHEM>0" ] + sb_sel )
    all_sb.setSelectionString( mcSelection + sb_sel )
    all_fit.setSelectionString( mcSelection + fit_sel )

    plotting.fill( plots, read_variables=read_variables, sequence=sequence )

    logger.info( "Plotting mode %s", mode )
    allPlots[mode] = copy.deepcopy(plots) # deep copy for creating SF/all plots afterwards!
    drawPlots( allPlots[mode], mode )

if args.mode != "None" or args.nJobs != 1:
    sys.exit(0)

# Add the different channels into SF and all
for plot in allPlots['mu']:
    for pl in ( p for p in allPlots['e'] if p.name == plot.name ):
        for i, j in enumerate( list( itertools.chain.from_iterable( plot.histos ) ) ):
            j.Add( list( itertools.chain.from_iterable( pl.histos ) )[i] )

drawPlots( allPlots['mu'], "all" )


