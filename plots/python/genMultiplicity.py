#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

# plotList
genMultiplicity = []
    
genMultiplicity.append( Plot(
    name      = 'nGenPhoton',
    texX      = 'N_{#gamma}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nGenPhoton/I" ),
    binning   = [ 4, 0, 4 ],
))

#genMultiplicity.append( Plot(
#    name      = 'nGenMGPhoton',
#    texX      = 'N_{#gamma}',
#    texY      = 'Number of Events',
#    attribute = TreeVariable.fromString( "nGenMGPhoton/I" ),
#    binning   = [ 4, 0, 4 ],
#))

genMultiplicity.append( Plot(
    name      = 'nGenLepton',
    texX      = 'N_{l}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nGenLepton/I" ),
    binning   = [ 4, 0, 4 ],
))

genMultiplicity.append( Plot(
    name      = 'nGenMuon',
    texX      = 'N_{#mu}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nGenMuon/I" ),
    binning   = [ 4, 0, 4 ],
))

genMultiplicity.append( Plot(
    name      = 'nGenElectron',
    texX      = 'N_{e}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nGenElectron/I" ),
    binning   = [ 4, 0, 4 ],
))

genMultiplicity.append( Plot(
    name      = 'nGenJet',
    texX      = 'N_{jet}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nGenJet/I" ),
    binning   = [ 10, 0, 10 ],
))

genMultiplicity.append( Plot(
    name      = 'nGenBJet',
    texX      = 'N_{bJet}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nGenBJet/I" ),
    binning   = [ 4, 0, 4 ],
))

