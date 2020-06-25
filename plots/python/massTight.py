#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

# plotList
massTight = []
    
massTight.append( Plot(
    name      = 'mL0PhotonTight',
    texX      = 'M(#gamma,l_{0}) (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "mLtight0Gamma/F" ),
    binning   = [ 50, 0, 200 ],
))

massTight.append( Plot(
    name      = 'mLinv0PhotonTight',
    texX      = 'M(#gamma,l_{0}) (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "mLinvtight0Gamma/F" ),
    binning   = [ 50, 0, 200 ],
))

massTight.append( Plot(
    name      = 'mllPhotonTight',
    texX      = 'M(ll#gamma) (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "mllgammatight/F" ),
    binning   = [ 50, 0, 200 ],
))


massTight.append( Plot(
    name      = 'mL0PhotonTight_coarse',
    texX      = 'M(#gamma,l_{0}) (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "mLtight0Gamma/F" ),
    binning   = [ 17, 25, 195 ],
))

massTight.append( Plot(
    name      = 'mLinv0PhotonTight_coarse',
    texX      = 'M(#gamma,l_{0}) (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "mLinvtight0Gamma/F" ),
    binning   = [ 17, 25, 195 ],
))

massTight.append( Plot(
    name      = 'mllPhotonTight_coarse',
    texX      = 'M(ll#gamma) (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "mllgammatight/F" ),
    binning   = [ 17, 25, 195 ],
))


massTight.append( Plot(
    name      = 'mT',
    texX      = 'M_{T} (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "mT/F" ),
    binning   = [ 20, 0, 200 ],
))

massTight.append( Plot(
    name      = 'mTinv',
    texX      = 'M_{T} (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "mTinv/F" ),
    binning   = [ 20, 0, 200 ],
))

massTight.append( Plot(
    name      = 'm3',
    texX      = 'M_{3} (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "m3/F" ),
    binning   = [ 70, 60, 500 ],
))

massTight.append( Plot(
    name      = 'm3gamma',
    texX      = 'M_{3} (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "m3gamma/F" ),
    binning   = [ 100, 0, 500 ],
))

massTight.append( Plot(
    name      = 'm3wBJet',
    texX      = 'M_{3} w/ 1 BJet (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "m3wBJet/F" ),
    binning   = [ 70, 0, 350 ],
))

massTight.append( Plot(
    name      = 'm3_coarse',
    texX      = 'M_{3} (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "m3/F" ),
    binning   = [ 22, 60, 500 ],
))

massTight.append( Plot(
    name      = 'm3inv',
    texX      = 'M_{3} (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "m3inv/F" ),
    binning   = [ 70, 60, 500 ],
))

massTight.append( Plot(
    name      = 'm3gammainv',
    texX      = 'M_{3} (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "m3gammainv/F" ),
    binning   = [ 100, 0, 500 ],
))

massTight.append( Plot(
    name      = 'm3wBJetinv',
    texX      = 'M_{3} w/ 1 BJet (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "m3wBJetinv/F" ),
    binning   = [ 70, 0, 350 ],
))

massTight.append( Plot(
    name      = 'm3inv_coarse',
    texX      = 'M_{3} (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "m3inv/F" ),
    binning   = [ 22, 60, 500 ],
))

massTight.append( Plot(
    name      = 'mT2lg',
    texX      = 'M_{T2}(l,#gamma) (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "mT2lg/F" ),
    binning   = [ 20, 0, 200 ],
))

massTight.append( Plot(
    name      = 'mT2lginv',
    texX      = 'M_{T2}(l,#gamma) (GeV)',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "mT2linvg/F" ),
    binning   = [ 20, 0, 200 ],
))

massTight.append( Plot(
    name      = 'Lp',
    texX      = 'Lp',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "lpTight/F" ),
    binning   = [ 20, -0.5, 1.5 ],
))

massTight.append( Plot(
    name      = 'Lpinv',
    texX      = 'Lp',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "lpInvTight/F" ),
    binning   = [ 20, -0.5, 1.5 ],
))


