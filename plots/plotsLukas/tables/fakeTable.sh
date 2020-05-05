
selections=(
            "SR3","Fake Region 3 Jets"
            "SR4p","Fake Region geq 4 Jets"
)

leps=("all" "e" "mu")

cat header > faketables_est_2018.dat
echo " " >> faketables_est_2018.dat

echo "\section{Yields - Semileptonic Channel 2018}" >> faketables_est_2018.dat
echo " " >> faketables_est_2018.dat

for seltuple in "${selections[@]}"; do 
    IFS=","; set -- ${seltuple};
    sel=$1;
    label=$2;
    echo ${sel}
#    python fakeTable.py --year 2018 --controlRegion ${sel} --label $label
    for lep in "${leps[@]}"; do
        cat logs/2018_fake_${sel}-${lep}.log >> faketables_est_2018.dat
    done
done

echo " " >> faketables_est_2018.dat

echo " " >> faketables_est_2018.dat
echo "\end{document}" >> faketables_est_2018.dat
