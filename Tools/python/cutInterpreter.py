''' Class to interpret string based cuts
'''

# TTGamma Imports
from Analysis.Tools.CutInterpreter import CutInterpreter

mZ              = 91.1876
mT              = 172.5
zMassRange      = 10
m3MassRange     = 50
mLgThresh       = mZ + zMassRange
isoThresh       = 2.2
chgIsoThresh    = 1.141
lowSieieThresh  = 0.01015
highSieieThresh = 0.011

special_cuts = {
    "OS":                "(LeptonGood0_pdgId*LeptonGood1_pdgId)<0",
    "OStight":           "(LeptonTight0_pdgId*LeptonTight1_pdgId)<0",
    "dilep":             "nLeptonGood==2&&nLeptonGoodLead>=1",
    "dilepOS":           "nLeptonGood==2&&nLeptonGoodLead>=1&&(LeptonGood0_pdgId*LeptonGood1_pdgId)<0",
    "dilepSS":           "nLeptonGood==2&&nLeptonGoodLead>=1&&(LeptonGood0_pdgId*LeptonGood1_pdgId)>0",
    "dilepOFOS":         "nLeptonGood==2&&nLeptonGoodLead>=1&&(LeptonGood0_pdgId*LeptonGood1_pdgId)<0&&nElectronGood==1&&nMuonGood==1",
    "dilepOFSS":         "nLeptonGood==2&&nLeptonGoodLead>=1&&(LeptonGood0_pdgId*LeptonGood1_pdgId)>0&&nElectronGood==1&&nMuonGood==1",
    "dilepSFOS":         "nLeptonGood==2&&nLeptonGoodLead>=1&&(LeptonGood0_pdgId*LeptonGood1_pdgId)<0&&(nElectronGood==2||nMuonGood==2)",
    "dilepSFSS":         "nLeptonGood==2&&nLeptonGoodLead>=1&&(LeptonGood0_pdgId*LeptonGood1_pdgId)>0&&(nElectronGood==2||nMuonGood==2)",
    "offZll":            "abs(mll-%s)>%s"%(mZ, zMassRange),
    "offZllg":           "abs(mllgamma-%s)>%s"%(mZ, zMassRange),

    "offZllgMVA":               "abs(mllgammaMVA-%s)>%s"%(mZ, zMassRange),
    "offZllgNoChgIso":          "abs(mllgammaNoChgIso-%s)>%s"%(mZ, zMassRange),
    "offZllgNoSieie":           "abs(mllgammaNoSieie-%s)>%s"%(mZ, zMassRange),
    "offZllgNoChgIsoNoSieie":   "abs(mllgammaNoChgIsoNoSieie-%s)>%s"%(mZ, zMassRange),

    "offZllTight":       "abs(mlltight-%s)>%s"%(mZ, zMassRange),
    "offZllgTight":      "abs(mllgammatight-%s)>%s"%(mZ, zMassRange),
    "offZSFll":          "((abs(mll-%s)>%s&&(nElectronGood==2||nMuonGood==2))||(nElectronGood==1&&nMuonGood==1))"%(mZ, zMassRange),                      # Cut Z-Window only for SF dilep events
    "offZSFllg":         "((abs(mllgamma-%s)>%s&&(nElectronGood==2||nMuonGood==2))||(nElectronGood==1&&nMuonGood==1))"%(mZ, zMassRange),                 # Cut Z-Window only for SF dilep events

    "offZSFllgMVA":             "((abs(mllgammaMVA-%s)>%s&&(nElectronGood==2||nMuonGood==2))||(nElectronGood==1&&nMuonGood==1))"%(mZ, zMassRange),                 # Cut Z-Window only for SF dilep events
    "offZSFllgNoChgIso":        "((abs(mllgammaNoChgIso-%s)>%s&&(nElectronGood==2||nMuonGood==2))||(nElectronGood==1&&nMuonGood==1))"%(mZ, zMassRange),                 # Cut Z-Window only for SF dilep events
    "offZSFllgNoSieie":         "((abs(mllgammaNoSieie-%s)>%s&&(nElectronGood==2||nMuonGood==2))||(nElectronGood==1&&nMuonGood==1))"%(mZ, zMassRange),                 # Cut Z-Window only for SF dilep events
    "offZSFllgNoChgIsoNoSieie": "((abs(mllgammaNoChgIsoNoSieie-%s)>%s&&(nElectronGood==2||nMuonGood==2))||(nElectronGood==1&&nMuonGood==1))"%(mZ, zMassRange),                 # Cut Z-Window only for SF dilep events

    "offZSFllTight":     "((abs(mlltight-%s)>%s&&(nElectronTight==2||nMuonTight==2))||(nElectronTight==1&&nMuonTight==1))"%(mZ, zMassRange),             # Cut Z-Window only for SF dilep events
    "offZSFllgTight":    "((abs(mllgammatight-%s)>%s&&(nElectronTight==2||nMuonTight==2))||(nElectronTight==1&&nMuonTight==1))"%(mZ, zMassRange),        # Cut Z-Window only for SF dilep events
    "onZll":             "abs(mll-%s)<=%s"%(mZ, zMassRange),
    "onZllg":            "abs(mllgamma-%s)<=%s"%(mZ, zMassRange),

    "onZllgMVA":               "abs(mllgammaMVA-%s)<=%s"%(mZ, zMassRange),
    "onZllgNoChgIso":          "abs(mllgammaNoChgIso-%s)<=%s"%(mZ, zMassRange),
    "onZllgNoSieie":           "abs(mllgammaNoSieie-%s)<=%s"%(mZ, zMassRange),
    "onZllgNoChgIsoNoSieie":   "abs(mllgammaNoChgIsoNoSieie-%s)<=%s"%(mZ, zMassRange),

    "onZllTight":        "abs(mlltight-%s)<=%s"%(mZ, zMassRange),
    "onZllgTight":       "abs(mllgammatight-%s)<=%s"%(mZ, zMassRange),
    "onZSFll":           "((abs(mll-%s)<=%s&&(nElectronGood==2||nMuonGood==2))||(nElectronGood==1&&nMuonGood==1))"%(mZ, zMassRange),                     # Cut Z-Window only for SF dilep events
    "onZSFllg":          "((abs(mllgamma-%s)<=%s&&(nElectronGood==2||nMuonGood==2))||(nElectronGood==1&&nMuonGood==1))"%(mZ, zMassRange),                # Cut Z-Window only for SF dilep events

    "onZSFllgMVA":             "((abs(mllgammaMVA-%s)<=%s&&(nElectronGood==2||nMuonGood==2))||(nElectronGood==1&&nMuonGood==1))"%(mZ, zMassRange),                 # Cut Z-Window only for SF dilep events
    "onZSFllgNoChgIso":        "((abs(mllgammaNoChgIso-%s)<=%s&&(nElectronGood==2||nMuonGood==2))||(nElectronGood==1&&nMuonGood==1))"%(mZ, zMassRange),                 # Cut Z-Window only for SF dilep events
    "onZSFllgNoSieie":         "((abs(mllgammaNoSieie-%s)<=%s&&(nElectronGood==2||nMuonGood==2))||(nElectronGood==1&&nMuonGood==1))"%(mZ, zMassRange),                 # Cut Z-Window only for SF dilep events
    "onZSFllgNoChgIsoNoSieie": "((abs(mllgammaNoChgIsoNoSieie-%s)<=%s&&(nElectronGood==2||nMuonGood==2))||(nElectronGood==1&&nMuonGood==1))"%(mZ, zMassRange),                 # Cut Z-Window only for SF dilep events

    "onZSFllTight":      "((abs(mlltight-%s)<=%s&&(nElectronTight==2||nMuonTight==2))||(nElectronTight==1&&nMuonTight==1))"%(mZ, zMassRange),            # Cut Z-Window only for SF dilep events
    "onZSFllgTight":     "((abs(mllgammatight-%s)<=%s&&(nElectronTight==2||nMuonTight==2))||(nElectronTight==1&&nMuonTight==1))"%(mZ, zMassRange),       # Cut Z-Window only for SF dilep events
    "mumu":              "nElectronGood==0&&nMuonGood==2",
    "mue":               "nElectronGood==1&&nMuonGood==1",
    "ee":                "nElectronGood==2&&nMuonGood==0",
    "all":               "(1)",
    "SF":                "(nElectronGood==2||nMuonGood==2)",
    "mumutight":         "nElectronTight==0&&nMuonTight==2",
    "muetight":          "nElectronTight==1&&nMuonTight==1",
    "eetight":           "nElectronTight==2&&nMuonTight==0",
    "SFtight":           "(nElectronTight==2||nMuonTight==2)",
    "trigger":           "(1)",

    "onM3":              "abs(m3-%s)<=%s"%(mT, m3MassRange),
    "offM3":             "abs(m3-%s)>%s"%(mT, m3MassRange),

    "MVAPhoton":             "nPhotonMVA>=1",
    "NoSieiePhoton":         "nPhotonNoSieie>=1",
    "NoChgIsoPhoton":        "nPhotonNoChgIso>=1",
    "NoChgIsoNoSieiePhoton": "nPhotonNoChgIsoNoSieie>=1",

    "offZegInv":            "((abs(mLinvtight0Gamma-%s)>%s&&nElectronTightInvIso==1)||(nElectronTightInvIso==0))"%(mZ, zMassRange),             # Cut Z-Window only for egamma
    "onZegInv":             "((abs(mLinvtight0Gamma-%s)<=%s&&nElectronTightInvIso==1)||(nElectronTightInvIso==0))"%(mZ, zMassRange),             # Cut Z-Window only for egamma
    "muInv":                "nMuonTightInvIso==1",
    "eInv":                 "nElectronTightInvIso==1",
    "allInv":               "(1)",

    "muNoIso":                "nMuonTightNoIso==1",
    "eNoIso":                 "nElectronTightNoIso==1",
    
    "offZeg":               "((abs(mLtight0Gamma-%s)>%s&&nElectronTight==1)||(nElectronTight==0))"%(mZ, zMassRange),             # Cut Z-Window only for egamma
    "onZeg":                "((abs(mLtight0Gamma-%s)<=%s&&nElectronTight==1)||(nElectronTight==0))"%(mZ, zMassRange),             # Cut Z-Window only for egamma
    "mu":                   "nMuonTight==1",
    "e":                    "nElectronTight==1",
    "all":                  "(1)",

    "phiGlt1p1":             "abs(PhotonGood0_phi)<1.1",
    "onZEphiGlt1p1":         "((abs(mLtight0Gamma-%s)<=%s&&abs(PhotonGood0_phi)<1.1&&nElectronTight==1)||(abs(mLtight0Gamma-%s)>%s&&nElectronTight==1)||(nElectronTight==0))"%(mZ,zMassRange,mZ,zMassRange),

    "n12Jet":               "nJetGood==1||nJetGood==2",

    "lowSieie":          "PhotonNoChgIsoNoSieie0_sieie<%f"%lowSieieThresh,
    "highSieie":         "PhotonNoChgIsoNoSieie0_sieie>=%f"%highSieieThresh,
    "lowChgIso":         "(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)<%f"%chgIsoThresh,
    "highChgIso":        "(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)>=%f"%chgIsoThresh,

    "lowChgIsolowSieie":   "(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)<%f&&PhotonNoChgIsoNoSieie0_sieie<%f"%(chgIsoThresh,lowSieieThresh),
    "highChgIsolowSieie":  "(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)>=%f&&PhotonNoChgIsoNoSieie0_sieie<%f"%(chgIsoThresh,lowSieieThresh),
    "lowChgIsohighSieie":  "(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)<%f&&PhotonNoChgIsoNoSieie0_sieie>=%f"%(chgIsoThresh,highSieieThresh),
    "highChgIsohighSieie": "(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)>=%f&&PhotonNoChgIsoNoSieie0_sieie>=%f"%(chgIsoThresh,highSieieThresh),

    "lowPT":             "PhotonGood0_pt>=20&&PhotonGood0_pt<120",
    "medPT":             "PhotonGood0_pt>=120&&PhotonGood0_pt<220",
    "highPT":            "PhotonGood0_pt>=220",
    "incl":              "PhotonGood0_pt>=20",

    "lowhadPT":          "PhotonNoChgIsoNoSieie0_pt>=20&&PhotonNoChgIsoNoSieie0_pt<120",
    "medhadPT":          "PhotonNoChgIsoNoSieie0_pt>=120&&PhotonNoChgIsoNoSieie0_pt<220",
    "highhadPT":         "PhotonNoChgIsoNoSieie0_pt>=220",
    "inclhad":           "PhotonNoChgIsoNoSieie0_pt>=20",

    "photoncat0":        "PhotonGood0_photonCat==0",
    "photoncat1":        "PhotonGood0_photonCat==1",
    "photoncat2":        "PhotonGood0_photonCat==2",
    "photoncat3":        "PhotonGood0_photonCat==3",
    "photoncat13":       "(PhotonGood0_photonCat==1||PhotonGood0_photonCat==3)",

    "photonhadcat0":        "PhotonNoChgIsoNoSieie0_photonCat==0",
    "photonhadcat1":        "PhotonNoChgIsoNoSieie0_photonCat==1",
    "photonhadcat2":        "PhotonNoChgIsoNoSieie0_photonCat==2",
    "photonhadcat3":        "PhotonNoChgIsoNoSieie0_photonCat==3",
    "photonhadcat13":       "(PhotonNoChgIsoNoSieie0_photonCat==1||PhotonNoChgIsoNoSieie0_photonCat==3)",

    "looseGenMatch":          "PhotonNoChgIsoNoSieie0_genPartIdx>=0",
    "genMatch":               "PhotonGood0_genPartIdx>=0",
    "noLooseGenMatch":        "PhotonNoChgIsoNoSieie0_genPartIdx<0",
    "noGenMatch":             "PhotonGood0_genPartIdx<0",

    "looseLeptonMother":       "PhotonNoChgIsoNoSieie0_leptonMother==1",
    "noLooseLeptonMother":     "PhotonNoChgIsoNoSieie0_leptonMother==0",
    "leptonMother":            "PhotonGood0_leptonMother==1",
    "noLeptonMother":          "PhotonGood0_leptonMother==0",

    "BadEEJetVeto":        "Sum$((2.6<abs(Jet_eta)&&abs(Jet_eta)<3&&Jet_pt>30))==0",

  }

