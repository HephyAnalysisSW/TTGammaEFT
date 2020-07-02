#!/bin/sh
python nanoPostProcessing.py --skim inclusive --year 2016 --processingEra TTGammaEFT_PP_2016_TTG_private_v47 --fileBasedSplitting --flagTTGamma --isTopSample --sample TTGHad_LO #SPLIT10
python nanoPostProcessing.py --skim inclusive --year 2016 --processingEra TTGammaEFT_PP_2016_TTG_private_v47 --fileBasedSplitting --flagTTGamma --isTopSample --sample TTGSingleLep_LO #SPLIT14
python nanoPostProcessing.py --skim inclusive --year 2016 --processingEra TTGammaEFT_PP_2016_TTG_private_v47 --fileBasedSplitting --flagTTGamma --isTopSample --sample TTGLep_LO #SPLIT5
python nanoPostProcessing.py --skim inclusive --year 2016 --processingEra TTGammaEFT_PP_2016_TTG_private_v47 --fileBasedSplitting --flagTTBar --isTopSample --sample TTLep_pow_CP5 #SPLIT40
python nanoPostProcessing.py --skim inclusive --year 2016 --processingEra TTGammaEFT_PP_2016_TTG_private_v47 --fileBasedSplitting --flagTTBar --isTopSample --sample TTSingleLep_pow_CP5 #SPLIT55
python nanoPostProcessing.py --skim inclusive --year 2016 --processingEra TTGammaEFT_PP_2016_TTG_private_v47 --fileBasedSplitting --flagTTBar --isTopSample --sample TTHad_pow_CP5 #SPLIT55

#python nanoPostProcessing.py --skim inclusive --year 2017 --processingEra TTGammaEFT_PP_2017_TTG_private_v46 --fileBasedSplitting --flagTTGamma --isTopSample --sample TTGHad_LO #SPLIT8
#python nanoPostProcessing.py --skim inclusive --year 2017 --processingEra TTGammaEFT_PP_2017_TTG_private_v46 --fileBasedSplitting --flagTTGamma --isTopSample --sample TTGSingleLep_LO #SPLIT17
#python nanoPostProcessing.py --skim inclusive --year 2017 --processingEra TTGammaEFT_PP_2017_TTG_private_v46 --fileBasedSplitting --flagTTGamma --isTopSample --sample TTGLep_LO #SPLIT7
#python nanoPostProcessing.py --skim inclusive --year 2017 --processingEra TTGammaEFT_PP_2017_TTG_private_v46 --fileBasedSplitting --flagTTBar --isTopSample --sample TTLep_pow #SPLIT11
#python nanoPostProcessing.py --skim inclusive --year 2017 --processingEra TTGammaEFT_PP_2017_TTG_private_v46 --fileBasedSplitting --flagTTBar --isTopSample --sample TTSingleLep_pow #SPLIT46
#python nanoPostProcessing.py --skim inclusive --year 2017 --processingEra TTGammaEFT_PP_2017_TTG_private_v46 --fileBasedSplitting --flagTTBar --isTopSample --sample TTHad_pow #SPLIT60
#
#python nanoPostProcessing.py --skim inclusive --year 2018 --processingEra TTGammaEFT_PP_2018_TTG_private_v46 --fileBasedSplitting --flagTTGamma --isTopSample --sample TTGHad_LO #SPLIT7
#python nanoPostProcessing.py --skim inclusive --year 2018 --processingEra TTGammaEFT_PP_2018_TTG_private_v46 --fileBasedSplitting --flagTTGamma --isTopSample --sample TTGSingleLep_LO #SPLIT20
#python nanoPostProcessing.py --skim inclusive --year 2018 --processingEra TTGammaEFT_PP_2018_TTG_private_v46 --fileBasedSplitting --flagTTGamma --isTopSample --sample TTGLep_LO #SPLIT10
#python nanoPostProcessing.py --skim inclusive --year 2018 --processingEra TTGammaEFT_PP_2018_TTG_private_v46 --fileBasedSplitting --flagTTBar --isTopSample --sample TTLep_pow #SPLIT40
#python nanoPostProcessing.py --skim inclusive --year 2018 --processingEra TTGammaEFT_PP_2018_TTG_private_v46 --fileBasedSplitting --flagTTBar --isTopSample --sample TTSingleLep_pow #SPLIT40
#python nanoPostProcessing.py --skim inclusive --year 2018 --processingEra TTGammaEFT_PP_2018_TTG_private_v46 --fileBasedSplitting --flagTTBar --isTopSample --sample TTHad_pow #SPLIT40
