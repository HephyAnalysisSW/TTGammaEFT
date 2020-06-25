# Standard Imports
import os, sys
import ROOT

# RootTools Imports
from RootTools.core.Sample import Sample

# Colors
from TTGammaEFT.Samples.color import color

# Data directory
from TTGammaEFT.Tools.user import gridpack_directory
data_directory           = "/afs/hephy.at/data/llechner03/TTGammaEFT/nanoTuples/"
postprocessing_directory = "TTGammaEFT_PP_GEN_TTG_v14/gen/"

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

dirs["TTG_SingleLeptFromT_1L_test_SM"]           = [ "TTGamma_SingleLeptFromT_SM_1Line_test" ]
dirs["TTG_SingleLeptFromT_3LBuggy_test_SM"]      = [ "TTGamma_SingleLeptFromT_SM_3LineBuggy_test" ]
dirs["TTG_SingleLeptFromT_3LPatched_test_SM"]    = [ "TTGamma_SingleLeptFromT_SM_3LinePatched_test" ]

dirs["TTG_SingleLeptFromT_1L_SM"]                = [ "TTGamma_SingleLeptFromT_SM_1Line" ]
dirs["TTG_SingleLeptFromT_3LinePatched_SM"]      = [ "TTGamma_SingleLeptFromT_SM_3LinePatched" ]

dirs["TTG_SingleLeptFromT_1L_test_EFT"]          = [ "TTGamma_SingleLeptFromT_EFT_1Line_test" ]
dirs["TTGamma_DiLept_EFT_1Line_small"]           = [ "TTGamma_DiLept_EFT_1Line_small" ]
dirs["TTGamma_DiLept_EFT_1Line"]                 = [ "TTGamma_DiLept_EFT_1Line" ]

dirs["ttGamma_SingleLeptFromT_SM_1Line"]         = [ "ttGamma_SingleLeptFromT_SM_1Line" ]
dirs["ttGamma_SingleLeptFromTbar_SM_1Line"]      = [ "ttGamma_SingleLeptFromTbar_SM_1Line" ]

dirs["ttGamma_SingleLeptFromT_SM_central"]       = [ "ttGamma_SingleLeptFromT_SM_central" ]
dirs["ttGamma_SingleLeptFromTbar_SM_central"]    = [ "ttGamma_SingleLeptFromTbar_SM_central" ]
dirs["ttGamma_Dilept_SM_central"]                = [ "ttGamma_Dilept_SM_central" ]
dirs["ttGamma_Hadronic_SM_central"]              = [ "ttGamma_Hadronic_SM_central" ]

dirs["ttGamma_NoFullyHad_SM_CMSrunCard"]          = [ "ttGamma_NoFullyHad_SM_CMSrunCard" ]
dirs["ttGamma_NoFullyHad_SM_CMSrunCard_small"]    = [ "ttGamma_NoFullyHad_SM_CMSrunCard_small" ]
dirs["ttGamma_NoFullyHad_SM_ATLASrunCard"]        = [ "ttGamma_NoFullyHad_SM_ATLASrunCard" ]
dirs["ttGamma_NoFullyHad_SM_ATLASrunCard_small"]  = [ "ttGamma_NoFullyHad_SM_ATLASrunCard_small" ]
dirs["ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR"] = [ "ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR" ]

dirs["ttGamma_NoFullyHad_SM_CMSrunCard_xqcut"] = [ "ttGamma_NoFullyHad_SM_CMSrunCard_xqcut" ]
dirs["ttGamma_NoFullyHad_SM_CMSrunCard_noJetPtCut"] = [ "ttGamma_NoFullyHad_SM_CMSrunCard_noJetPtCut" ]
dirs["ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_xqcut"] = [ "ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_xqcut" ]
dirs["ttGamma_NoFullyHad_SM_CMSrunCard_xqcut"] = [ "ttGamma_NoFullyHad_SM_CMSrunCard_xqcut" ]
#dirs["ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut"] = [ "ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut" ]

dirs["ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut_xqcut"] = [ "ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut_xqcut" ]
dirs["ttGamma_NoFullyHad_SM_CMSrunCard_noJetPtCut_xqcut"] = [ "ttGamma_NoFullyHad_SM_CMSrunCard_noJetPtCut_xqcut" ]
dirs["ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut_xqcut_wideLepEta"] = [ "ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut_xqcut_wideLepEta" ]

