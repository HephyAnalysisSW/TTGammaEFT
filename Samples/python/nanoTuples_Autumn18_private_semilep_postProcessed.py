# Standard Imports
import os, sys
import ROOT

# RootTools Imports
from RootTools.core.Sample import Sample

# Colors
from TTGammaEFT.Samples.color import color
from TTGammaEFT.Samples.helpers import getMCSample

# Data directory
if "data_directory" in os.environ:
    data_directory_ = os.environ["data_directory"]
else:
    from TTGammaEFT.Tools.user import dpm_directory as data_directory_
    data_directory_ += "postprocessed/"
if "postprocessing_directory" in os.environ:
    postprocessing_directory_ = os.environ["postprocessing_directory"]
else:
    from TTGammaEFT.Samples.default_locations import postprocessing_locations
    postprocessing_directory_ = postprocessing_locations.MC2018_semilep

try:
    fromDPM = sys.modules['__main__'].fromEOS != "True"
except:
    fromDPM = not "clip" in os.getenv("HOSTNAME").lower() 

if "gammaSkim" in os.environ and os.environ["gammaSkim"] == "True":
    postprocessing_directory_ = postprocessing_directory_.replace("/semilep/", "/semilepGamma/")

# Redirector
try:
    redirector = sys.modules["__main__"].redirector
except:
    from TTGammaEFT.Tools.user import redirector as redirector

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

dirs = {}
dirs["DY_LO"]            = ["DYJetsToLL_M50_LO", "DYJetsToLL_M10to50_LO"]
#dirs["Z_NuNu"]           = ["DYJetsToNuNu_HT100to200", "DYJetsToNuNu_HT200to400", "DYJetsToNuNu_HT400to600", "DYJetsToNuNu_HT600to800", "DYJetsToNuNu_HT800to1200", "DYJetsToNuNu_HT1200to2500", "DYJetsToNuNu_HT2500toInf"]

dirs["TT_pow"]           = ["TTLep_pow", "TTSingleLep_pow", "TTHad_pow" ]
dirs["TT_Lep"]           = ["TTLep_pow"]
dirs["TT_SemiLep"]       = ["TTSingleLep_pow"]

dirs["TTGSemiLep"]       = ["TTGSingleLep_LO", "TTGSingleLep_ptG100To200_LO", "TTGSingleLep_ptG200_LO"]
#dirs["TTGSemiLep"]       = ["TTGSingleLep_LO"]

dirs["TTG_NLO"]           = ["TTGJets"]

dirs["TTGLep"]           = ["TTGLep_LO", "TTGLep_ptG100To200_LO", "TTGLep_ptG200_LO"]
#dirs["TTGLep"]           = ["TTGLep_LO"]
dirs["TTG"]              = ["TTGLep_LO", "TTGLep_ptG100To200_LO", "TTGLep_ptG200_LO", "TTGSingleLep_LO", "TTGSingleLep_ptG100To200_LO", "TTGSingleLep_ptG200_LO", "TTGHad_LO", "TTGHad_ptG100To200_LO", "TTGHad_ptG200_LO"]
dirs["TTG_sys_incl"]     = ["TTGLep_LO", "TTGSingleLep_LO"]
#dirs["TTG"]              = ["TTGLep_LO", "TTGSingleLep_LO", "TTGHad_LO"]
dirs["TTG_TuneUp"]       = ["TTGLep_TuneUp_LO", "TTGSingleLep_TuneUp_LO"]
dirs["TTG_TuneDown"]     = ["TTGLep_TuneDown_LO", "TTGSingleLep_TuneDown_LO"]
dirs["TTG_erdOn"]        = ["TTGLep_erdOn_LO", "TTGSingleLep_erdOn_LO"]
dirs["TTG_GluonMove"]   = ["TTGLep_GluonMove_LO", "TTGSingleLep_GluonMove_LO"]
dirs["TTG_QCDbased"]    = ["TTGLep_QCDbased_LO", "TTGSingleLep_QCDbased_LO"]

dirs["TG"]               = ["TGJets_comb"] #"TGJets_lep"
#["TGJets_lep"]

dirs["singleTop"]        = ["T_tWch_incl", "TBar_tWch_incl", "TToLeptons_sch_amcatnlo", "T_tch_pow", "TBar_tch_pow"] + dirs["TG"]
dirs["st_tW"]            = ["T_tWch_incl", "TBar_tWch_incl"]
dirs["st_tch"]           = ["T_tch_pow", "TBar_tch_pow"] + dirs["TG"]
dirs["st_sch"]           = ["TToLeptons_sch_amcatnlo"]

