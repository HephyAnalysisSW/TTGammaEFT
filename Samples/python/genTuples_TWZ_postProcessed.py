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
#postprocessing_directory = "TWZ_rwgt_dim6top_GEN/gen/"
postprocessing_directory = "TWZ_rwgt_yt_GEN_SIM/gen/"

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

dirs["tWZ0j_rwgt_dim6top_GEN"]   = [ "tWZ0j_rwgt_dim6top" ]
dirs["tWZ01j_rwgt_dim6top_GEN"]  = [ "tWZ01j_rwgt_dim6top" ]
dirs["tWZ01j_rwgt_filter_yt_GEN_SIM"] = [ "tWZ01j_rwgt_filter_2" ]

directories = { key : [ os.path.join( data_directory, postprocessing_directory, dir) for dir in dirs[key] ] for key in dirs.keys() }

#tWZ0j_rwgt_dim6top_GEN               = Sample.fromDirectory(name="tWZ0j_rwgt_dim6top_GEN", treeName="Events", isData=False, color=color.VG1, texName="tWZ0j", directory=directories["tWZ0j_rwgt_dim6top_GEN"])
#tWZ0j_rwgt_dim6top_GEN.reweight_pkl  = "/afs/hephy.at/data/rschoefbeck01/gridpacks/dim6top/tWZ0j_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl"

#tWZ01j_rwgt_dim6top_GEN              = Sample.fromDirectory(name="tWZ01j_rwgt_dim6top_GEN", treeName="Events", isData=False, color=color.VG1, texName="tWZ01j", directory=directories["tWZ01j_rwgt_dim6top_GEN"])
#tWZ01j_rwgt_dim6top_GEN.reweight_pkl = "/afs/hephy.at/data/rschoefbeck01/gridpacks/dim6top/tWZ01j_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl"

tWZ01j_rwgt_filter_yt_GEN_SIM              = Sample.fromDirectory(name="tWZ01j_rwgt_filter_yt_GEN_SIM", treeName="Events", isData=False, color=color.VG1, texName="tWZ01j", directory=directories["tWZ01j_rwgt_filter_yt_GEN_SIM"])
tWZ01j_rwgt_filter_yt_GEN_SIM.reweight_pkl = "/afs/hephy.at/data/cms04/ttschida/gridpacks/Yt/tWZ01j_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl"

