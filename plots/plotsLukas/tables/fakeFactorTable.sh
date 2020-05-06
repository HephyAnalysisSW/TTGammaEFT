
selections=(
            "SR3M3","Fake Faktor 3 Jets"
            "SR4pM3","Fake Faktor geq 4 Jets"
)

echo 2016
cat header > tables/fakefactors_2016.tex
echo " " >> tables/fakefactors_2016.tex

echo "\section{DataDriven Fakes 2016}" >> tables/fakefactors_2016.tex
echo " " >> tables/fakefactors_2016.tex

for seltuple in "${selections[@]}"; do 
    IFS=","; set -- ${seltuple};
    sel=$1;
    label=$2;
    echo ${sel}
#    python fakeFactorTable.py --year 2016 --controlRegion ${sel} --label $label --cores 20
    cat logs/fakeFactors_2016_${sel}.log >> tables/fakefactors_2016.tex
done

echo " " >> tables/fakefactors_2016.tex

echo " " >> tables/fakefactors_2016.tex
echo "\end{document}" >> tables/fakefactors_2016.tex



echo 2017
cat header > tables/fakefactors_2017.tex
echo " " >> tables/fakefactors_2017.tex

echo "\section{DataDriven Fakes 2017}" >> tables/fakefactors_2017.tex
echo " " >> tables/fakefactors_2017.tex

for seltuple in "${selections[@]}"; do 
    IFS=","; set -- ${seltuple};
    sel=$1;
    label=$2;
    echo ${sel}
#    python fakeFactorTable.py --year 2017 --controlRegion ${sel} --label $label --cores 20
    cat logs/fakeFactors_2017_${sel}.log >> tables/fakefactors_2017.tex
done

echo " " >> tables/fakefactors_2017.tex

echo " " >> tables/fakefactors_2017.tex
echo "\end{document}" >> tables/fakefactors_2017.tex


echo 2018
cat header > tables/fakefactors_2018.tex
echo " " >> tables/fakefactors_2018.tex

echo "\section{DataDriven Fakes 2018}" >> tables/fakefactors_2018.tex
echo " " >> tables/fakefactors_2018.tex

for seltuple in "${selections[@]}"; do 
    IFS=","; set -- ${seltuple};
    sel=$1;
    label=$2;
    echo ${sel}
#    python fakeFactorTable.py --year 2018 --controlRegion ${sel} --label $label --cores 20
    cat logs/fakeFactors_2018_${sel}.log >> tables/fakefactors_2018.tex
done

echo " " >> tables/fakefactors_2018.tex

echo " " >> tables/fakefactors_2018.tex
echo "\end{document}" >> tables/fakefactors_2018.tex
