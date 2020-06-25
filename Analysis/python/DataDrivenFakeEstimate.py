import os, sys
import ROOT
ROOT.gROOT.SetBatch(True)
from math import sqrt

from TTGammaEFT.Analysis.SystematicEstimator   import SystematicEstimator
from TTGammaEFT.Analysis.SetupHelpers          import *
from TTGammaEFT.Analysis.Setup                 import Setup
from TTGammaEFT.Analysis.DataObservation       import DataObservation
from TTGammaEFT.Analysis.MCBasedEstimate       import MCBasedEstimate
from TTGammaEFT.Analysis.DataDrivenQCDEstimate import DataDrivenQCDEstimate

from TTGammaEFT.Tools.user                     import analysis_results, cache_directory
from TTGammaEFT.Tools.cutInterpreter           import cutInterpreter, zMassRange

from Analysis.Tools.MergingDirDB               import MergingDirDB
from Analysis.Tools.u_float                    import u_float

# Logging
if __name__=="__main__":
    import Analysis.Tools.logger as logger
    logger = logger.get_logger( "INFO", logFile=None)
    import RootTools.core.logger as logger_rt
    logger_rt = logger_rt.get_logger( "INFO", logFile=None )
else:
    import logging
    logger = logging.getLogger(__name__)

addSF = True

class DataDrivenFakeEstimate(SystematicEstimator):
    def __init__(self, name, cacheDir=None):
        super(DataDrivenFakeEstimate, self).__init__(name, cacheDir=cacheDir)
    #Concrete implementation of abstract method "estimate" as defined in Systematic
    def _estimate(self, region, channel, setup, signalAddon=None, overwrite=False):

        #Sum of all channels for "all"
        if channel == "all":
            return sum([ self.cachedEstimate(region, c, setup, signalAddon=signalAddon) for c in lepChannels])

        elif channel == "SFtight":
            return sum([ self.cachedEstimate(region, c, setup, signalAddon=signalAddon) for c in dilepChannels])

        else:
            # Estimate yield in highSieie (Hs), highChgIso (Hc), lowSieie (Ls) and lowChgIso (Lc)
            # ABCD like: LsLc = HsLc * LsHc / HsHc
            # data-driven estimation: LsLc (data-driven) = LsLc(MC) * LsLc(data) / LsLc(MC)
            # data-driven fake estimate = (data_LsHc  - MCPrompt_LsHc) * ( (data_HsLc - MCPrompt_HsLc) / (data_HsHc - MCPrompt_HsHc) ) * ( MChad_LsLc / MChad_LsHc ) * ( MChad_HsHc / MChad_HsLc ) * ( mc_LsLc / MChad_LsLc )
            # first term: data-driven estimate of all hadronic in LsHc
            # second term: shape correction for low/high chgIso in data
            # third/fourth term: shape correction for low/high chgIso in MC, actually it is a double ratio
            # fifth term: scale data-driven estimate to the process to estimate for according to the MC yield
            # MChad_LsLc cancels in that equation, leaving mc_LsLc * factor == mc yield to estimate for * datadriven correction factor (independent on the mc yield, just on the region cuts)
            # MChad = all hadronic MC
            # MCPrompt = all gen/misID/PU MC
            # mc = mc to estimate the fakes for
            # the datadriven fake correction factor is everything except the last term. Term 1-4 are independent on the process

            # get the ddFakeCorrection for the nominal setup, not the reweighted
#            setup_noSys = Setup( year=setup.year, photonSelection=False )
#            setup_noSys = setup_noSys.sysClone( parameters=setup.parameters )
            return self._dataDrivenFakes( region, channel, setup, overwrite=overwrite)
#                setup_noSys = Setup( year=setup.year, photonSelection=False )
#                setup_noSys = setup_noSys.sysClone( parameters=setup.parameters )
#                ddFakeCorrection = self.cachedFakeFactor(region, channel, setup_noSys, overwrite=overwrite).val

#                # take MC based fakes if the dd-SF is 0
#                if not ddFakeCorrection: return mc_LsLc

#                # DD fake estimate in SR
#                return mc_LsLc * ddFakeCorrection
#
#            else:
#                # get the MC based Estimate for fakes in the region including systematic uncertainties
#                estimate = MCBasedEstimate( name=self.name, process=self.process )
#                estimate.initCache(setup.defaultCacheDir())
#                mc_LsLc  = estimate.cachedEstimate( region, channel, setup, overwrite=overwrite )
#
#                if mc_LsLc <= 0: return u_float(0)

