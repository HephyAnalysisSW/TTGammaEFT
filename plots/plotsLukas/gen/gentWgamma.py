import ROOT
ROOT.gROOT.SetBatch(True)
import uuid
import os, sys, copy, array
from   math import log, sqrt
import numpy as np
import root_numpy

from RootTools.core.standard          import *
from RootTools.plot.helpers    import copyIndexPHP

from TTGammaEFT.Tools.user            import plot_directory, cache_directory
from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter
import Analysis.Tools.syncer

from Analysis.Tools.WeightInfo          import WeightInfo

sets = [
    ("GenPhotonCMSUnfold0_motherPdgId", "GenPhotonCMSUnfold0_motherPdgId", range(-25,25), "mother(#gamma)"),
    ("GenPhotonCMSUnfold0_pt","GenPhotonCMSUnfold0_pt", [20, 35, 50, 80, 120, 160, 200, 280, 360], "p^{fid.}_{T}(#gamma) [GeV]"),
    ("GenPhotonCMSUnfold0_eta", "abs(GenPhotonCMSUnfold0_eta)", [0, 0.3, 0.6, 0.9, 1.2, 1.45], "|#eta^{fid.}(#gamma)|"),
    ("genLCMStight0GammadR", "sqrt((GenPhotonCMSUnfold0_eta-GenLeptonCMSUnfold0_eta)**2+acos(cos(GenPhotonCMSUnfold0_phi-GenLeptonCMSUnfold0_phi))**2)", [0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.4], "#DeltaR(l, #gamma)^{fid.}"),
    ("GenLeptonCMSUnfold0_pt", "GenLeptonCMSUnfold0_pt", [35, 50, 80, 120, 160, 200, 280, 360], "p^{fid.}_{T}(l) [GeV]"),
    ("nGenBJetCMSUnfold", "nGenBJetCMSUnfold", [0, 1, 2, 3], "N_{b-jet}"),
    ("nGenJetsCMSUnfold", "nGenJetsCMSUnfold", [0,1,2,3,4,5,6,7], "N_{jet}"),
]

#sel = "nGenLepCMS1-nGenPhotonCMS1"
sel = "nGenLepCMS1-nGenJetCMS3-nGenBTagCMS1p-nGenPhotonCMS1"
#sel2 = "nGenLepCMS1-nGenJetCMS2p-nGenBTagCMS1p-nGenPhotonCMS1"

plot_directory_ = os.path.join( plot_directory, "gentWgamma", "ppv49_v2_noNorm", sel)
#plot_directory_ = os.path.join( plot_directory, "gentWgamma", "ppv49_v2", sel)
copyIndexPHP( plot_directory_ )

from  TTGammaEFT.Samples.nanoTuples_tWG_RunII_postProcessed import ST_tW

ST_tW.color = ROOT.kBlack
ST_tW.texName = "tW"

from  TTGammaEFT.Samples.genTuples_TTGamma_tWG_EFT_postProcessed  import tWG_2WC_ref

tWG_2WC_ref.color = ROOT.kGreen+2
tWG_2WC_ref.texName = "tW#gamma"

w = WeightInfo( tWG_2WC_ref.reweight_pkl )
w.set_order( 2 )
variables = w.variables
xsecComp = 1 #.78215125 / 0.3973
eftweightString = "(%s)*ref_weight*%f"%(w.get_weight_string(), xsecComp)
print eftweightString

tWG_2WC_ref.weight = "%s*(137.2)"%(eftweightString)
ST_tW.weight = "weight*(35.92*(year==2016)+41.53*(year==2017)+59.74*(year==2018))"

gen_sel = cutInterpreter.cutString(sel)
#gen_sel2 = cutInterpreter.cutString(sel2)
print gen_sel
tWG_2WC_ref.selection = gen_sel
ST_tW.selection = gen_sel +"&&(isTWG>0)"

samples = [ST_tW, tWG_2WC_ref]

# Text on the plots
def drawObjects():
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    line = (0.68, 0.95, "137 fb^{-1} (13 TeV)") 
    lines = [
      (0.15, 0.95, "CMS #bf{#it{Preliminary}}"), 
      line
    ]
    return [tex.DrawLatex(*l) for l in lines]

histModifications  = []
histModifications += [lambda h: h.GetYaxis().SetTitleOffset(2.0)]

ratioHistModifications  = []
ratioHistModifications += [lambda h: h.GetYaxis().SetTitleOffset(2.0)]

def draw( plot, **kwargs):
    plotting.draw(plot,
        plot_directory = plot_directory_,
        ratio          = {'yRange':(0.51,1.49),'texY':'tW#gamma / tW', 'histos':[(0,0),(1,0)], "histModifications":ratioHistModifications},
        logX = False, sorting = False,
        yRange = (13, "auto"),
#        scaling = {0:1},
        legend         = (0.23,0.72,0.8,0.88),
        drawObjects    = drawObjects(),
        copyIndexPHP   = True, 
        histModifications = histModifications,
        **kwargs
      )

for (name, genVar, fiducial_thresholds, gen_label) in sets:

    for i_s, sample in enumerate(samples):
        print sample.selection
        sample.hist = sample.get1DHistoFromDraw( genVar, binning=array.array('d', fiducial_thresholds), selectionString=sample.selection, weightString=sample.weight, binningIsExplicit=True)
        sample.hist.GetXaxis().SetTitle(gen_label)
        sample.hist.legendText = sample.texName #"MG5_aMC + Pythia8"
        sample.hist.style      = styles.lineStyle( sample.color, width=3, errors=True)

    for logY in [True, False]:
        plot = Plot.fromHisto( name = name + ('_log' if logY else ''),  histos = [[ sample.hist ] for sample in samples], texX = gen_label, texY = "Events")
        plot.stack = None
        draw(plot, logY = logY)
