year="2018"
carddir="limits/cardFiles/defaultSetup/observed"
cachedir="/afs/hephy.at/data/llechner01/TTGammaEFT/cache/analysis/"

cardpath=${cachedir}/${year}/${carddir}
for FILE in ${cardpath}/*.txt; do
    if [[ $FILE == *"shape"* ]]; then continue; fi
    card="$(basename -- $FILE)"
    card=${card%.txt}

    python impactPlot.py $@ --carddir ${carddir} --cardfile ${card} --year ${year} --cores 6 #--bkgOnly
done
