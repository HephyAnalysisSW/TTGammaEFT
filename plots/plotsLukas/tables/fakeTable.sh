
selections=(
            "SR3","Fake Region 3 Jets"
            "SR4p","Fake Region geq 4 Jets"
)

leps=("all" "e" "mu")

cat header > tables/faketables_est_2016.tex
echo " " >> tables/faketables_est_2016.tex

echo "\section{Yields - Semileptonic Channel 2016}" >> tables/faketables_est_2016.tex
echo " " >> tables/faketables_est_2016.tex

for seltuple in "${selections[@]}"; do 
    IFS=","; set -- ${seltuple};
    sel=$1;
    label=$2;
    echo ${sel}
#    python fakeTable.py --year 2016 --controlRegion ${sel} --label $label
    for lep in "${leps[@]}"; do
        cat logs/2016_fake_${sel}-${lep}.log >> tables/faketables_est_2016.tex
    done
done

echo " " >> tables/faketables_est_2016.tex

echo " " >> tables/faketables_est_2016.tex
echo "\end{document}" >> tables/faketables_est_2016.tex
