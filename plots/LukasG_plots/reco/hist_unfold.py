
import ROOT, os, imp, sys, copy
import time
import pickle



xminGen = 20
xmaxGen = 50
nGen = 3
nDet = 25
xminDet = 20
xmaxDet = 50
histUnfoldMatrix= ROOT.TH2D("unfolding matrix","z;ptrec;ptgen",nGen,xminGen,xmaxGen,nDet,xminDet,xmaxDet)
histUnfoldInput = ROOT.TH1D("unfolding input rec","ptrec",nDet,xminDet,xmaxDet)
histUnfoldBgr1 = ROOT.TH1D("unfolding bgr1 rec","ptrec",nDet,xminDet,xmaxDet)
histUnfoldBgr2 = ROOT.TH1D("unfolding bgr2 rec",";ptrec",nDet,xminDet,xmaxDet)
histUnfoldMatrixSys = ROOT.TH2D("unfolding matrix sys",";ptgen;ptrec",nGen,xminGen,xmaxGen,nDet,xminDet,xmaxDet)

pickle.load (file("histUnfoldMatrix" ) )

C1 = ROOT.TCanvas("output","output",900,1250)
C1.SetRightMargin(0.15)
C1.cd(1)
C1.SetLogz()
histUnfoldMatrix.GetXaxis().SetTitle("#p^{gen}_{T}(#gamma)[GeV]")
histUnfoldMatrix.GetYaxis().SetTitle("#p^{reco}_{T}(#gamma)[GeV]")
histUnfoldMatrix.Draw("colz")
C1.SaveAs("plot_9_1_19.png")
C1.SaveAs("plot_9_1_19.pdf")

#C2 = ROOT.TCanvas("output2","output2",900,1250)
#C2.cd(1)
#histUnfoldInput.Draw()
#C2.SaveAs("plot2.png")
print("regMode.....")
regMode = ROOT.TUnfold.kRegModeCurvature
print("done")
print("constraintMode......")
constraintMode = ROOT.TUnfold.kEConstraintArea
print("done")
print("densityFlags......")
densityFlags = ROOT.TUnfoldDensity.kDensityModeBinWidth
print("done")
print("unfolding......")
unfold = ROOT.TUnfoldDensity(histUnfoldMatrix,ROOT.TUnfold.kHistMapOutputHoriz,regMode,constraintMode,densityFlags)
print("done")
print("SetInput.....")
unfold.SetInput(histUnfoldInput)
print("done")

scale_bgr=1.0
dscale_bgr=0.1
#unfold.SubtractBackground(histUnfoldBgr1,"background1",scale_bgr,dscale_bgr)
#unfold.SubtractBackground(histUnfoldBgr2,"background2",scale_bgr,dscale_bgr)

  # add systematic error
#unfold.AddSysError(histUnfoldMatrixSys,"signalshape_SYS",ROOT.TUnfold.kHistMapOutputHoriz,ROOT.TUnfoldSys.kSysErrModeMatrix)
print("GetOutput.....")
histUnfoldOutput = unfold.GetOutput("PT")
print("done")
time.sleep(5)
C3 = ROOT.TCanvas("output3","output3",900,1250)
C3.cd(3)
histUnfoldOutput.Draw()
C3.SaveAs("plot3.png")
time.sleep(1000000)

