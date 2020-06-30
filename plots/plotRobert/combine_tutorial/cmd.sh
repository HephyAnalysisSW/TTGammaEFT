#!/bin/sh
python tutorial.py
 
text2workspace.py datacard.txt -o datacard.root -PHiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO map='.*/Gen_1:r_bin1[1,0,20]' --PO map='.*/Gen_2:r_bin2[1,0,20]' --PO map='.*/Gen_3:r_bin3[1,0,20]' --PO map='.*/Gen_4:r_bin4[1,0,20]' --PO map='.*/Gen_5:r_bin5[1,0,20]' --PO map='.*/Gen_6:r_bin6[1,0,20]' --PO map='.*/Gen_7:r_bin7[1,0,20]' --PO map='.*/Gen_8:r_bin8[1,0,20]' --PO map='.*/Gen_9:r_bin9[1,0,20]' --PO map='.*/Gen_10:r_bin10[1,0,20]'

combine -M MultiDimFit --algo singles -d datacard.root -t 0 

combine -M MultiDimFit --algo grid -d datacard.root -t 0 -P r_bin5 --floatOtherPOIs=1 -n Grid --setParameterRanges r_bin5=0.5,2
