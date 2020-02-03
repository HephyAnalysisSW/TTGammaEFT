#!/usr/bin/env python
import os, time, copy

from TTGammaEFT.Analysis.SetupHelpers import *
from TTGammaEFT.Analysis.regions      import regionsTTG, inclRegionsTTG, noPhotonRegionTTG

allPhotonRegions = regionsTTG
year = "2016"

# Here, all the estimators are defined, if empty: CR specific estimators are used
estimators = []

#submitCMD = "submitBatch.py --dpm "
submitCMD = "echo "
#submitCMD = ""

option  = ""
#option += " --noSystematics"
option += " --year " + year
#option += " --overwrite"
#option += " --checkOnly"
#option += " --createExecFile"

crs       = allRegions

for name, cr in crs.items():

    est = copy.copy(estimators)
    if not est and not "processes" in cr: est = default_sampleList
    elif not est:                         est = [ e for eList in cr["processes"].values() for e in eList["process"] ] + ["Data"]

#    if not "3p" in name: continue
#    if not "EtaUnfold" in name: continue
#    if "fake" in name: continue
#    if "fine" in name: continue
#    if "eta" in name: continue
#    if not cr["noPhotonCR"]: continue # safe time for qcd estimate

    for estimator in est:
        opt = option if not "DD" in estimator else option + " --noSystematics"
        title = " --title est%s_%s"%(year[2:], estimator) if submitCMD.count("submit") else ""

#        if not "DD" in estimator: continue # safe time for qcd estimate
#        if not "Data" in estimator: continue # safe time for qcd estimate
#        if not "DD" in estimator and not "Data" in estimator: continue # safe time for qcd estimate
#        if not "DY" in estimator or not cr["noPhotonCR"]: continue # safe time for qcd estimate
#        if not "TTG" in estimator: continue # safe time for qcd estimate
        if not "WG" in estimator: continue # safe time for qcd estimate

        photonRegions = cr["inclRegion"] + cr["regions"] if not cr["noPhotonCR"] else cr["regions"]

        for j, region in enumerate( photonRegions ):
            if submitCMD.count("submit") or submitCMD.count("echo"):
                os.system( submitCMD + title + ' "python run_estimate.py --cores 1 --selectRegion %i --controlRegion %s --selectEstimator '%(j,name) + estimator + opt + '"' )
                if submitCMD.count("submit"):
                    time.sleep(12)
