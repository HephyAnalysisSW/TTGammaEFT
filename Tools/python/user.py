import os

redirector        = "root://hephyse.oeaw.ac.at/"
redirector_global = "root://cms-xrd-global.cern.ch/"

if os.environ["USER"] in ["schoef", "rschoefbeck", "schoefbeck"]:
    results_directory               = "/afs/hephy.at/data/rschoefbeck02/TTGammaEFT/results/"
    tmp_directory                   = "/afs/hephy.at/data/rschoefbeck02/TTGammaEFT_tmp/"
    plot_directory                  = "/afs/hephy.at/user/r/rschoefbeck/www/TTGammaEFT/"
    postprocessing_directory        = "TTGammaEFT_PP_2016_TTG_v5/inclusive/"
    postprocessing_output_directory = "/afs/hephy.at/data/rschoefbeck02/cmgTuples/"
    gridpack_directory              = "/afs/hephy.at/data/llechner01/TTGammaEFT/gridpacks/"
    analysis_results                = results_directory

    cache_directory                     = "/afs/hephy.at/data/rschoefbeck01/TTGammaEFT/cache/"

    mva_directory                       = "/afs/hephy.at/data/rschoefbeck01/TTGammaEFT/mva/"
    dpm_directory                       = '/dpm/oeaw.ac.at/home/cms/store/user/llechner/'
    eos_directory                       = "/eos/cms/store/group/phys_susy/hephy/"

if os.environ["USER"] in ["llechner"]: #Heplx, Lxplus
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


if os.environ["USER"] in ["mfellinger"]: #Heplx, Lxplus
    tmp_directory                       = "/afs/hephy.at/data/mfellinger01/Top_tmp/"
    results_directory                   = "/afs/hephy.at/data/mfellinger01/TTGammaEFT/results/"

    mva_directory                       = "/afs/hephy.at/data/mfellinger01/TTGammaEFT/mva/"

    plot_directory                      = "/afs/hephy.at/user/l/mfellinger/www/TTGammaEFT/"

    postprocessing_output_directory     = "/afs/hephy.at/data/mfellinger03/TTGammaEFT/nanoTuples/"
    gridpack_directory                  = "/afs/hephy.at/data/mfellinger01/TTGammaEFT/gridpacks/"

    analysis_results                    = results_directory
    cache_directory                     = "/afs/hephy.at/data/mfellinger01/TTGammaEFT/cache/"
    combineReleaseLocation              = "/afs/hephy.at/work/l/mfellinger/CMSSW_10_2_9/src/"
    cardfileLocation                    = "/afs/hephy.at/data/mfellinger01/TTGammaEFT/results/cardfiles/"

    dpm_directory                       = "/dpm/oeaw.ac.at/home/cms/store/user/mfellinger/"
    eos_directory                       = "/eos/cms/store/group/phys_susy/hephy/"


if os.environ["USER"] in ["martina.fellinger"]: #CBE cluster
    tmp_directory                       = "/mnt/hephy/cms/martina.fellinger/tmp/TTGammaEFT/"
    results_directory                   = "/mnt/hephy/cms/martina.fellinger/TTGammaEFT/results/"

    mva_directory                       = "/mnt/hephy/cms/martina.fellinger/TTGammaEFT/mva/"
    plot_directory                      = "/mnt/hephy/cms/martina.fellinger/www/TTGammaEFT/"

    postprocessing_output_directory     = "/scratch/lukas.lechner/TTGammaEFT/nanoTuples/postprocessed"
    gridpack_directory                  = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/gridpacks/"

    analysis_results                    = results_directory
    cache_directory                     = "/users/martina.fellinger/public/cache/"

    unfolding_cache_directory           = "/mnt/hephy/cms/martina.fellinger/TTGammaEFT/cache/"
    combineReleaseLocation              = "/users/martina.fellinger/public/CMSSW_10_2_9/src/tmp"
    cardfileLocation                    = "/mnt/hephy/cms/martina.fellinger/TTGammaEFT/results/cardfiles/"

    dpm_directory                       = "/scratch/lukas.lechner/TTGammaEFT/nanoTuples/"
    eos_directory                       = "/mnt/hephy/cms/martina.fellinger/TTGammaEFT/"

if os.environ["USER"] in ["lukas.lechner"]: #CBE cluster
    tmp_directory                       = "/mnt/hephy/cms/lukas.lechner/tmp/TTGammaEFT/"
    results_directory                   = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/results/"

    mva_directory                       = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/mva/"
    plot_directory                      = "/mnt/hephy/cms/lukas.lechner/www/TTGammaEFT/"

    postprocessing_output_directory     = "/scratch/lukas.lechner/TTGammaEFT/nanoTuples/postprocessed/"
    gridpack_directory                  = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/gridpacks/"

    analysis_results                    = results_directory
#    cache_directory                     = "/users/lukas.lechner/public/cache/"
#    cache_directory                     = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/cache/"
    cache_directory                     = "/scratch/lukas.lechner/TTGammaEFT/cache/"
    unfolding_cache_directory           = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/cache/"

    combineReleaseLocation              = "/users/lukas.lechner/public/CMSSW_10_2_18/src/tmp/"
    cardfileLocation                    = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/results/cardfiles/"

    dpm_directory                       = "/scratch/lukas.lechner/TTGammaEFT/nanoTuples/"
    eos_directory                       = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/"

