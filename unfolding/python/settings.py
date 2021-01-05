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

#default_cache_directory = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/cache_read/"
#default_cache_directory = "/eos/vbc/user/lukas.lechner/TTGammaEFT/cache_read/"
default_cache_directory = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/cache_read/"

class observed_ptG_2016:
    expected        = False
    cache_directory = default_cache_directory 
    data_key        = "bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_data"
    signal_key      = "bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_signal"
    signal_stat_key = "bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3M3_SR4pM3_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_signal_stat"

    cache_dir       = os.path.join(cache_directory, "unfolding", "2016", "bkgSubstracted", "expected" if expected else "observed", "postFit", "noFreeze")
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
    fiducial_thresholds     = [20, 35, 50, 80, 120, 160, 200, 240, 280, 360] 

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
    tex_pur  = "p_{T}(#gamma) (GeV)"
    texY     = 'Fiducial cross section (fb)'    
    y_range         = (.9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.19,1.81)
    data_legendText = "Data (36/fb)"
    signal_legendText = "Observation"

    lumi_factor               = lumi_year[2016]/1000.
    unfolding_data_input      = data
    unfolding_data_input_systematic_bands          = [
#       {'name' : 'total',
#        'label': "\pm 1\sigma (sys.)",
#        'ref': data,
#        'up':  dirDB.get( data_key+'Up' ),
#        'down':dirDB.get( data_key+'Down' ),
#        'color':ROOT.kBlue,
#        } 
        ]

    unfolding_signal_input        = signal
    unfolding_signal_input_systematic_bands          = [
#       {'name' : 'stat',
#        'label': "\pm 1\sigma (stat.)",
#        'ref': signal,
#        'up':  add_sigmas(signal_stat, +1),
#        'down':add_sigmas(signal_stat, -1),
#        'color':ROOT.kBlue,
#        },
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'ref': data,
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'ref': signal,
        'up':  add_sigmas(signal, +1),
        'down':add_sigmas(signal, -1),
        'color':ROOT.kOrange-9,
        },
        ]


class expected_ptG_RunII:
    cache_directory = default_cache_directory 
    data_key        = "bkgSubtracted_SR3pPtUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_data_%s"
    signal_key      = "bkgSubtracted_SR3pPtUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_signal_%s"
    signal_stat_key = "bkgSubtracted_SR3pPtUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_signal_stat_%s"

    cache_dir       = os.path.join(cache_directory, "unfolding", "combined", "bkgSubstracted", "expected", "postFit", "noFreeze")
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
    fiducial_thresholds     = [20, 35, 50, 80, 120, 160, 200, 240, 280, 360]

    fiducial_overflow       = "upper"
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    tex_reco = "p^{reco}_{T}(#gamma) (GeV)"
    tex_gen  = "p^{gen}_{T}(#gamma) (GeV)"
    tex_unf  = "p^{fid.}_{T}(#gamma) (GeV)"
    tex_pur  = "p_{T}(#gamma) (GeV)"
    texY     = 'Fiducial cross section (fb)'    
    y_range         = (9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.39,1.61)
    data_legendText = "Data (137/fb)"
    signal_legendText = "Observation"

    lumi_factor               = (lumi_year[2016]+lumi_year[2017]+lumi_year[2018])/1000.
    unfolding_data_input      = data
    unfolding_data_input_systematic_bands          = [
#       {'name' : 'total',
#        'label': "\pm 1\sigma (sys.)",
#        'ref': data,
#        'up':  dirDB.get( data_key+'Up' ),
#        'down':dirDB.get( data_key+'Down' ),
#        'color':ROOT.kBlue,
#        } 
        ]

    unfolding_signal_input        = signal
    unfolding_signal_input_systematic_bands          = [
#       {'name' : 'stat',
#        'label': "\pm 1\sigma (stat.)",
#        'ref': signal,
#        'up':  add_sigmas(signal_stat, +1),
#        'down':add_sigmas(signal_stat, -1),
#        'color':ROOT.kBlue,
#        },
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'ref': data,
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'ref': signal,
        'up':  add_sigmas(signal, +1),
        'down':add_sigmas(signal, -1),
        'color':ROOT.kOrange-9,
        },
        ]

