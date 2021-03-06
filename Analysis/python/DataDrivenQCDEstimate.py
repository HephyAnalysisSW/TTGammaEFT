import os, sys
import ROOT
ROOT.gROOT.SetBatch(True)
from math import sqrt

from TTGammaEFT.Analysis.SystematicEstimator import SystematicEstimator
from TTGammaEFT.Analysis.SetupHelpers        import *
from TTGammaEFT.Tools.user                   import analysis_results, cache_directory
from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter, zMassRange

from Analysis.Tools.MergingDirDB             import MergingDirDB
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

overwriteHistos = False
ptBins  = [0, 45, 65, 80, 100, 120, -1]
etaBins = [0, 1.479, 1.7, 2.1, -1]

class DataDrivenQCDEstimate(SystematicEstimator):
    def __init__(self, name, cacheDir=None):
        super(DataDrivenQCDEstimate, self).__init__(name, cacheDir=cacheDir)

#    def _transferFactor(self, region, channel, setup, overwrite=False):
    def _transferFactor(self, channel, setup, qcdUpdates=None, overwrite=False):

        logger.info( "Calculating QCD transfer factor" )

        selection_MC_CR     = setup.selection("MC",   channel=channel, **setup.defaultParameters( update=qcdUpdates["CR"] if qcdUpdates else QCDTF_updates["CR"] ))
        selection_MC_SR     = setup.selection("MC",   channel=channel, **setup.defaultParameters( update=qcdUpdates["SR"] if qcdUpdates else QCDTF_updates["SR"] ))

        cut_MC_SR = selection_MC_SR["cut"]
        cut_MC_CR = selection_MC_CR["cut"]

        weight_MC_SR = selection_MC_SR["weightStr"]
        weight_MC_CR = selection_MC_SR["weightStr"].replace("reweightTrigger","reweightInvIsoTrigger").replace("reweightLeptonTrackingTightSF","reweightLeptonTrackingTightSFInvIso").replace("reweightLeptonTightSF","reweightLeptonTightSFInvIso") # w/ misID SF

        print
        print
        print channel, qcdUpdates
        print weight_MC_SR
        print cut_MC_SR
        print cut_MC_CR
        # The QCD yield in the CR with SR weight (sic)
        yield_QCD_CR = self.yieldFromCache(setup, "GJets",  channel, cut_MC_CR,   weight_MC_CR,   overwrite=overwrite)#*setup.dataLumi/1000.

        print "GJets CR", yield_QCD_CR

        if channel == "e":
            yield_QCD_CR     += self.yieldFromCache(setup, "QCD_e",    channel, cut_MC_CR,   weight_MC_CR,   overwrite=overwrite)#*setup.dataLumi/1000.
        elif channel == "mu":
            yield_QCD_CR     += self.yieldFromCache(setup, "QCD_mu",    channel, cut_MC_CR,   weight_MC_CR,   overwrite=overwrite)#*setup.dataLumi/1000.
        else:
            raise Exception("No QCD MC known for MC based TF and channel %s!"%channel)

        print "GJets + QCD CR", yield_QCD_CR
        # The QCD yield in the signal regions
        yield_QCD_SR    = self.yieldFromCache(setup, "GJets",  channel, cut_MC_SR,   weight_MC_SR,  overwrite=overwrite)#*setup.lumi/1000.

        print "GJets SR", yield_QCD_SR

        if channel == "e":
            yield_QCD_SR     += self.yieldFromCache(setup, "QCD_e",    channel, cut_MC_SR,   weight_MC_SR,  overwrite=overwrite)#*setup.lumi/1000.
        elif channel == "mu":
            yield_QCD_SR     += self.yieldFromCache(setup, "QCD_mu",    channel, cut_MC_SR,   weight_MC_SR,  overwrite=overwrite)#*setup.lumi/1000.
        else:
            raise Exception("No QCD MC known for MC based TF and channel %s!"%channel)

        print "GJets + QCD SR", yield_QCD_SR

        transferFac = yield_QCD_SR/yield_QCD_CR if yield_QCD_CR > 0 else u_float(0, 0)

        print "transfer factor", transferFac
        print
        print
        print
        print

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

        cut_MC_CR     = selection_MC_CR["cut"]
        cut_Data_CR   = selection_Data_CR["cut"]
        cut_MC_SR     = selection_MC_SR["cut"]
        cut_Data_SR   = selection_Data_SR["cut"]

        print( "Using QCD TF CR MC total cut %s"%(cut_MC_CR) )
        print( "Using QCD TF CR Data total cut %s"%(cut_Data_CR) )
        print( "Using QCD TF SR MC total cut %s"%(cut_MC_SR) )
        print( "Using QCD TF SR Data total cut %s"%(cut_Data_SR) )

        # Calculate yields for Data
        yield_data_SR  = self.yieldFromCache(setup, "Data", channel, cut_Data_SR, weight_Data_SR, overwrite=overwrite)

        if yield_data_SR <= 0:
            logger.warning("SR data yield for QCD TF is 0!")
            return u_float(0, 0)

        yield_data_CR  = self.yieldFromCache(setup, "Data", channel, cut_Data_CR, weight_Data_CR, overwrite=overwrite)

        if yield_data_CR <= 0:
            logger.warning("CR data yield for QCD TF is 0!")
            return u_float(0, 0)

        # Calculate yields for MC (normalized to data lumi)
        if addSF:
            if setup.nJet == "2":
                DYSF_val    = DY2SF_val
                WGSF_val    = WG2SF_val
                ZGSF_val    = ZG2SF_val
            elif setup.nJet == "3":
                DYSF_val    = DY3SF_val
                WGSF_val    = WG3SF_val
                ZGSF_val    = ZG3SF_val
            elif setup.nJet == "4":
                DYSF_val    = DY4SF_val
                WGSF_val    = WG4SF_val
                ZGSF_val    = ZG4SF_val
            elif setup.nJet == "5":
                DYSF_val    = DY5SF_val
                WGSF_val    = WG5SF_val
                ZGSF_val    = ZG5SF_val
            elif setup.nJet == "2p":
                DYSF_val    = DY2pSF_val
                WGSF_val    = WG2pSF_val
                ZGSF_val    = ZG2pSF_val
            elif setup.nJet == "3p":
                DYSF_val    = DY3pSF_val
                WGSF_val    = WG3pSF_val
                ZGSF_val    = ZG3pSF_val
            elif setup.nJet == "4p":
                DYSF_val    = DY4pSF_val
                WGSF_val    = WG4pSF_val
                ZGSF_val    = ZG4pSF_val

        yield_other_CR = 0
        yield_other_SR = 0
        for s in default_sampleList:
            if s in ["QCD-DD", "QCD", "QCD_e", "QCD_mu", "GJets", "Data"]: continue
            print s
            y_CR = self.yieldFromCache( setup, s, channel, cut_MC_CR, weight_MC_CR, overwrite=overwrite )
            y_SR = self.yieldFromCache( setup, s, channel, cut_MC_SR, weight_MC_SR, overwrite=overwrite )
            print "without SF", s, "CR", y_CR, "SR", y_SR

            if addSF:
                if "DY_LO" in s:
                    y_CR *= DYSF_val[setup.year] #add DY SF
                    y_SR *= DYSF_val[setup.year] #add DY SF
                elif "WJets" in s:
                    y_CR *= WJetsSF_val[setup.year] #add WJets SF
                    y_SR *= WJetsSF_val[setup.year] #add WJets SF
                elif "TTG" in s:
                    y_CR *= SSMSF_val[setup.year] #add TTG SF
                    y_SR *= SSMSF_val[setup.year] #add TTG SF
                elif "ZG" in s:
                    y_CR *= ZGSF_val[setup.year] #add ZGamma SF
                    y_SR *= ZGSF_val[setup.year] #add ZGamma SF
                elif "WG" in s:
                    y_CR *= WGSF_val[setup.year] #add WGamma SF
                    y_SR *= WGSF_val[setup.year] #add WGamma SF
            print "with SF", s, "CR", y_CR, "SR", y_SR
            yield_other_CR += y_CR
            yield_other_SR += y_SR

        qcd_est_CR   = yield_data_CR - yield_other_CR
        qcd_est_SR   = yield_data_SR - yield_other_SR
        # TF from full QCD CR to full SR
        transRatio   = qcd_est_SR / qcd_est_CR if qcd_est_CR > 0 else u_float(0, 0)
        # scale the TF for subregions in e.g. m(l,gamma) or m3 (region cuts)
        transferFac = transRatio # * fractionalSR

        print("Calculating data-driven QCD TF normalization in channel " + channel + " using lumi " + str(setup.dataLumi) + ":")
        print("TF CR yield data:                " + str(yield_data_CR))
        print("TF CR yield other:               " + str(yield_other_CR))
        print("TF CR yield (data-other):        " + str(qcd_est_CR))
        print("TF SR yield data:                " + str(yield_data_SR))
        print("TF SR yield other:               " + str(yield_other_SR))
        print("TF SR yield (data-other):        " + str(qcd_est_SR))
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

