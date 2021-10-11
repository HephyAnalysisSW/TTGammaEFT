# Standard Imports
import os, sys
import ROOT

# RootTools Imports
from RootTools.core.Sample import Sample

# Colors
from TTGammaEFT.Samples.color import color

from TTGammaEFT.Tools.user import gridpack_directory

# Data directory
try:
    data_directory_ = sys.modules['__main__'].data_directory
except:
#    from TTGammaEFT.Tools.user import dpm_directory as data_directory_
    from TTGammaEFT.Tools.user import dpm_directoryEFT as data_directory_
    data_directory_ += "postprocessed/"

try:
    postprocessing_directory_ = sys.modules['__main__'].postprocessing_directory
except:
    from TTGammaEFT.Samples.default_locations import postprocessing_locations
    postprocessing_directory_ = postprocessing_locations.twg

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

#dirs["ttGamma_incl_4WC"] = [ "ttGamma_incl_restrict_MadSpin_4WC_order2_ref_rwgt" ]

dirs["tWGamma_2WC"]      = [ "tWG_restrict_ref_rwgt_2WC" ]

directories = { key : [ os.path.join( data_directory_, postprocessing_directory_, dir) for dir in dirs[key] ] for key in dirs.keys() }

# Samples
tWG_2WC_ref                = Sample.fromDirectory( name="tWG_2WC_ref", treeName="Events", isData=False, color=color.TGamma, texName="tW#gamma", directory=directories["tWGamma_2WC"])
tWG_2WC_ref.reweight_pkl   = os.path.join( gridpack_directory, "EFT", "dipoles", "singleOp", "tWG_rwgt", "tWG_rwgt_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

all = [
    tWG_2WC_ref,
]
