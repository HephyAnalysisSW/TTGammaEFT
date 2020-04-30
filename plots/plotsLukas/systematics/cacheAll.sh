while read x; do echo $x; cmssw ${x}; submit --title sys16 missing.sh; done < systematicVariation.sh
