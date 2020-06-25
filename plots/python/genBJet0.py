#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

# plotList
genBJet0 = []
    
genBJet0.append( Plot(
    name      = 'genBJet0_pt',
    texX      = 'p_{T}(gen b_{0}) (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "GenBj0_pt/F" ),
    binning   = [ 20, 0, 200 ],
))

genBJet0.append( Plot(
    name      = 'genBJet0_eta',
    texX      = '#eta(gen b_{0})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "GenBj0_eta/F" ),
    binning   = [ 20, -6, 6 ],
))

genBJet0.append( Plot(
    name      = 'genBJet0_phi',
    texX      = '#phi(gen b_{0})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "GenBj0_phi/F" ),
    binning   = [ 10, -pi, pi ],
))
