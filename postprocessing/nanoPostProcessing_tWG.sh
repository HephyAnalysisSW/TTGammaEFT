#!/bin/sh

python nanoPostProcessing.py --skim inclusive --year 2016 --processingEra TTGammaEFT_PP_2016_TTG_private_v50 --fileBasedSplitting --isTopSample --sample T_tWch_incl #SPLIT6
python nanoPostProcessing.py --skim inclusive --year 2016 --processingEra TTGammaEFT_PP_2016_TTG_private_v50 --fileBasedSplitting --isTopSample --sample TBar_tWch_incl #SPLIT10
python nanoPostProcessing.py --skim inclusive --year 2017 --processingEra TTGammaEFT_PP_2017_TTG_private_v50 --fileBasedSplitting --isTopSample --sample T_tWch_incl #SPLIT6
python nanoPostProcessing.py --skim inclusive --year 2017 --processingEra TTGammaEFT_PP_2017_TTG_private_v50 --fileBasedSplitting --isTopSample --sample TBar_tWch_incl #SPLIT8
python nanoPostProcessing.py --skim inclusive --year 2018 --processingEra TTGammaEFT_PP_2018_TTG_private_v50 --fileBasedSplitting --isTopSample --sample T_tWch_incl #SPLIT12
python nanoPostProcessing.py --skim inclusive --year 2018 --processingEra TTGammaEFT_PP_2018_TTG_private_v50 --fileBasedSplitting --isTopSample --sample TBar_tWch_incl #SPLIT11
