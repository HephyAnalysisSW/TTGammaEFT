
selections=(
            "SR3","Signal Region 3 Jets"
            "SR4p","Signal Region geq 4 Jets"

            "misDY2","MisID DY CR 2 Jets"
            "misDY3","MisID DY CR 3 Jets"
            "misDY4","MisID DY CR 4 Jets"
            "misDY5","MisID DY CR 5 Jets"
            "misDY4p","MisID DY CR geq 4 Jets"
            "misDY2-addDYSF-addMisIDSF","MisID DY CR 2 Jets + SF"
            "misDY3-addDYSF-addMisIDSF","MisID DY CR 3 Jets + SF"
            "misDY4-addDYSF-addMisIDSF","MisID DY CR 4 Jets + SF"
            "misDY5-addDYSF-addMisIDSF","MisID DY CR 5 Jets + SF"
            "misDY4p-addDYSF-addMisIDSF","MisID DY CR geq 4 Jets + SF"
            "misTT2","MisID TT CR"
            "misTT2-addMisIDSF","MisID TT CR + SF"
)

noPhotonSelections=(
            "WJets3","W+Jets CR 3 Jets"
            "WJets4p","W+Jets CR geq 4 Jets"

            "TT3","TT CR 3 Jets"
            "TT4p","TT CR geq 4 Jets"

            "DY2","DY CR 2 Jets"
            "DY3","DY CR 3 Jets"
            "DY4","DY CR 4 Jets"
            "DY5","DY CR 5 Jets"
            "DY4p","DY CR geq 4 Jets"
)

leps=("all" "e" "mu")

cat header > tables_est_2018.dat
echo " " >> tables_est_2018.dat

echo "\section{Yields - Semileptonic Channel 2018}" >> tables_est_2018.dat
echo " " >> tables_est_2018.dat

for seltuple in "${selections[@]}"; do 
    IFS=","; set -- ${seltuple};
    sel=$1;
    label=$2;
    echo ${sel}
#    python yieldTable.py --year 2018 --controlRegion ${sel} --label $label   --removeNegative
    for lep in "${leps[@]}"; do
#        python yieldTable.py --year 2018 --controlRegion ${sel} --mode ${lep} --label $label  --removeNegative
        cat logs/2018_${sel}-${lep}.log >> tables_est_2018.dat
    done
done


for seltuple in "${noPhotonSelections[@]}"; do 
    IFS=","; set -- ${seltuple};
    sel=$1;
    label=$2;
    echo ${sel}
#    python yieldTable.py --year 2018 --controlRegion ${sel} --label $label  --removeNegative
    cat logs/2018_${sel}.log >> tables_est_2018.dat
done


echo " " >> tables_est_2018.dat

echo " " >> tables_est_2018.dat
echo "\end{document}" >> tables_est_2018.dat
