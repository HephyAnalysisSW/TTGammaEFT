# Standard imports
import ROOT
import os, sys
import pickle
import time
import argparse
# RootTools
from RootTools.core.standard          import *
from RootTools.plot.helpers           import copyIndexPHP

# Analysis
from Analysis.Tools.helpers           import deltaR

# Internal Imports
from TTGammaEFT.Tools.user            import plot_directory
from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter
from TTGammaEFT.Tools.Variables       import NanoVariables

# Logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   "INFO", logFile = None)
logger_rt = logger_rt.get_logger("INFO", logFile = None)


parser = argparse.ArgumentParser()
parser.add_argument('--year',      type=int, nargs='?', default= 2016)
parser.add_argument('--overwrite', type = bool , nargs='?', default = False)
args = parser.parse_args()
if (args.year == 2016):
    Lumi = 35.92
if (args.year == 2017):
    Lumi = 41.53
if (args.year == 2018):
    Lumi = 59.74

endings               = [".png", ".pdf", ".root"]

filename_unfoldMatrix = "histUnfoldMatrix.pkl"
filename_inputHisto   = "histInput.pkl"
filename_datatruthHisto = "histTruth.pkl"

numEvents = 0.
xminGen   = 20
xmaxGen   = 250
nGen      = 10
nReco     = 10#25
xminReco  = 20
xmaxReco  = 250


if os.path.exists(filename_unfoldMatrix) and  os.path.exists(filename_inputHisto) and os.path.exists(filename_datatruthHisto) and not args.overwrite:
    # load pickled unfolding matrix
     histUnfoldMatrix = pickle.load( file(filename_unfoldMatrix) )
     histUnfoldInput =  pickle.load( file(filename_inputHisto) )
     histDataTruth = pickle.load( file(filename_datatruthHisto) )
     logger.info("Re-using pickled histogram!")

else:

    # change to EOS
#    from TTGammaEFT.Tools.user import eos_directory
#    data_directory = os.path.join( eos_directory, "nanoTuples" )
#    fromEOS = "True"
#    os.environ["gammaSkim"]="True"
    from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed import *

    sample = TTGSemiLep_16
    #sample.files = sample.files[:1]

    # add needed variables
    NanoVars         = NanoVariables(args.year)
    genVarString     = NanoVars.getVariableString(   "Gen",    postprocessed=True, data=False,             plot=True )
    photonVarString  = NanoVars.getVariableString(   "Photon", postprocessed=True, data=True, plot=True )
    photonVariables  = NanoVars.getVariables(        "Photon", postprocessed=True, data=True, plot=True )
    variables = [ TreeVariable.fromString("event/l"),
                  TreeVariable.fromString("weight/F"),
                  TreeVariable.fromString('run/i'),
                  TreeVariable.fromString("luminosityBlock/i"),
    	          VectorTreeVariable.fromString('Photon[%s]'%photonVarString, nMax=100),
                  VectorTreeVariable.fromString('GenPhoton[%s]'%genVarString, nMax=100),
                  VectorTreeVariable.fromString('GenPart[%s]'%genVarString, nMax=1000),
                  TreeVariable.fromString('nPhotonGood/I'),
                  TreeVariable.fromString('nJetGood/I'),
                  TreeVariable.fromString('nBTagGood/I'),
                  TreeVariable.fromString('nLeptonTight/I'),
                  TreeVariable.fromString('nLeptonVetoIsoCorr/I'),
#                  VectorTreeVariable.fromString('PhotonGood0[%s]'%photonVariables, nMax=100),
                  TreeVariable.fromString("nGenPhoton/I"),
                  TreeVariable.fromString('nGenPart/I'),
                  TreeVariable.fromString( "PhotonGood0_eta/F" ),
                  TreeVariable.fromString( "PhotonGood0_pdgId/F" ),
                  TreeVariable.fromString( "PhotonGood0_pt/F" )
                 ]

