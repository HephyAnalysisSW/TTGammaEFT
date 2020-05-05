
selections=(
            "VG3","VGamma CR 3 Jets"
            "VG4p","VGamma CR geq 4 Jets"
)

leps=("all" "e" "mu")

cat header > tables/vgtables_est_2016.tex
echo " " >> tables/vgtables_est_2016.tex

echo "\section{Yields - Semileptonic Channel 2016}" >> tables/vgtables_est_2016.tex
echo " " >> tables/vgtables_est_2016.tex

for seltuple in "${selections[@]}"; do 
    IFS=","; set -- ${seltuple};
    sel=$1;
    label=$2;
    echo ${sel}
#    python vgTable.py --year 2016 --controlRegion ${sel} --label $label low Mlg
#    python vgTable.py --year 2016 --controlRegion ${sel} --label $label high Mlg --highMlg
    for lep in "${leps[@]}"; do
        cat logs/2016_${sel}-${lep}_lowMlg.log >> tables/vgtables_est_2016.tex
        cat logs/2016_${sel}-${lep}_highMlg.log >> tables/vgtables_est_2016.tex
    done
done

echo " " >> tables/vgtables_est_2016.tex

echo " " >> tables_est_2016.tex
echo "\end{document}" >> tables_est_2016.tex
