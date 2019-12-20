path="${CMSSW_BASE}/src/TTGammaEFT/plots/plotsLukas/regions"
cdir="limits/cardFiles/defaultSetup/observed"

runNotifier.sh "python ${path}/fitResults.py --carddir ${cdir} --cardfile ${2} --year ${1} --sorted --plotCovMatrix --plotRegionPlot ${@:3}"
runNotifier.sh "python ${path}/fitResults.py --carddir ${cdir} --cardfile ${2} --year ${1} --sorted --plotCorrelations --plotCovMatrix --plotRegionPlot --plotImpacts --postFit ${@:3}"
