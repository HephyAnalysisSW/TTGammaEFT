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
ttGamma_incl_restrict_MadSpin_4WC_order2_ref_rwgt              = FWLiteSample.fromDAS("ttGamma_incl_restrict_MadSpin_4WC_order2_ref_rwgt", "/ttGamma_incl_restrict_MadSpin_ctZ_ctZI_ctW_ctWI_rwgt/llechner-ttGamma_incl_restrict_MadSpin_ctZ_ctZI_ctW_ctWI_rwgt-77f451cfcb0f9308ee130fe88fc833a6/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
#ttGamma_incl_restrict_MadSpin_4WC_order2_ref_rwgt              = FWLiteSample.fromDirectory("ttGamma_incl_restrict_MadSpin_4WC_order2_ref_rwgt", "/ttGamma_incl_restrict_MadSpin_ctZ_ctZI_ctW_ctWI_rwgt/llechner-ttGamma_incl_restrict_MadSpin_ctZ_ctZI_ctW_ctWI_rwgt-77f451cfcb0f9308ee130fe88fc833a6/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_incl_restrict_MadSpin_4WC_order2_ref_rwgt.reweight_pkl = os.path.join( gridpack_directory, "EFT", "dipoles", "ttGamma_restrict_rwgt", "ttGamma_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
ttGamma_incl_restrict_MadSpin_4WC_order2_ref_rwgt.xSection     = 2.5
ttGamma_incl_restrict_MadSpin_4WC_order2_ref_rwgt.nEvents      = 1000000

ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt", "/ttGamma_SemiLept_restrict_ctZ_ctZI_ctW_ctWI_rwgt_v3/llechner-ttGamma_SemiLept_restrict_ctZ_ctZI_ctW_ctWI_rwgt_v3-52ccdb836f4f6a71f0c2e2dfd2ac5032/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
#ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDirectory("ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt", "/ttGamma_SemiLept_restrict_ctZ_ctZI_ctW_ctWI_rwgt_v3/llechner-ttGamma_SemiLept_restrict_ctZ_ctZI_ctW_ctWI_rwgt_v3-52ccdb836f4f6a71f0c2e2dfd2ac5032/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "ttGamma_SemiLept_restrict", "ttGamma_SemiLept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt.xSection         = 14.21
ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt.nEvents          = 1000000

ttGamma_Dilept_restrict_4WC_order2_ref_rwgt                    = FWLiteSample.fromDAS("ttGamma_Dilept_restrict_4WC_order2_ref_rwgt", "/ttGamma_Dilept_restrict_ctZ_ctZI_ctW_ctWI_rwgt/llechner-ttGamma_Dilept_restrict_ctZ_ctZI_ctW_ctWI_rwgt-ca5a5defbc9ea37daa37f4d84541274e/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
#ttGamma_Dilept_restrict_4WC_order2_ref_rwgt                    = FWLiteSample.fromDirectory("ttGamma_Dilept_restrict_4WC_order2_ref_rwgt", "/ttGamma_Dilept_restrict_ctZ_ctZI_ctW_ctWI_rwgt/llechner-ttGamma_Dilept_restrict_ctZ_ctZI_ctW_ctWI_rwgt-ca5a5defbc9ea37daa37f4d84541274e/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_Dilept_restrict_4WC_order2_ref_rwgt.reweight_pkl       = os.path.join( gridpack_directory, "EFT", "dipoles", "ttGamma_Dilept_restrict", "ttGamma_Dilept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
ttGamma_Dilept_restrict_4WC_order2_ref_rwgt.xSection           = 4.2
ttGamma_Dilept_restrict_4WC_order2_ref_rwgt.nEvents            = 1000000

ttGamma_Had_restrict_4WC_order2_ref_rwgt                       = FWLiteSample.fromDAS("ttGamma_Had_restrict_4WC_order2_ref_rwgt", "/ttGamma_Had_restrict_ctZ_ctZI_ctW_ctWI_rwgt/llechner-ttGamma_Had_restrict_ctZ_ctZI_ctW_ctWI_rwgt-3a8b03a4c138eccf092e79c105a0428d/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
#ttGamma_Had_restrict_4WC_order2_ref_rwgt                       = FWLiteSample.fromDirectory("ttGamma_Had_restrict_4WC_order2_ref_rwgt", "/ttGamma_Had_restrict_ctZ_ctZI_ctW_ctWI_rwgt/llechner-ttGamma_Had_restrict_ctZ_ctZI_ctW_ctWI_rwgt-3a8b03a4c138eccf092e79c105a0428d/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_Had_restrict_4WC_order2_ref_rwgt.reweight_pkl          = os.path.join( gridpack_directory, "EFT", "dipoles", "ttGamma_Had_restrict", "ttGamma_Had_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
ttGamma_Had_restrict_4WC_order2_ref_rwgt.xSection              = 11.77
ttGamma_Had_restrict_4WC_order2_ref_rwgt.nEvents               = 1000000

EFT = [
    ttGamma_incl_restrict_MadSpin_4WC_order2_ref_rwgt,
    ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt,
    ttGamma_Dilept_restrict_4WC_order2_ref_rwgt,
    ttGamma_Had_restrict_4WC_order2_ref_rwgt,
]

allSamples = EFT

for s in allSamples:
    s.isData = False
    print s.files
