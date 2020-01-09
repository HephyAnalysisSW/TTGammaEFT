# Standard imports
import ROOT, os, imp, sys, copy
from TTGammaEFT.Tools.Variables       import NanoVariables
import time
# RootTools
from RootTools.core.standard             import *
import pickle
# Analysis
from Analysis.Tools.helpers              import deltaR

# Internal Imports
from TTGammaEFT.Tools.cutInterpreter     import cutInterpreter

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   "INFO", logFile = None)
logger_rt = logger_rt.get_logger("INFO", logFile = None)

# change to EOS
from TTGammaEFT.Tools.user import eos_directory
from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed import *
data_directory = os.path.join( eos_directory, "nanoTuples")
fromEOS = "True"
os.environ["gammaSkim"]="True"

#sample = DY_LO_16
sample = TTGSemiLep_16
sample.files = sample.files[:1]

selectionString="all"

# add needed variables
NanoVars        = NanoVariables(2016)
genVarString     = NanoVars.getVariableString(   "Gen",    postprocessed=True, data=False,             plot=True )
photonVarString  = NanoVars.getVariableString(   "Photon", postprocessed=True, data=True, plot=True )
photonVariables  = NanoVars.getVariables(        "Photon", postprocessed=True, data=True, plot=True )
variables = [ TreeVariable.fromString("event/l"),
              TreeVariable.fromString('run/i'),
              TreeVariable.fromString("luminosityBlock/i"),
	      VectorTreeVariable.fromString('Photon[%s]'%photonVarString, nMax=100),
              VectorTreeVariable.fromString('GenPhoton[%s]'%photonVarString, nMax=100),
              VectorTreeVariable.fromString('GenPart[%s]'%genVarString, nMax=1000),
              TreeVariable.fromString('nPhotonGood/I'),
              TreeVariable.fromString('nJetGood/I'),
              TreeVariable.fromString('nBTagGood/I'),
              TreeVariable.fromString('nLeptonTight/I'),
              TreeVariable.fromString('nLeptonVetoIsoCorr/I'),
#              VectorTreeVariable.fromString('PhotonGood0[%s]'%photonVariables, nMax=100),
              TreeVariable.fromString("nGenPhoton/I"),
              TreeVariable.fromString('nGenPart/I'),
              TreeVariable.fromString( "PhotonGood0_eta/F" ),
              TreeVariable.fromString( "PhotonGood0_pdgId/F" ),
              TreeVariable.fromString( "PhotonGood0_pt/F" )
             ]

#variables += map(lambda var: "PhotonGood0_"             + var, photonVariables )

# Define a reader
r = sample.treeReader( \
    variables = variables,
    selectionString = cutInterpreter.cutString(selectionString),
)
numEvents = 0.
r.start()
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

weight = 1
allGoodGenPhotons = []
allGoodrecoPhotons = []

def selection(dic_typedata):
    return dic_typedata["pdgId"] == 22 and dic_typedata["pt"] >= 20 and abs(dic_typedata["eta"] <5.)

while r.run():
    allGoodGenPhotons = []
    allGoodrecoPhotons = []
    for i in range(r.event.nGenPart):
        p = {"pdgId" : r.event.GenPart_pdgId[i], "pt" : r.event.GenPart_pt[i],"eta" : r.event.GenPart_eta[i]}
        if selection(p):
            allGoodGenPhotons.append(p)
    if not  allGoodGenPhotons:        
        continue       
    numEvents += 1
    allGoodGenPhotons.sort(key = lambda x: -x["pt"])
    gen = allGoodGenPhotons[0]
    if r.event.nPhotonGood == 1 and r.event.nJetGood >= 4 and r.event.nBTagGood >= 1 and r.event.nLeptonTight == 1 and r.event.nLeptonVetoIsoCorr == 1:
        reco = {"pdgId" : r.event.PhotonGood0_pdgId, "pt" : r.event.PhotonGood0_pt, "eta" : r.event.PhotonGood0_eta}
#        allGoodrecoPhotons.append(reco)
#        allGoodrecoPhotons.sort(key = lambda x: -x["pt"])
#        reco = allGoodrecoPhotons[0]
    else:
        reco = {"pdgId" : 0, "pt" : 0, "eta" : 0}

    histUnfoldMatrix.Fill(gen["pt"],reco["pt"],weight)
    histUnfoldInput.Fill(reco["pt"])
   
   # print(r.event.GenPhoton_eta[0])
   # print(r.event.GenPhoton_phi[0])
    run, evt, lumi = r.event.run, r.event.event, r.event.luminosityBlock
   # print run, evt, lumi

histUnfoldMatrix.Scale(1./numEvents)
pickle.dump(histUnfoldMatrix, file("histUnfoldMatrix" , "w" ) )
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
