import os
from Analysis.Tools.MergingDirDB      import MergingDirDB

expected        = False
cache_directory = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/cache/"
data_key        = "bkgSubtracted_SR3pFine_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_data"
signal_key      = "bkgSubtracted_SR3pFine_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_signal"
signal_stat_key = "bkgSubtracted_SR3pFine_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_signal_stat"
year            = 2016

cache_dir       = os.path.join(cache_directory, "unfolding", str(year), "bkgSubstracted", "expected" if expected else "observed")
dirDB           = MergingDirDB(cache_dir)

data            = dirDB.get( data_key )
signal          = dirDB.get( signal_key )
signal_stat     = dirDB.get( signal_stat_key )

print data, signal, signal_stat
