import os
import json

from Analysis.Tools.u_float           import u_float
from Analysis.Tools.MergingDirDB             import MergingDirDB
from TTGammaEFT.Analysis.SetupHelpers import dilepChannels, lepChannels
from TTGammaEFT.Analysis.Region       import Region
from TTGammaEFT.Tools.user            import cache_directory

# Logging
if __name__=="__main__":
    import Analysis.Tools.logger as logger
    logger = logger.get_logger( "INFO", logFile=None)
    import RootTools.core.logger as logger_rt
    logger_rt = logger_rt.get_logger( "INFO", logFile=None )
else:
    import logging
    logger = logging.getLogger(__name__)

class DataObservation():

    def __init__(self, name, process, cacheDir=None):
        self.name = name
        self.process = process
        self.initCache(cacheDir)

    def initCache(self, cacheDir="dataObs"):
        if cacheDir:
            self.cacheDir = os.path.join(cache_directory, cacheDir)
            try:    os.makedirs(cacheDir)
            except: pass

            cacheDirName       = os.path.join(cacheDir, self.name)
            self.cache = MergingDirDB(cacheDirName)
            if not self.cache: raise

        else:
            self.cache=None

    def uniqueKey(self, region, channel, setup):
        ## this is used in MCBasedEstimate
        if hasattr(setup, "blinding"): return str(region), channel, json.dumps(setup.sys, sort_keys=True), json.dumps(setup.parameters, sort_keys=True), json.dumps(setup.lumi, sort_keys=True), setup.blinding
        else:                          return str(region), channel, json.dumps(setup.sys, sort_keys=True), json.dumps(setup.parameters, sort_keys=True), json.dumps(setup.lumi, sort_keys=True)

    # alias for cachedObservation to make it easier to call the same function as for the mc"s
    def cachedEstimate(self, region, channel, setup, signalAddon=None, save=True, overwrite=False, checkOnly=False):
        return self.cachedObservation(region, channel, setup, overwrite=overwrite, checkOnly=checkOnly)

    def cachedObservation(self, region, channel, setup, save=True, overwrite=False, checkOnly=False):
        key =  self.uniqueKey(region, channel, setup)
        if (self.cache and self.cache.contains(key)) and not overwrite:
            res = self.cache.get(key)
            logger.debug( "Loading cached %s result for %r : %r"%(self.name, key, res) )
        elif self.cache and not checkOnly:
            res  = self.observation( region, channel, setup, overwrite)
            _res = self.cache.add( key, res, overwrite=True )
            logger.debug( "Adding cached %s result for %r"%(self.name, key) )
        elif not checkOnly:
            res = self.observation( region, channel, setup, overwrite )
        else:
            res = u_float(-1,0)
        return res if res >= 0 or checkOnly else u_float(0,0)

    def writeToCache(self, region, channel, setup, value, signalAddon=None, save=True, overwrite=False, checkOnly=False):
        key =  self.uniqueKey(region, channel, setup)
        if (self.cache and self.cache.contains(key)) and not overwrite:
            res = self.cache.get(key)
            if res.val != value.val: print "Warning, caches estimate not equal to input value: have %s, got %s"%(res, value)
            logger.debug( "Loading cached %s result for %r : %r"%(self.name, key, res) )
        elif self.cache and not checkOnly:
            _res = self.cache.add( key, value, overwrite=True )
            res = value
            logger.debug( "Adding cached %s result for %r"%(self.name, key) )
        else:
            res = u_float(-1,0)
        return res if res >= 0 or checkOnly else u_float(0,0)

    def observation(self, region, channel, setup, overwrite):

        if setup.nJet == "3p":
            setup4p = setup.sysClone( parameters={"nJet":(4,-1)} )
            setup3 = setup.sysClone( parameters={"nJet":(3,3)} )
            return sum([ self.cachedEstimate(region, channel, s, overwrite=overwrite) for s in [setup3,setup4p]])

        if channel=="all":
            return sum([self.cachedEstimate(region, c, setup, overwrite=overwrite) for c in lepChannels ])

        elif channel=="SFtight":
            return sum([self.cachedEstimate(region, c, setup, overwrite=overwrite) for c in dilepChannels ])

        else:
            preSelection = setup.preselection("Data", channel=channel)
#            cut = "&&".join([region.cutString(setup.sys['selectionModifier']), preSelection['cut']])
            cut = "&&".join([region.cutString(), preSelection['cut']])

            logger.debug( "Using cut %s"% cut )

            weight = preSelection['weightStr']
            if hasattr(setup, "blinding") and setup.blinding: weight += "*" + setup.blinding

            return u_float(**self.process.getYieldFromDraw(selectionString = cut, weightString = weight) )