dirs["ttGamma_NoFullyHad_SM_TTBarrunCard_mllOnly"] = [ "ttGamma_NoFullyHad_SM_TTBarrunCard_mllOnly" ]
dirs["ttGamma_NoFullyHad_SM_TTBarrunCard_modified"] = [ "ttGamma_NoFullyHad_SM_TTBarrunCard_modified" ]
dirs["ttGamma_NoFullyHad_SM_TTBarrunCard"] = [ "ttGamma_NoFullyHad_SM_TTBarrunCard" ]

dirs["ttGamma_Dilept_newCentral"]                = [ "ttGamma_Dilept_newCentral_1Line" ]
dirs["ttGamma_SemiLept_newCentral"]              = [ "ttGamma_SemiLept_newCentral_1Line" ]
dirs["ttGamma_Had_newCentral"]                   = [ "ttGamma_Had_newCentral_1Line" ]
dirs["ttGamma_NoFullyHad_newCentral"]            = [ "ttGamma_NoFullyHad_newCentral_1Line" ]
dirs["ttGamma_NoFullyHad_comb_newCentral"]       = [ "ttGamma_Dilept_newCentral_1Line", "ttGamma_SemiLept_newCentral_1Line" ]

dirs["ttGamma_NoFullyHad_SM_ATLASrunCard_comp"]         = [ "ttGamma_NoFullyHad_SM_ATLASrunCard_comp" ]
dirs["ttGamma_NoFullyHad_newCentral_comp"]              = [ "ttGamma_NoFullyHad_newCentral_1Line_comp" ]
dirs["ttGamma_NoFullyHad_newCentral_pTG100To200_comp"]  = [ "ttGamma_NoFullyHad_newCentral_1Line_pTG100To200_comp" ]
dirs["ttGamma_NoFullyHad_newCentral_pTGgt200_comp"]     = [ "ttGamma_NoFullyHad_newCentral_1Line_pTGgt200_comp" ]
dirs["ttGamma_NoFullyHad_newCentral_Herwig"]            = [ "ttGamma_NoFullyHad_newCentral_1Line_Herwig" ]

dirs["ttGamma_NoFullyHad_noLHE_Herwig"]     = [ "ttGamma_NoFullyHad_noLHE_1Line_Herwig" ]
dirs["ttGamma_Had_noLHE_Herwig"]            = [ "ttGamma_Had_noLHE_1Line_Herwig" ]
dirs["ttGamma_SemiLept_noLHE_Herwig"]       = [ "ttGamma_SemiLept_noLHE_1Line_Herwig" ]
dirs["ttGamma_Dilept_noLHE_Herwig"]         = [ "ttGamma_Dilept_noLHE_1Line_Herwig" ]

dirs["ttGamma_NoFullyHad_noLHE_Herwig7"]     = [ "ttGamma_NoFullyHad_noLHE_1Line_Herwig7" ]
dirs["ttGamma_Had_noLHE_Herwig7"]            = [ "ttGamma_Had_noLHE_1Line_Herwig7" ]
dirs["ttGamma_SemiLept_noLHE_Herwig7"]       = [ "ttGamma_SemiLept_noLHE_1Line_Herwig7" ]
dirs["ttGamma_Dilept_noLHE_Herwig7"]         = [ "ttGamma_Dilept_noLHE_1Line_Herwig7" ]

dirs["WGamma_noPtj"]   = [ "WGamma_noPtj" ]
dirs["ZGamma_noPtj"]   = [ "ZGamma_noPtj" ]
dirs["WGamma_central"] = [ "WGamma_central" ]
dirs["ZGamma_central"] = [ "ZGamma_central" ]

dirs["ZGamma_NLO_CUEP8M1_93X"] = [ "ZGamma_central_NLO_01j_93X_CUEP8M1" ]
dirs["ZGamma_NLO_CP5_93X"]     = [ "ZGamma_central_NLO_01j_93X_CP5" ]
dirs["ZGamma_NLO_CUEP8M1_71X"] = [ "ZGamma_central_NLO_01j_71X_CUEP8M1" ]
dirs["ZGamma_NLO_CP5_71X"]     = [ "ZGamma_central_NLO_01j_71X_CP5" ]

