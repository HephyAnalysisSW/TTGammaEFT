from RootTools.core.standard import *

from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import Run2016
from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import Run2017
from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import Run2018

RunII      = Sample.combine( "RunII", [Run2016, Run2017, Run2018] ) 
RunII.lumi = Run2016.lumi + Run2017.lumi + Run2018.lumi

lumi_year  = {2016:Run2016.lumi, 2017:Run2017.lumi, 2018:Run2018.lumi}

import TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed as Summer16
import TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed   as Fall17
import TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed as Autumn18

TTG     = Sample.combine( "TTG", [Summer16.TTG, Fall17.TTG, Autumn18.TTG] )
Top     = Sample.combine( "Top", [Summer16.Top, Fall17.Top, Autumn18.Top] )
DY_LO   = Sample.combine( "DY_LO", [Summer16.DY_LO, Fall17.DY_LO, Autumn18.DY_LO] )
WJets   = Sample.combine( "WJets", [Summer16.WJets, Fall17.WJets, Autumn18.WJets] )
WG      = Sample.combine( "WG", [Summer16.WG, Fall17.WG, Autumn18.WG] )
ZG      = Sample.combine( "ZG", [Summer16.ZG, Fall17.ZG, Autumn18.ZG] )
rest    = Sample.combine( "rest", [Summer16.rest, Fall17.rest, Autumn18.rest] )
QCD     = Sample.combine( "QCD", [Summer16.QCD, Fall17.QCD, Autumn18.QCD] )
GJets   = Sample.combine( "GJets", [Summer16.GJets, Fall17.GJets, Autumn18.GJets] )
