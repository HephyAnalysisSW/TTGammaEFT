
selections=(
            "VG3","VGamma CR 3 Jets"
            "VG4p","VGamma CR geq 4 Jets"
)

leps=("all" "e" "mu")

cat header > vgtables_est_2018.dat
echo " " >> vgtables_est_2018.dat

echo "\section{Yields - Semileptonic Channel 2018}" >> vgtables_est_2018.dat
echo " " >> vgtables_est_2018.dat

for seltuple in "${selections[@]}"; do 
    IFS=","; set -- ${seltuple};
    sel=$1;
    label=$2;
    echo ${sel}
#    python vgTable.py --year 2018 --controlRegion ${sel} --label $label low Mlg
#    python vgTable.py --year 2018 --controlRegion ${sel} --label $label high Mlg --highMlg
    for lep in "${leps[@]}"; do
        cat logs/2018_${sel}-${lep}_lowMlg.log >> vgtables_est_2018.dat
        cat logs/2018_${sel}-${lep}_highMlg.log >> vgtables_est_2018.dat
    done
done

echo " " >> vgtables_est_2018.dat

echo " " >> tables_est_2018.dat
echo "\end{document}" >> tables_est_2018.dat