class observed_ptG_RunII:
    cache_directory = default_cache_directory 
    data_key        = "bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_data_%s"
    signal_key      = "bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_signal_%s"
    signal_stat_key = "bkgSubtracted_SR3pPtUnfold_addDYSF_addPtBinnedUnc_SR3PtUnfold_SR4pPtUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_signal_stat_%s"

    cache_dir       = os.path.join(cache_directory, "unfolding", "combined", "bkgSubstracted", "observed", "postFit", "noFreeze")
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
    fiducial_thresholds     = [20, 35, 50, 80, 120, 160, 200, 240, 280, 360]

    fiducial_overflow       = "upper"
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    tex_reco = "p^{reco}_{T}(#gamma) (GeV)"
    tex_gen  = "p^{gen}_{T}(#gamma) (GeV)"
    tex_unf  = "p^{fid.}_{T}(#gamma) (GeV)"
    tex_pur  = "p_{T}(#gamma) (GeV)"
    texY     = 'Fiducial cross section (fb)'    
    y_range         = (9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.39,1.61)
    data_legendText = "Data (137/fb)"
    signal_legendText = "Observation"

    lumi_factor               = (lumi_year[2016]+lumi_year[2017]+lumi_year[2018])/1000.
    unfolding_data_input      = data
    unfolding_data_input_systematic_bands          = [
#       {'name' : 'total',
#        'label': "\pm 1\sigma (sys.)",
#        'ref': data,
#        'up':  dirDB.get( data_key+'Up' ),
#        'down':dirDB.get( data_key+'Down' ),
#        'color':ROOT.kBlue,
#        } 
        ]

    unfolding_signal_input        = signal
    unfolding_signal_input_systematic_bands          = [
#       {'name' : 'stat',
#        'label': "\pm 1\sigma (stat.)",
#        'ref': signal,
#        'up':  add_sigmas(signal_stat, +1),
#        'down':add_sigmas(signal_stat, -1),
#        'color':ROOT.kBlue,
#        },
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'ref': data,
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'ref': signal,
        'up':  add_sigmas(signal, +1),
        'down':add_sigmas(signal, -1),
        'color':ROOT.kOrange-9,
        },
        ]

class expected_absEta_RunII:
    expected        = True
    cache_directory = default_cache_directory 
    data_key        = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_data_%s"
    signal_key      = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_signal_%s"
    signal_stat_key = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_signal_stat_%s"

    cache_dir       = os.path.join(cache_directory, "unfolding", "combined", "bkgSubstracted", "expected" if expected else "observed", "postFit", "noFreeze")
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
    fiducial_thresholds = [0, 0.3, 0.6, 0.9, 1.2, 1.45]
    fiducial_overflow       = None

    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    tex_reco = "|#eta^{reco}(#gamma)|"
    tex_gen  = "|#eta^{gen}(#gamma)|"
    tex_unf  = "|#eta^{fid.}(#gamma)|"
    tex_pur  = "|#eta(#gamma)|"
    texY     = 'Fiducial cross section (fb)'    
    y_range         = (0.9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.39,1.61)
    data_legendText = "Data (137/fb)"
    signal_legendText = "Observation"

    lumi_factor               = (lumi_year[2016]+lumi_year[2017]+lumi_year[2018])/1000.
    unfolding_data_input      = data
    unfolding_data_input_systematic_bands          = [
#       {'name' : 'total',
#        'label': "\pm 1\sigma (sys.)",
#        'ref': data,
#        'up':  dirDB.get( data_key+'Up' ),
#        'down':dirDB.get( data_key+'Down' ),
#        'color':ROOT.kBlue,
#        } 
        ]

    unfolding_signal_input        = signal
    unfolding_signal_input_systematic_bands          = [
#       {'name' : 'stat',
#        'label': "\pm 1\sigma (stat.)",
#        'ref': signal,
#        'up':  add_sigmas(signal_stat, +1),
#        'down':add_sigmas(signal_stat, -1),
#        'color':ROOT.kBlue,
#        },
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'ref': data,
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'ref': signal,
        'up':  add_sigmas(signal, +1),
        'down':add_sigmas(signal, -1),
        'color':ROOT.kOrange-9,
        },
        ]

