cat header.dat > cutflowtables_weight.dat
echo " " >> cutflowtables_weight.dat

python cutflowtable_weight.py --selection nLepTight1-nLepVeto1-nJet4p-nBTag1p-nPhoton1p --useCorrectedIsoVeto
python cutflowtable_weight.py --selection nLepTight1-e-nLepVeto1-nJet4p-nBTag1p-nPhoton1p --useCorrectedIsoVeto
python cutflowtable_weight.py --selection nLepTight1-mu-nLepVeto1-nJet4p-nBTag1p-nPhoton1p --useCorrectedIsoVeto
#python cutflowtable_weight.py --year 2017 --selection nLepTight1-nLepVeto1-nJet4p-nBTag1p-nPhoton1p 
#python cutflowtable_weight.py --year 2018 --selection nLepTight1-nLepVeto1-nJet4p-nBTag1p-nPhoton1p 

echo "\section{Yields - Cutflow Table Semileptonic Channel}" >> cutflowtables_weight.dat
echo " " >> cutflowtables_weight.dat
cat logs/weightFlow_nLepTight1-nLepVeto1-nJet4p-nBTag1p-nPhoton1p.log >> cutflowtables_weight.dat
cat logs/weightFlow_nLepTight1-e-nLepVeto1-nJet4p-nBTag1p-nPhoton1p.log >> cutflowtables_weight.dat
cat logs/weightFlow_nLepTight1-mu-nLepVeto1-nJet4p-nBTag1p-nPhoton1p.log >> cutflowtables_weight.dat
#cat logs/weightFlow_2017_nLepTight1-nLepVeto1-nJet4p-nBTag1p-nPhoton1p.log >> cutflowtables_weight.dat
#cat logs/weightFlow_2018_nLepTight1-nLepVeto1-nJet4p-nBTag1p-nPhoton1p.log >> cutflowtables_weight.dat

echo " " >> cutflowtables_weight.dat

##python cutflowtable_weight.py --selection dilepOS-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1p 
##python cutflowtable_weight.py --selection dilepOS-ee-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1p 
##python cutflowtable_weight.py --selection dilepOS-mue-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1p 
##python cutflowtable_weight.py --selection dilepOS-mumu-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1p 
#python cutflowtable_weight.py --year 2017 --selection dilepOS-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1p 
#python cutflowtable_weight.py --year 2018 --selection dilepOS-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1p 


##echo "\section{Yields - Cutflow Table Dileptonic Channel}" >> cutflowtables_weight.dat
##echo " " >> cutflowtables_weight.dat
##cat logs/weightFlow_dilepOS-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1p.log >> cutflowtables_weight.dat
##cat logs/weightFlow_dilepOS-ee-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1p.log >> cutflowtables_weight.dat
##cat logs/weightFlow_dilepOS-mue-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1p.log >> cutflowtables_weight.dat
##cat logs/weightFlow_dilepOS-mumu-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1p.log >> cutflowtables_weight.dat
#cat logs/weightFlow_2017_dilepOS-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1p.log >> cutflowtables_weight.dat
#cat logs/weightFlow_2018_dilepOS-nLepVeto2-offZSFll-mll40-nJet2p-nBTag1p-nPhoton1p.log >> cutflowtables_weight.dat

##echo " " >> cutflowtables_weight.dat
echo "\end{document}" >> cutflowtables_weight.dat

