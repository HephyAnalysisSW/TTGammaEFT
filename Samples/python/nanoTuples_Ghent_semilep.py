# Standard Imports
import os, sys
import ROOT

# RootTools Imports
from RootTools.core.Sample import Sample

# Colors
from TTGammaEFT.Samples.color import color
from TTGammaEFT.Samples.helpers import getMCSample

from Samples.Tools.config import redirector_clip_local as redirector

# Data directory
data_directory_ = "/eos/vbc/incoming/user/lukas.lechner/TTGammaEFT"
postprocessing_directory_ = "ghentTuples"
# Logging

if __name__=="__main__":
    import Analysis.Tools.logger as logger
    logger = logger.get_logger("INFO", logFile = None )
    import RootTools.core.logger as logger_rt
    logger_rt = logger_rt.get_logger("INFO", logFile = None )
else:
    import logging
    logger = logging.getLogger(__name__)

logger.info( "Loading MC samples from directory %s", os.path.join( data_directory_, postprocessing_directory_ ) )

# Directories
dirs = {}

dirs["TTG_0l_16"]           = ["ttgHad2016"]
dirs["TTG_1l_16"]           = ["ttgSem2016"]
dirs["TTG_2l_16"]           = ["ttgDil2016"]
dirs["TTG_16"]              = dirs["TTG_0l_16"] + dirs["TTG_1l_16"] + dirs["TTG_2l_16"]

dirs["TTG_0l_17"]           = ["ttgHad2017"]
dirs["TTG_1l_17"]           = ["ttgSem2017"]
dirs["TTG_2l_17"]           = ["ttgDil2017"]
dirs["TTG_17"]              = dirs["TTG_0l_17"] + dirs["TTG_1l_17"] + dirs["TTG_2l_17"]

dirs["TTG_0l_18"]           = ["ttgHad2018"]
dirs["TTG_1l_18"]           = ["ttgSem2018"]
dirs["TTG_2l_18"]           = ["ttgDil2018"]
dirs["TTG_18"]              = dirs["TTG_0l_18"] + dirs["TTG_1l_18"] + dirs["TTG_2l_18"]

directories = { key : [ os.path.join( data_directory_, postprocessing_directory_, dir) for dir in dirs[key] ] for key in dirs.keys() }

# Samples
TTG_16            = getMCSample(name="TTG", redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_16"],    noCheckProxy=True, fromDPM=False)
TTG_0l_16         = getMCSample(name="TTG", redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_0l_16"], noCheckProxy=True, fromDPM=False)
TTG_1l_16         = getMCSample(name="TTG", redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_1l_16"], noCheckProxy=True, fromDPM=False)
TTG_2l_16         = getMCSample(name="TTG", redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_2l_16"], noCheckProxy=True, fromDPM=False)

TTG_17            = getMCSample(name="TTG", redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_17"],    noCheckProxy=True, fromDPM=False)
TTG_0l_17         = getMCSample(name="TTG", redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_0l_17"], noCheckProxy=True, fromDPM=False)
TTG_1l_17         = getMCSample(name="TTG", redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_1l_17"], noCheckProxy=True, fromDPM=False)
TTG_2l_17         = getMCSample(name="TTG", redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_2l_17"], noCheckProxy=True, fromDPM=False)

TTG_18            = getMCSample(name="TTG", redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_18"],    noCheckProxy=True, fromDPM=False)
TTG_0l_18         = getMCSample(name="TTG", redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_0l_18"], noCheckProxy=True, fromDPM=False)
TTG_1l_18         = getMCSample(name="TTG", redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_1l_18"], noCheckProxy=True, fromDPM=False)
TTG_2l_18         = getMCSample(name="TTG", redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_2l_18"], noCheckProxy=True, fromDPM=False)

signals = []

