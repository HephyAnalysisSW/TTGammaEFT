import os
from Analysis.Tools.MergingDirDB      import MergingDirDB

expected        = False
cache_directory = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/cache/"

#data_key        = "bkgSubtracted_SR3pFine_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_data"
#signal_key      = "bkgSubtracted_SR3pFine_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_signal"
#signal_stat_key = "bkgSubtracted_SR3pFine_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_signal_stat"

#data_key        = "bkgSubtracted_SR3pEtaUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_data"
#signal_key      = "bkgSubtracted_SR3pEtaUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_signal"
#signal_stat_key = "bkgSubtracted_SR3pEtaUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_signal_stat"

data_key        = "bkgSubtracted_SR3pEtaUnfold_addDYSF_mu_SR3pM3_VG3p_misDY3p_addDYSF_data"
signal_key      = "bkgSubtracted_SR3pEtaUnfold_addDYSF_mu_SR3pM3_VG3p_misDY3p_addDYSF_signal"
signal_stat_key = "bkgSubtracted_SR3pEtaUnfold_addDYSF_mu_SR3pM3_VG3p_misDY3p_addDYSF_signal_stat"

#data_key        = "bkgSubtracted_SR3pdPhiUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_data"
#signal_key      = "bkgSubtracted_SR3pdPhiUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_signal"
#signal_stat_key = "bkgSubtracted_SR3pdPhiUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_signal_stat"

#data_key        = "bkgSubtracted_SR3pdRUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_data"
#signal_key      = "bkgSubtracted_SR3pdRUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_signal"
#signal_stat_key = "bkgSubtracted_SR3pdRUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_signal_stat"

#data_key = "bkgSubtracted_SR3pEtaUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_data_2016"
#signal_key = "bkgSubtracted_SR3pEtaUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_signal_2016"
#signal_stat_key = "bkgSubtracted_SR3pEtaUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_signal_stat_2016"

#data_key = "bkgSubtracted_SR3pEtaUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_data_2017"
#signal_key = "bkgSubtracted_SR3pEtaUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_signal_2017"
#signal_stat_key = "bkgSubtracted_SR3pEtaUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_signal_stat_2017"

#data_key = "bkgSubtracted_SR3pEtaUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_data_2018"
#signal_key = "bkgSubtracted_SR3pEtaUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_signal_2018"
#signal_stat_key = "bkgSubtracted_SR3pEtaUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_signal_stat_2018"

year            = 2016 #"combined"

cache_dir       = os.path.join(cache_directory, "unfolding", str(year), "bkgSubstracted", "expected" if expected else "observed")
dirDB           = MergingDirDB(cache_dir)

data            = dirDB.get( data_key )
signal          = dirDB.get( signal_key )
signal_stat     = dirDB.get( signal_stat_key )

print cache_dir
print data, signal, signal_stat

