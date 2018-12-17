# Problems with HLT_DoubleEle33_CaloIdL_GsfTrkIdVL, HLT_TkMu50 and HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL

class TriggerSelector:
    def __init__( self, year ):
        if year == 2016:
            self.mm     = [ "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL", "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ", "HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL", "HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ", "HLT_Mu30_TkMu11" ]
#            self.m      = [ "HLT_IsoMu24", "HLT_IsoTkMu24", "HLT_Mu50", "HLT_TkMu50", "HLT_Mu45_eta2p1" ] #HLT_IsoTkMu24, HLT_IsoMu24
            self.m      = [ "HLT_IsoMu24", "HLT_IsoTkMu24", "HLT_Mu50", "HLT_Mu45_eta2p1" ] #HLT_IsoTkMu24, HLT_IsoMu24
#            self.ee     = [ "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_DoubleEle33_CaloIdL_GsfTrkIdVL", "HLT_DoubleEle33_CaloIdL_GsfTrkIdVL_MW" ]
            self.ee     = [ "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_DoubleEle33_CaloIdL_GsfTrkIdVL_MW" ]
            self.e      = [ "HLT_Ele27_WPTight_Gsf", "HLT_Ele105_CaloIdVT_GsfTrkIdT", "HLT_Ele115_CaloIdVT_GsfTrkIdT" ] #HLT_Ele105_CaloIdVT_GsfTrkIdT
#            self.em     = [ "HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL", "HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL", "HLT_Mu17_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL", "HLT_Mu8_TrkIsoVVL_Ele17_CaloIdL_TrackIdL_IsoVL", "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL", "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu30_Ele30_CaloIdL_GsfTrkIdVL" ]
            self.em     = [ "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL", "HLT_Mu17_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL", "HLT_Mu8_TrkIsoVVL_Ele17_CaloIdL_TrackIdL_IsoVL"]

        # not adapted yet
        elif year == 2017:
            self.mm     = ["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ", "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8"] # "HLT_Mu37_TkMu27" not in nanoAOD
            self.m      = ["HLT_IsoMu27", "HLT_Mu50"]
            self.ee     = ["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL", "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"]
            self.e      = ["HLT_Ele35_WPTight_Gsf", "HLT_Ele32_WPTight_Gsf_L1DoubleEG"] # add single photon trigger? "HLT_Ele115_CaloIdVT_GsfTrkIdT" missing
            self.em     = ["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"]

        # not adapted yet
        elif year == 2018:
            self.mm     = ["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8", "HLT_Mu37_TkMu27"]
            self.m      = ["HLT_IsoMu24", "HLT_IsoMu27", "HLT_Mu50"]
            self.ee     = ["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL", "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"]
            self.e      = ["HLT_Ele32_WPTight_Gsf", "HLT_Ele115_CaloIdVT_GsfTrkIdT", "HLT_Ele32_WPTight_Gsf_L1DoubleEG"]
            self.em     = ["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Mu27_Ele37_CaloIdL_MW", "HLT_Mu37_Ele27_CaloIdL_MW"]

        else:
            raise NotImplementedError( "Trigger selection %r not implemented" %year )

        # define which triggers should be used for which dataset
        self.DoubleMuon     = "(%s)"%"||".join( self.mm )
        self.DoubleEG       = "(%s)"%"||".join( self.ee )
        self.MuonEG         = "(%s)"%"||".join( self.em )
        self.SingleMuon     = "(%s)"%"||".join( self.m  )
        self.SingleElectron = "(%s)"%"||".join( self.e  )

        # define an arbitrary hierarchy
        self.PDHierarchy = [ "DoubleMuon", "DoubleEG", "MuonEG", "SingleMuon", "SingleElectron" ]

    def __getVeto( self, cutString ):
        return "!%s" %cutString

    def getSelection( self, PD ):
        found     = False
        cutString = ""

        if PD == "MC":
            return "(%s)"%"||".join( [ self.DoubleMuon, self.DoubleEG, self.MuonEG, self.SingleMuon, self.SingleElectron ] )
        else:
            for x in reversed( self.PDHierarchy ):
                if found:
                    cutString += "&&%s" %self.__getVeto( getattr( self, x ) )
                if x in PD:
                    found     = True
                    cutString = getattr( self, x )

            return "(%s)" %cutString

#tr = TriggerSelector(2017)
#print tr.mm + tr.m + tr.ee + tr.e + tr.em