#                # MC based fake estimate in CR
#                return mc_LsLc

    def _dataDrivenFakeCorrectionFactor(self, region, channel, setup, overwrite=False):
            # not used anymore, gives some kind of fake SF which could be compared to Nabin
            # factor to multiply with non-prompt mc yield for data-driven estimation
            mcFakes = self._fakesMC(region, channel, setup, overwrite=overwrite)
            if mcFakes <= 0: return u_float(0)

            ddFakes = self._dataDrivenFakes(region, channel, setup, overwrite=overwrite)
            return ddFakes / mcFakes

    def _dataDrivenFakes(self, region, channel, setup, overwrite=False):

            dataFakes = self._fakesData(region, channel, setup, overwrite=overwrite)
            if dataFakes <= 0: return u_float(0)

            kappaData = self._kappaData(region, channel, setup, overwrite=overwrite)
            if kappaData <= 0: return u_float(0)

            kappaMC   = self._kappaMC(region, channel, setup, overwrite=overwrite)
            if kappaMC <= 0: return u_float(0)

            return dataFakes * kappaData * kappaMC


    def _kappaData(self, region, channel, setup, overwrite=False):
            # data correction factor for low chgIso -> high chgIso

            param_HsLc = { "photonIso":"highSieie",           "addMisIDSF":addSF }
            param_HsHc = { "photonIso":"highChgIsohighSieie", "addMisIDSF":addSF }

            params_HsLc = copy.deepcopy(setup.parameters)
            params_HsHc = copy.deepcopy(setup.parameters)

            params_HsLc.update( param_HsLc )
            params_HsHc.update( param_HsHc )

            setup_HsLc = setup.sysClone(parameters=params_HsLc)
            setup_HsHc = setup.sysClone(parameters=params_HsHc)

            estimate = DataObservation(name="Data", process=setup.processes["Data"], cacheDir=setup.defaultCacheDir())

            estimate.initCache(setup_HsLc.defaultCacheDir())
            data_HsLc = estimate.cachedEstimate( region, channel, setup_HsLc, overwrite=overwrite )
            estimate.initCache(setup_HsHc.defaultCacheDir())
            data_HsHc = estimate.cachedEstimate( region, channel, setup_HsHc, overwrite=overwrite )

            mcPrompt_HsLc = u_float(0)
            mcPrompt_HsHc = u_float(0)

            if addSF:
                if setup.nJet == "2":
                    DYSF_val    = DY2SF_val
                    WGSF_val    = WG2SF_val
                    ZGSF_val    = ZG2SF_val
                    QCDSF_val   = QCD2SF_val
                elif setup.nJet == "3":
                    DYSF_val    = DY3SF_val
                    WGSF_val    = WG3SF_val
                    ZGSF_val    = ZG3SF_val
                    QCDSF_val   = QCD3SF_val
                elif setup.nJet == "4":
                    DYSF_val    = DY4SF_val
                    WGSF_val    = WG4SF_val
                    ZGSF_val    = ZG4SF_val
                    QCDSF_val   = QCD4SF_val
                elif setup.nJet == "5":
                    DYSF_val    = DY5SF_val
                    WGSF_val    = WG5SF_val
                    ZGSF_val    = ZG5SF_val
                    QCDSF_val   = QCD5SF_val
                elif setup.nJet == "2p":
                    DYSF_val    = DY2pSF_val
                    WGSF_val    = WG2pSF_val
                    ZGSF_val    = ZG2pSF_val
                    QCDSF_val   = QCD2pSF_val
                elif setup.nJet == "3p":
                    DYSF_val    = DY3pSF_val
                    WGSF_val    = WG3pSF_val
                    ZGSF_val    = ZG3pSF_val
                    QCDSF_val   = QCD3pSF_val
                elif setup.nJet == "4p":
                    DYSF_val    = DY4pSF_val
                    WGSF_val    = WG4pSF_val
                    ZGSF_val    = ZG4pSF_val
                    QCDSF_val   = QCD4pSF_val

            for s in default_photonSampleList:
                if s in ["QCD-DD", "QCD", "GJets", "Data", "fakes-DD"]: continue
                if "had" in s: continue

                # get the MC based Estimate for fakes in the region
                estimate = MCBasedEstimate( name=s, process=setup.processes[s] )
                estimate.initCache(setup.defaultCacheDir())

                y_HsLc = estimate.cachedEstimate( region, channel, setup_HsLc, overwrite=overwrite )
                y_HsHc = estimate.cachedEstimate( region, channel, setup_HsHc, overwrite=overwrite )

                if addSF:
                    if "DY_LO" in s:
                        y_HsLc *= DYSF_val[setup.year].val #add DY SF
                        y_HsHc *= DYSF_val[setup.year].val #add DY SF
