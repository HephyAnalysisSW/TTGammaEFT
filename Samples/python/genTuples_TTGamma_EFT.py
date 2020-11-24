# Standard
import os, sys

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
#        redirector = 'root://eos.grid.vbc.ac.at/'
        redirector = '/eos/vbc/experiments/cms/'
#        from Samples.Tools.config import redirector_clip as redirector
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
#ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt", "/ttGamma_SemiLept_restrict_ctZ_ctZI_ctW_ctWI_rwgt_v3/llechner-ttGamma_SemiLept_restrict_ctZ_ctZI_ctW_ctWI_rwgt_v3-52ccdb836f4f6a71f0c2e2dfd2ac5032/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "ttGamma_SemiLept_restrict", "ttGamma_SemiLept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt.xSection         = 14.208233244 * 1.4852 # 1.994
#ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt.nEvents          = 1000000

#ttGamma_Dilept_restrict_rwgt SM xsec (LO): 1.35234104243 +- 0.0918894201164 pb 
#ttGamma_Dilept_restrict_rwgt ref point xsec (LO): 4.1996660736 +- 0.005027258 pb 
#ttGamma_Dilept_restrict_4WC_order2_ref_rwgt                    = FWLiteSample.fromDAS("ttGamma_Dilept_restrict_4WC_order2_ref_rwgt", "/ttGamma_Dilept_restrict_ctZ_ctZI_ctW_ctWI_rwgt/llechner-ttGamma_Dilept_restrict_ctZ_ctZI_ctW_ctWI_rwgt-ca5a5defbc9ea37daa37f4d84541274e/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#ttGamma_Dilept_restrict_4WC_order2_ref_rwgt.reweight_pkl       = os.path.join( gridpack_directory, "EFT", "dipoles", "ttGamma_Dilept_restrict", "ttGamma_Dilept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#ttGamma_Dilept_restrict_4WC_order2_ref_rwgt.xSection           = 4.1996660736 * 1.4852 # 1.616
#ttGamma_Dilept_restrict_4WC_order2_ref_rwgt.nEvents            = 1000000

#ttGamma_Had_restrict_rwgt SM xsec (LO): 3.66135127723 +- 0.423416766218 pb 
#ttGamma_Had_restrict_rwgt ref point xsec (LO): 11.772568724 +- 0.02751207 pb 
#ttGamma_Had_restrict_4WC_order2_ref_rwgt                       = FWLiteSample.fromDAS("ttGamma_Had_restrict_4WC_order2_ref_rwgt", "/ttGamma_Had_restrict_ctZ_ctZI_ctW_ctWI_rwgt/llechner-ttGamma_Had_restrict_ctZ_ctZI_ctW_ctWI_rwgt-3a8b03a4c138eccf092e79c105a0428d/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#ttGamma_Had_restrict_4WC_order2_ref_rwgt.reweight_pkl          = os.path.join( gridpack_directory, "EFT", "dipoles", "ttGamma_Had_restrict", "ttGamma_Had_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#ttGamma_Had_restrict_4WC_order2_ref_rwgt.xSection              = 11.772568724 * 1.4852 # 1.565
#ttGamma_Had_restrict_4WC_order2_ref_rwgt.nEvents               = 1000000

# EFT bkg
# inclusive decays
#tW_rwgt SM xsec (LO): 49.4963861473 +- 3.69463520611 pb 
#tW_rwgt ref point xsec (LO): 140.572342341 +- 0.2891878 pb 
#tW_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("tW_restrict_4WC_order2_ref_rwgt", "/tW_rwgt_ref/llechner-tW_rwgt_ref-2d8f5fdca1229e45c3a70a69bd387c61/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#tW_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "tW_rwgt", "tW_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#tW_restrict_4WC_order2_ref_rwgt.xSection         = 140.572342341
#tW_restrict_4WC_order2_ref_rwgt.nEvents          = 5000000

# inclusive decays
#tWG_rwgt SM xsec (LO): 0.368323201938 +- 0.0320749303946 pb 
#tWG_rwgt ref point xsec (LO): 1.78215125 +- 0.002279561 pb 
#tWG_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("tWG_restrict_4WC_order2_ref_rwgt", "/tWG_rwgt_ref_v3/llechner-tWG_rwgt_ref_v3-7cad25d8018690e060a09b0cfd608304/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#tWG_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "tWG_rwgt", "tWG_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#tWG_restrict_4WC_order2_ref_rwgt.xSection         = 1.78215125
#tWG_restrict_4WC_order2_ref_rwgt.nEvents          = 5000000

# inclusive decays
#st_tch_rwgt SM xsec (LO): 148.924871329 +- 12.6630598052 pb 
#st_tch_rwgt ref point xsec (LO): 509.727000356 +- 1.168766 pb 
#st_tch_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("st_tch_restrict_4WC_order2_ref_rwgt", "/st_tch_rwgt_ref/llechner-st_tch_rwgt_ref-553d2d42a0865b5dbac64c04516f94d1/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#st_tch_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "st_tch_rwgt", "st_tch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#st_tch_restrict_4WC_order2_ref_rwgt.xSection         = 509.727000356
#st_tch_restrict_4WC_order2_ref_rwgt.nEvents          = 5000000