#        var    = "MET_pt" #"mT"
#        invVar = "MET_pt" #"mTinv"
        var    = "mT"
        invVar = "mTinv"
        print( "Calculating data-driven QCD transfer factor" )

        selection_MC_CR     = setup.selection("MC",   channel=channel, **setup.defaultParameters( update=qcdUpdates["CR"] if qcdUpdates else QCDTF_updates["CR"] ))
        selection_Data_CR   = setup.selection("Data", channel=channel, **setup.defaultParameters( update=qcdUpdates["CR"] if qcdUpdates else QCDTF_updates["CR"] ))
        selection_MC_SR     = setup.selection("MC",   channel=channel, **setup.defaultParameters( update=qcdUpdates["SR"] if qcdUpdates else QCDTF_updates["SR"] ))
        selection_Data_SR   = setup.selection("Data", channel=channel, **setup.defaultParameters( update=qcdUpdates["SR"] if qcdUpdates else QCDTF_updates["SR"] ))

        weight_MC_CR      = selection_MC_CR["weightStr"].replace("reweightTrigger","reweightInvIsoTrigger").replace("reweightLeptonTrackingTightSF","reweightLeptonTrackingTightSFInvIso").replace("reweightLeptonTightSF","reweightLeptonTightSFInvIso") # w/ misID SF
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
        updates      = qcdUpdates["SR"] if qcdUpdates else QCDTF_updates["SR"]
        photonRegion = updates["nPhoton"][0] > 0 if "nPhoton" in updates.keys() else setup.isPhotonSelection
        bjetRegion   = updates["nBTag"][0] > 0   if "nBTag" in updates.keys()   else setup.parameters["nBTag"][0] > 0
        njets        = updates["nJet"][0]        if "nJet" in updates.keys()    else setup.parameters["nJet"][0]

        if var == "mT":
            if       photonRegion and not bjetRegion:                floatSample = "WG"
            elif     photonRegion and     bjetRegion and njets == 2: floatSample = "other"
            elif     photonRegion and     bjetRegion:                floatSample = "TTG" #"Top"?
            elif not photonRegion and not bjetRegion:                floatSample = "WJets"
            elif not photonRegion and     bjetRegion and njets == 2: floatSample = "WJets"
            elif not photonRegion and     bjetRegion:                floatSample = "Top"

        else:
            if       photonRegion and not bjetRegion:                floatSample = "WG"
            elif     photonRegion and     bjetRegion and njets == 2: floatSample = "other"
            elif     photonRegion and     bjetRegion:                floatSample = "TTG" #"Top"?
            elif not photonRegion and not bjetRegion:                floatSample = "WJets"
            elif not photonRegion and     bjetRegion and njets == 2: floatSample = "WJets"
            elif not photonRegion and     bjetRegion:                floatSample = "Top"

        print( "Leaving sample %s floating in the fit"%(floatSample) )

        binning = [ 20, 0, 200 ]
        print( "Getting %s histograms with binning %s"%(var," ".join(map(str,binning))) )

        # get mT histos
        dataHist  = self.histoFromCache( var,    binning, setup, "Data", channel, cut_Data_SR, weight_Data_SR, overwrite=overwriteHistos)
        # safe some memory, you don't need the CR data hist, only for estimating the qcd hist
        qcdHist   = self.histoFromCache( invVar, binning, setup, "Data", channel, cut_Data_CR, weight_Data_CR, overwrite=overwriteHistos)

        fixedHist = dataHist.Clone("fixed") # sum of contributions that stay fixed
        fixedHist.Scale(0.)

        if addSF:
            if setup.nJet == "2":
                DYSF_val    = DY2SF_val
                WGSF_val    = WG2SF_val
                ZGSF_val    = ZG2SF_val
            elif setup.nJet == "3":
                DYSF_val    = DY3SF_val
                WGSF_val    = WG3SF_val
                ZGSF_val    = ZG3SF_val
            elif setup.nJet == "4":
                DYSF_val    = DY4SF_val
                WGSF_val    = WG4SF_val
                ZGSF_val    = ZG4SF_val
            elif setup.nJet == "5":
                DYSF_val    = DY5SF_val
                WGSF_val    = WG5SF_val
                ZGSF_val    = ZG5SF_val
            elif setup.nJet == "2p":
                DYSF_val    = DY2pSF_val
                WGSF_val    = WG2pSF_val
                ZGSF_val    = ZG2pSF_val
            elif setup.nJet == "3p":
                DYSF_val    = DY3pSF_val
                WGSF_val    = WG3pSF_val
                ZGSF_val    = ZG3pSF_val
            elif setup.nJet == "4p":
                DYSF_val    = DY4pSF_val
                WGSF_val    = WG4pSF_val
                ZGSF_val    = ZG4pSF_val

        # Calculate mTs for MC (normalized to data lumi)
        for s in default_sampleList:
            if s in ["QCD-DD", "QCD", "QCD_e", "QCD_mu", "GJets", "Data"]: continue
            tmp_SR = self.histoFromCache( var,    binning, setup, s, channel, cut_MC_SR, weight_MC_SR, overwrite=overwriteHistos )
            tmp_CR = self.histoFromCache( invVar, binning, setup, s, channel, cut_MC_CR, weight_MC_CR, overwrite=overwriteHistos )
            # apply SF after histo caching
            if addSF:
                if "DY" in s:
                    tmp_SR.Scale(DYSF_val[setup.year].val)
                    tmp_CR.Scale(DYSF_val[setup.year].val)
                elif "WJets" in s:
                    tmp_SR.Scale(WJetsSF_val[setup.year].val)
                    tmp_CR.Scale(WJetsSF_val[setup.year].val)
                elif "ZG" in s:
                    tmp_SR.Scale(ZGSF_val[setup.year].val)
                    tmp_CR.Scale(ZGSF_val[setup.year].val)
                elif "WG" in s:
                    tmp_SR.Scale(WGSF_val[setup.year].val)
                    tmp_CR.Scale(WGSF_val[setup.year].val)
                elif "TTG" in s:
                    tmp_SR.Scale(SSMSF_val[setup.year].val)
                    tmp_CR.Scale(SSMSF_val[setup.year].val)

