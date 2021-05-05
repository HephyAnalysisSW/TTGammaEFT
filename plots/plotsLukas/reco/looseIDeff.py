#!/usr/bin/env python
''' Analysis script for standard plots
'''

# Standard imports
import ROOT, os, sys
ROOT.gROOT.SetBatch(True)
from math                             import pi, sqrt

# RootTools
from RootTools.core.standard          import *

from TTGammaEFT.Tools.Variables                  import NanoVariables
# Internal Imports
from TTGammaEFT.Tools.user            import plot_directory, cache_directory
from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter
from TTGammaEFT.Tools.overlapRemovalTTG import getParentIds

from Analysis.Tools.helpers           import getCollection, deltaR

# Default Parameter
loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO', nargs='?', choices=loggerChoices,                  help="Log level for logging")
argParser.add_argument('--plot_directory',     action='store',      default='myFirstPlots')
argParser.add_argument('--small',              action='store_true',                                                                    help='Run only on a small subset of the data?', )
argParser.add_argument('--year',               action='store',      default=2016,   type=int,  choices=[2016,2017,2018],               help="Which year to plot?")
argParser.add_argument('--mode',               action='store',      default="all",   type=str,  choices=["e","mu","all"],               help="Which mode to plot?")
args = argParser.parse_args()

#selection = cutInterpreter.cutString( "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1" )
#selection += "&&"+"nLeptonTight==1&&(1)&&nLeptonVetoIsoCorr==1&&nJetGood>=3&&nBTagGood>=1&&nPhotonGood>=1&&nPhotonGood<=1&&nPhotonNoChgIsoNoSieie>=1&&nPhotonNoChgIsoNoSieie<=1&&triggered==1&&reweightHEM>0&&overlapRemoval==1&&pTStitching==1&&Flag_goodVertices&&Flag_globalSuperTightHalo2016Filter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_BadPFMuonFilter&&PV_ndof>4&&sqrt(PV_x*PV_x+PV_y*PV_y)<=2&&abs(PV_z)<=24"
if args.mode == "e":
    lep = "abs(GenPart_pdgId)==11&&(abs(GenPart_eta)<1.4442||abs(GenPart_eta)>1.566)"
    recolep = "Sum$(Lepton_cutBased>=1&&abs(Lepton_pdgId)==11&&Lepton_pt>=15&&abs(Lepton_eta)<=2.4&&(abs(Lepton_eta)<1.4442||abs(Lepton_eta)>1.566))>=1"
elif args.mode == "mu":
    lep = "abs(GenPart_pdgId)==13"
    recolep = "Sum$((Lepton_isTracker||Lepton_isGlobal)&&Lepton_isPFcand&&abs(Lepton_pdgId)==13&&Lepton_pt>=15&&abs(Lepton_eta)<=2.4)==1"
elif args.mode == "all":
    lep = "(abs(GenPart_pdgId)==11||abs(GenPart_pdgId)==13)"
    recolep = "(Sum$(Lepton_cutBased>=1&&abs(Lepton_pdgId)==11&&Lepton_pt>=15&&abs(Lepton_eta)<=2.4)==1||Sum$((Lepton_isTracker||Lepton_isGlobal)&&Lepton_isPFcand&&abs(Lepton_pdgId)==13&&Lepton_pt>=15&&abs(Lepton_eta)<=2.4)==1)"
#selection = "overlapRemoval==1&&pTStitching==1&&Sum$(%s&&GenPart_pt>=15&&GenPart_status==1&&abs(GenPart_eta)<=2.4)==1"%lep
selection = "pTStitching==1&&Sum$(%s&&GenPart_pt>=15&&GenPart_status==1&&abs(GenPart_eta)<=2.4)==1"%lep

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

# load samples
# we have a photon skim (smaller samples if you plot a selection containing a photon)
# Set it to "True" if you want to use it, which will make the plot script much faster
# can only be used if you have a selection with at least one photon
os.environ["gammaSkim"]="True"
if args.year == 2016:
    import TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed as mc_samples

elif args.year == 2017:
    import TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed as mc_samples

elif args.year == 2018:
    import TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed as mc_samples

elif args.year == "RunII":
    import TTGammaEFT.Samples.nanoTuples_RunII_postProcessed as mc_samples

#print mc_samples.TTG.getYieldFromDraw(selectionString=selection, weightString="weight")
#print mc_samples.TTG.getYieldFromDraw(selectionString=selection+"&&"+recolep, weightString="weight")
mc_samples.TT_SemiLep.files = mc_samples.TT_SemiLep.files[:2]

print mc_samples.TT_SemiLep.getYieldFromDraw(selectionString=selection, weightString="weight")
print mc_samples.TT_SemiLep.getYieldFromDraw(selectionString=selection+"&&"+recolep, weightString="weight")



sys.exit()




# add here variables that should be read by all samples
read_variables  = ["weight/F",
                   "PV_npvsGood/I",
                   "PV_npvs/I", "PV_npvsGood/I",
                   "nJetGood/I", "nBTagGood/I",
                   "nLeptonTight/I", "nElectronTight/I", "nMuonTight/I",
                   "nPhotonGood/I",
                   "Photon[pt/F,eta/F,phi/F]",
                   "MET_pt/F", "MET_phi/F", "ht/F",
                   "mLtight0Gamma/F",
                   "m3/F", "mT/F",
                  ]

