from TTGammaEFT.Analysis.SystematicEstimator import SystematicEstimator
from TTGammaEFT.Analysis.Region              import Region
from TTGammaEFT.Analysis.SetupHelpers        import dilepChannels, lepChannels
from Analysis.Tools.u_float                  import u_float

# Logging
if __name__=="__main__":
    import Analysis.Tools.logger as logger
    logger = logger.get_logger( "INFO", logFile=None)
    import RootTools.core.logger as logger_rt
    logger_rt = logger_rt.get_logger( "INFO", logFile=None )
else:
    import logging
    logger = logging.getLogger(__name__)

class SumEstimate(SystematicEstimator):
    def __init__(self, name, cacheDir=None):
        super(SumEstimate, self).__init__(name, cacheDir=cacheDir)

    def _estimate(self, region, channel, setup, signalAddon=None, overwrite=False):
        if channel=='all':
            # 'all' is the total of all contributions
            return sum([self.cachedEstimate(region, c, setup, signalAddon=signalAddon) for c in lepChannels])
        if channel=='SFtight':
            return sum([self.cachedEstimate(region, c, setup, signalAddon=signalAddon) for c in dilepChannels])
        else:
            raise NotImplementedError("Run sum_estimates.py first")