if os.environ["USER"] in ["robert.schoefbeck"]: #CBE cluster
    tmp_directory                       = "/mnt/hephy/cms/robert.schoefbeck/tmp/TTGammaEFT/"
    results_directory                   = "/mnt/hephy/cms/robert.schoefbeck/TTGammaEFT/results/"

    mva_directory                       = "/mnt/hephy/cms/robert.schoefbeck/TTGammaEFT/mva/"
    plot_directory                      = "/mnt/hephy/cms/robert.schoefbeck/www/TTGammaEFT/"

    postprocessing_output_directory     = "/scratch/robert.schoefbeck/TTGammaEFT/nanoTuples/postprocessed/"
    gridpack_directory                  = "/mnt/hephy/cms/robert.schoefbeck/TTGammaEFT/gridpacks/"

    analysis_results                    = results_directory
    cache_directory                     = "/users/robert.schoefbeck/public/cache/"
    unfolding_cache_directory           = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/cache/"
    combineReleaseLocation              = "/users/robert.schoefbeck/public/CMSSW_10_2_18/src/tmp/"
    cardfileLocation                    = "/mnt/hephy/cms/robert.schoefbeck/TTGammaEFT/results/cardfiles/"

    dpm_directory                       = "/scratch/lukas.lechner/TTGammaEFT/nanoTuples/"
    eos_directory                       = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/"

if os.environ["USER"] in ["rosmarie.schoefbeck"]: #CBE cluster
    tmp_directory                       = "/mnt/hephy/cms/rosmarie.schoefbeck/tmp/TTGammaEFT/"
    results_directory                   = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/results/"

    mva_directory                       = "/mnt/hephy/cms/rosmarie.schoefbeck/TTGammaEFT/mva/"
    plot_directory                      = "/mnt/hephy/cms/rosmarie.schoefbeck/www/TTGammaEFT/"

    postprocessing_output_directory     = "/scratch/lukas.lechner/TTGammaEFT/nanoTuples/postprocessed/" 
    gridpack_directory                  = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/gridpacks/"

    analysis_results                    = results_directory
    cache_directory                     = "/users/rosmarie.schoefbeck/public/cache/"
    combineReleaseLocation              = "/users/rosmarie.schoefbeck/public/CMSSW_10_2_18/src/tmp/"
    cardfileLocation                    = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/results/cardfiles/"

#    dpm_directory                       = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/nanoTuples/"
    dpm_directory                       = "/scratch/lukas.lechner/TTGammaEFT/nanoTuples/"
    eos_directory                       = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/"

if os.environ["USER"] in ["ttschida"]:
    plot_directory                      = "/afs/hephy.at/user/t/ttschida/www/HiggsWithoutHiggs/TTGammaEFT/"
    dpm_directory                       = "/dpm/oeaw.ac.at/home/cms/store/user/llechner/"
    results_directory                   = "/afs/hephy.at/data/cms04/ttschida/TTGammaEFT/results/"
    tmp_directory                       = "/afs/hephy.at/data/cms04/ttschida/TTGammaEFT/tmp/"
    cache_directory                     = "/afs/hephy.at/data/cms04/ttschida/TTGammaEFT/cache/"
    #gridpack_directory                  = "/afs/hephy.at/data/cms04/ttschida/TTGammaEFT/gridpacks/"   
    gridpack_directory                  = "/afs/hephy.at/data/cms04/ttschida/TTXPheno/gridpacks/"
    postprocessing_output_directory     = "/afs/hephy.at/data/cms04/ttschida/TTGammaEFT/Tuples/"

if os.environ["USER"] in ["lgoldsch"]:
    results_directory               = "/afs/hephy.at/data/rschoefbeck02/TTGammaEFT/results/"
#    plot_directory                  = "/afs/cern.ch/user/l/lgoldsch/public/CMSSW_10_2_9/src/TTGammaEFT/plots/LukasG_plots" #  "/afs/hephy.at/user/l/lgoldschmied/www/plots"
    plot_directory                  = "/afs/hephy.at/user/l/lgoldschmied/www/plots"
    dpm_directory                   = "/dpm/oeaw.ac.at/home/cms/store/user/llechner/"
    eos_directory                   = "/eos/cms/store/group/phys_susy/hephy/"
    cache_directory                 = "/afs/hephy.at/data/llechner01/TTGammaEFT/cache/"

if os.environ["USER"] in ["meikee.pagsinohin"]: #CBE cluster
    tmp_directory                       = "/mnt/hephy/cms/meikee.pagsinohin/tmp/TTGammaEFT/"
    results_directory                   = "/mnt/hephy/cms/meikee.pagsinohin/TTGammaEFT/results/"

    mva_directory                       = "/mnt/hephy/cms/meikee.pagsinohin/TTGammaEFT/mva/"
    plot_directory                      = "/mnt/hephy/cms/meikee.pagsinohin/www/TTGammaEFT/"

    postprocessing_output_directory     = "/scratch/lukas.lechner/TTGammaEFT/nanoTuples/postprocessed/"
    gridpack_directory                  = "/mnt/hephy/cms/lukas.lechner/TTGammaEFT/gridpacks/"

    analysis_results                    = results_directory
    cache_directory                     = "/users/meikee.pagsinohin/public/cache/"
    unfolding_cache_directory           = "/mnt/hephy/cms/meikee.pagsinohin/TTGammaEFT/cache/"

    combineReleaseLocation              = "/users/meikee.pagsinohin/public/CMSSW_10_2_18/src/tmp/"
    cardfileLocation                    = "/mnt/hephy/cms/meikee.pagsinohin/TTGammaEFT/results/cardfiles/"

    dpm_directory                       = "/scratch/lukas.lechner/TTGammaEFT/nanoTuples/"
    eos_directory                       = "/mnt/hephy/cms/meikee.pagsinohin/TTGammaEFT/"


