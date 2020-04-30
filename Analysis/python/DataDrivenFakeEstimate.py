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
    def __init__(self, name, process, cacheDir=None):
        super(DataDrivenFakeEstimate, self).__init__(name, cacheDir=cacheDir)
        self.process = process
    #Concrete implementation of abstract method "estimate" as defined in Systematic
    def _estimate(self, region, channel, setup, signalAddon=None, overwrite=False):

        #Sum of all channels for "all"
        if channel == "all":
            return sum([ self.cachedEstimate(region, c, setup, signalAddon=signalAddon) for c in lepChannels])

        elif channel == "SFtight":
            return sum([ self.cachedEstimate(region, c, setup, signalAddon=signalAddon) for c in dilepChannels])

        else:

            # get the MC based Estimate for fakes in the region including systematic uncertainties
            estimate = MCBasedEstimate( name=self.name, process=self.process )
            estimate.initCache(setup.defaultCacheDir())
            mc_LsLc  = estimate.cachedEstimate( region, channel, setup, overwrite=overwrite )

            if mc_LsLc <= 0: return u_float(0)

            # MC based fake estimate in CR
            if not setup.isSignalRegion: return mc_LsLc

            # get the ddFakeCorrection for the nominal setup, not the reweighted
            setup_noSys = Setup( year=setup.year, photonSelection=False )
            setup_noSys = setup_noSys.sysClone( parameters=setup.parameters )
            ddFakeCorrection = self.cachedFakeFactor(region, channel, setup_noSys, overwrite=False).val

            # take MC based fakes if the dd-SF is 0
            if not ddFakeCorrection: return mc_LsLc

            # DD fake estimate in SR
            return mc_LsLc * ddFakeCorrection


    def _dataDrivenFakeCorrectionFactor(self, region, channel, setup, overwrite=False):

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

            param_LsHc = { "photonIso":"highChgIso",          "addMisIDSF":addSF }
            param_HsLc = { "photonIso":"highSieie",           "addMisIDSF":addSF }
            param_HsHc = { "photonIso":"highChgIsohighSieie", "addMisIDSF":addSF }

            params_LsHc = copy.deepcopy(setup.parameters)
            params_HsLc = copy.deepcopy(setup.parameters)
            params_HsHc = copy.deepcopy(setup.parameters)

            params_LsHc.update( param_LsHc )
            params_HsLc.update( param_HsLc )
            params_HsHc.update( param_HsHc )

