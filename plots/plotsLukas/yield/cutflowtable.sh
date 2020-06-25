cat header.dat > cutflowtables.dat
echo " " >> cutflowtables.dat

python cutflowtable.py --selection nLepTight1-nLepVeto1-nJet4p-nBTag1p-nPhoton1 --useCorrectedIsoVeto
python cutflowtable.py --selection nLepTight1-e-nLepVeto1-nJet4p-nBTag1p-nPhoton1 --useCorrectedIsoVeto
python cutflowtable.py --selection nLepTight1-mu-nLepVeto1-nJet4p-nBTag1p-nPhoton1 --useCorrectedIsoVeto
#python cutflowtable.py --year 2017 --selection nLepTight1-nLepVeto1-nJet4p-nBTag1p-nPhoton1 
#python cutflowtable.py --year 2018 --selection nLepTight1-nLepVeto1-nJet4p-nBTag1p-nPhoton1 

echo "\section{Yields - Cutflow Table Semileptonic Channel}" >> cutflowtables.dat
echo " " >> cutflowtables.dat
cat logs/cutFlow_triggerCut-METfilter-nLepTight1-nLepVeto1-nJet4p-nBTag1p-nPhoton1-overlapRemoval.log >> cutflowtables.dat
cat logs/cutFlow_triggerCut-METfilter-nLepTight1-e-nLepVeto1-nJet4p-nBTag1p-nPhoton1-overlapRemoval.log >> cutflowtables.dat
cat logs/cutFlow_triggerCut-METfilter-nLepTight1-mu-nLepVeto1-nJet4p-nBTag1p-nPhoton1-overlapRemoval.log >> cutflowtables.dat
#cat logs/cutFlow_2017_triggerCut-METfilter-nLepTight1-nLepVeto1-nJet4p-nBTag1p-nPhoton1-overlapRemoval.log >> cutflowtables.dat
#cat logs/cutFlow_2018_triggerCut-METfilter-nLepTight1-nLepVeto1-nJet4p-nBTag1p-nPhoton1-overlapRemoval.log >> cutflowtables.dat

echo " " >> cutflowtables.dat

##python cutflowtable.py --selection dilepOS-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1 
##python cutflowtable.py --selection dilepOS-ee-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1 
##python cutflowtable.py --selection dilepOS-mue-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1 
##python cutflowtable.py --selection dilepOS-mumu-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1 
#python cutflowtable.py --year 2017 --selection dilepOS-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1 
#python cutflowtable.py --year 2018 --selection dilepOS-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1 


##echo "\section{Yields - Cutflow Table Dileptonic Channel}" >> cutflowtables.dat
##echo " " >> cutflowtables.dat
##cat logs/cutFlow_triggerCut-METfilter-dilepOS-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1-overlapRemoval.log >> cutflowtables.dat
##cat logs/cutFlow_triggerCut-METfilter-dilepOS-ee-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1-overlapRemoval.log >> cutflowtables.dat
##cat logs/cutFlow_triggerCut-METfilter-dilepOS-mue-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1-overlapRemoval.log >> cutflowtables.dat
##cat logs/cutFlow_triggerCut-METfilter-dilepOS-mumu-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1-overlapRemoval.log >> cutflowtables.dat
#cat logs/cutFlow_2017_triggerCut-METfilter-dilepOS-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1-overlapRemoval.log >> cutflowtables.dat
#cat logs/cutFlow_2018_triggerCut-METfilter-dilepOS-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1-overlapRemoval.log >> cutflowtables.dat

##echo " " >> cutflowtables.dat
echo "\end{document}" >> cutflowtables.dat

