import os, sys
import ROOT
ROOT.gROOT.SetBatch(True)
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
except: addSF = True
logger.info("Adding scale factors is set to %s"%str(addSF))

class DataDrivenQCDEstimate(SystematicEstimator):
    def __init__(self, name, cacheDir=None):
        super(DataDrivenQCDEstimate, self).__init__(name, cacheDir=cacheDir)

#    def _transferFactor(self, region, channel, setup, overwrite=False):
    def _transferFactor(self, channel, setup, qcdUpdates=None, overwrite=False):

        logger.info( "Calculating QCD transfer factor" )

        selection_MC_SR = setup.selection("MC",   channel=channel, **setup.defaultParameters())
        selection_MC_CR = setup.selection("MC",   channel=channel, **setup.defaultParameters( update=qcdUpdates if qcdUpdates else QCD_updates ))

        # currently we don't need a region dependence of the TF, if you do, uncomment here

#        # remove specific region cuts for TF
#        regionCut_CR    = region.cutString()
#        for cut in QCDTF_regionCutRemovals:
#            if not cut in regionCut_CR: continue
#            regionCut_CR = "&&".join( [ subCut for subCut in regionCut_CR.split("&&") if not cut in subCut ] )
#            print( "Removing region cut containing %s"%(cut) )
#            if not regionCut_CR:
#                regionCut_CR = "(1)"
#                break
#
#        regionCut_SR = copy.copy(regionCut_CR)
#
#        # change region cuts for inverted leptons
#        for cut, invCut in QCD_cutReplacements.iteritems():
#            regionCut_CR = regionCut_CR.replace( cut, invCut )
#            logger.info( "Changing region cut %s to %s"%(cut, invCut) )
#
#        logger.info( "Using CR region cut %s"%(regionCut_CR) )
#        logger.info( "Using SR region cut %s"%(regionCut_SR) )
#
#        cuts_MC_SR = [ regionCut_SR, selection_MC_SR["cut"] ]
#        if self.processCut:
#            cuts_MC_SR.append( self.processCut )
#            logger.info( "Adding process specific cut %s"%self.processCut )
#
#        cut_MC_SR = "&&".join( cuts_MC_SR )
#        # QCD CR with 0 bjets and inverted lepton isolation +  SF for DY and MisIDSF
#        # Attention: change region.cutstring to invLepIso and nBTag0 if there are leptons or btags in regions!!!
#        cut_MC_CR    = "&&".join([ regionCut_CR, selection_MC_CR["cut"] ])

        cut_MC_SR = selection_MC_SR["cut"]
        cut_MC_CR = selection_MC_CR["cut"]

        weight_MC = selection_MC_SR["weightStr"] # w/o misID SF

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



#    def _dataDrivenTransferFactor(self, region, channel, setup, overwrite=False):
    def _dataDrivenTransferFactor(self, channel, setup, qcdUpdates=None, overwrite=False):

        print( "Calculating data-driven QCD transfer factor" )

        selection_MC_CR     = setup.selection("MC",   channel=channel, **setup.defaultParameters( update=qcdUpdates["CR"] if qcdUpdates else QCDTF_updates["CR"] ))
        selection_Data_CR   = setup.selection("Data", channel=channel, **setup.defaultParameters( update=qcdUpdates["CR"] if qcdUpdates else QCDTF_updates["CR"] ))
        selection_MC_SR     = setup.selection("MC",   channel=channel, **setup.defaultParameters( update=qcdUpdates["SR"] if qcdUpdates else QCDTF_updates["SR"] ))
        selection_Data_SR   = setup.selection("Data", channel=channel, **setup.defaultParameters( update=qcdUpdates["SR"] if qcdUpdates else QCDTF_updates["SR"] ))
