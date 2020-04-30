from TTGammaEFT.Analysis.DataDrivenFakeEstimate      import DataDrivenFakeEstimate
from TTGammaEFT.Analysis.DataDrivenQCDEstimate       import DataDrivenQCDEstimate
from TTGammaEFT.Analysis.MCBasedEstimate             import MCBasedEstimate
from TTGammaEFT.Analysis.SetupHelpers                import allProcesses

# Logging
if __name__=="__main__":
    import Analysis.Tools.logger as logger
    logger = logger.get_logger( "INFO", logFile=None)
    import RootTools.core.logger as logger_rt
    logger_rt = logger_rt.get_logger( "INFO", logFile=None )
else:
    import logging
    logger = logging.getLogger(__name__)


class EstimatorList:
    def __init__( self, setup, processes=allProcesses ):
        for p in processes:
            if "DD" in p:
                setattr( self, p, DataDrivenQCDEstimate( name=p ) )
            elif "had" in p:
                setattr( self, p, DataDrivenFakeEstimate( name=p, process=setup.processes[p] ) )
            else:
                setattr( self, p, MCBasedEstimate( name=p, process=setup.processes[p] ) )


    def constructEstimatorList(self, processes):
        self.estimatorList = [ getattr(self, p) for p in processes ]
        return self.estimatorList

    def constructProcessDict(self, processDict):
        self.processDict = { pName:self.constructEstimatorList( processes=pList["process"] ) for pName, pList in processDict.items() }
        return self.processDict