#                    elif "WJets" in s:
#                        y_HsLc *= WJetsSF_val[setup.year].val #add WJets SF
#                        y_HsHc *= WJetsSF_val[setup.year].val #add WJets SF
                    elif "TTG" in s:
                        y_HsLc *= SSMSF_val[setup.year].val #add TTG SF
                        y_HsHc *= SSMSF_val[setup.year].val #add TTG SF
                    elif "ZG" in s:
                        y_HsLc *= ZGSF_val[setup.year].val #add ZGamma SF
                        y_HsHc *= ZGSF_val[setup.year].val #add ZGamma SF
                    elif "WG" in s:
                        y_HsLc *= WGSF_val[setup.year].val #add WGamma SF
                        y_HsHc *= WGSF_val[setup.year].val #add WGamma SF

                mcPrompt_HsLc += y_HsLc
                mcPrompt_HsHc += y_HsHc

            # check if any of the factors would be <= 0 to safe time:
            if data_HsLc - mcPrompt_HsLc <= 0: return u_float(0)
            if data_HsHc - mcPrompt_HsHc <= 0: return u_float(0)

            # Add QCD to Prompt, make sure you run on the semilep skim
            estimate = DataDrivenQCDEstimate( name="QCD-DD" )
            estimate.initCache(setup.defaultCacheDir())

            setup_noSys_HsHc = Setup( year=setup.year, photonSelection=False )
            setup_noSys_HsHc = setup_noSys_HsHc.sysClone( parameters=setup.parameters )
            setup_noSys_HsHc = setup_noSys_HsHc.sysClone( parameters=params_HsHc )

            y_QCD_HsHc     = estimate.cachedEstimate( region, channel, setup_noSys_HsHc, overwrite=overwrite )
            y_QCD_HsHc    *= QCDSF_val[setup.year].val
            mcPrompt_HsHc += y_QCD_HsHc.val
            dataHad_HsHc   = data_HsHc-mcPrompt_HsHc

            if dataHad_HsHc <= 0: return u_float(0)

            setup_noSys_HsLc = Setup( year=setup.year, photonSelection=False )
            setup_noSys_HsLc = setup_noSys_HsLc.sysClone( parameters=setup.parameters )
            setup_noSys_HsLc = setup_noSys_HsLc.sysClone( parameters=params_HsLc )

            y_QCD_HsLc     = estimate.cachedEstimate( region, channel, setup_noSys_HsLc, overwrite=overwrite )
            y_QCD_HsLc    *= QCDSF_val[setup.year].val
            mcPrompt_HsLc += y_QCD_HsLc.val
            dataHad_HsLc   = data_HsLc-mcPrompt_HsLc

            if dataHad_HsLc <= 0: return u_float(0)

            return dataHad_HsLc / dataHad_HsHc


    def _fakesData(self, region, channel, setup, overwrite=False):

            param_LsHc  = { "photonIso":"highChgIso",          "addMisIDSF":addSF }
            params_LsHc = copy.deepcopy(setup.parameters)
            params_LsHc.update( param_LsHc )
            setup_LsHc  = setup.sysClone(parameters=params_LsHc)

            estimate = DataObservation(name="Data", process=setup.processes["Data"], cacheDir=setup.defaultCacheDir())

            estimate.initCache(setup_LsHc.defaultCacheDir())
            data_LsHc = estimate.cachedEstimate( region, channel, setup_LsHc, overwrite=overwrite )

            mcPrompt_LsHc = u_float(0)

            if addSF:
                if setup.nJet == "2":
                    DYSF_val    = DY2SF_val
                    WGSF_val    = WG2SF_val
                    ZGSF_val    = ZG2SF_val
                    QCDSF_val   = QCD2SF_val
                elif setup.nJet == "3":
                    DYSF_val    = DY3SF_val
                    WGSF_val    = WG3SF_val
                    ZGSF_val    = ZG3SF_val
                    QCDSF_val   = QCD3SF_val
                elif setup.nJet == "4":
                    DYSF_val    = DY4SF_val
                    WGSF_val    = WG4SF_val
                    ZGSF_val    = ZG4SF_val
                    QCDSF_val   = QCD4SF_val
                elif setup.nJet == "5":
                    DYSF_val    = DY5SF_val
                    WGSF_val    = WG5SF_val
                    ZGSF_val    = ZG5SF_val
                    QCDSF_val   = QCD5SF_val
                elif setup.nJet == "2p":
                    DYSF_val    = DY2pSF_val
                    WGSF_val    = WG2pSF_val
                    ZGSF_val    = ZG2pSF_val
                    QCDSF_val   = QCD2pSF_val
                elif setup.nJet == "3p":
                    DYSF_val    = DY3pSF_val
                    WGSF_val    = WG3pSF_val
                    ZGSF_val    = ZG3pSF_val
                    QCDSF_val   = QCD3pSF_val
                elif setup.nJet == "4p":
                    DYSF_val    = DY4pSF_val
                    WGSF_val    = WG4pSF_val
                    ZGSF_val    = ZG4pSF_val
                    QCDSF_val   = QCD4pSF_val

            for s in default_photonSampleList:
                if s in ["QCD-DD", "QCD", "GJets", "Data", "fakes-DD"]: continue
                if "had" in s: continue

                # get the MC based Estimate for fakes in the region
                estimate = MCBasedEstimate( name=s, process=setup.processes[s] )
                estimate.initCache(setup.defaultCacheDir())

                y_LsHc = estimate.cachedEstimate( region, channel, setup_LsHc, overwrite=overwrite )

                if addSF:
                    if "DY_LO" in s:    y_LsHc *= DYSF_val[setup.year].val #add DY SF
