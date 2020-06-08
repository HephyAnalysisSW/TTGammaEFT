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

    est = allProcesses

    if "unfold" in name.lower(): continue
    if "fake" in name.lower(): continue
    if "fine" in name.lower(): continue
    if "vgmis" in name.lower(): continue
    if "eta" in name.lower(): continue
#    if name=="SR2": continue
#    if name=="SR3": continue
#    if name=="SR4p": continue
    if not "SR" in name or "M3" in name: continue

#    if not "3p" in name: continue
#    if not "SR" in name: continue

    for estimator in est:
        opt = option if not "QCD-DD" in estimator else option + " --noSystematics"
        title = " --title est%s_%s"%(year[2:], estimator) if submitCMD.count("submit") else ""

        if not "np" in estimator and not "fake" in estimator and not "hp" in estimator and not "PU" in estimator: continue
#        if not "had" in estimator or "SR" in name: continue # safe time for qcd estimate
#        if not ("had" in estimator and "SR" in name): continue # safe time for qcd estimate
#        if not "QCD-DD" in estimator: continue # safe time for qcd estimate
#        if not "QCD-DD" in estimator and estimator != "DY_LO": continue # safe time for qcd estimate
#        if not "other" in estimator: continue # safe time for qcd estimate
#        if not "DD" in estimator: continue # safe time for qcd estimate
#        if not "DY" in estimator or not cr["noPhotonCR"]: continue # safe time for qcd estimate
#        if not "TTG" in estimator: continue # safe time for qcd estimate
#        if not "ZG" in estimator: continue # safe time for qcd estimate

        photonRegions = cr["inclRegion"] + cr["regions"] if not cr["noPhotonCR"] else cr["regions"]

        nJobs = len(photonRegions)*2
        if "fakes-DD" in estimator: nJobs *= 23

        if submitCMD.count("submit") or submitCMD.count("echo"):
            os.system( submitCMD + title + ' "python run_estimate.py --cores 1 --controlRegion %s --selectEstimator '%(name) + estimator + opt + ' #SPLIT%i"'%nJobs )
            if submitCMD.count("submit"):
                time.sleep(12)