# inclusive decays
#stg_tch_rwgt SM xsec (LO): 2.98828345609 +- 0.387420768092 pb 
#stg_tch_rwgt ref point xsec (LO): 10.4706308012 +- 0.03982736 pb 
#stg_tch_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("stg_tch_restrict_4WC_order2_ref_rwgt", "/stg_tch_rwgt_ref/llechner-stg_tch_rwgt_ref-fe2213c58e4de06cf875593f88d095b3/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#stg_tch_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "stg_tch_rwgt", "stg_tch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#stg_tch_restrict_4WC_order2_ref_rwgt.xSection         = 10.4706308012
#stg_tch_restrict_4WC_order2_ref_rwgt.nEvents          = 5000000

# inclusive decays
#st_sch_rwgt SM xsec (LO): 7.7155571983 +- 0.405141972721 pb 
#st_sch_rwgt ref point xsec (LO): 89.040000519 +- 0.32239 pb 
#st_sch_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("st_sch_restrict_4WC_order2_ref_rwgt", "/st_sch_rwgt_ref/llechner-st_sch_rwgt_ref-8953fc0dffb64448b800da0f6a738d05/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#st_sch_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "st_sch_rwgt", "st_sch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#st_sch_restrict_4WC_order2_ref_rwgt.xSection         = 89.040000519
#st_sch_restrict_4WC_order2_ref_rwgt.nEvents          = 5000000

# inclusive decays
#stg_sch_rwgt SM xsec (LO): 0.0436672357263 +- 0.0020812951441 pb 
#stg_sch_rwgt ref point xsec (LO): 0.65070908604 +- 0.002168962 pb 
#stg_sch_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("stg_sch_restrict_4WC_order2_ref_rwgt", "/stg_sch_rwgt_ref/llechner-stg_sch_rwgt_ref-038f8ce656868e08138c1d1b935cd738/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#stg_sch_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "stg_sch_rwgt", "stg_sch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#stg_sch_restrict_4WC_order2_ref_rwgt.xSection         = 0.65070908604
#stg_sch_restrict_4WC_order2_ref_rwgt.nEvents          = 5000000

# lepton decays
#tt01j_Dilept_restrict_rwgt SM xsec (LO): 91.7780884431 +- 4.27396010612 pb 
#tt01j_Dilept_restrict_rwgt ref point xsec (LO): 276.438705 +- 0.35586 pb 
#After matching: total cross section = 1.176e+02 +- 4.401e+00 pb
#tt01j_Dilept_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("tt01j_Dilept_restrict_4WC_order2_ref_rwgt", "/tt01j_Dilept_restrict/llechner-tt01j_Dilept_restrict-0b79b9f7eebc26f55cce2b3a3c8ffbc3/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#tt01j_Dilept_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "tt01j_Dilept_restrict", "tt01j_Dilept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#tt01j_Dilept_restrict_4WC_order2_ref_rwgt.xSection         = 117.6 #xsec after matching, 276.438705 before matching, 42.5% matching efficiency (run 2.5x more events!)
#tt01j_Dilept_restrict_4WC_order2_ref_rwgt.nEvents          = int(5000000 * 117.6 / 276.438705) #adjust for matching efficiency

#tt01j_SemiLept_restrict_rwgt SM xsec (LO): 305.643575078 +- 9.07989616885 pb 
#tt01j_SemiLept_restrict_rwgt ref point xsec (LO): 904.0769324 +- 0.831361 pb 
#After matching: total cross section = 4.021e+02 +- 1.433e+01 pb
#tt01j_SemiLept_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("tt01j_SemiLept_restrict_4WC_order2_ref_rwgt", "/tt01j_SemiLept_restrict/llechner-tt01j_SemiLept_restrict-5db64ed27da7c89b9af8454cf81f4652/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#tt01j_SemiLept_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "tt01j_SemiLept_restrict", "tt01j_SemiLept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#tt01j_SemiLept_restrict_4WC_order2_ref_rwgt.xSection         = 402.1 #xsec after matching, 904.0769324 before matching, 44.4% matching efficiency (run 2.5x more events!)
#tt01j_SemiLept_restrict_4WC_order2_ref_rwgt.nEvents          = int(5000000 * 402.1 / 904.0769324) #adjust for matching efficiency

#tt01j_Had_restrict_rwgt SM xsec (LO): 248.962760818 +- 13.5734885372 pb 
#tt01j_Had_restrict_rwgt ref point xsec (LO): 743.47548 +- 1.790016 pb 
#After matching: total cross section = 3.286e+02 +- 1.200e+01 pb
#tt01j_Had_restrict_4WC_order2_ref_rwgt                  = FWLiteSample.fromDAS("tt01j_Had_restrict_4WC_order2_ref_rwgt", "/tt01j_Had_restrict/llechner-tt01j_Had_restrict-f7a73630bc5ec4386806d8af3a3bf963/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#tt01j_Had_restrict_4WC_order2_ref_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "tt01j_Had_restrict", "tt01j_Had_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#tt01j_Had_restrict_4WC_order2_ref_rwgt.xSection         = 328.6 #xsec after matching, 743.47548 before matching, 44.2% matching efficiency (run 2.5x more events!)
#tt01j_Had_restrict_4WC_order2_ref_rwgt.nEvents          = int(5000000 * 328.6 / 743.47548) #adjust for matching efficiency