#                    elif "WJets" in s:  y_LsHc *= WJetsSF_val[setup.year].val #add WJets SF
                    elif "TTG" in s:    y_LsHc *= SSMSF_val[setup.year].val #add TTG SF
                    elif "ZG" in s:     y_LsHc *= ZGSF_val[setup.year].val #add ZGamma SF
                    elif "WG" in s:     y_LsHc *= WGSF_val[setup.year].val #add WGamma SF

                mcPrompt_LsHc += y_LsHc

            # check if any of the factors would be <= 0 to safe time:
            if data_LsHc - mcPrompt_LsHc <= 0: return u_float(0)

            # Add QCD to Prompt, make sure you run on the semilep skim
            estimate = DataDrivenQCDEstimate( name="QCD-DD" )
            estimate.initCache(setup.defaultCacheDir())

            setup_noSys_LsHc = Setup( year=setup.year, photonSelection=False )
            setup_noSys_LsHc = setup_noSys_LsHc.sysClone( parameters=setup.parameters )
            setup_noSys_LsHc = setup_noSys_LsHc.sysClone( parameters=params_LsHc )

            y_QCD_LsHc     = estimate.cachedEstimate( region, channel, setup_noSys_LsHc, overwrite=False )
            y_QCD_LsHc    *= QCDSF_val[setup.year].val
            mcPrompt_LsHc += y_QCD_LsHc.val

            # create the data-driven factor
            dataHad_LsHc = data_LsHc-mcPrompt_LsHc

            return dataHad_LsHc if dataHad_LsHc > 0 else u_float(0)


    def _kappaMC(self, region, channel, setup, overwrite=False):

            param_LsLc = { "addMisIDSF":addSF }
            param_LsHc = { "photonIso":"highChgIso",          "addMisIDSF":addSF }
            param_HsLc = { "photonIso":"highSieie",           "addMisIDSF":addSF }
            param_HsHc = { "photonIso":"highChgIsohighSieie", "addMisIDSF":addSF }

            params_LsLc = copy.deepcopy(setup.parameters)
            params_LsHc = copy.deepcopy(setup.parameters)
            params_HsLc = copy.deepcopy(setup.parameters)
            params_HsHc = copy.deepcopy(setup.parameters)

            params_LsLc.update( param_LsLc )
            params_LsHc.update( param_LsHc )
            params_HsLc.update( param_HsLc )
            params_HsHc.update( param_HsHc )

            setup_LsLc = setup.sysClone(parameters=params_LsLc)
            setup_LsHc = setup.sysClone(parameters=params_LsHc)
            setup_HsLc = setup.sysClone(parameters=params_HsLc)
            setup_HsHc = setup.sysClone(parameters=params_HsHc)

            mcHad_LsLc = u_float(0)
            mcHad_LsHc = u_float(0)
            mcHad_HsLc = u_float(0)
            mcHad_HsHc = u_float(0)

            if addSF:
                if setup.nJet == "2":
                    DYSF_val    = DY2SF_val
                    WGSF_val    = WG2SF_val
                    ZGSF_val    = ZG2SF_val
                    QCDSF_val   = QCD2SF_val
                elif setup.nJet == "3":
                    DYSF_val    = DY3SF_val
                    WGSF_val    = WG3SF_val
                    ZGSF_val    = ZG3SF_val
                    QCDSF_val   = QCD3SF_val
                elif setup.nJet == "4":
                    DYSF_val    = DY4SF_val
                    WGSF_val    = WG4SF_val
                    ZGSF_val    = ZG4SF_val
                    QCDSF_val   = QCD4SF_val
                elif setup.nJet == "5":
                    DYSF_val    = DY5SF_val
                    WGSF_val    = WG5SF_val
                    ZGSF_val    = ZG5SF_val
                    QCDSF_val   = QCD5SF_val
                elif setup.nJet == "2p":
                    DYSF_val    = DY2pSF_val
                    WGSF_val    = WG2pSF_val
                    ZGSF_val    = ZG2pSF_val
                    QCDSF_val   = QCD2pSF_val
                elif setup.nJet == "3p":
                    DYSF_val    = DY3pSF_val
                    WGSF_val    = WG3pSF_val
                    ZGSF_val    = ZG3pSF_val
                    QCDSF_val   = QCD3pSF_val
                elif setup.nJet == "4p":
                    DYSF_val    = DY4pSF_val
                    WGSF_val    = WG4pSF_val
                    ZGSF_val    = ZG4pSF_val
                    QCDSF_val   = QCD4pSF_val

            for s in default_photonSampleList:
                if s in ["QCD-DD", "QCD", "GJets", "Data", "fakes-DD"]: continue
                if not "had" in s: continue

                # get the MC based Estimate for fakes in the region
                estimate = MCBasedEstimate( name=s, process=setup.processes[s] )
                estimate.initCache(setup.defaultCacheDir())

                y_LsLc = estimate.cachedEstimate( region, channel, setup_LsLc, overwrite=overwrite )
                y_LsHc = estimate.cachedEstimate( region, channel, setup_LsHc, overwrite=overwrite )
                y_HsLc = estimate.cachedEstimate( region, channel, setup_HsLc, overwrite=overwrite )
                y_HsHc = estimate.cachedEstimate( region, channel, setup_HsHc, overwrite=overwrite )

                if addSF:
                    if "DY_LO" in s:
                        y_LsLc *= DYSF_val[setup.year].val #add DY SF
                        y_LsHc *= DYSF_val[setup.year].val #add DY SF
                        y_HsLc *= DYSF_val[setup.year].val #add DY SF
                        y_HsHc *= DYSF_val[setup.year].val #add DY SF
