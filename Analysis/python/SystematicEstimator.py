# Standard imports
import os
import abc
from math import sqrt
import json

# Framework imports
from Analysis.Tools.MergingDirDB      import MergingDirDB
from Analysis.Tools.u_float           import u_float
from TTGammaEFT.Tools.user            import cache_directory
from TTGammaEFT.Analysis.SetupHelpers import allChannels

# Logging
if __name__=="__main__":
    import Analysis.Tools.logger as logger
    logger = logger.get_logger( "INFO", logFile=None)
    import RootTools.core.logger as logger_rt
    logger_rt = logger_rt.get_logger( "INFO", logFile=None )
else:
    import logging
    logger = logging.getLogger(__name__)

class SystematicEstimator:
    __metaclass__ = abc.ABCMeta

    def __init__(self, name, cacheDir=None):
        logger.info("Initializing Systematic Estimator for %s"%name)
        self.name = name
        self.initCache(cacheDir)
        self.processCut = None

        if   "_gen"   in name: self.processCut = "photoncat0"
        elif "_misID" in name: self.processCut = "photoncat2"
        elif "_had"   in name: self.processCut = "photoncat13"

    def initCache(self, cacheDir="systematics"):
        logger.info("Initializing cache for %s in directory %s"%(self.name, cacheDir))
        if cacheDir:
            self.cacheDir = os.path.join(cache_directory, cacheDir)
            try:    os.makedirs(cacheDir)
            except: pass

            cacheDirName       = os.path.join(cacheDir, self.name)
            self.cache = MergingDirDB(cacheDirName)
            if not self.cache:
                raise Exeption("Cache not initiated!")

            if self.name.count("DD"):
                helperCacheDirName = os.path.join(cacheDir, self.name+"_helper")
                self.helperCache = MergingDirDB(helperCacheDirName)
                if not self.helperCache: raise
                histoHelperCacheDirName = os.path.join(cacheDir, self.name+"_histo")
                self.histoHelperCache = MergingDirDB(histoHelperCacheDirName)
                if not self.histoHelperCache: raise
                tfCacheDirName = os.path.join(cacheDir, self.name+"_tf")
                self.tfCache = MergingDirDB(tfCacheDirName)
                if not self.tfCache: raise
            else:
                self.helperCache=None
                self.tfCache=None

        else:
            self.cache=None
            self.helperCache=None
            self.tfCache=None

    # For the datadriven subclasses which often need the same getYieldFromDraw we write those yields to a cache
    def yieldFromCache(self, setup, process, c, selectionString, weightString, overwrite=False):
        s = (process, c, selectionString, weightString)
        if self.helperCache and self.helperCache.contains(s) and not overwrite:
            return self.helperCache.get(s)
        else:
            yieldFromDraw = u_float(**setup.processes[process].getYieldFromDraw(selectionString, weightString))
            if self.helperCache: self.helperCache.add(s, yieldFromDraw, overwrite=True)
            return yieldFromDraw

    # For the datadriven subclasses which often need the same mT histos we write those yields to a cache
    def histoFromCache(self, var, binning, setup, process, c, selectionString, weightString, overwrite=False):
        s = (var, "_".join(map(str,binning)), process, c, selectionString, weightString)
        if self.histoHelperCache and self.histoHelperCache.contains(s) and not overwrite:
            return self.histoHelperCache.get(s)
        else:
            histo = setup.processes[process].get1DHistoFromDraw( var, binning=binning, selectionString=selectionString, weightString=weightString, addOverFlowBin="upper" )
            if self.histoHelperCache: self.histoHelperCache.add(s, histo, overwrite=True)
            return histo

    def uniqueKey(self, region, channel, setup, signalAddon=None, qcdUpdates={}):
        sysForKey = setup.sys.copy()
        sysForKey["reweight"] = "TEMP"
        reweightKey = '["' + '", "'.join(sorted([i for i in setup.sys['reweight']])) + '"]' # little hack to preserve order of list when being dumped into json
        key = region, channel, json.dumps(sysForKey, sort_keys=True).replace('"TEMP"',reweightKey), json.dumps(setup.parameters, sort_keys=True), json.dumps(setup.lumi, sort_keys=True)
        if qcdUpdates:  key += tuple(json.dumps(qcdUpdates, sort_keys=True))
        if signalAddon: key += tuple(signalAddon)
        return key

    def replace(self, i, r):
        try:
          if i.count("reweight"): return i.replace(r[0], r[1])
          else:                   return i
        except:                   return i

    def cachedEstimate(self, region, channel, setup, signalAddon=None, save=True, overwrite=False, checkOnly=False):
        key =  self.uniqueKey(region, channel, setup, signalAddon=signalAddon)
        if (self.cache and self.cache.contains(key)) and not overwrite:
            res = self.cache.get(key)
            logger.debug( "Loading cached %s result for %r : %r"%(self.name, key, res) )
        elif self.cache and not checkOnly:
            logger.debug( "Calculating %s result for %r"%(self.name, key) )
            res = self._estimate( region, channel, setup, signalAddon=signalAddon, overwrite=overwrite )
            _res = self.cache.add( key, res, overwrite=True )
            logger.debug( "Adding cached %s result for %r : %r" %(self.name, key, res) )
        elif not checkOnly:
            res = self._estimate( region, channel, setup, signalAddon=signalAddon, overwrite=overwrite)
        else:
            res = u_float(-1,0)
        return res if res > 0 or checkOnly else u_float(0,0)

    def cachedTransferFactor(self, channel, setup, qcdUpdates=None, save=True, overwrite=False, checkOnly=False):
        key =  self.uniqueKey("region", channel, setup, qcdUpdates=qcdUpdates)
        if (self.tfCache and self.tfCache.contains(key)) and not overwrite:
            res = self.tfCache.get(key)
            logger.debug( "Loading cached %s result for %r : %r"%(self.name, key, res) )
        elif self.tfCache and not checkOnly:
            logger.debug( "Calculating %s result for %r"%(self.name, key) )
