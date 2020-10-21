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

dirs["ttGamma_1l_2WC"]      = [ "ttGamma_SemiLept_restrict_ref_rwgt_2WC" ]
dirs["ttGamma_1l_ctZ2"]     = [ "ttGamma_SemiLept_restrict_ctZ2" ]
#dirs["ttGamma_1l_ctW2"]     = [ "ttGamma_SemiLept_restrict_ctW2" ]
dirs["ttGamma_1l_ctZI2"]    = [ "ttGamma_SemiLept_restrict_ctZI2" ]
#dirs["ttGamma_1l_ctWI2"]    = [ "ttGamma_SemiLept_restrict_ctWI2" ]
dirs["ttGamma_1l_ctZm1"]    = [ "ttGamma_SemiLept_restrict_ctZm1" ]
#dirs["ttGamma_1l_ctWm1"]    = [ "ttGamma_SemiLept_restrict_ctWm1" ]
dirs["ttGamma_1l_ctZIm1"]   = [ "ttGamma_SemiLept_restrict_ctZIm1" ]
#dirs["ttGamma_1l_ctWIm1"]   = [ "ttGamma_SemiLept_restrict_ctWIm1" ]
dirs["ttGamma_1l_SM"]       = [ "ttGamma_SemiLept_restrict_SM" ]

#dirs["ttGamma_1l_old"]   = [ "ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt" ]
#dirs["ttGamma_1l_dim2"]   = [ "ttGamma_SemiLept_restrict_4WC_medRef_rwgt_dim2" ]
#dirs["ttGamma_incl_4WC"]   = [ "ttGamma_restrict_4WC_medRef_rwgt" ]

#dirs["ttGamma_0l_4WC"]   = [ "ttGamma_Had_restrict_4WC_ref_rwgt_dim3" ]
#dirs["ttGamma_1l_4WC"]   = [ "ttGamma_SemiLept_restrict_4WC_ref_rwgt_dim3" ]
#dirs["ttGamma_2l_4WC"]   = [ "ttGamma_Dilept_restrict_4WC_ref_rwgt_dim3" ]

# only combine samples with the same reference point!
#dirs["ttGamma_4WC"]      = dirs["ttGamma_2l_4WC"] + dirs["ttGamma_1l_4WC"] + dirs["ttGamma_0l_4WC"]

#dirs["tt01j_1l_4WC"]   = [ "tt01j_SemiLept_restrict_4WC_ref_rwgt_dim3" ]
#dirs["tt01j_2l_4WC"]   = [ "tt01j_Dilept_restrict_4WC_ref_rwgt_dim3" ]

# only combine samples with the same reference point!
#dirs["tt01j_4WC"]      = dirs["tt01j_2l_4WC"] + dirs["tt01j_1l_4WC"]

#dirs["tW_4WC"]           = [ "tW_restrict_4WC_ref_rwgt_dim3" ]
#dirs["tWGamma_4WC"]      = [ "tWG_restrict_4WC_ref_rwgt_dim3" ]
#dirs["st_tch_4WC"]       = [ "st_tch_restrict_4WC_ref_rwgt_dim3" ]
#dirs["stGamma_tch_4WC"]  = [ "stg_tch_restrict_4WC_ref_rwgt_dim3" ]
#dirs["st_sch_4WC"]       = [ "st_sch_restrict_4WC_ref_rwgt_dim3" ]
#dirs["stGamma_sch_4WC"]  = [ "stg_sch_restrict_4WC_ref_rwgt_dim3" ]

directories = { key : [ os.path.join( data_directory_, postprocessing_directory_, dir) for dir in dirs[key] ] for key in dirs.keys() }

# Samples
#TTG_4WC_ref                        = Sample.fromDirectory( name="TTG_4WC_ref", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_4WC"])
#TTG_4WC_ref.reweight_pkl           = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "ttGamma_SemiLept_restrict_rwgt", "ttGamma_SemiLept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

