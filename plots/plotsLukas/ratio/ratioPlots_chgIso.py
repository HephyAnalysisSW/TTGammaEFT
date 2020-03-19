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
from Analysis.Tools.overlapRemovalTTG import photonFromTopDecay, hasMesonMother, getParentIds, isIsolatedPhoton, getPhotonCategory, hasLeptonMother, getPhotonMother, getAdvancedPhotonCategory

# Default Parameter
loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']
photonCatChoices = [ "None", "PhotonGood0", "PhotonGood1", "PhotonMVA0", "PhotonNoChgIso0", "PhotonNoSieie0", "PhotonNoChgIsoNoSieie0" ]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                     help="Log level for logging")
argParser.add_argument('--plot_directory',     action='store',      default='102X_TTG_ppv21_v1')
#argParser.add_argument('--plotFile',           action='store',      default='all_noPhoton')
argParser.add_argument('--selection',          action='store',      default='dilepOS-nLepVeto2-pTG20-nPhoton1p-offZSFllg-offZSFll-mll40')
argParser.add_argument('--small',              action='store_true',                                                                       help='Run only on a small subset of the data?', )
argParser.add_argument('--year',               action='store',      default=None,      type=int,  choices=[2016,2017,2018],                  help="Which year to plot?")
argParser.add_argument('--onlyTT',             action='store_true', default=False,                                                        help="Plot only tt sample")
argParser.add_argument('--onlyTTLep',          action='store_true', default=False,                                                        help="Plot only tt 2l sample")
argParser.add_argument('--onlyTTSemiLep',      action='store_true', default=False,                                                        help="Plot only tt 1l sample")
argParser.add_argument('--normalize',          action='store_true', default=False,                                                        help="normalize shapes")
#argParser.add_argument('--normalize',          action='store_true', default=False,                                                        help="Normalize yields" )
argParser.add_argument('--addOtherBg',         action='store_true', default=False,                                                        help="add others background" )
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
if args.normalize:       args.plot_directory += "_normalize"

# Samples
os.environ["gammaSkim"]="True"# if ("hoton" in args.selection or "pTG" in args.selection) and not args.invLeptonIso else "False"
if args.year == 2016:
    from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed      import *
elif args.year == 2017:
    from TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed        import *
elif args.year == 2018:
    from TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed      import *

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
            extensions_ = ["pdf", "png", "root"] if mode in ['all', 'SF', 'mue', "mu", "e"] else ['png']

            scaling = { 0:2 }

            if "_cat" in plot.name:
                pf = plot.name.split("_cat")[1].split("_")[0]
                plot.histos[0][0].legendText     = mc[0].texName + " (%s)"%pf
                plot.histos[2][0].legendText     = mc[2].texName + " (%s)"%pf

            plot.histos[0][0].Add(plot.histos[1][0])
            plot.histos[2][0].Add(plot.histos[3][0])

            plot.histos[0][0].style        = styles.lineStyle( ROOT.kCyan+2, width = 2, dotted=False, dashed=False, errors = True )
            plot.histos[2][0].style        = styles.lineStyle( ROOT.kRed+2, width = 2, dotted=False, dashed=False, errors = True )

            plot.histos[1][0].style        = styles.lineStyle( ROOT.kBlack, width = 1 )
            plot.histos[1][0].Scale(0.)
#            plot.histos[1][0].notInLegend  = True
            plot.histos[3][0].style        = styles.lineStyle( ROOT.kBlack, width = 1 )
            plot.histos[3][0].Scale(0.)
