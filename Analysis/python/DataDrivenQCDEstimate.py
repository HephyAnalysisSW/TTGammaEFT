import os, sys
from math import sqrt

from TTGammaEFT.Analysis.SystematicEstimator import SystematicEstimator
from TTGammaEFT.Analysis.SetupHelpers        import *
from TTGammaEFT.Tools.user                   import analysis_results, cache_directory

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

# apply EWK SF for QCD estimation, global flag
try:    addSF = sys.modules['__main__'].addSF == "True"
except: addSF = False
logger.info("Adding scale factors is set to %s"%str(addSF))

class DataDrivenQCDEstimate(SystematicEstimator):
    def __init__(self, name, cacheDir=None):
        super(DataDrivenQCDEstimate, self).__init__(name, cacheDir=cacheDir)

    def _transferFactor(self, region, channel, setup, overwrite=False):

        logger.info( "Calculating QCD transfer factor" )

        selection_MC_SR   = setup.selection("MC",   channel=channel, **setup.defaultParameters())
        selection_MC_CR   = setup.selection("MC",   channel=channel, **setup.defaultParameters( update=QCD_updates ))
        regionCutMod_SR   = region.cutString(setup.sys["selectionModifier"])
        regionCutMod_CR   = region.cutString(setup.sys["selectionModifier"])

        # change region cuts for inverted leptons
        for cut, invCut in QCD_cutReplacements.iteritems():
            regionCutMod_CR = regionCutMod_CR.replace( cut, invCut )
            logger.info( "Changing region cut %s to %s"%(cut, invCut) )

        logger.info( "Using CR region cut %s"%(regionCutMod_CR) )
        logger.info( "Using SR region cut %s"%(regionCutMod_SR) )

        cuts_MC_SR = [ regionCutMod_SR, selection_MC_SR["cut"] ]
        if self.processCut:
            cuts_MC_SR.append( self.processCut )
            logger.info( "Adding process specific cut %s"%self.processCut )
        cut_MC_SR = "&&".join( cuts_MC_SR )


        weight_MC    = selection_MC_SR["weightStr"] # w/o misID SF

        # QCD CR with 0 bjets and inverted lepton isolation +  SF for DY and MisIDSF
        # Attention: change region.cutstring to invLepIso and nBTag0 if there are leptons or btags in regions!!!
        cut_MC_CR    = "&&".join([ regionCutMod_CR, selection_MC_CR["cut"] ])

        # The QCD yield in the CR with SR weight (sic)
        yield_QCD_CR     = self.yieldFromCache(setup, "QCD",    channel, cut_MC_CR,   weight_MC,   overwrite=overwrite)*setup.dataLumi/1000.
        yield_QCD_CR    += self.yieldFromCache(setup, "GJets",  channel, cut_MC_CR,   weight_MC,   overwrite=overwrite)*setup.dataLumi/1000.

        # The QCD yield in the signal regions
        yield_QCD_SR     = self.yieldFromCache(setup, "QCD",    channel, cut_MC_SR,   weight_MC,  overwrite=overwrite)*setup.lumi/1000.
        yield_QCD_SR    += self.yieldFromCache(setup, "GJets",  channel, cut_MC_SR,   weight_MC,  overwrite=overwrite)*setup.lumi/1000.

        transferFac = yield_QCD_SR/yield_QCD_CR if yield_QCD_CR > 0 else u_float(0, 0)

        logger.info("yield QCD + GJets CR:         " + str(yield_QCD_CR))
        logger.info("yield QCD + GJets SR:         " + str(yield_QCD_SR))
        logger.info("transfer factor:              " + str(transferFac))

        return transferFac



    def _dataDrivenTransferFactor(self, region, channel, setup, overwrite=False):

        logger.info( "Calculating data-driven QCD transfer factor" )

        selection_MC_CR   = setup.selection("MC",   channel=channel, **setup.defaultParameters( update=QCDTF_updates["CR"] ))
        selection_Data_CR = setup.selection("Data", channel=channel, **setup.defaultParameters( update=QCDTF_updates["CR"] ))
        selection_MC_SR   = setup.selection("MC",   channel=channel, **setup.defaultParameters( update=QCDTF_updates["SR"] ))
        selection_Data_SR = setup.selection("Data", channel=channel, **setup.defaultParameters( update=QCDTF_updates["SR"] ))

        weight_MC_CR      = selection_MC_CR["weightStr"] # w/ misID SF
        weight_Data_CR    = selection_Data_CR["weightStr"]
        weight_MC_SR      = selection_MC_SR["weightStr"] # w/ misID SF
        weight_Data_SR    = selection_Data_SR["weightStr"]

        regionCutMod_CR   = region.cutString(setup.sys["selectionModifier"]) # MC
        regionCut_CR      = region.cutString() # Data
        regionCutMod_SR   = region.cutString(setup.sys["selectionModifier"]) # MC
        regionCut_SR      = region.cutString() # Data

        logger.info( "Using QCD TF CR weightstring MC %s"%(weight_MC_CR) )
        logger.info( "Using QCD TF CR weightstring Data %s"%(weight_Data_CR) )
        logger.info( "Using QCD TF SR weightstring MC %s"%(weight_MC_SR) )
        logger.info( "Using QCD TF SR weightstring Data %s"%(weight_Data_SR) )

        # change region cuts for inverted leptons
        for cut, invCut in QCD_cutReplacements.iteritems():
            regionCutMod_CR = regionCutMod_CR.replace( cut, invCut )
            regionCut_CR    = regionCut_CR.replace(    cut, invCut )
            logger.info( "Changing region cut %s to %s"%(cut, invCut) )

        logger.info( "Using QCD TF CR MC region cut %s"%(regionCutMod_CR) )
        logger.info( "Using QCD TF CR Data region cut %s"%(regionCut_CR) )
        logger.info( "Using QCD TF SR MC region cut %s"%(regionCutMod_SR) )
        logger.info( "Using QCD TF SR Data region cut %s"%(regionCut_SR) )

        # QCD CR with 0 bjets and inverted lepton isolation +  SF for DY and MisIDSF
        # Attention: change region.cutstring to invLepIso and nBTag0 if there are leptons or btags in regions!!!
        cut_MC_CR    = "&&".join([ regionCutMod_CR, selection_MC_CR["cut"]   ])
        cut_Data_CR  = "&&".join([ regionCut_CR,    selection_Data_CR["cut"] ])
        cut_MC_SR    = "&&".join([ regionCutMod_SR, selection_MC_SR["cut"]   ])
        cut_Data_SR  = "&&".join([ regionCut_SR,    selection_Data_SR["cut"] ])

        logger.info( "Using QCD TF CR MC total cut %s"%(cut_MC_CR) )
        logger.info( "Using QCD TF CR Data total cut %s"%(cut_Data_CR) )
        logger.info( "Using QCD TF SR MC total cut %s"%(cut_MC_SR) )
        logger.info( "Using QCD TF SR Data total cut %s"%(cut_Data_SR) )

        # Calculate yields for Data
        yield_data_CR  = self.yieldFromCache(setup, "Data", channel, cut_Data_CR, weight_Data_CR, overwrite=overwrite)
        yield_data_SR  = self.yieldFromCache(setup, "Data", channel, cut_Data_SR, weight_Data_SR, overwrite=overwrite)

        # Calculate yields for MC (normalized to data lumi)
        yield_other_CR = 0
        yield_other_SR = 0
        for s in default_sampleList:
            if s in ["QCD-DD", "QCD", "GJets", "Data"]: continue
            y_CR = self.yieldFromCache( setup, s, channel, cut_MC_CR, weight_MC_CR, overwrite=overwrite )
            y_SR = self.yieldFromCache( setup, s, channel, cut_MC_SR, weight_MC_SR, overwrite=overwrite )
            print "without SF", s, "CR", y_CR*setup.dataLumi/1000., "SR", y_SR*setup.dataLumi/1000.
            if addSF:
                if s == "DY_LO":
                    y_CR *= DYSF_val[setup.year] #add DY SF
                    y_SR *= DYSF_val[setup.year] #add DY SF
                elif s == "WJets":
                    y_CR *= WJetsSF_val[setup.year] #add WJets SF
                    y_SR *= WJetsSF_val[setup.year] #add WJets SF
                elif s == "TT_pow":
                    y_CR *= TTSF_val[setup.year] #add TT SF
                    y_SR *= TTSF_val[setup.year] #add TT SF
                elif s == "ZG":
                    y_CR *= ZGSF_val[setup.year] #add ZGamma SF
                    y_SR *= ZGSF_val[setup.year] #add ZGamma SF
                elif s == "WG":
                    y_CR *= WGSF_val[setup.year] #add WGamma SF
                    y_SR *= WGSF_val[setup.year] #add WGamma SF
            print "with SF", s, "CR", y_CR*setup.dataLumi/1000., "SR", y_SR*setup.dataLumi/1000.
            yield_other_CR += y_CR
            yield_other_SR += y_SR

        yield_other_CR *= setup.dataLumi/1000.
        yield_other_SR *= setup.dataLumi/1000.

        qcd_est_CR = yield_data_CR - yield_other_CR
        qcd_est_SR = yield_data_SR - yield_other_SR

        transferFac = qcd_est_SR/qcd_est_CR if qcd_est_CR > 0 else u_float(0, 0)

        logger.info("Calculating data-driven QCD TF normalization in channel " + channel + " using lumi " + str(setup.dataLumi) + ":")
        logger.info("TF CR yield data:                " + str(yield_data_CR))
        logger.info("TF CR yield other:               " + str(yield_other_CR))
        logger.info("TF CR yield (data-other):        " + str(qcd_est_CR))
        logger.info("TF SR yield data:                " + str(yield_data_SR))
        logger.info("TF SR yield other:               " + str(yield_other_SR))
        logger.info("TF SR yield (data-other):        " + str(qcd_est_SR))
        logger.info("transfer factor:                 " + str(transferFac))

        if qcd_est_CR < 0 and yield_data_CR > 0:
            logger.warning("Negative QCD TF CR estimate yield!")
            return u_float(0, 0)

        if qcd_est_SR < 0 and yield_data_SR > 0:
            logger.warning("Negative QCD TF SR estimate yield!")
            return u_float(0, 0)

        return transferFac if transferFac > 0 else u_float(0, 0)

    #Concrete implementation of abstract method "estimate" as defined in Systematic
    def _estimate(self, region, channel, setup, overwrite=False):

        #Sum of all channels for "all"
        if channel=="all":
            estimate     = sum([ self.cachedEstimate(region, c, setup) for c in lepChannels])

        elif channel=="SFtight":
            estimate     = sum([ self.cachedEstimate(region, c, setup) for c in dilepChannels])

        else:

            logger.info( "Calculating QCD estimate" )
            # Skip QCD estimate for 2 lepton CR (QCD = 0)
            if channel in dilepChannels:
                logger.info("Estimate for QCD in dileptonic channels skipped: 0")
                return u_float(0, 0)

            transferFac   = self.cachedTransferFactor(region, channel, setup, save=True, overwrite=overwrite, checkOnly=False)

            if transferFac == 0:
                logger.info("Transfer factor is 0. Skipping QCD estimate calculation and settting it to 0!")
                return u_float(1, 1)

            selection_MC_CR   = setup.selection("MC",   channel=channel, **setup.defaultParameters( update=QCD_updates ))
            selection_Data_CR = setup.selection("Data", channel=channel, **setup.defaultParameters( update=QCD_updates ))

            weight_Data_CR    = selection_Data_CR["weightStr"]
            weight_MC_CR      = selection_MC_CR["weightStr"] # w/ misID SF

            regionCutMod_CR   = region.cutString(setup.sys["selectionModifier"])
            regionCut_CR      = region.cutString()

            # change region cuts for inverted leptons
            for cut, invCut in QCD_cutReplacements.iteritems():
                regionCutMod_CR = regionCutMod_CR.replace( cut, invCut )
                regionCut_CR    = regionCut_CR.replace(    cut, invCut )
                logger.info( "Changing region cut %s to %s"%(cut, invCut) )

            logger.info( "Using CR MC region cut %s"%(regionCutMod_CR) )
            logger.info( "Using CR Data region cut %s"%(regionCut_CR) )

            # QCD CR with 0 bjets and inverted lepton isolation +  SF for DY and MisIDSF
            # Attention: change region.cutstring to invLepIso and nBTag0 if there are leptons or btags in regions!!!
            cut_MC_CR    = "&&".join([ regionCutMod_CR, selection_MC_CR["cut"]   ])
            cut_Data_CR  = "&&".join([ regionCut_CR,    selection_Data_CR["cut"] ])

            logger.info( "Using CR MC total cut %s"%(cut_MC_CR) )
            logger.info( "Using CR Data total cut %s"%(cut_Data_CR) )

            # Calculate yields for CR (normalized to data lumi)
            yield_data    = self.yieldFromCache(setup, "Data",   channel, cut_Data_CR, weight_Data_CR, overwrite=overwrite)

            yield_other = 0
            for s in default_sampleList:
                if s in ["QCD-DD", "QCD", "GJets", "Data"]: continue
                y = self.yieldFromCache( setup, s, channel, cut_MC_CR, weight_MC_CR, overwrite=overwrite )
                if addSF:
                    if   s == "DY_LO":  y *= DYSF_val[setup.year]    #add DY SF
                    elif s == "WJets":  y *= WJetsSF_val[setup.year] #add WJets SF
                    elif s == "TT_pow": y *= TTSF_val[setup.year]    #add TT SF
                    elif s == "ZG":     y *= ZGSF_val[setup.year]    #add ZGamma SF
                    elif s == "WG":     y *= WGSF_val[setup.year]    #add WGamma SF
                yield_other += y

            yield_other *= setup.dataLumi/1000.

            normRegYield  = yield_data - yield_other
            estimate      = normRegYield*transferFac

            logger.info("Calculating data-driven QCD normalization in channel " + channel + " using lumi " + str(setup.dataLumi) + ":")
            logger.info("yield data:                " + str(yield_data))
            logger.info("yield other:               " + str(yield_other))
            logger.info("yield (data-other):        " + str(normRegYield))
            logger.info("transfer factor:           " + str(transferFac))

            if normRegYield < 0 and yield_data > 0:
                logger.warning("Negative normalization region yield!")

        logger.info("Estimate for QCD in " + channel + " channel" + (" (lumi=" + str(setup.lumi) + "/pb)" if channel != "all" else "") + ": " + str(estimate) + (" (negative estimated being replaced by 0)" if estimate < 0 else ""))
        return estimate if estimate > 0 else u_float(1, 1)

