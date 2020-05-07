''' Class to interpret string based cuts
'''

# TTGamma Imports
from Analysis.Tools.CutInterpreter import CutInterpreter

mZ              = 91.1876
mT              = 172.5
zMassRange      = 10
m3MassRange     = 50
mLgThresh       = mZ# - zMassRange
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

    "lhighEta":          "abs(LeptonTight0_eta)>1.5",
    "llowEta":           "abs(LeptonTight0_eta)<=1.5",

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

#    "onZSFllTight":      "((abs(mlltight-%s)<=%s&&(nElectronTight==2||nMuonTight==2))||(nElectronTight==1&&nMuonTight==1))"%("90", zMassRange),            # Cut Z-Window only for SF dilep events
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
    "allInv":               "(nMuonTightInvIso==1||nElectronTightInvIso==1)",

    "allNoIso":               "(nMuonTightNoIso==1||nElectronTightNoIso==1)",
    "muNoIso":                "nMuonTightNoIso==1",
    "eNoIso":                 "nElectronTightNoIso==1",
    
    "lowZlg":               "mLtight0Gamma<=%f"%(mLgThresh),
    "highZlg":              "mLtight0Gamma>%f"%(mLgThresh),

    "offZeg":               "((abs(mLtight0Gamma-%s)>%s&&nElectronTight==1)||(nElectronTight==0))"%(mZ, zMassRange),             # Cut Z-Window only for egamma
    "onZeg":                "((abs(mLtight0Gamma-%s)<=%s&&nElectronTight==1)||(nElectronTight==0))"%(mZ, zMassRange),             # Cut Z-Window only for egamma
    "mu":                   "nMuonTight==1",
    "e":                    "nElectronTight==1",
    "all":                  "(1)",

    "genMu":                "nGenMuonCMSUnfold==1",
    "genE":                 "nGenElectronCMSUnfold==1",

    "phiGlt1p1":             "abs(PhotonGood0_phi)<1.1",
    "onZEphiGlt1p1":         "((abs(mLtight0Gamma-%s)<=%s&&abs(PhotonGood0_phi)<1.1&&nElectronTight==1)||(abs(mLtight0Gamma-%s)>%s&&nElectronTight==1)||(nElectronTight==0))"%(mZ,zMassRange,mZ,zMassRange),

    "n12Jet":               "nJetGood==1||nJetGood==2",

    "noChgIso":          "PhotonNoChgIsoNoSieie0_sieie<%f"%lowSieieThresh,
    "highChgIso":        "(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)>=%f&&PhotonNoChgIsoNoSieie0_sieie<%f"%(chgIsoThresh,lowSieieThresh),
    "noSieie":           "(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)<%f"%chgIsoThresh,
    "highSieie":         "PhotonNoChgIsoNoSieie0_sieie>=%f&&(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)<%f"%(highSieieThresh,chgIsoThresh),

    "noChgIsoNoSieie":          "nPhotonNoChgIsoNoSieie==1",
    "noChgIsoNoSieieInvL":      "nPhotonNoChgIsoNoSieieInvLepIso==1",

    "lowSieieNoChgIso":          "PhotonNoChgIsoNoSieie0_sieie<%f"%lowSieieThresh,
    "lowSieieHighChgIso":        "PhotonNoChgIsoNoSieie0_sieie<%f&&(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)>=%f"%(lowSieieThresh,chgIsoThresh),
    "highSieieNoChgIso":         "PhotonNoChgIsoNoSieie0_sieie>=%f"%highSieieThresh,
    "lowChgIsoNoSieie":         "(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)<%f"%chgIsoThresh,
    "lowChgIsoHighSieie":       "(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)<%f&&PhotonNoChgIsoNoSieie0_sieie>=%f"%(chgIsoThresh,highSieieThresh),
    "highChgIsoNoSieie":        "(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)>=%f"%chgIsoThresh,

    "lowChgIsolowSieie":   "(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)<%f&&PhotonNoChgIsoNoSieie0_sieie<%f"%(chgIsoThresh,lowSieieThresh),
    "highChgIsolowSieie":  "(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)>=%f&&PhotonNoChgIsoNoSieie0_sieie<%f"%(chgIsoThresh,lowSieieThresh),
    "lowChgIsohighSieie":  "(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)<%f&&PhotonNoChgIsoNoSieie0_sieie>=%f"%(chgIsoThresh,highSieieThresh),
    "highChgIsohighSieie": "(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)>=%f&&PhotonNoChgIsoNoSieie0_sieie>=%f"%(chgIsoThresh,highSieieThresh),

    "noChgIsoInvL":          "PhotonNoChgIsoNoSieieInvLepIso0_sieie<%f"%lowSieieThresh,
    "highChgIsoInvL":        "(PhotonNoChgIsoNoSieieInvLepIso0_pfRelIso03_chg*PhotonNoChgIsoNoSieieInvLepIso0_pt)>=%f&&PhotonNoChgIsoNoSieieInvLepIso0_sieie<%f"%(chgIsoThresh,lowSieieThresh),
    "noSieieInvL":           "(PhotonNoChgIsoNoSieieInvLepIso0_pfRelIso03_chg*PhotonNoChgIsoNoSieieInvLepIso0_pt)<%f"%chgIsoThresh,
    "highSieieInvL":         "PhotonNoChgIsoNoSieieInvLepIso0_sieie>=%f&&(PhotonNoChgIsoNoSieieInvLepIso0_pfRelIso03_chg*PhotonNoChgIsoNoSieieInvLepIso0_pt)<%f"%(highSieieThresh,chgIsoThresh),

    "lowSieieNoChgIsoInvL":          "PhotonNoChgIsoNoSieieInvLepIso0_sieie<%f"%lowSieieThresh,
    "highSieieNoChgIsoInvL":         "PhotonNoChgIsoNoSieieInvLepIso0_sieie>=%f"%highSieieThresh,
    "lowChgIsoNoSieieInvL":         "(PhotonNoChgIsoNoSieieInvLepIso0_pfRelIso03_chg*PhotonNoChgIsoNoSieieInvLepIso0_pt)<%f"%chgIsoThresh,
    "highChgIsoNoSieieInvL":        "(PhotonNoChgIsoNoSieieInvLepIso0_pfRelIso03_chg*PhotonNoChgIsoNoSieieInvLepIso0_pt)>=%f"%chgIsoThresh,

    "lowChgIsolowSieieInvL":   "(PhotonNoChgIsoNoSieieInvLepIso0_pfRelIso03_chg*PhotonNoChgIsoNoSieieInvLepIso0_pt)<%f&&PhotonNoChgIsoNoSieieInvLepIso0_sieie<%f"%(chgIsoThresh,lowSieieThresh),
    "highChgIsolowSieieInvL":  "(PhotonNoChgIsoNoSieieInvLepIso0_pfRelIso03_chg*PhotonNoChgIsoNoSieieInvLepIso0_pt)>=%f&&PhotonNoChgIsoNoSieieInvLepIso0_sieie<%f"%(chgIsoThresh,lowSieieThresh),
    "lowChgIsohighSieieInvL":  "(PhotonNoChgIsoNoSieieInvLepIso0_pfRelIso03_chg*PhotonNoChgIsoNoSieieInvLepIso0_pt)<%f&&PhotonNoChgIsoNoSieieInvLepIso0_sieie>=%f"%(chgIsoThresh,highSieieThresh),
    "highChgIsohighSieieInvL": "(PhotonNoChgIsoNoSieieInvLepIso0_pfRelIso03_chg*PhotonNoChgIsoNoSieieInvLepIso0_pt)>=%f&&PhotonNoChgIsoNoSieieInvLepIso0_sieie>=%f"%(chgIsoThresh,highSieieThresh),

    "lowPT":             "PhotonGood0_pt>=20&&PhotonGood0_pt<120",
    "medPT":             "PhotonGood0_pt>=120&&PhotonGood0_pt<220",
    "highPT":            "PhotonGood0_pt>=220",
    "incl":              "PhotonGood0_pt>=20",

    "lowhadPT":          "PhotonNoChgIsoNoSieie0_pt>=20&&PhotonNoChgIsoNoSieie0_pt<120",
    "medhadPT":          "PhotonNoChgIsoNoSieie0_pt>=120&&PhotonNoChgIsoNoSieie0_pt<220",
    "highhadPT":         "PhotonNoChgIsoNoSieie0_pt>=220",
    "inclhad":           "PhotonNoChgIsoNoSieie0_pt>=20",

    "photoncat0":        "PhotonGood0_photonCatMagic==0",
    "photoncat1":        "PhotonGood0_photonCatMagic==1",
    "photoncat2":        "PhotonGood0_photonCatMagic==2",
    "photoncat3":        "PhotonGood0_photonCatMagic==3",
    "photoncat4":        "PhotonGood0_photonCatMagic==4",
    "photoncat13":       "(PhotonGood0_photonCatMagic==1||PhotonGood0_photonCatMagic==3)",
    "photoncat134":      "(PhotonGood0_photonCatMagic==1||PhotonGood0_photonCatMagic==3||PhotonGood0_photonCatMagic==4)",

    "photonAdvcat0":        "PhotonGood0_photonCatMagic==0",
    "photonAdvcat1":        "PhotonGood0_photonCatMagic==1",
    "photonAdvcat2":        "PhotonGood0_photonCatMagic==2",
    "photonAdvcat3":        "PhotonGood0_photonCatMagic==3",
    "photonAdvcat4":        "PhotonGood0_photonCatMagic==4",
    "photonAdvcat4":        "PhotonGood0_photonCatMagic==4",

    "invLphotoncat0":        "PhotonGoodInvLepIso0_photonCatMagic==0",
    "invLphotoncat1":        "PhotonGoodInvLepIso0_photonCatMagic==1",
    "invLphotoncat2":        "PhotonGoodInvLepIso0_photonCatMagic==2",
    "invLphotoncat3":        "PhotonGoodInvLepIso0_photonCatMagic==3",
    "invLphotoncat4":        "PhotonGoodInvLepIso0_photonCatMagic==4",
    "invLphotoncat13":       "(PhotonGoodInvLepIso0_photonCatMagic==1||PhotonGoodInvLepIso0_photonCatMagic==3)",
    "invLphotoncat134":      "(PhotonGoodInvLepIso0_photonCatMagic==1||PhotonGoodInvLepIso0_photonCatMagic==3||PhotonGoodInvLepIso0_photonCatMagic==4)",

    "invSieiephotoncat0":        "PhotonInvSieie0_photonCatMagic==0",
    "invSieiephotoncat1":        "PhotonInvSieie0_photonCatMagic==1",
    "invSieiephotoncat2":        "PhotonInvSieie0_photonCatMagic==2",
    "invSieiephotoncat3":        "PhotonInvSieie0_photonCatMagic==3",
    "invSieiephotoncat4":        "PhotonInvSieie0_photonCatMagic==4",
    "invSieiephotoncat13":       "(PhotonInvSieie0_photonCatMagic==1||PhotonInvSieie0_photonCatMagic==3)",
    "invSieiephotoncat134":       "(PhotonInvSieie0_photonCatMagic==1||PhotonInvSieie0_photonCatMagic==3||PhotonInvSieie0_photonCatMagic==4)",

    "invLInvSieiephotoncat0":        "PhotonInvSieieInvLepIso0_photonCatMagic==0",
    "invLInvSieiephotoncat1":        "PhotonInvSieieInvLepIso0_photonCatMagic==1",
    "invLInvSieiephotoncat2":        "PhotonInvSieieInvLepIso0_photonCatMagic==2",
    "invLInvSieiephotoncat3":        "PhotonInvSieieInvLepIso0_photonCatMagic==3",
    "invLInvSieiephotoncat4":        "PhotonInvSieieInvLepIso0_photonCatMagic==4",
    "invLInvSieiephotoncat13":       "(PhotonInvSieieInvLepIso0_photonCatMagic==1||PhotonInvSieieInvLepIso0_photonCatMagic==3)",
    "invLInvSieiephotoncat134":      "(PhotonInvSieieInvLepIso0_photonCatMagic==1||PhotonInvSieieInvLepIso0_photonCatMagic==3||PhotonInvSieieInvLepIso0_photonCatMagic==4)",

    "invChgIsophotoncat0":        "PhotonInvChgIso0_photonCatMagic==0",
    "invChgIsophotoncat1":        "PhotonInvChgIso0_photonCatMagic==1",
    "invChgIsophotoncat2":        "PhotonInvChgIso0_photonCatMagic==2",
    "invChgIsophotoncat3":        "PhotonInvChgIso0_photonCatMagic==3",
    "invChgIsophotoncat4":        "PhotonInvChgIso0_photonCatMagic==4",
    "invChgIsophotoncat13":       "(PhotonInvChgIso0_photonCatMagic==1||PhotonInvChgIso0_photonCatMagic==3)",
    "invChgIsophotoncat134":      "(PhotonInvChgIso0_photonCatMagic==1||PhotonInvChgIso0_photonCatMagic==3||PhotonInvChgIso0_photonCatMagic==4)",

    "invLInvChgIsophotoncat0":        "PhotonInvChgIsoInvLepIso0_photonCatMagic==0",
    "invLInvChgIsophotoncat1":        "PhotonInvChgIsoInvLepIso0_photonCatMagic==1",
    "invLInvChgIsophotoncat2":        "PhotonInvChgIsoInvLepIso0_photonCatMagic==2",
    "invLInvChgIsophotoncat3":        "PhotonInvChgIsoInvLepIso0_photonCatMagic==3",
    "invLInvChgIsophotoncat4":        "PhotonInvChgIsoInvLepIso0_photonCatMagic==4",
    "invLInvChgIsophotoncat13":       "(PhotonInvChgIsoInvLepIso0_photonCatMagic==1||PhotonInvChgIsoInvLepIso0_photonCatMagic==3)",
    "invLInvChgIsophotoncat134":      "(PhotonInvChgIsoInvLepIso0_photonCatMagic==1||PhotonInvChgIsoInvLepIso0_photonCatMagic==3||PhotonInvChgIsoInvLepIso0_photonCatMagic==4)",

    "invChgIsoInvSieiephotoncat0":        "PhotonInvChgIsoInvSieie0_photonCatMagic==0",
    "invChgIsoInvSieiephotoncat1":        "PhotonInvChgIsoInvSieie0_photonCatMagic==1",
    "invChgIsoInvSieiephotoncat2":        "PhotonInvChgIsoInvSieie0_photonCatMagic==2",
    "invChgIsoInvSieiephotoncat3":        "PhotonInvChgIsoInvSieie0_photonCatMagic==3",
    "invChgIsoInvSieiephotoncat4":        "PhotonInvChgIsoInvSieie0_photonCatMagic==4",
    "invChgIsoInvSieiephotoncat13":       "(PhotonInvChgIsoInvSieie0_photonCatMagic==1||PhotonInvChgIsoInvSieie0_photonCatMagic==3)",
    "invChgIsoInvSieiephotoncat134":      "(PhotonInvChgIsoInvSieie0_photonCatMagic==1||PhotonInvChgIsoInvSieie0_photonCatMagic==3||PhotonInvChgIsoInvSieie0_photonCatMagic==4)",

    "noChgIsoNoSieiephotoncat0":        "PhotonNoChgIsoNoSieie0_photonCatMagic==0",
    "noChgIsoNoSieiephotoncat1":        "PhotonNoChgIsoNoSieie0_photonCatMagic==1",
    "noChgIsoNoSieiephotoncat2":        "PhotonNoChgIsoNoSieie0_photonCatMagic==2",
    "noChgIsoNoSieiephotoncat3":        "PhotonNoChgIsoNoSieie0_photonCatMagic==3",
    "noChgIsoNoSieiephotoncat4":        "PhotonNoChgIsoNoSieie0_photonCatMagic==4",
    "noChgIsoNoSieiephotoncat13":       "(PhotonNoChgIsoNoSieie0_photonCatMagic==1||PhotonNoChgIsoNoSieie0_photonCatMagic==3)",
    "noChgIsoNoSieiephotoncat134":      "(PhotonNoChgIsoNoSieie0_photonCatMagic==1||PhotonNoChgIsoNoSieie0_photonCatMagic==3||PhotonNoChgIsoNoSieie0_photonCatMagic==4)",

    "invLInvChgIsoInvSieiephotoncat0":        "PhotonInvChgIsoInvSieieInvLepIso0_photonCatMagic==0",
    "invLInvChgIsoInvSieiephotoncat1":        "PhotonInvChgIsoInvSieieInvLepIso0_photonCatMagic==1",
    "invLInvChgIsoInvSieiephotoncat2":        "PhotonInvChgIsoInvSieieInvLepIso0_photonCatMagic==2",
    "invLInvChgIsoInvSieiephotoncat3":        "PhotonInvChgIsoInvSieieInvLepIso0_photonCatMagic==3",
    "invLInvChgIsoInvSieiephotoncat4":        "PhotonInvChgIsoInvSieieInvLepIso0_photonCatMagic==4",
    "invLInvChgIsoInvSieiephotoncat13":       "(PhotonInvChgIsoInvSieieInvLepIso0_photonCatMagic==1||PhotonInvChgIsoInvSieieInvLepIso0_photonCatMagic==3)",
    "invLInvChgIsoInvSieiephotoncat134":      "(PhotonInvChgIsoInvSieieInvLepIso0_photonCatMagic==1||PhotonInvChgIsoInvSieieInvLepIso0_photonCatMagic==3||PhotonInvChgIsoInvSieieInvLepIso0_photonCatMagic==4)",

    "invLNoChgIsoNoSieiephotoncat0":        "PhotonNoChgIsoNoSieieInvLepIso0_photonCatMagic==0",
    "invLNoChgIsoNoSieiephotoncat1":        "PhotonNoChgIsoNoSieieInvLepIso0_photonCatMagic==1",
    "invLNoChgIsoNoSieiephotoncat2":        "PhotonNoChgIsoNoSieieInvLepIso0_photonCatMagic==2",
    "invLNoChgIsoNoSieiephotoncat3":        "PhotonNoChgIsoNoSieieInvLepIso0_photonCatMagic==3",
    "invLNoChgIsoNoSieiephotoncat4":        "PhotonNoChgIsoNoSieieInvLepIso0_photonCatMagic==4",
    "invLNoChgIsoNoSieiephotoncat13":       "(PhotonNoChgIsoNoSieieInvLepIso0_photonCatMagic==1||PhotonNoChgIsoNoSieieInvLepIso0_photonCatMagic==3)",
    "invLNoChgIsoNoSieiephotoncat134":      "(PhotonNoChgIsoNoSieieInvLepIso0_photonCatMagic==1||PhotonNoChgIsoNoSieieInvLepIso0_photonCatMagic==3||PhotonNoChgIsoNoSieieInvLepIso0_photonCatMagic==4)",

    "photonhadcat0":        "PhotonNoChgIsoNoSieie0_photonCatMagic==0",
    "photonhadcat1":        "PhotonNoChgIsoNoSieie0_photonCatMagic==1",
    "photonhadcat2":        "PhotonNoChgIsoNoSieie0_photonCatMagic==2",
    "photonhadcat3":        "PhotonNoChgIsoNoSieie0_photonCatMagic==3",
    "photonhadcat4":        "PhotonNoChgIsoNoSieie0_photonCatMagic==4",
    "photonhadcat13":       "(PhotonNoChgIsoNoSieie0_photonCatMagic==1||PhotonNoChgIsoNoSieie0_photonCatMagic==3)",
    "photonhadcat134":      "(PhotonNoChgIsoNoSieie0_photonCatMagic==1||PhotonNoChgIsoNoSieie0_photonCatMagic==3||PhotonNoChgIsoNoSieie0_photonCatMagic==4)",

    "looseGenMatch":          "PhotonNoChgIsoNoSieie0_genPartIdx>=0",
    "genMatch":               "PhotonGood0_genPartIdx>=0",
    "noLooseGenMatch":        "PhotonNoChgIsoNoSieie0_genPartIdx<0",
    "noGenMatch":             "PhotonGood0_genPartIdx<0",

    "looseLeptonMother":       "PhotonNoChgIsoNoSieie0_leptonMother==1",
    "noLooseLeptonMother":     "PhotonNoChgIsoNoSieie0_leptonMother==0",
    "leptonMother":            "PhotonGood0_leptonMother==1",
    "noLeptonMother":          "PhotonGood0_leptonMother==0",

    "BadEEJetVeto":        "Sum$((2.6<abs(Jet_eta)&&abs(Jet_eta)<3&&Jet_pt>30))==0&&Sum$((2.6<abs(Photon_eta)&&abs(Photon_eta)<3&&Photon_pt>5))==0&&Sum$((2.6<abs(Lepton_eta)&&abs(Lepton_eta)<3&&Lepton_pt>5&&abs(Lepton_pdgId)==11))==0",
    "advHEMVetoMuData":      "((Sum$(Lepton_pt>5&&Lepton_eta>-3.0&&Lepton_eta<-1.4&&Lepton_phi>-1.57&&Lepton_phi<-0.87)==0&&Sum$(Photon_pt>5&&Photon_eta>-3.0&&Photon_eta<-1.4&&Photon_phi>-1.57&&Photon_phi<-0.87)==0)||run<319077)",
    "advHEMVetoMuMC":        "((Sum$(Lepton_pt>5&&Lepton_eta>-3.0&&Lepton_eta<-1.4&&Lepton_phi>-1.57&&Lepton_phi<-0.87)==0&&Sum$(Photon_pt>5&&Photon_eta>-3.0&&Photon_eta<-1.4&&Photon_phi>-1.57&&Photon_phi<-0.87)==0))",
    "advHEMVetoPtData":      "((Sum$(abs(Lepton_pdgId)==11&&Lepton_pt>5&&Lepton_eta>-3.0&&Lepton_eta<-1.4&&Lepton_phi>-1.57&&Lepton_phi<-0.87)==0&&Sum$(Photon_pt>5&&Photon_eta>-3.0&&Photon_eta<-1.4&&Photon_phi>-1.57&&Photon_phi<-0.87)==0)||run<319077)",
    "advHEMVetoPtMC":        "((Sum$(abs(Lepton_pdgId)==11&&Lepton_pt>5&&Lepton_eta>-3.0&&Lepton_eta<-1.4&&Lepton_phi>-1.57&&Lepton_phi<-0.87)==0&&Sum$(Photon_pt>5&&Photon_eta>-3.0&&Photon_eta<-1.4&&Photon_phi>-1.57&&Photon_phi<-0.87)==0))",

  }

