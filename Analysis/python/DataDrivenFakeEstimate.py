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
    def __init__(self, name, cacheDir=None, expected=False):
        super(DataDrivenFakeEstimate, self).__init__(name, cacheDir=cacheDir)
        self.expected = expected
    #Concrete implementation of abstract method "estimate" as defined in Systematic
    def _estimate(self, region, channel, setup, signalAddon=None, overwrite=False):

        if setup.nJet == "3p":
            setup4p = setup.sysClone( parameters={"nJet":(4,-1)} )
            setup3 = setup.sysClone( parameters={"nJet":(3,3)} )
            return sum([ self.cachedEstimate(region, channel, s, signalAddon=signalAddon, overwrite=overwrite) for s in [setup3,setup4p]])

        #Sum of all channels for "all"
        if channel == "all":
            return sum([ self.cachedEstimate(region, c, setup, signalAddon=signalAddon, overwrite=overwrite) for c in lepChannels])

        elif channel == "SFtight":
            return sum([ self.cachedEstimate(region, c, setup, signalAddon=signalAddon, overwrite=overwrite) for c in dilepChannels])

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
            return self._dataDrivenFakes( region, channel, setup, overwrite=overwrite)

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

            # no shape correction if 0
            kappaMC   = self._kappaMC(region, channel, setup, overwrite=overwrite)
            if kappaMC <= 0: kappaMC = u_float(1)

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

            if self.expected:
#                estimate = MCBasedEstimate( name="all_mc_e" if channel == "e" else "all_mc_mu", process=setup.processes["all_mc_e" if channel == "e" else "all_mc_mu"] )
                estimate = MCBasedEstimate( name="all_noQCD", process=setup.processes["all_noQCD"] )
            else:
                estimate = DataObservation(name="Data", process=setup.processes["Data"])

            data_HsLc = estimate.cachedEstimate( region, channel, setup_HsLc, overwrite=overwrite )
            data_HsHc = estimate.cachedEstimate( region, channel, setup_HsHc, overwrite=overwrite )

            # get the MC based Estimate for fakes in the region
#            estimate = MCBasedEstimate( name="all_mc_e_prompt" if channel == "e" else "all_mc_mu_prompt", process=setup.processes["all_mc_e_prompt" if channel == "e" else "all_mc_mu_prompt"] )
            estimate = MCBasedEstimate( name="all_noQCD_prompt", process=setup.processes["all_noQCD_prompt"] )

            mcPrompt_HsLc = estimate.cachedEstimate( region, channel, setup_HsLc, overwrite=overwrite )
            print "prompt hslc", mcPrompt_HsLc
            mcPrompt_HsHc = estimate.cachedEstimate( region, channel, setup_HsHc, overwrite=overwrite )
            print "prompt hshc", mcPrompt_HsHc

            dataHad_HsHc = data_HsHc-mcPrompt_HsHc
            if dataHad_HsHc <= 0: return u_float(0)

            dataHad_HsLc = data_HsLc-mcPrompt_HsLc
            if dataHad_HsLc <= 0: dataHad_HsLc = u_float(.1,.1)

            return dataHad_HsLc / dataHad_HsHc


    def _fakesData(self, region, channel, setup, overwrite=False):

            param_LsHc  = { "photonIso":"highChgIso",          "addMisIDSF":addSF }
            params_LsHc = copy.deepcopy(setup.parameters)
            params_LsHc.update( param_LsHc )
            setup_LsHc  = setup.sysClone(parameters=params_LsHc)

            if self.expected:
#                estimate = MCBasedEstimate( name="all_mc_e" if channel == "e" else "all_mc_mu", process=setup.processes["all_mc_e" if channel == "e" else "all_mc_mu"] )
                estimate = MCBasedEstimate( name="all_noQCD", process=setup.processes["all_noQCD"] )
            else:
                estimate = DataObservation(name="Data", process=setup.processes["Data"])

            data_LsHc = estimate.cachedEstimate( region, channel, setup_LsHc, overwrite=overwrite )

