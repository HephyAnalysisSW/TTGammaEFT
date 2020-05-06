echo "copy from Clip"
scp -r lukas.lechner@cbe.vbc.ac.at:/users/lukas.lechner/public/CMSSW_10_2_18/src/TTGammaEFT/plots/plotsLukas/tables/tables/yieldTables* ./
echo "running Latex"
pdflatex yieldTables_2016.tex -interaction=nonstopmode  #>> /dev/null 2>&1
pdflatex yieldTables_2016.tex -interaction=nonstopmode  #>> /dev/null 2>&1
pdflatex yieldTables_2017.tex -interaction=nonstopmode  #>> /dev/null 2>&1
pdflatex yieldTables_2017.tex -interaction=nonstopmode  #>> /dev/null 2>&1
pdflatex yieldTables_2018.tex -interaction=nonstopmode  #>> /dev/null 2>&1
pdflatex yieldTables_2018.tex -interaction=nonstopmode  #>> /dev/null 2>&1
echo "done"
#scp -r yieldTables_2016.pdf llechner@lxplus.cern.ch:/eos/user/l/llechner/www/TTGammaEFT/tables/tables/
#scp -r yieldTables_2017.pdf llechner@lxplus.cern.ch:/eos/user/l/llechner/www/TTGammaEFT/tables/tables/
#scp -r yieldTables_2018.pdf llechner@lxplus.cern.ch:/eos/user/l/llechner/www/TTGammaEFT/tables/tables/