dirs["ZGamma_LO_CUEP8M1_93X"]  = [ "ZGamma_central_LO_0123j_93X_CUEP8M1" ]
dirs["ZGamma_LO_CP5_93X"]      = [ "ZGamma_central_LO_0123j_93X_CP5" ]
dirs["ZGamma_LO_CUEP8M1_71X"]  = [ "ZGamma_central_LO_0123j_71X_CUEP8M1" ]
dirs["ZGamma_LO_CP5_71X"]      = [ "ZGamma_central_LO_0123j_71X_CP5" ]

directories = { key : [ os.path.join( data_directory, postprocessing_directory, dir) for dir in dirs[key] ] for key in dirs.keys() }

# Samples
#TTG_SingleLeptFromT_1L_test_SM                     = Sample.fromDirectory(name="TTG_SingleLeptFromT_1Line",        treeName="Events", isData=False, color=color.TTG1L,        texName="tt#gamma (1L)",         directory=directories["TTG_SingleLeptFromT_1L_test_SM"])
#TTG_SingleLeptFromT_1L_test_SM.reweight_pkl        = os.path.join( gridpack_directory, "SM/TTGamma_SingleLeptFromT_1Line_test/", "TTGamma_SingleLeptFromT_1Line_test_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.pkl" )

#TTG_SingleLeptFromT_3LBuggy_test_SM                = Sample.fromDirectory(name="TTG_SingleLeptFromT_3LineBuggy",   treeName="Events", isData=False, color=color.TTG3LBuggy,   texName="tt#gamma (3L buggy)",   directory=directories["TTG_SingleLeptFromT_3LBuggy_test_SM"])
#TTG_SingleLeptFromT_3LBuggy_test_SM.reweight_pkl   = os.path.join( gridpack_directory, "SM/TTGamma_SingleLeptFromT_3LineBuggy_test/", "TTGamma_SingleLeptFromT_3LineBuggy_test_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.pkl" )

#TTG_SingleLeptFromT_3LPatched_test_SM              = Sample.fromDirectory(name="TTG_SingleLeptFromT_3LinePatched", treeName="Events", isData=False, color=color.TTG3LPatched, texName="tt#gamma (3L patched)", directory=directories["TTG_SingleLeptFromT_3LPatched_test_SM"])
#TTG_SingleLeptFromT_3LPatched_test_SM.reweight_pkl = os.path.join( gridpack_directory, "SM/TTGamma_SingleLeptFromT_3LinePatched_test/", "TTGamma_SingleLeptFromT_3LinePatched_test_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.pkl" )

#TTG_SingleLeptFromT_1L_SM                          = Sample.fromDirectory(name="TTG_SingleLeptFromT_1Line",        treeName="Events", isData=False, color=color.TTG1L,        texName="tt#gamma (1L)",         directory=directories["TTG_SingleLeptFromT_1L_SM"])
#TTG_SingleLeptFromT_1L_SM.reweight_pkl             = os.path.join( gridpack_directory, "SM/TTGamma_SingleLeptFromT_1Line/", "TTGamma_SingleLeptFromT_1Line_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.pkl" )

#TTG_SingleLeptFromT_3LPatched_SM                   = Sample.fromDirectory(name="TTG_SingleLeptFromT_3LinePatched", treeName="Events", isData=False, color=color.TTG3LPatched, texName="tt#gamma (3L patched)", directory=directories["TTG_SingleLeptFromT_3LinePatched_SM"])
#TTG_SingleLeptFromT_3LPatched_SM.reweight_pkl      = os.path.join( gridpack_directory, "SM/TTGamma_SingleLeptFromT_3LinePatched/", "TTGamma_SingleLeptFromT_3LinePatched_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.pkl" )

#TTG_SingleLeptFromT_1L_test_EFT                    = Sample.fromDirectory(name="TTG_SingleLeptFromT_1Line_EFT",    treeName="Events", isData=False, color=color.TTG,          texName="tt#gamma", directory=directories["TTG_SingleLeptFromT_1L_test_EFT"])
#TTG_SingleLeptFromT_1L_test_EFT.reweight_pkl       = os.path.join( gridpack_directory, "EFT/TTGamma_SingleLeptFromT_1Line_EFT_test/", "TTGamma_SingleLeptFromT_1Line_EFT_test_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.pkl" )

#TTG_DiLept_1L_small_EFT                            = Sample.fromDirectory(name="TTG_DiLept_1L_small_EFT",          treeName="Events", isData=False, color=color.TTG,          texName="tt#gamma", directory=directories["TTGamma_DiLept_EFT_1Line_small"])
#TTG_DiLept_1L_small_EFT.reweight_pkl               = os.path.join( gridpack_directory, "EFT/TTGamma_DiLept_1Line_EFT/", "TTGamma_DiLept_1Line_EFT_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.pkl" )