continous_variables  = [ ("glDR","photonLepdR"), ("mT", "mT"), ("metSig", "METSig"), ("mll", "mll"), ("mllgamma", "mllgamma"), ("mlgamma", "mLtight0Gamma"), ("met", "MET_pt"), ("pTG","PhotonGood0_pt"), ("phiG","PhotonGood0_phi"), ("pTj","Jet_pt[0]"), ("etaj","abs(JetGood0_eta)"), ("etak", "abs(JetGood1_eta)"), ("sip","LeptonTight0_sip3d"), ("dxyl","abs(LeptonTight0_dxy)"), ("dzl","abs(LeptonTight0_dz)"), ("etal","LeptonTight0_eta"), ("etainvl","LeptonTightInvIso0_eta"), ("ptl","LeptonTight0_pt"), ("ptinvl","LeptonTightInvIso0_pt") ]
continous_variables += [ ("lnoIsorelIso","LeptonTightNoIso0_pfRelIso03_all") ]
continous_variables += [ ("mt","mT"), ("lgDR","ltight0GammadR"), ("linvgDR","linvtight0GammadR") ]

discrete_variables  = [ ("nAllJet", "nJet"), ("nJet", "nJetGood"), ("nBTag", "nBTagGood"), ("nLepNoCorrVeto","nLeptonVeto"), ("nLepVeto","nLeptonVetoIsoCorr"), ("nNoIsoLepTight","nLeptonTightNoIso"), ("nInvLepTight","nLeptonTightInvIso"), ("nLepTight","nLeptonTight"), ("nLep","nLeptonGood"), ("nNoIsoLepVeto","nLeptonVetoNoIso"), ("nInvLeptVetoTight","nLeptonVetoNoIso") ]

