import os
import copy
import ROOT
import array
from Analysis.Tools.MergingDirDB      import MergingDirDB

#from TTGammaEFT.Samples.nanoTuples_RunII_postProcessed import lumi_year
# hard coded to remove dependency
lumi_year = {2016: 35920.0, 2017: 41530.0, 2018: 59740.0}


def add_sigmas( h, sigmas):
    res = h.Clone()
    for i in range(0, h.GetNbinsX()+2):
        res.SetBinContent( i, h.GetBinContent( i ) + sigmas*h.GetBinError( i ) )
    return res

def thresholds_from_histo( histo ):
    last_bin        = histo.GetNbinsX()
    return tuple([histo.GetBinLowEdge(i) for i in range(1,last_bin+1)] + [ histo.GetBinLowEdge(last_bin) + histo.GetBinWidth(last_bin) ])

def merge_x( histos, bin_threshold_years):

    input_bins = []    
    for i_year, bins_in_year in enumerate(map( lambda h: range(1, h.GetNbinsX()+1), histos )):
        for i_t, bin_in_year in enumerate(bins_in_year):
            input_bins.append( (i_year, bin_in_year) )

    assert len(input_bins) == len(bin_threshold_years)-1, "Inconsistent number of input thresholds!"

    output = ROOT.TH1D(histos[0].GetName(), histos[0].GetTitle(), len(bin_threshold_years)-1, array.array('d', bin_threshold_years))
    
    for i_bin_output, (i_year, bin_input) in enumerate(input_bins):
        output.SetBinContent( i_bin_output + 1, histos[i_year].GetBinContent(bin_input) )  
        output.SetBinError  ( i_bin_output + 1, histos[i_year].GetBinError  (bin_input) ) 

    # Note: Leave overflows empty 
        
    return output
   
 
class final_ptG_2016:
    expected        = False
    cache_directory = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/cache_read/"
    data_key        = "bkgSubtracted_SR3pPtUnfold_addDYSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_data"
    signal_key      = "bkgSubtracted_SR3pPtUnfold_addDYSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_signal"
    signal_stat_key = "bkgSubtracted_SR3pPtUnfold_addDYSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_signal_stat"

    cache_dir       = os.path.join(cache_directory, "unfolding", "2016", "bkgSubstracted", "expected" if expected else "observed")
    dirDB           = MergingDirDB(cache_dir)

    data            = dirDB.get( data_key )
    signal          = dirDB.get( signal_key )
    signal_stat     = dirDB.get( signal_stat_key )

    years           = ["2016"]

    reco_variable   = "PhotonGood0_pt"
    reco_selection  = "SR3p"
    
    reco_thresholds = thresholds_from_histo( data )

    # events not in the reco region are filled with this value
    reco_variable_underflow = -1

    fiducial_variable   = "GenPhotonCMSUnfold0_pt"
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds     = [20, 35, 50, 65, 80, 120, 160, 200, 260, 320, 400] 
    fiducial_overflow       = "upper"
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    # appending reco thresholds for multiple years
    reco_overflow        = "upper"
    max_reco_val         = reco_thresholds[-1]
    min_reco_val         = reco_thresholds[0]
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

class final_ptG_2016_wrong:
    expected        = False
    cache_directory = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/cache_read/"
    data_key        = "bkgSubtracted_SR3pPtUnfold_addDYSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_data"
    signal_key      = "bkgSubtracted_SR3pPtUnfold_addDYSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_signal"
    signal_stat_key = "bkgSubtracted_SR3pPtUnfold_addDYSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_signal_stat"

    cache_dir       = os.path.join(cache_directory, "unfolding", "2016", "bkgSubstracted", "expected" if expected else "observed")
    dirDB           = MergingDirDB(cache_dir)

    data            = dirDB.get( data_key )
    signal          = dirDB.get( signal_key )
    signal_stat     = dirDB.get( signal_stat_key )

    years           = ["2016"]

    reco_variable   = "PhotonGood0_pt"
    reco_selection  = "SR3p"
    
    reco_thresholds = thresholds_from_histo( data )

    # events not in the reco region are filled with this value
    reco_variable_underflow = -1

    fiducial_variable   = "GenPhotonCMSUnfold0_pt"
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds     = [20, 35, 50, 65, 80, 120, 160, 200, 260, 320, 400] 
    fiducial_overflow       = "upper"
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    # appending reco thresholds for multiple years
    reco_overflow        = "upper"
    max_reco_val         = reco_thresholds[-1]
    min_reco_val         = reco_thresholds[0]
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