#TTG_DiLept_1L_EFT                                  = Sample.fromDirectory(name="TTG_DiLept_1L_EFT",          treeName="Events", isData=False, color=color.TTG,          texName="tt#gamma", directory=directories["TTGamma_DiLept_EFT_1Line"])
#TTG_DiLept_1L_EFT.reweight_pkl                     = os.path.join( gridpack_directory, "EFT/TTGamma_DiLept_1Line_EFT/", "TTGamma_DiLept_1Line_EFT_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.pkl" )

signals = []

# Private 1Line Production
#ttGamma_SingleLeptFromT_SM_1Line                 = Sample.fromDirectory(name="ttGamma_SingleLeptFromT_SM_1Line",      treeName="Events", isData=False, color=color.TTG1L,          texName="tt#gamma (1Line)", directory=directories["ttGamma_SingleLeptFromT_SM_1Line"])
#ttGamma_SingleLeptFromTbar_SM_1Line              = Sample.fromDirectory(name="ttGamma_SingleLeptFromTbar_SM_1Line",   treeName="Events", isData=False, color=color.TTG1L,          texName="tt#gamma (1Line)", directory=directories["ttGamma_SingleLeptFromTbar_SM_1Line"])

# Central Samples
#ttGamma_SingleLeptFromT_SM_central               = Sample.fromDirectory(name="ttGamma_SingleLeptFromT_SM_central",    treeName="Events", isData=False, color=color.TTG3LBuggy,     texName="tt#gamma (central)", directory=directories["ttGamma_SingleLeptFromT_SM_central"])
#ttGamma_SingleLeptFromTbar_SM_central            = Sample.fromDirectory(name="ttGamma_SingleLeptFromTbar_SM_central", treeName="Events", isData=False, color=color.TTG3LBuggy,     texName="tt#gamma (central)", directory=directories["ttGamma_SingleLeptFromTbar_SM_central"])
#ttGamma_Dilept_SM_central                        = Sample.fromDirectory(name="ttGamma_Dilept_SM_central",             treeName="Events", isData=False, color=color.TTG3LBuggy,     texName="tt#gamma (central)", directory=directories["ttGamma_Dilept_SM_central"])
#ttGamma_Hadronic_SM_central                      = Sample.fromDirectory(name="ttGamma_Hadronic_SM_central",           treeName="Events", isData=False, color=color.TTG3LBuggy,     texName="tt#gamma (central)", directory=directories["ttGamma_Hadronic_SM_central"])

# CMS ATLAS runcard comparison
#TTG_CMS_RunCard_noDeltaR                         = Sample.fromDirectory(name="TTG_CMS_RunCard_noDeltaR",   treeName="Events", isData=False, color=color.TTG3LPatched, texName="tt#gamma (CMS, no #DeltaR)",   directory=directories["ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR"])
#TTG_CMS_RunCard                                  = Sample.fromDirectory(name="TTG_CMS_RunCard",            treeName="Events", isData=False, color=color.TTG6,        texName="tt#gamma (CMS)",   directory=directories["ttGamma_NoFullyHad_SM_CMSrunCard"])
#TTG_CMS_RunCard_small                            = Sample.fromDirectory(name="TTG_CMS_RunCard_small",      treeName="Events", isData=False, color=color.TTG1L,        texName="tt#gamma (CMS)",   directory=directories["ttGamma_NoFullyHad_SM_CMSrunCard_small"])
#TTG_ATLAS_RunCard                                = Sample.fromDirectory(name="TTG_ATLAS_RunCard",          treeName="Events", isData=False, color=color.TTG3LBuggy,   texName="tt#gamma (ATLAS)", directory=directories["ttGamma_NoFullyHad_SM_ATLASrunCard"])
#TTG_ATLAS_RunCard_small                          = Sample.fromDirectory(name="TTG_ATLAS_RunCard_small",    treeName="Events", isData=False, color=color.TTG3LBuggy,   texName="tt#gamma (ATLAS)", directory=directories["ttGamma_NoFullyHad_SM_ATLASrunCard_small"])