discrete_variables += [ ("nPhoton",    "nPhotonGood"),          ("nHadPhoton",    "nPhotonNoChgIsoNoSieie"),          ("nSieiePhoton",    "nPhotonNoSieie"),          ("nChgIsoPhoton",    "nPhotonNoChgIso")  ]
discrete_variables += [ ("nInvLPhoton","nPhotonGoodInvLepIso"), ("nInvLHadPhoton","nPhotonNoChgIsoNoSieieInvLepIso"), ("nInvLSieiePhoton","nPhotonNoSieieInvLepIso"), ("nInvLChgIsoPhoton","nPhotonNoChgIsoInvLepIso")  ]
discrete_variables += [ ("nNoLPhoton", "nPhotonGoodNoLepIso"),  ("nNoLHadPhoton", "nPhotonNoChgIsoNoSieieNoLepIso"),  ("nNoLSieiePhoton", "nPhotonNoSieieNoLepIso"),  ("nNoLChgIsoPhoton", "nPhotonNoChgIsoNoLepIso")  ]

discrete_variables += [ ("nIHadPhoton",    "nPhotonInvChgIsoInvSieie"),          ("nISieiePhoton",    "nPhotonInvSieie"),          ("nIChgIsoPhoton",    "nPhotonInvChgIso")  ]
discrete_variables += [ ("nInvLIHadPhoton","nPhotonInvChgIsoInvSieieInvLepIso"), ("nInvLISieiePhoton","nPhotonInvSieieInvLepIso"), ("nInvLIChgIsoPhoton","nPhotonInvChgIsoInvLepIso")  ]
discrete_variables += [ ("nNoLIHadPhoton", "nPhotonInvChgIsoInvSieieNoLepIso"),  ("nNoLISieiePhoton", "nPhotonInvSieieNoLepIso"),  ("nNoLIChgIsoPhoton", "nPhotonInvChgIsoNoLepIso")  ]


