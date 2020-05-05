
selections=(
            "SR3M3","Fake Faktor 3 Jets"
            "SR4pM3","Fake Faktor geq 4 Jets"
)

cat header > tables/fakefactors_2016.tex
echo " " >> tables/fakefactors_2016.tex

echo "\section{DataDriven Fakes 2016}" >> tables/fakefactors_2016.tex
echo " " >> tables/fakefactors_2016.tex

for seltuple in "${selections[@]}"; do 
    IFS=","; set -- ${seltuple};
    sel=$1;
    label=$2;
    echo ${sel}
    python fakeFactorTable.py --year 2016 --controlRegion ${sel} --label $label --cores 20
    cat logs/fakeFactors_2016_${sel}.log >> tables/fakefactors_2016.tex
done

echo " " >> tables/fakefactors_2016.tex

echo " " >> tables/fakefactors_2016.tex
echo "\end{document}" >> tables/fakefactors_2016.tex
