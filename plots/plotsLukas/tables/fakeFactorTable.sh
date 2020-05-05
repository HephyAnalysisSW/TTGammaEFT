
selections=(
            "SR3M3","Fake Faktor 3 Jets"
            "SR4pM3","Fake Faktor geq 4 Jets"
)

cat header > fakefactors_2016.dat
echo " " >> fakefactors_2016.dat

echo "\section{DataDriven Fakes 2016}" >> fakefactors_2016.dat
echo " " >> fakefactors_2016.dat

for seltuple in "${selections[@]}"; do 
    IFS=","; set -- ${seltuple};
    sel=$1;
    label=$2;
    echo ${sel}
    python fakeFactorTable.py --year 2016 --controlRegion ${sel} --label $label --cores 20
    cat logs/fakeFactors_2016_${sel}.log >> fakefactors_2016.dat
done

echo " " >> fakefactors_2016.dat

echo " " >> fakefactors_2016.dat
echo "\end{document}" >> fakefactors_2016.dat