class expected_ptG_RunII:
    cache_directory = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/cache_read/"
    data_key        = "bkgSubtracted_SR3pPtUnfold_addDYSF_addMisIDSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_data_%s"
    signal_key      = "bkgSubtracted_SR3pPtUnfold_addDYSF_addMisIDSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_signal_%s"
    signal_stat_key = "bkgSubtracted_SR3pPtUnfold_addDYSF_addMisIDSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_signal_stat_%s"

    cache_dir       = os.path.join(cache_directory, "unfolding", "combined", "bkgSubstracted", "expected")
    dirDB           = MergingDirDB(cache_dir)

    years           = ["2016", "2017", "2018"]

    data_histos     =  [ dirDB.get( data_key%year ) for year in years ] 
    signal_histos   =  [ dirDB.get( signal_key%year ) for year in years ] 
    signal_stat_histos=[ dirDB.get( signal_stat_key%year ) for year in years ] 

    reco_variable   = "PhotonGood0_pt"
    reco_selection  = "SR3p"
    
    assert len(set( map( thresholds_from_histo, data_histos)))==1, "Not all data histos have the same x-axis binning!"
    assert len(set( map( thresholds_from_histo, signal_histos)))==1, "Not all signal histos have the same x-axis binning!"
    assert len(set( map( thresholds_from_histo, signal_stat_histos)))==1, "Not all signal-stat histos have the same x-axis binning!"

    reco_thresholds = thresholds_from_histo( data_histos[0] )

    # appending reco thresholds for multiple years
    reco_overflow        = "upper"
    max_reco_val         = reco_thresholds[-1]
    min_reco_val         = reco_thresholds[0]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    # events not in the reco region are filled with this value
    reco_variable_underflow = -1

    # make reco_thresholds for all years
    reco_thresholds_years = list(copy.deepcopy(reco_thresholds))
    for i_year in range(1, len(years)):
        reco_thresholds_years +=  [ x + (max_reco_val-min_reco_val)*i_year for x in reco_thresholds[1:] ]

    data        = merge_x( data_histos, reco_thresholds_years )
    signal      = merge_x( signal_histos, reco_thresholds_years )
    signal_stat = merge_x( signal_stat_histos, reco_thresholds_years )

    fiducial_variable   = "GenPhotonCMSUnfold0_pt"
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds     = [20, 35, 50, 65, 80, 120, 160, 200, 260, 320, 400]
    fiducial_overflow       = "upper"
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    tex_reco = "p^{reco}_{T}(#gamma) (GeV)"
    tex_gen  = "p^{gen}_{T}(#gamma) (GeV)"
    tex_unf  = "p^{fid.}_{T}(#gamma) (GeV)"
    texY     = 'Fiducial cross section (fb)'    
    y_range         = (9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.7,1.3)
    data_legendText = "Data (137/fb)"
    mc_legendText =   "Simulation"

    unfolding_data_input      = data
    lumi_factor               = (lumi_year[2016]+lumi_year[2017]+lumi_year[2018])/1000.

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

