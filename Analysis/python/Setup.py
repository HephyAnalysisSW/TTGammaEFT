#Standard import
import copy
import os

# RootTools
from RootTools.core.standard          import *

#user specific
from TTGammaEFT.Tools.TriggerSelector import TriggerSelector
from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter, zMassRange
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
    def __init__(self, year=2016, photonSelection=False, checkOnly=False, runOnLxPlus=False):

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

        self.sys = {"weight":"weight", "reweight":["reweightHEM", "reweightTrigger", "reweightL1Prefire", "reweightPU", "reweightLeptonTightSF", "reweightLeptonTrackingTightSF", "reweightPhotonSF", "reweightPhotonElectronVetoSF", "reweightBTag_SF"], "selectionModifier":None} 

        if runOnLxPlus:
            # Set the redirector in the samples repository to the global redirector
            from Samples.Tools.config import redirector_global as redirector
        os.environ["gammaSkim"] = str(photonSelection)
        if year == 2016 and not checkOnly:
            #define samples
            from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed  import TTG_16, TT_pow_16, DY_LO_16, WJets_16, WG_16, ZG_16, QCD_16, GJets_16, rest_16, TTG_TuneUp_16, TTG_TuneDown_16, TTG_erdOn_16
            from TTGammaEFT.Samples.nanoTuples_Run2016_14Dec2018_semilep_postProcessed import Run2016
            ttg         = TTG_16
            ttg_TuneUp   = TTG_TuneUp_16
            ttg_TuneDown = TTG_TuneDown_16
            ttg_erdOn    = TTG_erdOn_16
            tt          = TT_pow_16
            DY          = DY_LO_16
            zg          = ZG_16
            wg          = WG_16
            wjets       = WJets_16
            other       = rest_16 #other_16
            qcd         = QCD_16
            gjets       = GJets_16
            data        = Run2016

        elif year == 2017 and not checkOnly:
            #define samples
            from TTGammaEFT.Samples.nanoTuples_Fall17_private_semilep_postProcessed    import TTG_17, TT_pow_17, DY_LO_17, WJets_17, WG_17, ZG_17, QCD_17, GJets_17, rest_17, TTG_TuneUp_17, TTG_TuneDown_17, TTG_erdOn_17
            from TTGammaEFT.Samples.nanoTuples_Run2017_14Dec2018_semilep_postProcessed import Run2017
            ttg          = TTG_17
            ttg_TuneUp   = TTG_TuneUp_17
            ttg_TuneDown = TTG_TuneDown_17
            ttg_erdOn    = TTG_erdOn_17
            tt           = TT_pow_17
            DY           = DY_LO_17
            zg           = ZG_17
            wg           = WG_17
            wjets        = WJets_17
            other        = rest_17 #other_17
            qcd          = QCD_17
            gjets        = GJets_17
            data         = Run2017

        elif year == 2018 and not checkOnly:
            #define samples
            from TTGammaEFT.Samples.nanoTuples_Autumn18_private_semilep_postProcessed  import TTG_18, TT_pow_18, DY_LO_18, WJets_18, WG_18, ZG_18, QCD_18, GJets_18, rest_18, TTG_TuneUp_18, TTG_TuneDown_18, TTG_erdOn_18
            from TTGammaEFT.Samples.nanoTuples_Run2018_14Dec2018_semilep_postProcessed import Run2018
            ttg         = TTG_18
            ttg_TuneUp   = TTG_TuneUp_18
            ttg_TuneDown = TTG_TuneDown_18
            ttg_erdOn    = TTG_erdOn_18
            tt          = TT_pow_18
            DY          = DY_LO_18
            zg          = ZG_18
            wg          = WG_18
            wjets       = WJets_18
            other       = rest_18 #other_18
            qcd         = QCD_18
            gjets       = GJets_18
            data        = Run2018


        if checkOnly:
            self.processes = {}
            self.processes.update( { sample:          None for sample in default_sampleList + default_systematicList } )
            self.processes.update( { sample+"_gen":   None for sample in default_sampleList + default_systematicList } )
            self.processes.update( { sample+"_misID": None for sample in default_sampleList + default_systematicList } )
            self.processes.update( { sample+"_had":   None for sample in default_sampleList + default_systematicList } )
            self.processes.update( { sample+"_magic": None for sample in default_sampleList + default_systematicList } )
            self.processes["Data"] = "Run%i"%self.year

            if year == 2016:
                self.lumi     = 35.92*1000
                self.dataLumi = 35.92*1000
            elif year == 2017:
                self.lumi     = 41.53*1000
                self.dataLumi = 41.53*1000
            elif year == 2018:
                self.lumi     = 59.74*1000
                self.dataLumi = 59.74*1000

        else:
            mc           = [ ttg, tt, DY, zg, wjets, wg, other, qcd, gjets ]
            mc          += [ ttg_TuneUp, ttg_TuneDown, ttg_erdOn ]
            self.processes = {}
            self.processes.update( { sample.name:          sample for sample in mc } )
            self.processes.update( { sample.name+"_gen":   sample for sample in mc } )
            self.processes.update( { sample.name+"_misID": sample for sample in mc } )
            self.processes.update( { sample.name+"_had":   sample for sample in mc } )
            self.processes.update( { sample.name+"_magic": sample for sample in mc } )
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
                    
                    for upOrDown in ["Up","Down"]:
                        if "reweightL1Prefire"+upOrDown             in res.sys[k]: res.sys[k].remove("reweightL1Prefire")
                        if "reweightTrigger"+upOrDown               in res.sys[k]: res.sys[k].remove("reweightTrigger")
                        if "reweightPU"+upOrDown                    in res.sys[k]: res.sys[k].remove("reweightPU")
                        if "reweightLeptonTightSF"+upOrDown         in res.sys[k]: res.sys[k].remove("reweightLeptonTightSF")
                        if "reweightLeptonTrackingTightSF"+upOrDown in res.sys[k]: res.sys[k].remove("reweightLeptonTrackingTightSF")
                        if "reweightPhotonSF"+upOrDown              in res.sys[k]: res.sys[k].remove("reweightPhotonSF")
                        if "reweightPhotonElectronVetoSF"+upOrDown  in res.sys[k]: res.sys[k].remove("reweightPhotonElectronVetoSF")
                        if 'reweightBTag_SF_b_'+upOrDown            in res.sys[k]: res.sys[k].remove('reweightBTag_SF')
                        if 'reweightBTag_SF_l_'+upOrDown            in res.sys[k]: res.sys[k].remove('reweightBTag_SF')
                else:
                    res.sys[k] = sys[k]

        if parameters:
            for k in parameters.keys():
                res.parameters[k] = parameters[k]

        res.isPhotonSelection = res.parameters["nPhoton"][0] != 0
        res.isSignalRegion    = res.parameters["nBTag"][0] == 1 and res.parameters["nPhoton"][0] == 1 and not self.parameters["photonIso"]
        res.nJet = str(res.parameters["nJet"][0])
        if res.parameters["nJet"][1] < 0: res.nJet += "p"
        return res

    def defaultParameters(self, update={} ):
        assert type(update)==type({}), "Update arguments with key arg dictionary. Got this: %r"%update
        res = copy.deepcopy(self.parameters)
        res.update(update)
        return res

    def weightString(self, dataMC, photon="PhotonGood0", addMisIDSF=False):
        _weightString = {}
        _weightString["Data"] = "weight" 
        _weightString["MC"] = "*".join([self.sys["weight"]] + (self.sys["reweight"] if self.sys["reweight"] else []))

        if addMisIDSF and photon:
            if self.nJet == "2p": misIDSF_val   = misID2pSF_val
            elif self.nJet == "3p": misIDSF_val = misID3pSF_val
            elif self.nJet == "4p": misIDSF_val = misID4pSF_val
            elif self.nJet == "2": misIDSF_val  = misID2SF_val
            elif self.nJet == "3": misIDSF_val  = misID3SF_val
            elif self.nJet == "4": misIDSF_val  = misID4SF_val
            elif self.nJet == "5": misIDSF_val  = misID5SF_val

            _weightString["MC"] += "+%s*(%s0_photonCatMagic==2)*(%f-1)" %(_weightString["MC"], photon, misIDSF_val[self.year].val)

        if   dataMC == "DataMC": return _weightString

        if   dataMC == "Data": _weightString = _weightString["Data"]
        elif dataMC == "MC":   _weightString = _weightString["MC"]
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
           dataMC: "Data" or "MC"
           channel: all, e or mu, eetight, mumutight, SFtight
           zWindow: offZeg, onZeg, onZSFllTight, onZSFllgTight or all
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
        assert dataMC in ["Data","MC","DataMC"], "dataMC = Data or MC or DataMC, got %r."%dataMC
        assert channel in allChannels, "channel must be one of "+",".join(allChannels)+". Got %r."%channel
        assert zWindow in ["offZeg", "onZeg", "onZSFllTight", "onZSFllgTight", "all"], "zWindow must be one of onZeg, offZeg, onZSFllTight, onZSFllgTight, all. Got %r"%zWindow
        assert m3Window in ["offM3", "onM3", "all"], "m3Window must be one of onM3, offM3, all. Got %r"%m3Window
        assert photonIso in [None, "highSieieNoChgIso", "lowSieieNoChgIso", "noSieie", "highSieie", "lowChgIsoNoSieie", "highChgIsoNoSieie", "noChgIso", "highChgIso", "noChgIsoNoSieie", "highChgIsohighSieie"], "PhotonIso must be one of highSieie, highChgIso, highChgIsohighSieie. Got %r"%photonIso
        assert processCut in [None, "cat0","cat2","cat13","cat4"], "Process specific cut must be one of cat0, cat2, cat13, cat4. Got %r"%processCut
        if self.sys['selectionModifier']:
            assert self.sys['selectionModifier'] in jmeVariations+metVariations, "Don't know about systematic variation %r, take one of %s"%(self.sys['selectionModifier'], ",".join(jmeVariations+metVariations))

        res={"cuts":[], "prefixes":[]}

        # default lepton selections
        tightLepton  = "nLepTight1"
        vetoLepton   = "nLepVeto1"
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

        if invertLepIso:
            # invert leptonIso in lepton cuts
            channel     += "Inv"
            zWindow     += "Inv"
            tightLepton  = "nInvLepTight1"
            vetoLepton   = "nLepVeto1"
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

            res["prefixes"].append( photonIso )
            preselphotonIso = cutInterpreter.cutString( photonIso )
            res["cuts"].append( preselphotonIso )

        if not photonSel and not dileptonic:
            # remove default zwindow cut in qcd estimation for non photon regions
            zWindow = "all"

        #Postfix for variables (only for MC and if we have a jme variation)
        sysStr = ""
        if dataMC == "MC" and self.sys['selectionModifier'] in jmeVariations + metVariations:
            sysStr = "_" + self.sys['selectionModifier']

        #leptons or inv. iso leptons
        res["prefixes"].append( tightLepton )
        lepSel = cutInterpreter.cutString( tightLepton )
        res["cuts"].append( lepSel )
              
        #lepton channel or inv. iso lepton channel
        res["prefixes"].append( channel )
        chStr = cutInterpreter.cutString( channel )
        res["cuts"].append(chStr)

        #lepton veto or no Iso lepton veto
        res["prefixes"].append( vetoLepton )
        chVetoStr = cutInterpreter.cutString( vetoLepton )
        res["cuts"].append( chVetoStr )

        if nJet and not (nJet[0]==0 and nJet[1]<0):
            assert nJet[0]>=0 and (nJet[1]>=nJet[0] or nJet[1]<0), "Not a good nJet selection: %r"%nJet
            njetsstr = jetCutVar+sysStr+">="+str(nJet[0])
            prefix   = jetPrefix+str(nJet[0])
            if nJet[1]>=0:
                njetsstr+= "&&"+jetCutVar+sysStr+"<="+str(nJet[1])
                if nJet[1]!=nJet[0]: prefix+="To"+str(nJet[1])
            else:
                prefix+="p"
            res["cuts"].append(njetsstr)
            res["prefixes"].append(prefix)

        if nBTag and not (nBTag[0]==0 and nBTag[1]<0):
            assert nBTag[0]>=0 and (nBTag[1]>=nBTag[0] or nBTag[1]<0), "Not a good nBTag selection: %r"% nBTag
            if sysStr: nbtstr = btagCutVar+sysStr+">="+str(nBTag[0])
            else:      nbtstr = btagCutVar+sysStr+">="+str(nBTag[0])
            prefix = btagPrefix+str(nBTag[0])
            if nBTag[1]>=0:
                if sysStr: nbtstr+= "&&"+btagCutVar+sysStr+"<="+str(nBTag[1])
                else:      nbtstr+= "&&"+btagCutVar+sysStr+"<="+str(nBTag[1])
                if nBTag[1]!=nBTag[0]: prefix+="To"+str(nBTag[1])
            else:
                prefix+="p"
            res["cuts"].append(nbtstr)
            res["prefixes"].append(prefix)

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

            if photonVetoCutVar:
                nphotonVetosstr = photonVetoCutVar+">="+str(nPhoton[0])
                prefix          = photonVetoPrefix+str(nPhoton[0])
                if nPhoton[1]>=0:
                    nphotonVetosstr += "&&"+photonVetoCutVar+"<="+str(nPhoton[1])
                    if nPhoton[1] != nPhoton[0]: prefix+="To"+str(nPhoton[1])
                else:
                    prefix+="p"
                res["cuts"].append(nphotonVetosstr)
                res["prefixes"].append(prefix)

        else:
            addMisIDSF   = False
            res["cuts"].append(photonCutVar+"==0")
            res["prefixes"].append(photonPrefix+"0")
            if photonVetoCutVar:
                res["cuts"].append(photonVetoCutVar+"==0")
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
            metsstr = "MET_pt"+sysStr+">="+str(MET[0])
            prefix   = "met"+str(MET[0])
            if MET[1]>=0:
                metsstr+= "&&"+"MET_pt"+sysStr+"<"+str(MET[1])
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

        if processCut:
            catPrefix = photonCatPrefix + processCut.replace("cat","")
            res["prefixes"].append( catPrefix )
            catCut = cutInterpreter.cutString( catPrefix )
            res["cuts"].append( catCut )

        #badEEVeto