#TTG_CMS_RunCard_noJetPtCut                       = Sample.fromDirectory(name="TTG_CMS_RunCard_noJetPtCut",            treeName="Events", isData=False, color=color.TTG1, texName="tt#gamma (CMS, pT(jet)>0)",   directory=directories["ttGamma_NoFullyHad_SM_CMSrunCard_noJetPtCut"])
#TTG_CMS_RunCard_xqcut                            = Sample.fromDirectory(name="TTG_CMS_RunCard_xqcut",                 treeName="Events", isData=False, color=color.TTG2, texName="tt#gamma (CMS, xqcut=0)",   directory=directories["ttGamma_NoFullyHad_SM_CMSrunCard_xqcut"])
#TTG_CMS_RunCard_noDeltaR_noJetPtCut              = Sample.fromDirectory(name="TTG_CMS_RunCard_noDeltaR_noJetPtCut",   treeName="Events", isData=False, color=color.TTG3LPatched, texName="tt#gamma (CMS, no #DeltaR, pT(jet)>0)",   directory=directories["ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut"])
#TTG_CMS_RunCard_noDeltaR_xqcut                   = Sample.fromDirectory(name="TTG_CMS_RunCard_noDeltaR_xqcut",        treeName="Events", isData=False, color=color.TTG3, texName="tt#gamma (CMS, no #DeltaR, xqcut=0)",   directory=directories["ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_xqcut"])

#TTG_CMS_RunCard_noDeltaR_noJetPtCut_xqcut        = Sample.fromDirectory(name="TTG_CMS_RunCard_noDeltaR_noJetPtCut_xqcut",        treeName="Events", isData=False, color=color.TTG1, texName="tt#gamma (CMS, no #DeltaR, pT(jet)>0)",   directory=directories["ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut_xqcut"])
#TTG_CMS_RunCard_noJetPtCut_xqcut                 = Sample.fromDirectory(name="TTG_CMS_RunCard_noJetPtCut_xqcut",                 treeName="Events", isData=False, color=color.TTG5, texName="tt#gamma (CMS, pT(jet)>0)",   directory=directories["ttGamma_NoFullyHad_SM_CMSrunCard_noJetPtCut_xqcut"])
#TTG_CMS_RunCard_noDeltaR_noJetPtCut_xqcut_wideLepEta        = Sample.fromDirectory(name="TTG_CMS_RunCard_noDeltaR_noJetPtCut_xqcut_wideLepEta",        treeName="Events", isData=False, color=color.TTG4, texName="tt#gamma (CMS, no #DeltaR, pT(jet)>0, xqcut=0, abs(#eta(l))<5)",   directory=directories["ttGamma_NoFullyHad_SM_CMSrunCard_noDeltaR_noJetPtCut_xqcut_wideLepEta"])

#TTG_TTBar_RunCard                                  = Sample.fromDirectory(name="TTG_TTBar_RunCard",            treeName="Events", isData=False, color=color.TTG1,        texName="tt#gamma (tt)",   directory=directories["ttGamma_NoFullyHad_SM_TTBarrunCard"])
#TTG_TTBar_RunCard_modified                         = Sample.fromDirectory(name="TTG_TTBar_RunCard_modified",    treeName="Events", isData=False, color=color.TTG5,        texName="tt#gamma (tt mod)",   directory=directories["ttGamma_NoFullyHad_SM_TTBarrunCard_modified"])
#TTG_TTBar_RunCard_mllOnly                          = Sample.fromDirectory(name="TTG_TTBar_RunCard_mllOnly",    treeName="Events", isData=False, color=color.TTG4,        texName="tt#gamma (tt mmll=0)",   directory=directories["ttGamma_NoFullyHad_SM_TTBarrunCard_mllOnly"])

#TTG_Dilept_newCentral_RunCard                      = Sample.fromDirectory(name="TTG_Dilept_newCentral_RunCard", treeName="Events", isData=False, color=color.TTG1,        texName="tt#gamma (2l, new)",   directory=directories["ttGamma_Dilept_newCentral"])
#TTG_SemiLept_newCentral_RunCard                    = Sample.fromDirectory(name="TTG_SemiLept_newCentral_RunCard", treeName="Events", isData=False, color=color.TTG5,        texName="tt#gamma (1l, new)",   directory=directories["ttGamma_SemiLept_newCentral"])
#TTG_Had_newCentral_RunCard                         = Sample.fromDirectory(name="TTG_Had_newCentral_RunCard", treeName="Events", isData=False, color=color.TTG4,        texName="tt#gamma (had, new)",   directory=directories["ttGamma_Had_newCentral"])
#TTG_NoFullyHad_newCentral_RunCard                  = Sample.fromDirectory(name="TTG_NoFullyHad_newCentral_RunCard", treeName="Events", isData=False, color=color.TTG5,        texName="tt#gamma (new)",   directory=directories["ttGamma_NoFullyHad_newCentral"])
#TTG_NoFullyHad_comb_newCentral_RunCard             = Sample.fromDirectory(name="TTG_NoFullyHad_comb_newCentral_RunCard", treeName="Events", isData=False, color=color.TTG1,        texName="tt#gamma (new, comb)",   directory=directories["ttGamma_NoFullyHad_comb_newCentral"])