#            plot.histos[3][0].notInLegend  = True

            plotting.draw( plot,
	                       plot_directory = plot_directory_,
                           extensions = extensions_,
                           ratio = {'histos':[(0,2)], 'texY': 'Sig/SB', 'yRange':(0.1,1.9)},
	                       logX = False, logY = log, sorting = False,
	                       yRange = (0.03, "auto") if log else (0.001, "auto"),
	                       scaling = scaling if args.normalize else {},
	                       legend = [ (0.2,0.87-0.04*sum(map(len, plot.histos)),0.8,0.87), 1],
	                       drawObjects = drawObjects( False , lumi_scale ),
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

read_variables += [ "%s_photonCat/I"%item for item in photonCatChoices if item != "None" ]

#read_variables += [ VectorTreeVariable.fromString('Lepton[%s]'%leptonVarString, nMax=10) ]
#read_variables += [ VectorTreeVariable.fromString('Photon[%s]'%photonVarString, nMax=10) ]
#read_variables += [ VectorTreeVariable.fromString('Photon[%s]'%photonVarString, nMax=10) ]
#read_variables += [ VectorTreeVariable.fromString('Jet[%s]'%jetVarString, nMax=10) ]
#read_variables += [ VectorTreeVariable.fromString('JetGood[%s]'%jetVarString, nMax=10) ]


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
read_variables    += map( lambda var: args.categoryPhoton + "_"  + var, photonVariables )
read_variables_MC += [ VectorTreeVariable.fromString('GenPart[%s]'%genVarString, nMax=1000) ]
#read_variables_MC += [ "%s_genPartIdx/I"%item for item in photonCatChoices if item != "None" ]
#read_variables_MC += [ "PhotonGood0_genPartIdx/I" ]
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
#sequence = []
sequence = [ checkParentList ]

# Sample definition
if args.year == 2016:
    if args.onlyTT: all = TT_pow_16
    elif args.onlyTTLep: all = TT_Lep_16
    elif args.onlyTTSemiLep: all = TT_SemiLep_16
    elif args.addOtherBg: all = all_16
    else: all = all_noOther_16
elif args.year == 2017:
    if args.onlyTT: all = TT_pow_17
    elif args.onlyTTLep: all = TT_Lep_17
    elif args.onlyTTSemiLep: all = TT_SemiLep_17
    elif args.addOtherBg: all = all_17
    else: all = all_noOther_17
elif args.year == 2018:
    if args.onlyTT: all = TT_pow_18
    elif args.onlyTTLep: all = TT_Lep_18
    elif args.onlyTTSemiLep: all = TT_SemiLep_18
    elif args.addOtherBg: all = all_18
    else: all = all_noOther_18

high_sb = copy.deepcopy(all)
high_sb.name = "high_sb"
high_sb.texName  = "tt " if args.onlyTT else "MC "
if args.sideband == "chgIso":
    high_sb.texName += "high chg Iso"
elif args.sideband == "iso":
    high_sb.texName += "high Iso"
elif args.sideband == "sieie":
    high_sb.texName += "high #sigma_{i#etai#eta}"
high_sb.color   = ROOT.kRed+2

low_sb = copy.deepcopy(all)
low_sb.name = "low_sb"
low_sb.texName = ""
low_sb.color   = ROOT.kRed+2
low_sb.notInLegend  = True

high_fit = copy.deepcopy(all)
high_fit.name = "high_fit"
high_fit.texName  = "tt " if args.onlyTT else "MC "
if args.sideband == "chgIso":
    high_fit.texName += "low chg Iso"
elif args.sideband == "iso":
    high_fit.texName += "low Iso"
elif args.sideband == "sieie":
    high_fit.texName += "low #sigma_{i#etai#eta}"
high_fit.color   = ROOT.kCyan+2

low_fit = copy.deepcopy(all)
low_fit.name = "low_fit"
low_fit.texName = ""
low_fit.color   = ROOT.kCyan+2
low_fit.notInLegend  = True

sel_lSlI = cutInterpreter.cutString( args.selection )
sel_hSlI = cutInterpreter.cutString( args.selection.replace("nPhoton", "nISieiePhoton").replace("nJet","nInvSieieJet").replace("nBTag","nInvSieieBTag") )
sel_lShI = cutInterpreter.cutString( args.selection.replace("nPhoton", "nIChgIsoPhoton").replace("nJet","nInvChgIsoJet").replace("nBTag","nInvChgIsoBTag") )
sel_hShI = cutInterpreter.cutString( args.selection.replace("nPhoton", "nIHadPhoton").replace("nJet","nInvChgIsoInvSieieJet").replace("nBTag","nInvChgIsoInvSieieBTag") )

mc  = [ high_fit, low_fit, high_sb, low_sb ]

if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74

for sample in mc:
    sample.read_variables = read_variables_MC
    sample.scale          = lumi_scale
    if "dilep" in args.selection:
        sample.weight         = lambda event, sample: event.reweightL1Prefire*event.reweightPU*event.reweightLeptonMediumSF*event.reweightLeptonTracking2lSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF
    else:
        sample.weight         = lambda event, sample: event.reweightTrigger*event.reweightL1Prefire*event.reweightPU*event.reweightLeptonTightSF*event.reweightLeptonTrackingTightSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF

if args.small:
    for sample in stack.samples:
        sample.normalization=1.
        sample.reduceFiles( factor=20 )
        sample.scale /= sample.normalization

stackSamples  = [ [s] for s in mc ]
stack = Stack( *stackSamples )

weight_ = lambda event, sample: event.weight

# Use some defaults (set defaults before you create/import list of Plots!!)
#preSelection = "&&".join( [ cutInterpreter.cutString( args.selection ) ] )
Plot.setDefaults( stack=stack, weight=staticmethod( weight_ ), selectionString="(1)" ) #preSelection )#, addOverFlowBin='upper' )

# plotList
addPlots = []
isoBinning    = Binning.fromThresholds([0, isoThresh, 20])
chgIsoBinning = Binning.fromThresholds([0, chgIsoThresh, 20])
sieieBinning  = Binning.fromThresholds([0, lowSieieThresh, highSieieThresh, 0.025])

if True: #not use it for now
  addPlots.append( Plot(
    name      = 'photonLepdR_%s'%("ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'min #DeltaR(#gamma,l)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.photonLepdR if event.photonLepdR > 0 else -999,
    binning   = [40,0,2],
  ))

  addPlots.append( Plot(
    name      = 'photonLepdR_catFake_%s'%("ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'min #DeltaR(#gamma,l)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.photonLepdR if event.photonLepdR > 0 and getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = [40,0,2],
  ))

  addPlots.append( Plot(
    name      = 'photonLepdR_catHad_%s'%("ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'min #DeltaR(#gamma,l)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.photonLepdR if event.photonLepdR > 0 and getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = [40,0,2],
  ))

  addPlots.append( Plot(
    name      = 'photonLepdR_catMagic_%s'%("ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'min #DeltaR(#gamma,l)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.photonLepdR if event.photonLepdR > 0 and getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = [40,0,2],
  ))


  addPlots.append( Plot(
    name      = 'photonJetdR_%s'%("ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'min #DeltaR(#gamma,jet)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.photonJetdR if event.photonLepdR > 0 else -999,
    binning   = [40,0,2],
  ))

  addPlots.append( Plot(
    name      = 'photonJetdR_catFake_%s'%("ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'min #DeltaR(#gamma,jet)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.photonJetdR if event.photonJetdR > 0 and getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = [40,0,2],
  ))

  addPlots.append( Plot(
    name      = 'photonJetdR_catHad_%s'%("ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'min #DeltaR(#gamma,jet)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.photonJetdR if event.photonJetdR > 0 and getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = [40,0,2],
  ))

  addPlots.append( Plot(
    name      = 'photonJetdR_catMagic_%s'%("ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'min #DeltaR(#gamma,jet)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.photonJetdR if event.photonJetdR > 0 and getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = [40,0,2],
  ))

addPlots.append( Plot(
    name      = '%s_mother_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "%s_mother/F"%args.categoryPhoton ),
    binning   = [61,-30,30],
))

addPlots.append( Plot(
    name      = '%s_mother_wide_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "%s_mother/F"%args.categoryPhoton ),
    binning   = [1201,-600,600],
))

if args.sideband == "chgIso" or args.sideband == "iso":
  addPlots.append( Plot(
    name      = '%s_mother_%s_lowSieie'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_sieie" ) < lowSieieThresh else -999,
    binning   = [61,-30,30],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_%s_highSieie'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_sieie" ) > highSieieThresh else -999,
    binning   = [61,-30,30],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_catHad_%s_lowSieie'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_sieie" ) < lowSieieThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = [61,-30,30],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_catHad_%s_highSieie'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_sieie" ) > highSieieThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = [61,-30,30],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_catMagic_%s_lowSieie'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_sieie" ) < lowSieieThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = [61,-30,30],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_catMagic_%s_highSieie'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_sieie" ) > highSieieThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = [61,-30,30],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_catFake_%s_lowSieie'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_sieie" ) < lowSieieThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = [61,-30,30],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_catFake_%s_highSieie'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_sieie" ) > highSieieThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = [61,-30,30],
  ))




  addPlots.append( Plot(
    name      = '%s_mother_wide_%s_lowSieie'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_sieie" ) < lowSieieThresh else -999,
    binning   = [1201,-600,600],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_wide_%s_highSieie'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_sieie" ) > highSieieThresh else -999,
    binning   = [1201,-600,600],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_wide_catHad_%s_lowSieie'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_sieie" ) < lowSieieThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = [1201,-600,600],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_wide_catHad_%s_highSieie'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_sieie" ) > highSieieThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = [1201,-600,600],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_wide_catMagic_%s_lowSieie'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_sieie" ) < lowSieieThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = [1201,-600,600],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_wide_catMagic_%s_highSieie'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_sieie" ) > highSieieThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = [1201,-600,600],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_wide_catFake_%s_lowSieie'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_sieie" ) < lowSieieThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = [1201,-600,600],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_wide_catFake_%s_highSieie'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_sieie" ) > highSieieThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = [1201,-600,600],
  ))




if args.sideband == "sieie":
  addPlots.append( Plot(
    name      = '%s_mother_%s_lowChgIso'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) < chgIsoThresh else -999,
    binning   = [61,-30,30],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_%s_highChgIso'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) > chgIsoThresh else -999,
    binning   = [61,-30,30],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_catHad_%s_lowChgIso'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) < chgIsoThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = [61,-30,30],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_catHad_%s_highChgIso'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) > chgIsoThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = [61,-30,30],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_catMagic_%s_lowChgIso'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) < chgIsoThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = [61,-30,30],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_catMagic_%s_highChgIso'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) > chgIsoThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = [61,-30,30],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_catFake_%s_lowChgIso'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) < chgIsoThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = [61,-30,30],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_catFake_%s_highChgIso'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) > chgIsoThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = [61,-30,30],
  ))





  addPlots.append( Plot(
    name      = '%s_mother_wide_%s_lowChgIso'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) < chgIsoThresh else -999,
    binning   = [1201,-600,600],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_wide_%s_highChgIso'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) > chgIsoThresh else -999,
    binning   = [1201,-600,600],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_wide_catHad_%s_lowChgIso'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) < chgIsoThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = [1201,-600,600],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_wide_catHad_%s_highChgIso'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) > chgIsoThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = [1201,-600,600],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_wide_catMagic_%s_lowChgIso'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) < chgIsoThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = [1201,-600,600],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_wide_catMagic_%s_highChgIso'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) > chgIsoThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = [1201,-600,600],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_wide_catFake_%s_lowChgIso'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) < chgIsoThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = [1201,-600,600],
  ))

  addPlots.append( Plot(
    name      = '%s_mother_wide_catFake_%s_highChgIso'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'mother(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_mother" ) if getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) > chgIsoThresh and getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = [1201,-600,600],
  ))




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
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catHad_20ptG120_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catHad_120ptG220_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catHad_220ptGinf_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = sieieBinning,
  ))



  addPlots.append( Plot(
    name      = '%s_sieie_catMagic_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catMagic_20ptG120_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catMagic_120ptG220_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catMagic_220ptGinf_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = sieieBinning,
  ))



  addPlots.append( Plot(
    name      = '%s_sieie_catFake_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catFake_20ptG120_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catFake_120ptG220_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = sieieBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catFake_220ptGinf_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = sieieBinning,
  ))