#            tmp_SR.Scale( setup.dataLumi/1000. )
#            tmp_CR.Scale( setup.dataLumi/1000. )

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
        if var == "mT":
            fitter.SetRangeX(1,12)
        # it is a FRACTION fitter, so the range is the fraction of the data hist
        nTotal      = dataHist.Integral()
        nFloatScale = floatHist.Integral() / nTotal
        nFixedScale = fixedHist.Integral() / nTotal
        nQCDScale   = qcdHist.Integral()   / nTotal

        if not all([nTotal,nFloatScale,nFixedScale,nQCDScale]):
            raise Exception("Something is wrong with the cached histograms for the QCD TF!")

        firstApprox = 0.2 if bjetRegion else 1. # be kind an help the fit a little
        tfitter = fitter.GetFitter()
        tfitter.Config().ParSettings(0).Set("qcd",   nQCDScale*firstApprox, 0.01, 0.,               1.)
        tfitter.Config().ParSettings(1).Set("float", nFloatScale,           0.01, 0.,               1.)
        tfitter.Config().ParSettings(2).Set("fixed", nFixedScale,           0.0,   nFixedScale*0.999, nFixedScale*1.001)
        tfitter.Config().ParSettings(2).Fix()
        # fix the floating sample in photonRegions e-channel since mT is not a good handle