if __name__ == "__main__":
    from TTGammaEFT.Analysis.regions      import regionsTTG, noPhotonRegionTTG, inclRegionsTTG
    from TTGammaEFT.Analysis.SetupHelpers import allRegions
    from TTGammaEFT.Analysis.Setup        import Setup

    overwrite = True
    print "incl"

    setup = Setup(year=2016, photonSelection=False)
    setup = setup.sysClone(parameters=allRegions["VG3"]["parameters"])

    estimate = DataDrivenQCDEstimate( "QCD-DD" )    
    estimate.initCache(setup.defaultCacheDir())

    r = allRegions["VG3"]["inclRegion"][0]
    print "e", "dd",       estimate._dataDrivenTransferFactor( r, "e", setup, overwrite=overwrite )
#    print "e", "classic",  estimate._transferFactor( r, "e", setup, overwrite=overwrite )
#    print "mu", "dd",      estimate._dataDrivenTransferFactor( r, "mu", setup, overwrite=overwrite )
#    print "mu", "classic", estimate._transferFactor( r, "mu", setup, overwrite=overwrite )

    exit()

    print "lowPT"
    r = allRegions["VG3"]["regions"][0]

    setup = Setup(year=2016, photonSelection=True)
    setup = setup.sysClone(parameters=allRegions["VG3"]["parameters"])

    estimate = DataDrivenQCDEstimate( "QCD-DD" )    
    estimate.initCache(setup.defaultCacheDir())

    res = estimate._estimate( r, "e", setup, overwrite=overwrite )
    print res



    print "medPT"
    r = allRegions["VG3"]["regions"][1]

    setup = Setup(year=2016, photonSelection=True)
    setup = setup.sysClone(parameters=allRegions["VG3"]["parameters"])

    estimate = DataDrivenQCDEstimate( "QCD-DD" )    
    estimate.initCache(setup.defaultCacheDir())

    print setup.defaultParameters()
    res = estimate._estimate( r, "e", setup, overwrite=overwrite )
    print res


    print "highPT"
    r = allRegions["VG3"]["regions"][2]

    setup = Setup(year=2016, photonSelection=True)
    setup = setup.sysClone(parameters=allRegions["VG3"]["parameters"])

    estimate = DataDrivenQCDEstimate( "QCD-DD" )    
    estimate.initCache(setup.defaultCacheDir())

    print setup.defaultParameters()
    res = estimate._estimate( r, "e", setup, overwrite=overwrite )
    print res
