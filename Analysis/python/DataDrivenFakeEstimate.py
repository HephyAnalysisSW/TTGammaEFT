import os, sys
import ROOT
ROOT.gROOT.SetBatch(True)
from math import sqrt

from TTGammaEFT.Analysis.MCBasedEstimate     import MCBasedEstimate
from TTGammaEFT.Analysis.SystematicEstimator import SystematicEstimator
from TTGammaEFT.Analysis.EstimatorList       import EstimatorList
from TTGammaEFT.Analysis.SetupHelpers        import *
from TTGammaEFT.Analysis.Setup               import Setup
from TTGammaEFT.Analysis.DataObservation     import DataObservation

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

addSF = True

class DataDrivenFakeEstimate(SystematicEstimator):
    def __init__(self, name, process, cacheDir=None):
        super(DataDrivenFakeEstimate, self).__init__(name, cacheDir=cacheDir)
        self.process = process

    #Concrete implementation of abstract method "estimate" as defined in Systematic
    def _estimate(self, region, channel, setup, signalAddon=None, overwrite=False):

        #Sum of all channels for "all"
        if channel=="all":
            estimate     = sum([ self.cachedEstimate(region, c, setup, signalAddon=signalAddon) for c in lepChannels])

        elif channel=="SFtight":
            estimate     = sum([ self.cachedEstimate(region, c, setup, signalAddon=signalAddon) for c in dilepChannels])

        else:

            print region.cutString()
            # get the MC based Estimate for fakes in the region including systematic uncertainties
            estimators = EstimatorList( setup, processes=[self.name] )
            estimate   = getattr( estimators, self.name )
            estimate.initCache(setup.defaultCacheDir())
            mc_LsLc    = estimate.cachedEstimate( region, channel, setup, overwrite=overwrite )
            if mc_LsLc <= 0: return u_float(0)

            # MC based fake estimate in CR
            if not setup.isSignalRegion: return mc_LsLc

#            selection_MC_LsLc = setup.selection("MC", channel=channel )
#            weight_MC_LsLc    = selection_MC_LsLc["weightStr"]
#            selection_MC_LsLc = selection_MC_LsLc["cut"]
#            mc_LsLc           = self.yieldFromCache(setup, self.name, channel, selection_MC_LsLc, weight_MC_LsLc, overwrite=overwrite)*setup.dataLumi/1000.
#            if mc_LsLc <= 0: return u_float(0)

#            mcHad = u_float(0)
#            for s in default_photonSampleList:
#                if not "had" in s: continue
#                if s in ["QCD-DD", "QCD", "GJets", "Data"]: continue
#                mcHad += self.yieldFromCache(setup, s, channel, selection_MC_LsLc, weight_MC_LsLc, overwrite=overwrite)
#            mcHad *= setup.dataLumi/1000.

            # get a data-driven fake estimate for all fakes, then scale it according to the mc fraction
            print mc_LsLc
            kappa = self.cachedFakeFactor(region, channel, setup, overwrite=overwrite).val
            print kappa
            return mc_LsLc * kappa


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

#            params_LsLc = copy.deepcopy(setup.parameters)
            params_LsHc = copy.deepcopy(setup.parameters)
            params_HsLc = copy.deepcopy(setup.parameters)
            params_HsHc = copy.deepcopy(setup.parameters)

            params_LsHc.update( param_LsHc )
            params_HsLc.update( param_HsLc )
            params_HsHc.update( param_HsHc )

#            selection_MC_LsLc   = setup.selection("MC",   channel=channel )
#            selection_MC_HsHc   = setup.selection("MC",   channel=channel, **setup.defaultParameters( update=param_HsHc ))
#            selection_Data_HsHc = setup.selection("Data", channel=channel, **setup.defaultParameters( update=param_HsHc ))
#            selection_MC_HsLc   = setup.selection("MC",   channel=channel, **setup.defaultParameters( update=param_HsLc ))
#            selection_Data_HsLc = setup.selection("Data", channel=channel, **setup.defaultParameters( update=param_HsLc ))
#            selection_MC_LsHc   = setup.selection("MC",   channel=channel, **setup.defaultParameters( update=param_LsHc ))
#            selection_Data_LsHc = setup.selection("Data", channel=channel, **setup.defaultParameters( update=param_LsHc ))

