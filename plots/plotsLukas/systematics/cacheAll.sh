while read x; do echo $x; rm missing.sh; cmssw ${x}; submit --title sys16 missing.sh; done < systematicVariation.sh
