##Standard import
import copy
import os

# RootTools
from RootTools.core.standard          import *

#user specific
from TTGammaEFT.Tools.TriggerSelector import TriggerSelector
from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter, zMassRange
from TTGammaEFT.Analysis.Region       import systematicReplacements
from TTGammaEFT.Analysis.SetupHelpers import *

from Analysis.Tools.metFilters        import getFilterCut

# Logging
if __name__=="__main__":
    import Analysis.Tools.logger as logger
    logger = logger.get_logger( "INFO", logFile=None)
    import RootTools.core.logger as logger_rt
    logger_rt = logger_rt.get_logger( "INFO", logFile=None )
else:
    import logging
    logger = logging.getLogger(__name__)

class Setup:
    def __init__(self, year=2016, photonSelection=False, checkOnly=False, runOnLxPlus=False, private=False):

        logger.info("Initializing Setup")

        self.analysis_results = analysis_results
        self.zMassRange       = zMassRange
        self.prefixes         = []
        self.externalCuts     = []
        self.year             = year

        #Default cuts and requirements. Those three things below are used to determine the key in the cache!
        self.parameters   = {
            "dileptonic":   default_dileptonic,
            "zWindow":      default_zWindow,
            "leptonEta":    default_leptonEta,
            "leptonPt":     default_leptonPt,
            "nJet":         default_nJet,
            "nBTag":        default_nBTag,
            "nPhoton":      default_nPhoton,
            "MET":          default_MET,
            "invertLepIso": default_invLepIso,
            "addMisIDSF":   default_addMisIDSF,
            "m3Window":     default_m3Window,
            "photonIso":    default_photonIso,
        }

        self.isPhotonSelection = default_nPhoton[0] != 0
        self.isSignalRegion    = self.parameters["nBTag"][0] == 1 and self.parameters["nPhoton"][0] == 1 and not self.parameters["photonIso"]
        self.nJet = str(self.parameters["nJet"][0])
        if self.parameters["nJet"][1] < 0: self.nJet += "p"
        self.isBTagged = self.parameters["nBTag"][0] >= 1

        self.sys = {"weight":"weight", "reweight":["reweightHEM", "reweightTrigger", "reweightL1Prefire", "reweightPU", "reweightLeptonTightSF", "reweightLeptonTrackingTightSF", "reweightPhotonSF", "reweightPhotonElectronVetoSF", "reweightBTag_SF"], "selectionModifier":None} 

        if runOnLxPlus:
            # Set the redirector in the samples repository to the global redirector
            from Samples.Tools.config import redirector_global as redirector
        os.environ["gammaSkim"] = str(photonSelection)
        #define samples

        from TTGammaEFT.Samples.default_locations import postprocessing_locations
        if year == 2016 and not checkOnly:
            from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import Run2016 as data
            if private:
                import TTGammaEFT.Samples.nanoTuples_Summer16_private_v6_semilep_postProcessed as mc_samples
            else:
                import TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed as mc_samples
        elif year == 2017 and not checkOnly:
            from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import Run2017 as data
            if private:
                import TTGammaEFT.Samples.nanoTuples_Fall17_private_v6_semilep_postProcessed  as mc_samples
            else:
                import TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed  as mc_samples
        elif year == 2018 and not checkOnly:
            from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import Run2018 as data
            if private:
                import TTGammaEFT.Samples.nanoTuples_Autumn18_private_v6_semilep_postProcessed as mc_samples
            else:
                import TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed as mc_samples
        elif year == "RunII" and not checkOnly:
            if private:
                from TTGammaEFT.Samples.nanoTuples_RunII_private_postProcessed import RunII as data
                import TTGammaEFT.Samples.nanoTuples_RunII_private_postProcessed as mc_samples
            else:
                from TTGammaEFT.Samples.nanoTuples_RunII_postProcessed import RunII as data
                import TTGammaEFT.Samples.nanoTuples_RunII_postProcessed as mc_samples

        if checkOnly:
            self.processes = {}
            self.processes.update( { sample:           None for sample in default_sampleList + default_systematicList + [ "TT_pow", "ST_tW", "ST_tch", "ST_sch", "WG", "WG_NLO", "GJets", "QCD", "GQCD", "QCD_e", "QCD_mu", "all_mc", "all_mc_mu", "all_mc_e", "all_noQCD" ] } )
            self.processes.update( { sample+"_gen":    None for sample in default_sampleList + default_systematicList + [ "TT_pow", "ST_tW", "ST_tch", "ST_sch", "WG", "WG_NLO", "GJets", "QCD", "GQCD", "QCD_e", "QCD_mu", "all_mc", "all_mc_mu", "all_mc_e", "all_noQCD" ] } )
            self.processes.update( { sample+"_misID":  None for sample in default_sampleList + default_systematicList + [ "TT_pow", "ST_tW", "ST_tch", "ST_sch", "WG", "WG_NLO", "GJets", "QCD", "GQCD", "QCD_e", "QCD_mu", "all_mc", "all_mc_mu", "all_mc_e", "all_noQCD" ] } )
            self.processes.update( { sample+"_had":    None for sample in default_sampleList + default_systematicList + [ "TT_pow", "ST_tW", "ST_tch", "ST_sch", "WG", "WG_NLO", "GJets", "QCD", "GQCD", "QCD_e", "QCD_mu", "all_mc", "all_mc_mu", "all_mc_e", "all_noQCD" ] } )
            self.processes.update( { sample+"_prompt": None for sample in default_sampleList + default_systematicList + [ "TT_pow", "ST_tW", "ST_tch", "ST_sch", "WG", "WG_NLO", "GJets", "QCD", "GQCD", "QCD_e", "QCD_mu", "all_mc", "all_mc_mu", "all_mc_e", "all_noQCD" ] } )
            self.processes.update( { sample+"_hp":     None for sample in default_sampleList + default_systematicList + [ "TT_pow", "ST_tW", "ST_tch", "ST_sch", "WG", "WG_NLO", "GJets", "QCD", "GQCD", "QCD_e", "QCD_mu", "all_mc", "all_mc_mu", "all_mc_e", "all_noQCD" ] } )
            self.processes.update( { sample+"_fake":   None for sample in default_sampleList + default_systematicList + [ "TT_pow", "ST_tW", "ST_tch", "ST_sch", "WG", "WG_NLO", "GJets", "QCD", "GQCD", "QCD_e", "QCD_mu", "all_mc", "all_mc_mu", "all_mc_e", "all_noQCD" ] } )
            self.processes.update( { sample+"_PU":     None for sample in default_sampleList + default_systematicList + [ "TT_pow", "ST_tW", "ST_tch", "ST_sch", "WG", "WG_NLO", "GJets", "QCD", "GQCD", "QCD_e", "QCD_mu", "all_mc", "all_mc_mu", "all_mc_e", "all_noQCD" ] } )
            self.processes.update( { sample+"_np":     None for sample in default_sampleList + default_systematicList + [ "TT_pow", "ST_tW", "ST_tch", "ST_sch", "WG", "WG_NLO", "GJets", "QCD", "GQCD", "QCD_e", "QCD_mu", "all_mc", "all_mc_mu", "all_mc_e", "all_noQCD" ] } )
            self.processes["Data"] = "Run%i"%self.year if self.year != "RunII" else "RunII"

            if year == 2016:
                self.lumi     = 35.92*1000
                self.dataLumi = 35.92*1000
            elif year == 2017:
                self.lumi     = 41.53*1000
                self.dataLumi = 41.53*1000
            elif year == 2018:
                self.lumi     = 59.74*1000
                self.dataLumi = 59.74*1000
            elif year == "RunII":
                self.lumi     = (35.92+41.53+59.74)*1000
                self.dataLumi = (35.92+41.53+59.74)*1000

        else:
            # not really needed I think:
            ttg           = mc_samples.TTG
            tt            = mc_samples.TT_pow
            if not private:
                ttg_TuneUp    = mc_samples.TTG_TuneUp
                ttg_TuneDown  = mc_samples.TTG_TuneDown
                ttg_erdOn     = mc_samples.TTG_erdOn
                ttg_QCDbased  = mc_samples.TTG_QCDbased
                ttg_GluonMove = mc_samples.TTG_GluonMove
                ttg_sys_incl = mc_samples.TTG_sys_incl
                top          = mc_samples.Top
                DY           = mc_samples.DY_LO
                zg           = mc_samples.ZG
                wg           = mc_samples.WG
                wg_NLO       = mc_samples.WG_NLO
                wjets        = mc_samples.WJets
                other        = mc_samples.rest #other
                gqcd         = mc_samples.GQCD
                qcd          = mc_samples.QCD
                qcd_e        = mc_samples.QCD_e
                qcd_mu       = mc_samples.QCD_mu
                gjets        = mc_samples.GJets
                tW           = mc_samples.ST_tW
                st_tch       = mc_samples.ST_tch
                st_sch       = mc_samples.ST_sch
                all          = mc_samples.all_mc
                all_noQCD    = mc_samples.all_noQCD
                all_e        = mc_samples.all_mc_e
                all_mu       = mc_samples.all_mc_mu
            else:
                ttg_NLO       = mc_samples.TTG_NLO

            if private:
                mc           = [ ttg, tt, ttg_NLO ]
            else:
                mc           = [ ttg, top, DY, zg, wjets, wg, wg_NLO, other, qcd, gqcd, qcd_e, qcd_mu, gjets, all, all_e, all_mu, all_noQCD ]
                mc          += [ ttg_TuneUp, ttg_TuneDown, ttg_erdOn, ttg_QCDbased, ttg_GluonMove, ttg_sys_incl ]
                mc          += [ tt, tW, st_tch, st_sch ]
            self.processes = {}
            self.processes.update( { sample.name:           sample for sample in mc } )
            self.processes.update( { sample.name+"_gen":    sample for sample in mc } )
            self.processes.update( { sample.name+"_misID":  sample for sample in mc } )
            self.processes.update( { sample.name+"_had":    sample for sample in mc } )
            self.processes.update( { sample.name+"_prompt": sample for sample in mc } )
            self.processes.update( { sample.name+"_hp":     sample for sample in mc } )
            self.processes.update( { sample.name+"_fake":   sample for sample in mc } )
            self.processes.update( { sample.name+"_PU":     sample for sample in mc } )
            self.processes.update( { sample.name+"_np":     sample for sample in mc } )
            self.processes["Data"] = data

            self.lumi     = data.lumi
            self.dataLumi = data.lumi # get from data samples later
        

    def prefix(self, channel="all"):
        return "_".join(self.prefixes+[self.preselection("MC", channel=channel)["prefix"]])

    def defaultCacheDir(self):
        cacheDir = os.path.join(cache_dir, str(self.year), "estimates")
        logger.info("Default cache dir is: %s", cacheDir)
        return cacheDir

    #Clone the setup and optinally modify the systematic variation
    def sysClone(self, sys=None, parameters=None):
        """Clone setup and change systematic if provided"""

        res            = copy.copy(self)
        res.sys        = copy.deepcopy(self.sys)
        res.parameters = copy.deepcopy(self.parameters)

        if sys:
            for k in sys.keys():
                if k=="remove":
                    for i in sys[k]:
                      res.sys["reweight"].remove(i)
                elif k=="reweight":
                    res.sys[k] = list(set(res.sys[k]+sys[k])) #Add with unique elements
                    
                    if "reweightLeptonTightSFSyst"     in res.sys[k]: res.sys[k].remove("reweightLeptonTightSF")
                    if "reweightLeptonTightSFStat"     in res.sys[k]: res.sys[k].remove("reweightLeptonTightSF")
                    for upOrDown in ["Up","Down"]:
                        if "reweightL1Prefire"+upOrDown             in res.sys[k]: res.sys[k].remove("reweightL1Prefire")
                        if "reweightTrigger"+upOrDown               in res.sys[k]: res.sys[k].remove("reweightTrigger")
                        if "reweightPU"+upOrDown                    in res.sys[k]: res.sys[k].remove("reweightPU")
                        if "reweightLeptonTightSF"+upOrDown         in res.sys[k]: res.sys[k].remove("reweightLeptonTightSF")
                        if "reweightLeptonTightSFSyst"+upOrDown     in res.sys[k]: res.sys[k].remove("reweightLeptonTightSF")
                        if "reweightLeptonTightSFStat"+upOrDown     in res.sys[k]: res.sys[k].remove("reweightLeptonTightSF")
                        if "reweightLeptonTrackingTightSF"+upOrDown in res.sys[k]: res.sys[k].remove("reweightLeptonTrackingTightSF")
                        if "reweightPhotonSF"+upOrDown              in res.sys[k]: res.sys[k].remove("reweightPhotonSF")
                        if "reweightPhotonAltSigSF"+upOrDown        in res.sys[k]: res.sys[k].remove("reweightPhotonSF")
                        if "reweightPhotonElectronVetoSF"+upOrDown  in res.sys[k]: res.sys[k].remove("reweightPhotonElectronVetoSF")
                        if 'reweightBTag_SF_b_'+upOrDown            in res.sys[k]: res.sys[k].remove('reweightBTag_SF')
                        if 'reweightBTag_SF_l_'+upOrDown            in res.sys[k]: res.sys[k].remove('reweightBTag_SF')
                else:
                    res.sys[k] = sys[k]

        if parameters:
            for k in parameters.keys():
                res.parameters[k] = parameters[k]

        res.isPhotonSelection = res.parameters["nPhoton"][0] != 0
        res.isSignalRegion    = res.parameters["nBTag"][0] == 1 and res.parameters["nPhoton"][0] == 1 and not res.parameters["photonIso"]
        res.nJet = str(res.parameters["nJet"][0])
        if res.parameters["nJet"][1] < 0: res.nJet += "p"
        res.isBTagged = res.parameters["nBTag"][0] >= 1
        return res

    def defaultParameters(self, update={} ):
        assert type(update)==type({}), "Update arguments with key arg dictionary. Got this: %r"%update
        res = copy.deepcopy(self.parameters)
        res.update(update)
        return res

    def weightString(self, dataMC, photon="PhotonGood0", addMisIDSF=False):
        lumiString = "(35.92*(year==2016)+41.53*(year==2017)+59.74*(year==2018))"
        _weightString = {}
        _weightString["Data"] = "weight" 
        _weightString["MC"] = "*".join([self.sys["weight"]] + (self.sys["reweight"] if self.sys["reweight"] else []))
        _weightString["MC"] += "*%s"%lumiString


        if addMisIDSF and photon:
            if self.nJet == "2p": misIDSF_val   = misID2pSF_val
            elif self.nJet == "3p": misIDSF_val = misID3pSF_val
            elif self.nJet == "4p": misIDSF_val = misID4pSF_val
            elif self.nJet == "2": misIDSF_val  = misID2SF_val
            elif self.nJet == "3": misIDSF_val  = misID3SF_val
            elif self.nJet == "4": misIDSF_val  = misID4SF_val
            elif self.nJet == "5": misIDSF_val  = misID5SF_val

            if self.year == "RunII":
                ws   = "(%s)"%_weightString["MC"]
                ws16 = "+(%s*(%s_photonCatMagic==2)*(%f-1)*(year==2016))" %(_weightString["MC"], photon, misIDSF_val[2016].val)
                ws17 = "+(%s*(%s_photonCatMagic==2)*(%f-1)*(year==2017))" %(_weightString["MC"], photon, misIDSF_val[2017].val)
                ws18 = "+(%s*(%s_photonCatMagic==2)*(%f-1)*(year==2018))" %(_weightString["MC"], photon, misIDSF_val[2018].val)
                _weightString["MC"] = ws + ws16 + ws17 + ws18
            else:
                _weightString["MC"] += "+%s*(%s_photonCatMagic==2)*(%f-1)" %(_weightString["MC"], photon, misIDSF_val[self.year].val)

        if   dataMC == "DataMC": return _weightString

        if   dataMC == "Data": _weightString = _weightString["Data"]
        elif (dataMC == "MC" or dataMC == "MCpTincl"):   _weightString = _weightString["MC"]
        logger.debug("Using weight-string: %s", _weightString)

        return _weightString

    def preselection(self, dataMC , channel="all", processCut=None):
        """Get preselection  cutstring."""
        cut = self.selection(dataMC, channel = channel, processCut=processCut, **self.parameters)
        logger.debug("Using cut-string: %s", cut)
        if processCut:
            logger.info("Adding process specific cut: %s"%processCut)
        return cut

    def selection(self, dataMC,
                        dileptonic=None, invertLepIso=None, addMisIDSF=None,
                        nJet=None, nBTag=None, nPhoton=None,
                        MET=None,
                        zWindow=None, m3Window=None, leptonEta=None, leptonPt=None,
                        photonIso=None, processCut=None,
                        channel="all"):
        """Define full selection
           dataMC: "Data" or "MC" or "MCptincl
           channel: all, e or mu, eetight, mumutight, SFtight
           zWindow: offZeg, onZeg, onZSFllTight, onZSFllgTight, onZSFlloffZSFllg or all
           m3Window: offM3, onM3 or all
           photonIso: highSieie, highChgIso, highChgIsohighSieie
        """
        if not dileptonic:   dileptonic   = self.parameters["dileptonic"]
        if not invertLepIso: invertLepIso = self.parameters["invertLepIso"]
        if not addMisIDSF:   addMisIDSF   = self.parameters["addMisIDSF"]
        if not nJet:         nJet         = self.parameters["nJet"]
        if not nBTag:        nBTag        = self.parameters["nBTag"]
        if not nPhoton:      nPhoton      = self.parameters["nPhoton"]
        if not MET:          MET          = self.parameters["MET"]
        if not zWindow:      zWindow      = self.parameters["zWindow"]
        if not leptonEta:    leptonEta    = self.parameters["leptonEta"]
        if not leptonPt:     leptonPt     = self.parameters["leptonPt"]
        if not m3Window:     m3Window     = self.parameters["m3Window"]
        if not photonIso:    photonIso    = self.parameters["photonIso"]

        #Consistency checks
        assert dataMC in ["Data","MC","DataMC","MCpTincl"], "dataMC = Data or MC or DataMC, got %r."%dataMC
        assert channel in allChannels, "channel must be one of "+",".join(allChannels)+". Got %r."%channel
        assert zWindow in ["offZeg", "onZeg", "onZSFllTight", "onZSFllgTight", "onZSFlloffZSFllg", "all"], "zWindow must be one of onZeg, offZeg, onZSFllTight, onZSFllgTight, all. Got %r"%zWindow
        assert m3Window in ["offM3", "onM3", "all"], "m3Window must be one of onM3, offM3, all. Got %r"%m3Window
        assert photonIso in [None, "highSieieNoChgIso", "lowSieieNoChgIso", "noSieie", "highSieie", "lowChgIsoNoSieie", "highChgIsoNoSieie", "noChgIso", "highChgIso", "noChgIsoNoSieie", "highChgIsohighSieie"], "PhotonIso must be one of highSieie, highChgIso, highChgIsohighSieie. Got %r"%photonIso
        assert processCut in [None, "cat0","cat1","cat2","cat3","cat13","cat02","cat134", "cat4"], "Process specific cut must be one of cat0, cat2, cat13, cat4. Got %r"%processCut
        if self.sys['selectionModifier']:
            assert self.sys['selectionModifier'] in jmeVariations+metVariations+eVariations+muVariations, "Don't know about systematic variation %r, take one of %s"%(self.sys['selectionModifier'], ",".join(jmeVariations+metVariations+eVariations+muVariations))

        res={"cuts":[], "prefixes":[]}

        # default lepton selections
        tightLepton  = "nLepTight1"
        vetoLepton   = "nLepVeto1"
