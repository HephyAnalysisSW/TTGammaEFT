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

#    new_variables += [ 'GenPhotonCMSUnfold0_' + var for var in writeGenVariables ]
#    new_variables += [ 'GenLeptonCMSUnfold0_' + var for var in writeGenVariables ]
#    new_variables += [ 'nGenElectronCMSUnfold/I', 'nGenMuonCMSUnfold/I', 'nGenLeptonCMSUnfold/I', 'nGenPhotonCMSUnfold/I', 'nGenBJetCMSUnfold/I', 'nGenJetsCMSUnfold/I' ]
#    new_variables += [ 'genLCMStight0GammadPhi/F', 'genLCMStight0GammadR/F' ]
#    new_variables += [ 'genJetCMSGammadR/F' ]

#genVar = "GenPhotonCMSUnfold0_pt"
#fiducial_thresholds     = [20, 35, 50, 80, 120, 160, 200, 280, 360]
#gen_label = "p^{fid.}_{T}(#gamma) [GeV]"

sets = [
    ("GenPhotonCMSUnfold0_pt","GenPhotonCMSUnfold0_pt", [20, 35, 50, 80, 120, 160, 200, 280, 360], "p^{fid.}_{T}(#gamma) [GeV]"),
    ("GenPhotonCMSUnfold0_eta", "abs(GenPhotonCMSUnfold0_eta)", [0, 0.3, 0.6, 0.9, 1.2, 1.45], "|#eta^{fid.}(#gamma)|"),
    ("genLCMStight0GammadR", "sqrt((GenPhotonCMSUnfold0_eta-GenLeptonCMSUnfold0_eta)**2+acos(cos(GenPhotonCMSUnfold0_phi-GenLeptonCMSUnfold0_phi))**2)", [0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.4], "#DeltaR(l, #gamma)^{fid.}"),
    ("GenLeptonCMSUnfold0_pt", "GenLeptonCMSUnfold0_pt", [35, 50, 80, 120, 160, 200, 280, 360], "p^{fid.}_{T}(l) [GeV]"),
    ("nGenBJetCMSUnfold", "nGenBJetCMSUnfold", [0, 1, 2, 3], "N_{b-jet}"),
    ("nGenJetsCMSUnfold", "nGenJetsCMSUnfold", [0,1,2,3,4,5,6,7], "N_{jet}"),
]

#sel = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
#sel = "nGenLepCMS1"
#sel = "nGenPhotonCMS1"
#sel = "nGenLepCMS1-nGenPhotonCMS1"
#sel = "nGenLepCMS1-nGenJetCMS4p-nGenPhotonCMS1"
sel = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
#sel = "nGenLepCMS1-nGenJetCMS4p-nGenBTagCMS1p-nGenPhotonCMS1"
gen_sel = cutInterpreter.cutString(sel) #+"&&overlapRemoval==1"
gen_sel_nano = cutInterpreter.cutString(sel) #+"&&overlapRemoval==1"

#    TTG_P8,
#    TTG_SemiLep_P8,
#    TTG_Dilep_P8,
#    TTG_H7,
#    TTG_SemiLep_H7,
#    TTG_Dilep_H7,
#    TTG_Hpp,
#    TTG_SemiLep_Hpp,
#    TTG_Dilep_Hpp,


gen_weight = "weight" #*(137.2)"
#gen_weight = "weight*(35.92)"
#gen_weight = "weight*(41.53)"

plot_directory_ = os.path.join( plot_directory, "genHerwig", "ppv49_v5_norm", sel)
copyIndexPHP( plot_directory_ )

print gen_sel

data_dir = "/eos/vbc/user/lukas.lechner/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_2016_TTG_private_v49/inclusive"
#data_dir = "/eos/vbc/user/lukas.lechner/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_2017_TTG_private_v49/inclusive"

ttg1l_pyt = Sample.fromDirectory("ttg1l_pyt", directory = [os.path.join(data_dir, name) for name in ["TTGSingleLep_LO"]])
ttg2l_pyt = Sample.fromDirectory("ttg2l_pyt", directory = [os.path.join(data_dir, name) for name in ["TTGLep_LO"]])
sample_pyt = Sample.combine( "ttg_pyt", [ttg1l_pyt, ttg2l_pyt] )
sample_pyt.color = ROOT.kBlack
sample_pyt.texName = "tt#gamma (Pythia8, from nanoAOD)"
#sample_pyt = Sample.combine( "ttg_pyt", [ttg1l_pyt] )

from TTGammaEFT.Samples.genTuples_TTGamma_Herwig_postProcessed  import *
samples = [TTG_P8,TTG_H7,TTG_Hpp,sample_pyt]

norm  = sample_pyt.getYieldFromDraw( selectionString=gen_sel, weightString=gen_weight)["val"]
norm /= TTG_P8.getYieldFromDraw( selectionString=gen_sel, weightString=gen_weight)["val"]

print norm
gen_weight = "weight*%f"%norm #*(137.2)"
gen_weight_nano = "weight" #*(137.2)"
#gen_weight = "weight*(35.92)"
#gen_weight = "weight*(41.53)"

# Text on the plots
def drawObjects( offset=0 ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    line = (0.8-offset, 0.95, "(13 TeV)") 
    lines = [
      (0.15, 0.95, "CMS #bf{#it{Preliminary}}"), 
      line
    ]
    return [tex.DrawLatex(*l) for l in lines]

def draw( plot, **kwargs):
    plotting.draw(plot,
        plot_directory = plot_directory_,
#        ratio          = {'yRange':(0.61,1.39),'texY':'P8/H++'},
        ratio          = {'yRange':(0.61,1.39),'texY':'P8/Herwig', 'histos':[(i+1,0) for i,sample in enumerate(samples[1:])]},
        logX = False, sorting = False,
        #yRange         = (0.5, 1.5) ,
        #scaling        = {0:1} if len(plot.stack)==2 else {},
        legend         = [ (0.20,0.75,0.9,0.91), 2 ],
        drawObjects    = drawObjects(),
        copyIndexPHP   = True, 
        **kwargs
      )

for (name, genVar, fiducial_thresholds, gen_label) in sets:

    for i_s, sample in enumerate(samples):
        sample.hist = sample.get1DHistoFromDraw( genVar, binning=array.array('d', fiducial_thresholds), selectionString=gen_sel if i_s != len(samples)-1 else gen_sel_nano, weightString=gen_weight if i_s != len(samples)-1 else gen_weight_nano, addOverFlowBin="upper", binningIsExplicit=True)
        sample.hist.GetXaxis().SetTitle(gen_label)
        sample.hist.legendText = sample.texName #"MG5_aMC + Pythia8"
        sample.hist.style      = styles.lineStyle( sample.color, width=2)

    for logY in [True, False]:
        plot = Plot.fromHisto( name = name + ('_log' if logY else ''),  histos = [[ sample.hist ] for sample in samples], texX = gen_label, texY = "Fiducial cross section [fb]")
        plot.stack = None
        draw(plot, logY = logY )
