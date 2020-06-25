from TTGammaEFT.Analysis.Setup                 import Setup
from TTGammaEFT.Analysis.MCBasedEstimate       import MCBasedEstimate
from TTGammaEFT.Analysis.DataDrivenQCDEstimate import DataDrivenQCDEstimate
from TTGammaEFT.Analysis.SetupHelpers          import default_sampleList

setup = Setup()
bkgEstimators = []

for process in default_sampleList:
    if process.count("DD"): bkgEstimators.append( DataDrivenDYEstimate( name=process,                                   cacheDir="analysis" ) )
    else:                   bkgEstimators.append( MCBasedEstimate(      name=process, process=setup.processes[process], cacheDir="analysis" ) )

nList = [e.name for e in bkgEstimators]
assert len(list(set(nList))) == len(nList), "Names of bkgEstimators are not unique: %s"%",".join(nList)