#    selectionString="all"

    # Define a reader
    r = sample.treeReader( \
        variables = variables,
#        selectionString = cutInterpreter.cutString(selectionString),
    )
   
    histUnfoldMatrix = ROOT.TH2D("unfolding matrix",    "unfolding matrix",    nGen, xminGen, xmaxGen, nReco, xminReco, xmaxReco )
    histUnfoldInput  = ROOT.TH1D("unfolding input rec", "unfolding input rec", nReco, xminReco, xmaxReco)
#    histUnfoldMatrixSys = ROOT.TH2D("unfolding matrix sys",";ptgen;ptrec",nGen,xminGen,xmaxGen,nReco,xminReco,xmaxReco)
    histDataTruth = ROOT.TH1D("DATA truth gen",";ptgen",nGen,xminGen,xmaxGen)
    

    def selection(dic_typedata):
        return dic_typedata["status"] == 1 and dic_typedata["pdgId"] == 22 and dic_typedata["pt"] >= 20 and abs(dic_typedata["eta"]) < 1.47

    r.start()
    while r.run():
        weight = Lumi * r.event.weight
        allGoodGenPhotons = []
        for i in range(r.event.nGenPart):
            p = {"status": r.event.GenPart_status[i],"pdgId": r.event.GenPart_pdgId[i], "pt": r.event.GenPart_pt[i],"eta": r.event.GenPart_eta[i]}
            if selection(p): allGoodGenPhotons.append(p)
        if not allGoodGenPhotons: continue       
        #numEvents += 1
        allGoodGenPhotons.sort(key = lambda x: -x["pt"])
        gen = allGoodGenPhotons[0]
        if r.event.nPhotonGood == 1 and r.event.nJetGood >= 4 and r.event.nBTagGood >= 1 and r.event.nLeptonTight == 1 and r.event.nLeptonVetoIsoCorr == 1:
            reco = {"pdgId": r.event.PhotonGood0_pdgId, "pt": r.event.PhotonGood0_pt, "eta": r.event.PhotonGood0_eta}
        else:
            reco = {"pdgId": 22, "pt": -1, "eta": -1}

        histUnfoldMatrix.Fill( gen["pt"], reco["pt"], weight )
        histUnfoldInput.Fill(  reco["pt"], weight )
        histDataTruth.Fill(    gen["pt"], weight  )
        
    pickle.dump( histUnfoldMatrix, file( filename_unfoldMatrix, "w" ) )
    pickle.dump( histUnfoldInput,  file( filename_inputHisto, "w" )   )
    pickle.dump ( histDataTruth , file(  filename_datatruthHisto, "w"))
    del r
        
 
        

plot_directory_ = os.path.join( plot_directory, 'unfolding', str(args.year))
if not os.path.isdir( plot_directory_ ):
    os.makedirs( plot_directory_ )
    copyIndexPHP( plot_directory_ )

C1 = ROOT.TCanvas("output","output",900,1250)
C1.SetRightMargin(0.15)
#C1.cd(1)
C1.SetLogz()
histUnfoldMatrix.GetXaxis().SetTitle( "p^{gen}_{T}(#gamma) [GeV]" )
histUnfoldMatrix.GetYaxis().SetTitle( "p^{reco}_{T}(#gamma) [GeV]" )
histUnfoldMatrix.Draw("colz")
for ending in endings:
    C1.SaveAs( os.path.join( plot_directory_, "unfoldingMatrix"+ending ) )

C2 = ROOT.TCanvas("output2","output2",900,1250)
histUnfoldInput.GetXaxis().SetTitle( "p^{reco}_{T}(#gamma) [GeV]" )
histUnfoldInput.Draw()
for ending in endings:
    C2.SaveAs( os.path.join( plot_directory_, "input_spectrum"+ending ) )

# https://root.cern.ch/doc/v612/classTUnfold.html#adb3ade9e94eedc71e5258e1af589de62
logger.info("regMode.....")

HistEff =  ROOT.TH1D("Efficience",";eff",nGen,xminGen,xmaxGen)
HistPur = ROOT.TH1D("Purity", "pur", nReco, xminReco, xmaxReco)

