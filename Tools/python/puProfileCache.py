''' Class to construct & cache MC PU profiles (necessary for 2017 MC)
'''

# Standard imports
import ROOT
import os

# RootTools
from RootTools.core.standard import *

# Analysis
from Analysis.Tools.ResultsDB import ResultsDB
from Analysis.Tools.user      import cache_directory

loggerChoices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']

if __name__ == "__main__":
    # Arguments
    import argparse
    argParser = argparse.ArgumentParser( description="Argument parser" )
    argParser.add_argument( '--logLevel',  action='store',      default='INFO',  nargs='?', choices=loggerChoices, help="Log level for logging" )
    argParser.add_argument( '--makePlots', action='store_true',                                                    help="Make PU profile plots?")
    argParser.add_argument( '--overwrite', action='store_true',                                                    help="overwrite Database?")
    argParser.add_argument( '--year',      action='store', type=int, default=2017,                                 help="which year?")
    args      = argParser.parse_args()

    # Logger
    import Analysis.Tools.logger as logger
    import RootTools.core.logger as logger_rt
    logger    = logger.get_logger(    args.logLevel, logFile = None )
    logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

else:
    # Logger
    import logging
    logger = logging.getLogger(__name__)


class puProfile:

    def __init__( self, source_sample, cacheDir=os.path.join(cache_directory,"puProfiles"), year=2017 ):

        if not os.path.isdir( cacheDir ): os.makedirs( cacheDir )

        self.year           = year
        self.source_sample = source_sample
        self.initCache( cacheDir )
        self.binning        = [ 200, 0, 200 ]
        self.draw_string    = "Pileup_nTrueInt"

    def initCache(self, cacheDir):
        self.cache = ResultsDB( os.path.join( cacheDir, 'puProfiles_%i.sql'%self.year ), "puProfile", [ "selection", "weight", "source" ] )

    def uniqueKey( self, *arg ):
        '''No dressing required'''
        return arg

    def cachedTemplate( self, selection, weight = '(1)', save = True, overwrite = False):
        key = {"selection":selection, "weight":weight, "source":self.source_sample.name}
        if (self.cache and self.cache.contains(key)) and not overwrite:
            result = self.cache.get(key)
            logger.info( "Loaded MC PU profile from %s"%(self.cache.database_file) )
            logger.debug( "Key used: %s result: %r"%(key, result) )
        elif self.cache:
            logger.info( "Obtain PU profile for %s"%( key, ) )
            result = self.makeTemplate( selection = selection, weight = weight)
            if result:
                result = self.cache.addData( key, result, overwrite=save )
                logger.info( "Adding PU profile to cache for %s : %r" %( key, result) )
            else:
                logger.warning( "Couldn't create PU profile to cache for %s : %r" %( key, result) )
        else:
            result = self.makeTemplate( selection = selection, weight = weight)
        return result

    def makeTemplate( self, selection, weight='(1)' ):
        logger.info( "Make PU profile for sample %s and selection %s and weight %s", self.source_sample.name, selection, weight )

        h_source = self.source_sample.get1DHistoFromDraw(self.draw_string, self.binning, selectionString = selection, weightString = weight )
        logger.info( "PU histogram contains %s weighted events", h_source.Integral() )
        h_source.Scale( 1./h_source.Integral() )
        return h_source

if __name__ == "__main__":

    # Get all NanoAOD tuples for caching
    if args.year == 2016:
        from Samples.nanoAOD.Summer16_nanoAODv6 import *
#        from TTGammaEFT.Samples.Summer16_nanoAODv5 import *
    elif args.year == 2017:
        from Samples.nanoAOD.Fall17_nanoAODv6 import *
    elif args.year == 2018:
        from Samples.nanoAOD.Autumn18_nanoAODv6 import *

    from Analysis.Tools.user                      import plot_directory
    
    if args.overwrite: os.remove( cache_directory + "/puProfiles/puProfiles_%i.sql"%args.year )
    for sample in allSamples:
        logger.info( "Working on samples %s", sample.name )
        puProfiles = puProfile( source_sample=sample, cacheDir=cache_directory + "/puProfiles/", year=args.year )

        # reweighting selection
        selection = "( 1 )"
        profile = puProfiles.cachedTemplate( selection, weight='genWeight', overwrite=False )

        # plot the MC PU profile
        if args.makePlots:
            profilePlot = Plot.fromHisto( sample.name, texX = "nTrueInt", histos = [[profile]] )
            plotting.draw( profilePlot, plot_directory = os.path.join( plot_directory, 'puProfiles', str(args.year)), logY=True, copyIndexPHP=True, extensions = ["png"] )