#TTG_Had_4WC_ref                    = Sample.fromDirectory( name="TTG_Had_4WC_ref", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_0l_4WC"])
#TTG_Had_4WC_ref.reweight_pkl       = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "ttGamma_Had_restrict_rwgt", "ttGamma_Had_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

#TTG_SemiLep_4WC_ref                = Sample.fromDirectory( name="TTG_SemiLep_4WC_ref", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_1l_4WC"])
#TTG_SemiLep_4WC_ref.reweight_pkl   = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "ttGamma_SemiLept_restrict_rwgt", "ttGamma_SemiLept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

#TTG_Dilep_4WC_ref                  = Sample.fromDirectory( name="TTG_Dilep_4WC_ref", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_2l_4WC"])
#TTG_Dilep_4WC_ref.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "ttGamma_Dilept_restrict_rwgt", "ttGamma_Dilept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

# special samples
#TTG_SemiLep_4WC_ref_dim2                = Sample.fromDirectory( name="TTG_SemiLep_4WC_ref_dim2", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_1l_dim2"])
#TTG_SemiLep_4WC_ref_dim2.reweight_pkl   = os.path.join( gridpack_directory, "EFT", "dipoles", "medRef", "ttGamma_SemiLept_restrict_rwgt_dim2", "ttGamma_SemiLept_restrict_rwgt_dim2_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

#TTG_SemiLep_old                = Sample.fromDirectory( name="TTG_SemiLep_old", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_1l_old"])
#TTG_SemiLep_old.reweight_pkl   = os.path.join( gridpack_directory, "EFT", "dipoles", "ttGamma_SemiLept_restrict", "ttGamma_SemiLept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

#TTG_incl                        = Sample.fromDirectory( name="TTG_incl", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_incl_4WC"])
#TTG_incl.reweight_pkl           = os.path.join( gridpack_directory, "EFT", "dipoles", "medRef", "ttGamma_restrict_rwgt", "ttGamma_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

# EFT bkg
#tW_4WC_ref                     = Sample.fromDirectory( name="tW_4WC_ref", treeName="Events", isData=False, color=color.tW, texName="tW", directory=directories["tW_4WC"])
#tW_4WC_ref.reweight_pkl        = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "tW_rwgt", "tW_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

#tWG_4WC_ref                    = Sample.fromDirectory( name="tWG_4WC_ref", treeName="Events", isData=False, color=color.tW, texName="tW#gamma", directory=directories["tWGamma_4WC"])
#tWG_4WC_ref.reweight_pkl       = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "tWG_rwgt", "tWG_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

#st_tch_4WC_ref                 = Sample.fromDirectory( name="st_tch_4WC_ref", treeName="Events", isData=False, color=color.T, texName="t/#bar{t} (t-ch)", directory=directories["st_tch_4WC"])
#st_tch_4WC_ref.reweight_pkl    = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "st_tch_rwgt", "st_tch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

#stg_tch_4WC_ref                = Sample.fromDirectory( name="stg_tch_4WC_ref", treeName="Events", isData=False, color=color.TGamma, texName="t#gamma (t-ch)", directory=directories["stGamma_tch_4WC"])
#stg_tch_4WC_ref.reweight_pkl   = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "stg_tch_rwgt", "stg_tch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

#st_sch_4WC_ref                 = Sample.fromDirectory( name="st_sch_4WC_ref", treeName="Events", isData=False, color=color.T, texName="t/#bar{t} (s-ch)", directory=directories["st_sch_4WC"])
#st_sch_4WC_ref.reweight_pkl    = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "st_sch_rwgt", "st_sch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

#stg_sch_4WC_ref                = Sample.fromDirectory( name="stg_sch_4WC_ref", treeName="Events", isData=False, color=color.TGamma, texName="t#gamma (s-ch)", directory=directories["stGamma_sch_4WC"])
#stg_sch_4WC_ref.reweight_pkl   = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "stg_sch_rwgt", "stg_sch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

#TT_4WC_ref                        = Sample.fromDirectory( name="TT_4WC_ref", treeName="Events", isData=False, color=color.TT, texName="t#bar{t}", directory=directories["tt01j_4WC"])
#TT_4WC_ref.reweight_pkl           = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "tt01j_SemiLept_restrict_rwgt", "tt01j_SemiLept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