for i in range(1,histUnfoldMatrix.GetNbinsX()+1):
    pt =  histDataTruth.GetBinCenter(i)
   # binX = histDataTruth.FindBin(pt)
    binY = histUnfoldInput.FindBin(pt)
    eff = histUnfoldMatrix.GetBinContent(i,binY)/ histDataTruth.GetBinContent(i)
    HistEff.SetBinContent(i,eff)
for i in range(1,histUnfoldMatrix.GetNbinsY()+1):
    pt = histUnfoldInput.GetBinCenter(i)
   # binX = histDataTruth.FindBin(pt)
    binY = histUnfoldInput.FindBin(pt)
    pur = histUnfoldMatrix.GetBinContent(i,binY)/ histUnfoldInput.GetBinContent(i)
    HistPur.SetBinContent(i,pur)
E1 = ROOT.TCanvas("eff","eff",800,1000)
E1.SetRightMargin(0.15)
HistEff.GetXaxis().SetTitle( "p^{gen}_{T}(#gamma) [GeV]" )
HistEff.GetYaxis().SetTitle( "Efficiency" )
E1.cd(1)
HistEff.Draw()
P1 =  ROOT.TCanvas("pur","pur",800,1000)
P1.SetRightMargin(0.15)
histUnfoldMatrix.GetXaxis().SetTitle( "p^{reco}_{T}(#gamma) [GeV]" )
histUnfoldMatrix.GetYaxis().SetTitle( "Purrity" )

HistPur.Draw()
E1.SaveAs("Efficience.png")
P1.SaveAs("Purity.png")
E1.SaveAs("Efficience.pdf")
P1.SaveAs("Purity.pdf")


# regularization
#regMode = ROOT.TUnfold.kRegModeNone
#regMode = ROOT.TUnfold.kRegModeSize
#regMode = ROOT.TUnfold.kRegModeDerivative
regMode = ROOT.TUnfold.kRegModeCurvature
#regMode = ROOT.TUnfold.kRegModeMixed
logger.info("done")

logger.info("constraintMode......")
# extra contrains
#constraintMode = ROOT.TUnfold.kEConstraintNone
constraintMode = ROOT.TUnfold.kEConstraintArea
logger.info("done")

logger.info("output mapping......")
#mapping = ROOT.TUnfold.kHistMapOutputVert
mapping = ROOT.TUnfold.kHistMapOutputHoriz
logger.info("done")

logger.info("densityFlags......")
#densityFlags = ROOT.TUnfoldDensity.kDensityModeNone
densityFlags = ROOT.TUnfoldDensity.kDensityModeUser
#densityFlags = ROOT.TUnfoldDensity.kDensityModeBinWidth
#densityFlags = ROOT.TUnfoldDensity.kDensityModeBinWidthAndUser
logger.info("done")

logger.info("unfolding......")
unfold = ROOT.TUnfoldDensity( histUnfoldMatrix, mapping, regMode, constraintMode, densityFlags )
logger.info("done")
logger.info("SetInput.....")
unfold.SetInput(histUnfoldInput)
logger.info("done")

# add systematic error
#unfold.AddSysError(histUnfoldMatrixSys,"signalshape_SYS",ROOT.TUnfold.kHistMapOutputHoriz,ROOT.TUnfoldSys.kSysErrModeMatrix)

logger.info("ScanLcurve.....")
logTauX = ROOT.TSpline3()
logTauY = ROOT.TSpline3()
lCurve  = ROOT.TGraph()
# Here work needs to be done! Did not work in the tutorial! FIXME
iBest   = unfold.ScanLcurve(30,0,0,lCurve,logTauX,logTauY)
logger.info("done")

logger.info("GetOutput.....")
histUnfoldOutput = unfold.GetOutput("PT")
logger.info("done")

C3 = ROOT.TCanvas("output3","output3",900,1250)
histUnfoldOutput.Draw()
for ending in endings:
    C3.SaveAs( os.path.join( plot_directory_, "unfolded_spectrum"+ending ) )
