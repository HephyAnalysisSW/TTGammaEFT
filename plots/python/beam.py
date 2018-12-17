#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

# TTGammaEFT
from TTGammaEFT.Tools.constants       import defaultValue

# plotList
beam = []
    
beam.append(Plot(
    name = 'PV_npvs',
    texX = 'N_{PV} (total)',
    texY = 'Number of Events',
    attribute = TreeVariable.fromString( "PV_npvs/I" ),
    binning=[50,0,50],
))

beam.append(Plot(
    name = 'PV_npvs_good',
    texX = 'N_{PV} (good)',
    texY = 'Number of Events',
    attribute = TreeVariable.fromString( "PV_npvsGood/I" ),
    binning=[50,0,50],
))
