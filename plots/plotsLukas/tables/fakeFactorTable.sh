year=$1
echo ${year}
cat header > tables/fakefactors_${year}.tex
echo " " >> tables/fakefactors_${year}.tex

echo "\section{DataDriven Fakes ${year}}" >> tables/fakefactors_${year}.tex
echo " " >> tables/fakefactors_${year}.tex

cat logs/fakeFactors_${year}_SR3M3.log >> tables/fakefactors_${year}.tex
cat logs/fakeFactors_${year}_SR4pM3.log >> tables/fakefactors_${year}.tex

echo " " >> tables/fakefactors_${year}.tex
echo " " >> tables/fakefactors_${year}.tex
echo "\end{document}" >> tables/fakefactors_${year}.tex