#        if var == "mT" and channel == "e": # cant make it fixed, as the nDOF is not matching, no clue how to change that, nice workaround
#        if var == "mT" and photonRegion and channel == "e": # cant make it fixed, as the nDOF is not matching, no clue how to change that, nice workaround
        # let it float a bit
        if photonRegion:
            tfitter.Config().ParSettings(1).Set("float", nFloatScale, 0.001, nFloatScale*0.999, nFloatScale*1.001)
        elif bjetRegion:
            tfitter.Config().ParSettings(1).Set("float", nFloatScale, 0.001, nFloatScale*0.8, nFloatScale*1.2)
        else:
            tfitter.Config().ParSettings(1).Set("float", nFloatScale, 0.001, nFloatScale*0.8, nFloatScale*1.2)


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

        return transferFac if transferFac > 0 else u_float(0.001, 1)


    def _nJetFitFunction(self, channel, setup, qcdUpdates=None, overwrite=False):

        # fill a histogram with the QCD MC TF for 2, 3 and >=4 jets and fit a linear function to it
        qcdTF = ROOT.TH1F( "tf", "tf", 3, 1.5, 4.5 )
        func  = ROOT.TF1("func", "[0]+[1]*x", 1, 5 )

        for nJet in [(2,2), (3,3), (4,-1)]:
            qcdUpdate = copy.deepcopy(qcdUpdates) if qcdUpdates else QCDTF_updates
            qcdUpdate["CR"]["nJet"] = nJet
            qcdUpdate["SR"]["nJet"] = nJet
            tf = self.cachedQCDMCTransferFactor( channel, setup, qcdUpdates=qcdUpdate, overwrite=overwrite )
            qcdTF.SetBinContent( qcdTF.FindBin(nJet[0]), tf.val )
            qcdTF.SetBinError(   qcdTF.FindBin(nJet[0]), tf.sigma )

        qcdTF.Fit(func,"NO")

        return func

    def _nJetFittedScaleFactor(self, channel, setup, qcdUpdates=None, overwrite=False, evalForNJet=None ):
        """ fit the MC TF in nJet bins
            flat in 0 b-tag, but linear in b-tagged regions
            estimate the ratio of the QCD TF in x Jet / 2 Jet and apply the factor in the QCD estimation
            currently implemented for 3 and >=4 jet bins
        """
        # no scale factor for 2 jet or 1 jet bins
        if (not evalForNJet and setup.nJet in ["2", "2p", "1", "1p"]) or (evalForNJet and evalForNJet==2): return 1.

        func = self._nJetFitFunction(channel=channel, setup=setup, qcdUpdates=qcdUpdates, overwrite=overwrite)

        # return the ratio of the value at the 2 jet bin to the current nJet bin in the setup, as the QCD TF is evaluated at the 2 jet bin
        sf = func.Eval( int(setup.nJet[0]) if not evalForNJet else evalForNJet ) / func.Eval( 2 )
        return sf if sf > 0 else 1.

    def _nJetScaleFactor(self, channel, setup, qcdUpdates=None, overwrite=False, evalForNJet=None ):
        """ fit the MC TF in nJet bins
            flat in 0 b-tag, but linear in b-tagged regions
            estimate the ratio of the QCD TF in x Jet / 2 Jet and apply the factor in the QCD estimation
            currently implemented for 3 and >=4 jet bins
        """
        # no scale factor for 2 jet or 1 jet bins
        if (not evalForNJet and setup.nJet in ["2", "2p", "1", "1p"]) or (evalForNJet and evalForNJet==2): return 1.

        # inclusive qcd mc tf if not otherwise stated
        qcdUpdate = copy.deepcopy(qcdUpdates) if qcdUpdates else QCDTF_updates
        qcdUpdate["CR"]["nJet"] = setup.parameters["nJet"]
        qcdUpdate["SR"]["nJet"] = setup.parameters["nJet"]
        tfnjet = self.cachedQCDMCTransferFactor( channel, setup, qcdUpdates=qcdUpdate, overwrite=overwrite ).val

        # inclusive 2 jet qcd mc tf if not otherwise stated
        qcdUpdate["CR"]["nJet"] = (2,2)
        qcdUpdate["SR"]["nJet"] = (2,2)
        tf2jet = self.cachedQCDMCTransferFactor( channel, setup, qcdUpdates=qcdUpdate, overwrite=overwrite ).val
        return tfnjet / tf2jet if tf2jet > 0 else 1.

    #Concrete implementation of abstract method "estimate" as defined in Systematic
    def _estimate(self, region, channel, setup, signalAddon=None, overwrite=False):

        if setup.nJet == "3p":
            setup4p = setup.sysClone( parameters={"nJet":(4,-1)} )
            setup3 = setup.sysClone( parameters={"nJet":(3,3)} )
            return sum([ self.cachedEstimate(region, channel, s, signalAddon=signalAddon, overwrite=overwrite) for s in [setup3,setup4p]])

        #Sum of all channels for "all"
        if channel=="all":
            return sum([ self.cachedEstimate(region, c, setup, signalAddon=signalAddon) for c in lepChannels])

        elif channel=="SFtight":
            return sum([ self.cachedEstimate(region, c, setup, signalAddon=signalAddon) for c in dilepChannels])

        else:

            logger.info( "Calculating QCD estimate" )
            # Skip QCD estimate for 2 lepton CR (QCD = 0)
            if channel in dilepChannels:
                logger.info("Estimate for QCD in dileptonic channels skipped: 0")
                return u_float(0, 0)

            selection_MC_CR   = setup.selection("MC",   channel=channel, **setup.defaultParameters( update=QCD_updates ))
            selection_Data_CR = setup.selection("Data", channel=channel, **setup.defaultParameters( update=QCD_updates ))