#        vetoLepton   = "nLepNoCorrVeto1"
        jetCutVar    = "nJetGood"
        jetPrefix    = "nJet"
        btagCutVar   = "nBTagGood"
        btagPrefix   = "nBTag"
        photonCutVar = "nPhotonGood"
        photonPrefix = "nPhoton"
        photonCatVar = "PhotonGood0_photonCatMagic"
        photonCatPrefix = "photoncat"
        photonVetoCutVar = "nPhotonNoChgIsoNoSieie"
        photonVetoPrefix = "nHadPhoton"
#        photonVetoCutVar = None
#        photonVetoPrefix = None
        if channel in ["e","eetight"]:
            leptonEtaCutVar = "abs(LeptonTight0_eta+LeptonTight0_deltaEtaSC)"
            leptonEtaPrefix = "etascl"
        else:
            leptonEtaCutVar = "abs(LeptonTight0_eta)"
            leptonEtaPrefix = "etal"

        leptonPtCutVar = "LeptonTight0_pt"
        leptonPtPrefix = "ptl"

        if dileptonic:
            tightLepton = "nLepTight2-OStight"
            vetoLepton = "nLepVeto2"

        if photonIso:
            zWindow     += "SB"

        if invertLepIso:
            # invert leptonIso in lepton cuts
            channel     += "Inv"
            zWindow     += "Inv"
            tightLepton  = "nInvLepTight1"
            vetoLepton   = "nLepVeto1"