#TTG_ATLAS_RunCard_comp                             = Sample.fromDirectory(name="TTG_ATLAS_RunCard",          treeName="Events", isData=False, color=color.TTG3LBuggy,   texName="tt#gamma (ATLAS)", directory=directories["ttGamma_NoFullyHad_SM_ATLASrunCard_comp"])
TTG_NoFullyHad_newCentral_RunCard_comp             = Sample.fromDirectory(name="TTG_NoFullyHad_newCentral_RunCard", treeName="Events", isData=False, color=color.TTG5,        texName="tt#gamma (Pythia)",   directory=directories["ttGamma_NoFullyHad_newCentral_comp"])
#TTG_NoFullyHad_newCentral_RunCard_pTG100To200_comp = Sample.fromDirectory(name="TTG_NoFullyHad_newCentral_RunCard_pTG100To200", treeName="Events", isData=False, color=color.TTG6,        texName="tt#gamma (100<p_{T}(#gamma)<200 GeV)",   directory=directories["ttGamma_NoFullyHad_newCentral_pTG100To200_comp"])
#TTG_NoFullyHad_newCentral_RunCard_pTGgt200_comp    = Sample.fromDirectory(name="TTG_NoFullyHad_newCentral_RunCard_pTGgt200", treeName="Events", isData=False, color=color.TTG6,        texName="tt#gamma (p_{T}(#gamma)>200 GeV)",   directory=directories["ttGamma_NoFullyHad_newCentral_pTGgt200_comp"])
TTG_NoFullyHad_newCentral_RunCard_Herwig           = Sample.fromDirectory(name="TTG_NoFullyHad_newCentral_RunCard_Herwig", treeName="Events", isData=False, color=color.TTG6,        texName="tt#gamma (Herwig)",   directory=directories["ttGamma_NoFullyHad_newCentral_Herwig"])

TTG_NoFullyHad_noLHE_RunCard_Herwig    = Sample.fromDirectory(name="TTG_NoFullyHad_noLHE_RunCard_Herwig", treeName="Events", isData=False, color=color.TTG4,        texName="tt#gamma (Herwig++)",   directory=directories["ttGamma_NoFullyHad_noLHE_Herwig"])
TTG_Had_noLHE_RunCard_Herwig           = Sample.fromDirectory(name="TTG_Had_noLHE_RunCard_Herwig", treeName="Events", isData=False, color=color.TTG4,        texName="tt#gamma (Herwig++)",   directory=directories["ttGamma_Had_noLHE_Herwig"])
TTG_SemiLept_noLHE_RunCard_Herwig      = Sample.fromDirectory(name="TTG_SemiLept_noLHE_RunCard_Herwig", treeName="Events", isData=False, color=color.TTG4,        texName="tt#gamma (Herwig++)",   directory=directories["ttGamma_SemiLept_noLHE_Herwig"])
TTG_Dilept_noLHE_RunCard_Herwig        = Sample.fromDirectory(name="TTG_Dilept_noLHE_RunCard_Herwig", treeName="Events", isData=False, color=color.TTG4,        texName="tt#gamma (Herwig++)",   directory=directories["ttGamma_Dilept_noLHE_Herwig"])

