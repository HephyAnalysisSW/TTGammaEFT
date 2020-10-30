cwd=$PWD
card=${cwd}/${1}
#tmp_dir=$(mktemp -d -t mg-XXXXXXXXXX)

#echo "Running in tmp-directory ${tmp_dir}"
#cd $tmp_dir

#wget --no-check-certificate https://cms-project-generators.web.cern.ch/cms-project-generators/MG5_aMC_v2.6.5.tar.gz
#tar -xf MG5_aMC_v2.6.5.tar.gz
#rm MG5_aMC_v2.6.5.tar.gz

# that command is actually everything we want
./MG5_aMC_v2_6_5/bin/mg5_aMC ${card}

#rm -rf MG5_aMC_v2_6_5 getMadgraph.sh

#if [ ! -d ${cwd}/output/ ]; then
#    mkdir -p ${cwd}/output/
#fi

#mv * ${cwd}/output/
#cd ${cwd}
#rm -rf $tmp_dir


