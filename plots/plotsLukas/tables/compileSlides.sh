year=$1
echo ${year}

cat header > tables/yieldTables_${year}.tex
echo " " >> tables/yieldTables_${year}.tex

# SR CR
echo "\section{Signal Regions ${year}}" >> tables/yieldTables_${year}.tex
echo " " >> tables/yieldTables_${year}.tex

#cat logs/${year}_SR3-all.log >> tables/yieldTables_${year}.tex
cat logs/${year}_SR3-e.log >> tables/yieldTables_${year}.tex
cat logs/${year}_SR3-mu.log >> tables/yieldTables_${year}.tex

#cat logs/${year}_SR4p-all.log >> tables/yieldTables_${year}.tex
cat logs/${year}_SR4p-e.log >> tables/yieldTables_${year}.tex
cat logs/${year}_SR4p-mu.log >> tables/yieldTables_${year}.tex

echo " " >> tables/yieldTables_${year}.tex
echo " " >> tables/yieldTables_${year}.tex

# Fake CR
echo "\section{Fake Control Region ${year}}" >> tables/yieldTables_${year}.tex
echo " " >> tables/yieldTables_${year}.tex

#cat logs/${year}_fake_SR3-all.log >> tables/yieldTables_${year}.tex
cat logs/${year}_fake_SR3-e.log >> tables/yieldTables_${year}.tex
cat logs/${year}_fake_SR3-mu.log >> tables/yieldTables_${year}.tex

#cat logs/${year}_fake_SR4p-all.log >> tables/yieldTables_${year}.tex
cat logs/${year}_fake_SR4p-e.log >> tables/yieldTables_${year}.tex
cat logs/${year}_fake_SR4p-mu.log >> tables/yieldTables_${year}.tex

echo " " >> tables/yieldTables_${year}.tex
echo " " >> tables/yieldTables_${year}.tex

# VG CR
echo "\section{W/ZGamma Control Region ${year}}" >> tables/yieldTables_${year}.tex
echo " " >> tables/yieldTables_${year}.tex

#cat logs/${year}_VG3-all_lowMlg.log >> tables/yieldTables_${year}.tex
cat logs/${year}_VG3-e_lowMlg.log >> tables/yieldTables_${year}.tex
cat logs/${year}_VG3-mu_lowMlg.log >> tables/yieldTables_${year}.tex

#cat logs/${year}_VG3-all_highMlg.log >> tables/yieldTables_${year}.tex
cat logs/${year}_VG3-e_highMlg.log >> tables/yieldTables_${year}.tex
cat logs/${year}_VG3-mu_highMlg.log >> tables/yieldTables_${year}.tex

#cat logs/${year}_VG4p-all_lowMlg.log >> tables/yieldTables_${year}.tex
cat logs/${year}_VG4p-e_lowMlg.log >> tables/yieldTables_${year}.tex
cat logs/${year}_VG4p-mu_lowMlg.log >> tables/yieldTables_${year}.tex

#cat logs/${year}_VG4p-all_highMlg.log >> tables/yieldTables_${year}.tex
cat logs/${year}_VG4p-e_highMlg.log >> tables/yieldTables_${year}.tex
cat logs/${year}_VG4p-mu_highMlg.log >> tables/yieldTables_${year}.tex

echo " " >> tables/yieldTables_${year}.tex
echo " " >> tables/yieldTables_${year}.tex


# MisID CR
echo "\section{MisID-e Control Regions ${year}}" >> tables/yieldTables_${year}.tex
echo " " >> tables/yieldTables_${year}.tex

cat logs/${year}_misDY2-e.log >> tables/yieldTables_${year}.tex
cat logs/${year}_misDY3-e.log >> tables/yieldTables_${year}.tex
cat logs/${year}_misDY4p-e.log >> tables/yieldTables_${year}.tex

#cat logs/${year}_misTT2-all.log >> tables/yieldTables_${year}.tex
cat logs/${year}_misTT2-e.log >> tables/yieldTables_${year}.tex
cat logs/${year}_misTT2-mu.log >> tables/yieldTables_${year}.tex

echo " " >> tables/yieldTables_${year}.tex
echo " " >> tables/yieldTables_${year}.tex


# no photon CR
echo "\section{0 Photon Control Regions ${year}}" >> tables/yieldTables_${year}.tex
echo " " >> tables/yieldTables_${year}.tex

cat logs/${year}_DY2.log >> tables/yieldTables_${year}.tex
cat logs/${year}_DY3.log >> tables/yieldTables_${year}.tex
cat logs/${year}_DY4p.log >> tables/yieldTables_${year}.tex
cat logs/${year}_TT3.log >> tables/yieldTables_${year}.tex
cat logs/${year}_TT4p.log >> tables/yieldTables_${year}.tex
cat logs/${year}_WJets3.log >> tables/yieldTables_${year}.tex
cat logs/${year}_WJets4p.log >> tables/yieldTables_${year}.tex

echo " " >> tables/yieldTables_${year}.tex
echo " " >> tables/yieldTables_${year}.tex

echo "\end{document}" >> tables/yieldTables_${year}.tex
