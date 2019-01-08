#!/bin/bash

declare -a cards=("TTGamma_SingleLeptFromT_3LineBuggy" "TTGamma_SingleLeptFromT_3LinePatched" "TTGamma_SingleLeptFromT_1Line" )
declare -a params=("ctZ 0.5" "ctZ 1" "cpQM 1" "cpt 1")

runCard="/afs/hephy.at/user/l/llechner/public/CMSSW_9_4_10/src/TTGammaEFT/Generation/data/runCards/TTGamma.dat"
model="dim6top_LO"

#################################################

for card in "${cards[@]}"
do

   echo "run.py --calcXSec --runCard ${runCard} --process ${card} --model ${model} --overwrite > logs/${card}.xsec 2>&1" &
#   nohup krenew -t -K 10 -- bash -c "run.py --calcXSec --run_card ${run_card} --process ${card} --model ${model} --overwrite" > logs/${card}.xsec 2>&1 &

#   for param in "${params[@]}"
#   do

#      nohup krenew -t -K 10 -- bash -c "run.py --calcXSec --run_card ${run_card} --process ${card} --model ${model} --couplings ${param} --overwrite" > logs/${card}_${param// /_}.xsec 2>&1 &

#   done

done


