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

#ttGamma_SemiLept_restrict_rwgt SM xsec (LO): 4.61400569578 +- 0.168386402874 pb 
#ttGamma_SemiLept_restrict_rwgt ref point xsec (LO): 14.208233244 +- 0.008421588 pb 
ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt", "/ttGamma_SemiLept_restrict_ctZ_ctZI_ctW_ctWI_rwgt_v3/llechner-ttGamma_SemiLept_restrict_ctZ_ctZI_ctW_ctWI_rwgt_v3-52ccdb836f4f6a71f0c2e2dfd2ac5032/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "ttGamma_SemiLept_restrict", "ttGamma_SemiLept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt.xSection         = 14.208233244 * 1.994
ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt.nEvents          = 1000000

#ttGamma_Dilept_restrict_rwgt SM xsec (LO): 1.35234104243 +- 0.0918894201164 pb 
#ttGamma_Dilept_restrict_rwgt ref point xsec (LO): 4.1996660736 +- 0.005027258 pb 
ttGamma_Dilept_restrict_4WC_order2_ref_rwgt                    = FWLiteSample.fromDAS("ttGamma_Dilept_restrict_4WC_order2_ref_rwgt", "/ttGamma_Dilept_restrict_ctZ_ctZI_ctW_ctWI_rwgt/llechner-ttGamma_Dilept_restrict_ctZ_ctZI_ctW_ctWI_rwgt-ca5a5defbc9ea37daa37f4d84541274e/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
ttGamma_Dilept_restrict_4WC_order2_ref_rwgt.reweight_pkl       = os.path.join( gridpack_directory, "EFT", "dipoles", "ttGamma_Dilept_restrict", "ttGamma_Dilept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
ttGamma_Dilept_restrict_4WC_order2_ref_rwgt.xSection           = 4.1996660736 * 1.616
ttGamma_Dilept_restrict_4WC_order2_ref_rwgt.nEvents            = 1000000

#ttGamma_Had_restrict_rwgt SM xsec (LO): 3.66135127723 +- 0.423416766218 pb 
#ttGamma_Had_restrict_rwgt ref point xsec (LO): 11.772568724 +- 0.02751207 pb 
ttGamma_Had_restrict_4WC_order2_ref_rwgt                       = FWLiteSample.fromDAS("ttGamma_Had_restrict_4WC_order2_ref_rwgt", "/ttGamma_Had_restrict_ctZ_ctZI_ctW_ctWI_rwgt/llechner-ttGamma_Had_restrict_ctZ_ctZI_ctW_ctWI_rwgt-3a8b03a4c138eccf092e79c105a0428d/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
ttGamma_Had_restrict_4WC_order2_ref_rwgt.reweight_pkl          = os.path.join( gridpack_directory, "EFT", "dipoles", "ttGamma_Had_restrict", "ttGamma_Had_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
ttGamma_Had_restrict_4WC_order2_ref_rwgt.xSection              = 11.772568724 * 2.565
ttGamma_Had_restrict_4WC_order2_ref_rwgt.nEvents               = 1000000

# EFT bkg
# inclusive decays
#tW_rwgt SM xsec (LO): 49.4963861473 +- 3.69463520611 pb 
#tW_rwgt ref point xsec (LO): 140.572342341 +- 0.2891878 pb 
tW_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("tW_restrict_4WC_order2_ref_rwgt", "/tW_rwgt_ref/llechner-tW_rwgt_ref-2d8f5fdca1229e45c3a70a69bd387c61/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
tW_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "tW_rwgt", "tW_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
tW_restrict_4WC_order2_ref_rwgt.xSection         = 140.572342341
tW_restrict_4WC_order2_ref_rwgt.nEvents          = 5000000

# inclusive decays
#tWG_rwgt SM xsec (LO): 0.368323201938 +- 0.0320749303946 pb 
#tWG_rwgt ref point xsec (LO): 1.78215125 +- 0.002279561 pb 
tWG_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("tWG_restrict_4WC_order2_ref_rwgt", "/tWG_rwgt_ref_v3/llechner-tWG_rwgt_ref_v3-7cad25d8018690e060a09b0cfd608304/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
tWG_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "tWG_rwgt", "tWG_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
tWG_restrict_4WC_order2_ref_rwgt.xSection         = 1.78215125
tWG_restrict_4WC_order2_ref_rwgt.nEvents          = 5000000

# inclusive decays
#st_tch_rwgt SM xsec (LO): 148.924871329 +- 12.6630598052 pb 
#st_tch_rwgt ref point xsec (LO): 509.727000356 +- 1.168766 pb 
st_tch_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("st_tch_restrict_4WC_order2_ref_rwgt", "/st_tch_rwgt_ref/llechner-st_tch_rwgt_ref-553d2d42a0865b5dbac64c04516f94d1/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
st_tch_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "st_tch_rwgt", "st_tch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
st_tch_restrict_4WC_order2_ref_rwgt.xSection         = 509.727000356
st_tch_restrict_4WC_order2_ref_rwgt.nEvents          = 5000000

# inclusive decays
#stg_tch_rwgt SM xsec (LO): 2.98828345609 +- 0.387420768092 pb 
#stg_tch_rwgt ref point xsec (LO): 10.4706308012 +- 0.03982736 pb 
stg_tch_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("stg_tch_restrict_4WC_order2_ref_rwgt", "/stg_tch_rwgt_ref/llechner-stg_tch_rwgt_ref-fe2213c58e4de06cf875593f88d095b3/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
stg_tch_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "stg_tch_rwgt", "stg_tch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
stg_tch_restrict_4WC_order2_ref_rwgt.xSection         = 10.4706308012
stg_tch_restrict_4WC_order2_ref_rwgt.nEvents          = 5000000

# inclusive decays
#st_sch_rwgt SM xsec (LO): 7.7155571983 +- 0.405141972721 pb 
#st_sch_rwgt ref point xsec (LO): 89.040000519 +- 0.32239 pb 
st_sch_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("st_sch_restrict_4WC_order2_ref_rwgt", "/st_sch_rwgt_ref/llechner-st_sch_rwgt_ref-8953fc0dffb64448b800da0f6a738d05/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
st_sch_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "st_sch_rwgt", "st_sch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
st_sch_restrict_4WC_order2_ref_rwgt.xSection         = 89.040000519
st_sch_restrict_4WC_order2_ref_rwgt.nEvents          = 5000000

# inclusive decays
#stg_sch_rwgt SM xsec (LO): 0.0436672357263 +- 0.0020812951441 pb 
#stg_sch_rwgt ref point xsec (LO): 0.65070908604 +- 0.002168962 pb 
stg_sch_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("stg_sch_restrict_4WC_order2_ref_rwgt", "/stg_sch_rwgt_ref/llechner-stg_sch_rwgt_ref-038f8ce656868e08138c1d1b935cd738/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
stg_sch_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "stg_sch_rwgt", "stg_sch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
stg_sch_restrict_4WC_order2_ref_rwgt.xSection         = 0.65070908604
stg_sch_restrict_4WC_order2_ref_rwgt.nEvents          = 5000000

# lepton decays
#tt01j_Dilept_restrict_rwgt SM xsec (LO): 91.7780884431 +- 4.27396010612 pb 
#tt01j_Dilept_restrict_rwgt ref point xsec (LO): 276.438705 +- 0.35586 pb 
#After matching: total cross section = 1.176e+02 +- 4.401e+00 pb
tt01j_Dilept_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("tt01j_Dilept_restrict_4WC_order2_ref_rwgt", "/tt01j_Dilept_restrict/llechner-tt01j_Dilept_restrict-0b79b9f7eebc26f55cce2b3a3c8ffbc3/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
tt01j_Dilept_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "tt01j_Dilept_restrict", "tt01j_Dilept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
tt01j_Dilept_restrict_4WC_order2_ref_rwgt.xSection         = 117.6 #xsec after matching, 276.438705 before matching, 42.5% matching efficiency (run 2.5x more events!)
tt01j_Dilept_restrict_4WC_order2_ref_rwgt.nEvents          = int(5000000 * 117.6 / 276.438705) #adjust for matching efficiency

#tt01j_SemiLept_restrict_rwgt SM xsec (LO): 305.643575078 +- 9.07989616885 pb 
#tt01j_SemiLept_restrict_rwgt ref point xsec (LO): 904.0769324 +- 0.831361 pb 
#After matching: total cross section = 4.021e+02 +- 1.433e+01 pb
tt01j_SemiLept_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("tt01j_SemiLept_restrict_4WC_order2_ref_rwgt", "/tt01j_SemiLept_restrict/llechner-tt01j_SemiLept_restrict-5db64ed27da7c89b9af8454cf81f4652/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
tt01j_SemiLept_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "tt01j_SemiLept_restrict", "tt01j_SemiLept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
tt01j_SemiLept_restrict_4WC_order2_ref_rwgt.xSection         = 402.1 #xsec after matching, 904.0769324 before matching, 44.4% matching efficiency (run 2.5x more events!)
tt01j_SemiLept_restrict_4WC_order2_ref_rwgt.nEvents          = int(5000000 * 402.1 / 904.0769324) #adjust for matching efficiency

#tt01j_Had_restrict_rwgt SM xsec (LO): 248.962760818 +- 13.5734885372 pb 
#tt01j_Had_restrict_rwgt ref point xsec (LO): 743.47548 +- 1.790016 pb 
#After matching: total cross section = 3.286e+02 +- 1.200e+01 pb
tt01j_Had_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("tt01j_Had_restrict_4WC_order2_ref_rwgt", "/tt01j_Had_restrict/llechner-tt01j_Had_restrict-f7a73630bc5ec4386806d8af3a3bf963/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
tt01j_Had_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "tt01j_Had_restrict", "tt01j_Had_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
tt01j_Had_restrict_4WC_order2_ref_rwgt.xSection         = 328.6 #xsec after matching, 743.47548 before matching, 44.2% matching efficiency (run 2.5x more events!)
tt01j_Had_restrict_4WC_order2_ref_rwgt.nEvents          = int(5000000 * 328.6 / 743.47548) #adjust for matching efficiency

EFT = [
    ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt,
    ttGamma_Dilept_restrict_4WC_order2_ref_rwgt,
    ttGamma_Had_restrict_4WC_order2_ref_rwgt,
    tt01j_SemiLept_restrict_4WC_order2_ref_rwgt,
    tt01j_Dilept_restrict_4WC_order2_ref_rwgt,
    tt01j_Had_restrict_4WC_order2_ref_rwgt,
    tW_restrict_4WC_order2_ref_rwgt,
    tWG_restrict_4WC_order2_ref_rwgt,
    st_tch_restrict_4WC_order2_ref_rwgt,
    stg_tch_restrict_4WC_order2_ref_rwgt,
    st_sch_restrict_4WC_order2_ref_rwgt,
    stg_sch_restrict_4WC_order2_ref_rwgt,
]

allSamples = EFT

for s in allSamples:
    print s.reweight_pkl
    s.isData = False