#            estimate = MCBasedEstimate( name="all_mc_e_prompt" if channel == "e" else "all_mc_mu_prompt", process=setup.processes["all_mc_e_prompt" if channel == "e" else "all_mc_mu_prompt"] )
            estimate = MCBasedEstimate( name="all_noQCD_prompt", process=setup.processes["all_noQCD_prompt"] )

            mcPrompt_LsHc = estimate.cachedEstimate( region, channel, setup_LsHc, overwrite=overwrite )
            print "prompt lshc", mcPrompt_LsHc

            dataHad_LsHc = data_LsHc-mcPrompt_LsHc

            return dataHad_LsHc if dataHad_LsHc > 0 else u_float(.1,.1)


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

#            estimate = MCBasedEstimate( name="all_mc_e_had" if channel == "e" else "all_mc_mu_had", process=setup.processes["all_mc_e_had" if channel == "e" else "all_mc_mu_had"] )
            estimate = MCBasedEstimate( name="all_noQCD_had", process=setup.processes["all_noQCD_had"] )

            mcHad_LsLc = estimate.cachedEstimate( region, channel, setup_LsLc, overwrite=overwrite )
            mcHad_LsHc = estimate.cachedEstimate( region, channel, setup_LsHc, overwrite=overwrite )
            mcHad_HsLc = estimate.cachedEstimate( region, channel, setup_HsLc, overwrite=overwrite )
            mcHad_HsHc = estimate.cachedEstimate( region, channel, setup_HsHc, overwrite=overwrite )
            print "had", mcHad_LsLc, mcHad_LsHc, mcHad_HsLc, mcHad_HsHc

            # no shape correction if any component is 0
            if mcHad_LsLc <= 0: return u_float(1)
            if mcHad_LsHc <= 0: return u_float(1)
            if mcHad_HsLc <= 0: return u_float(1)
            if mcHad_HsHc <= 0: return u_float(1)

            # create the data-driven factor
            mcRatio_Ls   = mcHad_LsLc / mcHad_LsHc
            mcRatio_Hs   = mcHad_HsLc / mcHad_HsHc

            return mcRatio_Ls / mcRatio_Hs


    def _fakesMC(self, region, channel, setup, overwrite=False):

            param_LsLc  = { "addMisIDSF":addSF }
            params_LsLc = copy.deepcopy(setup.parameters)
            params_LsLc.update( param_LsLc )
            setup_LsLc  = setup.sysClone(parameters=params_LsLc)

            estimate = MCBasedEstimate( name="all_mc_e_had" if channel == "e" else "all_mc_mu_had", process=setup.processes["all_mc_e_had" if channel == "e" else "all_mc_mu_had"] )
#            estimate = MCBasedEstimate( name="all_noQCD_had", process=setup.processes["all_noQCD_had"] )

            mcHad_LsLc = estimate.cachedEstimate( region, channel, setup_LsLc, overwrite=overwrite )

            if mcHad_LsLc <= 0: return u_float(0)
            return mcHad_LsLc


if __name__ == "__main__":
    from TTGammaEFT.Analysis.regions      import regionsTTG, noPhotonRegionTTG, inclRegionsTTG
    from TTGammaEFT.Analysis.SetupHelpers import allRegions
    from TTGammaEFT.Analysis.Setup        import Setup

    overwrite = False
    print "incl"

    setup = Setup(year=2016, photonSelection=True)
#    setup = setup.sysClone(parameters=allRegions["SR2"]["parameters"])
    setup = setup.sysClone(parameters=allRegions["SR4p"]["parameters"])

    estimate = DataDrivenFakeEstimate( "Top_had", process=setup.processes["Top_had"] )    
    estimate.initCache(setup.defaultCacheDir())

    print "e", "fake", estimate._estimate( allRegions["SR4p"]["regions"][0], "e", setup, overwrite=overwrite )


