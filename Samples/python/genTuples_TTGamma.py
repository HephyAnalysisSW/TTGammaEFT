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

dbFile = cache_directory + "/samples/DB_TTGamma_GEN.sql"

logger.info( "Using db file: %s", dbFile )

# SM point, no weights
# test samples
TTGamma_SingleLeptFromT_SM_1Line_test                     = FWLiteSample.fromDAS("TTGamma_SingleLeptFromT_SM_1Line_test", "/TTGamma_SingleLeptFromT_1Line_test_GENSIM/llechner-TTGamma_SingleLeptFromT_1Line_test_GENSIM-b3122b77720ca80362007ff086008b03/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
TTGamma_SingleLeptFromT_SM_1Line_test.reweight_pkl        = os.path.join( gridpack_directory, "SM/TTGamma_SingleLeptFromT_1Line_test/", "TTGamma_SingleLeptFromT_1Line_test_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.pkl" )
TTGamma_SingleLeptFromT_SM_1Line_test.xSection            = 0.1267
TTGamma_SingleLeptFromT_SM_1Line_test.nEvents             = 100000

TTGamma_SingleLeptFromT_SM_3LineBuggy_test                = FWLiteSample.fromDAS("TTGamma_SingleLeptFromT_SM_3LineBuggy_test", "/TTGamma_SingleLeptFromT_3LineBuggy_test_GENSIM/llechner-TTGamma_SingleLeptFromT_3LineBuggy_test_GENSIM-f3ebe776d7309479b1058aff34e27155/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
TTGamma_SingleLeptFromT_SM_3LineBuggy_test.reweight_pkl   = os.path.join( gridpack_directory, "SM/TTGamma_SingleLeptFromT_3LineBuggy_test/", "TTGamma_SingleLeptFromT_3LineBuggy_test_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.pkl" )
TTGamma_SingleLeptFromT_SM_3LineBuggy_test.xSection       = 0.1266
TTGamma_SingleLeptFromT_SM_3LineBuggy_test.nEvents        = 100000

TTGamma_SingleLeptFromT_SM_3LinePatched_test              = FWLiteSample.fromDAS("TTGamma_SingleLeptFromT_SM_3LinePatched_test", "/TTGamma_SingleLeptFromT_3LinePatched_test_GENSIM/llechner-TTGamma_SingleLeptFromT_3LinePatched_test_GENSIM-e94234d067bc2f081eff982fc497c503/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
TTGamma_SingleLeptFromT_SM_3LinePatched_test.reweight_pkl = os.path.join( gridpack_directory, "SM/TTGamma_SingleLeptFromT_3LinePatched_test/", "TTGamma_SingleLeptFromT_3LinePatched_test_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.pkl" )
TTGamma_SingleLeptFromT_SM_3LinePatched_test.xSection     = 0.1293
TTGamma_SingleLeptFromT_SM_3LinePatched_test.nEvents      = 100000

# full proc card
TTGamma_SingleLeptFromT_SM_1Line                          = FWLiteSample.fromDAS("TTGamma_SingleLeptFromT_SM_1Line", "/TTGamma_SingleLeptFromT_1Line_SM_GENSIM_v2/llechner-TTGamma_SingleLeptFromT_1Line_SM_GENSIM_v2-75ed994ddf291590a34f99ee2b8b5398/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
TTGamma_SingleLeptFromT_SM_1Line.reweight_pkl             = os.path.join( gridpack_directory, "SM/TTGamma_SingleLeptFromT_1Line/", "TTGamma_SingleLeptFromT_1Line_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.pkl" )
TTGamma_SingleLeptFromT_SM_1Line.xSection                 = 0.7491
TTGamma_SingleLeptFromT_SM_1Line.nEvents                  = 100000

TTGamma_SingleLeptFromT_SM_3LinePatched                   = FWLiteSample.fromDAS("TTGamma_SingleLeptFromT_SM_3LinePatched", "/TTGamma_SingleLeptFromT_3LinePatched_SM_GENSIM/llechner-TTGamma_SingleLeptFromT_3LinePatched_SM_GENSIM-cf918753c14f0b139153df060b08cdc2/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
TTGamma_SingleLeptFromT_SM_3LinePatched.reweight_pkl      = os.path.join( gridpack_directory, "SM/TTGamma_SingleLeptFromT_3LinePatched/", "TTGamma_SingleLeptFromT_3LinePatched_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.pkl" )
TTGamma_SingleLeptFromT_SM_3LinePatched.xSection          = 0.7664
TTGamma_SingleLeptFromT_SM_3LinePatched.nEvents           = 100000

# EFT weights included + reference point
TTGamma_SingleLeptFromT_EFT_1Line_test                    = FWLiteSample.fromDAS("TTGamma_SingleLeptFromT_EFT_1Line_test", "/TTGamma_SingleLeptFromT_1Line_EFT_test_GENSIM/llechner-TTGamma_SingleLeptFromT_1Line_EFT_test_GENSIM-c9d6edd965db7012e7f57ed560889b60/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
TTGamma_SingleLeptFromT_EFT_1Line_test.reweight_pkl       = os.path.join( gridpack_directory, "EFT/TTGamma_SingleLeptFromT_1Line_EFT_test/", "TTGamma_SingleLeptFromT_1Line_EFT_test_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.pkl" )
TTGamma_SingleLeptFromT_EFT_1Line_test.xSection           = 0.1724
TTGamma_SingleLeptFromT_EFT_1Line_test.nEvents            = 100000

TTGamma_DiLept_EFT_1Line_small                            = FWLiteSample.fromDAS("TTGamma_DiLept_EFT_1Line_small", "/TTGamma_DiLept_1Line_EFT_GENSIM_small_v2/llechner-TTGamma_DiLept_1Line_EFT_GENSIM_small_v2-f2b65dd54e97daa1934ff1f579c2bf2e/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
TTGamma_DiLept_EFT_1Line_small.reweight_pkl               = os.path.join( gridpack_directory, "EFT/TTGamma_DiLept_1Line_EFT/", "TTGamma_DiLept_1Line_EFT_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.pkl" )
TTGamma_DiLept_EFT_1Line_small.xSection                   = 0.3948
TTGamma_DiLept_EFT_1Line_small.nEvents                    = 100000

TTGamma_DiLept_EFT_1Line                                  = FWLiteSample.fromDAS("TTGamma_DiLept_EFT_1Line", "/TTGamma_DiLept_1Line_EFT_GENSIM_v3/llechner-TTGamma_DiLept_1Line_EFT_GENSIM_v3-f2b65dd54e97daa1934ff1f579c2bf2e/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
TTGamma_DiLept_EFT_1Line.reweight_pkl                     = os.path.join( gridpack_directory, "EFT/TTGamma_DiLept_1Line_EFT/", "TTGamma_DiLept_1Line_EFT_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.pkl" )
TTGamma_DiLept_EFT_1Line.xSection                         = 0.3948
TTGamma_DiLept_EFT_1Line.nEvents                          = 1000000

TTGamma_SingleLeptFromT_EFT_1Line                         = FWLiteSample.fromDAS("TTGamma_SingleLeptFromT_EFT_1Line", "/TTGamma_SingleLeptFromT_1Line_EFT_GENSIM_v3/llechner-TTGamma_SingleLeptFromT_1Line_EFT_GENSIM_v3-727ec4c92973027c1a2b5c77f6a1ad97/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
TTGamma_SingleLeptFromT_EFT_1Line.reweight_pkl            = os.path.join( gridpack_directory, "newEFT/TTGamma_SingleLeptFromT_1Line_EFT/", "TTGamma_SingleLeptFromT_1Line_EFT_reweight_card.pkl" )
TTGamma_SingleLeptFromT_EFT_1Line.xSection                = 0.664
TTGamma_SingleLeptFromT_EFT_1Line.nEvents                 = 1000000

TTGamma_SingleLeptFromTbar_EFT_1Line                      = FWLiteSample.fromDAS("TTGamma_SingleLeptFromTbar_EFT_1Line", "/TTGamma_SingleLeptFromTbar_1Line_EFT_GENSIM_v3/llechner-TTGamma_SingleLeptFromTbar_1Line_EFT_GENSIM_v3-8f460aa69f1845634346ff2facddea4c/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
TTGamma_SingleLeptFromTbar_EFT_1Line.reweight_pkl         = os.path.join( gridpack_directory, "newEFT/TTGamma_SingleLeptFromTbar_1Line_EFT/", "TTGamma_SingleLeptFromTbar_1Line_EFT_reweight_card.pkl" )
TTGamma_SingleLeptFromTbar_EFT_1Line.xSection             = 0.6611
TTGamma_SingleLeptFromTbar_EFT_1Line.nEvents              = 1000000

#################################
### New Generation of Samples ###
#################################

# Comparing SM 1Line to central samples
# central samples are produced with central gridpack + processed with modified 71X gen cfg
# 1Line samples are produced with central gridpack production repo 93X + usual 93X cfg

# Private 1Line Production
ttGamma_SingleLeptFromT_SM_1Line                 = FWLiteSample.fromDAS("ttGamma_SingleLeptFromT_SM_1Line", "/ttGamma_SingleLeptFromT_1line_5f_ckm_LO_v2/llechner-ttGamma_SingleLeptFromT_1line_5f_ckm_LO_v2-3da16231862a69c7a8ab2bd0d654d28a/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_SingleLeptFromT_SM_1Line.xSection        = 0.7092
ttGamma_SingleLeptFromT_SM_1Line.nEvents         = 100000

ttGamma_SingleLeptFromTbar_SM_1Line              = FWLiteSample.fromDAS("ttGamma_SingleLeptFromTbar_SM_1Line", "/ttGamma_SingleLeptFromTbar_1line_5f_ckm_LO_v2/llechner-ttGamma_SingleLeptFromTbar_1line_5f_ckm_LO_v2-d188e1ef76b4c681de518734d4a7e505/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_SingleLeptFromTbar_SM_1Line.xSection     = 0.7068
ttGamma_SingleLeptFromTbar_SM_1Line.nEvents      = 100000

# Central Samples
ttGamma_SingleLeptFromT_SM_central               = FWLiteSample.fromDAS("ttGamma_SingleLeptFromT_SM_central", "/ttGamma_SingleLeptFromT_5f_ckm_LO_central_v3/llechner-ttGamma_SingleLeptFromT_5f_ckm_LO_central_v3-f6bd36bbeee1fb1571f3e5f5514cd426/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_SingleLeptFromT_SM_central.xSection      = 0.7772
ttGamma_SingleLeptFromT_SM_central.nEvents       = 100000

ttGamma_SingleLeptFromTbar_SM_central            = FWLiteSample.fromDAS("ttGamma_SingleLeptFromTbar_SM_central", "/ttGamma_SingleLeptFromTbar_5f_ckm_LO_central_v3/llechner-ttGamma_SingleLeptFromTbar_5f_ckm_LO_central_v3-dda6ab68465cb0862bad77d9f61ac2c5/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_SingleLeptFromTbar_SM_central.xSection   = 0.7749
ttGamma_SingleLeptFromTbar_SM_central.nEvents    = 100000

#TTGamma_Dilept_SM_central                        = FWLiteSample.fromDAS("ttGamma_Dilept_SM_central", "", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
#TTGamma_Dilept_SM_central.xSection               = 0.6353
#TTGamma_Dilept_SM_central.nEvents                = 100000

ttGamma_Hadronic_SM_central                      = FWLiteSample.fromDAS("ttGamma_Hadronic_SM_central", "/ttGamma_Hadronic_5f_ckm_LO_central_v3/llechner-ttGamma_Hadronic_5f_ckm_LO_central_v3-a0b185cb632020d2d97d17a4c2a505b7/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_Hadronic_SM_central.xSection             = 0.7998
ttGamma_Hadronic_SM_central.nEvents              = 100000

# Run Card checks
ttGamma_NoFullyHad_SM_ATLASrunCard                = FWLiteSample.fromDAS("ttGamma_NoFullyHad_SM_ATLASrunCard", "/ttGamma_1Line_noFullyHad_ATLASrunCard/llechner-ttGamma_1Line_noFullyHad_ATLASrunCard-02683d38485cee1dd1397b4ddb798321/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_NoFullyHad_SM_ATLASrunCard.xSection       = 3.981
ttGamma_NoFullyHad_SM_ATLASrunCard.nEvents        = 1000000

ttGamma_NoFullyHad_SM_ATLASrunCard_small          = FWLiteSample.fromDAS("ttGamma_NoFullyHad_SM_ATLASrunCard_small", "/ttGamma_1Line_noFullyHad_ATLASrunCard_small/llechner-ttGamma_1Line_noFullyHad_ATLASrunCard_small-02683d38485cee1dd1397b4ddb798321/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_NoFullyHad_SM_ATLASrunCard_small.xSection = 3.981
ttGamma_NoFullyHad_SM_ATLASrunCard_small.nEvents  = 100000

ttGamma_NoFullyHad_SM_CMSrunCard_small            = FWLiteSample.fromDAS("ttGamma_NoFullyHad_SM_CMSrunCard_small", "/ttGamma_1Line_noFullyHad_CMSrunCard_small/llechner-ttGamma_1Line_noFullyHad_CMSrunCard_small-e6011fb4f3367f8efd038accaa47598b/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_NoFullyHad_SM_CMSrunCard_small.xSection   = 2.178
ttGamma_NoFullyHad_SM_CMSrunCard_small.nEvents    = 100000

ttGamma_NoFullyHad_SM_CMSrunCard                  = FWLiteSample.fromDAS("ttGamma_NoFullyHad_SM_CMSrunCard", "/ttGamma_1Line_noFullyHad_CMSrunCard/llechner-ttGamma_1Line_noFullyHad_CMSrunCard-e6011fb4f3367f8efd038accaa47598b/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_NoFullyHad_SM_CMSrunCard.xSection         = 2.178
ttGamma_NoFullyHad_SM_CMSrunCard.nEvents          = 1000000

ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR                     = FWLiteSample.fromDAS("ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR", "/ttGamma_1Line_noFullyHad_CMSrunCard_noDeltaR/llechner-ttGamma_1Line_noFullyHad_CMSrunCard_noDeltaR-c2e391c44b70e1bad2250ba48e7ad1c0/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR.xSection            = 2.614
ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR.nEvents             = 1000000

ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_xqcut               = FWLiteSample.fromDAS("ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_xqcut", "/ttGamma_1Line_noFullyHad_CMSrunCard_noDeltaR_xqcut/llechner-ttGamma_1Line_noFullyHad_CMSrunCard_noDeltaR_xqcut-7d13ea5bdcd99d34a8947ea1d7dc8334/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_xqcut.xSection      = 2.744
ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_xqcut.nEvents       = 1000000

ttGamma_NoFullyHad_SM_CMSrunCard_xqcut                        = FWLiteSample.fromDAS("ttGamma_NoFullyHad_SM_CMSrunCard_xqcut", "/ttGamma_1Line_noFullyHad_CMSrunCard_xqcut/llechner-ttGamma_1Line_noFullyHad_CMSrunCard_xqcut-69ad80f217aab28731bfb3c4efec1e3a/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_NoFullyHad_SM_CMSrunCard_xqcut.xSection               = 2.055
ttGamma_NoFullyHad_SM_CMSrunCard_xqcut.nEvents                = 1000000

ttGamma_NoFullyHad_SM_CMSrunCard_noJetPtCut                   = FWLiteSample.fromDAS("ttGamma_NoFullyHad_SM_CMSrunCard_noJetPtCut", "/ttGamma_1Line_noFullyHad_CMSrunCard_noJetPtCut/llechner-ttGamma_1Line_noFullyHad_CMSrunCard_noJetPtCut-afd89d7215542c3edcf4e47d82b47667/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_NoFullyHad_SM_CMSrunCard_noJetPtCut.xSection          = 2.178
ttGamma_NoFullyHad_SM_CMSrunCard_noJetPtCut.nEvents           = 995000

ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut_xqcut          = FWLiteSample.fromDAS("ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut_xqcut", "/ttGamma_1Line_noFullyHad_CMSrunCard_noDeltaR_noJetPtCut_xqcut/llechner-ttGamma_1Line_noFullyHad_CMSrunCard_noDeltaR_noJetPtCut_xqcut-aaa0a2d36aff549c554c58121e7f57c7/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut_xqcut.xSection = 4.138
ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut_xqcut.nEvents  = 1000000

ttGamma_NoFullyHad_SM_CMSrunCard_noJetPtCut_xqcut          = FWLiteSample.fromDAS("ttGamma_NoFullyHad_SM_CMSrunCard_noJetPtCut_xqcut", "/ttGamma_1Line_noFullyHad_CMSrunCard_noJetPtCut_xqcut_v2/llechner-ttGamma_1Line_noFullyHad_CMSrunCard_noJetPtCut_xqcut_v2-8ee018b7e9168c36abbeb423731d4136/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_NoFullyHad_SM_CMSrunCard_noJetPtCut_xqcut.xSection = 3.1
ttGamma_NoFullyHad_SM_CMSrunCard_noJetPtCut_xqcut.nEvents  = 1000000

ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut          = FWLiteSample.fromDAS("ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut", "/ttGamma_1Line_noFullyHad_CMSrunCard_noDeltaR_noJetPtCut_v2/llechner-ttGamma_1Line_noFullyHad_CMSrunCard_noDeltaR_noJetPtCut_v2-4f55cdb9331a749a20a4bc50482fb2ca/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut.xSection = 5.527
ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut.nEvents  = 1000000

ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut_xqcut_wideLepEta          = FWLiteSample.fromDAS("ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut_xqcut_wideLepEta", "/ttGamma_1Line_noFullyHad_CMSrunCard_noDeltaR_noJetPtCut_xqcut_wideLepEta/llechner-ttGamma_1Line_noFullyHad_CMSrunCard_noDeltaR_noJetPtCut_xqcut_wideLepEta-f709eb426af1740e1b0fee8558bc8aab/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut_xqcut_wideLepEta.xSection = 4.535
ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut_xqcut_wideLepEta.nEvents  = 995000

ttGamma_NoFullyHad_SM_TTBarrunCard                  = FWLiteSample.fromDAS("ttGamma_NoFullyHad_SM_TTBarrunCard", "/ttGamma_1Line_noFullyHad_TTBarrunCard_v2/llechner-ttGamma_1Line_noFullyHad_TTBarrunCard_v2-1d2fefe5e8f8ca18fa7ce16fa7fd3f92/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_NoFullyHad_SM_TTBarrunCard.xSection         = 7.495
ttGamma_NoFullyHad_SM_TTBarrunCard.nEvents          = 1000000

ttGamma_NoFullyHad_SM_TTBarrunCard_modified                  = FWLiteSample.fromDAS("ttGamma_NoFullyHad_SM_TTBarrunCard_modified", "/ttGamma_1Line_noFullyHad_TTBarrunCard_modified/llechner-ttGamma_1Line_noFullyHad_TTBarrunCard_modified-e3ad6238f1aa89850d9606dd6e9ea78a/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_NoFullyHad_SM_TTBarrunCard_modified.xSection         = 6.645
ttGamma_NoFullyHad_SM_TTBarrunCard_modified.nEvents          = 1000000

ttGamma_NoFullyHad_SM_TTBarrunCard_mllOnly                  = FWLiteSample.fromDAS("ttGamma_NoFullyHad_SM_TTBarrunCard_mllOnly", "/ttGamma_1Line_noFullyHad_TTBarrunCard_mllOnly/llechner-ttGamma_1Line_noFullyHad_TTBarrunCard_mllOnly-cdfd1b757b5d10296da2bda80929ba43/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_NoFullyHad_SM_TTBarrunCard_mllOnly.xSection         = 4.285
ttGamma_NoFullyHad_SM_TTBarrunCard_mllOnly.nEvents          = 995000


# Private 1Line Production, new run card
ttGamma_Dilept_newCentral_1Line                 = FWLiteSample.fromDAS("ttGamma_Dilept_newCentral_1Line", "/ttGamma_1Line_Dilept/llechner-ttGamma_1Line_Dilept-ad7c181eaba4dcf9b36e872f951a2fd9/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_Dilept_newCentral_1Line.xSection        = 1.512
ttGamma_Dilept_newCentral_1Line.nEvents         = 960000

ttGamma_SemiLept_newCentral_1Line               = FWLiteSample.fromDAS("ttGamma_SemiLept_newCentral_1Line", "/ttGamma_1Line_SemiLept/llechner-ttGamma_1Line_SemiLept-278d719001d8ddc9de05a9c5f6ca8736/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_SemiLept_newCentral_1Line.xSection      = 5.125
ttGamma_SemiLept_newCentral_1Line.nEvents       = 980000

ttGamma_Had_newCentral_1Line                    = FWLiteSample.fromDAS("ttGamma_Had_newCentral_1Line", "/ttGamma_1Line_Had/llechner-ttGamma_1Line_Had-141227a8e6d27ca9a0e4ef7748f55f6c/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_Had_newCentral_1Line.xSection           = 4.213
ttGamma_Had_newCentral_1Line.nEvents            = 995000

ttGamma_NoFullyHad_newCentral_1Line             = FWLiteSample.fromDAS("ttGamma_NoFullyHad_newCentral_1Line", "/ttGamma_1Line_NoFullyHad_v2/llechner-ttGamma_1Line_NoFullyHad_v2-17628da6eab494c9f81686715e5b9d62/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_NoFullyHad_newCentral_1Line.xSection    = 6.634
ttGamma_NoFullyHad_newCentral_1Line.nEvents     = 970000



# Sample comparison
ttGamma_NoFullyHad_newCentral_1Line_comp             = FWLiteSample.fromDAS("ttGamma_NoFullyHad_newCentral_1Line_comp", "/ttGamma_1Line_NoFullyHad_v2/llechner-ttGamma_1Line_NoFullyHad_v2-17628da6eab494c9f81686715e5b9d62/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_NoFullyHad_newCentral_1Line_comp.xSection    = 6.634
ttGamma_NoFullyHad_newCentral_1Line_comp.nEvents     = 1000000

ttGamma_NoFullyHad_SM_ATLASrunCard_comp                = FWLiteSample.fromDAS("ttGamma_NoFullyHad_SM_ATLASrunCard_comp", "/ttGamma_1Line_noFullyHad_ATLASrunCard/llechner-ttGamma_1Line_noFullyHad_ATLASrunCard-02683d38485cee1dd1397b4ddb798321/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_NoFullyHad_SM_ATLASrunCard_comp.xSection       = 3.981
ttGamma_NoFullyHad_SM_ATLASrunCard_comp.nEvents        = 1000000

ttGamma_NoFullyHad_newCentral_1Line_pTG100To200_comp             = FWLiteSample.fromDAS("ttGamma_NoFullyHad_newCentral_1Line_pTG100To200_comp", "/ttGamma_1Line_NoFullyHad_pTG100To200/llechner-ttGamma_1Line_NoFullyHad_pTG100To200-247c852135d86d5cd6079d15fa626189/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_NoFullyHad_newCentral_1Line_pTG100To200_comp.xSection    = 0.168
ttGamma_NoFullyHad_newCentral_1Line_pTG100To200_comp.nEvents     = 1000000

ttGamma_NoFullyHad_newCentral_1Line_pTGgt200_comp             = FWLiteSample.fromDAS("ttGamma_NoFullyHad_newCentral_1Line_pTGgt200_comp", "/ttGamma_1Line_NoFullyHad_pTGgt200/llechner-ttGamma_1Line_NoFullyHad_pTGgt200-3ec61e47eafa562ce3b543e2a9f923a7/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_NoFullyHad_newCentral_1Line_pTGgt200_comp.xSection    = 0.0342
ttGamma_NoFullyHad_newCentral_1Line_pTGgt200_comp.nEvents     = 795000

ttGamma_NoFullyHad_newCentral_1Line_Herwig             = FWLiteSample.fromDAS("ttGamma_NoFullyHad_newCentral_1Line_Herwig", "/ttGamma_1Line_NoFullyHad_Herwig_v2/llechner-ttGamma_1Line_NoFullyHad_Herwig_v2-d9fd44f63ec1bf900df78889a8ad4c5a/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_NoFullyHad_newCentral_1Line_Herwig.xSection    = 6.634
ttGamma_NoFullyHad_newCentral_1Line_Herwig.nEvents     = 95000

#noLHE
ttGamma_NoFullyHad_noLHE_1Line_Herwig             = FWLiteSample.fromDAS("ttGamma_NoFullyHad_noLHE_1Line_Herwig", "/ttGamma_1Line_NoFullyHad_noLHE_herwigpp/llechner-ttGamma_1Line_NoFullyHad_noLHE_herwigpp-707cf44a6e410b75d5faac48558a6059/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_NoFullyHad_noLHE_1Line_Herwig.xSection    = 6.634
ttGamma_NoFullyHad_noLHE_1Line_Herwig.nEvents     = 100000

ttGamma_Had_noLHE_1Line_Herwig             = FWLiteSample.fromDAS("ttGamma_Had_noLHE_1Line_Herwig", "/ttGamma_1Line_Had_noLHE_herwigpp/llechner-ttGamma_1Line_Had_noLHE_herwigpp-0800f6493e59eccc73b1b062e634a7a0/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_Had_noLHE_1Line_Herwig.xSection    = 4.213
ttGamma_Had_noLHE_1Line_Herwig.nEvents     = 100000

ttGamma_SemiLept_noLHE_1Line_Herwig             = FWLiteSample.fromDAS("ttGamma_SemiLept_noLHE_1Line_Herwig", "/ttGamma_1Line_SemiLept_noLHE_herwigpp/llechner-ttGamma_1Line_SemiLept_noLHE_herwigpp-09d44212faaa12309ac65a8117b17d1e/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_SemiLept_noLHE_1Line_Herwig.xSection    = 5.125
ttGamma_SemiLept_noLHE_1Line_Herwig.nEvents     = 100000

ttGamma_Dilept_noLHE_1Line_Herwig             = FWLiteSample.fromDAS("ttGamma_Dilept_noLHE_1Line_Herwig", "/ttGamma_1Line_Dilept_noLHE_herwigpp/llechner-ttGamma_1Line_Dilept_noLHE_herwigpp-b623c785839c36f2593f45f67ced4064/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_Dilept_noLHE_1Line_Herwig.xSection    = 1.512
ttGamma_Dilept_noLHE_1Line_Herwig.nEvents     = 100000


#noLHE
ttGamma_NoFullyHad_noLHE_1Line_Herwig7             = FWLiteSample.fromDAS("ttGamma_NoFullyHad_noLHE_1Line_Herwig7", "/ttGamma_1Line_NoFullyHad_noLHE_herwig7_v2/llechner-ttGamma_1Line_NoFullyHad_noLHE_herwig7_v2-c80c20745a948dbf72f366ad0ee0b641/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_NoFullyHad_noLHE_1Line_Herwig7.xSection    = 6.634
ttGamma_NoFullyHad_noLHE_1Line_Herwig7.nEvents     = 100000

ttGamma_Had_noLHE_1Line_Herwig7             = FWLiteSample.fromDAS("ttGamma_Had_noLHE_1Line_Herwig7", "/ttGamma_1Line_Had_noLHE_herwig7_v2/llechner-ttGamma_1Line_Had_noLHE_herwig7_v2-bb4b6865b1fd542d7d80efc375f508b5/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_Had_noLHE_1Line_Herwig7.xSection    = 4.213
ttGamma_Had_noLHE_1Line_Herwig7.nEvents     = 100000

ttGamma_SemiLept_noLHE_1Line_Herwig7             = FWLiteSample.fromDAS("ttGamma_SemiLept_noLHE_1Line_Herwig7", "/ttGamma_1Line_SemiLept_noLHE_herwig7_v2/llechner-ttGamma_1Line_SemiLept_noLHE_herwig7_v2-2fdcce1e5ac57a9c8a58534f88e90f6f/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_SemiLept_noLHE_1Line_Herwig7.xSection    = 5.125
ttGamma_SemiLept_noLHE_1Line_Herwig7.nEvents     = 100000

ttGamma_Dilept_noLHE_1Line_Herwig7             = FWLiteSample.fromDAS("ttGamma_Dilept_noLHE_1Line_Herwig7", "/ttGamma_1Line_Dilept_noLHE_herwig7_v2/llechner-ttGamma_1Line_Dilept_noLHE_herwig7_v2-5e9d62dd5f4ef18a2ce456209db108bb/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttGamma_Dilept_noLHE_1Line_Herwig7.xSection    = 1.512
ttGamma_Dilept_noLHE_1Line_Herwig7.nEvents     = 100000


# Sample comparison VGamma
WGamma_noPtj          = FWLiteSample.fromDAS("WGamma_noPtj", "/WGamma_noPtj_NLO_v1/llechner-WGamma_noPtj_NLO_v1-b5b2816dddfb90dc835a6661ec19164c/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
WGamma_noPtj.xSection = 724.3
WGamma_noPtj.nEvents  = 1000000

WGamma_central          = FWLiteSample.fromDAS("WGamma_central", "/WGamma_central_NLO_v1/llechner-WGamma_central_NLO_v1-7862da6a82507fca7a336a1a15f86fef/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
WGamma_central.xSection = 300.3
WGamma_central.nEvents  = 985000

ZGamma_noPtj          = FWLiteSample.fromDAS("ZGamma_noPtj", "/ZGamma_noPtj_NLO_v1/llechner-ZGamma_noPtj_NLO_v1-d83db26adbeec9c4413b48620e5bc468/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ZGamma_noPtj.xSection = 261.0
ZGamma_noPtj.nEvents  = 1000000

ZGamma_central          = FWLiteSample.fromDAS("ZGamma_central", "/ZGamma_central_NLO_v1/llechner-ZGamma_central_NLO_v1-38c6460c023e7ff49f40e64c5d271665/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ZGamma_central.xSection = 77.79
ZGamma_central.nEvents  = 990000

#NLO
ZGamma_central_NLO_01j_71X_CP5          = FWLiteSample.fromDAS("ZGamma_central_NLO_01j_71X_CP5", "/ZGamma_central_NLO_01j_CP5_71X_v3/llechner-ZGamma_central_NLO_01j_CP5_71X_v3-22355a42a8e0fc1ac349fb4a842bd3f0/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ZGamma_central_NLO_01j_71X_CP5.xSection = 77.79
ZGamma_central_NLO_01j_71X_CP5.nEvents  = 990000

ZGamma_central_NLO_01j_71X_CUEP8M1          = FWLiteSample.fromDAS("ZGamma_central_NLO_01j_71X_CUEP8M1", "/ZGamma_central_NLO_01j_CUEP8M1_71X_v3/llechner-ZGamma_central_NLO_01j_CUEP8M1_71X_v3-5f8f767332b31bf8be45567618311087/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ZGamma_central_NLO_01j_71X_CUEP8M1.xSection = 77.79
ZGamma_central_NLO_01j_71X_CUEP8M1.nEvents  = 990000

ZGamma_central_NLO_01j_93X_CP5          = FWLiteSample.fromDAS("ZGamma_central_NLO_01j_93X_CP5", "/ZGamma_central_NLO_01j_CP5_v4/llechner-ZGamma_central_NLO_01j_CP5_v4-93826f4c973f9f5e624a858e2ffbe517/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ZGamma_central_NLO_01j_93X_CP5.xSection = 77.79
ZGamma_central_NLO_01j_93X_CP5.nEvents  = 1000000

ZGamma_central_NLO_01j_93X_CUEP8M1          = FWLiteSample.fromDAS("ZGamma_central_NLO_01j_93X_CUEP8M1", "/ZGamma_central_NLO_01j_CUEP8M1_v4/llechner-ZGamma_central_NLO_01j_CUEP8M1_v4-94741d2a2711d10d1036801d36d8ced4/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ZGamma_central_NLO_01j_93X_CUEP8M1.xSection = 77.79
ZGamma_central_NLO_01j_93X_CUEP8M1.nEvents  = 1000000


#LO
ZGamma_central_LO_0123j_71X_CP5          = FWLiteSample.fromDAS("ZGamma_central_LO_0123j_71X_CP5", "/ZGamma_LO_0123j_CP5_71X_v3/llechner-ZGamma_LO_0123j_CP5_71X_v3-f4661f471bfed3c8be086563ccbee2b3/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ZGamma_central_LO_0123j_71X_CP5.xSection = 445.8
ZGamma_central_LO_0123j_71X_CP5.nEvents  = 370000

ZGamma_central_LO_0123j_71X_CUEP8M1          = FWLiteSample.fromDAS("ZGamma_central_LO_0123j_71X_CUEP8M1", "/ZGamma_LO_0123j_CUEP8M1_71X_v3/llechner-ZGamma_LO_0123j_CUEP8M1_71X_v3-0dfef519c394ad2df9404299bd61ecd6/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ZGamma_central_LO_0123j_71X_CUEP8M1.xSection = 445.8
ZGamma_central_LO_0123j_71X_CUEP8M1.nEvents  = 315000

ZGamma_central_LO_0123j_93X_CP5          = FWLiteSample.fromDAS("ZGamma_central_LO_0123j_93X_CP5", "/ZGamma_LO_0123j_CP5_v4/llechner-ZGamma_LO_0123j_CP5_v4-24f94ee56646339fa19ae37b9b00f473/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ZGamma_central_LO_0123j_93X_CP5.xSection = 445.8
ZGamma_central_LO_0123j_93X_CP5.nEvents  = 410000

ZGamma_central_LO_0123j_93X_CUEP8M1          = FWLiteSample.fromDAS("ZGamma_central_LO_0123j_93X_CUEP8M1", "/ZGamma_LO_0123j_CUEP8M1_v4/llechner-ZGamma_LO_0123j_CUEP8M1_v4-1777ab7bf30b66ec245d65a3a60ecdc9/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ZGamma_central_LO_0123j_93X_CUEP8M1.xSection = 445.8
ZGamma_central_LO_0123j_93X_CUEP8M1.nEvents  = 300000

# TWZ dim6top GEN samples


# computed from tWZ01j simulation w/ and w/o the filter
# checked in 0j sample (which has no matching eff) to be consistent with 1640034/(30.*10**6)
tWZ01j_filter_efficiency = (601438./(30*10**6))*(10**6/363784.) 

tWZ0j_rwgt_dim6top_GEN                                    = FWLiteSample.fromDAS("tWZ0j_rwgt_dim6top", "/tWZ0j_rwgt_filter_dim6top/ttschida-tWZ0j_rwgt_filter_dim6top-81f8b37f98d19250d93137d623fc245d/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
tWZ0j_rwgt_dim6top_GEN.reweight_pkl                       = "/afs/hephy.at/data/rschoefbeck01/gridpacks/dim6top/tWZ0j_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl"
tWZ0j_rwgt_dim6top_GEN.xSection                           = 0.4866*tWZ01j_filter_efficiency
tWZ0j_rwgt_dim6top_GEN.nEvents                            = 1640034


tWZ01j_rwgt_dim6top_GEN                                   = FWLiteSample.fromDAS("tWZ01j_rwgt_dim6top", "/tWZ01j_rwgt_filter_dim6top/ttschida-tWZ01j_rwgt_filter_dim6top-caa479f26b314574e6a3e9c0fc79c8e3/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
# attention! the gridpack was simulated on the SM point, i.e. ref-point=0 despite the fact that it has ctZ etc WC
tWZ01j_rwgt_dim6top_GEN.reweight_pkl                      = "/afs/hephy.at/data/rschoefbeck01/gridpacks/dim6top/tWZ01j_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl"
tWZ01j_rwgt_dim6top_GEN.xSection                          = 0.2059*tWZ01j_filter_efficiency
tWZ01j_rwgt_dim6top_GEN.nEvents                           = 584546

# TWW Yt GENSIM sample
tWW1j_rwgt_yt_GEN_SIM                                     = FWLiteSample.fromDAS("tWW1j_rwgt", "/tWW1j_rwgt/ttschida-tWW1j_rwgt_RAWSIMoutput-9cf7eb9ed7748fc2adb21552c72dfa0f/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
tWW1j_rwgt_yt_GEN_SIM.reweight_pkl                        = "/afs/hephy.at/data/cms04/ttschida/gridpacks/Yt/tWW1j_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl"
tWW1j_rwgt_yt_GEN_SIM.xSection                            = 0.02523
tWW1j_rwgt_yt_GEN_SIM.nEvents                             = 991000

# TWZ filter Yt GENSIM sample
tWZ01j_rwgt_filter_yt_GEN_SIM                             = FWLiteSample.fromDAS("tWZ01j_rwgt_filter_2", "/tWZ01j_rwgt_filter_2/ttschida-tWZ01j_rwgt_filter_2_RAWSIMoutput-d21de898ad3d5a9f1861cf5edf14f0e3/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
tWZ01j_rwgt_filter_yt_GEN_SIM.reweight_pkl                = "/afs/hephy.at/data/cms04/ttschida/gridpacks/Yt/tWZ01j_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl"
tWZ01j_rwgt_filter_yt_GEN_SIM.xSection                    = 0.2279*tWZ01j_filter_efficiency
tWZ01j_rwgt_filter_yt_GEN_SIM.nEvents                     = 601438

# TTW dim6top GENSIM sample
ttW01j_rwgt_dim6top_GEN_SIM                               = FWLiteSample.fromDAS("ttW01j_rwgt_dim6top", "/ttW01j_rwgt_dim6top/ttschida-ttW01j_rwgt_dim6top_RAWSIMoutput-922d23f892763d51c751153fd8c3e4fd/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix='root://hephyse.oeaw.ac.at/')
ttW01j_rwgt_dim6top_GEN_SIM.reweight_pkl                  = "/afs/hephy.at/data/cms04/ttschida/gridpacks/dim6top/ttW01j_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl"
ttW01j_rwgt_dim6top_GEN_SIM.xSection                      = 0.8324
ttW01j_rwgt_dim6top_GEN_SIM.nEvents                       = 498853

SM = [
    ttGamma_Dilept_newCentral_1Line,
    ttGamma_SemiLept_newCentral_1Line,
    ttGamma_Had_newCentral_1Line,
    ttGamma_NoFullyHad_newCentral_1Line,
    TTGamma_SingleLeptFromT_SM_1Line_test,
    TTGamma_SingleLeptFromT_SM_3LineBuggy_test,
    TTGamma_SingleLeptFromT_SM_3LinePatched_test,
    TTGamma_SingleLeptFromT_SM_1Line,
    TTGamma_SingleLeptFromT_SM_3LinePatched,
    ttGamma_SingleLeptFromT_SM_1Line,
    ttGamma_SingleLeptFromTbar_SM_1Line,
    ttGamma_SingleLeptFromT_SM_central,
    ttGamma_SingleLeptFromTbar_SM_central,
#    ttGamma_Dilept_SM_central,
    ttGamma_Hadronic_SM_central,
    ttGamma_NoFullyHad_SM_ATLASrunCard_small,
    ttGamma_NoFullyHad_SM_ATLASrunCard,
    ttGamma_NoFullyHad_SM_CMSrunCard_small,
    ttGamma_NoFullyHad_SM_CMSrunCard,
    ttGamma_NoFullyHad_SM_TTBarrunCard,
    ttGamma_NoFullyHad_SM_TTBarrunCard_modified,
    ttGamma_NoFullyHad_SM_TTBarrunCard_mllOnly,
    ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR,
    ttGamma_NoFullyHad_SM_CMSrunCard_xqcut,
    ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_xqcut,
    ttGamma_NoFullyHad_SM_CMSrunCard_noJetPtCut,
    ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut,
    ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut_xqcut,
    ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut_xqcut_wideLepEta,
    ttGamma_NoFullyHad_SM_CMSrunCard_noJetPtCut_xqcut,
    ttGamma_NoFullyHad_newCentral_1Line,
    ttGamma_NoFullyHad_newCentral_1Line_comp,
    ttGamma_NoFullyHad_SM_ATLASrunCard_comp,
    ttGamma_NoFullyHad_newCentral_1Line_pTG100To200_comp,
    ttGamma_NoFullyHad_newCentral_1Line_pTGgt200_comp,
    ttGamma_NoFullyHad_newCentral_1Line_Herwig,
    ttGamma_NoFullyHad_noLHE_1Line_Herwig,
    ttGamma_Had_noLHE_1Line_Herwig,
    ttGamma_SemiLept_noLHE_1Line_Herwig,
    ttGamma_Dilept_noLHE_1Line_Herwig,
    ttGamma_NoFullyHad_noLHE_1Line_Herwig7,
    ttGamma_Had_noLHE_1Line_Herwig7,
    ttGamma_SemiLept_noLHE_1Line_Herwig7,
    ttGamma_Dilept_noLHE_1Line_Herwig7,
]

EFT = [
    TTGamma_SingleLeptFromT_EFT_1Line_test,
    TTGamma_DiLept_EFT_1Line_small,
    TTGamma_DiLept_EFT_1Line,
    TTGamma_SingleLeptFromT_EFT_1Line,
    TTGamma_SingleLeptFromTbar_EFT_1Line,
]

VGamma = [
    WGamma_noPtj,
    WGamma_central,
    ZGamma_noPtj,
    ZGamma_central,
    ZGamma_central_NLO_01j_93X_CP5,
    ZGamma_central_NLO_01j_93X_CUEP8M1,
    ZGamma_central_NLO_01j_71X_CP5,
    ZGamma_central_NLO_01j_71X_CUEP8M1,
    ZGamma_central_LO_0123j_93X_CP5,
    ZGamma_central_LO_0123j_93X_CUEP8M1,
    ZGamma_central_LO_0123j_71X_CP5,
    ZGamma_central_LO_0123j_71X_CUEP8M1,
]

allSamples = SM + EFT + VGamma

for s in allSamples:
    s.isData = False