discrete_variables += [ ("nNoLJet",  "nJetGoodNoLepIso"),  ("nInvLJet",  "nJetGoodInvLepIso") ]
discrete_variables += [ ("nNoLBTag", "nBTagGoodNoLepIso"), ("nInvLBTag", "nBTagGoodInvLepIso") ]

discrete_variables += [ ("nNoChgIsoJet", "nJetGoodNoChgIso"), ("nNoSieieJet", "nJetGoodNoSieie"), ("nNoChgIsoNoSieieJet", "nJetGoodNoChgIsoNoSieie") ]
discrete_variables += [ ("nNoChgIsoBTag", "nBTagGoodNoChgIso"), ("nNoSieieBTag", "nBTagGoodNoSieie"), ("nNoChgIsoNoSieieBTag", "nBTagGoodNoChgIsoNoSieie") ]
discrete_variables += [ ("nInvChgIsoJet", "nJetGoodInvChgIso"), ("nInvSieieJet", "nJetGoodInvSieie"), ("nInvChgIsoInvSieieJet", "nJetGoodInvChgIsoInvSieie") ]
discrete_variables += [ ("nInvChgIsoBTag", "nBTagGoodInvChgIso"), ("nInvSieieBTag", "nBTagGoodInvSieie"), ("nInvChgIsoInvSieieBTag", "nBTagGoodInvChgIsoInvSieie") ]

