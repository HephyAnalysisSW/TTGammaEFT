#python nanoPostProcessing.py --skim inclusive --year 2016 --processingEra TTGammaEFT_PP_Sync_TTG_private_v47 --fileBasedSplitting --flagTTBar   --isTopSample --sample TTSingleLep_pow_CP5_sync
#python nanoPostProcessing.py --skim inclusive --year 2016 --processingEra TTGammaEFT_PP_Sync_TTG_private_v47 --fileBasedSplitting --flagDYWJets --sample DYJetsToLL_M50_LO_ext1_sync

python nanoPostProcessing.py --skim inclusive --year 2016 --processingEra TTGammaEFT_PP_Sync_TTG_private_v47 --fileBasedSplitting --flagTTGamma --isTopSample --sample TTGSingleLep_LO_sync
python nanoPostProcessing.py --skim inclusive --year 2016 --processingEra TTGammaEFT_PP_Sync_TTG_private_v47 --fileBasedSplitting --flagQCD --isTopSample --sample QCD_Mu_pt170to300_sync
python nanoPostProcessing.py --skim inclusive --year 2016 --processingEra TTGammaEFT_PP_Sync_TTG_private_v47 --fileBasedSplitting --flagQCD --isTopSample --sample QCD_Ele_pt170to300_sync
python nanoPostProcessing.py --skim inclusive --year 2016 --processingEra TTGammaEFT_PP_Sync_TTG_private_v47 --fileBasedSplitting --flagDYWJets --isTopSample --sample W3JetsToLNu_sync
