submitCondor.py $1 --dpm --hephyToken --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/mc16gs/   --queue testmatch nanoPostProcessing_Summer16_private_semilepGamma.sh

submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/mc16gs/   --queue testmatch nanoPostProcessing_Summer16_private_semilepGamma.sh
submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/mc17gs/   --queue testmatch nanoPostProcessing_Fall17_private_semilepGamma.sh
submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/mc18gs/   --queue testmatch nanoPostProcessing_Autumn18_private_semilepGamma.sh

submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/data16gs/ --queue testmatch nanoPostProcessing_Run2016_private_semilepGamma.sh
submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/data17gs/ --queue testmatch nanoPostProcessing_Run2017_private_semilepGamma.sh
submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/data18gs/ --queue testmatch nanoPostProcessing_Run2018_private_semilepGamma.sh

submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/mc16s/   --queue testmatch nanoPostProcessing_Summer16_private_semilep.sh
submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/mc17s/   --queue testmatch nanoPostProcessing_Fall17_private_semilep.sh
submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/mc18s/   --queue testmatch nanoPostProcessing_Autumn18_private_semilep.sh

submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/data16s/ --queue testmatch nanoPostProcessing_Run2016_private_semilep.sh
submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/data17s/ --queue testmatch nanoPostProcessing_Run2017_private_semilep.sh
submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/data18s/ --queue testmatch nanoPostProcessing_Run2018_private_semilep.sh

#submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/mc16/   --queue tomorrow nanoPostProcessing_Summer16_private_dilep.sh
#submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/mc17/   --queue tomorrow nanoPostProcessing_Fall17_private_dilep.sh
#submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/mc18/   --queue tomorrow nanoPostProcessing_Autumn18_private_dilep.sh

#submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/data16/ --queue tomorrow nanoPostProcessing_Run2016_private_dilep.sh
#submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/data17/ --queue tomorrow nanoPostProcessing_Run2017_private_dilep.sh
#submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/data18/ --queue tomorrow nanoPostProcessing_Run2018_private_dilep.sh


#submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/mc16g/   --queue tomorrow nanoPostProcessing_Summer16_private_dilepGamma.sh
#submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/mc17g/   --queue tomorrow nanoPostProcessing_Fall17_private_dilepGamma.sh
#submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/mc18g/   --queue tomorrow nanoPostProcessing_Autumn18_private_dilepGamma.sh

#submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/data16g/ --queue tomorrow nanoPostProcessing_Run2016_private_dilepGamma.sh
#submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/data17g/ --queue tomorrow nanoPostProcessing_Run2017_private_dilepGamma.sh
#submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/data18g/ --queue tomorrow nanoPostProcessing_Run2018_private_dilepGamma.sh



#submitCondor.py $1 --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/l/llechner/public/condor_logs/pf17/    --queue nextweek nanoPostProcessing_preFiring2017.sh
