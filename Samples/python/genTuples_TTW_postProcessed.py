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
postprocessing_directory = "TTW_rwgt_dim6top_GEN_SIM/gen/"
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

dirs["ttW01j_rwgt_dim6top_GEN_SIM"]    = [ "ttW01j_rwgt_dim6top" ]

directories = { key : [ os.path.join( data_directory, postprocessing_directory, dir) for dir in dirs[key] ] for key in dirs.keys() }

ttW01j_rwgt_dim6top_GEN_SIM               = Sample.fromDirectory(name="ttW01j_rwgt_dim6top_GEN_SIM", treeName="Events", isData=False, color=color.VG1, texName="ttW01j", directory=directories["ttW01j_rwgt_dim6top_GEN_SIM"])
ttW01j_rwgt_dim6top_GEN_SIM.reweight_pkl  = "/afs/hephy.at/data/cms04/ttschida/gridpacks/dim6top/ttW01j_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl"

