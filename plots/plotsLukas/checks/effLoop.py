# Standard imports
import ROOT, os, imp, sys, copy
# RootTools
from RootTools.core.standard             import *
import Analysis.Tools.syncer as syncer
from TTGammaEFT.Tools.Variables                  import NanoVariables
from TTGammaEFT.Tools.overlapRemovalTTG          import *
from TTGammaEFT.Tools.objectSelection            import *

# Internal Imports
from TTGammaEFT.Tools.cutInterpreter     import cutInterpreter

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   "INFO", logFile = None)
logger_rt = logger_rt.get_logger("INFO", logFile = None)

data16_dir = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_2016_TTG_private_v49/inclusive"

#ttg160l = Sample.fromDirectory("ttg0l_16", directory = [os.path.join(data16_dir, name) for name in ["TTGHad_LO","TTGHad_ptG100To200_LO","TTGHad_ptG200_LO"]])
#ttg161l = Sample.fromDirectory("ttg1l_16", directory = [os.path.join(data16_dir, name) for name in ["TTGSingleLep_LO","TTGSingleLep_ptG100To200_LO","TTGSingleLep_ptG200_LO"]])
#ttg162l = Sample.fromDirectory("ttg2l_16", directory = [os.path.join(data16_dir, name) for name in ["TTGLep_LO","TTGLep_ptG100To200_LO","TTGLep_ptG200_LO"]])

ttg160l = Sample.fromDirectory("ttg0l_16", directory = [os.path.join(data16_dir, name) for name in ["TTGHad_LO"]])
ttg161l = Sample.fromDirectory("ttg1l_16", directory = [os.path.join(data16_dir, name) for name in ["TTGSingleLep_LO"]])
ttg162l = Sample.fromDirectory("ttg2l_16", directory = [os.path.join(data16_dir, name) for name in ["TTGLep_LO"]])

data17_dir = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_2017_TTG_private_v49/inclusive"

ttg170l = Sample.fromDirectory("ttg0l_17", directory = [os.path.join(data17_dir, name) for name in ["TTGHad_LO","TTGHad_ptG100To200_LO","TTGHad_ptG200_LO"]])
ttg171l = Sample.fromDirectory("ttg1l_17", directory = [os.path.join(data17_dir, name) for name in ["TTGSingleLep_LO","TTGSingleLep_ptG100To200_LO","TTGSingleLep_ptG200_LO"]])
ttg172l = Sample.fromDirectory("ttg2l_17", directory = [os.path.join(data17_dir, name) for name in ["TTGLep_LO","TTGLep_ptG100To200_LO","TTGLep_ptG200_LO"]])

data18_dir = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_2018_TTG_private_v49/inclusive"

ttg180l = Sample.fromDirectory("ttg0l_18", directory = [os.path.join(data18_dir, name) for name in ["TTGHad_LO","TTGHad_ptG100To200_LO","TTGHad_ptG200_LO"]])
ttg181l = Sample.fromDirectory("ttg1l_18", directory = [os.path.join(data18_dir, name) for name in ["TTGSingleLep_LO","TTGSingleLep_ptG100To200_LO","TTGSingleLep_ptG200_LO"]])
ttg182l = Sample.fromDirectory("ttg2l_18", directory = [os.path.join(data18_dir, name) for name in ["TTGLep_LO","TTGLep_ptG100To200_LO","TTGLep_ptG200_LO"]])

#sample = Sample.combine( "ttg", [ttg160l, ttg161l, ttg162l, ttg170l, ttg171l, ttg172l, ttg180l, ttg181l, ttg182l] )
#sample = Sample.combine( "ttg", [ttg160l, ttg161l, ttg162l] )
sample = Sample.combine( "ttg", [ttg161l] )

