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
    postprocessing_directory_ = postprocessing_locations.MC2018_semilep

print postprocessing_directory_
try:
    fromDPM = sys.modules['__main__'].fromEOS != "True"
except:
    fromDPM = not "clip" in os.getenv("HOSTNAME").lower()

#if "gammaSkim" in os.environ and os.environ["gammaSkim"] == "True":
#    postprocessing_directory_ = postprocessing_directory_.replace("/semilep/", "/semilepGamma/")

# Redirector
try:
    redirector = sys.modules["__main__"].redirector
except:
    from TTGammaEFT.Tools.user import redirector as redirector

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

dirs["TTG"]              = ["TTGLep_LO", "TTGSingleLep_LO", "TTGHad_LO"]
dirs["TTG_DL"]           = ["TTGLep_LO"]
dirs["TTG_SL"]           = ["TTGSingleLep_LO"]
dirs["TTG_Had"]          = ["TTGHad_LO"]

dirs["TTG_stitched"]     = ["TTGLep_LO", "TTGLep_ptG100To200_LO", "TTGLep_ptG200_LO", "TTGSingleLep_LO", "TTGSingleLep_ptG100To200_LO", "TTGSingleLep_ptG200_LO", "TTGHad_LO", "TTGHad_ptG100To200_LO", "TTGHad_ptG200_LO"]
dirs["TTG_med"]          = ["TTGLep_ptG100To200_LO", "TTGSingleLep_ptG100To200_LO", "TTGHad_ptG100To200_LO"]
dirs["TTG_high"]         = ["TTGLep_ptG200_LO", "TTGSingleLep_ptG200_LO","TTGHad_ptG200_LO"]

dirs["TTG_DL_stitched"]  = ["TTGLep_LO", "TTGLep_ptG100To200_LO", "TTGLep_ptG200_LO"]
dirs["TTG_DL_med"]       = ["TTGLep_ptG100To200_LO"]
dirs["TTG_DL_high"]      = ["TTGLep_ptG200_LO"]

dirs["TTG_SL_stitched"]  = ["TTGSingleLep_LO", "TTGSingleLep_ptG100To200_LO", "TTGSingleLep_ptG200_LO"]
dirs["TTG_SL_med"]       = ["TTGSingleLep_ptG100To200_LO"]
dirs["TTG_SL_high"]      = ["TTGSingleLep_ptG200_LO"]

dirs["TTG_Had_stitched"] = ["TTGHad_LO", "TTGHad_ptG100To200_LO", "TTGHad_ptG200_LO"]
dirs["TTG_Had_med"]      = ["TTGHad_ptG100To200_LO"]
dirs["TTG_Had_high"]     = ["TTGHad_ptG200_LO"]

directories = { key : [ os.path.join( data_directory_, postprocessing_directory_, dir) for dir in dirs[key] ] for key in dirs.keys() }

# Samples
TTG              = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG"], noCheckProxy=True, fromDPM=fromDPM)
TTG_med          = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_med"], noCheckProxy=True, fromDPM=fromDPM)
TTG_high         = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_high"], noCheckProxy=True, fromDPM=fromDPM)
TTG_stitched     = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_stitched"], noCheckProxy=True, fromDPM=fromDPM)

TTG_DL           = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_DL"], noCheckProxy=True, fromDPM=fromDPM)
TTG_DL_med       = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_DL_med"], noCheckProxy=True, fromDPM=fromDPM)
TTG_DL_high      = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_DL_high"], noCheckProxy=True, fromDPM=fromDPM)
TTG_DL_stitched  = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_DL_stitched"], noCheckProxy=True, fromDPM=fromDPM)

TTG_SL           = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_SL"], noCheckProxy=True, fromDPM=fromDPM)
TTG_SL_med       = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_SL_med"], noCheckProxy=True, fromDPM=fromDPM)
TTG_SL_high      = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_SL_high"], noCheckProxy=True, fromDPM=fromDPM)
TTG_SL_stitched  = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_SL_stitched"], noCheckProxy=True, fromDPM=fromDPM)

TTG_Had          = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_Had"], noCheckProxy=True, fromDPM=fromDPM)
TTG_Had_med      = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_Had_med"], noCheckProxy=True, fromDPM=fromDPM)
TTG_Had_high     = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_Had_high"], noCheckProxy=True, fromDPM=fromDPM)
TTG_Had_stitched = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_Had_stitched"], noCheckProxy=True, fromDPM=fromDPM)
