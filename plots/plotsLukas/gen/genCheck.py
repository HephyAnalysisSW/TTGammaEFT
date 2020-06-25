import ROOT

from TTGammaEFT.Samples.nanoTuples_Summer16_private_semilep_postProcessed      import ZG_16

h0 = ROOT.TH2F("h0","h0", 20, 0, 100, 20, 0, 100)
ZG_16.chain.Draw("GenPart_pt[0]:GenPart_pt[1]>>h0" "(abs(GenPart_pdgId[1])==11||abs(GenPart_pdgId[1])==13)&&(abs(GenPart_pdgId[0])==11||abs(GenPart_pdgId[0]==13))")
h0.Print("~/www/TTGammaEFT/2D.png")
