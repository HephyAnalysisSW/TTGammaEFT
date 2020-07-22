import os
import copy
import ROOT
from Analysis.Tools.MergingDirDB      import MergingDirDB
from TTGammaEFT.Samples.nanoTuples_RunII_postProcessed import lumi_year

def add_sigmas( h, sigmas):
    res = h.Clone()
    for i in range(0, h.GetNbinsX()+2):
        res.SetBinContent( i, h.GetBinContent( i ) + sigmas*h.GetBinError( i ) )
    return res

class third_try_ptG:
    expected        = False
    cache_directory = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/cache/"
    data_key        = "bkgSubtracted_SR3pFine_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_data"
    signal_key      = "bkgSubtracted_SR3pFine_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_signal"
    signal_stat_key = "bkgSubtracted_SR3pFine_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_signal_stat"

    cache_dir       = os.path.join(cache_directory, "unfolding", "2016", "bkgSubstracted", "expected" if expected else "observed")
    dirDB           = MergingDirDB(cache_dir)

    data            = dirDB.get( data_key )
    signal          = dirDB.get( signal_key )
    signal_stat     = dirDB.get( signal_stat_key )

    years           = ["2016"]

    reco_variable   = "PhotonGood0_pt"
    reco_selection  = "SR3p"
    
    last_bin        = data.GetNbinsX()
    reco_thresholds = [data.GetBinLowEdge(i) for i in range(1,last_bin+1)] + [ data.GetBinLowEdge(last_bin) + data.GetBinWidth(last_bin) ]

    # events not in the reco region are filled with this value
    reco_variable_underflow = -1

    fiducial_variable   = "GenPhotonCMSUnfold0_pt"
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds     = reco_thresholds[::2]
    fiducial_overflow       = "upper"
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    # appending reco thresholds for multiple years
    reco_overflow        = "upper"
    max_reco_val         = reco_thresholds[-1]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    reco_thresholds_years = copy.deepcopy(reco_thresholds)
    #for i_year in range(1, len(years)):
    #    reco_thresholds_years += [t + i_year*max_reco_val for t in reco_thresholds]

    tex_reco = "p^{reco}_{T}(#gamma) (GeV)"
    tex_gen  = "p^{gen}_{T}(#gamma) (GeV)"
    tex_unf  = "p^{fid.}_{T}(#gamma) (GeV)"
    texY     = 'Fiducial cross section (fb)'    
    y_range         = (0.9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.39,1.61)
    data_legendText = "Data (36/fb)"
    mc_legendText =   "Simulation"

    unfolding_data_input      = data
    lumi_factor               = lumi_year[2016]/1000.

    unfolding_mc_input        = signal
    systematic_bands          = [
       {'name' : 'stat',
        'label': "\pm 1#sigma (stat.)",
        'ref': signal,
        'up':  add_sigmas(signal_stat, +1),
        'down':add_sigmas(signal_stat, -1),
        'color':ROOT.kBlue,
        },
       {'name' : 'total',
        'label': "\pm 1#sigma (tot.)",
        'ref': signal,
        'up':  add_sigmas(signal, +1),
        'down':add_sigmas(signal, -1),
        'color':ROOT.kOrange,
        }
        ]

class etaG:
    expected        = False
    cache_directory = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/cache/"
    data_key        = "bkgSubtracted_SR3pEtaUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_data"
    signal_key      = "bkgSubtracted_SR3pEtaUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_signal"
    signal_stat_key = "bkgSubtracted_SR3pEtaUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_signal_stat"

    cache_dir       = os.path.join(cache_directory, "unfolding", "2016", "bkgSubstracted", "expected" if expected else "observed")
    dirDB           = MergingDirDB(cache_dir)

    data            = dirDB.get( data_key )
    signal          = dirDB.get( signal_key )
    signal_stat     = dirDB.get( signal_stat_key )

    years           = ["2016"]

    reco_variable   = "PhotonGood0_eta"
    reco_selection  = "SR3p"
    
    last_bin        = data.GetNbinsX()
    reco_thresholds = [data.GetBinLowEdge(i) for i in range(1,last_bin+1)] + [ data.GetBinLowEdge(last_bin) + data.GetBinWidth(last_bin) ]


    fiducial_variable   = "GenPhotonCMSUnfold0_eta"
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds = [-1.5, -1.1, -0.7, -0.3, 0.3, 0.7, 1.1, 1.5]

    fiducial_overflow       = None
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    # appending reco thresholds for multiple years
    reco_overflow        = None
    max_reco_val         = reco_thresholds[-1]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    # events not in the reco region are filled with this value
    reco_variable_underflow = reco_thresholds[0]-0.5

    reco_thresholds_years = copy.deepcopy(reco_thresholds)
    #for i_year in range(1, len(years)):
    #    reco_thresholds_years += [t + i_year*max_reco_val for t in reco_thresholds]

    tex_reco = "#eta^{reco}(#gamma) (GeV)"
    tex_gen  = "#eta^{gen}(#gamma) (GeV)"
    tex_unf  = "#eta^{fid.}(#gamma) (GeV)"
    texY     = 'Fiducial cross section (fb)'    
    y_range         = (0.9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.39,1.61)
    data_legendText = "Data (36/fb)"
    mc_legendText =   "Simulation"

    unfolding_data_input      = data
    lumi_factor               = lumi_year[2016]/1000.

    unfolding_mc_input        = signal
    systematic_bands          = [
       {'name' : 'stat',
        'label': "\pm 1#sigma (stat.)",
        'ref': signal,
        'up':  add_sigmas(signal_stat, +1),
        'down':add_sigmas(signal_stat, -1),
        'color':ROOT.kBlue,
        },
       {'name' : 'total',
        'label': "\pm 1#sigma (tot.)",
        'ref': signal,
        'up':  add_sigmas(signal, +1),
        'down':add_sigmas(signal, -1),
        'color':ROOT.kOrange,
        }
        ]