discrete_variables += [ ("nInvLepNoChgIsoJet", "nJetGoodNoChgIsoInvLepIso"), ("nInvLepNoSieieJet", "nJetGoodNoSieieInvLepIso"), ("nInvLNoChgIsoNoSieieJet", "nJetGoodNoChgIsoNoSieieInvLepIso") ]
discrete_variables += [ ("nInvLepNoChgIsoBTag", "nBTagGoodNoChgIsoInvLepIso"), ("nInvLepNoSieieBTag", "nBTagGoodNoSieieInvLepIso"), ("nInvLNoChgIsoNoSieieBTag", "nBTagGoodNoChgIsoNoSieieInvLepIso") ]
discrete_variables += [ ("nNoLepNoChgIsoJet", "nJetGoodNoChgIsoNoLepIso"), ("nNoLepNoSieieJet", "nJetGoodNoSieieNoLepIso"), ("nNoLNoChgIsoNoSieieJet", "nJetGoodNoChgIsoNoSieieNoLepIso") ]
discrete_variables += [ ("nNoLepNoChgIsoBTag", "nBTagGoodNoChgIsoNoLepIso"), ("nNoLepNoSieieBTag", "nBTagGoodNoSieieNoLepIso"), ("nNoLNoChgIsoNoSieieBTag", "nBTagGoodNoChgIsoNoSieieNoLepIso") ]