dirs["top"]              = dirs["TT_pow"] + dirs["singleTop"]

# other
dirs["TZQ"]              = ["tZq_ll"]
#dirs["TWZ"]              = ["tWll", "tWnunu"]
#dirs["THQ"]              = ["THQ"]
#dirs["THW"]              = ["THW"]
#dirs["TTH"]              = ["TTHbbLep", "TTHbbSemiLep" "TTHnobb_pow"]

dirs["TTW"]              = ["TTWToLNu", "TTWToQQ"]
dirs["TTZ"]              = ["TTZToLLNuNu", "TTZToLLNuNu_m1to10", "TTZToQQ"]

#dirs["TTTT"]             = ["TTTT"]
#dirs["TTWZ"]             = ["TTWZ"]
#dirs["TTZZ"]             = ["TTZZ"]
#dirs["TTWW"]             = ["TTWW"]

#dirs["WWW"]              = ["WWW_4F"]
#dirs["WWZ"]              = ["WWZ"]
#dirs["WZZ"]              = ["WZZ"]
#dirs["ZZZ"]              = ["ZZZ"]

dirs["ZG_lowMLL"]        = ["ZGToLLG_lowMLL"]
dirs["ZG_lowMLL_lowGPt"]        = ["ZGToLLG_lowMLL_lowGPt"]
dirs["ZG_loose"]         = ["ZGToLLG_LoosePtlPtg"]
dirs["WJets"]            = ["W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu", "W4JetsToLNu"]
dirs["WG"]               = ["WGToLNuG"]
dirs["WG_NLO"]           = ["WGToLNuG_amcatnlo_ext1"]

dirs["VV"]               = ["VVTo2L2Nu"]

dirs["WW"]               = ["WWToLNuQQ", "WWTo4Q"]
dirs["WZ"]               = ["WZTo1L3Nu", "WZTo1L1Nu2Q", "WZTo2L2Q", "WZTo3LNu_amcatnlo_comb"] #FIXME: WZTo3LNu_amcatnlo_comb
dirs["ZZ"]               = ["ZZTo2L2Q", "ZZTo2Q2Nu", "ZZTo4L_amcatnlo" ]  #FIXME: ZZTo4L_amcatnlo

#dirs["WW"]               = [] #["WWTo2L2Nu"]
#dirs["ZZ"]               = ["ZZTo2L2Q", "ZZTo4L"] #"ZZTo2L2Nu"
#dirs["WZ"]               = ["WZTo3LNu_amcatnlo"]

#dirs["GluGlu"]           = ["GluGluHToZZTo4L", "GluGluToContinToZZTo2e2mu", "GluGluToContinToZZTo2e2tau", "GluGluToContinToZZTo2mu2tau", "GluGluToContinToZZTo4e", "GluGluToContinToZZTo4mu", "GluGluToContinToZZTo4tau"]

dirs["other"]            = []
dirs["other"]           += dirs["TZQ"] #  + dirs["TWZ"] + dirs["THW"] + dirs["THQ"]
dirs["other"]           += dirs["TTW"]  + dirs["TTZ"]
#dirs["other"]           += dirs["TTWZ"] + dirs["TTZZ"] + dirs["TTWW"] + dirs["TTTT"]
#dirs["other"]           += dirs["WWZ"] + dirs["WZZ"]  + dirs["ZZZ"] + dirs["WWW"]
dirs["other"]           += dirs["VV"]
dirs["other"]           += dirs["WW"]   + dirs["WZ"]  + dirs["ZZ"]
#dirs["other"]           += dirs["GluGlu"]

#dirs["QCD_mu"]           = [ "QCD_Mu_pt20to30", "QCD_Mu_pt30to50", "QCD_Mu_pt50to80", "QCD_Mu_pt80to120", "QCD_Mu_pt120to170_comb", "QCD_Mu_pt170to300", "QCD_Mu_pt300to470_comb", "QCD_Mu_pt470to600", "QCD_Mu_pt600to800", "QCD_Mu_pt800to1000_ext", "QCD_Mu_pt1000toInf" ]
dirs["QCD_mu"]           = [ "QCD_Mu_pt15to20", "QCD_Mu_pt20to30", "QCD_Mu_pt30to50", "QCD_Mu_pt50to80", "QCD_Mu_pt80to120", "QCD_Mu_pt120to170_comb", "QCD_Mu_pt170to300", "QCD_Mu_pt300to470_comb", "QCD_Mu_pt470to600", "QCD_Mu_pt600to800", "QCD_Mu_pt800to1000_ext", "QCD_Mu_pt1000toInf" ]
dirs["QCD_e"]            = [ "QCD_Ele_pt20to30", "QCD_Ele_pt30to50", "QCD_Ele_pt50to80", "QCD_Ele_pt80to120", "QCD_Ele_pt120to170", "QCD_Ele_pt170to300", "QCD_Ele_pt300toInf" ]
dirs["QCD_e"]           += [ "QCD_bcToE_pt20to30", "QCD_bcToE_pt30to80", "QCD_bcToE_pt80to170", "QCD_bcToE_pt170to250", "QCD_bcToE_pt250toInf" ]
dirs["QCD_e80To120"]    = [ "QCD_Ele_pt80to120" ]
dirs["QCD_mu80To120"]    = [ "QCD_Mu_pt80to120" ]