if args.sideband == "sieie":
  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catHad_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catHad_20ptG120_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catHad_120ptG220_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catHad_220ptGinf_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = chgIsoBinning,
  ))


  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catMagic_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catMagic_20ptG120_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catMagic_120ptG220_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catMagic_220ptGinf_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = chgIsoBinning,
  ))


  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catFake_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catFake_20ptG120_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catFake_120ptG220_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = chgIsoBinning,
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catFake_220ptGinf_%s_coarse'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
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
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catHad_20ptG120_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catHad_120ptG220_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catHad_220ptGinf_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))



  addPlots.append( Plot(
    name      = '%s_sieie_catMagic_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catMagic_20ptG120_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catMagic_120ptG220_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catMagic_220ptGinf_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))




  addPlots.append( Plot(
    name      = '%s_sieie_catFake_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catFake_20ptG120_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catFake_120ptG220_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catFake_220ptGinf_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))


  addPlots.append( Plot(
    name      = '%s_sieie_catFake_lowPU_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_photonCat" ) == 3 and event.PV_npvsGood < 5 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catFake_medPU_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_photonCat" ) == 3 and event.PV_npvsGood >= 5 and event.PV_npvsGood < 25 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catFake_highPU_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_photonCat" ) == 3 and event.PV_npvsGood >= 25 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))


  addPlots.append( Plot(
    name      = '%s_sieie_catHad_lowPU_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_photonCat" ) == 1 and event.PV_npvsGood < 5 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catHad_medPU_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_photonCat" ) == 1 and event.PV_npvsGood >= 5 and event.PV_npvsGood < 25 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catHad_highPU_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_photonCat" ) == 1 and event.PV_npvsGood >= 25 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))



  addPlots.append( Plot(
    name      = '%s_sieie_catMagic_lowPU_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_photonCat" ) == 4 and event.PV_npvsGood < 5 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catMagic_medPU_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_photonCat" ) == 4 and event.PV_npvsGood >= 5 and event.PV_npvsGood < 25 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))

  addPlots.append( Plot(
    name      = '%s_sieie_catMagic_highPU_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = '#sigma_{i#etai#eta}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_sieie" ) if getattr( event, args.categoryPhoton + "_photonCat" ) == 4 and event.PV_npvsGood >= 25 else -999,
    binning   = [ 20, 0.005, 0.025 ],
  ))





if args.sideband == "sieie":
  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catHad_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catHad_20ptG120_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catHad_120ptG220_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catHad_220ptGinf_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 1 else -999,
    binning   = [ 20, 0, 20 ],
  ))


  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catMagic_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catMagic_20ptG120_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catMagic_120ptG220_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catMagic_220ptGinf_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 4 else -999,
    binning   = [ 20, 0, 20 ],
  ))


  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catFake_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catFake_20ptG120_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 20 and getattr( event, args.categoryPhoton + "_pt" ) < 120 and getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catFake_120ptG220_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 120 and getattr( event, args.categoryPhoton + "_pt" ) < 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = [ 20, 0, 20 ],
  ))

  addPlots.append( Plot(
    name      = '%s_pfIso03_chg_catFake_220ptGinf_%s'%(args.categoryPhoton, "ttOnly" if args.onlyTT else "fullMC"),
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: getattr( event, args.categoryPhoton + "_pfRelIso03_chg" ) * getattr( event, args.categoryPhoton + "_pt" ) if getattr( event, args.categoryPhoton + "_pt" ) > 220 and getattr( event, args.categoryPhoton + "_photonCat" ) == 3 else -999,
    binning   = [ 20, 0, 20 ],
  ))



# Loop over channels
yields   = {}
allPlots = {}
if args.mode != "None":
    allModes = [ args.mode ]
elif args.nJobs != 1:
    allModes = [ 'mumu', 'mue', 'ee', 'SF', 'all'] if "nLepTight2" in args.selection or "dilep" in args.selection else [ "mu", "e", "all" ]
    allModes = splitList( allModes, args.nJobs)[args.job]
else:
    allModes = [ 'mumu', 'mue', 'ee' ] if "nLepTight2" in args.selection or "dilep" in args.selection else [ "mu", "e" ]

filterCutData = getFilterCut( args.year, isData=True, skipBadChargedCandidate=True )
filterCutMc   = getFilterCut( args.year, isData=False, skipBadChargedCandidate=True )
tr            = TriggerSelector( args.year, singleLepton="nLepTight1" in args.selection )
triggerCutMc  = tr.getSelection( "MC" )

for index, mode in enumerate( allModes ):
    logger.info( "Computing plots for mode %s", mode )

    yields[mode] = {}

    # always initialize with [], elso you get in trouble with pythons references!
    plots  = []
    plots += addPlots

    # Define 2l selections
    leptonSelection = cutInterpreter.cutString( mode )
    mcSelection = [ filterCutMc, leptonSelection, triggerCutMc ]
    if not (args.onlyTT or args.onlyTTLep or args.onlyTTSemiLep): mcSelection += [ "overlapRemoval==1" ]

    if args.sideband == "chgIso":
        high_sb.setSelectionString(  mcSelection + [sel_hShI] )
        low_sb.setSelectionString(   mcSelection + [sel_lShI] )
        high_fit.setSelectionString( mcSelection + [sel_hSlI] )
        low_fit.setSelectionString(  mcSelection + [sel_lSlI] )
    elif args.sideband == "sieie":
        high_sb.setSelectionString(  mcSelection + [sel_hShI] )
        low_sb.setSelectionString(   mcSelection + [sel_hSlI] )
        high_fit.setSelectionString( mcSelection + [sel_lShI] )
        low_fit.setSelectionString(  mcSelection + [sel_lSlI] )

    plotting.fill( plots, read_variables=read_variables, sequence=sequence )

    logger.info( "Plotting mode %s", mode )
    allPlots[mode] = copy.deepcopy(plots) # deep copy for creating SF/all plots afterwards!
    drawPlots( allPlots[mode], mode )

if args.mode != "None" or args.nJobs != 1:
    sys.exit(0)

# Add the different channels into SF and all
if "nLepTight2" in args.selection or "dilep" in args.selection:
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