class expected_absEta_RunII:
    expected        = True
    cache_directory = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/"
    data_key        = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addMisIDSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_data_%s"
    signal_key      = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addMisIDSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_signal_%s"
    signal_stat_key = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addMisIDSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_signal_stat_%s"

    cache_dir       = os.path.join(cache_directory, "unfolding", "combined", "bkgSubstracted", "expected" if expected else "observed")
    dirDB           = MergingDirDB(cache_dir)

    years           = ["2016", "2017", "2018"]

    data_histos     =  [ dirDB.get( data_key%year ) for year in years ]
    signal_histos   =  [ dirDB.get( signal_key%year ) for year in years ]
    signal_stat_histos=[ dirDB.get( signal_stat_key%year ) for year in years ]

    reco_variable   = { "absEta_reco":"abs(PhotonGood0_eta)"}
    reco_selection  = "SR3p"

    assert len(set( map( thresholds_from_histo, data_histos)))==1, "Not all data histos have the same x-axis binning!"
    assert len(set( map( thresholds_from_histo, signal_histos)))==1, "Not all signal histos have the same x-axis binning!"
    assert len(set( map( thresholds_from_histo, signal_stat_histos)))==1, "Not all signal-stat histos have the same x-axis binning!"

    reco_thresholds = thresholds_from_histo( data_histos[0] )
    # appending reco thresholds for multiple years
    reco_overflow        = None
    max_reco_val         = reco_thresholds[-1]
    min_reco_val         = reco_thresholds[0]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    # events not in the reco region are filled with this value
    reco_variable_underflow = reco_thresholds[0]-0.5

    # make reco_thresholds for all years
    reco_thresholds_years = list(copy.deepcopy(reco_thresholds))
    for i_year in range(1, len(years)):
        reco_thresholds_years +=  [ x + (max_reco_val-min_reco_val)*i_year for x in reco_thresholds[1:] ]

    data        = merge_x( data_histos, reco_thresholds_years )
    signal      = merge_x( signal_histos, reco_thresholds_years )
    signal_stat = merge_x( signal_stat_histos, reco_thresholds_years )

    fiducial_variable   = {"absEta_fid":"abs(GenPhotonCMSUnfold0_eta)"}
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds = [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.45]
    fiducial_overflow       = None

    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    tex_reco = "|#eta^{reco}(#gamma)|"
    tex_gen  = "|#eta^{gen}(#gamma)|"
    tex_unf  = "|#eta^{fid.}(#gamma)|"
    texY     = 'Fiducial cross section (fb)'    
    y_range         = (0.9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.39,1.61)
    data_legendText = "Data (137/fb)"
    mc_legendText =   "Simulation"

    unfolding_data_input      = data
    lumi_factor               = (lumi_year[2016]+lumi_year[2017]+lumi_year[2018])/1000.

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

class final_absEta_2016:
    expected        = False
    cache_directory = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/cache_read"
    data_key        = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_data"
    signal_key      = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_signal"
    signal_stat_key = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_signal_stat"

    cache_dir       = os.path.join(cache_directory, "unfolding", "2016", "bkgSubstracted", "expected" if expected else "observed")
    dirDB           = MergingDirDB(cache_dir)

    data            = dirDB.get( data_key )
    signal          = dirDB.get( signal_key )
    signal_stat     = dirDB.get( signal_stat_key )

    years           = ["2016"]

    reco_variable   = { "absEta_reco":"abs(PhotonGood0_eta)"}
    reco_selection  = "SR3p"
    
    reco_thresholds = thresholds_from_histo( data )

    # events not in the reco region are filled with this value
    reco_variable_underflow = -1

    fiducial_variable   = {"absEta_fid":"abs(GenPhotonCMSUnfold0_eta)"}
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    fiducial_thresholds = [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.45]
    
    fiducial_overflow       = None
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    # appending reco thresholds for multiple years
    reco_overflow        = None
    max_reco_val         = reco_thresholds[-1]
    min_reco_val         = reco_thresholds[0]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    reco_thresholds_years = copy.deepcopy(reco_thresholds)
    #for i_year in range(1, len(years)):
    #    reco_thresholds_years += [t + i_year*max_reco_val for t in reco_thresholds]

    tex_reco = "|#eta(#gamma)|^{reco}"
    tex_gen  = "|#eta(#gamma)|^{gen}"
    tex_unf  = "|#eta(#gamma)|^{fid.}"
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

class final_dRlg_2016:
    expected        = False
    cache_directory = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/cache_read"
    data_key        = "bkgSubtracted_SR3pdRUnfold_addDYSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_data"
    signal_key      = "bkgSubtracted_SR3pdRUnfold_addDYSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_signal"
    signal_stat_key = "bkgSubtracted_SR3pdRUnfold_addDYSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_signal_stat"

    cache_dir       = os.path.join(cache_directory, "unfolding", "2016", "bkgSubstracted", "expected" if expected else "observed")
    dirDB           = MergingDirDB(cache_dir)

    data            = dirDB.get( data_key )
    signal          = dirDB.get( signal_key )
    signal_stat     = dirDB.get( signal_stat_key )

    years           = ["2016"]

    reco_variable   = { "dRlg_reco":"sqrt((PhotonGood0_eta-LeptonTight0_eta)**2+acos(cos(PhotonGood0_phi-LeptonTight0_phi))**2)"}
    reco_selection  = "SR3p"
    
    reco_thresholds = thresholds_from_histo( data )

    # events not in the reco region are filled with this value
    reco_variable_underflow = -1

    fiducial_variable   = "genLCMStight0GammadR"
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    #extra_fiducial_selection_str = "genLCMStight0GammadR<3.4"
    fiducial_thresholds     = (0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2, 3.4)
    #plot_range_x_fiducial   = (0.4, 3.2)
    #fiducial_thresholds     = reco_thresholds[::2]
    #if fiducial_thresholds[-1]!=reco_thresholds[-1]:
    #    fiducial_thresholds=list(fiducial_thresholds)
    #    fiducial_thresholds[-1]=reco_thresholds[-1]
    #    fiducial_thresholds=tuple(fiducial_thresholds)
    
    fiducial_overflow       = "upper"
    #underflow_fiducial_val  = fiducial_thresholds[0]-0.5 # only for fiducial_overflow = None
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    # appending reco thresholds for multiple years
    reco_overflow        = "upper"
    max_reco_val         = reco_thresholds[-1]
    min_reco_val         = reco_thresholds[0]
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

