python dataDataComparisonEra.py --year 2017 --mode mu --plot_directory 102X_TTG_ppv41_v1 --selection fake3 --addCut lowSieieNoChgIso --binning 20 0 22.82 --variable "PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt"
python dataDataComparisonEra.py --year 2017 --mode e --plot_directory 102X_TTG_ppv41_v1 --selection fake3 --addCut lowSieieNoChgIso --binning 20 0 22.82 --variable "PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt"
python dataDataComparisonEra.py --year 2017 --mode mu --plot_directory 102X_TTG_ppv41_v1 --selection fake3 --addCut highSieieNoChgIso --binning 20 0 22.82 --variable "PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt"
python dataDataComparisonEra.py --year 2017 --mode e --plot_directory 102X_TTG_ppv41_v1 --selection fake3 --addCut highSieieNoChgIso --binning 20 0 22.82 --variable "PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt"

python dataDataComparisonEra.py --year 2017 --mode mu --plot_directory 102X_TTG_ppv41_v1 --selection fake3 --addCut lowChgIsoNoSieie --binning 20 0.005 0.025 --variable PhotonNoChgIsoNoSieie0_sieie
python dataDataComparisonEra.py --year 2017 --mode e --plot_directory 102X_TTG_ppv41_v1 --selection fake3 --addCut lowChgIsoNoSieie --binning 20 0.005 0.025 --variable PhotonNoChgIsoNoSieie0_sieie
python dataDataComparisonEra.py --year 2017 --mode mu --plot_directory 102X_TTG_ppv41_v1 --selection fake3 --addCut highChgIsoNoSieie --binning 20 0.005 0.025 --variable PhotonNoChgIsoNoSieie0_sieie
python dataDataComparisonEra.py --year 2017 --mode e --plot_directory 102X_TTG_ppv41_v1 --selection fake3 --addCut highChgIsoNoSieie --binning 20 0.005 0.025 --variable PhotonNoChgIsoNoSieie0_sieie

python dataDataComparisonEra.py --year 2017 --mode mu --plot_directory 102X_TTG_ppv41_v1 --selection fake3 --addCut lowChgIsoHighSieie --binning 20 0.005 0.025 --variable PhotonNoChgIsoNoSieie0_sieie
python dataDataComparisonEra.py --year 2017 --mode e --plot_directory 102X_TTG_ppv41_v1 --selection fake3 --addCut lowChgIsoHighSieie --binning 20 0.005 0.025 --variable PhotonNoChgIsoNoSieie0_sieie

