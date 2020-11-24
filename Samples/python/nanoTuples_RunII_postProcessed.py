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

TTG           = Sample.combine( "TTG",          [Summer16.TTG, Fall17.TTG, Autumn18.TTG] )
TTG.texName="t#bar{t}#gamma"
TTG_TuneUp    = Sample.combine( "TTG_TuneUp",   [Summer16.TTG_TuneUp, Fall17.TTG_TuneUp, Autumn18.TTG_TuneUp] )
TTG_TuneDown  = Sample.combine( "TTG_TuneDown", [Summer16.TTG_TuneDown, Fall17.TTG_TuneDown, Autumn18.TTG_TuneDown] )
TTG_erdOn     = Sample.combine( "TTG_erdOn",    [Summer16.TTG_erdOn, Fall17.TTG_erdOn, Autumn18.TTG_erdOn] )
TTG_QCDbased     = Sample.combine( "TTG_QCDbased",    [Summer16.TTG_QCDbased, Fall17.TTG_QCDbased, Autumn18.TTG_QCDbased] )
TTG_GluonMove     = Sample.combine( "TTG_GluonMove",    [Summer16.TTG_GluonMove, Fall17.TTG_GluonMove, Autumn18.TTG_GluonMove] )
TTG_sys_incl     = Sample.combine( "TTG_sys_incl",    [Summer16.TTG_sys_incl, Fall17.TTG_sys_incl, Autumn18.TTG_sys_incl] )
Top           = Sample.combine( "Top",          [Summer16.Top, Fall17.Top, Autumn18.Top] )
Top.texName="t / t#bar{t}"
TT_pow           = Sample.combine( "TT_pow",          [Summer16.TT_pow, Fall17.TT_pow, Autumn18.TT_pow] )
TT_pow.texName="t#bar{t}"
DY_LO         = Sample.combine( "DY_LO",        [Summer16.DY_LO, Fall17.DY_LO, Autumn18.DY_LO] )
DY_LO.texName="Drell-Yan"
WJets         = Sample.combine( "WJets",        [Summer16.WJets, Fall17.WJets, Autumn18.WJets] )
WJets.texName="W+jets"
WG            = Sample.combine( "WG",           [Summer16.WG, Fall17.WG, Autumn18.WG] )
WG.texName="W#gamma"
WG_NLO            = Sample.combine( "WG_NLO",           [Summer16.WG_NLO, Fall17.WG_NLO, Autumn18.WG_NLO] )
WG_NLO.texName="W#gamma"
ZG            = Sample.combine( "ZG",           [Summer16.ZG, Fall17.ZG, Autumn18.ZG] )
ZG.texName="Z#gamma"
rest          = Sample.combine( "other",        [Summer16.rest, Fall17.rest, Autumn18.rest] )
rest.texName="Other"
QCD           = Sample.combine( "QCD",          [Summer16.QCD, Fall17.QCD, Autumn18.QCD] )
QCD.texName="QCD"
GJets         = Sample.combine( "GJets",        [Summer16.GJets, Fall17.GJets, Autumn18.GJets] )
GJets.texName="#gamma+jets"
GQCD           = Sample.combine( "GQCD",          [Summer16.GQCD, Fall17.GQCD, Autumn18.GQCD] )
GQCD.texName="QCD"
QCD_e           = Sample.combine( "QCD_e",          [Summer16.QCD_e, Fall17.QCD_e, Autumn18.QCD_e] )
QCD_e.texName="QCD_e"
QCD_mu           = Sample.combine( "QCD_mu",          [Summer16.QCD_mu, Fall17.QCD_mu, Autumn18.QCD_mu] )
QCD_mu.texName="QCD_mu"

ST_tW           = Sample.combine( "ST_tW",          [Summer16.ST_tW, Fall17.ST_tW, Autumn18.ST_tW] )
ST_tW.texName="ST_tW"

ST_tch           = Sample.combine( "ST_tch",          [Summer16.ST_tch, Fall17.ST_tch, Autumn18.ST_tch] )
ST_tch.texName="ST_tch"

ST_sch           = Sample.combine( "ST_sch",          [Summer16.ST_sch, Fall17.ST_sch, Autumn18.ST_sch] )
ST_sch.texName="ST_sch"

all_mc           = Sample.combine( "all_mc",          [Summer16.all_mc, Fall17.all_mc, Autumn18.all_mc] )
all_mc.texName="all_mc"
all_noQCD           = Sample.combine( "all_noQCD",          [Summer16.all_noQCD, Fall17.all_noQCD, Autumn18.all_noQCD] )
all_noQCD.texName="all_noQCD"
all_mc_e           = Sample.combine( "all_mc_e",          [Summer16.all_mc_e, Fall17.all_mc_e, Autumn18.all_mc_e] )
all_mc_e.texName="all_mc_e"
all_mc_mu           = Sample.combine( "all_mc_mu",          [Summer16.all_mc_mu, Fall17.all_mc_mu, Autumn18.all_mc_mu] )
all_mc_mu.texName="all_mc_mu"
