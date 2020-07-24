# Standard
import os

# RootTools
from RootTools.core.standard import *

# TTGammaEFT
from TTGammaEFT.Tools.user   import gridpack_directory, cache_directory

def get_parser():
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser for samples file")
    argParser.add_argument( '--overwrite',   action='store_true',    help="Overwrite current entry in db?" )
    return argParser

# Redirector
try:
    redirector = sys.modules['__main__'].redirector
except:
    if "clip" in os.getenv("HOSTNAME").lower():
        from Samples.Tools.config import redirector_clip_local as redirector
    else:
        from Samples.Tools.config import redirector as redirector

# Logging
if __name__=="__main__":
    import Analysis.Tools.logger as logger
    logger = logger.get_logger("INFO", logFile = None )
    import RootTools.core.logger as logger_rt
    logger_rt = logger_rt.get_logger("INFO", logFile = None )
    options = get_parser().parse_args()
    ov = options.overwrite
else:
    import logging
    logger = logging.getLogger(__name__)
    ov = False


dbFile = cache_directory + "/samples/DB_TTGamma_GEN_EFT.sql"

logger.info( "Using db file: %s", dbFile )

# EFT, restriction card, 4 WC (dipoles), reference point ctZ = ctZI = ctW = ctWI = 4

ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt", "/ttGamma_SemiLept_restrict_ctZ_ctZI_ctW_ctWI_rwgt_v3/llechner-ttGamma_SemiLept_restrict_ctZ_ctZI_ctW_ctWI_rwgt_v3-52ccdb836f4f6a71f0c2e2dfd2ac5032/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "ttGamma_SemiLept_restrict", "ttGamma_SemiLept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt.xSection         = 4.614
ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt.nEvents          = 1000000

