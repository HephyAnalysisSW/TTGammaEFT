#!/usr/bin/env python

""" 
Extraction of PDF and scale uncertainties in the SRs
"""

# Standard imports
import ROOT
import os, copy
import sys
import math
import array

# TTGammaEFT
from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter

# RootTools
from RootTools.core.standard           import *

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--variable",                 action="store",      type=str, default="pt",    help="Which distribution?")
args = argParser.parse_args()

os.environ["gammaSkim"] = str(True)
import TTGammaEFT.Samples.nanoTuples_Summer16_private_v6_semilep_postProcessed as mc_samples16
import TTGammaEFT.Samples.nanoTuples_Fall17_private_v6_semilep_postProcessed  as mc_samples17
import TTGammaEFT.Samples.nanoTuples_Autumn18_private_v6_semilep_postProcessed as mc_samples18
import TTGammaEFT.Samples.nanoTuples_RunII_private_postProcessed as mc_samples
sample = mc_samples.TTG_NLO #, mc_samples16.TTG_NLO, mc_samples16.TTG_NLO
allSamples = [mc_samples16.TTG_NLO, mc_samples17.TTG_NLO, mc_samples18.TTG_NLO]
c = "all"

if args.variable == "pt":
    variable = "GenPhotonCMSUnfold0_pt"
    binning = array.array('d', [20, 35, 50, 80, 120, 160, 200, 260, 320] )

elif args.variable == "eta":
    variable = "abs(GenPhotonCMSUnfold0_eta)"
    binning = array.array('d', [0, 0.3, 0.6, 0.9, 1.2] )

elif args.variable == "dR":
    variable = "sqrt((GenPhotonCMSUnfold0_eta-GenLeptonCMSUnfold0_eta)**2+acos(cos(GenPhotonCMSUnfold0_phi-GenLeptonCMSUnfold0_phi))**2)"
    binning = array.array('d', [0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8] )

#weight = "weight"
weight = "weight*reweightHEM*reweightTrigger*reweightL1Prefire*reweightPU*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF*(35.92*(year==2016)+41.53*(year==2017)+59.74*(year==2018))"
selection = cutInterpreter.cutString("nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1")
selection += "&&nLeptonTight==1&&nLeptonVetoIsoCorr==1&&nJetGood>=3&&nBTagGood>=1&&nPhotonGood>=1&&nPhotonGood<=1&&nPhotonNoChgIsoNoSieie>=1&&nPhotonNoChgIsoNoSieie<=1&&triggered==1&&reweightHEM>0&&Flag_goodVertices&&Flag_globalSuperTightHalo2016Filter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_BadPFMuonFilter&&PV_ndof>4&&sqrt(PV_x*PV_x+PV_y*PV_y)<=2&&abs(PV_z)<=24"

scale_indices       = [0,1,3,5,7,8] #4 central?
pdf_indices         = range(100)
aS_variations16 = ["abs(LHEPdfWeight[100])", "abs(LHEPdfWeight[101])"]
aS_variations = ["abs(LHEPdfWeight[101])", "abs(LHEPdfWeight[102])"]
scale_variations    = [ "abs(LHEScaleWeight[%i])"%i for i in scale_indices ]
PDF_variations      = [ "abs(LHEPdfWeight[%i])"%i for i in pdf_indices ]

# central hist
central = sample.get1DHistoFromDraw( variable, binning=binning, selectionString=selection, weightString=weight, addOverFlowBin="upper", binningIsExplicit=True )

# Scale
scalesHists   = []
for var in scale_variations:
    scalesHists.append( sample.get1DHistoFromDraw( variable, binning=binning, selectionString=selection, weightString=weight+"*%s"%var, addOverFlowBin="upper", binningIsExplicit=True ) )

scales        = []
for i in range(len(binning)):
    scales.append( max( [abs(h.GetBinContent(i+1) - central.GetBinContent(i+1)) / central.GetBinContent(i+1) if central.GetBinContent(i+1) > 0 else 0 for h in scalesHists] ) )
print "scales", scales

# PDF
pdfHists   = []
for var in PDF_variations:
    pdfHists.append( sample.get1DHistoFromDraw( variable, binning=binning, selectionString=selection, weightString=weight+"*%s"%var, addOverFlowBin="upper", binningIsExplicit=True ) )

pdf = []
for i in range(len(binning)):
    centVal = central.GetBinContent(i+1)
    unc = 0
    if centVal > 0:
        deltas = [h.GetBinContent(i+1) for h in pdfHists]
        deltas = sorted(deltas)
        upper = len(deltas)*84/100 - 1
        lower = len(deltas)*16/100 - 1
        delta_sigma = abs(deltas[upper]-deltas[lower])*0.5
        unc = delta_sigma/centVal
    pdf.append( unc )
print "pdf", pdf

# alpha_s
asHists = []
for i_v, var in enumerate(aS_variations):
#    asHists.append( sample.get1DHistoFromDraw( variable, binning=binning, selectionString=selection, weightString=weight+"*%s"%var, addOverFlowBin="upper", binningIsExplicit=True ) )
    for i_s, s in enumerate(allSamples):
        if i_s==0:
            hist = s.get1DHistoFromDraw( variable, binning=binning, selectionString=selection, weightString=weight+"*%s"%aS_variations16[i_v], addOverFlowBin="upper", binningIsExplicit=True )
        else:
            hist.Add( s.get1DHistoFromDraw( variable, binning=binning, selectionString=selection, weightString=weight+"*%s"%var, addOverFlowBin="upper", binningIsExplicit=True ) )
    asHists.append( hist )

pdfAs = []
asu = []
for i in range(len(binning)):
    centVal = central.GetBinContent(i+1)
    print asHists[0].GetBinContent(i+1), asHists[1].GetBinContent(i+1), centVal
    unc = 0
    if centVal > 0:
        delta_sigma_alphaS = abs( asHists[1].GetBinContent(i+1) - asHists[0].GetBinContent(i+1) ) * 0.5
        unc = delta_sigma_alphaS/centVal
    asu.append( unc )
    unc_tot = math.sqrt( unc**2 + pdf[i]**2 )
    pdfAs.append( unc_tot )
print "as", asu
print "pdf+as", pdfAs

# total
tot = [ math.sqrt( scales[i]**2 + pdfAs[i]**2 ) for i in range(len(binning)) ]
print "total", tot

print
print
print "SR3p", "TTG_NLO", c, "PDF+alphaS", pdfAs
print "SR3p", "TTG_NLO", c, "Scale", scales
print "SR3p", "TTG_NLO", c, "Total Theory", tot