dirs["QCD"]              = dirs["QCD_mu"] + dirs["QCD_e"]
dirs["GJets"]            = ["GJets_HT40to100", "GJets_HT100to200", "GJets_HT200to400", "GJets_HT400to600", "GJets_HT600toInf"]

dirs["GQCD"]             = dirs["QCD_mu"] + dirs["QCD_e"] + dirs["GJets"]

dirs["all_noOther_noTT"] = dirs["DY_LO"] + dirs["ZG_lowMLL"] + dirs["WJets"] + dirs["WG"] # + dirs["QCD"] + dirs["GJets"]
dirs["all_noTT"]         = dirs["all_noOther_noTT"] + dirs["other"]

dirs["all_noOther"]      = dirs["TTG"] + dirs["top"] + dirs["DY_LO"] + dirs["ZG_lowMLL"] + dirs["WJets"] + dirs["WG"] + dirs["QCD"] + dirs["GJets"]
dirs["all"]              = dirs["all_noOther"] + dirs["other"]

dirs["all_e"]            = dirs["TTG"] + dirs["top"] + dirs["DY_LO"] + dirs["ZG_lowMLL"] + dirs["WJets"] + dirs["WG"] + dirs["QCD_e"] + dirs["GJets"] + dirs["other"]
dirs["all_mu"]           = dirs["TTG"] + dirs["top"] + dirs["DY_LO"] + dirs["ZG_lowMLL"] + dirs["WJets"] + dirs["WG"] + dirs["QCD_mu"] + dirs["GJets"] + dirs["other"]

dirs["all_noQCD_noOther"] = dirs["TTG"] + dirs["top"] + dirs["DY_LO"] + dirs["ZG_lowMLL"] + dirs["WJets"] + dirs["WG"]
dirs["all_noQCD"]         = dirs["all_noQCD_noOther"] + dirs["other"]

dirs["VG"]               = dirs["ZG_lowMLL"] + dirs["WG"]
#dirs["rest"]             = dirs["singleTop"] + dirs["TG"] + dirs["other"]
dirs["rest"]             = dirs["other"]

directories = { key : [ os.path.join( data_directory_, postprocessing_directory_, dir) for dir in dirs[key] ] for key in dirs.keys() }