discrete_variables += [ ("nInvLepInvChgIsoJet", "nJetGoodInvChgIsoInvLepIso"), ("nInvLepInvSieieJet", "nJetGoodInvSieieInvLepIso"), ("nInvLInvChgIsoInvSieieJet", "nJetGoodInvChgIsoInvSieieInvLepIso") ]
discrete_variables += [ ("nInvLepInvChgIsoBTag", "nBTagGoodInvChgIsoInvLepIso"), ("nInvLepInvSieieBTag", "nBTagGoodInvSieieInvLepIso"), ("nInvLInvChgIsoInvSieieBTag", "nBTagGoodInvChgIsoInvSieieInvLepIso") ]
discrete_variables += [ ("nNoLepInvChgIsoJet", "nJetGoodInvChgIsoNoLepIso"), ("nNoLepInvSieieJet", "nJetGoodInvSieieNoLepIso"), ("nNoLInvChgIsoInvSieieJet", "nJetGoodInvChgIsoInvSieieNoLepIso") ]
discrete_variables += [ ("nNoLepInvChgIsoBTag", "nBTagGoodInvChgIsoNoLepIso"), ("nNoLepInvSieieBTag", "nBTagGoodInvSieieNoLepIso"), ("nNoLInvChgIsoInvSieieBTag", "nBTagGoodInvChgIsoInvSieieNoLepIso") ]

discrete_variables += [ ("nGenLepATLAS", "nGenLeptonATLASUnfold"), ("nGenJetATLAS", "nGenJetsATLASUnfold"), ("nGenBTagATLAS", "nGenBJetATLASUnfold"), ("nGenPhotonATLAS", "nGenPhotonATLASUnfold"), ("nGenLepCMS", "nGenLeptonCMSUnfold"), ("nGenJetCMS", "nGenJetsCMSUnfold"), ("nGenBTagCMS", "nGenBJetCMSUnfold"), ("nGenPhotonCMS", "nGenPhotonCMSUnfold") ]
cutInterpreter = CutInterpreter( continous_variables, discrete_variables, special_cuts)

if __name__ == "__main__":
#    print cutInterpreter.cutString("nGenLepCMS1-nGenJetCMS4p-nGenBTagCMS1p-nGenPhotonCMS1")
    print cutInterpreter.cutString("llowEta-mt100")