#            vetoLepton   = "nLepNoCorrVeto1"
            jetCutVar    = "nJetGoodInvLepIso"
            jetPrefix    = "nInvLJet"
            btagCutVar   = "nBTagGoodInvLepIso"
            btagPrefix   = "nInvLBTag"
            photonCutVar = "nPhotonGoodInvLepIso"
            photonPrefix = "nInvLPhoton"
            photonCatVar = "PhotonGoodInvLepIso0_photonCatMagic"
            photonCatPrefix = "invLphotoncat"
#            photonVetoCutVar = None
#            photonVetoPrefix = None
            photonVetoCutVar = "nPhotonNoChgIsoNoSieieInvLepIso"
            photonVetoPrefix = "nInvLHadPhoton"
            if channel in ["eInv","eetightInv"]:
                leptonEtaCutVar = "abs(LeptonTightInvIso0_eta+LeptonTightInvIso0_deltaEtaSC)"
                leptonEtaPrefix = "etainvscl"
            else:
                leptonEtaCutVar = "abs(LeptonTightInvIso0_eta)"
                leptonEtaPrefix = "etainvl"

            leptonPtCutVar = "LeptonTightInvIso0_pt"
            leptonPtPrefix = "ptinvl"

        #photon cut
        photonSel = nPhoton and not (nPhoton[0]==0 and nPhoton[1]<=0)

        if photonSel and photonIso:

            if invertLepIso:
                jetCutVar    = "nJetGoodNoChgIsoNoSieieInvLepIso"
                jetPrefix    = "nInvLNoChgIsoNoSieieJet"
                btagCutVar   = "nBTagGoodNoChgIsoNoSieieInvLepIso"
                btagPrefix   = "nInvLNoChgIsoNoSieieBTag"
                photonCutVar = "nPhotonNoChgIsoNoSieieInvLepIso"
                photonPrefix = "nInvLHadPhoton"
                photonVetoCutVar = "nPhotonNoChgIsoNoSieieInvLepIso"
                photonVetoPrefix = "nInvLHadPhoton"
                photonCatVar = "PhotonNoChgIsoNoSieieInvLepIso0_photonCatMagic"
                photonCatPrefix = "invLNoChgIsoNoSieiephotoncat"
                photonIso += "InvL"

            else:
                jetCutVar    = "nJetGoodNoChgIsoNoSieie"
                jetPrefix    = "nNoChgIsoNoSieieJet"
                btagCutVar   = "nBTagGoodNoChgIsoNoSieie"
                btagPrefix   = "nNoChgIsoNoSieieBTag"
                photonCutVar = "nPhotonNoChgIsoNoSieie"
                photonPrefix = "nHadPhoton"
                photonVetoCutVar = "nPhotonNoChgIsoNoSieie"
                photonVetoPrefix = "nHadPhoton"
                photonCatVar = "PhotonNoChgIsoNoSieie0_photonCatMagic"
                photonCatPrefix = "noChgIsoNoSieiephotoncat"

        if not photonSel and not dileptonic:
            # remove default zwindow cut in qcd estimation for non photon regions
            zWindow = "all"

        #Postfix for variables (only for MC and if we have a jme variation)
        jSysStr = ""
        if (dataMC == "MC" or dataMC == "MCpTincl") and self.sys['selectionModifier'] in jmeVariations + metVariations:
            jSysStr = "_" + self.sys['selectionModifier']
        pSysStr = ""
        lSysStr = ""
        isEVar  = False
        isMuVar = False
        if (dataMC == "MC" or dataMC == "MCpTincl") and self.sys['selectionModifier'] in muVariations:
            lSysStr = "_" + self.sys['selectionModifier']