#            estimators = EstimatorList( setup )

            setup_LsHc = setup.sysClone(parameters=params_LsHc)
            setup_HsLc = setup.sysClone(parameters=params_HsLc)
            setup_HsHc = setup.sysClone(parameters=params_HsHc)

            # sum MC for Prompt and hadronic in (A)BCD regions
            # get data in the BCD regions
            # get the MC based Estimate for fakes in the region
            estimate = DataObservation(name="Data", process=setup.processes["Data"], cacheDir=setup.defaultCacheDir())
            estimate.initCache(setup_LsHc.defaultCacheDir())
            data_LsHc = estimate.cachedEstimate( region, channel, setup_LsHc, overwrite=overwrite )
            print "data", "LsHc", data_LsHc
            estimate.initCache(setup_HsLc.defaultCacheDir())
            data_HsLc = estimate.cachedEstimate( region, channel, setup_HsLc, overwrite=overwrite )
            print "data", "HsLc", data_HsLc
            estimate.initCache(setup_HsHc.defaultCacheDir())
            data_HsHc = estimate.cachedEstimate( region, channel, setup_HsHc, overwrite=overwrite )
            print "data", "HsHc", data_HsHc

            mcPrompt_LsHc = u_float(0)
            mcPrompt_HsLc = u_float(0)
            mcPrompt_HsHc = u_float(0)

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
                if s in ["QCD-DD", "QCD", "GJets", "Data"]: continue

                # get the MC based Estimate for fakes in the region
                estimate = MCBasedEstimate( name=s, process=setup.processes[s] )
                estimate.initCache(setup.defaultCacheDir())

                y_LsHc = estimate.cachedEstimate( region, channel, setup_LsHc, overwrite=overwrite )
                y_HsLc = estimate.cachedEstimate( region, channel, setup_HsLc, overwrite=overwrite )
                y_HsHc = estimate.cachedEstimate( region, channel, setup_HsHc, overwrite=overwrite )

                if addSF:
                    if "DY_LO" in s:
                        y_LsHc *= DYSF_val[setup.year] #add DY SF
                        y_HsLc *= DYSF_val[setup.year] #add DY SF
                        y_HsHc *= DYSF_val[setup.year] #add DY SF
                    elif "WJets" in s:
                        y_LsHc *= WJetsSF_val[setup.year] #add WJets SF
                        y_HsLc *= WJetsSF_val[setup.year] #add WJets SF
                        y_HsHc *= WJetsSF_val[setup.year] #add WJets SF
                    elif "TT_pow" in s:
                        y_LsHc *= TTSF_val[setup.year] #add TT SF
                        y_HsLc *= TTSF_val[setup.year] #add TT SF
                        y_HsHc *= TTSF_val[setup.year] #add TT SF
                    elif "TTG" in s:
                        y_LsHc *= SSMSF_val[setup.year] #add TTG SF
                        y_HsLc *= SSMSF_val[setup.year] #add TTG SF
                        y_HsHc *= SSMSF_val[setup.year] #add TTG SF
                    elif "ZG" in s:
                        y_LsHc *= ZGSF_val[setup.year] #add ZGamma SF
                        y_HsLc *= ZGSF_val[setup.year] #add ZGamma SF
                        y_HsHc *= ZGSF_val[setup.year] #add ZGamma SF
                    elif "WG" in s:
                        y_LsHc *= WGSF_val[setup.year] #add WGamma SF
                        y_HsLc *= WGSF_val[setup.year] #add WGamma SF
                        y_HsHc *= WGSF_val[setup.year] #add WGamma SF

                if "had" in s:
                    mcHad_LsHc += y_LsHc
                    mcHad_HsLc += y_HsLc
                    mcHad_HsHc += y_HsHc
                else:
                    mcPrompt_LsHc += y_LsHc
                    mcPrompt_HsLc += y_HsLc
                    mcPrompt_HsHc += y_HsHc

            # check if any of the factors would be <= 0 to safe time:
            if data_LsHc - mcPrompt_LsHc <= 0: return u_float(0)
            if data_HsLc - mcPrompt_HsLc <= 0: return u_float(0)
            if data_HsHc - mcPrompt_HsHc <= 0: return u_float(0)

            if mcHad_LsHc <= 0: return u_float(0)
            if mcHad_HsLc <= 0: return u_float(0)
            if mcHad_HsHc <= 0: return u_float(0)

            # Add QCD to Prompt, make sure you run on the semilep skim
            estimate = DataDrivenQCDEstimate( name="QCD-DD" )
            estimate.initCache(setup.defaultCacheDir())

            y_QCD_LsHc     = estimate.cachedEstimate( region, channel, setup_LsHc, overwrite=overwrite )
            y_QCD_LsHc    *= QCDSF_val[setup.year]
            mcPrompt_LsHc += y_QCD_LsHc

            y_QCD_HsLc     = estimate.cachedEstimate( region, channel, setup_HsLc, overwrite=overwrite )
            y_QCD_HsLc    *= QCDSF_val[setup.year]
            mcPrompt_HsLc += y_QCD_HsLc

            y_QCD_HsHc     = estimate.cachedEstimate( region, channel, setup_HsHc, overwrite=overwrite )
            y_QCD_HsHc    *= QCDSF_val[setup.year]
            mcPrompt_HsHc += y_QCD_HsHc

            # create the data-driven factor
            dataHad_LsHc = data_LsHc-mcPrompt_LsHc
            dataHad_HsLc = data_HsLc-mcPrompt_HsLc
            dataHad_HsHc = data_HsHc-mcPrompt_HsHc
            mcRatio_Hs   = mcHad_HsHc / mcHad_HsLc

            return dataHad_LsHc * (dataHad_HsLc / dataHad_HsHc) * mcRatio_Hs / mcHad_LsHc


if __name__ == "__main__":
    from TTGammaEFT.Analysis.regions      import regionsTTG, noPhotonRegionTTG, inclRegionsTTG
    from TTGammaEFT.Analysis.SetupHelpers import allRegions
    from TTGammaEFT.Analysis.Setup        import Setup

    overwrite = False
    print "incl"

    setup = Setup(year=2016, photonSelection=False)
#    setup = setup.sysClone(parameters=allRegions["SR2"]["parameters"])
    setup = setup.sysClone(parameters=allRegions["SR4p"]["parameters"])

    estimate = DataDrivenFakeEstimate( "TT_pow_had", process=setup.processes["TT_pow_had"] )    
    estimate.initCache(setup.defaultCacheDir())

    print "e", "fake", estimate._estimate( allRegions["SR4p"]["regions"][0], "e", setup, overwrite=overwrite )