class expected_dRlg_RunII:
    expected        = True
    cache_directory = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/"
    data_key        = "bkgSubtracted_SR3pdRUnfold_addDYSF_addMisIDSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_data_%s"
    signal_key      = "bkgSubtracted_SR3pdRUnfold_addDYSF_addMisIDSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_signal_%s"
    signal_stat_key = "bkgSubtracted_SR3pdRUnfold_addDYSF_addMisIDSF_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_signal_stat_%s"

    cache_dir       = os.path.join(cache_directory, "unfolding", "combined", "bkgSubstracted", "expected" if expected else "observed")
    dirDB           = MergingDirDB(cache_dir)

    years           = ["2016", "2017", "2018"]

    data_histos     =  [ dirDB.get( data_key%year ) for year in years ]
    signal_histos   =  [ dirDB.get( signal_key%year ) for year in years ]
    signal_stat_histos=[ dirDB.get( signal_stat_key%year ) for year in years ]

    reco_variable   = { "dRlg_reco":"sqrt((PhotonGood0_eta-LeptonTight0_eta)**2+acos(cos(PhotonGood0_phi-LeptonTight0_phi))**2)"}
    reco_selection  = "SR3p"
    
    reco_thresholds = thresholds_from_histo( data_histos[0] )

    # events not in the reco region are filled with this value
    reco_variable_underflow = -1
    # appending reco thresholds for multiple years
    reco_overflow        = "upper"
    max_reco_val         = reco_thresholds[-1]
    min_reco_val         = reco_thresholds[0]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    # events not in the reco region are filled with this value
    reco_variable_underflow = reco_thresholds[0]-0.5

    # make reco_thresholds for all years
    reco_thresholds_years = list(copy.deepcopy(reco_thresholds))
    for i_year in range(1, len(years)):
        reco_thresholds_years +=  [ x + (max_reco_val-min_reco_val)*i_year for x in reco_thresholds[1:] ]

    data        = merge_x( data_histos, reco_thresholds_years )
    signal      = merge_x( signal_histos, reco_thresholds_years )
    signal_stat = merge_x( signal_stat_histos, reco_thresholds_years )

    fiducial_variable   = "genLCMStight0GammadR"
    fiducial_selection  = "nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1"
    #extra_fiducial_selection_str = "sqrt((PhotonGood0_eta-LeptonTight0_eta)**2+acos(cos(PhotonGood0_phi-LeptonTight0_phi))**2)<3.4"
    fiducial_thresholds     = (0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2, 3.4)
    #plot_range_x_fiducial   = (0.4, 3.2)
    #if fiducial_thresholds[-1]!=reco_thresholds[-1]:
    #    fiducial_thresholds=list(fiducial_thresholds)
    #    fiducial_thresholds[-1]=reco_thresholds[-1]
    #    fiducial_thresholds=tuple(fiducial_thresholds)
    
    fiducial_overflow       = "upper"
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    tex_reco = "#Delta R(#gamma, l)^{reco}"
    tex_gen  = "#Delta R(#gamma, l)^{gen}"
    tex_unf  = "#Delta R(#gamma, l)^{fid.}"
    texY     = 'Fiducial cross section (fb)'    
    y_range         = (0.9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.39,1.61)
    data_legendText = "Data (137/fb)"
    mc_legendText =   "Simulation"

    unfolding_data_input      = data
    lumi_factor               = (lumi_year[2016]+lumi_year[2017]+lumi_year[2018])/1000.

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
