import os

redirector        = "root://hephyse.oeaw.ac.at/"
redirector_global = "root://cms-xrd-global.cern.ch/"

if os.environ["USER"] in ["schoef", "rschoefbeck", "schoefbeck"]:
    results_directory               = "/afs/hephy.at/data/rschoefbeck02/TTGammaEFT/results/"
    tmp_directory                   = "/afs/hephy.at/data/rschoefbeck02/TTGammaEFT_tmp/"
    plot_directory                  = "/afs/hephy.at/user/r/rschoefbeck/www/TTGammaEFT/"
    postprocessing_directory        = "TTGammaEFT_PP_2016_TTG_v5/inclusive/"
    postprocessing_output_directory = "/afs/hephy.at/data/rschoefbeck02/cmgTuples/"
    analysis_results                = results_directory

    cache_directory                     = "/afs/hephy.at/data/rschoefbeck01/TTGammaEFT/cache/"

    mva_directory                       = "/afs/hephy.at/data/llechner01/TTGammaEFT/mva/"
    dpm_directory                       = "/dpm/oeaw.ac.at/home/cms/store/user/llechner/"
    eos_directory                       = "/eos/cms/store/group/phys_susy/hephy/"

if os.environ["USER"] in ["llechner"]:
    tmp_directory                       = "/afs/hephy.at/data/llechner01/Top_tmp/"
    results_directory                   = "/afs/hephy.at/data/llechner01/TTGammaEFT/results/"

    mva_directory                       = "/afs/hephy.at/data/llechner01/TTGammaEFT/mva/"

    plot_directory                      = "/afs/hephy.at/user/l/llechner/www/TTGammaEFT/"

    postprocessing_output_directory     = "/afs/hephy.at/data/llechner03/TTGammaEFT/nanoTuples/"
    gridpack_directory                  = "/afs/hephy.at/data/llechner01/TTGammaEFT/gridpacks/"

    analysis_results                    = results_directory
    cache_directory                     = "/afs/hephy.at/data/llechner01/TTGammaEFT/cache/"
    combineReleaseLocation              = "/afs/hephy.at/work/l/llechner/CMSSW_10_2_9/src/"
    cardfileLocation                    = "/afs/hephy.at/data/llechner01/TTGammaEFT/results/cardfiles/"

    dpm_directory                       = "/dpm/oeaw.ac.at/home/cms/store/user/llechner/"
    eos_directory                       = "/eos/cms/store/group/phys_susy/hephy/"

if os.environ["USER"] in ["ttschida"]:
    plot_directory                      = "/afs/hephy.at/user/t/ttschida/www/HiggsWithoutHiggs/TTGammaEFT/"
    dpm_directory                       = "/dpm/oeaw.ac.at/home/cms/store/user/llechner/"
    results_directory                   = "/afs/hephy.at/data/cms04/ttschida/TTGammaEFT/results/"
    tmp_directory                       = "/afs/hephy.at/data/cms04/ttschida/TTGammaEFT/tmp/"
    cache_directory                     = "/afs/hephy.at/data/cms04/ttschida/TTGammaEFT/cache/"
    #gridpack_directory                  = "/afs/hephy.at/data/cms04/ttschida/TTGammaEFT/gridpacks/"   
    gridpack_directory                  = "/afs/hephy.at/data/cms04/ttschida/TTXPheno/gridpacks/"
    postprocessing_output_directory     = "/afs/hephy.at/data/cms04/ttschida/TTGammaEFT/Tuples/"
