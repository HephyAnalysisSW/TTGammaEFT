# Standard Imports
import os, sys
import ROOT

# RootTools Imports
from RootTools.core.Sample import Sample

# Colors
from TTGammaEFT.Samples.color import color
from TTGammaEFT.Samples.helpers import getMCSample

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
    postprocessing_directory_ = postprocessing_locations.MC2017

try:
    fromDPM = sys.modules['__main__'].fromEOS != "True"
except:
    fromDPM = not "clip" in os.getenv("HOSTNAME").lower()

if "gammaSkim" in os.environ and os.environ["gammaSkim"] == "True":
    postprocessing_directory_ = postprocessing_directory_.replace("/dilep/", "/dilepGamma/")

# Redirector
try:
    redirector = sys.modules['__main__'].redirector
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
dirs['DY_LO']            = ["DYJetsToLL_M50_LO_comb", "DYJetsToLL_M10to50_LO"]
dirs['TT_pow']           = ["TTLep_pow", "TTSingleLep_pow"]

dirs['singleTop']        = ["TBar_tWch_ext", "T_tWch_ext", "T_tch_pow", "TBar_tch_pow", "TToLeptons_sch_amcatnlo" ]

dirs["TTGSemiLep"]       = ["TTGSingleLep_LO"]
dirs["TTGLep"]           = ["TTGLep_LO"]
dirs["TTG"]              = ["TTGLep_LO", "TTGSingleLep_LO", "TTGHad_LO"]

dirs['ZGToLLG']          = ["ZGToLLG"]
dirs['ZG_lowMLL']        = ["ZGToLLG_lowMLL"]
dirs['TG']               = ["TGJets"]
dirs["WJets"]            = ["W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu", "W4JetsToLNu"]
dirs['WG']               = ["WGToLNuG"]
dirs['WG_NLO']           = ["WGToLNuG_amcatnlo"]

dirs['TZQ']              = ["tZq_ll", "tZq_nunu"]
dirs['THQ']              = ["THQ"]
dirs['THW']              = ["THW"]

#dirs['TTW']              = ["TTW_LO_comb"]
dirs['TTW']              = ["TTWToLNu", "TTWToQQ"]
dirs['TTZ']              = ["TTZToQQ", "TTZToLLNuNu", "TTZToLLNuNu_m1to10"]

dirs['TTWZ']             = ["TTWZ"]
dirs['TTZZ']             = ["TTZZ"]
dirs['TTWW']             = ["TTWW"]
dirs['TTTT']             = ["TTTT"]

dirs['WWW']              = ["WWW_4F"]
dirs['WWZ']              = ["WWZ_4F"]
dirs['WZZ']              = ["WZZ"]
dirs['ZZZ']              = ["ZZZ"]

dirs['VV']               = ["VVTo2L2Nu"]
dirs['WW']               = ["WWToLNuQQ"] #, "WWTo1L1Nu2Q"] #"WWTo2L2Nu"
dirs['WZ']               = ["WZTo1L3Nu", "WZTo1L1Nu2Q", "WZTo2L2Q", "WZTo3LNu_amcatnlo"]
dirs['ZZ']               = ["ZZTo2L2Q"] #"ZZTo2L2Nu"

dirs['GluGlu']           = ["GluGluToContinToZZTo2e2mu", "GluGluToContinToZZTo2e2tau", "GluGluToContinToZZTo2mu2tau", "GluGluToContinToZZTo4e", "GluGluToContinToZZTo4mu"]

dirs['other']            = []
dirs['other']           += dirs['TZQ']  + dirs['THQ']  + dirs['THW']
dirs['other']           += dirs['TTW']  + dirs['TTZ']
dirs['other']           += dirs['TTWZ'] + dirs['TTZZ'] + dirs['TTWW'] + dirs['TTTT']
dirs['other']           += dirs['WWW']  + dirs['WWZ']  + dirs['WZZ']  + dirs['ZZZ']
dirs['other']           += dirs['VV']
dirs['other']           += dirs['WW']   + dirs['WZ']   + dirs['ZZ']
dirs['other']           += dirs['GluGlu']

dirs['all_noOther']      = dirs['TTG'] + dirs['TT_pow'] + dirs['DY_LO'] + dirs['singleTop']
dirs['all']              = dirs['all_noOther'] + dirs['other']

