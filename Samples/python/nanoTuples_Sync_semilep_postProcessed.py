# Standard Imports
import os, sys
import ROOT

# RootTools Imports
from RootTools.core.Sample import Sample

# Colors
from TTGammaEFT.Samples.color import color
from TTGammaEFT.Samples.helpers import getMCSample

# Data directory
try:
    data_directory_ = sys.modules['__main__'].data_directory
except:
    from TTGammaEFT.Tools.user import dpm_directory as data_directory_
    data_directory_ += "postprocessed/"
try:
    postprocessing_directory_ = sys.modules['__main__'].postprocessing_directory
except:
    from TTGammaEFT.Samples.default_locations import postprocessing_locations
    postprocessing_directory_ = postprocessing_locations.MCSync_semilep

try:
    fromDPM = sys.modules['__main__'].fromEOS != "True"
except:
    fromDPM = not "clip" in os.getenv("HOSTNAME").lower()

if "gammaSkim" in os.environ and os.environ["gammaSkim"] == "True":
    postprocessing_directory_ = postprocessing_directory_.replace("/semilep/", "/semilepGamma/")

# Redirector
try:
    redirector = sys.modules["__main__"].redirector
except:
    from TTGammaEFT.Tools.user import redirector as redirector

from Summer16_nanoAODv5 import *

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

dirs["TT_pow"]           = ["TTSingleLep_pow_CP5_sync" ]
dirs["TTG"]              = ["TTGSingleLep_LO_sync"]
dirs["DY_LO"]            = ["DYJetsToLL_M50_LO_ext1_sync"]

directories = { key : [ os.path.join( data_directory_, postprocessing_directory_, dir) for dir in dirs[key] ] for key in dirs.keys() }

# Samples
TT_sync_16          = getMCSample(name="TT_pow",           redirector=redirector, color=color.TT,              texName="t#bar{t}",          directory=directories["TT_pow"], noCheckProxy=True, fromDPM=fromDPM)
TT_sync_16.normalization = TTSingleLep_pow_CP5_sync.normalization
TTG_sync_16         = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG"], noCheckProxy=True, fromDPM=fromDPM)
TTG_sync_16.normalization = TTGSingleLep_LO_sync.normalization
DY_LO_sync_16       = getMCSample(name="DY_LO",            redirector=redirector, color=color.DY,              texName="DY",                directory=directories["DY_LO"], noCheckProxy=False, fromDPM=fromDPM)
DY_LO_sync_16.normalization = DYJetsToLL_M50_LO_ext1_sync.normalization

signals = []