#            res = self._dataDrivenTransferFactor( channel, setup, qcdUpdates=qcdUpdates, overwrite=overwrite )
            res = self._fittedTransferFactor( channel, setup, qcdUpdates=qcdUpdates, overwrite=overwrite )
            _res = self.tfCache.add( key, res, overwrite=True )
            logger.debug( "Adding cached transfer factor for %r : %r" %(key, res) )
        elif not checkOnly:
#            res = self._dataDrivenTransferFactor( channel, setup, qcdUpdates=qcdUpdates, overwrite=overwrite )
            res = self._fittedTransferFactor( channel, setup, qcdUpdates=qcdUpdates, overwrite=overwrite )
        else:
            res = u_float(-1,0)
        return res if res > 0 or checkOnly else u_float(0,0)


    @abc.abstractmethod
    def _estimate(self, region, channel, setup, signalAddon=None, overwrite=False):
        """Estimate yield in "region" using setup"""
        return

    def _transferFactor(self, channel, setup, overwrite=False):
        """Estimate transfer factor for QCD in "region" using setup"""
        return

    def _dataDrivenTransferFactor(self, channel, setup, qcdUpdates=None, overwrite=False):
        """Estimate transfer factor for QCD in "region" using setup"""
        return

    def _fittedTransferFactor(self, channel, setup, qcdUpdates=None, overwrite=False):
        """Estimate transfer factor for QCD in "region" using setup"""
        return

    def TransferFactorStatistic(self, region, channel, setup):
        ref  = self.cachedTransferFactor(channel, setup)
        up   = u_float(ref.val + ref.sigma)
        down = u_float(ref.val - ref.sigma)
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up,down)

    def TuneSystematic(self, region, channel, setup):
        up   = self.cachedEstimate(region, channel, setup, signalAddon="TuneUp")
        down = self.cachedEstimate(region, channel, setup, signalAddon="TuneDown")
        ref  = self.cachedEstimate(region, channel, setup)
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up,down)

    def ErdOnSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup)
        up   = self.cachedEstimate(region, channel, setup, signalAddon="erdOn")
        return abs((up-ref)/ref) if ref > 0 else up

    def PUSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup)
        up   = self.cachedEstimate(region, channel, setup.sysClone({"reweight":["reweightPUUp"]}))
        down = self.cachedEstimate(region, channel, setup.sysClone({"reweight":["reweightPUDown"]}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up,down)

    def JERSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup)
        up   = self.cachedEstimate(region, channel, setup.sysClone({"selectionModifier":"jerUp"}))
        down = self.cachedEstimate(region, channel, setup.sysClone({"selectionModifier":"jerDown"}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)

    def JECSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup)
        up   = self.cachedEstimate(region, channel, setup.sysClone({"selectionModifier":"jesTotalUp"}))
        down = self.cachedEstimate(region, channel, setup.sysClone({"selectionModifier":"jesTotalDown"}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)

    def unclusteredSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup)
        up   = self.cachedEstimate(region, channel, setup.sysClone({"selectionModifier":"unclustEnUp"}))
        down = self.cachedEstimate(region, channel, setup.sysClone({"selectionModifier":"unclustEnDown"}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)

    def L1PrefireSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup)
        up   = self.cachedEstimate(region, channel, setup.sysClone({"reweight":["reweightL1PrefireUp"]}))
        down = self.cachedEstimate(region, channel, setup.sysClone({"reweight":["reweightL1PrefireDown"]}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)
    
    def btaggingSFbSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup)
        up   = self.cachedEstimate(region, channel, setup.sysClone({"reweight":["reweightBTag_SF_b_Up"]}))
        down = self.cachedEstimate(region, channel, setup.sysClone({"reweight":["reweightBTag_SF_b_Down"]}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)

    def btaggingSFlSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup)
        up   = self.cachedEstimate(region, channel, setup.sysClone({"reweight":["reweightBTag_SF_l_Up"]}))
        down = self.cachedEstimate(region, channel, setup.sysClone({"reweight":["reweightBTag_SF_l_Down"]}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)

    def leptonSFSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup)
        up   = self.cachedEstimate(region, channel, setup.sysClone({"reweight":["reweightLeptonTightSFUp"]}))
        down = self.cachedEstimate(region, channel, setup.sysClone({"reweight":["reweightLeptonTightSFDown"]}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)

    def leptonTrackingSFSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup)
        up   = self.cachedEstimate(region, channel, setup.sysClone({"reweight":["reweightLeptonTrackingTightSFUp"]}))
        down = self.cachedEstimate(region, channel, setup.sysClone({"reweight":["reweightLeptonTrackingTightSFDown"]}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)

    def photonSFSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup)
        up   = self.cachedEstimate(region, channel, setup.sysClone({"reweight":["reweightPhotonSFUp"]}))
        down = self.cachedEstimate(region, channel, setup.sysClone({"reweight":["reweightPhotonSFDown"]}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)

    def photonElectronVetoSFSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup)
        up   = self.cachedEstimate(region, channel, setup.sysClone({"reweight":["reweightPhotonElectronVetoSFUp"]}))
        down = self.cachedEstimate(region, channel, setup.sysClone({"reweight":["reweightPhotonElectronVetoSFDown"]}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)

#    def triggerSystematic(self, region, channel, setup):
#        ref  = self.cachedEstimate(region, channel, setup)
#        up   = self.cachedEstimate(region, channel, setup.sysClone({"reweight":["reweightDilepTriggerUp"]}))
#        down = self.cachedEstimate(region, channel, setup.sysClone({"reweight":["reweightDilepTriggerDown"]}))
#        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)

    def getBkgSysJobs(self, region, channel, setup):
        l = [
            (region, channel, setup.sysClone({"reweight":["reweightPUUp"]}), None),
            (region, channel, setup.sysClone({"reweight":["reweightPUDown"]}), None),

            (region, channel, setup.sysClone({"selectionModifier":"jerUp"}), None),
            (region, channel, setup.sysClone({"selectionModifier":"jerDown"}), None),

            (region, channel, setup.sysClone({"selectionModifier":"jesTotalUp"}), None),
            (region, channel, setup.sysClone({"selectionModifier":"jesTotalDown"}), None),

#            (region, channel, setup.sysClone({"selectionModifier":"unclustEnUp"}), None),
#            (region, channel, setup.sysClone({"selectionModifier":"unclustEnDown"}), None),

            (region, channel, setup.sysClone({"reweight":["reweightL1PrefireUp"]}), None),
            (region, channel, setup.sysClone({"reweight":["reweightL1PrefireDown"]}), None),

            (region, channel, setup.sysClone({"reweight":["reweightBTag_SF_b_Up"]}), None),
            (region, channel, setup.sysClone({"reweight":["reweightBTag_SF_b_Down"]}), None),
            (region, channel, setup.sysClone({"reweight":["reweightBTag_SF_l_Up"]}), None),
            (region, channel, setup.sysClone({"reweight":["reweightBTag_SF_l_Down"]}), None),

            (region, channel, setup.sysClone({"reweight":["reweightLeptonTightSFUp"]}), None),
            (region, channel, setup.sysClone({"reweight":["reweightLeptonTightSFDown"]}), None),

            (region, channel, setup.sysClone({"reweight":["reweightLeptonTrackingTightSFUp"]}), None),
            (region, channel, setup.sysClone({"reweight":["reweightLeptonTrackingTightSFDown"]}), None),

            (region, channel, setup.sysClone({"reweight":["reweightPhotonSFUp"]}), None),
            (region, channel, setup.sysClone({"reweight":["reweightPhotonSFDown"]}), None),

            (region, channel, setup.sysClone({"reweight":["reweightPhotonElectronVetoSFUp"]}), None),
            (region, channel, setup.sysClone({"reweight":["reweightPhotonElectronVetoSFDown"]}), None),

#            (region, channel, setup.sysClone({"reweight":["reweightDilepTriggerUp"]}), None),
#            (region, channel, setup.sysClone({"reweight":["reweightDilepTriggerDown"]}), None),
        ]
        return l

    def getSigSysJobs(self, region, channel, setup):
        # in case there is a difference, enter it here (originally for fastSim)
        l  = self.getBkgSysJobs(region = region, channel = channel, setup = setup)
        l += [
            (region, channel, setup, "TuneUp"),
            (region, channel, setup, "TuneDown"),
            (region, channel, setup, "erdOn"),
        ]
        return l

    def getTexName(self, channel, rootTex=True):
        try:
          name = self.texName
        except:
          try:
            name = self.process[channel].texName
          except:
            try:
              texNames = [self.process[c].texName for c in allChannels]                # If all, only take texName if it is the same for all lepChannels
              if texNames.count(texNames[0]) == len(texNames):
                name = texNames[0]
              else:
                name = self.name
            except:
              name = self.name
        if not rootTex: name = "$" + name.replace("#","\\") + "$" # Make it tex format
        return name
