#!/bin/bash

#
# Example of usage:
# submitCondor.py --execFile submit_estimates.sh --queue tomorrow allEstimates.sh
#

export USER=$(whoami)
initial="$(echo $USER | head -c 1)"
export SCRAM_ARCH=slc6_amd64_gcc630

echo "---------------------"
echo "Grid certificate 1"
voms-proxy-info --all
echo "---------------------"
echo "Current dir: `pwd`"
ls -l
echo "---------------------"
export HOME=/afs/cern.ch/user/${initial}/${USER}
echo "Current home dir: ${HOME}"
echo "---------------------"

echo "---------------------"
echo "Changing to script dir: $IWD"
cd $IWD
ls -l
echo "---------------------"

eval `scramv1 runtime -sh`

echo "---------------------"
echo "Using hephy token: /afs/cern.ch/user/${initial}/${USER}/private/kerberos/krb5_token_hephy.at"
export KRB5CCNAME=/afs/cern.ch/user/${initial}/${USER}/private/kerberos/krb5_token_hephy.at
aklog -d hephy.at
echo "---------------------"

echo "Executing:"
echo ${@:2} --runOnLxPlus
echo "---------------------"

${@:2} --runOnLxPlus
