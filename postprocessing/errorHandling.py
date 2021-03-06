import os, sys, glob

from helpers import *

# Logging
if __name__=="__main__":
    import Analysis.Tools.logger as logger
    logger = logger.get_logger("INFO", logFile = None )
    import RootTools.core.logger as logger_rt
    logger_rt = logger_rt.get_logger("INFO", logFile = None )

else:
    import logging
    logger = logging.getLogger(__name__)

accepted_errors = [
    "Error in <TTreeFormula::Compile>:  Bad numerical expression : ", # missing trigger branches are handled with Alt$
    "input bins have zero error, and are ignored.",                   # TUnfold
    "No branch name is matching wildcard -> LHE_*",                   # samples without weights
    "slurmstepd:",                                                    # cancelled batch job or killed by walltime
    "Error in <TNetXNGFile::Close>:",                                 # dpm closing issue, dont care
    "Analysis.Tools.MergingDirDB",                                    # double entries in cache or caching error, dont care
    "Analysing bin errors",                                           # cardfile writer
    "Bin        Contents        Error           Notes",               # combine header
    "unknown branch -> MET_p",                                        # 2017 MET processing
    "ZGToLLG_01J_5f_lowMLL_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/crab_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1_legacy_nano_v4/190812_124339/0000/nanoAOD_65.root", #broken file
    "TTGamma_Dilept_TuneCP5_erdON_PSweights_13TeV-madgraph-pythia8/crab_RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1_legacy_nano_v6/200118_211725/0000/nanoAOD_10.root", #broken file
    "matching wildcard -> nLHE*",                                     # mc w/o LHE weights
    "matching wildcard -> LHE*",                                      # mc w/o LHE weights
]

trigger_words = [
    "error",
    "zombie",
]

def loopOverLogs( directory, filterCommand=None, addon=None, ignore="" ):

    logger.info("Checking log files in directory %s"%directory )

    files = list(filter(os.path.isfile, glob.glob(directory + "/*")))
#    files = list(filter(os.path.isfile, glob.glob(directory + "/*.err")))
    # sort logs by latest one
    files.sort(key=lambda x: -os.path.getmtime(x))

    # filter logs by latest cmd
    filteredFiles = []
    filteredCmds  = []
    for file in files:
        cmd = getCommandFromLog(file.replace(".err",".out"))

        if not cmd:
            logger.debug( "Could not find command for file %s"%file )
            continue

        # filter commands
        if filterCommand and not all( [c in cmd for c in filterCommand.split("*")] ): continue
        # check if a later version of the cmd has already been executed
        if cmd.replace(ignore,"").replace(" ","") not in [f.replace(ignore,"").replace(" ","") for f in filteredCmds]:
            filteredFiles.append(file)
            filteredCmds.append(cmd)

    logger.info("Loop over %i file%s"%(len(filteredFiles),"s" if len(filteredFiles)>1 else "") )

    # Loop over error filteredFiles
    for i, file in enumerate(filteredFiles):
        # filter for scripts like nanopostprocessing.py
        cmd = filteredCmds[i]

        with open( file, "r" ) as f:
            logs = f.readlines()

        logger.debug("Loop over %i entries in file"%len(logs))

        # Loop over error lines
        for log in logs:

            if any( word in log.lower() for word in trigger_words ):
                # Found error!
                logger.debug("Found error '%s' in file %s"%(log.split("\n")[0], file) )

                if any( expression.lower() in log.lower() for expression in accepted_errors ):
                    # Error is ok!
                    logger.debug("Error is accepted!")
                    continue

                # Found uncaught error!
                logger.info("Error in file %s:\t\t%s"%(file, log[:80].replace("\n"," ")))

                # logging error files and commands
                with open( "errorCommands.sh", "a" ) as ferr:
                    ferr.write( " ".join([cmd, addon if addon else "", "\n"]) )
                with open( "errorLogs.log", "a" ) as ferr:
                    ferr.write( file + "\n" )

                # Skipping rest of the log file
                break

if __name__ == "__main__":

    cmd   = sys.argv[1] if len(sys.argv) > 1 else None
    addon = sys.argv[2] if len(sys.argv) > 2 else None

    # clean up
    open( "errorCommands.sh", "w" )
    open( "errorLogs.log",    "w" )
    loopOverLogs( "/mnt/hephy/cms/%s/batch_output/"%os.getenv("USER"), filterCommand=cmd, addon=addon, ignore="--overwrite" )