#            if channel == "e":
#                selection_MC_CR["cut"] += "&&LeptonTightInvIso0_pfRelIso03_all<0.2"
#                selection_Data_CR["cut"] += "&&LeptonTightInvIso0_pfRelIso03_all<0.2"
#            else:
#                selection_MC_CR["cut"] += "&&LeptonTightInvIso0_pfRelIso04_all<0.4"
#                selection_Data_CR["cut"] += "&&LeptonTightInvIso0_pfRelIso04_all<0.4"

            weight_Data_CR    = selection_Data_CR["weightStr"]
            weight_MC_CR      = selection_MC_CR["weightStr"].replace("reweightTrigger","reweightInvIsoTrigger").replace("reweightLeptonTrackingTightSF","reweightLeptonTrackingTightSFInvIso").replace("reweightLeptonTightSF","reweightLeptonTightSFInvIso") # w/ misID SF

            regionCut_CR      = region.cutString( setup.sys['selectionModifier'] )

            # change region cuts for inverted leptons
            for cut, invCut in QCD_cutReplacements.iteritems():
                regionCut_CR = regionCut_CR.replace( cut, invCut )
                logger.info( "Changing region cut %s to %s"%(cut, invCut) )

            logger.info( "Using CR Data region cut %s"%(regionCut_CR) )

            # QCD CR with 0 bjets and inverted lepton isolation +  SF for DY and MisIDSF
            # Attention: change region.cutstring to invLepIso and nBTag0 if there are leptons or btags in regions!!!