EFT = [
#    ttGamma_SemiLept_restrict_4WC_order2_ref_rwgt,
#    ttGamma_Dilept_restrict_4WC_order2_ref_rwgt,
#    ttGamma_Had_restrict_4WC_order2_ref_rwgt,
#    tt01j_SemiLept_restrict_4WC_order2_ref_rwgt,
#    tt01j_Dilept_restrict_4WC_order2_ref_rwgt,
#    tt01j_Had_restrict_4WC_order2_ref_rwgt,
#    tW_restrict_4WC_order2_ref_rwgt,
#    tWG_restrict_4WC_order2_ref_rwgt,
#    st_tch_restrict_4WC_order2_ref_rwgt,
#    stg_tch_restrict_4WC_order2_ref_rwgt,
#    st_sch_restrict_4WC_order2_ref_rwgt,
#    stg_sch_restrict_4WC_order2_ref_rwgt,
]

#from Samples.Tools.config import redirector_clip_local as redirector
#from Samples.Tools.config import redirector_clip as redirector
#from Samples.Tools.config import redirector_global as redirector


#ttGamma_SemiLept_restrict_rwgt/ttGamma_SemiLept_restrict_rwgt SM xsec (LO) : 4.84740083014 +- 0.164201795725 pb
#ttGamma_SemiLept_restrict_rwgt/ttGamma_SemiLept_restrict_rwgt ref point xsec (LO) : 5.5683434238 +- 0.002784588 pb
#ttGamma_SemiLept_restrict_4WC_ref_rwgt_dim3                  = FWLiteSample.fromDAS("ttGamma_SemiLept_restrict_4WC_ref_rwgt_dim3", "/ttGamma_SemiLept_restrict_rwgt_ref_dim3/llechner-ttGamma_SemiLept_restrict_rwgt_ref_dim3-c667af2b36a80bb7df7d629751130eb8/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#ttGamma_SemiLept_restrict_4WC_ref_rwgt_dim3.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "ttGamma_SemiLept_restrict_rwgt", "ttGamma_SemiLept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#ttGamma_SemiLept_restrict_4WC_ref_rwgt_dim3.xSection         = 5.5683434238 * 1.4852 # 1.994
#ttGamma_SemiLept_restrict_4WC_ref_rwgt_dim3.nEvents          = 20000 * len(ttGamma_SemiLept_restrict_4WC_ref_rwgt_dim3.files)

#ttGamma_Dilept_restrict_rwgt/ttGamma_Dilept_restrict_rwgt SM xsec (LO) : 1.42364456092 +- 0.0893995220222 pb
#ttGamma_Dilept_restrict_rwgt/ttGamma_Dilept_restrict_rwgt ref point xsec (LO) : 1.61851737614 +- 0.001665757 pb
#ttGamma_Dilept_restrict_4WC_ref_rwgt_dim3                    = FWLiteSample.fromDAS("ttGamma_Dilept_restrict_4WC_ref_rwgt_dim3", "/ttGamma_Dilept_restrict_rwgt_ref_dim3/llechner-ttGamma_Dilept_restrict_rwgt_ref_dim3-b57285320665589a75f879325a45239e/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#ttGamma_Dilept_restrict_4WC_ref_rwgt_dim3.reweight_pkl       = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "ttGamma_Dilept_restrict_rwgt", "ttGamma_Dilept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#ttGamma_Dilept_restrict_4WC_ref_rwgt_dim3.xSection           = 1.61851737614 * 1.4852 # 1.616
#ttGamma_Dilept_restrict_4WC_ref_rwgt_dim3.nEvents            = 20000 * len(ttGamma_Dilept_restrict_4WC_ref_rwgt_dim3.files)

#ttGamma_Had_restrict_rwgt/ttGamma_Had_restrict_rwgt SM xsec (LO) : 3.97374503392 +- 0.562422778965 pb
#ttGamma_Had_restrict_rwgt/ttGamma_Had_restrict_rwgt ref point xsec (LO) : 4.668529203 +- 0.00947815 pb
#ttGamma_Had_restrict_4WC_ref_rwgt_dim3                    = FWLiteSample.fromDAS("ttGamma_Had_restrict_4WC_ref_rwgt_dim3", "/ttGamma_Had_restrict_rwgt_ref_dim3/llechner-ttGamma_Had_restrict_rwgt_ref_dim3-8c52d8dc60d4dc6f9921eda098332184/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#ttGamma_Had_restrict_4WC_ref_rwgt_dim3.reweight_pkl       = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "ttGamma_Had_restrict_rwgt", "ttGamma_Had_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#ttGamma_Had_restrict_4WC_ref_rwgt_dim3.xSection           = 4.668529203 * 1.4852 # 1.565
#ttGamma_Had_restrict_4WC_ref_rwgt_dim3.nEvents            = 20000 * len(ttGamma_Had_restrict_4WC_ref_rwgt_dim3.files)

