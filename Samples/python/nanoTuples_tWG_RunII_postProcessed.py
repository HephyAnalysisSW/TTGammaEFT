from RootTools.core.standard import *

import TTGammaEFT.Samples.nanoTuples_tWG_Summer16_private_incl_postProcessed as Summer16
import TTGammaEFT.Samples.nanoTuples_tWG_Fall17_private_incl_postProcessed   as Fall17
import TTGammaEFT.Samples.nanoTuples_tWG_Autumn18_private_incl_postProcessed as Autumn18

ST_tW           = Sample.combine( "ST_tW",          [Summer16.ST_tW, Fall17.ST_tW, Autumn18.ST_tW] )
ST_tW.texName="ST_tW"
