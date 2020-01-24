import os
import datetime

from helpers import *

user          = os.getenv("USER")
hostname      = os.getenv("HOSTNAME")
batch_output  = "/mnt/hephy/cms/%s/batch_output/"%(user)


def get_parser():
    ''' Argument parser for post-processing module.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser for nanoPostProcessing")
    argParser.add_argument('--file',       action='store', type=str, default='nanoPostProcessing_Summer16', help="postprocessing sh file to check")
    argParser.add_argument('--createExec', action='store_true', help="create .sh file with missing files?")
    argParser.add_argument('--overwrite',  action='store_true', help="overwrite existing missingFiles.sh file?")
    return argParser

args = get_parser().parse_args()

# Logging
if __name__=="__main__":
    import Analysis.Tools.logger as logger
    logger = logger.get_logger("INFO", logFile = None )
    import RootTools.core.logger as logger_rt
    logger_rt = logger_rt.get_logger("INFO", logFile = None )

else:
    import logging
    logger = logging.getLogger(__name__)

if args.file.endswith(".sh"):
    args.file = args.file.rstrip(".sh")


# Load File
logger.info( "Now running on pp file %s" %args.file )
file     = os.path.expandvars( "$CMSSW_BASE/src/TTGammaEFT/postprocessing/%s.sh" % args.file )
dictList = getDataDictList( file )
isData   = "Run" in args.file

logFiles = os.listdir(batch_output)
logFiles = filter( lambda file: file.endswith(".out"), logFiles )
logFiles = map( lambda file: os.path.join( batch_output, file ), logFiles )

logs = [{"cpuTime":getCPUTime( file ), "filePath":file, "jobID":getJobIDFromLogName(file), "command":getCommandFromLog(file)} for file in logFiles]
logs = filter( lambda log: not -1 in log["cpuTime"].values(), logs )

writeExec = []
for sampleDict in dictList:
    command = sampleDict["command"].split(" #SPLIT")[0]

    jobFiles = filter( lambda log: log["command"].replace(" ","").startswith(command.replace(" ","")), logs )
    if not jobFiles: continue

    jobIDs   = [ file["jobID"] for file in jobFiles ]
#    jobs     = filter( lambda file: file["jobID"] == max(jobIDs), jobFiles ) # get latest ones
    jobs = jobFiles

    maxCpuTime = max([ file["cpuTime"]["hours"]*3600+file["cpuTime"]["minutes"]*60+file["cpuTime"]["seconds"] for file in jobs ])

    if args.createExec:
        writeExec.append( sampleDict["command"] + " " + str(datetime.timedelta(seconds=maxCpuTime)) + "\n" )
    else:
        print datetime.timedelta(seconds=maxCpuTime), max(jobIDs), sampleDict["sample"], sampleDict["skim"]


if args.createExec:
    outFile = args.file.split(".sh")[0] + "_wTime.sh"
    with open( outFile, "w" ) as f:
        for line in writeExec:
            f.write(line)