#            leptonPtCutVar += "_totalUp" if "up" in self.sys['selectionModifier'].lower() else "_totalDown"
            isMuVar = True
        if (dataMC == "MC" or dataMC == "MCpTincl") and self.sys['selectionModifier'] in eVariations:
            lSysStr = "_" + self.sys['selectionModifier']
            pSysStr = "_" + self.sys['selectionModifier']
            isEVar = True
#            leptonPtCutVar += "_totalUp" if "up" in self.sys['selectionModifier'].lower() else "_totalDown"

        if photonSel and photonIso:

            res["prefixes"].append( photonIso )
            preselphotonIso = cutInterpreter.cutString( photonIso )
            if dataMC == "MC":
                res["cuts"].append( preselphotonIso.replace("0_","0"+pSysStr+"_") )
            else:
                res["cuts"].append( preselphotonIso )

        #leptons or inv. iso leptons
        res["prefixes"].append( tightLepton )
        lepSel = cutInterpreter.cutString( tightLepton )
        if lSysStr: lepSel = lepSel.replace("==","%s=="%lSysStr)
        res["cuts"].append( lepSel )
              
        #lepton channel or inv. iso lepton channel
        res["prefixes"].append( channel )
        chStr = cutInterpreter.cutString( channel )
        if lSysStr and ( (channel in ["e","eetight"] and isEVar) or (channel in ["mu","mumutight"] and isMuVar) ): chStr = chStr.replace("==","%s=="%lSysStr)
        res["cuts"].append(chStr)

        #lepton veto or no Iso lepton veto
        res["prefixes"].append( vetoLepton )
        chVetoStr = cutInterpreter.cutString( vetoLepton )
        if lSysStr: chVetoStr = chVetoStr.replace("==","%s=="%lSysStr)
        res["cuts"].append( chVetoStr )

        if nJet and not (nJet[0]==0 and nJet[1]<0):
            assert nJet[0]>=0 and (nJet[1]>=nJet[0] or nJet[1]<0), "Not a good nJet selection: %r"%nJet
            njetsstr = jetCutVar+jSysStr+">="+str(nJet[0])
            prefix   = jetPrefix+str(nJet[0])
            if nJet[1]>=0:
                njetsstr+= "&&"+jetCutVar+jSysStr+"<="+str(nJet[1])
                if nJet[1]!=nJet[0]: prefix+="To"+str(nJet[1])
            else:
                prefix+="p"
            res["cuts"].append(njetsstr)
            res["prefixes"].append(prefix)

        if nBTag and not (nBTag[0]==0 and nBTag[1]<0):
            assert nBTag[0]>=0 and (nBTag[1]>=nBTag[0] or nBTag[1]<0), "Not a good nBTag selection: %r"% nBTag
            if jSysStr: nbtstr = btagCutVar+jSysStr+">="+str(nBTag[0])
            else:      nbtstr = btagCutVar+jSysStr+">="+str(nBTag[0])
            prefix = btagPrefix+str(nBTag[0])
            if nBTag[1]>=0:
                if jSysStr: nbtstr+= "&&"+btagCutVar+jSysStr+"<="+str(nBTag[1])
                else:      nbtstr+= "&&"+btagCutVar+jSysStr+"<="+str(nBTag[1])
                if nBTag[1]!=nBTag[0]: prefix+="To"+str(nBTag[1])
            else:
                prefix+="p"
            res["cuts"].append(nbtstr)
            res["prefixes"].append(prefix)

        if photonSel:
            #photon cut
            assert nPhoton[0]>=0 and (nPhoton[1]>=nPhoton[0] or nPhoton[1]<0), "Not a good nPhoton selection: %r"%nPhoton
            nphotonsstr = photonCutVar+pSysStr+">="+str(nPhoton[0])
            prefix      = photonPrefix+str(nPhoton[0])
            if nPhoton[1]>=0:
                nphotonsstr+= "&&"+photonCutVar+pSysStr+"<="+str(nPhoton[1])
                if nPhoton[1]!=nPhoton[0]: prefix+="To"+str(nPhoton[1])
            else:
                prefix+="p"
            res["cuts"].append(nphotonsstr)
            res["prefixes"].append(prefix)

            if photonVetoCutVar:
                nphotonVetosstr = photonVetoCutVar+pSysStr+">="+str(nPhoton[0])
                prefix          = photonVetoPrefix+str(nPhoton[0])
                if nPhoton[1]>=0:
                    nphotonVetosstr += "&&"+photonVetoCutVar+pSysStr+"<="+str(nPhoton[1])
                    if nPhoton[1] != nPhoton[0]: prefix+="To"+str(nPhoton[1])
                else:
                    prefix+="p"
                res["cuts"].append(nphotonVetosstr)
                res["prefixes"].append(prefix)

        else:
            addMisIDSF   = False
            res["cuts"].append(photonCutVar+pSysStr+"==0")
            res["prefixes"].append(photonPrefix+"0")
            if photonVetoCutVar:
                res["cuts"].append(photonVetoCutVar+pSysStr+"==0")
                res["prefixes"].append(photonVetoPrefix+"0")

        #leptonEta cut
        if leptonEta and not (leptonEta[0]==0 and leptonEta[1]<0):
            assert leptonEta[0]>=0 and (leptonEta[1]>=leptonEta[0] or leptonEta[1]<0) and leptonEta[1]!=leptonEta[0], "Not a good leptonEta selection: %r"%leptonEta
            leptonEtastr = leptonEtaCutVar+">="+str(leptonEta[0])
            prefix       = leptonEtaPrefix+str(leptonEta[0])
            if leptonEta[1]>=0:
                leptonEtastr += "&&"+leptonEtaCutVar+"<"+str(leptonEta[1])
                prefix       += "To"+str(leptonEta[1])
            res["cuts"].append(leptonEtastr)
            res["prefixes"].append(prefix)

        #leptonPt cut
        if leptonPt and not (leptonPt[0]==0 and leptonPt[1]<0):
            assert leptonPt[0]>=0 and (leptonPt[1]>=leptonPt[0] or leptonPt[1]<0) and leptonPt[1]!=leptonPt[0], "Not a good leptonPt selection: %r"%leptonPt
            leptonPtstr = leptonPtCutVar+">="+str(leptonPt[0])
            prefix       = leptonPtPrefix+str(leptonPt[0])
            if leptonPt[1]>=0:
                leptonPtstr += "&&"+leptonPtCutVar+"<"+str(leptonPt[1])
                prefix       += "To"+str(leptonPt[1])
            res["cuts"].append(leptonPtstr)
            res["prefixes"].append(prefix)

        #MET cut
        if MET and not (MET[0]==0 and MET[1]<0):
            assert MET[0]>=0 and (MET[1]>=MET[0] or MET[1]<0), "Not a good MET selection: %r"%MET
            metsstr = "MET_pt"+jSysStr+">="+str(MET[0])
            prefix   = "met"+str(MET[0])
            if MET[1]>=0:
                metsstr+= "&&"+"MET_pt"+jSysStr+"<"+str(MET[1])
                if MET[1]!=MET[0]: prefix+="To"+str(MET[1])
            res["cuts"].append(metsstr)
            res["prefixes"].append(prefix)

        #Z window
        if not "all" in zWindow:
            res["prefixes"].append( zWindow )
            preselZWindow = cutInterpreter.cutString( zWindow )
            if pSysStr:
                for s in systematicReplacements[self.sys['selectionModifier']]:
                    if s in preselZWindow: preselZWindow=preselZWindow.replace(s,s+pSysStr)
            res["cuts"].append( preselZWindow )

        #M3 window
        if m3Window != "all":
            res["prefixes"].append( m3Window )
            preselM3Window = cutInterpreter.cutString( m3Window )
            res["cuts"].append( preselM3Window )

        if processCut:
            catPrefix = photonCatPrefix + processCut.replace("cat","")
            res["prefixes"].append( catPrefix )
            catCut = cutInterpreter.cutString( catPrefix )
            res["cuts"].append( catCut.replace("0_","0"+pSysStr+"_") )

        #badEEVeto
