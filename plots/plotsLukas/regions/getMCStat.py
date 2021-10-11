import ROOT, copy

#tfile = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/2016/limits/cardFiles/defaultSetup/observed/SR3PtUnfoldEFT_SR4pPtUnfoldEFT_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_shape.root"
tfile = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/analysis/2016/limits/cardFiles/defaultSetup/observed/SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_shape.root"

rootfile = ROOT.TFile( tfile, "READ")
mcstat = copy.deepcopy(rootfile.Get("signal").Clone("x"))
mcstat.Scale(0)
rootfile.Close()
del rootfile

print mcstat
for year in ["2016","2017","2018"]:
    rootfile = ROOT.TFile( tfile.replace("2016",year), "READ")

    for process in ["signal","QCD","WG","ZG","fakes","misID","other"]:
        mcstat.Add(rootfile.Get(process).Clone())

for i in range(1, mcstat.GetNbinsX()+1):
    print i-1, mcstat.GetBinContent(i), mcstat.GetBinError(i), mcstat.GetBinError(i)/mcstat.GetBinContent(i)
