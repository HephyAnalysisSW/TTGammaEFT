#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

# plotList
massTight_noPhoton = []

massTight_noPhoton.append( Plot(
    name      = 'mT',
    texX      = 'M_{T} (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "mT/F" ),
    binning   = [ 20, 0, 200 ],
))

massTight_noPhoton.append( Plot(
    name      = 'mTinv',
    texX      = 'M_{T} (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "mTinv/F" ),
    binning   = [ 20, 0, 200 ],
))

massTight_noPhoton.append( Plot(
    name      = 'm3',
    texX      = 'M_{3} (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "m3/F" ),
    binning   = [ 70, 60, 500 ],
))

massTight_noPhoton.append( Plot(
    name      = 'm3wBJet',
    texX      = 'M_{3} w/ 1 BJet (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "m3wBJet/F" ),
    binning   = [ 70, 60, 500 ],
))

massTight_noPhoton.append( Plot(
    name      = 'm3_coarse',
    texX      = 'M_{3} (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "m3/F" ),
    binning   = [ 22, 60, 500 ],
))

massTight_noPhoton.append( Plot(
    name      = 'm3inv',
    texX      = 'M_{3} (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "m3inv/F" ),
    binning   = [ 70, 60, 500 ],
))

massTight_noPhoton.append( Plot(
    name      = 'm3wBJetinv',
    texX      = 'M_{3} w/ 1 BJet (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "m3wBJetinv/F" ),
    binning   = [ 70, 60, 500 ],
))

massTight_noPhoton.append( Plot(
    name      = 'm3inv_coarse',
    texX      = 'M_{3} (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "m3inv/F" ),
    binning   = [ 22, 60, 500 ],
))

massTight_noPhoton.append( Plot(
    name      = 'Lp',
    texX      = 'Lp',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "lpTight/F" ),
    binning   = [ 20, -0.5, 1.5 ],
))

massTight_noPhoton.append( Plot(
    name      = 'Lpinv',
    texX      = 'Lp',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "lpInvTight/F" ),
    binning   = [ 20, -0.5, 1.5 ],
))