#TT_SemiLep_4WC_ref                = Sample.fromDirectory( name="TT_SemiLep_4WC_ref", treeName="Events", isData=False, color=color.TT, texName="t#bar{t}", directory=directories["tt01j_1l_4WC"])
#TT_SemiLep_4WC_ref.reweight_pkl   = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "tt01j_SemiLept_restrict_rwgt", "tt01j_SemiLept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

#TT_Dilep_4WC_ref                  = Sample.fromDirectory( name="TT_Dilep_4WC_ref", treeName="Events", isData=False, color=color.TT, texName="t#bar{t}", directory=directories["tt01j_2l_4WC"])
#TT_Dilep_4WC_ref.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "tt01j_Dilept_restrict_rwgt", "tt01j_Dilept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

#ctZ

TTG_SemiLep_2WC_ref                = Sample.fromDirectory( name="TTG_SemiLep_2WC_ref", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_1l_2WC"])
TTG_SemiLep_2WC_ref.reweight_pkl   = os.path.join( gridpack_directory, "EFT", "dipoles", "singleOp", "ttGamma_SemiLept_restrict_rwgt_2WC", "ttGamma_SemiLept_restrict_rwgt_2WC_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )

TTG_SemiLep_ctZ2 = Sample.fromDirectory( name="TTG_SemiLep_ctZ2", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_1l_ctZ2"])
#TTG_SemiLep_ctW2 = Sample.fromDirectory( name="TTG_SemiLep_ctW2", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_1l_ctW2"])
TTG_SemiLep_ctZI2 = Sample.fromDirectory( name="TTG_SemiLep_ctZI2", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_1l_ctZI2"])
#TTG_SemiLep_ctWI2 = Sample.fromDirectory( name="TTG_SemiLep_ctWI2", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_1l_ctWI2"])
TTG_SemiLep_ctZm1 = Sample.fromDirectory( name="TTG_SemiLep_ctZm1", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_1l_ctZm1"])
#TTG_SemiLep_ctWm1 = Sample.fromDirectory( name="TTG_SemiLep_ctWm1", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_1l_ctWm1"])
TTG_SemiLep_ctZIm1 = Sample.fromDirectory( name="TTG_SemiLep_ctZIm1", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_1l_ctZIm1"])
#TTG_SemiLep_ctWIm1 = Sample.fromDirectory( name="TTG_SemiLep_ctWIm1", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_1l_ctWIm1"])
TTG_SemiLep_SM = Sample.fromDirectory( name="TTG_SemiLep_SM", treeName="Events", isData=False, color=color.TTG, texName="tt#gamma", directory=directories["ttGamma_1l_SM"])

all = [
#    TTG_4WC_ref,
#    TTG_Had_4WC_ref,
#    TTG_SemiLep_4WC_ref,
#    TTG_Dilep_4WC_ref,
#    TTG_SemiLep_4WC_ref_dim2,
#    TTG_SemiLep_4WC_ref_dim3,
#    TTG_SemiLep_old,
#    TTG_incl,
#    tW_4WC_ref,
#    tWG_4WC_ref,
#    st_tch_4WC_ref,
#    stg_tch_4WC_ref,
#    st_sch_4WC_ref,
#    stg_sch_4WC_ref,
#    TT_4WC_ref,
#    TT_SemiLep_4WC_ref,
#    TT_Dilep_4WC_ref,

    TTG_SemiLep_2WC_ref,
    TTG_SemiLep_ctZ2,
    TTG_SemiLep_ctZI2,
#    TTG_SemiLep_ctW2,
#    TTG_SemiLep_ctWI2,
    TTG_SemiLep_ctZm1,
    TTG_SemiLep_ctZIm1,
#    TTG_SemiLep_ctWm1,
#    TTG_SemiLep_ctWIm1,
    TTG_SemiLep_SM,
]

#for s in all: print os.path.exists(s.reweight_pkl), s.reweight_pkl