#                    elif "WJets" in s:
#                        y_LsLc *= WJetsSF_val[setup.year].val #add WJets SF
#                        y_LsHc *= WJetsSF_val[setup.year].val #add WJets SF
#                        y_HsLc *= WJetsSF_val[setup.year].val #add WJets SF
#                        y_HsHc *= WJetsSF_val[setup.year].val #add WJets SF
                    elif "TTG" in s:
                        y_LsLc *= SSMSF_val[setup.year].val #add TTG SF
                        y_LsHc *= SSMSF_val[setup.year].val #add TTG SF
                        y_HsLc *= SSMSF_val[setup.year].val #add TTG SF
                        y_HsHc *= SSMSF_val[setup.year].val #add TTG SF
                    elif "ZG" in s:
                        y_LsLc *= ZGSF_val[setup.year].val #add ZGamma SF
                        y_LsHc *= ZGSF_val[setup.year].val #add ZGamma SF
                        y_HsLc *= ZGSF_val[setup.year].val #add ZGamma SF
                        y_HsHc *= ZGSF_val[setup.year].val #add ZGamma SF
                    elif "WG" in s:
                        y_LsLc *= WGSF_val[setup.year].val #add WGamma SF
                        y_LsHc *= WGSF_val[setup.year].val #add WGamma SF
                        y_HsLc *= WGSF_val[setup.year].val #add WGamma SF
                        y_HsHc *= WGSF_val[setup.year].val #add WGamma SF

                mcHad_LsLc += y_LsLc
                mcHad_LsHc += y_LsHc
                mcHad_HsLc += y_HsLc
                mcHad_HsHc += y_HsHc

            # check if any of the factors would be <= 0 to safe time:
            if mcHad_LsLc <= 0: return u_float(0)
            if mcHad_LsHc <= 0: return u_float(0)
            if mcHad_HsLc <= 0: return u_float(0)
            if mcHad_HsHc <= 0: return u_float(0)

            # create the data-driven factor
            mcRatio_Ls   = mcHad_LsLc / mcHad_LsHc
            mcRatio_Hs   = mcHad_HsLc / mcHad_HsHc

            return mcRatio_Ls / mcRatio_Hs


    def _fakesMC(self, region, channel, setup, overwrite=False):

            param_LsLc  = { "addMisIDSF":addSF }
            params_LsLc = copy.deepcopy(setup.parameters)
            params_LsLc.update( param_LsLc )
            setup_LsLc  = setup.sysClone(parameters=params_LsLc)

            mcHad_LsLc  = u_float(0)

            if addSF:
                if setup.nJet == "2":
                    DYSF_val    = DY2SF_val
                    WGSF_val    = WG2SF_val
                    ZGSF_val    = ZG2SF_val
                    QCDSF_val   = QCD2SF_val
                elif setup.nJet == "3":
                    DYSF_val    = DY3SF_val
                    WGSF_val    = WG3SF_val
                    ZGSF_val    = ZG3SF_val
                    QCDSF_val   = QCD3SF_val
                elif setup.nJet == "4":
                    DYSF_val    = DY4SF_val
                    WGSF_val    = WG4SF_val
                    ZGSF_val    = ZG4SF_val
                    QCDSF_val   = QCD4SF_val
                elif setup.nJet == "5":
                    DYSF_val    = DY5SF_val
                    WGSF_val    = WG5SF_val
                    ZGSF_val    = ZG5SF_val
                    QCDSF_val   = QCD5SF_val
                elif setup.nJet == "2p":
                    DYSF_val    = DY2pSF_val
                    WGSF_val    = WG2pSF_val
                    ZGSF_val    = ZG2pSF_val
                    QCDSF_val   = QCD2pSF_val
                elif setup.nJet == "3p":
                    DYSF_val    = DY3pSF_val
                    WGSF_val    = WG3pSF_val
                    ZGSF_val    = ZG3pSF_val
                    QCDSF_val   = QCD3pSF_val
                elif setup.nJet == "4p":
                    DYSF_val    = DY4pSF_val
                    WGSF_val    = WG4pSF_val
                    ZGSF_val    = ZG4pSF_val
                    QCDSF_val   = QCD4pSF_val

            for s in default_photonSampleList:
                if s in ["QCD-DD", "QCD", "GJets", "Data", "fakes-DD"]: continue
                if not "had" in s: continue

                # get the MC based Estimate for fakes in the region
                estimate = MCBasedEstimate( name=s, process=setup.processes[s] )
                estimate.initCache(setup.defaultCacheDir())

                y_LsLc = estimate.cachedEstimate( region, channel, setup_LsLc, overwrite=overwrite )

                if addSF:
                    if "DY_LO" in s:    y_LsLc *= DYSF_val[setup.year].val #add DY SF
