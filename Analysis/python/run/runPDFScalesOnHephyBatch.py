#!/usr/bin/env python
import os, time, copy

from TTGammaEFT.Analysis.SetupHelpers import *
from TTGammaEFT.Analysis.regions      import regionsTTG, inclRegionsTTG, noPhotonRegionTTG

# Here, all the estimators are defined, if empty: CR specific estimators are used
estimators = []

submitCMD = "echo "

option  = ""
option += " --year 2016"
option += " --overwrite"

crs       = allRegions

for name, cr in crs.items():

    est = copy.copy(estimators)
    if not est and not "processes" in cr: est = default_sampleList
    elif not est:                         est = [ e for eList in cr["processes"].values() for e in eList["process"] ] + ["Data"]

    if "fake" in name.lower(): continue
    if "fine" in name.lower(): continue
    if "eta" in name.lower(): continue
    if "unfold" in name.lower(): continue

    for estimator in est:
        if not "TTG" in estimator: continue

        opt = option if not "DD" in estimator else option + " --noSystematics"
        title = " --title est%s_%s"%(year[2:], estimator) if submitCMD.count("submit") else ""

        photonRegions = cr["inclRegion"] + cr["regions"] if not cr["noPhotonCR"] else cr["regions"]
        nJobs = (len(photonRegions)+1)*2*44
        os.system( submitCMD + title + ' "python runPDFandScale.py %s --controlRegion %s --selectEstimator %s #SPLIT%i"'%(option, name, estimator, nJobs) )
