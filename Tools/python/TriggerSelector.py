
class TriggerSelector:
    def __init__( self, year ):

        # https://twiki.cern.ch/twiki/bin/view/CMS/TopTrigger
        if year == 2016:
                self.m  = [ "HLT_IsoMu24", "HLT_IsoTkMu24" ]
                self.e  = [ "HLT_Ele27_WPTight_Gsf" ]
        elif year == 2017:
                self.m   = [ "HLT_IsoMu27" ]
                self.e   = [ "HLT_Ele32_WPTight_Gsf_L1DoubleEG" ]
#                self.e   = [ "HLT_Ele32_WPTight_Gsf", "HLT_Ele32_WPTight_Gsf_L1DoubleEG" ]
                self.eL1 = [ "L1_SingleEG24", "L1_SingleEG26", "L1_SingleEG30", "L1_SingleEG32", "L1_SingleEG34", "L1_SingleEG36", "L1_SingleEG38", "L1_SingleEG40", "L1_SingleEG42", "L1_SingleEG45", "L1_SingleEG50", "L1_SingleEG34er2p1", "L1_SingleEG36er2p1", "L1_SingleEG38er2p1", "L1_SingleIsoEG24er2p1", "L1_SingleIsoEG26er2p1", "L1_SingleIsoEG28er2p1", "L1_SingleIsoEG30er2p1", "L1_SingleIsoEG32er2p1", "L1_SingleIsoEG34er2p1", "L1_SingleIsoEG36er2p1", "L1_SingleIsoEG24", "L1_SingleIsoEG26", "L1_SingleIsoEG28", "L1_SingleIsoEG30", "L1_SingleIsoEG32", "L1_SingleIsoEG34", "L1_SingleIsoEG36", "L1_SingleIsoEG38"]
        elif year == 2018:
                self.m  = [ "HLT_IsoMu24" ]
                self.e  = [ "HLT_Ele32_WPTight_Gsf" ]
        else:
            raise NotImplementedError( "Trigger selection %r not implemented" %year )

        self.year = year
        self.SingleMuon     = "("+"||".join( self.m  )+")"
        self.SingleElectron = "("+"||".join( self.e  )+")"
        if self.year == 2017:
            self.SingleElectron += "&&("+"||".join( ["Alt$(%s,0)"%trigger for trigger in self.eL1] )+")"
        elif self.year == 2018:
            self.EGamma         = self.SingleElectron

    def getDataTrigger( self, PD ):
        # define which triggers should be used for which dataset
        cutString = getattr( self, PD.split("_")[0] )
        return cutString

    def getTriggerVariableList( self ):
        if self.year == 2017:
            return [ trigger + "/O" for trigger in self.m+self.e+self.eL1 ]
        else:
            return [ trigger + "/O" for trigger in self.m+self.e ]

    def getSelection( self ):
        return "(triggered==1)"

    def getTriggerDecision( self, pdgId ):
        if   abs(pdgId) == 11: triggerList = self.e
        elif abs(pdgId) == 13: triggerList = self.m
        else:                  triggerList = []

        if self.year == 2017 and abs(pdgId) == 11:
            # check L1 trigger for e-trigger in 2017 as recommended in TopTrigger
            def func( event ):
                for tr in triggerList:
                    if getattr( event, tr ):
                        for lTr in self.eL1:
                            if getattr( event, lTr ): return True
                return False
        else:
            def func( event ):
                for tr in triggerList:
                    if getattr( event, tr ): return True
                return False

        return func

if __name__=="__main__":
    tr = TriggerSelector(2017)
    print tr.getDataTrigger( "SingleElectron" )
