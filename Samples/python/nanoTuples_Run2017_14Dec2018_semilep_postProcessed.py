# Standard Imports
import os, sys, copy
import ROOT

# RootTools Imports
from RootTools.core.Sample import Sample 

# TTGammaEFT Imports
from TTGammaEFT.Samples.helpers import getDataSample, merge

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
    postprocessing_directory_ = postprocessing_locations.Run2017_semilep

try:
    fromDPM = sys.modules['__main__'].fromEOS != "True"
except:
    fromDPM = not "clip" in os.getenv("HOSTNAME").lower()

if "gammaSkim" in os.environ and os.environ["gammaSkim"] == "True":
    postprocessing_directory_ = postprocessing_directory_.replace("/semilep/", "/semilepGamma/")

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

logger.info( "Loading data samples from directory %s", os.path.join(data_directory_, postprocessing_directory_ ) )

allSamples = [ 'SingleMuon', 'SingleElectron' ]
lumi       = 41.53

dirs = {}
for ( run, version ) in [ ( 'B', '' ), ( 'C', '' ), ( 'D', '' ), ( 'E', '' ), ( 'F', '' ) ]:
#    runTag = 'Run2017' + run + '_14Dec2018' + version
    runTag = 'Run2017' + run + '_31Mar2018' + version
    for pd in allSamples:
        dirs[ pd + "_Run2017" + run + version ] = [ pd + "_" + runTag ]

for pd in allSamples:
    merge( pd, 'Run2017',    [ 'Run2017B', 'Run2017C', 'Run2017D', 'Run2017E', 'Run2017F' ], dirs )
    merge( pd, 'Run2017CDE', [ 'Run2017C', 'Run2017D', 'Run2017E' ], dirs )

for key in dirs:
    dirs[key] = [ os.path.join( data_directory_, postprocessing_directory_, dir ) for dir in dirs[key] ]

allSamples_Data25ns  = []
for pd in allSamples:
    vars()[ pd + '_Run2017' ] = getDataSample( pd, 'Run2017', lumi*1000, dirs, redirector=redirector, fromDPM=fromDPM )
    allSamples_Data25ns += [ vars()[ pd + '_Run2017' ] ]

Run2017      = Sample.combine( "Run2017", allSamples_Data25ns, texName = "Data" )
Run2017.lumi = lumi*1000

for s in allSamples_Data25ns:
    s.color   = ROOT.kBlack
    s.isData  = True


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

    pool = Pool( processes=16 )
    _ = pool.map( checkFile, Run2017.files )
    pool.close()

