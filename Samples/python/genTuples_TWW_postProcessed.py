# Standard Imports
import os, sys
import ROOT

# RootTools Imports
from RootTools.core.Sample import Sample

# Colors
from TTGammaEFT.Samples.color import color

# Data directory
from TTGammaEFT.Tools.user import gridpack_directory
data_directory           = "/afs/hephy.at/data/cms04/ttschida/TTGammaEFT/Tuples/"
postprocessing_directory = "TWW_rwgt_yt_GEN_SIM/gen/"

# Logging
if __name__=="__main__":
    import Analysis.Tools.logger as logger
    logger = logger.get_logger("INFO", logFile = None )
    import RootTools.core.logger as logger_rt
    logger_rt = logger_rt.get_logger("INFO", logFile = None )
else:
    import logging
    logger = logging.getLogger(__name__)

logger.info( "Loading MC samples from directory %s", os.path.join( data_directory, postprocessing_directory ) )

# Directories
dirs = {}

dirs["tWW1j_rwgt_yt_GEN_SIM"]    = [ "tWW1j_rwgt" ]

directories = { key : [ os.path.join( data_directory, postprocessing_directory, dir) for dir in dirs[key] ] for key in dirs.keys() }

tWW1j_rwgt_yt_GEN_SIM               = Sample.fromDirectory(name="tWW1j_rwgt_yt_GEN_SIM", treeName="Events", isData=False, color=color.VG1, texName="tWW1j", directory=directories["tWW1j_rwgt_yt_GEN_SIM"])
tWW1j_rwgt_yt_GEN_SIM.reweight_pkl  = "/afs/hephy.at/data/cms04/ttschida/gridpacks/Yt/tWW1j_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl"