#                    elif "WJets" in s:  y_LsLc *= WJetsSF_val[setup.year].val #add WJets SF
                    elif "TTG" in s:    y_LsLc *= SSMSF_val[setup.year].val #add TTG SF
                    elif "ZG" in s:     y_LsLc *= ZGSF_val[setup.year].val #add ZGamma SF
                    elif "WG" in s:     y_LsLc *= WGSF_val[setup.year].val #add WGamma SF

                mcHad_LsLc += y_LsLc

            if mcHad_LsLc <= 0: return u_float(0)
            return mcHad_LsLc


if __name__ == "__main__":
    from TTGammaEFT.Analysis.regions      import regionsTTG, noPhotonRegionTTG, inclRegionsTTG
    from TTGammaEFT.Analysis.SetupHelpers import allRegions
    from TTGammaEFT.Analysis.Setup        import Setup

    overwrite = False
    print "incl"

    setup = Setup(year=2016, photonSelection=False)
#    setup = setup.sysClone(parameters=allRegions["SR2"]["parameters"])
    setup = setup.sysClone(parameters=allRegions["SR4p"]["parameters"])

    estimate = DataDrivenFakeEstimate( "Top_had", process=setup.processes["Top_had"] )    
    estimate.initCache(setup.defaultCacheDir())

    print "e", "fake", estimate._estimate( allRegions["SR4p"]["regions"][0], "e", setup, overwrite=overwrite )