continous_variables = [ ("glDR","photonLepdR"), ("mT", "mT"), ("metSig", "METSig"), ("mll", "mll"), ("mllgamma", "mllgamma"), ("mlgamma", "mLtight0Gamma"), ("met", "MET_pt"), ("pTG","PhotonGood0_pt"), ("pTj","Jet_pt[0]"), ("etaj","abs(Jet_eta[0])") ]
discrete_variables  = [ ("nAllJet", "nJet"), ("nJet", "nJetGood"), ("nBTag", "nBTagGood"), ("nLepNoCorrVeto","nLeptonVeto"), ("nLepVeto","nLeptonVetoIsoCorr"), ("nNoIsoLepTight","nLeptonTightNoIso"), ("nInvLepTight","nLeptonTightInvIso"), ("nLepTight","nLeptonTight"), ("nLep","nLeptonGood"), ("nPhoton","nPhotonGood"), ("nHadPhoton","nPhotonNoChgIsoNoSieie") ]
cutInterpreter = CutInterpreter( continous_variables, discrete_variables, special_cuts)

if __name__ == "__main__":
    print cutInterpreter.cutString("dilepOS-pTG20-nPhoton1p-offZSFllgNoChgIsoNoSieie-mll40")
#    print cutInterpreter.cutString("etaj2.25To3-pTj100")