# EFT bkg
# inclusive decays
#tW_rwgt/tW_rwgt SM xsec (LO) : 49.2366970531 +- 1.04500051284 pb
#tW_rwgt/tW_rwgt ref point xsec (LO) : 56.307218076 +- 0.1167354 pb
#tW_restrict_4WC_ref_rwgt_dim3                  = FWLiteSample.fromDAS("tW_restrict_4WC_ref_rwgt_dim3", "/tW_rwgt_ref_dim3/llechner-tW_rwgt_ref_dim3-f5eeddca9a1818f544ceddf0b5b1a2de/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#tW_restrict_4WC_ref_rwgt_dim3.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "tW_rwgt", "tW_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#tW_restrict_4WC_ref_rwgt_dim3.xSection         = 56.307218076
#tW_restrict_4WC_ref_rwgt_dim3.nEvents          = 20000 * len(tW_restrict_4WC_ref_rwgt_dim3.files)

# inclusive decays
#tWG_rwgt/tWG_rwgt SM xsec (LO) : 0.372373387106 +- 0.0147676144766 pb
#tWG_rwgt/tWG_rwgt ref point xsec (LO) : 0.546187763952 +- 0.0007756813 pb
#tWG_restrict_4WC_ref_rwgt_dim3                  = FWLiteSample.fromDAS("tWG_restrict_4WC_ref_rwgt_dim3", "/tWG_rwgt_ref_dim3/llechner-tWG_rwgt_ref_dim3-5a9fed622551fbf3bf93e525967b5280/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#tWG_restrict_4WC_ref_rwgt_dim3.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "tWG_rwgt", "tWG_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#tWG_restrict_4WC_ref_rwgt_dim3.xSection         = 0.546187763952
#tWG_restrict_4WC_ref_rwgt_dim3.nEvents          = 20000 * len(tWG_restrict_4WC_ref_rwgt_dim3.files)

# inclusive decays
#st_tch_rwgt/st_tch_rwgt SM xsec (LO) : 168.515941868 +- 5.92040132896 pb
#st_tch_rwgt/st_tch_rwgt ref point xsec (LO) : 169.28019472 +- 1.07733 pb
#st_tch_restrict_4WC_ref_rwgt_dim3                  = FWLiteSample.fromDAS("st_tch_restrict_4WC_ref_rwgt_dim3", "/st_tch_rwgt_ref_dim3/llechner-st_tch_rwgt_ref_dim3-01581bd1061cabdeb9123588ad82402c/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#st_tch_restrict_4WC_ref_rwgt_dim3.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "st_tch_rwgt", "st_tch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#st_tch_restrict_4WC_ref_rwgt_dim3.xSection         = 169.28019472
#st_tch_restrict_4WC_ref_rwgt_dim3.nEvents          = 20000 * len(st_tch_restrict_4WC_ref_rwgt_dim3.files)

# inclusive decays
#stg_tch_rwgt/stg_tch_rwgt SM xsec (LO) : 3.35597541183 +- 0.105895512067 pb
#stg_tch_rwgt/stg_tch_rwgt ref point xsec (LO) : 3.80225445 +- 0.007775464 pb
#stg_tch_restrict_4WC_ref_rwgt_dim3                  = FWLiteSample.fromDAS("stg_tch_restrict_4WC_ref_rwgt_dim3", "/stg_tch_rwgt_ref_dim3/llechner-stg_tch_rwgt_ref_dim3-bacd46d067e9743098328d28d32e8055/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#stg_tch_restrict_4WC_ref_rwgt_dim3.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "stg_tch_rwgt", "stg_tch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#stg_tch_restrict_4WC_ref_rwgt_dim3.xSection         = 3.80225445
#stg_tch_restrict_4WC_ref_rwgt_dim3.nEvents          = 20000 * len(stg_tch_restrict_4WC_ref_rwgt_dim3.files)

# inclusive decays
#st_sch_rwgt/st_sch_rwgt SM xsec (LO) : 7.70274599862 +- 0.1956385136 pb
#st_sch_rwgt/st_sch_rwgt ref point xsec (LO) : 5.4363000106 +- 0.016096 pb
#st_sch_restrict_4WC_ref_rwgt_dim3                  = FWLiteSample.fromDAS("st_sch_restrict_4WC_ref_rwgt_dim3", "/st_sch_rwgt_ref_dim3/llechner-st_sch_rwgt_ref_dim3-de3a7317749d54438a3418c433dea82f/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#st_sch_restrict_4WC_ref_rwgt_dim3.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "st_sch_rwgt", "st_sch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#st_sch_restrict_4WC_ref_rwgt_dim3.xSection         = 5.4363000106
#st_sch_restrict_4WC_ref_rwgt_dim3.nEvents          = 20000 * len(st_sch_restrict_4WC_ref_rwgt_dim3.files)

