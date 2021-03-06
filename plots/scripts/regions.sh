path="${CMSSW_BASE}/src/TTGammaEFT/plots/plotsLukas/regions"
cdir="limits/cardFiles/defaultSetup/observed"

runNotifier.sh "python ${path}/signalRegionPlot.py --cardfile ${1} --carddir ${cdir} --year 2016"
runNotifier.sh "python ${path}/signalRegionPlot.py --cardfile ${1} --carddir ${cdir} --year 2016 --postFit"
runNotifier.sh "python ${path}/signalRegionPlot_sorted.py --cardfile ${1} --carddir ${cdir} --year 2016"
runNotifier.sh "python ${path}/signalRegionPlot_sorted.py --cardfile ${1} --carddir ${cdir} --year 2016 --postFit"

runNotifier.sh "python ${path}/covMatrixPlot.py --cardfile ${1} --carddir ${cdir} --year 2016 --postFit"
runNotifier.sh "python ${path}/covMatrixPlot.py --cardfile ${1} --carddir ${cdir} --year 2016"
runNotifier.sh "python ${path}/fitMatrixPlot.py --cardfile ${1} --carddir ${cdir} --year 2016 --restrict"
runNotifier.sh "python ${path}/fitMatrixPlot.py --cardfile ${1} --carddir ${cdir} --year 2016"

