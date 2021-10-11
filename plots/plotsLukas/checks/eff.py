import os
from RootTools.core.standard          import *
from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter

data16_dir = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_2016_TTG_private_v49/inclusive"

ttg160l = Sample.fromDirectory("ttg0l_16", directory = [os.path.join(data16_dir, name) for name in ["TTGHad_LO","TTGHad_ptG100To200_LO","TTGHad_ptG200_LO"]])
ttg161l = Sample.fromDirectory("ttg1l_16", directory = [os.path.join(data16_dir, name) for name in ["TTGSingleLep_LO","TTGSingleLep_ptG100To200_LO","TTGSingleLep_ptG200_LO"]])
ttg162l = Sample.fromDirectory("ttg2l_16", directory = [os.path.join(data16_dir, name) for name in ["TTGLep_LO","TTGLep_ptG100To200_LO","TTGLep_ptG200_LO"]])

data17_dir = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_2017_TTG_private_v49/inclusive"

ttg170l = Sample.fromDirectory("ttg0l_17", directory = [os.path.join(data17_dir, name) for name in ["TTGHad_LO","TTGHad_ptG100To200_LO","TTGHad_ptG200_LO"]])
ttg171l = Sample.fromDirectory("ttg1l_17", directory = [os.path.join(data17_dir, name) for name in ["TTGSingleLep_LO","TTGSingleLep_ptG100To200_LO","TTGSingleLep_ptG200_LO"]])
ttg172l = Sample.fromDirectory("ttg2l_17", directory = [os.path.join(data17_dir, name) for name in ["TTGLep_LO","TTGLep_ptG100To200_LO","TTGLep_ptG200_LO"]])

data18_dir = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_2018_TTG_private_v49/inclusive"

ttg180l = Sample.fromDirectory("ttg0l_18", directory = [os.path.join(data18_dir, name) for name in ["TTGHad_LO","TTGHad_ptG100To200_LO","TTGHad_ptG200_LO"]])
ttg181l = Sample.fromDirectory("ttg1l_18", directory = [os.path.join(data18_dir, name) for name in ["TTGSingleLep_LO","TTGSingleLep_ptG100To200_LO","TTGSingleLep_ptG200_LO"]])
ttg182l = Sample.fromDirectory("ttg2l_18", directory = [os.path.join(data18_dir, name) for name in ["TTGLep_LO","TTGLep_ptG100To200_LO","TTGLep_ptG200_LO"]])

sample = Sample.combine( "ttg", [ttg160l, ttg161l, ttg162l, ttg170l, ttg171l, ttg172l, ttg180l, ttg181l, ttg182l] )
#sample = Sample.combine( "ttg", [ttg160l, ttg161l, ttg162l] )


sel = "nGenPhotonCMS1"
selection = cutInterpreter.cutString(sel)
selection += "&&pTStitching==1&&overlapRemoval==1"
weight = "weight*(35.92*(year==2016)+41.53*(year==2017)+59.74*(year==2018))"

print selection
print weight

xfid = sample.getYieldFromDraw(selectionString=selection, weightString=weight)["val"]/(35.92+41.53+59.74)
print xfid

sel = "nPhoton1"
selection += "&&"+cutInterpreter.cutString(sel)
#weight += "*reweightPhotonElectronVetoSF*reweightPhotonSF"
print selection
print weight

xrecfid = sample.getYieldFromDraw(selectionString=selection, weightString=weight)["val"]/(35.92+41.53+59.74)
print xrecfid

print xrecfid*100/xfid
