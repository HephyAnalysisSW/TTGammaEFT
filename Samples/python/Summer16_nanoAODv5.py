import copy, os, sys
from RootTools.core.Sample import Sample
import ROOT

def get_parser():
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser for samples file")
    argParser.add_argument('--overwrite',          action='store_true',    help="Overwrite current entry in db?")
    argParser.add_argument('--update',             action='store_true',    help="Update current entry in db?")
    argParser.add_argument('--check_completeness', action='store_true',    help="Check competeness?")
    return argParser

# Logging
if __name__=="__main__":
    import Samples.Tools.logger as logger
    logger = logger.get_logger("INFO", logFile = None )
    import RootTools.core.logger as logger_rt
    logger_rt = logger_rt.get_logger("INFO", logFile = None )
    options = get_parser().parse_args()
    ov = options.overwrite
    if options.update:
        ov = 'update'
else:
    import logging
    logger = logging.getLogger(__name__)
    ov = False

# Redirector
try:
    redirector = sys.modules['__main__'].redirector
except:
    if "clip" in os.getenv("HOSTNAME").lower():
        if __name__ == "__main__" and not options.check_completeness:
            from Samples.Tools.config import redirector_global as redirector
        else:
            from Samples.Tools.config import redirector_clip_local as redirector
    else:
        from Samples.Tools.config import redirector as redirector

from Samples.Tools.config import redirector_clip_local as redirector
# DB
from Samples.Tools.config import dbDir
dbFile = dbDir+'/DB_Summer16_nanoAODv5.sql'

logger.info("Using db file: %s", dbFile)

## ttbar
# Attention!! Only one file is copied to clip, not the full sample yet!
TTSingleLep_pow_CP5_sync                  = Sample.nanoAODfromDAS("TTSingleLep_pow_CP5_sync", "/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",      dbFile=dbFile, redirector=redirector, overwrite=ov, xSection=831.762*(3*0.108)*(1-3*0.108)*2)
TTSingleLep_pow_CP5_sync.files            = [redirector+"/store/mc/RunIISummer16NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/250000/611CC3F1-CB86-2A42-B1FC-73FFBFA8F2DC.root"]
#TTSingleLep_pow_CP5_sync.normalization    = TTSingleLep_pow_CP5_sync.getYieldFromDraw(weightString="genWeight")['val']
#TTGSingleLep_LO_sync                      = Sample.nanoAODfromDAS("TTGSingleLep_LO_sync",     "/TTGamma_SingleLept_TuneCP5_PSweights_13TeV-madgraph-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",  dbFile=dbFile, redirector=redirector, overwrite=ov, xSection=5.125*1.994)
#TTGSingleLep_LO_sync.files                = [redirector+"/store/mc/RunIISummer16NanoAODv5/TTGamma_SingleLept_TuneCP5_PSweights_13TeV-madgraph-pythia8/NANOAODSIM/PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/40000/939379FD-E254-CE4F-8E42-8DA2B1CA7980.root"]
#TTGSingleLep_LO_sync.normalization        = TTGSingleLep_LO_sync.getYieldFromDraw(weightString="genWeight")['val']
DYJetsToLL_M50_LO_ext1_sync               = Sample.nanoAODfromDAS("DYJetsToLL_M50_LO_ext1_sync",  "/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7_ext1-v1/NANOAODSIM",   dbFile=dbFile, redirector=redirector, overwrite=ov, xSection=2075.14*3)
DYJetsToLL_M50_LO_ext1_sync.files         = [redirector+"/store/mc/RunIISummer16NanoAODv5/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7_ext1-v1/60000/CD7B7D86-499C-8D45-8391-DDCC9DD7C8DD.root"]
#DYJetsToLL_M50_LO_ext1_sync.normalization = DYJetsToLL_M50_LO_ext1_sync.getYieldFromDraw(weightString="genWeight")['val']
QCD_Mu_pt170to300_sync                    = Sample.nanoAODfromDAS("QCD_Mu_pt170to300_sync",          "/QCD_Pt-170to300_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",     dbFile=dbFile, redirector=redirector, overwrite=ov, xSection=117989*0.07335)
QCD_Mu_pt170to300_sync.files              = [redirector+"/store/mc/RunIISummer16NanoAODv6/QCD_Pt-170to300_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8/NANOAODSIM/PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/100000/119A84E6-CE47-8B4E-BEA8-80F47D37BA60.root"]
QCD_Ele_pt170to300_sync                   = Sample.nanoAODfromDAS("QCD_Ele_pt170to300_sync",         "/QCD_Pt-170to300_EMEnriched_TuneCUETP8M1_13TeV_pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",     dbFile=dbFile, redirector=redirector, overwrite=ov, xSection=114000*0.165)
QCD_Ele_pt170to300_sync.files             = [redirector+"/store/mc/RunIISummer16NanoAODv6/QCD_Pt-170to300_EMEnriched_TuneCUETP8M1_13TeV_pythia8/NANOAODSIM/PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/70000/21F250EF-6B5A-214B-B63A-F931AB722436.root"]
W3JetsToLNu_sync                          = Sample.nanoAODfromDAS("W3JetsToLNu_sync",          "/W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",         dbFile=dbFile, redirector=redirector, overwrite=ov, xSection=1144.) #948.5 #NLO xsec from AN-2016/289
W3JetsToLNu_sync.files                    = [redirector+"/store/mc/RunIISummer16NanoAODv6/W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/260000/A6377D24-EE0E-CD49-B0F5-8B4D314CCA0A.root"]
TTGSingleLep_LO_sync                      = Sample.nanoAODfromDAS("TTGSingleLep_LO_sync",             "/TTGamma_SingleLept_TuneCP5_PSweights_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",  dbFile=dbFile, redirector=redirector, overwrite=ov, xSection=5.056*1.994)
TTGSingleLep_LO_sync.files                = [redirector+"/store/mc/RunIISummer16NanoAODv6/TTGamma_SingleLept_TuneCP5_PSweights_13TeV-madgraph-pythia8/NANOAODSIM/PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/250000/7ACB80CA-F751-A246-8D31-8118A4884B63.root"]


allSamples = [TTSingleLep_pow_CP5_sync, DYJetsToLL_M50_LO_ext1_sync, QCD_Mu_pt170to300_sync, QCD_Ele_pt170to300_sync, W3JetsToLNu_sync, TTGSingleLep_LO_sync]

for s in allSamples:
    s.isData = False
#    print s.normalization


from Samples.Tools.AutoClass import AutoClass
samples = AutoClass( allSamples )
if __name__=="__main__":
#    for s in allSamples: print s.name, s.normalization
    if options.check_completeness:
        samples.check_completeness( cores=1 )