class observed_absEta_RunII:
    expected        = False
    cache_directory = default_cache_directory 
    data_key        = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_data_%s"
    signal_key      = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_signal_%s"
    signal_stat_key = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_signal_stat_%s"

    cache_dir       = os.path.join(cache_directory, "unfolding", "combined", "bkgSubstracted", "expected" if expected else "observed", "postFit", "noFreeze")
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
    fiducial_thresholds = [0, 0.3, 0.6, 0.9, 1.2, 1.45]
    fiducial_overflow       = None

    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])

    tex_reco = "|#eta^{reco}(#gamma)|"
    tex_gen  = "|#eta^{gen}(#gamma)|"
    tex_unf  = "|#eta^{fid.}(#gamma)|"
    tex_pur  = "|#eta(#gamma)|"
    texY     = 'Fiducial cross section (fb)'    
    y_range         = (0.9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.39,1.61)
    data_legendText = "Data (137/fb)"
    signal_legendText = "Observation"

    lumi_factor               = (lumi_year[2016]+lumi_year[2017]+lumi_year[2018])/1000.
    unfolding_data_input      = data
    unfolding_data_input_systematic_bands          = [
#       {'name' : 'total',
#        'label': "\pm 1\sigma (sys.)",
#        'ref': data,
#        'up':  dirDB.get( data_key+'Up' ),
#        'down':dirDB.get( data_key+'Down' ),
#        'color':ROOT.kBlue,
#        } 
        ]

    unfolding_signal_input        = signal
    unfolding_signal_input_systematic_bands          = [
#       {'name' : 'stat',
#        'label': "\pm 1\sigma (stat.)",
#        'ref': signal,
#        'up':  add_sigmas(signal_stat, +1),
#        'down':add_sigmas(signal_stat, -1),
#        'color':ROOT.kBlue,
#        },
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'ref': data,
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'ref': signal,
        'up':  add_sigmas(signal, +1),
        'down':add_sigmas(signal, -1),
        'color':ROOT.kOrange-9,
        },
        ]

class observed_absEta_2016:
    expected        = False
    cache_directory = default_cache_directory 
    data_key        = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_data"
    signal_key      = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_signal"
    signal_stat_key = "bkgSubtracted_SR3pAbsEtaUnfold_addDYSF_addPtBinnedUnc_SR3AbsEtaUnfold_SR4pAbsEtaUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_signal_stat"

    cache_dir       = os.path.join(cache_directory, "unfolding", "2016", "bkgSubstracted", "expected" if expected else "observed", "postFit", "noFreeze")

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
    fiducial_thresholds = [0, 0.3, 0.6, 0.9, 1.2, 1.45]
    
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

    tex_reco = "|#eta^{reco}(#gamma)|"
    tex_gen  = "|#eta^{gen}(#gamma)|"
    tex_unf  = "|#eta^{fid.}(#gamma)|"
    tex_pur  = "|#eta(#gamma)|"
    texY     = 'Fiducial cross section (fb)'    
    y_range         = (0.9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.39,1.61)
    data_legendText = "Data (36/fb)"
    signal_legendText = "Observation"

    lumi_factor               = lumi_year[2016]/1000.
    unfolding_data_input      = data
    unfolding_data_input_systematic_bands          = [
#       {'name' : 'total',
#        'label': "\pm 1\sigma (sys.)",
#        'ref': data,
#        'up':  dirDB.get( data_key+'Up' ),
#        'down':dirDB.get( data_key+'Down' ),
#        'color':ROOT.kBlue,
#        } 
        ]

    unfolding_signal_input        = signal
    unfolding_signal_input_systematic_bands          = [
#       {'name' : 'stat',
#        'label': "\pm 1\sigma (stat.)",
#        'ref': signal,
#        'up':  add_sigmas(signal_stat, +1),
#        'down':add_sigmas(signal_stat, -1),
#        'color':ROOT.kBlue,
#        },
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'ref': data,
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'ref': signal,
        'up':  add_sigmas(signal, +1),
        'down':add_sigmas(signal, -1),
        'color':ROOT.kOrange-9,
        },
        ]

class observed_dRlg_2016:
    expected        = False
    cache_directory = default_cache_directory 
    data_key        = "bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_data"
    signal_key      = "bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_signal"
    signal_stat_key = "bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_signal_stat"

    cache_dir       = os.path.join(cache_directory, "unfolding", "2016", "bkgSubstracted", "expected" if expected else "observed", "postFit", "noFreeze")
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
    fiducial_thresholds     = (0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.4)
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
    tex_pur  = "#Delta R(#gamma, l)"
    texY     = 'Fiducial cross section (fb)'    
    y_range         = (0.9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.39,1.61)
    data_legendText = "Data (36/fb)"
    signal_legendText =   "Observation"

    lumi_factor               = lumi_year[2016]/1000.
    unfolding_data_input      = data
    unfolding_data_input_systematic_bands          = [
#       {'name' : 'total',
#        'label': "\pm 1\sigma (sys.)",
#        'ref': data,
#        'up':  dirDB.get( data_key+'Up' ),
#        'down':dirDB.get( data_key+'Down' ),
#        'color':ROOT.kBlue,
#        } 
        ]

    unfolding_signal_input        = signal
    unfolding_signal_input_systematic_bands          = [
#       {'name' : 'stat',
#        'label': "\pm 1\sigma (stat.)",
#        'ref': signal,
#        'up':  add_sigmas(signal_stat, +1),
#        'down':add_sigmas(signal_stat, -1),
#        'color':ROOT.kBlue,
#        },
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'ref': data,
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'ref': signal,
        'up':  add_sigmas(signal, +1),
        'down':add_sigmas(signal, -1),
        'color':ROOT.kOrange-9,
        },
        ]