#        selection_Data_full = setup.selection("Data", channel=channel, **setup.defaultParameters( update=QCDTF_updates["SRDenom"] ))
#        selection_Data_part = setup.selection("Data", channel=channel, **setup.defaultParameters())

        weight_MC_CR      = selection_MC_CR["weightStr"] # w/ misID SF
        weight_Data_CR    = selection_Data_CR["weightStr"]
        weight_MC_SR      = selection_MC_SR["weightStr"] # w/ misID SF
        weight_Data_SR    = selection_Data_SR["weightStr"]

        print( "Using QCD TF CR weightstring MC %s"%(weight_MC_CR) )
        print( "Using QCD TF CR weightstring Data %s"%(weight_Data_CR) )
        print( "Using QCD TF SR weightstring MC %s"%(weight_MC_SR) )
        print( "Using QCD TF SR weightstring Data %s"%(weight_Data_SR) )

        # currently we don't need a region dependence of the TF, if you do, uncomment here

#        regionCut_part = region.cutString()
#        # remove specific region cuts for TF
#        regionCut_CR   = copy.copy(regionCut_part)
#        for cut in QCDTF_regionCutRemovals:
#            if not cut in regionCut_CR: continue
#            regionCut_CR = "&&".join( [ subCut for subCut in regionCut_CR.split("&&") if not cut in subCut ] )
#            print( "Removing region cut containing %s"%(cut) )
#            if not regionCut_CR:
#                regionCut_CR = "(1)"
#                break
#
#        regionCut_SR = copy.copy(regionCut_CR)
#
#        # change region cuts for inverted leptons
#        for cut, invCut in QCD_cutReplacements.iteritems():
#            regionCut_CR = regionCut_CR.replace( cut, invCut )
#            print( "Changing region cut %s to %s"%(cut, invCut) )
#
#        print( "Using QCD TF full region cut %s"%(regionCut_part) )
#        print( "Using QCD TF CR region cut %s"%(regionCut_CR) )
#        print( "Using QCD TF SR region cut %s"%(regionCut_SR) )
#
#        # QCD CR with 0 bjets and inverted lepton isolation +  SF for DY and MisIDSF
#        # Attention: change region.cutstring to invLepIso and nBTag0 if there are leptons or btags in regions!!!
#        cut_MC_CR     = "&&".join([ regionCut_CR,   selection_MC_CR["cut"]   ])
#        cut_Data_CR   = "&&".join([ regionCut_CR,   selection_Data_CR["cut"] ])
#        cut_MC_SR     = "&&".join([ regionCut_SR,   selection_MC_SR["cut"]   ])
#        cut_Data_SR   = "&&".join([ regionCut_SR,   selection_Data_SR["cut"] ])
#        cut_Data_part = "&&".join([ regionCut_part, selection_Data_part["cut"] ])
#        cut_Data_full = "&&".join([ regionCut_SR,   selection_Data_full["cut"] ])

        cut_MC_CR     = selection_MC_CR["cut"]
        cut_Data_CR   = selection_Data_CR["cut"]
        cut_MC_SR     = selection_MC_SR["cut"]
        cut_Data_SR   = selection_Data_SR["cut"]

        print( "Using QCD TF CR MC total cut %s"%(cut_MC_CR) )
        print( "Using QCD TF CR Data total cut %s"%(cut_Data_CR) )
        print( "Using QCD TF SR MC total cut %s"%(cut_MC_SR) )
        print( "Using QCD TF SR Data total cut %s"%(cut_Data_SR) )
#        print( "Using QCD TF SR full total cut %s"%(cut_Data_full) )
#        print( "Using QCD TF SR part total cut %s"%(cut_Data_part) )

        # Calculate yields for Data
        yield_data_SR  = self.yieldFromCache(setup, "Data", channel, cut_Data_SR, weight_Data_SR, overwrite=overwrite)

        if yield_data_SR <= 0:
            logger.warning("SR data yield for QCD TF is 0!")
            return u_float(0, 0)

        yield_data_CR  = self.yieldFromCache(setup, "Data", channel, cut_Data_CR, weight_Data_CR, overwrite=overwrite)

        if yield_data_CR <= 0:
            logger.warning("CR data yield for QCD TF is 0!")
            return u_float(0, 0)