#            cut_MC_CR    = "&&".join([ regionCut_CR, selection_MC_CR["cut"]   ])
#            cut_Data_CR  = "&&".join([ regionCut_CR, selection_Data_CR["cut"] ])
#            logger.info( "Using CR MC total cut %s"%(cut_MC_CR) )
#            logger.info( "Using CR Data total cut %s"%(cut_Data_CR) )

            # Accounting for 
            leptonPtCutVar = "LeptonTightInvIso0_pt"
            if channel in ["e", "eetight"]:
                leptonEtaCutVar = "abs(LeptonTightInvIso0_eta+LeptonTightInvIso0_deltaEtaSC)"
            else:
                leptonEtaCutVar = "abs(LeptonTightInvIso0_eta)"

            QCDTF_updates_2J = copy.deepcopy(QCDTF_updates)
            QCDTF_updates_nJ = copy.deepcopy(QCDTF_updates)
            if "nJet" in QCDTF_updates_nJ["CR"].keys(): del QCDTF_updates_nJ["CR"]["nJet"]
            if "nJet" in QCDTF_updates_nJ["SR"].keys(): del QCDTF_updates_nJ["SR"]["nJet"]

            if addSF:
                if setup.nJet == "2":
                    DYSF_val    = DY2SF_val
                    WGSF_val    = WG2SF_val
                    ZGSF_val    = ZG2SF_val
                elif setup.nJet == "3":
                    DYSF_val    = DY3SF_val
                    WGSF_val    = WG3SF_val
                    ZGSF_val    = ZG3SF_val
                elif setup.nJet == "4":
                    DYSF_val    = DY4SF_val
                    WGSF_val    = WG4SF_val
                    ZGSF_val    = ZG4SF_val
                elif setup.nJet == "5":
                    DYSF_val    = DY5SF_val
                    WGSF_val    = WG5SF_val
                    ZGSF_val    = ZG5SF_val
                elif setup.nJet == "2p":
                    DYSF_val    = DY2pSF_val
                    WGSF_val    = WG2pSF_val
                    ZGSF_val    = ZG2pSF_val
                elif setup.nJet == "3p":
                    DYSF_val    = DY3pSF_val
                    WGSF_val    = WG3pSF_val
                    ZGSF_val    = ZG3pSF_val
                elif setup.nJet == "4p":
                    DYSF_val    = DY4pSF_val
                    WGSF_val    = WG4pSF_val
                    ZGSF_val    = ZG4pSF_val

            qcd_yield = u_float(0)
            for i_pt, pt in enumerate(ptBins[:-1]):
                for i_eta, eta in enumerate(etaBins[:-1]):
                    etaLow, etaHigh = eta, etaBins[i_eta+1]
                    ptLow, ptHigh   = pt,  ptBins[i_pt+1]

                    # Transfer Factor, get the QCD histograms always in barrel regions
                    QCDTF_updates_2J["CR"]["leptonEta"] = ( etaLow, etaHigh )
                    QCDTF_updates_2J["CR"]["leptonPt"]  = ( ptLow,  ptHigh   )
                    QCDTF_updates_2J["SR"]["leptonEta"] = ( etaLow, etaHigh )
                    QCDTF_updates_2J["SR"]["leptonPt"]  = ( ptLow,  ptHigh   )

