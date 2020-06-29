#!/usr/bin/env python

# use https://github.com/danbarto/nanoAOD-tools/tree/stopsDilepton in PhysicsTools/NanoAODTools/ for this producer

# standard imports
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import os
import uuid

theano_compile_dir = '/tmp/%s'%str(uuid.uuid4())
if not os.path.exists( theano_compile_dir ):
    os.makedirs( theano_compile_dir )
os.environ['THEANO_FLAGS'] = 'base_compiledir=%s'%theano_compile_dir 

# RootTools
from RootTools.core.standard import *
from Analysis.Tools.helpers  import nonEmptyFile
### nanoAOD postprocessor
from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor   import PostProcessor
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel       import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop       import Module
    
## modules for nanoAOD postprocessor
#from PhysicsTools.NanoAODTools.postprocessing.modules.jme.METSigProducer        import METSigProducer 
from   PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2      import createJMECorrector
import PhysicsTools.NanoAODTools.postprocessing.modules.common.ElectronScaleSmear as ElectronScaleSmear
import PhysicsTools.NanoAODTools.postprocessing.modules.common.PhotonScaleSmear   as PhotonScaleSmear

# Logger
import logging
logger = logging.getLogger(__name__)

def extractEra(sampleName):
    return sampleName[sampleName.find("Run"):sampleName.find("Run")+len('Run2000A')]

class NanoAODTools:

    def __init__( self, sample, year, output_directory, runOnUL=False ):

        if year not in [ 2016, 2017, 2018 ]:
            raise Exception("year %i not known"%year)

        logger.info("Preparing nanoAOD postprocessing")
        logger.info("Will put files into directory %s", output_directory)

        self.runOnUL          = runOnUL
        self.year             = year
        self.output_directory = output_directory
        self.isData           = sample.isData
        self.name             = sample.name
        self.postfix          = "_for_%s"%self.name
        self.files            = [ f for f in sample.files if nonEmptyFile(f) ]
        self.outfiles         = None

        self.era = None
        if self.isData:
            self.era = extractEra(self.name)[-1]

#        logger.info("Using JERs: %s", self.JER)

#        self.unclEnThreshold = 15
#        self.vetoEtaRegion   = (2.65, 3.14) if self.year == 2017 and not self.runOnUL else (10,10)
        self.METCollection   = "METFixEE2017" if self.year == 2017 and not self.runOnUL else "MET"

        # set the params for MET Significance calculation
#        self.metSigParams = metSigParamsMC if not self.isData else metSigParamsData

    def __call__( self, cut ):
        newFileList = []
        logger.info("Starting nanoAOD postprocessing")
        for f in self.files:
            # need a hash to avoid data loss
            file_hash = str(hash(f))

            self.modules = []
    
            JMECorrector = createJMECorrector( isMC=(not self.isData), dataYear=self.year, runPeriod=self.era, jesUncert="Total", jetType = "AK4PFchs", metBranchName=self.METCollection, applySmearing=False )
            self.modules.append( JMECorrector() )
            if not self.isData:
                if self.year == 2016:
                    self.modules.append(ElectronScaleSmear.elecUnc2016MC())
                    self.modules.append(PhotonScaleSmear.phoUnc2016MC())
                elif self.year == 2017:
                    self.modules.append(ElectronScaleSmear.elecUnc2017MC())
                    self.modules.append(PhotonScaleSmear.phoUnc2017MC())
                elif self.year == 2018:
                    self.modules.append(ElectronScaleSmear.elecUnc2018MC())
                    self.modules.append(PhotonScaleSmear.phoUnc2018MC())

            p = PostProcessor( self.output_directory, [f], cut=cut, modules=self.modules, postfix="%s_%s"%(self.postfix, file_hash))
            p.run()
            newFileList += [self.output_directory + '/' + f.split('/')[-1].replace('.root', '%s_%s.root'%(self.postfix, file_hash))]
        logger.info("Done. Replacing input files for further processing.")
        self.outfiles = newFileList

    def getNewSampleFilenames( self ):
        # return sample.files
        return self.outfiles

if __name__ == "__main__":

    year = 2017
    mc   = True

    import os, uuid
    if year == 2016:
        if mc: from Samples.nanoAOD.Summer16_private_legacy_v1 import TTSingleLep_pow               as sample
        else:  from Samples.nanoAOD.Run2016_17Jul2018_private  import DoubleMuon_Run2016C_17Jul2018 as sample
    elif year == 2017:
        if mc: from Samples.nanoAOD.Fall17_private_legacy_v1   import TTSingleLep_pow               as sample
        else:  from Samples.nanoAOD.Run2017_31Mar2018_private  import DoubleMuon_Run2017C_31Mar2018 as sample
    elif year == 2018:
        if mc: from Samples.nanoAOD.Autumn18_private_legacy_v1 import TTSingleLep_pow               as sample
        else:  from Samples.nanoAOD.Run2018_17Sep2018_private  import DoubleMuon_Run2018C_17Sep2018 as sample

    twoJetCond             = "(Sum$(Jet_pt>=29&&abs(Jet_eta)<=2.41)>=2)"
    semilepCond_ele        = "(Sum$(Electron_pt>=34&&abs(Electron_eta)<=2.11&&Electron_cutBased>=4)>=1)"
    semilepCond_mu         = "(Sum$(Muon_pt>=29&&abs(Muon_eta)<=2.41&&Muon_tightId&&Muon_pfRelIso04_all<=0.16)>=1)"
    semilepCond            = "(" + "||".join( [semilepCond_ele, semilepCond_mu] ) + ")"
    gammaCond              = "(Sum$(Photon_pt>=19&&abs(Photon_eta)<=1.5&&Photon_electronVeto&&Photon_pixelSeed==0)>=1)"

    skimConds              = [semilepCond, gammaCond, twoJetCond]
    output_directory       = os.path.join( '/tmp/%s'%os.environ['USER'], str(uuid.uuid4()) )
    sample.reduceFiles( factor = 200 )

    nanoAODTools = NanoAODTools( sample, year, output_directory )
    nanoAODTools( "&&".join(skimConds) )
    newfiles = nanoAODTools.getNewSampleFilenames()
