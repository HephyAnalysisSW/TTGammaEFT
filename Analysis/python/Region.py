allowedVars = [ "ltight0GammaNoSieieNoChgIsodPhi", "ltight0GammadPhi", "ltight0GammaNoSieieNoChgIsodR", "photonNoSieieNoChgIsoJetdR", "photonJetdR", "ltight0GammadR", "mLtight0Gamma", "PhotonNoChgIsoNoSieie0_pt", "PhotonNoChgIsoNoSieie0_eta", "abs(PhotonNoChgIsoNoSieie0_eta)", "PhotonInvChgIsoInvSieie0_pt", "PhotonInvSieie0_pt", "PhotonInvChgIso0_pt", "PhotonGood0_eta", "abs(PhotonGood0_eta)", "PhotonGood0_pt", "GenPhoton_pt[0]", "Jet_eta", "Jet_pt", "Jet_phi", "nPhotonGood", "m3", "(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)" ]
texString   = { "photonNoSieieNoChgIsoJetdR":"#DeltaR(#gamma,j)", "photonJetdR":"#DeltaR(#gamma,j)", "ltight0GammaNoSieieNoChgIsodPhi":"#Delta#Phi(#gamma,l)", "ltight0GammadPhi":"#Delta#Phi(#gamma,l)", "ltight0GammaNoSieieNoChgIsodR":"#DeltaR(#gamma,l)", "ltight0GammadR":"#DeltaR(#gamma,l)", "nPhotonGood":"N_{#gamma}", "mLtight0Gamma":"M(l,#gamma)", "PhotonNoChgIsoNoSieie0_pt":"p_{T}(#gamma)", "PhotonNoChgIsoNoSieie0_eta":"#eta(#gamma)", "abs(PhotonNoChgIsoNoSieie0_eta)":"|#eta(#gamma)|", "PhotonInvChgIsoInvSieie0_pt":"p_{T}(#gamma)", "PhotonInvChgIso0_pt":"p_{T}(#gamma)", "PhotonInvSieie0_pt":"p_{T}(#gamma)",  "PhotonGood0_eta":"#eta(#gamma)", "abs(PhotonGood0_eta)":"|#eta(#gamma)|", "PhotonGood0_pt":"p_{T}(#gamma)", "GenPhoton_pt[0]":"p_{T}(#gamma)", "Jet_eta":"#eta(jets)", "Jet_pt":"p_{T}(jets)", "Jet_phi":"#phi(jets)", "(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)":"chg Iso(#gamma_{0})", "m3":"M_{3}" }

aliases     = { "PhotonGood0_pt":"genLepZ_pt", "nPhotonGood":"genLepZ_cosThetaStar", "m3":"gen_m3", "PhotonNoChgIsoNoSieie0_pt":"" }

jes  = ["FlavorQCD", "RelativeBal", "HF", "BBEC1", "EC2", "Absolute", "Total"]
jes += ["Absolute_%i"%year       for year in [2016,2107,2018]]
jes += ["HF_%i"%year             for year in [2016,2107,2018]]
jes += ["EC2_%i"%year            for year in [2016,2107,2018]]
jes += ["RelativeSample_%i"%year for year in [2016,2107,2018]]
jes += ["BBEC1_%i"%year          for year in [2016,2107,2018]]
jesVar = ["jes"+j+"Up" for j in jes] + ["jes"+j+"Down" for j in jes]

