# Standard
import os, sys

# RootTools
from RootTools.core.standard import *

# TTGammaEFT
from TTGammaEFT.Tools.user   import gridpack_directory, cache_directory

def get_parser():
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser for samples file")
    argParser.add_argument( '--overwrite',   action='store_true',    help="Overwrite current entry in db?" )
    return argParser

# Redirector
try:
    redirector = sys.modules['__main__'].redirector
except:
    if "clip" in os.getenv("HOSTNAME").lower():
        redirector = 'root://eos.grid.vbc.ac.at/'
#        redirector = '/eos/vbc/experiments/cms/'
#        from Samples.Tools.config import redirector_clip as redirector
    else:
        from Samples.Tools.config import redirector as redirector

# Logging
if __name__=="__main__":
    import Analysis.Tools.logger as logger
    logger = logger.get_logger("INFO", logFile = None )
    import RootTools.core.logger as logger_rt
    logger_rt = logger_rt.get_logger("INFO", logFile = None )
    options = get_parser().parse_args()
    ov = options.overwrite
else:
    import logging
    logger = logging.getLogger(__name__)
    ov = False

dbFile = cache_directory + "/samples/DB_TTGamma_GEN_Herwig.sql"

logger.info( "Using db file: %s", dbFile )

TTGSingleLep_LO_xSection = 5.056*1.4852
TTGLep_LO_xSection = 1.495*1.4852

ttGamma_SemiLept_restrict_P8                      = FWLiteSample.fromDAS("ttGamma_SemiLept_restrict_P8", "/ttGamma_SingleLept_Pythia8_v2/llechner-ttGamma_SingleLept_Pythia8_v2-91bb5965459168088318c70c13975c93/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
ttGamma_SemiLept_restrict_P8.xSection             = TTGSingleLep_LO_xSection
ttGamma_SemiLept_restrict_P8.nEvents              = 20000 * len(ttGamma_SemiLept_restrict_P8.files)

ttGamma_Dilept_restrict_P8                      = FWLiteSample.fromDAS("ttGamma_Dilept_restrict_P8", "/ttGamma_Dilept_Pythia8_v2/llechner-ttGamma_Dilept_Pythia8_v2-3235ac99d32b02e75cdf84f3991fb456/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
ttGamma_Dilept_restrict_P8.xSection             = TTGLep_LO_xSection
ttGamma_Dilept_restrict_P8.nEvents              = 20000 * len(ttGamma_Dilept_restrict_P8.files)

ttGamma_SemiLept_restrict_H7                      = FWLiteSample.fromDAS("ttGamma_SemiLept_restrict_H7", "/ttGamma_SingleLept_Herwig7_v2/llechner-ttGamma_SingleLept_Herwig7_v2-f7064284577cde94337a77d0bf2715ed/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
ttGamma_SemiLept_restrict_H7.xSection             = TTGSingleLep_LO_xSection
ttGamma_SemiLept_restrict_H7.nEvents              = 20000 * len(ttGamma_SemiLept_restrict_H7.files)

ttGamma_Dilept_restrict_H7                      = FWLiteSample.fromDAS("ttGamma_Dilept_restrict_H7", "/ttGamma_Dilept_Herwig7_v2/llechner-ttGamma_Dilept_Herwig7_v2-184b45e233661508058d4d3e8cc08451/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
ttGamma_Dilept_restrict_H7.xSection             = TTGLep_LO_xSection
ttGamma_Dilept_restrict_H7.nEvents              = 20000 * len(ttGamma_Dilept_restrict_H7.files)

ttGamma_SemiLept_restrict_Hpp                      = FWLiteSample.fromDAS("ttGamma_SemiLept_restrict_Hpp", "/ttGamma_SingleLept_Herwigpp_v2/llechner-ttGamma_SingleLept_Herwigpp_v2-887f9fca5c9e88e115204f35190c74cb/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
ttGamma_SemiLept_restrict_Hpp.xSection             = TTGSingleLep_LO_xSection
ttGamma_SemiLept_restrict_Hpp.nEvents              = 20000 * len(ttGamma_SemiLept_restrict_Hpp.files)

ttGamma_Dilept_restrict_Hpp                      = FWLiteSample.fromDAS("ttGamma_Dilept_restrict_Hpp", "/ttGamma_Dilept_Herwigpp_v2/llechner-ttGamma_Dilept_Herwigpp_v2-46dc77707139d61a2d9b33d87c462057/USER", "phys03", dbFile=dbFile, overwrite=ov, prefix=redirector)
ttGamma_Dilept_restrict_Hpp.xSection             = TTGLep_LO_xSection
ttGamma_Dilept_restrict_Hpp.nEvents              = 20000 * len(ttGamma_Dilept_restrict_Hpp.files)


Herwig = [
    ttGamma_SemiLept_restrict_P8,
    ttGamma_Dilept_restrict_P8,
    ttGamma_SemiLept_restrict_H7,
    ttGamma_Dilept_restrict_H7,
    ttGamma_SemiLept_restrict_Hpp,
    ttGamma_Dilept_restrict_Hpp,
]

allSamples = Herwig


for s in allSamples:
    s.isData = False
