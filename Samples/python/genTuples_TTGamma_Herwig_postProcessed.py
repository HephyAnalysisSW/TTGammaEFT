# Standard Imports
import os, sys
import ROOT

# RootTools Imports
from RootTools.core.Sample import Sample

# Colors
from TTGammaEFT.Samples.color import color

from TTGammaEFT.Tools.user import gridpack_directory

# Data directory
try:
    data_directory_ = sys.modules['__main__'].data_directory
except:
    from TTGammaEFT.Tools.user import dpm_directory as data_directory_
    data_directory_ += "postprocessed/"

try:
    postprocessing_directory_ = sys.modules['__main__'].postprocessing_directory
except:
    from TTGammaEFT.Samples.default_locations import postprocessing_locations
    postprocessing_directory_ = postprocessing_locations.Herwig

# Logging
if __name__=="__main__":
    import Analysis.Tools.logger as logger
    logger = logger.get_logger("INFO", logFile = None )
    import RootTools.core.logger as logger_rt
    logger_rt = logger_rt.get_logger("INFO", logFile = None )
else:
    import logging
    logger = logging.getLogger(__name__)

logger.info( "Loading MC samples from directory %s", os.path.join( data_directory_, postprocessing_directory_ ) )

# Directories
dirs = {}

dirs["ttGamma_1l_P8"]      = [ "ttGamma_SemiLept_restrict_P8" ]
dirs["ttGamma_2l_P8"]      = [ "ttGamma_Dilept_restrict_P8" ]
dirs["ttGamma_P8"]         = dirs["ttGamma_1l_P8"] + dirs["ttGamma_2l_P8"]

dirs["ttGamma_1l_H7"]      = [ "ttGamma_SemiLept_restrict_H7" ]
dirs["ttGamma_2l_H7"]      = [ "ttGamma_Dilept_restrict_H7" ]
dirs["ttGamma_H7"]         = dirs["ttGamma_1l_H7"] + dirs["ttGamma_2l_H7"]

dirs["ttGamma_1l_Hpp"]      = [ "ttGamma_SemiLept_restrict_Hpp" ]
dirs["ttGamma_2l_Hpp"]      = [ "ttGamma_Dilept_restrict_Hpp" ]
dirs["ttGamma_Hpp"]         = dirs["ttGamma_1l_Hpp"] + dirs["ttGamma_2l_Hpp"]

directories = { key : [ os.path.join( data_directory_, postprocessing_directory_, dir) for dir in dirs[key] ] for key in dirs.keys() }

# Samples

TTG_P8                = Sample.fromDirectory( name="TTG_P8", treeName="Events", isData=False, color=color.TTGP8, texName="tt#gamma (Pythia8)", directory=directories["ttGamma_P8"])
TTG_SemiLep_P8                = Sample.fromDirectory( name="TTG_SemiLep_P8", treeName="Events", isData=False, color=color.TTGP8, texName="tt#gamma (Pythia8)", directory=directories["ttGamma_1l_P8"])
TTG_Dilep_P8                = Sample.fromDirectory( name="TTG_Dilep_P8", treeName="Events", isData=False, color=color.TTGP8, texName="tt#gamma (Pythia8)", directory=directories["ttGamma_2l_P8"])

TTG_H7                = Sample.fromDirectory( name="TTG_H7", treeName="Events", isData=False, color=color.TTGH7, texName="tt#gamma (Herwig7)", directory=directories["ttGamma_H7"])
TTG_SemiLep_H7                = Sample.fromDirectory( name="TTG_SemiLep_H7", treeName="Events", isData=False, color=color.TTGH7, texName="tt#gamma (Herwig7)", directory=directories["ttGamma_1l_H7"])
TTG_Dilep_H7                = Sample.fromDirectory( name="TTG_Dilep_H7", treeName="Events", isData=False, color=color.TTGH7, texName="tt#gamma (Herwig7)", directory=directories["ttGamma_2l_H7"])

TTG_Hpp                = Sample.fromDirectory( name="TTG_Hpp", treeName="Events", isData=False, color=color.TTGHpp, texName="tt#gamma (Herwig++)", directory=directories["ttGamma_Hpp"])
TTG_SemiLep_Hpp                = Sample.fromDirectory( name="TTG_SemiLep_Hpp", treeName="Events", isData=False, color=color.TTGHpp, texName="tt#gamma (Herwig++)", directory=directories["ttGamma_1l_Hpp"])
TTG_Dilep_Hpp                = Sample.fromDirectory( name="TTG_Dilep_Hpp", treeName="Events", isData=False, color=color.TTGHpp, texName="tt#gamma (Herwig++)", directory=directories["ttGamma_2l_Hpp"])

all = [
    TTG_P8,
    TTG_SemiLep_P8,
    TTG_Dilep_P8,
    TTG_H7,
    TTG_SemiLep_H7,
    TTG_Dilep_H7,
    TTG_Hpp,
    TTG_SemiLep_Hpp,
    TTG_Dilep_Hpp,
]