def convertUnits( coll ):
    for p in coll:
        if abs(p['pdgId'])==11 and isinstance( p['lostHits'], basestring ): p['lostHits']    = ord( p['lostHits'] )
        if abs(p['pdgId'])==13 and isinstance( p['pfIsoId'], basestring ):  p['pfIsoId']     = ord( p['pfIsoId'] )
        if isinstance( p['genPartFlav'], basestring ):             p['genPartFlav'] = ord( p['genPartFlav'] )

selectionString = "overlapRemoval==1"

NanoVars = NanoVariables( 2016 )
readGenVarString      = NanoVars.getVariableString(   "Gen",      postprocessed=True, data=False )
readGenVarList        = NanoVars.getVariableNameList( "Gen",      postprocessed=True, data=False )
readPhotonVarList     = NanoVars.getVariableNameList( "Photon",   postprocessed=True, data=False, skipSyst=True)
readPhotonVarString   = NanoVars.getVariableString(   "Photon",   postprocessed=True, data=False, skipSyst=True)

genLeptonSel_CMSUnfold = genLeptonSelector( "CMSUnfolding" )
genPhotonSel_CMSUnfold = genPhotonSelector( "CMSUnfolding" )

recoPhotonSel_medium    = photonSelector( 'medium', year=2016 )

read_variables = [ TreeVariable.fromString('weight/F'),TreeVariable.fromString('nGenPart/I'),
                   VectorTreeVariable.fromString('GenPart[%s]'%readGenVarString, nMax = 1000) ] # all needed for genMatching
read_variables += [ TreeVariable.fromString('nPhoton/I'),
                    VectorTreeVariable.fromString('Photon[%s]'%readPhotonVarString) ]

# Define a reader
r = sample.treeReader( \
    variables = read_variables,
    selectionString = selectionString,
)
r.start()

nev = 0
tot = 0
noIso = 0
iso = 0
reco = 0
while r.run():
    gPart = getParticles( r.event, collVars=readGenVarList,    coll="GenPart" )
    gPart.sort( key = lambda p: -p['pt'] )

    GenMuon            = filterGenMuons( gPart, status='last' )
    GenElectron        = filterGenElectrons( gPart, status='last' )
    GenLepton          = GenMuon + GenElectron
    GenLeptonCMSUnfold = filter( lambda l: not hasMesonMother( getParentIds( l, gPart ) ), GenLepton )
    GenLeptonCMSUnfold = filter( lambda l: genLeptonSel_CMSUnfold(l), GenLeptonCMSUnfold )

    GenPhoton = filterGenPhotons( gPart, status='last' )
    GenPhotonCMSUnfoldNoIso = filter( lambda g: not hasMesonMother( getParentIds( g, gPart ) ), GenPhoton )
    GenPhotonCMSUnfoldNoIso = filter( lambda g: genPhotonSel_CMSUnfold(g), GenPhotonCMSUnfoldNoIso )

    GenPhotonCMSUnfold = filter( lambda g: isIsolatedPhoton( g, gPart, coneSize=0.1,  ptCut=5, excludedPdgIds=[12,-12,14,-14,16,-16] ), copy.deepcopy(GenPhotonCMSUnfoldNoIso) )

    GenPhotonCMSUnfold = deltaRCleaning( GenPhotonCMSUnfold, GenLeptonCMSUnfold, dRCut=0.4 )

    allPhotons = getParticles( r.event, readPhotonVarList, coll="Photon" )
    allPhotons.sort( key = lambda g: -g['pt'] )
    convertUnits( allPhotons )
    mediumPhotons = list( filter( lambda g: recoPhotonSel_medium(g), allPhotons ) )

    nev += 1
    tot += r.event.weight
    if len(GenPhotonCMSUnfoldNoIso):
        noIso += r.event.weight
    if len(GenPhotonCMSUnfold):
        iso += r.event.weight
    if len(mediumPhotons) and len(GenPhotonCMSUnfold):
        reco += r.event.weight


    if nev > 100000: break

print tot, noIso, iso
print iso*100./noIso
print reco*100./iso