# inclusive decays
#stg_sch_rwgt/stg_sch_rwgt SM xsec (LO) : 0.0430771791323 +- 0.00193395520978 pb
#stg_sch_rwgt/stg_sch_rwgt ref point xsec (LO) : 0.038696910317 +- 0.0001018029 pb
#stg_sch_restrict_4WC_ref_rwgt_dim3                  = FWLiteSample.fromDAS("stg_sch_restrict_4WC_ref_rwgt_dim3", "/stg_sch_rwgt_ref_dim3/llechner-stg_sch_rwgt_ref_dim3-196dedb69b9a34640738340ec219b659/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#stg_sch_restrict_4WC_ref_rwgt_dim3.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "stg_sch_rwgt", "stg_sch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#stg_sch_restrict_4WC_ref_rwgt_dim3.xSection         = 0.038696910317
#stg_sch_restrict_4WC_ref_rwgt_dim3.nEvents          = 20000 * len(stg_sch_restrict_4WC_ref_rwgt_dim3.files)

# lepton decays
#tt01j_Dilept_restrict_rwgt/tt01j_Dilept_restrict_rwgt SM xsec (LO) : 94.5447015452 +- 2.5678321686 pb 
#tt01j_Dilept_restrict_rwgt/tt01j_Dilept_restrict_rwgt ref point xsec (LO) : 97.7469795 +- 0.1204569 pb
#After matching: total cross section = 4.394e+01 +- 2.422e+00 pb
#tt01j_Dilept_restrict_4WC_ref_rwgt_dim3                  = FWLiteSample.fromDAS("tt01j_Dilept_restrict_4WC_ref_rwgt_dim3", "/tt01j_Dilept_restrict_rwgt_ref_dim3/llechner-tt01j_Dilept_restrict_rwgt_ref_dim3-ed3f54974e3ea9f23eb8cee84a4f17f1/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#tt01j_Dilept_restrict_4WC_ref_rwgt_dim3.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "tt01j_Dilept_restrict_rwgt", "tt01j_Dilept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#tt01j_Dilept_restrict_4WC_ref_rwgt_dim3.xSection         = 43.94 #xsec after matching, 97.7469795 before matching, 42.5% matching efficiency (run 2.5x more events!)
#tt01j_Dilept_restrict_4WC_ref_rwgt_dim3.nEvents          = int(20000 * len(tt01j_Dilept_restrict_4WC_ref_rwgt_dim3.files) * 43.94 / 97.7469795) #adjust for matching efficiency

#tt01j_SemiLept_restrict_rwgt/tt01j_SemiLept_restrict_rwgt SM xsec (LO) : 314.534639389 +- 4.82884684205 pb
#tt01j_SemiLept_restrict_rwgt/tt01j_SemiLept_restrict_rwgt ref point xsec (LO) : 320.66061004 +- 0.2540632 pb
#After matching: total cross section = 1.429e+02 +- 7.969e+00 pb
#tt01j_SemiLept_restrict_4WC_ref_rwgt_dim3                  = FWLiteSample.fromDAS("tt01j_SemiLept_restrict_4WC_ref_rwgt_dim3", "/tt01j_SemiLept_restrict_rwgt_ref_dim3/llechner-tt01j_SemiLept_restrict_rwgt_ref_dim3-5cb9bd7702827c45090fcba2236a683f/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#tt01j_SemiLept_restrict_4WC_ref_rwgt_dim3.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "medRefdim3", "tt01j_SemiLept_restrict_rwgt", "tt01j_SemiLept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#tt01j_SemiLept_restrict_4WC_ref_rwgt_dim3.xSection         = 142.9 #xsec after matching, 320.66061004 before matching, 44.4% matching efficiency (run 2.5x more events!)
#tt01j_SemiLept_restrict_4WC_ref_rwgt_dim3.nEvents          = int(20000 * len(tt01j_SemiLept_restrict_4WC_ref_rwgt_dim3.files) * 142.9 / 320.66061004) #adjust for matching efficiency


EFT_dim3 = [
#    ttGamma_Dilept_restrict_4WC_ref_rwgt_dim3,
#    ttGamma_SemiLept_restrict_4WC_ref_rwgt_dim3,
#    ttGamma_Had_restrict_4WC_ref_rwgt_dim3,
#    tt01j_Dilept_restrict_4WC_ref_rwgt_dim3,
#    tt01j_SemiLept_restrict_4WC_ref_rwgt_dim3,
#    tW_restrict_4WC_ref_rwgt_dim3,
#    tWG_restrict_4WC_ref_rwgt_dim3,
#    st_tch_restrict_4WC_ref_rwgt_dim3,
#    stg_tch_restrict_4WC_ref_rwgt_dim3,
#    st_sch_restrict_4WC_ref_rwgt_dim3,
#    stg_sch_restrict_4WC_ref_rwgt_dim3,
]

