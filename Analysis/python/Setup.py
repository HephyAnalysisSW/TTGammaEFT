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

#        self.puWeight = "reweightPUVUp" if self.year == 2018 else "reweightPU"
#        self.sys = {"weight":"weight", "reweight":["reweightHEM", "reweightL1Prefire", "reweightPU", "reweightLeptonTightSF", "reweightLeptonTrackingTightSF", "reweightPhotonSF", "reweightPhotonElectronVetoSF", "reweightBTag_SF"], "selectionModifier":None} 
        self.sys = {"weight":"weight", "reweight":["reweightL1Prefire", "reweightPU", "reweightLeptonTightSF", "reweightLeptonTrackingTightSF", "reweightPhotonSF", "reweightPhotonElectronVetoSF", "reweightBTag_SF"], "selectionModifier":None} 

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
        if addMisIDSF and photon: _weightString["MC"] += "+%s*(%s0_photonCat==2)*(%f-1)" %(_weightString["MC"], photon, misIDSF_val[self.year].val)

        if   dataMC == "DataMC": return _weightString

        if   dataMC == "Data": _weightString = _weightString["Data"]
        elif dataMC == "MC":   _weightString = _weightString["MC"]
        logger.debug("Using weight-string: %s", _weightString)

        return _weightString

    def preselection(self, dataMC , channel="all"):
        """Get preselection  cutstring."""
        cut = self.selection(dataMC, channel = channel, **self.parameters)
        logger.debug("Using cut-string: %s", cut)
        return cut

    def selection(self, dataMC,
                        dileptonic=None, invertLepIso=None, addMisIDSF=None,
                        nJet=None, nBTag=None, nPhoton=None,
                        MET=None,
                        zWindow=None, m3Window=None,
                        photonIso=None,
                        channel="all"):
        """Define full selection
           dataMC: "Data" or "MC"
           channel: all, e or mu, eetight, mumutight, SFtight
           zWindow: offZeg, onZeg, onZSFllTight, onZSFllgTight or all
           m3Window: offM3, onM3 or all
           photonIso: lowSieie, highSieie, lowChgIso, highChgIso, lowChgIsolowSieie, highChgIsolowSieie, lowChgIsohighSieie, highChgIsohighSieie
        """
        if not dileptonic:   dileptonic   = self.parameters["dileptonic"]
        if not invertLepIso: invertLepIso = self.parameters["invertLepIso"]
        if not addMisIDSF:   addMisIDSF   = self.parameters["addMisIDSF"]
        if not nJet:         nJet         = self.parameters["nJet"]
        if not nBTag:        nBTag        = self.parameters["nBTag"]
        if not nPhoton:      nPhoton      = self.parameters["nPhoton"]
        if not MET:          MET          = self.parameters["MET"]
        if not zWindow:      zWindow      = self.parameters["zWindow"]
        if not m3Window:     m3Window     = self.parameters["m3Window"]
        if not photonIso:    photonIso    = self.parameters["photonIso"]

        #Consistency checks
        assert dataMC in ["Data","MC","DataMC"], "dataMC = Data or MC or DataMC, got %r."%dataMC
        assert channel in allChannels, "channel must be one of "+",".join(allChannels)+". Got %r."%channel
        assert zWindow in ["offZeg", "onZeg", "onZSFllTight", "onZSFllgTight", "all"], "zWindow must be one of onZeg, offZeg, onZSFllTight, onZSFllgTight, all. Got %r"%zWindow
        assert m3Window in ["offM3", "onM3", "all"], "m3Window must be one of onM3, offM3, all. Got %r"%m3Window
        assert photonIso in [None, "lowSieie", "highSieie", "lowChgIso", "highChgIso", "lowChgIsolowSieie", "highChgIsolowSieie", "lowChgIsohighSieie", "highChgIsohighSieie"], "PhotonIso must be one of lowSieie, highSieie, lowChgIso, highChgIso, lowChgIsolowSieie, highChgIsolowSieie, lowChgIsohighSieie, highChgIsohighSieie. Got %r"%photonIso
        if self.sys['selectionModifier']:
            assert self.sys['selectionModifier'] in jmeVariations+metVariations, "Don't know about systematic variation %r, take one of %s"%(self.sys['selectionModifier'], ",".join(jmeVariations+metVariations))

        # default lepton selections
        tightLepton = "nLepTight1"
        vetoLepton = "nLepVeto1"

        if invertLepIso:
            # invert leptonIso in lepton cuts
            channel += "Inv"
            zWindow += "Inv"
            tightLepton = "nInvLepTight1"
#            vetoLepton = "nInvLeptVetoTight1"
            vetoLepton = "nNoIsoLepVeto1"

        if dileptonic:
            tightLepton = "nLepTight2-OStight"
            vetoLepton = "nLepVeto2"

        #Postfix for variables (only for MC and if we have a jme variation)
        sysStr = ""
        if dataMC == "MC" and self.sys['selectionModifier'] in jmeVariations + metVariations:
            sysStr = "_" + self.sys['selectionModifier']

        res={"cuts":[], "prefixes":[]}

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
            njetsstr = "nJetGood"+sysStr+">="+str(nJet[0])
            prefix   = "nJet"+str(nJet[0])
            if nJet[1]>=0:
                njetsstr+= "&&"+"nJetGood"+sysStr+"<="+str(nJet[1])
                if nJet[1]!=nJet[0]: prefix+=str(nJet[1])
