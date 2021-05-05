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
    ("GenPhotonCMSUnfold0_pt", [20, 35, 50, 80, 120, 160, 200, 280, 360], "p^{fid.}_{T}(#gamma) [GeV]"),
    ("GenLeptonCMSUnfold0_pt", [35, 50, 80, 120, 160, 200, 280, 360], "p^{fid.}_{T}(l) [GeV]"),
    ("genJetCMSGammadR", [0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2], "#DeltaR(jet,#gamma)"),
    ("genLCMStight0GammadR", [0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2], "#DeltaR(l,#gamma)"),
    ("nGenBJetCMSUnfold", [0, 1, 2, 3], "N_{b-jet}"),
    ("nGenJetsCMSUnfold", [0,1,2,3,4,5,6,7], "N_{jet}"),
]

#sel = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
sel = "nGenLepCMS1"
#sel = "nGenPhotonCMS1"
#sel = "nGenLepCMS1-nGenPhotonCMS1"
#sel = "nGenLepCMS1-nGenJetCMS3p-nGenPhotonCMS1"
#sel = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
#sel = "nGenLepCMS1-nGenJetCMS4p-nGenBTagCMS1p-nGenPhotonCMS1"
gen_sel = cutInterpreter.cutString(sel) +"&&overlapRemoval==1"

#gen_weight = "weight*(35.92)"
gen_weight = "weight*(41.53)"

plot_directory_ = os.path.join( plot_directory, "herwig", "ppv49_v1_h7", sel)
copyIndexPHP( plot_directory_ )

print gen_sel

#data_dir = "/eos/vbc/user/lukas.lechner/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_2016_TTG_private_v49/inclusive"
data_dir = "/eos/vbc/user/lukas.lechner/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_2017_TTG_private_v49/inclusive"

ttg0l_pyt = Sample.fromDirectory("ttg0l_pyt", directory = [os.path.join(data_dir, name) for name in ["TTGHad_LO","TTGHad_ptG100To200_LO","TTGHad_ptG200_LO"]])
ttg1l_pyt = Sample.fromDirectory("ttg1l_pyt", directory = [os.path.join(data_dir, name) for name in ["TTGSingleLep_LO","TTGSingleLep_ptG100To200_LO","TTGSingleLep_ptG200_LO"]])
ttg2l_pyt = Sample.fromDirectory("ttg2l_pyt", directory = [os.path.join(data_dir, name) for name in ["TTGLep_LO","TTGLep_ptG100To200_LO","TTGLep_ptG200_LO"]])
sample_pyt = Sample.combine( "ttg_pyt", [ttg1l_pyt, ttg2l_pyt, ttg0l_pyt] )
#sample_pyt = Sample.combine( "ttg_pyt", [ttg1l_pyt] )

ttg1l_hpp = Sample.fromDirectory("ttg1l_hpp", directory = [os.path.join(data_dir, "TTGSingleLep_LO_Herwig")])
ttg2l_hpp = Sample.fromDirectory("ttg2l_hpp", directory = [os.path.join(data_dir, "TTGLep_LO_Herwig")])
sample_hpp = Sample.combine( "ttg_hpp", [ttg1l_hpp, ttg2l_hpp] )
#sample_hpp = Sample.combine( "ttg_hpp", [ttg1l_hpp] )

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
        ratio          = {'yRange':(0.61,1.39),'texY':'P8/H7'},
        logX = False, sorting = False,
        #yRange         = (0.5, 1.5) ,
        #scaling        = {0:1} if len(plot.stack)==2 else {},
        legend         = [ (0.20,0.75,0.9,0.91), 2 ],
        drawObjects    = drawObjects(),
        copyIndexPHP   = True, 
        **kwargs
      )

for (genVar, fiducial_thresholds, gen_label) in sets:

    fiducial_spectrum_Pyt = sample_pyt.get1DHistoFromDraw( genVar, binning=array.array('d', fiducial_thresholds), selectionString=gen_sel+"&&pTStitching==1", weightString=gen_weight, addOverFlowBin="upper", binningIsExplicit=True)
    fiducial_spectrum_Pyt.GetXaxis().SetTitle(gen_label)
    fiducial_spectrum_Pyt.legendText = "MG5_aMC + Pythia8"
    fiducial_spectrum_Pyt.style      = styles.lineStyle( ROOT.kRed, width=2)

    fiducial_spectrum_Hpp = sample_hpp.get1DHistoFromDraw( genVar, binning=array.array('d', fiducial_thresholds), selectionString=gen_sel, weightString=gen_weight, addOverFlowBin="upper", binningIsExplicit=True)
    fiducial_spectrum_Hpp.GetXaxis().SetTitle(gen_label)
#    fiducial_spectrum_Hpp.legendText = "MG5_aMC + Herwig++"
    fiducial_spectrum_Hpp.legendText = "MG5_aMC + Herwig7"
    fiducial_spectrum_Hpp.style      = styles.lineStyle( ROOT.kBlue, width=2)

    for logY in [True, False]:
        plot = Plot.fromHisto( name = genVar + ('_log' if logY else ''),  histos = [[ fiducial_spectrum_Hpp ], [fiducial_spectrum_Pyt]], texX = gen_label, texY = "Events")
        plot.stack = None
        draw(plot, logY = logY )