#        if self.year == 2017:
#            res["prefixes"].append("BadEEJetVeto")
#            badEEStr = cutInterpreter.cutString( "BadEEJetVeto" )
#            res["cuts"].append( badEEStr )

        if invertLepIso:
            res["cuts"].append( "triggeredInvIso==1" )
        else:
            res["cuts"].append( "triggered==1" )

        res["cuts"].append( "reweightHEM>0" )

        if dataMC == "MC":
            res["cuts"].append( "overlapRemoval==1" )

        if dataMC != "DataMC":
            res["cuts"].append( getFilterCut(isData=(dataMC=="Data"), year=self.year, skipBadChargedCandidate=True) )
            res["cuts"].extend(self.externalCuts)

        return {"cut":"&&".join(res["cuts"]), "prefix":"-".join(res["prefixes"]), "weightStr": self.weightString(dataMC,photon=photonCatVar.split("0")[0] if addMisIDSF else None,addMisIDSF=addMisIDSF and self.isPhotonSelection)}


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
    setup = Setup( year=2016 )
    for name, dict in allRegions.items():
#        if not "wjetsec3" in name.lower() and not "wjetsbarrel3" in name.lower(): continue
        if not "vg4p" in name.lower(): continue
        print
        print name
        print
        setup = setup.sysClone( parameters=dict["parameters"] )
#        setup = setup.sysClone({"selectionModifier":"jerUp"})
        for channel in dict["channels"]:
            print
            print channel
            print
            res = setup.selection("MC", channel=channel, **setup.defaultParameters( update=dict["parameters"] ))
            print res["cut"]
            print res["prefix"]
            print res["weightStr"]