#                if nJet[1]!=nJet[0]: prefix+="To"+str(nJet[1])
            else:
                prefix+="p"
            res["cuts"].append(njetsstr)
            res["prefixes"].append(prefix)

        if nBTag and not (nBTag[0]==0 and nBTag[1]<0):
            assert nBTag[0]>=0 and (nBTag[1]>=nBTag[0] or nBTag[1]<0), "Not a good nBTag selection: %r"% nBTag
            if sysStr: nbtstr = "nBTagGood"+sysStr+">="+str(nBTag[0])
            else:      nbtstr = "nBTagGood"+sysStr+">="+str(nBTag[0])
            prefix = "nBTag"+str(nBTag[0])
            if nBTag[1]>=0:
                if sysStr: nbtstr+= "&&nBTagGood"+sysStr+"<="+str(nBTag[1])
                else:      nbtstr+= "&&nBTagGood"+sysStr+"<="+str(nBTag[1])
                if nBTag[1]!=nBTag[0]: prefix+=str(nBTag[1])
#                if nBTag[1]!=nBTag[0]: prefix+="To"+str(nBTag[1])
            else:
                prefix+="p"
            res["cuts"].append(nbtstr)
            res["prefixes"].append(prefix)

        #photon cut
        photonSel = nPhoton and not (nPhoton[0]==0 and nPhoton[1]<=0)

        if photonSel:
            #photonIso of leading photon
            if not photonIso or photonIso == "lowChgIsolowSieie":
                photonCutVar = "nPhotonGood"
                photonPrefix = "nPhoton"
                # no special photon iso cut needed
            else:
                photonCutVar = "nPhotonNoChgIsoNoSieie"
                photonPrefix = "nHadPhoton"
                
                res["prefixes"].append( photonIso )
                preselphotonIso = cutInterpreter.cutString( photonIso )
                res["cuts"].append( preselphotonIso )

            #photon cut
            assert nPhoton[0]>=0 and (nPhoton[1]>=nPhoton[0] or nPhoton[1]<0), "Not a good nPhoton selection: %r"%nPhoton
            nphotonsstr = photonCutVar+">="+str(nPhoton[0])
            prefix   = photonPrefix+str(nPhoton[0])
            if nPhoton[1]>=0:
                nphotonsstr+= "&&"+photonCutVar+"<="+str(nPhoton[1])
                if nPhoton[1]!=nPhoton[0]: prefix+="To"+str(nPhoton[1])
            else:
                prefix+="p"
            res["cuts"].append(nphotonsstr)
            res["prefixes"].append(prefix)
        else:
            addMisIDSF   = False

        if not photonSel or (photonCutVar=="nPhotonNoChgIsoNoSieie"):
            # remove default zwindow cut in qcd estimation for non photon regions
            zWindow = "all"

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

        #badEEVeto
#        if self.year == 2017 and photonSel:
#            res["prefixes"].append("BadEEJetVeto")
#            badEEStr = cutInterpreter.cutString( "BadEEJetVeto" )
#            res["cuts"].append( badEEStr )

        if dataMC == "MC":
            res["cuts"].append( "overlapRemoval==1" )
#            res["prefixes"].append( "overlapRemoval" )

#            tr            = TriggerSelector( self.year, singleLepton=(not dileptonic) )
            tr            = TriggerSelector( self.year, singleLepton=True )
            triggerCutMc  = tr.getSelection( "MC" )

            res["cuts"].append( triggerCutMc )
#            res["prefixes"].append( "trigger" )


#        if dataMC=="Data" and self.year == 2018:
#            res["cuts"].append("reweightHEM>0")

        if dataMC != "DataMC":
            res["cuts"].append( getFilterCut(isData=(dataMC=="Data"), year=self.year, skipBadChargedCandidate=True) )
            res["cuts"].extend(self.externalCuts)

        return {"cut":"&&".join(res["cuts"]), "prefix":"-".join(res["prefixes"]), "weightStr": self.weightString(dataMC,photon=str(photonCutVar[1:]) if addMisIDSF else None,addMisIDSF=addMisIDSF and self.isPhotonSelection)}

if __name__ == "__main__":
    setup = Setup( year=2016 )
    for name, dict in allRegions.items():
        if not "Iso" in name: continue
        print
        print name
        print
        for channel in dict["channels"]:
            print
            print channel
            print
            res = setup.selection("MC", channel=channel, **setup.defaultParameters( update={"MET":(0,30)} ))
            print res["cut"]
            print res["prefix"]
            print res["weightStr"]

            print
            res = setup.selection("Data", channel=channel, **setup.defaultParameters( update=dict["parameters"] ))
            print res["cut"]
            print res["prefix"]
            print res["weightStr"]