TTG_NoFullyHad_noLHE_RunCard_Herwig7    = Sample.fromDirectory(name="TTG_NoFullyHad_noLHE_RunCard_Herwig7", treeName="Events", isData=False, color=color.TTG6,        texName="tt#gamma (Herwig7)",   directory=directories["ttGamma_NoFullyHad_noLHE_Herwig7"])
TTG_Had_noLHE_RunCard_Herwig7           = Sample.fromDirectory(name="TTG_Had_noLHE_RunCard_Herwig7", treeName="Events", isData=False, color=color.TTG6,        texName="tt#gamma (Herwig7)",   directory=directories["ttGamma_Had_noLHE_Herwig7"])
TTG_SemiLept_noLHE_RunCard_Herwig7      = Sample.fromDirectory(name="TTG_SemiLept_noLHE_RunCard_Herwig7", treeName="Events", isData=False, color=color.TTG6,        texName="tt#gamma (Herwig7)",   directory=directories["ttGamma_SemiLept_noLHE_Herwig7"])
TTG_Dilept_noLHE_RunCard_Herwig7        = Sample.fromDirectory(name="TTG_Dilept_noLHE_RunCard_Herwig7", treeName="Events", isData=False, color=color.TTG6,        texName="tt#gamma (Herwig7)",   directory=directories["ttGamma_Dilept_noLHE_Herwig7"])

#ZGamma_central  = Sample.fromDirectory(name="ZGamma_central", treeName="Events", isData=False, color=color.TTG3LBuggy,     texName="Z#gamma (p_{T}(jet)>10)", directory=directories["ZGamma_central"])
#ZGamma_noPtj    = Sample.fromDirectory(name="ZGamma_noPtj",   treeName="Events", isData=False, color=color.TTG3LPatched,   texName="Z#gamma (p_{T}(jet)>0)",  directory=directories["ZGamma_noPtj"])
#WGamma_central  = Sample.fromDirectory(name="WGamma_central", treeName="Events", isData=False, color=color.TTG3LBuggy,     texName="W#gamma (p_{T}(jet)>10)", directory=directories["WGamma_central"])
#WGamma_noPtj    = Sample.fromDirectory(name="WGamma_noPtj",   treeName="Events", isData=False, color=color.TTG3LPatched,   texName="W#gamma (p_{T}(jet)>0)",  directory=directories["WGamma_noPtj"])

ZGamma_NLO_CUEP8M1_93X  = Sample.fromDirectory(name="ZGamma_NLO_CUEP8M1_93X", treeName="Events", isData=False, color=color.VG1,     texName="Z#gamma (NLO, CUEP8M1, 2017)", directory=directories["ZGamma_NLO_CUEP8M1_93X"])
ZGamma_NLO_CP5_93X      = Sample.fromDirectory(name="ZGamma_NLO_CP5_93X",     treeName="Events", isData=False, color=color.VG2,     texName="Z#gamma (NLO, CP5, 2017)",     directory=directories["ZGamma_NLO_CP5_93X"])
ZGamma_LO_CUEP8M1_93X  = Sample.fromDirectory(name="ZGamma_LO_CUEP8M1_93X", treeName="Events", isData=False, color=color.VG3,     texName="Z#gamma (LO, CUEP8M1, 2017)", directory=directories["ZGamma_LO_CUEP8M1_93X"])
ZGamma_LO_CP5_93X      = Sample.fromDirectory(name="ZGamma_LO_CP5_93X",     treeName="Events", isData=False, color=color.VG4,     texName="Z#gamma (LO, CP5, 2017)",     directory=directories["ZGamma_LO_CP5_93X"])

ZGamma_NLO_CUEP8M1_71X  = Sample.fromDirectory(name="ZGamma_NLO_CUEP8M1_71X", treeName="Events", isData=False, color=color.VG5,     texName="Z#gamma (NLO, CUEP8M1, 2016)", directory=directories["ZGamma_NLO_CUEP8M1_71X"])
ZGamma_NLO_CP5_71X      = Sample.fromDirectory(name="ZGamma_NLO_CP5_71X",     treeName="Events", isData=False, color=color.VG6,     texName="Z#gamma (NLO, CP5, 2016)",     directory=directories["ZGamma_NLO_CP5_71X"])
ZGamma_LO_CUEP8M1_71X  = Sample.fromDirectory(name="ZGamma_LO_CUEP8M1_71X", treeName="Events", isData=False, color=color.VG7,     texName="Z#gamma (LO, CUEP8M1, 2016)", directory=directories["ZGamma_LO_CUEP8M1_71X"])
ZGamma_LO_CP5_71X      = Sample.fromDirectory(name="ZGamma_LO_CP5_71X",     treeName="Events", isData=False, color=color.VG8,     texName="Z#gamma (LO, CP5, 2016)",     directory=directories["ZGamma_LO_CP5_71X"])
