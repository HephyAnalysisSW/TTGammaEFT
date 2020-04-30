
class TriggerSelector:
    def __init__( self, year ):

        # https://twiki.cern.ch/twiki/bin/view/CMS/TopTrigger
        if year == 2016:
                self.m  = [ "HLT_IsoMu24", "HLT_IsoTkMu24" ]
                self.e  = [ "HLT_Ele27_WPTight_Gsf" ]
        elif year == 2017:
                self.m  = [ "HLT_IsoMu24" ]
                self.e  = [ "HLT_Ele32_WPTight_Gsf", "HLT_Ele32_WPTight_Gsf_L1DoubleEG" ]
        elif year == 2018:
                self.m  = [ "HLT_IsoMu24" ]
                self.e  = [ "HLT_Ele32_WPTight_Gsf" ]
        else:
            raise NotImplementedError( "Trigger selection %r not implemented" %year )

        # define an arbitrary hierarchy
        self.PDHierarchy = [ "SingleMuon", "EGamma" if year == 2018 else "SingleElectron" ]

        # define which triggers should be used for which dataset
        self.SingleMuon     = "(%s)"%"||".join( ["Alt$(%s,0)"%trigger for trigger in self.m]  )
        self.SingleElectron = "(%s)"%"||".join( ["Alt$(%s,0)"%trigger for trigger in self.e]  )
        self.EGamma         = self.SingleElectron

    def __getVeto( self, cutString ):
        return "!%s" %cutString

    def getDataTrigger( self, PD ):
        cutString = getattr( self, PD.split("_")[0] )
        return cutString
#        for x in self.PDHierarchy:
#            if x in PD: continue
#            cutString += "&&!"
#            cutString += getattr( self, x )
#        return "(%s)" %cutString

    def getTriggerVariableList( self ):
        return [ trigger + "/O" for trigger in self.m+self.e ]

    def getSelection( self ):
        return "(triggered==1)"

    def getTriggerDecision( self, pdgId ):
        if   abs(pdgId) == 11: triggerList = self.e
        elif abs(pdgId) == 13: triggerList = self.m
        else:                  triggerList = []

        def func( event ):
            for tr in triggerList:
                if getattr( event, tr ): return True
            return False

        return func


if __name__=="__main__":
    tr            = TriggerSelector( 2016, singleLepton=True )
    triggerCutMc  = tr.getSelection( "MC" )
    print triggerCutMc
    Ts          = TriggerSelector( 2016, singleLepton=True )
    triggerCond = Ts.getSelection( "SingleMuon" )
    print triggerCond
