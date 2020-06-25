''' Class to interpret string based cuts
'''

# TTGamma Imports
from Analysis.Tools.CutInterpreter import CutInterpreter

mZ = 91.1876

special_cuts = {
    "leadLepPT15":       "Sum$(GenLepton_pt>15)>=1",
    "OS":                "(GenLepton_pdgId[0]*GenLepton_pdgId[1])<0",
    "dilep":             "nGenLepton==2",
    "dilepOS":           "nGenLepton==2&&(GenLepton_pdgId[0]*GenLepton_pdgId[1])<0",
    "dilepSS":           "nGenLepton==2&&(GenLepton_pdgId[0]*GenLepton_pdgId[1])>0",
    "dilepOFOS":         "nGenLepton==2&&(GenLepton_pdgId[0]*GenLepton_pdgId[1])<0&&nGenElectron==1&&nGenMuon==1",
    "dilepOFSS":         "nGenLepton==2&&(GenLepton_pdgId[0]*GenLepton_pdgId[1])>0&&nGenElectron==1&&nGenMuon==1",
    "dilepSFOS":         "nGenLepton==2&&(GenLepton_pdgId[0]*GenLepton_pdgId[1])<0&&(nGenElectron==2||nGenMuon==2)",
    "dilepSFSS":         "nGenLepton==2&&(GenLepton_pdgId[0]*GenLepton_pdgId[1])>0&&(nGenElectron==2||nGenMuon==2)",
    "offZll":            "abs(mll-%s)>15"%(mZ),
    "offZllg":           "abs(mllgamma-%s)>15"%(mZ),
    "offZSFll":          "((abs(mll-%s)>15&&(nGenElectron==2||nGenMuon==2))||(nGenElectron==1&&nGenMuon==1))"%(mZ),                      # Cut Z-Window only for SF dilep events
    "offZSFllg":         "((abs(mllgamma-%s)>15&&(nGenElectron==2||nGenMuon==2))||(nGenElectron==1&&nGenMuon==1))"%(mZ),                 # Cut Z-Window only for SF dilep events
    "onZll":             "abs(mll-%s)<=15"%(mZ),
    "onZllg":            "abs(mllgamma-%s)<=15"%(mZ),
    "onZSFll":           "((abs(mll-%s)<=15&&(nGenElectron==2||nGenMuon==2))||(nGenElectron==1&&nGenMuon==1))"%(mZ),                     # Cut Z-Window only for SF dilep events
    "onZSFllg":          "((abs(mllgamma-%s)<=15&&(nGenElectron==2||nGenMuon==2))||(nGenElectron==1&&nGenMuon==1))"%(mZ),                # Cut Z-Window only for SF dilep events
    "mumu":              "nGenElectron==0&&nGenMuon==2",
    "mue":               "nGenElectron==1&&nGenMuon==1",
    "ee":                "nGenElectron==2&&nGenMuon==0",
    "e":                 "nGenElectron==1&&nGenMuon==0",
    "mu":                "nGenElectron==0&&nGenMuon==1",
    "all":               "(1)",
    "SF":                "(nGenElectron==2||nGenMuon==2)",
    "clean":             "nGenLepton==nGenAllLepton",
    "trilepTWZ":         "nGenLepton==3",
    "quadlepTWZ":        "nGenLepton==4",
  }

continous_variables = [ ("met", "GenMET_pt"), ("pTG","GenPhoton_pt[0]"), ("pTAllG", "GenMGPhoton_pt[0]"), ("mll", "mll"), ("mllgamma", "mllgamma") ]
discrete_variables  = [ ("nGenLepGood", "Sum$(GenPart_pt>30&&abs(GenPart_eta)<2.4&&(abs(GenPart_pdgId)==11||abs(GenPart_pdgId)==13))"), ("nGenJet", "Sum$(GenJet_pt>30)"), ("nJet", "nGenJet"), ("nBTag", "nGenBJet"), ("nLep","nGenLepton"), ("nAllPhoton","nGenMGPhoton"), ("nPhoton","nGenPhoton") ]

cutInterpreter = CutInterpreter( continous_variables, discrete_variables, special_cuts)

if __name__ == "__main__":
    print cutInterpreter.cutString("dilepOS-pTG20-nPhoton1p-offZSFll-offZSFllg-mll40")
