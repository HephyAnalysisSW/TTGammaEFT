#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

# plotList
genMass = []
    
genMass.append( Plot(
    name      = 'mll',
    texX      = 'gen M(ll) (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "mll/F" ),
    binning   = [ 50, 0, 200 ],
))

genMass.append( Plot(
    name      = 'mllPhoton',
    texX      = 'gen M(ll#gamma) (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "mllgamma/F" ),
    binning   = [ 50, 0, 200 ],
))
