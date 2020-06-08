python mcMcComparisonJets.py --year 2016 --mode mu --plot_directory 102X_TTG_ppv41_v1 --selection fake4p --addCut lowSieieNoChgIso --binning 20 0 22.82 --variable "PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt"
python mcMcComparisonJets.py --year 2016 --mode e --plot_directory 102X_TTG_ppv41_v1 --selection fake4p --addCut lowSieieNoChgIso --binning 20 0 22.82 --variable "PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt"
python mcMcComparisonJets.py --year 2016 --mode mu --plot_directory 102X_TTG_ppv41_v1 --selection fake4p --addCut highSieieNoChgIso --binning 20 0 22.82 --variable "PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt"
python mcMcComparisonJets.py --year 2016 --mode e --plot_directory 102X_TTG_ppv41_v1 --selection fake4p --addCut highSieieNoChgIso --binning 20 0 22.82 --variable "PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt"

python mcMcComparisonJets.py --year 2016 --mode mu --plot_directory 102X_TTG_ppv41_v1 --selection fake4p --addCut lowChgIsoNoSieie --binning 40 0.005 0.025 --variable PhotonNoChgIsoNoSieie0_sieie
python mcMcComparisonJets.py --year 2016 --mode e --plot_directory 102X_TTG_ppv41_v1 --selection fake4p --addCut lowChgIsoNoSieie --binning 40 0.005 0.025 --variable PhotonNoChgIsoNoSieie0_sieie
python mcMcComparisonJets.py --year 2016 --mode mu --plot_directory 102X_TTG_ppv41_v1 --selection fake4p --addCut highChgIsoNoSieie --binning 40 0.005 0.025 --variable PhotonNoChgIsoNoSieie0_sieie
python mcMcComparisonJets.py --year 2016 --mode e --plot_directory 102X_TTG_ppv41_v1 --selection fake4p --addCut highChgIsoNoSieie --binning 40 0.005 0.025 --variable PhotonNoChgIsoNoSieie0_sieie

python mcMcComparisonJets.py --year 2016 --mode mu --plot_directory 102X_TTG_ppv41_v1 --selection fake4p --addCut lowChgIsoHighSieie --binning 40 0.005 0.025 --variable PhotonNoChgIsoNoSieie0_sieie
python mcMcComparisonJets.py --year 2016 --mode e --plot_directory 102X_TTG_ppv41_v1 --selection fake4p --addCut lowChgIsoHighSieie --binning 40 0.005 0.025 --variable PhotonNoChgIsoNoSieie0_sieie

