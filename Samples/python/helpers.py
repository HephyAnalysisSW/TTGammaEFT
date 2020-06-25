''' Helpers Functions
'''
# Imports
from RootTools.core.Sample import Sample

# Helpers Functions
def singleton(class_):
  instances = {}
  def getinstance(*args, **kwargs):
    if class_ not in instances:
        instances[class_] = class_(*args, **kwargs)
    return instances[class_]
  return getinstance

def getDataSample( pd, runName, lumi, dirs, redirector=None, fromDPM=True ):
    if fromDPM: sample = Sample.fromDPMDirectory( name=( pd + '_' + runName ), treeName="Events", redirector=redirector, texName=( pd + ' (' + runName + ')' ), directory=dirs[ pd + '_' + runName ], noCheckProxy=True )
    else:       sample = Sample.fromDirectory( name=( pd + '_' + runName ), treeName="Events", texName=( pd + ' (' + runName + ')' ), directory=dirs[ pd + '_' + runName ] )
    sample.lumi = lumi
    return sample

def getMCSample( name, texName, directory, redirector=None, color=None, noCheckProxy=True, fromDPM=True ):
    if fromDPM: sample = Sample.fromDPMDirectory( name=name, isData=False, color=color, treeName="Events", redirector=redirector, texName=texName, directory=directory, noCheckProxy=noCheckProxy )
    else:       sample = Sample.fromDirectory(    name=name, isData=False, color=color, treeName="Events",                        texName=texName, directory=directory )
    return sample

def merge( pd, totalRunName, listOfRuns, dirs ):
    dirs[ pd + '_' + totalRunName ] = []
    for run in listOfRuns:
        dirs[ pd + '_' + totalRunName ].extend( dirs[ pd + '_' + run ] )