#                    QCDTF_updates_nJ["CR"]["leptonEta"] = ( etaLow, etaHigh )
#                    QCDTF_updates_nJ["CR"]["leptonPt"]  = ( ptLow,  ptHigh   )
#                    QCDTF_updates_nJ["SR"]["leptonEta"] = ( etaLow, etaHigh )
#                    QCDTF_updates_nJ["SR"]["leptonPt"]  = ( ptLow,  ptHigh   )

                    # Remove that for now
                    # define the 2016 e-channel QCD sideband in barrel only (bad mT fit in EC)
                    if False and channel == "e" and setup.year == 2016 and (etaHigh > 1.479 or etaHigh < 0):
                        QCDTF_updates_2J["CR"]["leptonEta"] = ( 0, 1.479 )
#                        QCDTF_updates_nJ["CR"]["leptonEta"] = ( 0, 1.479 )

                    qcdUpdates  = { "CR":QCDTF_updates_2J["CR"], "SR":QCDTF_updates_2J["SR"] }
                    transferFac = self.cachedTransferFactor( channel, setup, qcdUpdates=qcdUpdates, overwrite=overwrite, checkOnly=False )
                    if transferFac.val <= 0: continue

                    nJetSF = 1.
                    if setup.isBTagged:
                        nJetUpdates = copy.deepcopy(qcdUpdates)
                        nJetUpdates["CR"]["leptonPt"] = ( 0, -1 )
                        nJetUpdates["SR"]["leptonPt"] = ( 0, -1 )

                        nJetSF = self._nJetScaleFactor("mu", setup, qcdUpdates=nJetUpdates)
                        if nJetSF <= 0: nJetSF = 1.


#                    qcdUpdates     = { "CR":QCDTF_updates_nJ["CR"], "SR":QCDTF_updates_nJ["SR"] }
#                    transferFac_nJ = self.cachedTransferFactor( channel, setup, qcdUpdates=qcdUpdates, overwrite=overwrite, checkOnly=False )

                    # set the transferfactor uncertainty to the nJet dependence uncertainty