ttGamma_Dilept_restrict_4WC_order2_ref_rwgt                    = FWLiteSample.fromDAS("ttGamma_Dilept_restrict_4WC_order2_ref_rwgt", "/ttGamma_Dilept_restrict_ctZ_ctZI_ctW_ctWI_rwgt/llechner-ttGamma_Dilept_restrict_ctZ_ctZI_ctW_ctWI_rwgt-ca5a5defbc9ea37daa37f4d84541274e/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
ttGamma_Dilept_restrict_4WC_order2_ref_rwgt.reweight_pkl       = os.path.join( gridpack_directory, "EFT", "dipoles", "ttGamma_Dilept_restrict", "ttGamma_Dilept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
ttGamma_Dilept_restrict_4WC_order2_ref_rwgt.xSection           = 1.352
ttGamma_Dilept_restrict_4WC_order2_ref_rwgt.nEvents            = 1000000

ttGamma_Had_restrict_4WC_order2_ref_rwgt                       = FWLiteSample.fromDAS("ttGamma_Had_restrict_4WC_order2_ref_rwgt", "/ttGamma_Had_restrict_ctZ_ctZI_ctW_ctWI_rwgt/llechner-ttGamma_Had_restrict_ctZ_ctZI_ctW_ctWI_rwgt-3a8b03a4c138eccf092e79c105a0428d/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
ttGamma_Had_restrict_4WC_order2_ref_rwgt.reweight_pkl          = os.path.join( gridpack_directory, "EFT", "dipoles", "ttGamma_Had_restrict", "ttGamma_Had_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
ttGamma_Had_restrict_4WC_order2_ref_rwgt.xSection              = 3.661
ttGamma_Had_restrict_4WC_order2_ref_rwgt.nEvents               = 1000000

# EFT bkg
# inclusive decays
tW_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("tW_restrict_4WC_order2_ref_rwgt", "/tW_rwgt_ref/llechner-tW_rwgt_ref-2d8f5fdca1229e45c3a70a69bd387c61/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
tW_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "tW_rwgt", "tW_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
tW_restrict_4WC_order2_ref_rwgt.xSection         = 48.164 #LO dim6top
tW_restrict_4WC_order2_ref_rwgt.nEvents          = 5000000

# inclusive decays
tWG_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("tWG_restrict_4WC_order2_ref_rwgt", "/tWG_rwgt_ref_v3/llechner-tWG_rwgt_ref_v3-7cad25d8018690e060a09b0cfd608304/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
tWG_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "tWG_rwgt", "tWG_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
tWG_restrict_4WC_order2_ref_rwgt.xSection         = 0.339 #LO dim6top
tWG_restrict_4WC_order2_ref_rwgt.nEvents          = 5000000

# inclusive decays
st_tch_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("st_tch_restrict_4WC_order2_ref_rwgt", "/st_tch_rwgt_ref/llechner-st_tch_rwgt_ref-553d2d42a0865b5dbac64c04516f94d1/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
st_tch_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "st_tch_rwgt", "st_tch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
st_tch_restrict_4WC_order2_ref_rwgt.xSection         = 142.049 #LO dim6top
st_tch_restrict_4WC_order2_ref_rwgt.nEvents          = 5000000

# inclusive decays
stg_tch_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("stg_tch_restrict_4WC_order2_ref_rwgt", "/stg_tch_rwgt_ref/llechner-stg_tch_rwgt_ref-fe2213c58e4de06cf875593f88d095b3/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
stg_tch_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "stg_tch_rwgt", "stg_tch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
stg_tch_restrict_4WC_order2_ref_rwgt.xSection         = 3.122 #LO dim6top
stg_tch_restrict_4WC_order2_ref_rwgt.nEvents          = 5000000

# inclusive decays
st_sch_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("st_sch_restrict_4WC_order2_ref_rwgt", "/st_sch_rwgt_ref/llechner-st_sch_rwgt_ref-8953fc0dffb64448b800da0f6a738d05/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
st_sch_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "st_sch_rwgt", "st_sch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
st_sch_restrict_4WC_order2_ref_rwgt.xSection         = 7.126 #LO dim6top
st_sch_restrict_4WC_order2_ref_rwgt.nEvents          = 5000000

# inclusive decays
stg_sch_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("stg_sch_restrict_4WC_order2_ref_rwgt", "/stg_sch_rwgt_ref/llechner-stg_sch_rwgt_ref-038f8ce656868e08138c1d1b935cd738/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
stg_sch_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "stg_sch_rwgt", "stg_sch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
stg_sch_restrict_4WC_order2_ref_rwgt.xSection         = 0.040 #LO dim6top
stg_sch_restrict_4WC_order2_ref_rwgt.nEvents          = 5000000

# inclusive decays
tt01j_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("tt01j_restrict_4WC_order2_ref_rwgt", "/tt01j_rwgt/llechner-tt01j_rwgt-a43d8e2c7540f23671c2e6d2b50e6e71/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
tt01j_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "tt01j_rwgt", "tt01j_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
tt01j_restrict_4WC_order2_ref_rwgt.xSection         = 489.2 #LO dim6top xsec after matching, 1278.883 before matching, 40% matching efficiency (run 2.5x more events!)
tt01j_restrict_4WC_order2_ref_rwgt.nEvents          = int(10000000 * 489.2 / 1278.883) #adjust for matching efficiency

# inclusive decays
#tt0123j_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("tt0123j_restrict_4WC_order2_ref_rwgt", "", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#tt0123j_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "tt0123j_rwgt", "tt0123j_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#tt0123j_restrict_4WC_order2_ref_rwgt.xSection         = 
#tt0123j_restrict_4WC_order2_ref_rwgt.nEvents          = 10000000


EFT = [
#    ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt,
#    ttGamma_Dilept_restrict_4WC_order2_ref_rwgt,
#    ttGamma_Had_restrict_4WC_order2_ref_rwgt,
    tW_restrict_4WC_order2_ref_rwgt,
    tWG_restrict_4WC_order2_ref_rwgt,
    st_tch_restrict_4WC_order2_ref_rwgt,
    stg_tch_restrict_4WC_order2_ref_rwgt,
    st_sch_restrict_4WC_order2_ref_rwgt,
    stg_sch_restrict_4WC_order2_ref_rwgt,
#    tt01j_restrict_4WC_order2_ref_rwgt,
#    tt0123j_restrict_4WC_order2_ref_rwgt,
]

allSamples = EFT

for s in allSamples:
    s.isData = False