#        # Calculate the fraction of data for the subregion (e.g. slices in M3 or M(l,gamma))
#        yield_data_part = self.yieldFromCache(setup, "Data", channel, cut_Data_part, weight_Data_SR, overwrite=overwrite)
#
#        if yield_data_part <= 0:
#            logger.warning("Fractional data yield for QCD TF is 0!")
#            return u_float(0, 0)
#
#        yield_data_full = self.yieldFromCache(setup, "Data", channel, cut_Data_full, weight_Data_SR, overwrite=overwrite)
#
#        if yield_data_full <= 0:
#            logger.warning("Full data yield for QCD TF is 0!")
#            return u_float(0, 0)

        # Calculate yields for MC (normalized to data lumi)
        yield_other_CR = 0
        yield_other_SR = 0
        for s in default_sampleList:
            if s in ["QCD-DD", "QCD", "GJets", "Data"]: continue
            y_CR = self.yieldFromCache( setup, s, channel, cut_MC_CR, weight_MC_CR, overwrite=overwrite )
            y_SR = self.yieldFromCache( setup, s, channel, cut_MC_SR, weight_MC_SR, overwrite=overwrite )
            print "without SF", s, "CR", y_CR*setup.dataLumi/1000., "SR", y_SR*setup.dataLumi/1000.
            if addSF:
                if "DY_LO" in s:
                    y_CR *= DYSF_val[setup.year] #add DY SF
                    y_SR *= DYSF_val[setup.year] #add DY SF
                elif "WJets" in s:
                    y_CR *= WJetsSF_val[setup.year] #add WJets SF
                    y_SR *= WJetsSF_val[setup.year] #add WJets SF
                elif "TT_pow" in s:
                    y_CR *= TTSF_val[setup.year] #add TT SF
                    y_SR *= TTSF_val[setup.year] #add TT SF
                elif "TTG" in s:
                    y_CR *= SSMSF_val[setup.year] #add TTG SF
                    y_SR *= SSMSF_val[setup.year] #add TTG SF
                elif "ZG" in s:
                    y_CR *= ZGSF_val[setup.year] #add ZGamma SF
                    y_SR *= ZGSF_val[setup.year] #add ZGamma SF
                elif "WG" in s:
                    y_CR *= WGSF_val[setup.year] #add WGamma SF
                    y_SR *= WGSF_val[setup.year] #add WGamma SF
            print "with SF", s, "CR", y_CR*setup.dataLumi/1000., "SR", y_SR*setup.dataLumi/1000.
            yield_other_CR += y_CR
            yield_other_SR += y_SR

        yield_other_CR *= setup.dataLumi/1000.
        yield_other_SR *= setup.dataLumi/1000.

        qcd_est_CR   = yield_data_CR - yield_other_CR
        qcd_est_SR   = yield_data_SR - yield_other_SR
        # TF from full QCD CR to full SR
        transRatio   = qcd_est_SR / qcd_est_CR if qcd_est_CR > 0 else u_float(0, 0)
        # scale the TF for subregions in e.g. m(l,gamma) or m3 (region cuts)
#        fractionalSR = yield_data_part / yield_data_full if yield_data_full > 0 else u_float(0, 0)

        transferFac = transRatio# * fractionalSR

        print("Calculating data-driven QCD TF normalization in channel " + channel + " using lumi " + str(setup.dataLumi) + ":")
        print("TF CR yield data:                " + str(yield_data_CR))
        print("TF CR yield other:               " + str(yield_other_CR))
        print("TF CR yield (data-other):        " + str(qcd_est_CR))
        print("TF SR yield data:                " + str(yield_data_SR))
        print("TF SR yield other:               " + str(yield_other_SR))
        print("TF SR yield (data-other):        " + str(qcd_est_SR))