class expected_dRlg_RunII:
    expected        = True
    cache_directory = default_cache_directory 
    data_key        = "bkgSubtracted_SR3pdRUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_data_%s"
    signal_key      = "bkgSubtracted_SR3pdRUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_signal_%s"
    signal_stat_key = "bkgSubtracted_SR3pdRUnfold_addDYSF_addMisIDSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF_addPtBinnedUnc_signal_stat_%s"

    cache_dir       = os.path.join(cache_directory, "unfolding", "combined", "bkgSubstracted", "expected" if expected else "observed", "postFit", "noFreeze")
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
    fiducial_thresholds     = (0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.4)
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
    tex_pur  = "#Delta R(#gamma, l)"
    texY     = 'Fiducial cross section (fb)'    
    y_range         = (0.9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.39,1.61)
    data_legendText = "Data (137/fb)"
    signal_legendText =  "Observation"

    lumi_factor               = (lumi_year[2016]+lumi_year[2017]+lumi_year[2018])/1000.
    unfolding_data_input      = data
    unfolding_data_input_systematic_bands          = [
#       {'name' : 'total',
#        'label': "\pm 1\sigma (sys.)",
#        'ref': data,
#        'up':  dirDB.get( data_key+'Up' ),
#        'down':dirDB.get( data_key+'Down' ),
#        'color':ROOT.kBlue,
#        } 
        ]

    unfolding_signal_input        = signal
    unfolding_signal_input_systematic_bands          = [
#       {'name' : 'stat',
#        'label': "\pm 1\sigma (stat.)",
#        'ref': signal,
#        'up':  add_sigmas(signal_stat, +1),
#        'down':add_sigmas(signal_stat, -1),
#        'color':ROOT.kBlue,
#        },
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'ref': data,
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'ref': signal,
        'up':  add_sigmas(signal, +1),
        'down':add_sigmas(signal, -1),
        'color':ROOT.kOrange-9,
        },
        ]




class observed_dRlg_RunII:
    expected        = False
    cache_directory = default_cache_directory 
    data_key        = "bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_data_%s"
    signal_key      = "bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_signal_%s"
    signal_stat_key = "bkgSubtracted_SR3pdRUnfold_addDYSF_addPtBinnedUnc_SR3dRUnfold_SR4pdRUnfold_VG3_VG4p_misDY3_misDY4p_addDYSF_addPtBinnedUnc_signal_stat_%s"

    cache_dir       = os.path.join(cache_directory, "unfolding", "combined", "bkgSubstracted", "expected" if expected else "observed", "postFit", "noFreeze")
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
    fiducial_thresholds     = (0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.4)
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
    tex_pur  = "#Delta R(#gamma, l)"
    texY     = 'Fiducial cross section (fb)'    
    y_range         = (0.9, "auto") #(0.9, 9000)
    y_range_ratio   = (0.39,1.61)
    data_legendText = "Data (137/fb)"
    signal_legendText =  "Observation"

    lumi_factor               = (lumi_year[2016]+lumi_year[2017]+lumi_year[2018])/1000.
    unfolding_data_input      = data
    unfolding_data_input_systematic_bands          = [
#       {'name' : 'total',
#        'label': "\pm 1\sigma (sys.)",
#        'ref': data,
#        'up':  dirDB.get( data_key+'Up' ),
#        'down':dirDB.get( data_key+'Down' ),
#        'color':ROOT.kBlue,
#        } 
        ]

    unfolding_signal_input        = signal
    unfolding_signal_input_systematic_bands          = [
#       {'name' : 'stat',
#        'label': "\pm 1\sigma (stat.)",
#        'ref': signal,
#        'up':  add_sigmas(signal_stat, +1),
#        'down':add_sigmas(signal_stat, -1),
#        'color':ROOT.kBlue,
#        },
       {'name' : 'stat',
        'label': "\pm 1\sigma (stat.)",
        'ref': data,
        'up':  add_sigmas(data, +1),
        'down':add_sigmas(data, -1),
        'color':ROOT.kBlue -10,
        },
       {'name' : 'total',
        'label': "\pm 1\sigma (tot.)",
        'ref': signal,
        'up':  add_sigmas(signal, +1),
        'down':add_sigmas(signal, -1),
        'color':ROOT.kOrange-9,
        },
        ]

