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
    postprocessing_directory_ = postprocessing_locations.MC2016_incl

try:
    fromDPM = sys.modules['__main__'].fromEOS != "True"
except:
    fromDPM = not "clip" in os.getenv("HOSTNAME").lower()

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

# Directories
dirs = {}

dirs["TTGNLO"]           = ["TTGJets_comb"]
dirs["TTGLep"]           = ["TTGLep_LO", "TTGLep_ptG100To200_LO", "TTGLep_ptG200_LO"]
dirs["TTGSemiLep"]       = ["TTGSingleLep_LO", "TTGSingleLep_ptG100To200_LO", "TTGSingleLep_ptG200_LO"]
dirs["TTG"]              = ["TTGLep_LO", "TTGLep_ptG100To200_LO", "TTGLep_ptG200_LO", "TTGSingleLep_LO", "TTGSingleLep_ptG100To200_LO", "TTGSingleLep_ptG200_LO", "TTGHad_LO", "TTGHad_ptG100To200_LO", "TTGHad_ptG200_LO"]

#dirs["TTGLep"]           = ["TTGLep_LO"]
#dirs["TTGSemiLep"]       = ["TTGSingleLep_LO"]
#dirs["TTG"]              = ["TTGLep_LO", "TTGSingleLep_LO", "TTGHad_LO"]

directories = { key : [ os.path.join( data_directory_, postprocessing_directory_, dir) for dir in dirs[key] ] for key in dirs.keys() }

# Samples
#TTG_NLO         = getMCSample(name="TTG_NLO",          redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTGNLO"], noCheckProxy=True, fromDPM=fromDPM)
TTG             = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTG"], noCheckProxy=True, fromDPM=fromDPM)
TTGSemiLep      = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTGSemiLep"], noCheckProxy=True, fromDPM=fromDPM)
TTGLep          = getMCSample(name="TTG",              redirector=redirector, color=color.TTG,             texName="t#bar{t}#gamma",    directory=directories["TTGLep"], noCheckProxy=True, fromDPM=fromDPM)

#print TTG_NLO.getYieldFromDraw(selectionString="1") #(Sum$(abs(LHEPart_pdgId)==11)+Sum$(abs(LHEPart_pdgId)==13)+Sum$(abs(LHEPart_pdgId)==15))==2")
print TTG.getYieldFromDraw(selectionString="pTStitching==1&&(Sum$(abs(LHEPart_pdgId)==11)+Sum$(abs(LHEPart_pdgId)==13)+Sum$(abs(LHEPart_pdgId)==15))==2", weightString="weight")

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
