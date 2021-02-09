from RootTools.core.standard import *

from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import Run2016
from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import Run2017
from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import Run2018

RunII      = Sample.combine( "RunII", [Run2016, Run2017, Run2018] ) 
RunII.lumi = Run2016.lumi + Run2017.lumi + Run2018.lumi

lumi_year  = {2016:Run2016.lumi, 2017:Run2017.lumi, 2018:Run2018.lumi}

import TTGammaEFT.Samples.nanoTuples_Summer16_private_v6_semilep_postProcessed as Summer16
import TTGammaEFT.Samples.nanoTuples_Fall17_private_v6_semilep_postProcessed   as Fall17
import TTGammaEFT.Samples.nanoTuples_Autumn18_private_v6_semilep_postProcessed as Autumn18

TTG           = Sample.combine( "TTG",          [Summer16.TTG, Fall17.TTG, Autumn18.TTG] )
TTG.texName="t#bar{t}#gamma"

TT_pow           = Sample.combine( "TT_pow",          [Summer16.TT_pow, Fall17.TT_pow, Autumn18.TT_pow] )
TT_pow.texName="t#bar{t}"

TTG_NLO           = Sample.combine( "TTG_NLO",          [Summer16.TTG_NLO, Fall17.TTG_NLO, Autumn18.TTG_NLO] )
TTG_NLO.texName="t#bar{t}#gamma"
