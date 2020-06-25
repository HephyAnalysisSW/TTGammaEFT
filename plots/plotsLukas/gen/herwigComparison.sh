runNotifier.sh "python herwigComparison.py --version herwig_v6 --plot_directory runCardComparison --selection all"
runNotifier.sh "python herwigComparison.py --normalize --version herwig_v6 --plot_directory runCardComparison --selection all"

runNotifier.sh "python herwigComparison.py --version herwig_v6 --plot_directory runCardComparison --selection dilepOS-leadLepPT15-nPhoton1p-pTG15"
runNotifier.sh "python herwigComparison.py --version herwig_v6 --plot_directory runCardComparison --selection nLep1-leadLepPT15-nPhoton1p-pTG15"
runNotifier.sh "python herwigComparison.py --normalize --version herwig_v6 --plot_directory runCardComparison --selection dilepOS-leadLepPT15-nPhoton1p-pTG15"
runNotifier.sh "python herwigComparison.py --normalize --version herwig_v6 --plot_directory runCardComparison --selection nLep1-leadLepPT15-nPhoton1p-pTG15"

runNotifier.sh "python herwigComparison.py --version herwig_v6 --plot_directory runCardComparison --selection dilepOS"
runNotifier.sh "python herwigComparison.py --version herwig_v6 --plot_directory runCardComparison --selection nLep1"
runNotifier.sh "python herwigComparison.py --normalize --version herwig_v6 --plot_directory runCardComparison --selection dilepOS"
runNotifier.sh "python herwigComparison.py --normalize --version herwig_v6 --plot_directory runCardComparison --selection nLep1"

runNotifier.sh "python herwigComparison.py --version herwig_v6 --plot_directory runCardComparison --selection dilepOS-nJet2p"
runNotifier.sh "python herwigComparison.py --version herwig_v6 --plot_directory runCardComparison --selection nLep1-nJet4p"
runNotifier.sh "python herwigComparison.py --normalize --version herwig_v6 --plot_directory runCardComparison --selection dilepOS-nJet2p"
runNotifier.sh "python herwigComparison.py --normalize --version herwig_v6 --plot_directory runCardComparison --selection nLep1-nJet4p"
