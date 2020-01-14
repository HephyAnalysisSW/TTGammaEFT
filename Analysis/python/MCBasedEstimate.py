from Analysis.Tools.u_float                  import u_float

from TTGammaEFT.Analysis.SystematicEstimator import SystematicEstimator
from TTGammaEFT.Analysis.SetupHelpers        import dilepChannels, lepChannels
from TTGammaEFT.Tools.cutInterpreter         import cutInterpreter

# Logging
if __name__=="__main__":
    import Analysis.Tools.logger as logger
    logger = logger.get_logger( "INFO", logFile=None)
    import RootTools.core.logger as logger_rt
    logger_rt = logger_rt.get_logger( "INFO", logFile=None )
else:
    import logging
    logger = logging.getLogger(__name__)

class MCBasedEstimate(SystematicEstimator):
    def __init__(self, name, process, cacheDir=None):
        super(MCBasedEstimate, self).__init__(name, cacheDir=cacheDir)
        self.process = process
        
    def _transferFactor(self, channel, setup, overwrite=False):
        """Estimate transfer factor for QCD in "region" using setup"""
        return u_float(0, 0)

    def _dataDrivenTransferFactor(self, channel, setup, overwrite=False):
        """Estimate transfer factor for QCD in "region" using setup"""
        return u_float(0, 0)

    def _estimate(self, region, channel, setup, overwrite=False):

        ''' Concrete implementation of abstract method 'estimate' as defined in Systematic
        '''

        logger.debug( "MC prediction for %s channel %s" %(self.name, channel) )

        if channel=='all':
            # 'all' is the total of all contributions
            return sum([self.cachedEstimate(region, c, setup) for c in lepChannels])

        elif channel=='SFtight':
            # 'SFtight' is the total of mumutight and eetight contributions
            return sum([self.cachedEstimate(region, c, setup) for c in dilepChannels])

        else:
            preSelection = setup.preselection('MC', channel=channel)
            cuts         = [ region.cutString( setup.sys['selectionModifier'] ), preSelection['cut'] ]
            if setup.parameters["photonIso"] and setup.parameters["photonIso"] != "lowChgIsolowSieie":
                self.processCut = self.processCut.replace("photoncat", "photonhadcat")
            if self.processCut:
                cuts.append( cutInterpreter.cutString(self.processCut) )
                logger.info( "Adding process specific cut %s"%self.processCut )
            cut          = "&&".join( cuts )
            weight       = preSelection['weightStr']

            logger.debug( "Using cut %s and weight %s"%(cut, weight) )

            return setup.lumi/1000.*u_float(**self.process.getYieldFromDraw(selectionString = cut, weightString = weight) )


if __name__ == "__main__":
    from TTGammaEFT.Analysis.regions      import regionsTTG, noPhotonRegionTTG, inclRegionsTTG
    from TTGammaEFT.Analysis.SetupHelpers import allRegions
    from TTGammaEFT.Analysis.Setup        import Setup

    print "lowPT"
    r = regionsTTG[0]

    setup = Setup(year=2016, photonSelection=True)
    setup = setup.sysClone(parameters=allRegions["VG3"]["parameters"])

    estimate = MCBasedEstimate( name="TTG", process=setup.processes["TTG"] )
    estimate.initCache(setup.defaultCacheDir())
    res = estimate._estimate( r, "e", setup, overwrite=False )
    print "TTG", res


    estimate = MCBasedEstimate( name="TTG_gen", process=setup.processes["TTG_gen"] )
    estimate.initCache(setup.defaultCacheDir())
    res = estimate._estimate( r, "e", setup, overwrite=False )
    print "TTG_gen", res


    estimate = MCBasedEstimate( name="TTG_misID", process=setup.processes["TTG_misID"] )
    estimate.initCache(setup.defaultCacheDir())
    res = estimate._estimate( r, "e", setup, overwrite=False )
    print "TTG_misID", res


    estimate = MCBasedEstimate( name="TTG_had", process=setup.processes["TTG_had"] )
    estimate.initCache(setup.defaultCacheDir())
    res = estimate._estimate( r, "e", setup, overwrite=False )
    print "TTG_had", res

