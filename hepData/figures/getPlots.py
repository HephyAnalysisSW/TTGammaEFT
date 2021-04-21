#!/usr/bin/env python

import os, sys

plotDir = os.getcwd()
anDir   = plotDir + "/../"

# alias of the upper directory to the plot directory on EOS
# key = AN directory, value = directory on EOS
aliases = {}
aliases["qcdTF"]       = "transferFactor"
aliases["validation"]  = "qcdChecks"
aliases["DYChecks"]    = "DYChecks"
aliases["systematics"] = "systematics"
aliases["misTTChecks"] = "misTTChecks"
aliases["fakes"]       = "ratioPlots"
aliases["fakeRatio"]   = "fakeRatio"
aliases["fit"]         = "fit"

# directories that are not synced
blacklist  = []
blacklist += ["sketches"]
blacklist += ["trigger"]
blacklist += ["feynman"]

def extractFilePath( l ):
    return l.split("figures/")[1].split("\n")[0].replace("}","").replace("{","").replace("\\","")

for texFile in filter( lambda x: x.endswith(".tex"), os.listdir(anDir) ):
    with open( anDir+texFile, "r" ) as f:
        plots = map( extractFilePath, filter( lambda line: "figures/" in line, f.readlines() ) )
#    lines = filter( lambda line: ".pdf" in line or ".png" in line, lines )
    if not plots: continue
    for plot in plots:
        if os.path.exists( plot ):
            print "File exists: %s"%plot
            print "Skipping"
            continue
        path, file = os.path.dirname(plot), os.path.basename(plot)
        key = path.split("/")[0]
        if key in blacklist: continue
        if not os.path.exists( path ): os.makedirs( path )
#        if "unfolding/" in path: 
#            cmd = "wget -4 -P %s http://schoef.web.cern.ch/schoef/TTGammaEFT/%s --no-check-certificate"%( path+"/", plot.replace(key, aliases[key]) if key in aliases.keys() else plot )
#        else:
        cmd = "wget -4 -P %s http://llechner.web.cern.ch/llechner/TTGammaEFT/%s --no-check-certificate"%( path+"/", plot.replace(key, aliases[key]) if key in aliases.keys() else plot )

        #cmd = "wget -P %s http://www.hephy.at/user/roschoefbeck/TTGammaEFT/%s"%( path+"/", plot.replace(key, aliases[key]) if key in aliases.keys() else plot )
        print "Executing: %s"%cmd
        os.system(cmd)
