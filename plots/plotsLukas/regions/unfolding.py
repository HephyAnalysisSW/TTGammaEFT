import os
from Analysis.Tools.MergingDirDB      import MergingDirDB

expected        = False
#cache_directory = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache/"
cache_directory = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/"

hists = [
    "SR3pPtUnfold",
    "SR3pAbsEtaUnfold",
    "SR3pdRUnfold",
]

year            = 2016
#year            = "combined"
cache_dir       = os.path.join(cache_directory, "unfolding", str(year), "bkgSubstracted", "expected" if expected else "observed")
dirDB           = MergingDirDB(cache_dir)

if year == "combined": years = [2016,2017,2018]
else: years = [year]

for h in hists:
    for y in years:

        if year == "combined":
            data_key        = "bkgSubtracted_%s_addDYSF_addMisIDSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_data_%i"%(h,y)
            signal_key      = "bkgSubtracted_%s_addDYSF_addMisIDSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_signal_%i"%(h,y)
            signal_stat_key = "bkgSubtracted_%s_addDYSF_addMisIDSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_signal_stat_%i"%(h,y)
        else:
            data_key        = "bkgSubtracted_%s_addDYSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_data"%h
            signal_key      = "bkgSubtracted_%s_addDYSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_signal"%h
            signal_stat_key = "bkgSubtracted_%s_addDYSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_signal_stat"%h

        data            = dirDB.get( data_key )
        signal          = dirDB.get( signal_key )
        signal_stat     = dirDB.get( signal_stat_key )

        print cache_dir
        print h, y
        print data_key
        print signal_key
        print signal_stat_key
        print data, signal, signal_stat

