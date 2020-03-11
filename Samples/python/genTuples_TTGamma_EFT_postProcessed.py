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
    from TTGammaEFT.Tools.user import dpm_directory as data_directory_
    data_directory_ += "postprocessed/"

try:
    postprocessing_directory_ = sys.modules['__main__'].postprocessing_directory
except:
    from TTGammaEFT.Samples.default_locations import postprocessing_locations
    postprocessing_directory_ = postprocessing_locations.EFT

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

dirs["ttGamma_0l_4WC"]   = [ "ttGamma_Had_restrict_4WC_order2_ref_rwgt" ]
dirs["ttGamma_1l_4WC"]   = [ "ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt" ]
dirs["ttGamma_2l_4WC"]   = [ "ttGamma_Dilept_restrict_4WC_order2_ref_rwgt" ]

# only combine samples with the same reference point!
dirs["ttGamma_4WC"]      = dirs["ttGamma_0l_4WC"] + dirs["ttGamma_1l_4WC"] + dirs["ttGamma_2l_4WC"]

directories = { key : [ os.path.join( data_directory_, postprocessing_directory_, dir) for dir in dirs[key] ] for key in dirs.keys() }

# Samples
TTG_4WC_ref                        = Sample.fromDirectory( name="TTG_4WC_ref", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_4WC"])
TTG_4WC_ref.reweight_pkl           = os.path.join( gridpack_directory, "EFT", "dipoles", "ttGamma_SemiLept_restrict", "ttGamma_SemiLept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

#TTG_Incl_4WC_ref                   = Sample.fromDirectory( name="TTG_Incl_4WC_ref", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_incl_4WC"])
#TTG_incl_4WC_ref.reweight_pkl      = os.path.join( gridpack_directory, "EFT", "dipoles", "ttGamma_restrict_rwgt", "ttGamma_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

TTG_Had_4WC_ref                    = Sample.fromDirectory( name="TTG_Had_4WC_ref", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_0l_4WC"])
TTG_Had_4WC_ref.reweight_pkl       = os.path.join( gridpack_directory, "EFT", "dipoles", "ttGamma_Had_restrict", "ttGamma_Had_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

TTG_SemiLep_4WC_ref                = Sample.fromDirectory( name="TTG_SemiLep_4WC_ref", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_1l_4WC"])
TTG_SemiLep_4WC_ref.reweight_pkl   = os.path.join( gridpack_directory, "EFT", "dipoles", "ttGamma_SemiLept_restrict", "ttGamma_SemiLept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

TTG_Dilep_4WC_ref                  = Sample.fromDirectory( name="TTG_Dilep_4WC_ref", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_2l_4WC"])
TTG_Dilep_4WC_ref.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "ttGamma_Dilept_restrict", "ttGamma_Dilept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )