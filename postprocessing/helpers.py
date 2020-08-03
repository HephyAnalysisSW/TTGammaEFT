import logging
logger = logging.getLogger(__name__)

def filterEmpty( strList ):
    return list( filter ( bool, strList ) )

def getDataDictList( filepath ):
    ''' Read postprocessing sh file and format it to dictionary
    '''
    with open( filepath, 'r' ) as f:
        ppLines = f.readlines()

    ppLines = [ line for line in ppLines if line.startswith('python') ]

    dictList = []
    for line in ppLines:
        skim    = filterEmpty( line.split("--skim ")[1].split(" ") )[0] if "--skim" in line else "gen"
        year    = filterEmpty( line.split("--year ")[1].split(" ") )[0] if "--year" in line else 2016
        dir     = filterEmpty( line.split("--processingEra ")[1].split(" ") )[0]
        sample  = filterEmpty( line.split("--sample ")[1].split(" ") )[0]
        command = line.split("\n")[0]
        if not filterEmpty( line.split("--sample ")[1].split(" ") )[1].startswith("--") and not filterEmpty( line.split("--sample ")[1].split(" ") )[1].startswith("#SPLIT"):
            sample += "_comb"
        nFiles = filterEmpty( line.split("#SPLIT")[1].split(" ") )[0].split("\n")[0]
        dictList.append( { "skim":skim, "year":int(year), "dir":dir, "sample":sample, "nFiles":int(nFiles), "command":command} )

    return dictList

def inLogFile( file, line ):
    with open( file, "r" ) as f:
        logLines = f.readlines()
    return any( [ line in logLine for logLine in logLines ] )

def getCPUTime( file ):
    with open( file, "r" ) as f:
        log = f.readlines()
    log = filter( lambda line: "Job Wall-clock time" in line, log )
    if not log: return {"hours":-1, "minutes":-1, "seconds":-1}
    hours, minutes, seconds = log[0].split(": ")[1].split("\n")[0].split(":")
    return {"hours":int(hours), "minutes":int(minutes), "seconds":int(seconds)}

def getCommandFromLog( file ):
    with open( file, "r" ) as f:
        log = f.readlines()
    for i, line in enumerate(log):
        if "Executing user command:" in line:
            command = log[i+1].split("\n")[0]
            return command
    return None

def getJobIDFromLogName( log ):
    jobID = log.split("/")[-1].split("batch.")[1].split(".")[0]
    if "-" in jobID:
        return int(jobID.split("-")[0])
    else:
        return int(jobID)