NanoVars = NanoVariables( 2016 )
readGenVarString      = NanoVars.getVariableString(   "Gen",      postprocessed=True, data=False )
readGenVarString = readGenVarString.replace("index/I,","")
variables = ["pt/F","eta/F","phi/F","pdgId/I","genPartIdxMother/I"]

# add here variables that should be read only for MC samples
read_variables_MC = ["overlapRemoval/I",
                     'nGenElectronCMSUnfold/I', 'nGenMuonCMSUnfold/I', 'nGenLeptonCMSUnfold/I', 'nGenPhotonCMSUnfold/I', 'nGenBJetCMSUnfold/I', 'nGenJetsCMSUnfold/I', 'nGenPart/I',
                     "reweightTrigger/F", "reweightPU/F", "reweightLeptonTightSF/F", "reweightLeptonTrackingTightSF/F", "reweightPhotonSF/F", "reweightPhotonElectronVetoSF/F", "reweightBTag_SF/F", 'reweightL1Prefire/F',
                    ]

read_variables_MC += map( lambda var: "GenLeptonCMSUnfold0_"  + var, variables )
#read_variables_MC += map( lambda var: "GenPart_"  + var, variables )
read_variables_MC += [ VectorTreeVariable.fromString('GenPart[%s]'%readGenVarString, nMax=300) ]

taus = 0
notaus = 0
total = 0
wtaus = 0
wnotaus = 0
wtotal = 0
# example of how to calculate your own variables
def sequenceExample( event, sample ):
    global taus, notaus, total, wtaus, wnotaus, wtotal, mcWeight
    # get all photons
    gPart  = getCollection( event, 'GenPart', ["pt","eta","phi","pdgId","genPartIdxMother"], 'nGenPart' )
    genLep = filter( lambda g: g["pt"]>=15 and abs(g["eta"])<=2.4, gPart )
    genE = filter( lambda g: abs(g["pdgId"])==11, genLep )
    genMu = filter( lambda g: abs(g["pdgId"])==13, genLep )

    recoLep  = getCollection( event, 'Lepton', ["pt","eta","phi","pdgId","isTracker", "isGlobal", "isPFcand", ""], 'nLepton' )


    selection = "overlapRemoval==1&&pTStitching==1&&Sum$(%s&&GenPart_pt>=15&&abs(GenPart_eta)<=2.4)==1"%lep
    lep = {"pt":event.GenLeptonCMSUnfold0_pt,"eta":event.GenLeptonCMSUnfold0_eta,"phi":event.GenLeptonCMSUnfold0_phi,"pdgId":event.GenLeptonCMSUnfold0_pdgId, "genPartIdxMother":event.GenLeptonCMSUnfold0_genPartIdxMother}
    ids = map( abs, getParentIds( lep, gPart ) )
    if 15 in ids:
        taus += 1
        wtaus += mcWeight( event, sample )
    else:
        notaus += 1
        wnotaus += mcWeight( event, sample )
    total +=1
    wtotal += mcWeight( event, sample )

# add functions to calculate your own variables here
# this is slow, use it only if needed
sequence = [ sequenceExample ]

# MC samples need to be corrected by certain scale factors to correct e.g. detector effects. Define the "weight" here:
mcWeight = lambda event, sample: event.reweightTrigger*event.reweightL1Prefire*event.reweightPU*event.reweightLeptonTightSF*event.reweightLeptonTrackingTightSF*event.reweightPhotonSF*event.reweightPhotonElectronVetoSF*event.reweightBTag_SF

# Sample definition
mc = [ mc_samples.TTG ]

# Scale the histograms by the luminosity taken by CMS in each year
if args.year == 2016:   lumi_scale = 35.92
elif args.year == 2017: lumi_scale = 41.53
elif args.year == 2018: lumi_scale = 59.74
# add all samples to the Stack
stack = Stack( mc )

if args.small:
    for sample in stack.samples:
        sample.reduceFiles( factor=20 )


# settings for MC Samples
for sample in mc:
    # add here variables that should be read only for MC samples
    sample.read_variables = read_variables_MC
    # set additional cuts specific for MC
    # overlapremoval for separating samples with and without a photon (e.g. ttbar from ttgamma)
    # you can scale the histograms of each sample by defining sample.scale (don't scale data)
    # Scale the MC histograms by the luminosity taken by CMS in each year
    sample.scale          = lumi_scale
    # change the style of the MC sample (filled histograms)
    # the color is defined where mc samples are defined
    sample.style          = styles.fillStyle( sample.color )
    # add the predefined weight to the samples

# set default settings for your plots (weight, selection, do you want an overflow bin?)
Plot.setDefaults(   stack=stack, weight=staticmethod( mcWeight ), selectionString=selection, addOverFlowBin="upper" )

# define a list of plots here
plotList = []

plotList.append( Plot(
    name      = 'GenLeptonCMSUnfold0_pt', # name of the plot file
    texX      = 'p_{T}(l_{0}) (GeV)', # x axis label
    texY      = 'Number of Events', # y axis label
    attribute = lambda event, sample: event.GenLeptonCMSUnfold0_pt, # variable to plot
    binning   = [ 20, 20, 420 ], # 20 bins from 20 to 120
))

# fill the histograms here, depending on the selection this can take a while
# here you also say which plots you want to fill (plots), which variables they need (read_variables) and which additionl functions to call for each event (sequence)
plotting.fill( plotList, read_variables=read_variables, sequence=sequence )

print "tau", "notau", "total"
print taus, notaus, total
print "weighted", "tau", "notau", "total"
print wtaus, wnotaus, wtotal

# print the plots
#drawPlots( plotList )