systematicReplacements = {}
systematicReplacements["eScaleUp"]    = ["PhotonGood0","PhotonNoChgIsoNoSieie0","LeptonTight0","mllgammatight","mLtight0GammaNoSieieNoChgIso","mLtight0Gamma","mLinvtight0GammaNoSieieNoChgIso","mLinvtight0Gamma","mlltight"]
systematicReplacements["eScaleDown"]  = ["PhotonGood0","PhotonNoChgIsoNoSieie0","LeptonTight0","mllgammatight","mLtight0GammaNoSieieNoChgIso","mLtight0Gamma","mLinvtight0GammaNoSieieNoChgIso","mLinvtight0Gamma","mlltight"]
systematicReplacements["eResUp"]      = ["PhotonGood0","PhotonNoChgIsoNoSieie0","LeptonTight0","mllgammatight","mLtight0GammaNoSieieNoChgIso","mLtight0Gamma","mLinvtight0GammaNoSieieNoChgIso","mLinvtight0Gamma","mlltight"]
systematicReplacements["eResDown"]    = ["PhotonGood0","PhotonNoChgIsoNoSieie0","LeptonTight0","mllgammatight","mLtight0GammaNoSieieNoChgIso","mLtight0Gamma","mLinvtight0GammaNoSieieNoChgIso","mLinvtight0Gamma","mlltight"]
systematicReplacements["muTotalUp"]   = ["LeptonTight0","mllgammatight","mLtight0GammaNoSieieNoChgIso","mLtight0Gamma","mLinvtight0GammaNoSieieNoChgIso","mLinvtight0Gamma","mlltight"]
systematicReplacements["muTotalDown"] = ["LeptonTight0","mllgammatight","mLtight0GammaNoSieieNoChgIso","mLtight0Gamma","mLinvtight0GammaNoSieieNoChgIso","mLinvtight0Gamma","mlltight"]
for var in ["jerUp", "jerDown"] + jesVar:
    systematicReplacements[var] = ["m3"]

class Region:

    def __init__(self, var, val):
        assert type(val)==type(()) and len(val)==2, "Don't know how to make region with this val argument: %r."%val
        assert var in allowedVars, "Use only these variables: %r"%allowedVars
        self.vals = {var:val}

    def variables(self):
        return self.vals.keys()

    def __iadd__(self, otherRegion):
        if not type(self)==type(otherRegion): raise TypeError("Can't add this type to a region %r"%type(otherRegion))
        for v in otherRegion.vals.keys():
            assert v not in self.vals.keys(), "Can't add regions, variable %s in both summands!"%v
        self.vals.update(otherRegion.vals)
        return self

    def __add__(self, otherRegion):
        if not type(self)==type(otherRegion): raise TypeError("Can't add this type to a region %r"%type(otherRegion))
        for v in otherRegion.vals.keys():
            assert v not in self.variables(), "Can't add regions, variable %s in both summands!"%v
        import copy
        res=copy.deepcopy(self)
        res.vals.update(otherRegion.vals)
        return res

    def cutString(self, selectionModifier=None):
        sysStr = ""
        if selectionModifier in systematicReplacements.keys():
            sysStr = "_" + selectionModifier
        res=[]
        for var in self.variables():
            svar = var
            if selectionModifier and sysStr and any( [s in var for s in systematicReplacements[selectionModifier] ] ):
                for s in systematicReplacements[selectionModifier]:
                    if s in var: svar=svar.replace(s,s+sysStr)
            s1=svar+">="+str(self.vals[var][0])
            if self.vals[var][1]>-999: s1+="&&"+svar+"<"+str(self.vals[var][1])
            res.append(s1)
        return "&&".join(res)

    def texStringForVar(self, var = None, useRootLatex = True):
        if var not in self.variables(): return None
        s1 = str(self.vals[var][0]) + (" #leq " if useRootLatex else " \\leq ") + texString[var]
        if self.vals[var][1]>-999: s1+=" < "+str(self.vals[var][1])
        return s1

    def simpleStringForVar(self, var = None):
        if var not in self.variables(): return None
        s1 = str(self.vals[var][0])
        if self.vals[var][1]>-999: s1+="To"+str(self.vals[var][1])
        return var+s1


    def texString(self, useRootLatex = True):
        res=[]
        for var in allowedVars: #Always keep the sequence in allowedVars
            if var in self.variables():
                res.append(self.texStringForVar(var, useRootLatex))
        return ", ".join(res)

    def __str__(self):
        res=[]
        for var in allowedVars: #Always keep the sequence in allowedVars
            if var in self.variables():
                res.append(self.simpleStringForVar(var))
        return "_".join(res)
        #return self.cutString()

    def __repr__(self):
        """ Sorry."""
        return "+".join([ "Region('%s', %r)"%(v, self.vals[v]) for v in self.variables()])

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return self.__repr__() == other.__repr__()