#        print("TF full region yield (data):     " + str(yield_data_full))
#        print("TF part region yield (data):     " + str(yield_data_part))
#        print("transfer ratio:                  " + str(transRatio))
#        print("transfer scale factor:           " + str(fractionalSR))
        print("transfer factor:                 " + str(transferFac))

        if transferFac <= 0:
            logger.warning("TF is 0!")
            return u_float(0, 0)

        if qcd_est_CR <= 0 and yield_data_CR > 0:
            logger.warning("Negative QCD TF CR estimate yield!")
            return u_float(0, 0)

        if qcd_est_SR <= 0 and yield_data_SR > 0:
            logger.warning("Negative QCD TF SR estimate yield!")
            return u_float(0, 0)

        return transferFac if transferFac > 0 else u_float(0, 0)

    def _fittedTransferFactor(self, channel, setup, qcdUpdates=None, overwrite=False):

        print( "Calculating data-driven QCD transfer factor" )

        selection_MC_CR     = setup.selection("MC",   channel=channel, **setup.defaultParameters( update=qcdUpdates["CR"] if qcdUpdates else QCDTF_updates["CR"] ))
        selection_Data_CR   = setup.selection("Data", channel=channel, **setup.defaultParameters( update=qcdUpdates["CR"] if qcdUpdates else QCDTF_updates["CR"] ))
        selection_MC_SR     = setup.selection("MC",   channel=channel, **setup.defaultParameters( update=qcdUpdates["SR"] if qcdUpdates else QCDTF_updates["SR"] ))
        selection_Data_SR   = setup.selection("Data", channel=channel, **setup.defaultParameters( update=qcdUpdates["SR"] if qcdUpdates else QCDTF_updates["SR"] ))

        weight_MC_CR      = selection_MC_CR["weightStr"] # w/ misID SF
        weight_Data_CR    = selection_Data_CR["weightStr"]
        weight_MC_SR      = selection_MC_SR["weightStr"] # w/ misID SF
        weight_Data_SR    = selection_Data_SR["weightStr"]

        print( "Using QCD TF CR weightstring MC %s"%(weight_MC_CR) )
        print( "Using QCD TF CR weightstring Data %s"%(weight_Data_CR) )
        print( "Using QCD TF SR weightstring MC %s"%(weight_MC_SR) )
        print( "Using QCD TF SR weightstring Data %s"%(weight_Data_SR) )

        cut_MC_CR     = selection_MC_CR["cut"]
        cut_Data_CR   = selection_Data_CR["cut"]
        cut_MC_SR     = selection_MC_SR["cut"]
        cut_Data_SR   = selection_Data_SR["cut"]

        print( "Using QCD TF CR MC total cut %s"%(cut_MC_CR) )
        print( "Using QCD TF CR Data total cut %s"%(cut_Data_CR) )
        print( "Using QCD TF SR MC total cut %s"%(cut_MC_SR) )
        print( "Using QCD TF SR Data total cut %s"%(cut_Data_SR) )

        # deside which sample should be free floating
        photonRegion = setup.parameters["nPhoton"][0] > 0
        bjetRegion   = setup.parameters["nBTag"][0] > 0
        if       photonRegion and not bjetRegion: floatSample = "WG"
        elif     photonRegion and     bjetRegion: floatSample = "TT_pow" #"TTG"?
        elif not photonRegion and not bjetRegion: floatSample = "WJets"
        elif not photonRegion and     bjetRegion: floatSample = "TT_pow"

        print( "Leaving sample %s floating in the fit"%(floatSample) )

        binning = [ 20, 0, 200 ]
        print( "Getting mT histograms with binning %s"%(" ".join(map(str,binning))) )

        # get mT histos
        dataHist  = self.histoFromCache( "mT",    binning, setup, "Data", channel, cut_Data_SR, weight_Data_SR, overwrite=overwrite)
        # safe some memory, you don't need the CR data hist, only for estimating the qcd hist
        qcdHist   = self.histoFromCache( "mTinv", binning, setup, "Data", channel, cut_Data_CR, weight_Data_CR, overwrite=overwrite)
        fixedHist = dataHist.Clone("fixed") # sum of contributions that stay fixed
        fixedHist.Scale(0.)

        # Calculate mTs for MC (normalized to data lumi)
        for s in default_sampleList:
            if s in ["QCD-DD", "QCD", "GJets", "Data"]: continue
            tmp_SR = self.histoFromCache( "mT",    binning, setup, s, channel, cut_MC_SR, weight_MC_SR, overwrite=overwrite )
            tmp_CR = self.histoFromCache( "mTinv", binning, setup, s, channel, cut_MC_CR, weight_MC_CR, overwrite=overwrite )
            # apply SF after histo caching
            if addSF:
                if "DY" in s:
                    tmp_SR.Scale(DYSF_val[setup.year].val)
                    tmp_CR.Scale(DYSF_val[setup.year].val)
                elif "WJets" in s:
                    tmp_SR.Scale(WJetsSF_val[setup.year].val)
                    tmp_CR.Scale(WJetsSF_val[setup.year].val)
                elif "TT_pow" in s:
                    tmp_SR.Scale(TTSF_val[setup.year].val)
                    tmp_CR.Scale(TTSF_val[setup.year].val)
                elif "ZG" in s:
                    tmp_SR.Scale(ZGSF_val[setup.year].val)
                    tmp_CR.Scale(ZGSF_val[setup.year].val)
                elif "WG" in s:
                    tmp_SR.Scale(WGSF_val[setup.year].val)
                    tmp_CR.Scale(WGSF_val[setup.year].val)
                elif "TTG" in s:
                    tmp_SR.Scale(SSMSF_val[setup.year].val)
                    tmp_CR.Scale(SSMSF_val[setup.year].val)

            tmp_SR.Scale( setup.dataLumi/1000. )
            tmp_CR.Scale( setup.dataLumi/1000. )

            qcdHist.Add( tmp_CR, -1 )
            if s == floatSample: floatHist = tmp_SR.Clone("float")
            else:                fixedHist.Add( tmp_SR )

            del tmp_SR
            del tmp_CR

        # remove negative bins
        for i in range(qcdHist.GetNbinsX()):
            if qcdHist.GetBinContent(i+1) < 0: qcdHist.SetBinContent(i+1, 0)

        # all histos prepared, now prepare the fit
        tarray = ROOT.TObjArray(3)
        tarray.Add( qcdHist )
        tarray.Add( floatHist )
        tarray.Add( fixedHist )

        fitter = ROOT.TFractionFitter( dataHist, tarray )

        # it is a FRACTION fitter, so the range is the fraction of the data hist
        nTotal      = dataHist.Integral()
        nFloatScale = floatHist.Integral() / nTotal
        nFixedScale = fixedHist.Integral() / nTotal
        nQCDScale   = qcdHist.Integral()   / nTotal

        tfitter = fitter.GetFitter()
        tfitter.Config().ParSettings(0).Set("qcd",   nQCDScale*0.4, 0.001, 0.,               1.)
        tfitter.Config().ParSettings(1).Set("float", nFloatScale,   0.001, 0.,               1.)
        tfitter.Config().ParSettings(2).Set("fixed", nFixedScale,   0.0,   nFixedScale*0.99, nFixedScale*1.01)
        tfitter.Config().ParSettings(2).Fix()
        # fix WGamma in photonRegions e-channel since mT is not a good handle
        if photonRegion and not bjetRegion and channel == "e": # cant make it fixed, as the nDOF is not matching, no clue how to change that, nice workaround
            tfitter.Config().ParSettings(1).Set("float", nFloatScale, 0.001, nFloatScale*0.99, nFloatScale*1.01)

        print("Performing Fit!")
        status = fitter.Fit()           # perform the fit
        print("Fit performed: status = %i"%status)

        qcdTFVal,   qcdTFErr   = ROOT.Double(0), ROOT.Double(0)
        floatSFVal, floatSFErr = ROOT.Double(0), ROOT.Double(0)

        fitter.GetResult( 0, qcdTFVal,   qcdTFErr )
        fitter.GetResult( 1, floatSFVal, floatSFErr )

        del fitter

        transferFac = u_float( qcdTFVal,   qcdTFErr ) / nQCDScale
        floatSF     = u_float( floatSFVal, floatSFErr ) / nFloatScale

        print("Calculating data-driven QCD TF normalization in channel " + channel + " using lumi " + str(setup.dataLumi) + ":")
        print("TF CR yield QCD:                 " + str(nQCDScale*nTotal))
        print("TF SR yield data:                " + str(nTotal))
        print("TF SR yield fixed:               " + str(nFixedScale*nTotal))
        print("TF SR yield float:               " + str(nFloatScale*nTotal))
        print("transfer factor:                 " + str(transferFac))
        print(floatSample + " scale factor:     " + str(floatSF))

        return transferFac if transferFac > 0 else u_float(0, 0)


    #Concrete implementation of abstract method "estimate" as defined in Systematic
    def _estimate(self, region, channel, setup, signalAddon=None, overwrite=False):

        #Sum of all channels for "all"
        if channel=="all":
            estimate     = sum([ self.cachedEstimate(region, c, setup, signalAddon=signalAddon) for c in lepChannels])

        elif channel=="SFtight":
            estimate     = sum([ self.cachedEstimate(region, c, setup, signalAddon=signalAddon) for c in dilepChannels])

        else:

            logger.info( "Calculating QCD estimate" )
            # Skip QCD estimate for 2 lepton CR (QCD = 0)
            if channel in dilepChannels:
                logger.info("Estimate for QCD in dileptonic channels skipped: 0")
                return u_float(0, 0)

            selection_MC_CR   = setup.selection("MC",   channel=channel, **setup.defaultParameters( update=QCD_updates ))
            selection_Data_CR = setup.selection("Data", channel=channel, **setup.defaultParameters( update=QCD_updates ))

            weight_Data_CR    = selection_Data_CR["weightStr"]
            weight_MC_CR      = selection_MC_CR["weightStr"] # w/ misID SF

            regionCut_CR      = region.cutString()

            # change region cuts for inverted leptons
            for cut, invCut in QCD_cutReplacements.iteritems():
                regionCut_CR = regionCut_CR.replace( cut, invCut )
                logger.info( "Changing region cut %s to %s"%(cut, invCut) )

            logger.info( "Using CR Data region cut %s"%(regionCut_CR) )

            # QCD CR with 0 bjets and inverted lepton isolation +  SF for DY and MisIDSF
            # Attention: change region.cutstring to invLepIso and nBTag0 if there are leptons or btags in regions!!!
            cut_MC_CR    = "&&".join([ regionCut_CR, selection_MC_CR["cut"]   ])
            cut_Data_CR  = "&&".join([ regionCut_CR, selection_Data_CR["cut"] ])

            logger.info( "Using CR MC total cut %s"%(cut_MC_CR) )
            logger.info( "Using CR Data total cut %s"%(cut_Data_CR) )

            # Calculate yields for CR (normalized to data lumi)
            yield_data = self.yieldFromCache(setup, "Data", channel, cut_Data_CR, weight_Data_CR, overwrite=overwrite)

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

            yield_other  *= setup.dataLumi/1000.

            normRegYield  = yield_data - yield_other


            transferFac   = self.cachedTransferFactor(channel, setup, save=True, overwrite=overwrite, checkOnly=False)

            if transferFac == 0:
                logger.info("Transfer factor is 0. Skipping QCD estimate calculation and settting it to 0!")
                return u_float(1, 1)


            estimate      = normRegYield*transferFac

            logger.info("Calculating data-driven QCD normalization in channel " + channel + " using lumi " + str(setup.dataLumi) + ":")
            logger.info("yield data:                " + str(yield_data))
            logger.info("yield other:               " + str(yield_other))
            logger.info("yield (data-other):        " + str(normRegYield))
            logger.info("transfer factor:           " + str(transferFac))

            if normRegYield < 0 and yield_data > 0:
                logger.warning("Negative normalization region yield!")

        logger.info("Estimate for QCD in " + channel + " channel" + (" (lumi=" + str(setup.lumi) + "/pb)" if channel != "all" else "") + ": " + str(estimate) + (" (negative estimated being replaced by 0)" if estimate < 0 else ""))
        return estimate if estimate > 1 else u_float(1, 1)

if __name__ == "__main__":
    from TTGammaEFT.Analysis.regions      import regionsTTG, noPhotonRegionTTG, inclRegionsTTG
    from TTGammaEFT.Analysis.SetupHelpers import allRegions
    from TTGammaEFT.Analysis.Setup        import Setup

    overwrite = False
    print "incl"

    setup = Setup(year=2016, photonSelection=False)
    setup = setup.sysClone(parameters=allRegions["VG3"]["parameters"])

    estimate = DataDrivenQCDEstimate( "QCD-DD" )    
    estimate.initCache(setup.defaultCacheDir())

#    print "e", "dd", estimate._dataDrivenTransferFactor( "e", setup, overwrite=overwrite )
    print "e", "dd", estimate._fittedTransferFactor( "e", setup, overwrite=overwrite )