stg_sch_restrict_ref_rwgt_2WC                  = FWLiteSample.fromDAS("stg_sch_restrict_ref_rwgt_2WC", "/stg_sch_rwgt_ref_v3/llechner-stg_sch_rwgt_ref_v3-89064afdbf280d34e266b56f0d026da6/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
stg_sch_restrict_ref_rwgt_2WC.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "singleOp", "stg_sch_rwgt", "stg_sch_rwgt_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
stg_sch_restrict_ref_rwgt_2WC.xSection         = 0.04415
stg_sch_restrict_ref_rwgt_2WC.nEvents          = 20000 * len(stg_sch_restrict_ref_rwgt_2WC.files)

stg_tch_restrict_ref_rwgt_2WC                  = FWLiteSample.fromDAS("stg_tch_restrict_ref_rwgt_2WC", "/stg_tch_rwgt_ref_v3/llechner-stg_tch_rwgt_ref_v3-ef229b6fd4562be8773a73ef5fe5bce3/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
stg_tch_restrict_ref_rwgt_2WC.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "singleOp", "stg_tch_rwgt", "stg_tch_rwgt_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
stg_tch_restrict_ref_rwgt_2WC.xSection         = 3.449
stg_tch_restrict_ref_rwgt_2WC.nEvents          = 20000 * len(stg_tch_restrict_ref_rwgt_2WC.files)

tWG_restrict_ref_rwgt_2WC                  = FWLiteSample.fromDAS("tWG_restrict_ref_rwgt_2WC", "/tWG_rwgt_ref_v3/llechner-tWG_rwgt_ref_v3-d3cb71b945b065c1220425aae4f3dbe2/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
tWG_restrict_ref_rwgt_2WC.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "singleOp", "tWG_rwgt", "tWG_rwgt_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
tWG_restrict_ref_rwgt_2WC.xSection         = 0.3973
tWG_restrict_ref_rwgt_2WC.nEvents          = 20000 * len(tWG_restrict_ref_rwgt_2WC.files)

ttGamma_SemiLept_restrict_ref_rwgt_2WC                  = FWLiteSample.fromDAS("ttGamma_SemiLept_restrict_ref_rwgt_2WC", "/ttGamma_SemiLept_restrict_rwgt_ref_2WC_v3/llechner-ttGamma_SemiLept_restrict_rwgt_ref_2WC_v3-0640206874b70578d88844db8a1a4ded/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
ttGamma_SemiLept_restrict_ref_rwgt_2WC.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "singleOp", "ttGamma_SemiLept_restrict_rwgt_2WC", "ttGamma_SemiLept_restrict_rwgt_2WC_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
ttGamma_SemiLept_restrict_ref_rwgt_2WC.xSection         = 4.753 * 1.4852 # 1.994
ttGamma_SemiLept_restrict_ref_rwgt_2WC.nEvents          = 20000 * len(ttGamma_SemiLept_restrict_ref_rwgt_2WC.files)

ttGamma_Dilept_restrict_ref_rwgt_2WC                  = FWLiteSample.fromDAS("ttGamma_Dilept_restrict_ref_rwgt_2WC", "/ttGamma_Dilept_restrict_rwgt_ref_2WC_v3/llechner-ttGamma_Dilept_restrict_rwgt_ref_2WC_v3-56cbec692fbe86ba20d968d1c4057952/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
ttGamma_Dilept_restrict_ref_rwgt_2WC.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "singleOp", "ttGamma_Dilept_restrict_rwgt_2WC", "ttGamma_Dilept_restrict_rwgt_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
ttGamma_Dilept_restrict_ref_rwgt_2WC.xSection         = 1.409 * 1.4852 # 1.616
ttGamma_Dilept_restrict_ref_rwgt_2WC.nEvents          = 20000 * len(ttGamma_Dilept_restrict_ref_rwgt_2WC.files)

ttGamma_SemiLept_restrict_ctZ2                  = FWLiteSample.fromDAS("ttGamma_SemiLept_restrict_ctZ2", "/ttGamma_SemiLept_restrict_singleOp_ctZ2_v3/llechner-ttGamma_SemiLept_restrict_singleOp_ctZ2_v3-42415c605bfefc1bae768a0414d5f542/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
ttGamma_SemiLept_restrict_ctZ2.xSection         =  4.925 * 1.4852 # 1.994
ttGamma_SemiLept_restrict_ctZ2.nEvents          = 20000 * len(ttGamma_SemiLept_restrict_ctZ2.files)

ttGamma_SemiLept_restrict_ctW2                  = FWLiteSample.fromDAS("ttGamma_SemiLept_restrict_ctW2", "/ttGamma_SemiLept_restrict_singleOp_ctW2/llechner-ttGamma_SemiLept_restrict_singleOp_ctW2-f6fd16ed73d49ac7b3424300441bc1f4/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
ttGamma_SemiLept_restrict_ctW2.xSection         =  4.825 * 1.4852 # 1.994
ttGamma_SemiLept_restrict_ctW2.nEvents          = 10000 * len(ttGamma_SemiLept_restrict_ctW2.files)

ttGamma_SemiLept_restrict_ctZI2                  = FWLiteSample.fromDAS("ttGamma_SemiLept_restrict_ctZI2", "/ttGamma_SemiLept_restrict_singleOp_ctZI2_v3/llechner-ttGamma_SemiLept_restrict_singleOp_ctZI2_v3-2fe29daa6135711d3f381b8d439a66a5/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
ttGamma_SemiLept_restrict_ctZI2.xSection         =  4.936 * 1.4852 # 1.994
ttGamma_SemiLept_restrict_ctZI2.nEvents          = 20000 * len(ttGamma_SemiLept_restrict_ctZI2.files)

ttGamma_SemiLept_restrict_ctWI2                  = FWLiteSample.fromDAS("ttGamma_SemiLept_restrict_ctWI2", "/ttGamma_SemiLept_restrict_singleOp_ctWI2/llechner-ttGamma_SemiLept_restrict_singleOp_ctWI2-2fb480a33a2a85c17a542ad97668e4e2/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
ttGamma_SemiLept_restrict_ctWI2.xSection         =  4.935 * 1.4852 # 1.994
ttGamma_SemiLept_restrict_ctWI2.nEvents          = 10000 * len(ttGamma_SemiLept_restrict_ctWI2.files)

ttGamma_SemiLept_restrict_ctZm1                  = FWLiteSample.fromDAS("ttGamma_SemiLept_restrict_ctZm1", "/ttGamma_SemiLept_restrict_singleOp_ctZm1_v3/llechner-ttGamma_SemiLept_restrict_singleOp_ctZm1_v3-c8c707208e2368c5285c97d21dd7e19a/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
ttGamma_SemiLept_restrict_ctZm1.xSection         =  4.727 * 1.4852 # 1.994
ttGamma_SemiLept_restrict_ctZm1.nEvents          = 20000 * len(ttGamma_SemiLept_restrict_ctZm1.files)

ttGamma_SemiLept_restrict_ctWm1                  = FWLiteSample.fromDAS("ttGamma_SemiLept_restrict_ctWm1", "/ttGamma_SemiLept_restrict_singleOp_ctWm1/llechner-ttGamma_SemiLept_restrict_singleOp_ctWm1-4681ca7f134f63fff63b4e4abd56c103/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
ttGamma_SemiLept_restrict_ctWm1.xSection         =  4.87 * 1.4852 # 1.994
ttGamma_SemiLept_restrict_ctWm1.nEvents          = 10000 * len(ttGamma_SemiLept_restrict_ctWm1.files)

ttGamma_SemiLept_restrict_ctZIm1                  = FWLiteSample.fromDAS("ttGamma_SemiLept_restrict_ctZIm1", "/ttGamma_SemiLept_restrict_singleOp_ctZIm1_v3/llechner-ttGamma_SemiLept_restrict_singleOp_ctZIm1_v3-7d87abf868c46c9b9a078fda3b10ec5c/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
ttGamma_SemiLept_restrict_ctZIm1.xSection         =  4.699 * 1.4852 # 1.994
ttGamma_SemiLept_restrict_ctZIm1.nEvents          = 20000 * len(ttGamma_SemiLept_restrict_ctZIm1.files)

ttGamma_SemiLept_restrict_ctWIm1                  = FWLiteSample.fromDAS("ttGamma_SemiLept_restrict_ctWIm1", "/ttGamma_SemiLept_restrict_singleOp_ctWIm1/llechner-ttGamma_SemiLept_restrict_singleOp_ctWIm1-aefcf5495f5626fff9fffaee8996af99/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
ttGamma_SemiLept_restrict_ctWIm1.xSection         =  4.818 * 1.4852 # 1.994
ttGamma_SemiLept_restrict_ctWIm1.nEvents          = 10000 * len(ttGamma_SemiLept_restrict_ctWIm1.files)

ttGamma_SemiLept_restrict_SM                      = FWLiteSample.fromDAS("ttGamma_SemiLept_restrict_SM", "/ttGamma_SemiLept_restrict_singleOp_SM_v3/llechner-ttGamma_SemiLept_restrict_singleOp_SM_v3-cb8bb7da15fae1d68fcedeb20add8c5a/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
ttGamma_SemiLept_restrict_SM.xSection             = 4.616 * 1.4852 # 1.994
ttGamma_SemiLept_restrict_SM.nEvents              = 20000 * len(ttGamma_SemiLept_restrict_SM.files)


EFT_ctZ = [
    stg_sch_restrict_ref_rwgt_2WC,
    stg_tch_restrict_ref_rwgt_2WC,
    tWG_restrict_ref_rwgt_2WC,
    ttGamma_SemiLept_restrict_ref_rwgt_2WC,
    ttGamma_Dilept_restrict_ref_rwgt_2WC,
    ttGamma_SemiLept_restrict_ctZ2,
    ttGamma_SemiLept_restrict_ctW2,
    ttGamma_SemiLept_restrict_ctZI2,
    ttGamma_SemiLept_restrict_ctWI2,
    ttGamma_SemiLept_restrict_ctZm1,
    ttGamma_SemiLept_restrict_ctWm1,
    ttGamma_SemiLept_restrict_ctZIm1,
    ttGamma_SemiLept_restrict_ctWIm1,
    ttGamma_SemiLept_restrict_SM,
]


#ttGamma_SemiLept_restrict_rwgt/ttGamma_SemiLept_restrict_rwgt SM xsec (LO) : 4.71380910627 +- 0.41330850793 pb 
#ttGamma_SemiLept_restrict_rwgt/ttGamma_SemiLept_restrict_rwgt ref point xsec (LO) : 3.579146736 +- 0.002020074 pb 
#ttGamma_SemiLept_restrict_4WC_medRef_rwgt                  = FWLiteSample.fromDAS("ttGamma_SemiLept_restrict_4WC_medRef_rwgt", "/ttGamma_SemiLept_restrict_rwgt_medRef/llechner-ttGamma_SemiLept_restrict_rwgt_medRef-c667af2b36a80bb7df7d629751130eb8/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#ttGamma_SemiLept_restrict_4WC_medRef_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "medRef", "ttGamma_SemiLept_restrict_rwgt", "ttGamma_SemiLept_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#ttGamma_SemiLept_restrict_4WC_medRef_rwgt.xSection         = 4.87946500443 * 1.4852 # 1.994
#ttGamma_SemiLept_restrict_4WC_medRef_rwgt.nEvents          = 20000 * len(ttGamma_SemiLept_restrict_4WC_medRef_rwgt.files)

#ttGamma_SemiLept_restrict_4WC_medRef_rwgt_dim2                  = FWLiteSample.fromDAS("ttGamma_SemiLept_restrict_4WC_medRef_rwgt_dim2", "/ttGamma_SemiLept_restrict_rwgt_medRef_dim2/llechner-ttGamma_SemiLept_restrict_rwgt_medRef_dim2-6a7a1c3e9c192edc03722859cc9141ef/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#ttGamma_SemiLept_restrict_4WC_medRef_rwgt_dim2.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "medRef", "ttGamma_SemiLept_restrict_rwgt_dim2", "ttGamma_SemiLept_restrict_rwgt_dim2_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#ttGamma_SemiLept_restrict_4WC_medRef_rwgt_dim2.xSection         = 4.87946500443 * 1.4852 # 1.994
#ttGamma_SemiLept_restrict_4WC_medRef_rwgt_dim2.nEvents          = 20000 * len(ttGamma_SemiLept_restrict_4WC_medRef_rwgt_dim2.files)

#ttGamma_SemiLept_restrict_4WC_medRef_rwgt_dim3                  = FWLiteSample.fromDAS("ttGamma_SemiLept_restrict_4WC_medRef_rwgt_dim3", "/ttGamma_SemiLept_restrict_rwgt_medRef_dim3/llechner-ttGamma_SemiLept_restrict_rwgt_medRef_dim3-4d0a51796f8068d09fb74bb9a71d1495/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#ttGamma_SemiLept_restrict_4WC_medRef_rwgt_dim3.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "medRef", "ttGamma_SemiLept_restrict_rwgt_dim3", "ttGamma_SemiLept_restrict_rwgt_dim3_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#ttGamma_SemiLept_restrict_4WC_medRef_rwgt_dim3.xSection         = 4.87946500443 * 1.4852 # 1.994
#ttGamma_SemiLept_restrict_4WC_medRef_rwgt_dim3.nEvents          = 20000 * len(ttGamma_SemiLept_restrict_4WC_medRef_rwgt_dim3.files)

#ttGamma_restrict_4WC_medRef_rwgt                  = FWLiteSample.fromDAS("ttGamma_restrict_4WC_medRef_rwgt", "/ttGamma_restrict_rwgt_medRef/llechner-ttGamma_restrict_rwgt_medRef-7a1684c2d364fb87a18e56ea7700cc86/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
#ttGamma_restrict_4WC_medRef_rwgt.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "medRef", "ttGamma_restrict_rwgt", "ttGamma_restrict_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#ttGamma_restrict_4WC_medRef_rwgt.xSection         = 4.87946500443 * 1.4852 # 1.994
#ttGamma_restrict_4WC_medRef_rwgt.nEvents          = 20000 * len(ttGamma_restrict_4WC_medRef_rwgt.files)

EFT_lowRef = [
#    ttGamma_SemiLept_restrict_4WC_medRef_rwgt,
#    ttGamma_SemiLept_restrict_4WC_medRef_rwgt_dim2,
#    ttGamma_SemiLept_restrict_4WC_medRef_rwgt_dim3,
#    ttGamma_restrict_4WC_medRef_rwgt,
]



# inclusive decays
#stg_tch_rwgt_weightWidth SM xsec (LO): 3.47677257521 +- 0.58170023496 pb
#stg_tch_rwgt_weightWidth ref point xsec (LO): 5.933654149 +- 0.02610673 pb
#test                  = FWLiteSample.fromDirectory("test", "/eos/vbc/user/lukas.lechner/TTGammaEFT/test/")
#test.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "stg_tch_rwgt", "stg_tch_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#test.reweight_pkl     = os.path.join( gridpack_directory, "EFT", "dipoles", "singleOp", "ttGamma_Dilept_restrict_rwgt_2WC", "ttGamma_Dilept_restrict_rwgt_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.pkl" )
#test.reweight_pkl     = "/mnt/hephy/cms/lukas.lechner/gridpacks/TTGammaEFT/gridpacks/EFT/dipoles/singleOp/ttGamma_SemiLept_restrict_rwgt_2WC_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.pkl"
#test.xSection         = 5.933654149
#test.nEvents          = 400

allSamples = EFT_lowRef + EFT_ctZ + EFT_dim3 + EFT #+ [test]


for s in allSamples:
#    try:
#        if not os.path.exists(s.reweight_pkl): print s.reweight_pkl
#    except:
#        pass
#    print s.files[0]
    s.isData = False

#for s in EFT_ctZ:
#    print s.nEvents
#    print len(s.files)
#    for f in s.files:
#        if not os.path.exists(f):
#            print f





