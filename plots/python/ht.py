#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

# plotList
ht = []
    
ht.append( Plot(
    name      = 'ht',
    texX      = 'H_{T} (GeV)',
    texY      = 'Number of Events / 30 GeV',
    attribute = TreeVariable.fromString( "ht/F" ),
    binning   = [ 20, 0, 600 ],
))

ht.append( Plot(
    name      = 'htinv',
    texX      = 'H_{T} (GeV)',
    texY      = 'Number of Events / 30 GeV',
    attribute = TreeVariable.fromString( "htinv/F" ),
    binning   = [ 20, 0, 600 ],
))
