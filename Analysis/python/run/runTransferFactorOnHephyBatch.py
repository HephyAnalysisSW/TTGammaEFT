#!/usr/bin/env python
import os, time, copy

from TTGammaEFT.Analysis.SetupHelpers import *
from TTGammaEFT.Analysis.regions      import *

year = "2016"

# Here, all the estimators are defined, if empty: CR specific estimators are used

#submitCMD = "submitBatch.py --dpm "
submitCMD = "echo "
#submitCMD = ""

option  = ""
option += " --year " + year
#option += " --overwrite"
#option += " --checkOnly"

crs       = allRegions

for name, cr in crs.items():

    title     = " --title tf%s_%s"%(year[2:], estimator) if submitCMD.count("submit") else ""

    if "unfold" in name.lower(): continue
    if "fake" in name.lower(): continue
    if "fine" in name.lower(): continue
    if "eta" in name.lower(): continue

    # double for e+mu channel
    if submitCMD.count("submit") or submitCMD.count("echo"):
        os.system( submitCMD + title + ' "python run_transferFactor.py %s --controlRegion %s --mode e"'%(option, name) )
        os.system( submitCMD + title + ' "python run_transferFactor.py %s --controlRegion %s --mode mu"'%(option, name) )
        if submitCMD.count("submit"):
            time.sleep(12)