#        if self.year == 2017:
#            res["prefixes"].append("BadEEJetVeto")
#            badEEStr = cutInterpreter.cutString( "BadEEJetVeto" )
#            res["cuts"].append( badEEStr )

        if invertLepIso:
            res["cuts"].append( "triggeredInvIso==1" )
        elif lSysStr:
            res["cuts"].append( "triggered"+lSysStr+"==1" )
        else:
            res["cuts"].append( "triggered==1" )

        res["cuts"].append( "reweightHEM>0" )

        if dataMC == "MC":
            res["cuts"].append( "overlapRemoval==1" )
            res["cuts"].append( "pTStitching==1" )

        if dataMC == "MCpTincl":
            res["cuts"].append( "overlapRemoval==1" )

        if dataMC != "DataMC":
            res["cuts"].append( getFilterCut(isData=(dataMC=="Data"), year=self.year, skipBadChargedCandidate=True) )
            res["cuts"].extend(self.externalCuts)

        catVar = photonCatVar.split("0")[0] + "0"
        if pSysStr: catVar += pSysStr
        return {"cut":"&&".join(res["cuts"]), "prefix":"-".join(res["prefixes"]), "weightStr": self.weightString(dataMC,photon=catVar if addMisIDSF else None,addMisIDSF=addMisIDSF and self.isPhotonSelection)}

    def genSelection(self, dataMC,
                        dileptonic=None, invertLepIso=None, addMisIDSF=None,
                        nJet=None, nBTag=None, nPhoton=None,
                        MET=None,
                        zWindow=None, m3Window=None, leptonEta=None, leptonPt=None,
                        photonIso=None, processCut=None,
                        channel="all"):

        # define input similar to selection() eventhough not used
        """Define full selection
           channel: all, e or mu, eetight, mumutight, SFtight
           zWindow: offZeg, onZeg, onZSFllTight, onZSFllgTight or all
           m3Window: offM3, onM3 or all
        """
        if not nJet:         nJet         = self.parameters["nJet"]
        if not nBTag:        nBTag        = self.parameters["nBTag"]
        if not nPhoton:      nPhoton      = self.parameters["nPhoton"]
        if not MET:          MET          = self.parameters["MET"]
        if not zWindow:      zWindow      = self.parameters["zWindow"]
        if not leptonEta:    leptonEta    = self.parameters["leptonEta"]
        if not leptonPt:     leptonPt     = self.parameters["leptonPt"]
        if not m3Window:     m3Window     = self.parameters["m3Window"]

        #Consistency checks
        assert channel in allChannels, "channel must be one of "+",".join(allChannels)+". Got %r."%channel
        assert zWindow in ["offZeg", "onZeg", "onZSFllTight", "onZSFllgTight", "all"], "zWindow must be one of onZeg, offZeg, onZSFllTight, onZSFllgTight, all. Got %r"%zWindow
        assert m3Window in ["offM3", "onM3", "all"], "m3Window must be one of onM3, offM3, all. Got %r"%m3Window

        res={"cuts":[], "prefixes":[]}

        # default lepton selections
        tightLepton  = "nLepTight1"
        jetCutVar    = "nJetGood"
        jetPrefix    = "nJet"
        btagCutVar   = "nBTagGood"
        btagPrefix   = "nBTag"
        photonCutVar = "nPhotonGood"
        photonPrefix = "nPhoton"
        leptonEtaCutVar = "abs(LeptonTight0_eta)"
        leptonEtaPrefix = "etal"
        leptonPtCutVar = "LeptonTight0_pt"
        leptonPtPrefix = "ptl"

        #leptons or inv. iso leptons
        res["prefixes"].append( tightLepton )
        lepSel = cutInterpreter.cutString( tightLepton )
        res["cuts"].append( lepSel )
              
        #lepton channel or inv. iso lepton channel
        res["prefixes"].append( channel )
        chStr = cutInterpreter.cutString( channel )
        res["cuts"].append(chStr)

        if nJet and not (nJet[0]==0 and nJet[1]<0):
            assert nJet[0]>=0 and (nJet[1]>=nJet[0] or nJet[1]<0), "Not a good nJet selection: %r"%nJet
            njetsstr = jetCutVar+">="+str(nJet[0])
            prefix   = jetPrefix+str(nJet[0])
            if nJet[1]>=0:
                njetsstr+= "&&"+jetCutVar+"<="+str(nJet[1])
                if nJet[1]!=nJet[0]: prefix+=str(nJet[1])
            else:
                prefix+="p"
            res["cuts"].append(njetsstr)
            res["prefixes"].append(prefix)

        if nBTag and not (nBTag[0]==0 and nBTag[1]<0):
            assert nBTag[0]>=0 and (nBTag[1]>=nBTag[0] or nBTag[1]<0), "Not a good nBTag selection: %r"% nBTag
            nbtstr = btagCutVar+">="+str(nBTag[0])
            prefix = btagPrefix+str(nBTag[0])
            if nBTag[1]>=0:
                nbtstr+= "&&"+btagCutVar+"<="+str(nBTag[1])
                if nBTag[1]!=nBTag[0]: prefix+=str(nBTag[1])
            else:
                prefix+="p"
            res["cuts"].append(nbtstr)
            res["prefixes"].append(prefix)

        photonSel = nPhoton and not (nPhoton[0]==0 and nPhoton[1]<=0)

        if photonSel:
            #photon cut
            assert nPhoton[0]>=0 and (nPhoton[1]>=nPhoton[0] or nPhoton[1]<0), "Not a good nPhoton selection: %r"%nPhoton
            nphotonsstr = photonCutVar+">="+str(nPhoton[0])
            prefix      = photonPrefix+str(nPhoton[0])
            if nPhoton[1]>=0:
                nphotonsstr+= "&&"+photonCutVar+"<="+str(nPhoton[1])
                if nPhoton[1]!=nPhoton[0]: prefix+="To"+str(nPhoton[1])
            else:
                prefix+="p"
            res["cuts"].append(nphotonsstr)
            res["prefixes"].append(prefix)

        else:
            res["cuts"].append(photonCutVar+"==0")
            res["prefixes"].append(photonPrefix+"0")

        #leptonEta cut
        if leptonEta and not (leptonEta[0]==0 and leptonEta[1]<0):
            assert leptonEta[0]>=0 and (leptonEta[1]>=leptonEta[0] or leptonEta[1]<0) and leptonEta[1]!=leptonEta[0], "Not a good leptonEta selection: %r"%leptonEta
            leptonEtastr = leptonEtaCutVar+">="+str(leptonEta[0])
            prefix       = leptonEtaPrefix+str(leptonEta[0])
            if leptonEta[1]>=0:
                leptonEtastr += "&&"+leptonEtaCutVar+"<"+str(leptonEta[1])
                prefix       += "To"+str(leptonEta[1])
            res["cuts"].append(leptonEtastr)
            res["prefixes"].append(prefix)

        #leptonPt cut
        if leptonPt and not (leptonPt[0]==0 and leptonPt[1]<0):
            assert leptonPt[0]>=0 and (leptonPt[1]>=leptonPt[0] or leptonPt[1]<0) and leptonPt[1]!=leptonPt[0], "Not a good leptonPt selection: %r"%leptonPt
            leptonPtstr = leptonPtCutVar+">="+str(leptonPt[0])
            prefix       = leptonPtPrefix+str(leptonPt[0])
            if leptonPt[1]>=0:
                leptonPtstr += "&&"+leptonPtCutVar+"<"+str(leptonPt[1])
                prefix       += "To"+str(leptonPt[1])
            res["cuts"].append(leptonPtstr)
            res["prefixes"].append(prefix)

        #MET cut
        if MET and not (MET[0]==0 and MET[1]<0):
            assert MET[0]>=0 and (MET[1]>=MET[0] or MET[1]<0), "Not a good MET selection: %r"%MET
            metsstr = "MET_pt"+">="+str(MET[0])
            prefix   = "met"+str(MET[0])
            if MET[1]>=0:
                metsstr+= "&&"+"MET_pt"+"<"+str(MET[1])
                if MET[1]!=MET[0]: prefix+="To"+str(MET[1])
            res["cuts"].append(metsstr)
            res["prefixes"].append(prefix)

        #Z window
        if not "all" in zWindow:
            res["prefixes"].append( zWindow )
            preselZWindow = cutInterpreter.cutString( zWindow )
            res["cuts"].append( preselZWindow )

        #M3 window
        if m3Window != "all":
            res["prefixes"].append( m3Window )
            preselM3Window = cutInterpreter.cutString( m3Window )
            res["cuts"].append( preselM3Window )

        return {"cut":"&&".join(res["cuts"]), "prefix":"-".join(res["prefixes"])}



if __name__ == "__main__":
    setup = Setup( year=2016, private=True )
    for name, dict in allRegions.items():
#        if not "wjetsec3" in name.lower() and not "wjetsbarrel3" in name.lower(): continue
        if not "sr3p" in name.lower(): continue
        print
        print name
#        dict["parameters"]["invertLepIso"] = False
        print
        setup = setup.sysClone( parameters=dict["parameters"] )
#        setup = setup.sysClone({"selectionModifier":"eResUp"})
        for channel in dict["channels"]:
            print
            print channel
            print
            res = setup.selection("MC", channel=channel, **setup.defaultParameters( update=dict["parameters"] ))
            print res["cut"]
            print cutInterpreter.cutString( res["prefix"] )
#            print res["prefix"]
#            print res["weightStr"]