class dRlg:
    expected        = False
    cache_directory = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/cache/"
    data_key        = "bkgSubtracted_SR3pdRUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_data"
    signal_key      = "bkgSubtracted_SR3pdRUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_signal"
    signal_stat_key = "bkgSubtracted_SR3pdRUnfold_addDYSF_SR3pM3_VG3p_misDY3p_addDYSF_signal_stat"

    cache_dir       = os.path.join(cache_directory, "unfolding", "2016", "bkgSubstracted", "expected" if expected else "observed")
    dirDB           = MergingDirDB(cache_dir)

    data            = dirDB.get( data_key )
    signal          = dirDB.get( signal_key )
    signal_stat     = dirDB.get( signal_stat_key )

    years           = ["2016"]

    reco_variable   = { "dRlg_reco":"sqrt((PhotonGood0_eta-LeptonTight0_eta)**2+acos(cos(PhotonGood0_phi-LeptonTight0_phi))**2)"}
    reco_selection  = "SR3p"
    
    last_bin        = data.GetNbinsX()
    reco_thresholds = [data.GetBinLowEdge(i) for i in range(1,last_bin+1)] + [ data.GetBinLowEdge(last_bin) + data.GetBinWidth(last_bin) ]

    # events not in the reco region are filled with this value
    reco_variable_underflow = -1

    fiducial_variable   = "genLCMStight0GammadR"
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds     = reco_thresholds[::2]
    
    fiducial_overflow       = "upper"
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    # appending reco thresholds for multiple years
    reco_overflow        = "upper"
    max_reco_val         = reco_thresholds[-1]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    reco_thresholds_years = copy.deepcopy(reco_thresholds)
    #for i_year in range(1, len(years)):
    #    reco_thresholds_years += [t + i_year*max_reco_val for t in reco_thresholds]

    tex_reco = "#Delta R(#gamma, l)^{reco}"
    tex_gen  = "#Delta R(#gamma, l)^{gen}"
    tex_unf  = "#Delta R(#gamma, l)^{fid.}"
    texY     = 'Fiducial cross section (fb)'    
    y_range         = (0.9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.39,1.61)
    data_legendText = "Data (36/fb)"
    mc_legendText =   "Simulation"

    unfolding_data_input      = data
    lumi_factor               = lumi_year[2016]/1000.

    unfolding_mc_input        = signal
    systematic_bands          = [
       {'name' : 'stat',
        'label': "\pm 1#sigma (stat.)",
        'ref': signal,
        'up':  add_sigmas(signal_stat, +1),
        'down':add_sigmas(signal_stat, -1),
        'color':ROOT.kBlue,
        },
       {'name' : 'total',
        'label': "\pm 1#sigma (tot.)",
        'ref': signal,
        'up':  add_sigmas(signal, +1),
        'down':add_sigmas(signal, -1),
        'color':ROOT.kOrange,
        }
        ]


# unfolding closure test
class ptG_unfolding_closure:
    years = ["2016"]

    reco_variable  = "PhotonGood0_pt"
    reco_selection = "SR3p"

    reco_thresholds         = range(20, 430, 15) #range(20, 430, 10)

    # events not in the reco region are filled with this value
    reco_variable_underflow = -1

    fiducial_variable   = "GenPhotonCMSUnfold0_pt"
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds     = reco_thresholds[::3]
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    # appending reco thresholds for multiple years
    max_reco_val         = reco_thresholds[-1]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    reco_thresholds_years = copy.deepcopy(reco_thresholds)
    for i_year in range(1, len(years)):
        reco_thresholds_years += [t + i_year*max_reco_val for t in reco_thresholds]

    tex_reco = "p^{reco}_{T}(#gamma) (GeV)"
    tex_gen  = "p^{gen}_{T}(#gamma) (GeV)"

    unfolding_input = None # closure