#                    transferFac.sigma = abs( transferFac.val - transferFac_nJ.val )
#                    if transferFac.sigma > transferFac.val: transferFac.sigma = transferFac.val #upper bound of 100%

                    # define the 2016 e-channel QCD sideband in barrel only (bad mT fit in EC)
                    # Remove that for now
                    if False and channel == "e" and setup.year == 2016 and (etaHigh > 1.479 or etaHigh < 0):
                        leptonPtEtaCut  = [ leptonEtaCutVar + ">=0", leptonPtCutVar + ">=" + str(ptLow) ]
                        leptonPtEtaCut += [ leptonEtaCutVar + "<1.479" ]
                        if ptHigh > 0:  leptonPtEtaCut += [ leptonPtCutVar + "<" + str(ptHigh) ]
                    else:
                        leptonPtEtaCut = [ leptonEtaCutVar + ">=" + str(etaLow), leptonPtCutVar + ">=" + str(ptLow) ]
                        if etaHigh > 0: leptonPtEtaCut += [ leptonEtaCutVar + "<" + str(etaHigh) ]
                        if ptHigh > 0:  leptonPtEtaCut += [ leptonPtCutVar + "<" + str(ptHigh) ]

                    leptonPtEtaCut = "&&".join( leptonPtEtaCut )

                    cut_MC_CR   = "&&".join([ regionCut_CR, selection_MC_CR["cut"],   leptonPtEtaCut ])
                    cut_Data_CR = "&&".join([ regionCut_CR, selection_Data_CR["cut"], leptonPtEtaCut ])
                    logger.info( "Using CR MC total cut %s"%(cut_MC_CR) )
                    logger.info( "Using CR Data total cut %s"%(cut_Data_CR) )

                    # Calculate yields for CR (normalized to data lumi)
                    yield_data = self.yieldFromCache(setup, "Data", channel, cut_Data_CR, weight_Data_CR, overwrite=overwrite)
                    if yield_data.val <= 0: continue

                    yield_other = 0
                    for s in default_sampleList:
                        if s in ["QCD-DD", "QCD", "QCD_e", "QCD_mu", "GJets", "Data"]: continue
                        y  = self.yieldFromCache( setup, s, channel, cut_MC_CR, weight_MC_CR, overwrite=overwrite )

                        if addSF:
                            if   s == "DY_LO":
                                y *= DYSF_val[setup.year]    #add DY SF
                            elif s == "WJets":
                                y *= WJetsSF_val[setup.year] #add WJets SF
                            elif s == "ZG":
                                y *= ZGSF_val[setup.year]    #add ZGamma SF
                            elif s == "WG":
                                y *= WGSF_val[setup.year]    #add WGamma SF
                        yield_other += y

#                    yield_other  *= setup.dataLumi/1000.

                    normRegYield = yield_data - yield_other
                    if normRegYield <= 0: continue
                    # remove uncertainty from yield, replace it with transfer factor uncertainty
                    normRegYield.sigma = 0

                    estimate   = normRegYield*transferFac*nJetSF
                    qcd_yield += estimate

                    logger.info("Calculating data-driven QCD normalization in channel " + channel + " using lumi " + str(setup.dataLumi) + ":")
                    logger.info("yield data:                " + str(yield_data))
                    logger.info("yield other:               " + str(yield_other))
                    logger.info("yield (data-other):        " + str(normRegYield))
                    logger.info("transfer factor:           " + str(transferFac))

            # correct for the nJet dependence
            return qcd_yield if qcd_yield >= 0 else u_float(0, 0)

if __name__ == "__main__":
    from TTGammaEFT.Analysis.regions      import regionsTTG, noPhotonRegionTTG, inclRegionsTTG
    from TTGammaEFT.Analysis.SetupHelpers import allRegions
    from TTGammaEFT.Analysis.Setup        import Setup

    overwrite = False
    print "incl"

    setup = Setup(year=2016, photonSelection=False)
#    setup = setup.sysClone(parameters=allRegions["SR2"]["parameters"])
    setup = setup.sysClone(parameters=allRegions["TT4p"]["parameters"])

    estimate = DataDrivenQCDEstimate( "QCD-DD" )    
    estimate.initCache(setup.defaultCacheDir())

#    print "e", "dd", estimate._fittedTransferFactor( "e", setup, overwrite=overwrite )
#    print "mu", "dd", estimate._fittedTransferFactor( "mu", setup, overwrite=overwrite )
    print estimate._nJetScaleFactor("e", setup, qcdUpdates=None, overwrite=False)
#    print "e", "dd", estimate._estimate( allRegions["WJets2"]["regions"][0], "e", setup, overwrite=overwrite )