directories = { key : [ os.path.join( data_directory_, postprocessing_directory_, dir) for dir in dirs[key] ] for key in dirs.keys() }

# Samples
DY_LO_17           = getMCSample(name="DY_LO",            redirector=redirector, color=color.DY,              texName="DY (LO)",           directory=directories['DY_LO'], noCheckProxy=False, fromDPM=fromDPM)
TT_pow_17          = getMCSample(name="TT_pow",           redirector=redirector, color=color.TT,              texName="t#bar{t}",          directory=directories['TT_pow'], noCheckProxy=True, fromDPM=fromDPM)
singleTop_17       = getMCSample(name="singleTop",        redirector=redirector, color=color.T,               texName="single-t",          directory=directories['singleTop'], noCheckProxy=True, fromDPM=fromDPM)
TTGLep_17          = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories['TTGLep'], noCheckProxy=True, fromDPM=fromDPM)
TTGSemiLep_17      = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories['TTGSemiLep'], noCheckProxy=True, fromDPM=fromDPM)
TTG_17             = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories['TTG'], noCheckProxy=True, fromDPM=fromDPM)
ZG_17              = getMCSample(name="ZG",               redirector=redirector, color=color.ZGamma,          texName="Z#gamma",           directory=directories['ZG_lowMLL'], noCheckProxy=True, fromDPM=fromDPM)
TG_17              = getMCSample(name="TG",               redirector=redirector, color=color.TGamma,          texName="t#gamma",           directory=directories['TG'], noCheckProxy=True, fromDPM=fromDPM)
WJets_17           = getMCSample(name="WJets",            redirector=redirector, color=color.W,               texName="W+jets",            directory=directories['WJets'], noCheckProxy=True, fromDPM=fromDPM)
WG_17              = getMCSample(name="WG",               redirector=redirector, color=color.WGamma,          texName="W#gamma",           directory=directories['WG'], noCheckProxy=True, fromDPM=fromDPM)
WG_NLO_17          = getMCSample(name="WG",               redirector=redirector, color=color.WGamma,          texName="W#gamma",           directory=directories['WG_NLO'], noCheckProxy=True, fromDPM=fromDPM)
other_17           = getMCSample(name="other",            redirector=redirector, color=color.Other,           texName="other",             directory=directories['other'], noCheckProxy=True, fromDPM=fromDPM)
all_17             = getMCSample(name="all",              redirector=redirector, color=color.TT,              texName="all",               directory=directories['all'], noCheckProxy=True, fromDPM=fromDPM)
all_noOther_17     = getMCSample(name="all_noOther",      redirector=redirector, color=color.TT,              texName="all_noOther",       directory=directories['all_noOther'], noCheckProxy=True, fromDPM=fromDPM)

signals = []

if __name__ == "__main__":

    def get_parser():
        ''' Argument parser for post-processing module.
        '''
        import argparse
        argParser = argparse.ArgumentParser(description = "Argument parser for nanoPostProcessing")
        argParser.add_argument('--check',   action='store_true', help="check root files?")
        argParser.add_argument('--deepcheck',   action='store_true', help="check events of root files?")
        argParser.add_argument('--checkWeight', action='store_true', help="check weight?")
        argParser.add_argument('--remove',  action='store_true', help="remove corrupt root files?")
        argParser.add_argument('--log',         action='store_true', help="print each filename?")
        return argParser

    args = get_parser().parse_args()

    if not (args.check or args.deepcheck or args.checkWeight): sys.exit(0)

    # check Root Files
    from Analysis.Tools.helpers import checkRootFile, deepCheckRootFile, deepCheckWeight
    from multiprocessing        import Pool

    def checkFile( file ):
        if not file:
            logger.info( "File not found!" )
            return
        elif args.log: logger.info( "Checking filepath: %s"%file )
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
            sample = getMCSample(name="sample", redirector=redirector, directory=path, fromDPM=fromDPM)
            files += sample.files
            del sample
        except:
            logger.info( "Sample not processed: %s"%path )

    pool = Pool( processes=16 )
    _ = pool.map( checkFile, files[::-1] )
    pool.close()
