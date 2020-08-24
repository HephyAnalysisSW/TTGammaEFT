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

dirs["tt01j_0l_4WC"]   = [ "tt01j_Had_restrict_4WC_order2_ref_rwgt" ]
dirs["tt01j_1l_4WC"]   = [ "tt01j_SemiLept_restrict_4WC_order2_ref_rwgt" ]
dirs["tt01j_2l_4WC"]   = [ "tt01j_Dilept_restrict_4WC_order2_ref_rwgt" ]

# only combine samples with the same reference point!
dirs["tt01j_4WC"]      = dirs["tt01j_0l_4WC"] + dirs["tt01j_1l_4WC"] + dirs["tt01j_2l_4WC"]

dirs["tW_4WC"]           = [ "tW_restrict_4WC_order2_ref_rwgt" ]
dirs["tWGamma_4WC"]      = [ "tWG_restrict_4WC_order2_ref_rwgt" ]
dirs["st_tch_4WC"]       = [ "st_tch_restrict_4WC_order2_ref_rwgt" ]
dirs["stGamma_tch_4WC"]  = [ "stg_tch_restrict_4WC_order2_ref_rwgt" ]
dirs["st_sch_4WC"]       = [ "st_sch_restrict_4WC_order2_ref_rwgt" ]
dirs["stGamma_sch_4WC"]  = [ "stg_sch_restrict_4WC_order2_ref_rwgt" ]
#dirs["tt_4WC"]           = [ "tt01j_restrict_4WC_order2_ref_rwgt" ]


directories = { key : [ os.path.join( data_directory_, postprocessing_directory_, dir) for dir in dirs[key] ] for key in dirs.keys() }

# Samples
TTG_4WC_ref                        = Sample.fromDirectory( name="TTG_4WC_ref", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_4WC"])
TTG_4WC_ref.reweight_pkl           = os.path.join( gridpack_directory, "EFT", "dipoles", "ttGamma_SemiLept_restrict", "ttGamma_SemiLept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

TTG_Had_4WC_ref                    = Sample.fromDirectory( name="TTG_Had_4WC_ref", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_0l_4WC"])
TTG_Had_4WC_ref.reweight_pkl       = os.path.join( gridpack_directory, "EFT", "dipoles", "ttGamma_Had_restrict", "ttGamma_Had_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

TTG_SemiLep_4WC_ref                = Sample.fromDirectory( name="TTG_SemiLep_4WC_ref", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_1l_4WC"])
TTG_SemiLep_4WC_ref.reweight_pkl   = os.path.join( gridpack_directory, "EFT", "dipoles", "ttGamma_SemiLept_restrict", "ttGamma_SemiLept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

TTG_Dilep_4WC_ref                  = Sample.fromDirectory( name="TTG_Dilep_4WC_ref", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_2l_4WC"])
TTG_Dilep_4WC_ref.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "ttGamma_Dilept_restrict", "ttGamma_Dilept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

# EFT bkg
tW_4WC_ref                     = Sample.fromDirectory( name="tW_4WC_ref", treeName="Events", isData=False, color=color.tW, texName="tW", directory=directories["tW_4WC"])
tW_4WC_ref.reweight_pkl        = os.path.join( gridpack_directory, "EFT", "dipoles", "tW_rwgt", "tW_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

tWG_4WC_ref                    = Sample.fromDirectory( name="tWG_4WC_ref", treeName="Events", isData=False, color=color.tW, texName="tW#gamma", directory=directories["tWGamma_4WC"])
tWG_4WC_ref.reweight_pkl       = os.path.join( gridpack_directory, "EFT", "dipoles", "tWG_rwgt", "tWG_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

st_tch_4WC_ref                 = Sample.fromDirectory( name="st_tch_4WC_ref", treeName="Events", isData=False, color=color.T, texName="t/#bar{t} (t-ch)", directory=directories["st_tch_4WC"])
st_tch_4WC_ref.reweight_pkl    = os.path.join( gridpack_directory, "EFT", "dipoles", "st_tch_rwgt", "st_tch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

stg_tch_4WC_ref                = Sample.fromDirectory( name="stg_tch_4WC_ref", treeName="Events", isData=False, color=color.TGamma, texName="t#gamma (t-ch)", directory=directories["stGamma_tch_4WC"])
stg_tch_4WC_ref.reweight_pkl   = os.path.join( gridpack_directory, "EFT", "dipoles", "stg_tch_rwgt", "stg_tch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

st_sch_4WC_ref                 = Sample.fromDirectory( name="st_sch_4WC_ref", treeName="Events", isData=False, color=color.T, texName="t/#bar{t} (s-ch)", directory=directories["st_sch_4WC"])
st_sch_4WC_ref.reweight_pkl    = os.path.join( gridpack_directory, "EFT", "dipoles", "st_sch_rwgt", "st_sch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

stg_sch_4WC_ref                = Sample.fromDirectory( name="stg_sch_4WC_ref", treeName="Events", isData=False, color=color.TGamma, texName="t#gamma (s-ch)", directory=directories["stGamma_sch_4WC"])
stg_sch_4WC_ref.reweight_pkl   = os.path.join( gridpack_directory, "EFT", "dipoles", "stg_sch_rwgt", "stg_sch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

TT_4WC_ref                        = Sample.fromDirectory( name="TT_4WC_ref", treeName="Events", isData=False, color=color.TT, texName="t#bar{t}", directory=directories["tt01j_4WC"])
TT_4WC_ref.reweight_pkl           = os.path.join( gridpack_directory, "EFT", "dipoles", "tt01j_SemiLept_restrict", "tt01j_SemiLept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

TT_Had_4WC_ref                    = Sample.fromDirectory( name="TT_Had_4WC_ref", treeName="Events", isData=False, color=color.TT, texName="t#bar{t}", directory=directories["tt01j_0l_4WC"])
TT_Had_4WC_ref.reweight_pkl       = os.path.join( gridpack_directory, "EFT", "dipoles", "tt01j_Had_restrict", "tt01j_Had_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

TT_SemiLep_4WC_ref                = Sample.fromDirectory( name="TT_SemiLep_4WC_ref", treeName="Events", isData=False, color=color.TT, texName="t#bar{t}", directory=directories["tt01j_1l_4WC"])
TT_SemiLep_4WC_ref.reweight_pkl   = os.path.join( gridpack_directory, "EFT", "dipoles", "tt01j_SemiLept_restrict", "tt01j_SemiLept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

TT_Dilep_4WC_ref                  = Sample.fromDirectory( name="TT_Dilep_4WC_ref", treeName="Events", isData=False, color=color.TT, texName="t#bar{t}", directory=directories["tt01j_2l_4WC"])
TT_Dilep_4WC_ref.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "tt01j_Dilept_restrict", "tt01j_Dilept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