# Samples
DY_LO            = getMCSample(name="DY_LO",            redirector=redirector, color=color.DY,              texName="Drell-Yan",                directory=directories["DY_LO"], noCheckProxy=False, fromDPM=fromDPM)
#Zinv             = getMCSample(name="Zinv",             redirector=redirector, color=color.Zinv,            texName="Z(#nu#nu)+jets",    directory=directories["Z_NuNu"], noCheckProxy=False, fromDPM=fromDPM)
Top              = getMCSample(name="Top",              redirector=redirector, color=color.TT,              texName="t / t#bar{t}",        directory=directories["top"], noCheckProxy=True, fromDPM=fromDPM)
TT_pow           = getMCSample(name="TT_pow",           redirector=redirector, color=color.TT,              texName="t#bar{t}",          directory=directories["TT_pow"], noCheckProxy=True, fromDPM=fromDPM)
#TT_Lep           = getMCSample(name="TT_pow",           redirector=redirector, color=color.TT,              texName="t#bar{t}",          directory=directories["TT_Lep"], noCheckProxy=True, fromDPM=fromDPM)
#TT_SemiLep       = getMCSample(name="TT_pow",           redirector=redirector, color=color.TT,              texName="t#bar{t}",          directory=directories["TT_SemiLep"], noCheckProxy=True, fromDPM=fromDPM)
singleTop        = getMCSample(name="singleTop",        redirector=redirector, color=color.T,               texName="single-t",          directory=directories["singleTop"], noCheckProxy=True, fromDPM=fromDPM)
ST_tW            = getMCSample(name="ST_tW",            redirector=redirector, color=color.T,               texName="tW",                directory=directories["st_tW"], noCheckProxy=True, fromDPM=fromDPM)
ST_tch           = getMCSample(name="ST_tch",           redirector=redirector, color=color.T,               texName="t (t-ch)",          directory=directories["st_tch"], noCheckProxy=True, fromDPM=fromDPM)
ST_sch           = getMCSample(name="ST_sch",           redirector=redirector, color=color.T,               texName="t (s-ch)",          directory=directories["st_sch"], noCheckProxy=True, fromDPM=fromDPM)
TTG_NLO          = getMCSample(name="TTG_NLO",          redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma (NLO)",    directory=directories["TTG_NLO"], noCheckProxy=True, fromDPM=fromDPM)
TTG              = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG"], noCheckProxy=True, fromDPM=fromDPM)
TTG_sys_incl     = getMCSample(name="TTG_sys",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_sys_incl"], noCheckProxy=True, fromDPM=fromDPM)
TTG_TuneUp       = getMCSample(name="TTG_TuneUp",       redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_TuneUp"], noCheckProxy=True, fromDPM=fromDPM)
TTG_TuneDown     = getMCSample(name="TTG_TuneDown",     redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_TuneDown"], noCheckProxy=True, fromDPM=fromDPM)
TTG_erdOn        = getMCSample(name="TTG_erdOn",        redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_erdOn"], noCheckProxy=True, fromDPM=fromDPM)
TTG_GluonMove    = getMCSample(name="TTG_GluonMove",    redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_GluonMove"], noCheckProxy=True, fromDPM=fromDPM)
TTG_QCDbased     = getMCSample(name="TTG_QCDbased",     redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG_QCDbased"], noCheckProxy=True, fromDPM=fromDPM)
TTGLep           = getMCSample(name="TTGLep",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTGLep"], noCheckProxy=True, fromDPM=fromDPM)
TTGSemiLep       = getMCSample(name="TTGSemiLep",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTGSemiLep"], noCheckProxy=True, fromDPM=fromDPM)
WJets            = getMCSample(name="WJets",            redirector=redirector, color=color.W,               texName="W+jets",            directory=directories["WJets"], noCheckProxy=True, fromDPM=fromDPM)
ZG               = getMCSample(name="ZG",               redirector=redirector, color=color.ZGamma,          texName="Z#gamma",           directory=directories["ZG_lowMLL"], noCheckProxy=True, fromDPM=fromDPM)
ZG_loose         = getMCSample(name="ZG_l",               redirector=redirector, color=color.ZGamma,          texName="Z#gamma",           directory=directories["ZG_loose"], noCheckProxy=True, fromDPM=fromDPM)
#ZG_lowpt         = getMCSample(name="ZG_lowpt",         redirector=redirector, color=color.ZGamma,          texName="Z#gamma",           directory=directories["ZG_lowMLL_lowGPt"], noCheckProxy=True, fromDPM=fromDPM)
TG               = getMCSample(name="TG",               redirector=redirector, color=color.TGamma,          texName="t#gamma",           directory=directories["TG"], noCheckProxy=True, fromDPM=fromDPM)
WG               = getMCSample(name="WG",               redirector=redirector, color=color.WGamma,          texName="W#gamma",           directory=directories["WG"], noCheckProxy=True, fromDPM=fromDPM)
WG_NLO           = getMCSample(name="WG_NLO",               redirector=redirector, color=color.WGamma,          texName="W#gamma",           directory=directories["WG_NLO"], noCheckProxy=True, fromDPM=fromDPM)
other            = getMCSample(name="otherold",            redirector=redirector, color=color.Other,           texName="Other",             directory=directories["other"], noCheckProxy=True, fromDPM=fromDPM)
GQCD             = getMCSample(name="GQCD",               redirector=redirector, color=color.QCD,             texName="Multijet",         directory=directories["GQCD"], noCheckProxy=True, fromDPM=fromDPM)
QCD             = getMCSample(name="QCD",               redirector=redirector, color=color.QCD,             texName="Multijet",         directory=directories["QCD"], noCheckProxy=True, fromDPM=fromDPM)
QCD_e           = getMCSample(name="QCD_e",             redirector=redirector, color=color.QCD,             texName="Multijet",         directory=directories["QCD_e"], noCheckProxy=True, fromDPM=fromDPM)
QCD_mu          = getMCSample(name="QCD_mu",            redirector=redirector, color=color.QCD,             texName="Multijet",         directory=directories["QCD_mu"], noCheckProxy=True, fromDPM=fromDPM)
GJets           = getMCSample(name="GJets",             redirector=redirector, color=color.GJets,           texName="#gamma+jets",       directory=directories["GJets"], noCheckProxy=True, fromDPM=fromDPM)
QCD_e80To120     = getMCSample(name="QCD_e80To120",            redirector=redirector, color=color.QCD,             texName="Multijet",         directory=directories["QCD_e80To120"], noCheckProxy=True, fromDPM=fromDPM)
QCD_mu80To120     = getMCSample(name="QCD_mu80To120",            redirector=redirector, color=color.QCD,             texName="Multijet",         directory=directories["QCD_mu80To120"], noCheckProxy=True, fromDPM=fromDPM)

VG              = getMCSample(name="VG",               redirector=redirector, color=color.WGamma,          texName="V+#gamma",          directory=directories["VG"], noCheckProxy=True, fromDPM=fromDPM)
rest            = getMCSample(name="other",             redirector=redirector, color=color.Other,          texName="Other",             directory=directories["rest"], noCheckProxy=True, fromDPM=fromDPM)

all_mc_mu        = getMCSample(name="all_mc_mu",        redirector=redirector, color=color.TT,              texName="all",               directory=directories["all_mu"], noCheckProxy=True, fromDPM=fromDPM)
all_mc_e         = getMCSample(name="all_mc_e",         redirector=redirector, color=color.TT,              texName="all",               directory=directories["all_e"], noCheckProxy=True, fromDPM=fromDPM)
all_mc           = getMCSample(name="all_mc",           redirector=redirector, color=color.TT,              texName="all",               directory=directories["all"], noCheckProxy=True, fromDPM=fromDPM)
all_noOther      = getMCSample(name="all_noOther",      redirector=redirector, color=color.TT,              texName="all_noOther",       directory=directories["all_noOther"], noCheckProxy=True, fromDPM=fromDPM)
all_noQCD        = getMCSample(name="all_noQCD",        redirector=redirector, color=color.TT,              texName="all",               directory=directories["all_noQCD"], noCheckProxy=True, fromDPM=fromDPM)
all_noTT         = getMCSample(name="all_noTT",         redirector=redirector, color=color.TT,              texName="all_noTT",          directory=directories["all_noTT"], noCheckProxy=True, fromDPM=fromDPM)
all_noOther_noTT = getMCSample(name="all_noOther_noTT", redirector=redirector, color=color.TT,              texName="all_noOther_noTT",  directory=directories["all_noOther_noTT"], noCheckProxy=True, fromDPM=fromDPM)

signals = []


if __name__ == "__main__":

    def get_parser():
        """ Argument parser for post-processing module.
        """
        import argparse
        argParser = argparse.ArgumentParser(description = "Argument parser for nanoPostProcessing")
        argParser.add_argument("--check",   action="store_true", help="check root files?")
        argParser.add_argument("--deepcheck",   action="store_true", help="check events of root files?")
        argParser.add_argument("--checkWeight", action="store_true", help="check weight?")
        argParser.add_argument("--remove",  action="store_true", help="remove corrupt root files?")
        argParser.add_argument("--log",         action="store_true", help="print each filename?")
        return argParser

    args = get_parser().parse_args()

    if not (args.check or args.deepcheck or args.checkWeight): sys.exit(0)

    # check Root Files
    from Analysis.Tools.helpers import checkRootFile, deepCheckRootFile, deepCheckWeight
    from multiprocessing        import Pool

    def checkFile( file ):
                if args.log: logger.info( "Checking filepath: %s"%file )
                corrupt = False
                if args.check:
                    corrupt = not checkRootFile(file, checkForObjects=["Events"])
                if args.deepcheck and not corrupt:
                    corrupt = not deepCheckRootFile(file)
                if args.checkWeight and not corrupt:
                    corrupt = not deepCheckWeight(file)
                if corrupt:
                    if file.startswith("root://hephyse.oeaw.ac.at/"):
                        file = file.split("root://hephyse.oeaw.ac.at/")[1]
                    logger.info( "File corrupt: %s"%file )
                    if args.remove:
                        logger.info( "Removing file: %s"%file )
                        os.system( "/usr/bin/rfrm -f %s"%file )

    pathes = [ path for dirList in directories.values() for path in dirList ]

    files = []
    for path in pathes:
        try:
            sample = getMCSample(name="sample", redirector=redirector, directory=path)
            files += sample.files
            del sample
        except:
            logger.info( "Sample not processed: %s"%path )

    pool = Pool( processes=16 )
    _ = pool.map( checkFile, files )
    pool.close()