#            weight_Data_HsHc = selection_Data_HsHc["weightStr"]
#            weight_Data_HsLc = selection_Data_HsLc["weightStr"]
#            weight_Data_LsHc = selection_Data_LsHc["weightStr"]
#            weight_MC_HsHc   = selection_MC_HsHc["weightStr"]
#            weight_MC_HsLc   = selection_MC_HsLc["weightStr"]
#            weight_MC_LsHc   = selection_MC_LsHc["weightStr"]
#            weight_MC_LsLc   = selection_MC_LsLc["weightStr"]

#            selection_MC_LsLc   = selection_MC_LsLc["cut"]
#            selection_MC_HsHc   = selection_MC_HsHc["cut"]
#            selection_Data_HsHc = selection_Data_HsHc["cut"]
#            selection_MC_HsLc   = selection_MC_HsLc["cut"]
#            selection_Data_HsLc = selection_Data_HsLc["cut"]
#            selection_MC_LsHc   = selection_MC_LsHc["cut"]
#            selection_Data_LsHc = selection_Data_LsHc["cut"]

            estimators = EstimatorList( setup )

#            setup_LsLc = setup.sysClone(parameters=params_LsLc)
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

#            data_LsHc = self.yieldFromCache(setup, "Data", channel, selection_Data_LsHc, weight_Data_LsHc, overwrite=overwrite)*setup.dataLumi/1000.
#            data_HsLc = self.yieldFromCache(setup, "Data", channel, selection_Data_HsLc, weight_Data_HsLc, overwrite=overwrite)*setup.dataLumi/1000.
#            data_HsHc = self.yieldFromCache(setup, "Data", channel, selection_Data_HsHc, weight_Data_HsHc, overwrite=overwrite)*setup.dataLumi/1000.

            mcPrompt_LsHc = u_float(0)
            mcPrompt_HsLc = u_float(0)
            mcPrompt_HsHc = u_float(0)

#            mcHad_LsLc = u_float(0)
            mcHad_LsHc = u_float(0)
            mcHad_HsLc = u_float(0)
            mcHad_HsHc = u_float(0)

            for s in default_photonSampleList:
                if s in ["QCD-DD", "QCD", "GJets", "Data"]: continue

                # get the MC based Estimate for fakes in the region
                estimate        = getattr( estimators, s )
                estimate.isData = False
                estimate.initCache(setup.defaultCacheDir())

#                y_LsLc = estimate.cachedEstimate( region, channel, setup_LsLc, overwrite=overwrite )
#                print s, "LsLc", y_LsLc
                y_LsHc = estimate.cachedEstimate( region, channel, setup_LsHc, overwrite=overwrite )
                print s, "LsHc", y_LsHc
                y_HsLc = estimate.cachedEstimate( region, channel, setup_HsLc, overwrite=overwrite )
                print s, "HsLc", y_HsLc
                y_HsHc = estimate.cachedEstimate( region, channel, setup_HsHc, overwrite=overwrite )
                print s, "HsHc", y_HsHc
                print

#                y_LsLc = self.yieldFromCache(setup, s, channel, selection_MC_LsLc, weight_MC_LsLc, overwrite=overwrite) if "had" in s else u_float(0)
#                y_LsHc = self.yieldFromCache(setup, s, channel, selection_MC_LsHc, weight_MC_LsHc, overwrite=overwrite)
#                y_HsLc = self.yieldFromCache(setup, s, channel, selection_MC_HsLc, weight_MC_HsLc, overwrite=overwrite)
#                y_HsHc = self.yieldFromCache(setup, s, channel, selection_MC_HsHc, weight_MC_HsHc, overwrite=overwrite)

                if addSF:
                    if "DY_LO" in s:
#                        y_LsLc *= DYSF_val[setup.year] #add DY SF
                        y_LsHc *= DYSF_val[setup.year] #add DY SF
                        y_HsLc *= DYSF_val[setup.year] #add DY SF
                        y_HsHc *= DYSF_val[setup.year] #add DY SF
                    elif "WJets" in s:
#                        y_LsLc *= WJetsSF_val[setup.year] #add WJets SF
                        y_LsHc *= WJetsSF_val[setup.year] #add WJets SF
                        y_HsLc *= WJetsSF_val[setup.year] #add WJets SF
                        y_HsHc *= WJetsSF_val[setup.year] #add WJets SF
                    elif "TT_pow" in s:
#                        y_LsLc *= TTSF_val[setup.year] #add TT SF
                        y_LsHc *= TTSF_val[setup.year] #add TT SF
                        y_HsLc *= TTSF_val[setup.year] #add TT SF
                        y_HsHc *= TTSF_val[setup.year] #add TT SF
                    elif "TTG" in s:
#                        y_LsLc *= SSMSF_val[setup.year] #add TTG SF
                        y_LsHc *= SSMSF_val[setup.year] #add TTG SF
                        y_HsLc *= SSMSF_val[setup.year] #add TTG SF
                        y_HsHc *= SSMSF_val[setup.year] #add TTG SF
                    elif "ZG" in s:
#                        y_LsLc *= ZGSF_val[setup.year] #add ZGamma SF
                        y_LsHc *= ZGSF_val[setup.year] #add ZGamma SF
                        y_HsLc *= ZGSF_val[setup.year] #add ZGamma SF
                        y_HsHc *= ZGSF_val[setup.year] #add ZGamma SF
                    elif "WG" in s:
#                        y_LsLc *= WGSF_val[setup.year] #add WGamma SF
                        y_LsHc *= WGSF_val[setup.year] #add WGamma SF
                        y_HsLc *= WGSF_val[setup.year] #add WGamma SF
                        y_HsHc *= WGSF_val[setup.year] #add WGamma SF

                if "had" in s:
#                    mcHad_LsLc += y_LsLc
                    mcHad_LsHc += y_LsHc
                    mcHad_HsLc += y_HsLc
                    mcHad_HsHc += y_HsHc
                else:
                    mcPrompt_LsHc += y_LsHc
                    mcPrompt_HsLc += y_HsLc
                    mcPrompt_HsHc += y_HsHc

#            mcPrompt_LsHc *= setup.dataLumi/1000.
#            mcPrompt_HsLc *= setup.dataLumi/1000.
#            mcPrompt_HsHc *= setup.dataLumi/1000.

#            mcHad_LsLc *= setup.dataLumi/1000.
#            mcHad_LsHc *= setup.dataLumi/1000.
#            mcHad_HsLc *= setup.dataLumi/1000.
#            mcHad_HsHc *= setup.dataLumi/1000.

            print
            print data_LsHc
            print mcPrompt_LsHc
            print
            print data_HsLc
            print mcPrompt_HsLc
            print
            print data_HsHc
            print mcPrompt_HsHc
            print
            print
            print data_LsHc - mcPrompt_LsHc
            print data_HsLc - mcPrompt_HsLc
            print data_HsHc - mcPrompt_HsHc
            print
#            print mcHad_LsLc
            print mcHad_LsHc
            print mcHad_HsLc
            print mcHad_HsHc

            # check if any of the factors would be <= 0 to safe time:
            if data_LsHc - mcPrompt_LsHc <= 0: return u_float(0)
            if data_HsLc - mcPrompt_HsLc <= 0: return u_float(0)
            if data_HsHc - mcPrompt_HsHc <= 0: return u_float(0)
#            if mcHad_LsLc <= 0: return u_float(0)
            if mcHad_LsHc <= 0: return u_float(0)
            if mcHad_HsLc <= 0: return u_float(0)
            if mcHad_HsHc <= 0: return u_float(0)

            # Add QCD to Prompt, make sure you run on the semilep skim
            estimate        = getattr( estimators, "QCD-DD" )
            estimate.isData = False
            estimate.initCache(setup.defaultCacheDir())

            y_QCD_LsHc = estimate.cachedEstimate( region, channel, setup_LsHc, overwrite=overwrite )
            mcPrompt_LsHc += y_QCD_LsHc
            print "QCD", "LsHc", y_QCD_LsHc

            y_QCD_HsLc = estimate.cachedEstimate( region, channel, setup_HsLc, overwrite=overwrite )
            mcPrompt_HsLc += y_QCD_HsLc
            print "QCD", "HsLc", y_QCD_HsLc

            y_QCD_HsHc = estimate.cachedEstimate( region, channel, setup_HsHc, overwrite=overwrite )
            mcPrompt_HsHc += y_QCD_HsHc
            print "QCD", "HsHc", y_QCD_HsHc

            # create the data-driven factor
            dataHad_LsHc = data_LsHc-mcPrompt_LsHc
            dataHad_HsLc = data_HsLc-mcPrompt_HsLc
            dataHad_HsHc = data_HsHc-mcPrompt_HsHc
#            mcRatio_Ls   = mcHad_LsLc / mcHad_LsHc
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


