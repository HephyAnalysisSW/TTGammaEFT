#!/usr/bin/env python
import os, time, copy

from TTGammaEFT.Analysis.SetupHelpers import *
from TTGammaEFT.Analysis.regions      import regionsTTG, inclRegionsTTG, noPhotonRegionTTG

allPhotonRegions = regionsTTG
year = "2016"

# Here, all the estimators are defined, if empty: CR specific estimators are used
#estimators  = default_sampleList
#estimators = ["WJets"]
#estimators = ["QCD-DD"]
#estimators = ["DY_LO"]
#estimators = ["Data"]
estimators = []

#submitCMD = "submitBatch.py --dpm "
submitCMD = "echo "
#submitCMD = ""

option  = ""
#option += " --noSystematics"
option += " --year " + year
option += " --overwrite"
#option += " --checkOnly"
#option += " --createExecFile"

#regions  = signalRegions
#crs  = controlRegions
crs       = allRegions
#crs       = {"DY3":allRegions["DY3"], "DY4p":allRegions["DY4p"]}
#crs       = {"VG3":allRegions["VG3"], "VG4p":allRegions["VG4p"], "misDY3":allRegions["misDY3"], "misDY4p":allRegions["misDY4p"], "DY3":allRegions["DY3"], "DY4p":allRegions["DY4p"]}
#crs       = {"SR4pIso":allRegions["SR4pIso"], "SR4pM3":allRegions["SR4pM3"], "VG3":allRegions["VG3"], "misDY3":allRegions["misDY3"], "VG5":allRegions["VG5"], "VG2":allRegions["VG2"], "VG4":allRegions["VG4"]}
#
#crs       = {"SR4pIso":allRegions["SR4pIso"], "SR4pM3":allRegions["SR4pM3"], "SR3Iso":allRegions["SR3Iso"], "SR3M3":allRegions["SR3M3"]}
#crs       = {"SR4poffM3":allRegions["SR4poffM3"]}
#crs.update({"SR4ponM3":allRegions["SR4ponM3"], "SR4poffM3":allRegions["SR4poffM3"], "SR4plowIso":allRegions["SR4plowIso"], "SR4phighIso":allRegions["SR4phighIso"]})

#if "--dryrun" in option or "--createExecFile" in option: submitCMD = ""

for name, cr in crs.items():

    if "fake" in name: continue
    if not "Fine" in name: continue

    est = copy.copy(estimators)
    if not est and not "processes" in cr: est = default_sampleList
    elif not est:                         est = [ e for eList in cr["processes"].values() for e in eList["process"] ] + ["Data"]

    for estimator in est:
        opt = option if not "DD" in estimator else option + " --noSystematics"
        title = " --title est%s_%s"%(year[2:], estimator) if submitCMD.count("submit") else ""
#        if not "DD" in estimator: continue # safe time for qcd estimate

        photonRegions = cr["inclRegion"] + cr["regions"] if not cr["noPhotonCR"] else cr["regions"]

        for j, region in enumerate( photonRegions ):
            if submitCMD.count("submit") or submitCMD.count("echo"):
                os.system( submitCMD + title + ' "python run_estimate.py --cores 1 --selectRegion %i --controlRegion %s --selectEstimator '%(j,name) + estimator + opt + '"' )
                if submitCMD.count("submit"):
                    time.sleep(12)
