#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

# plotList
genLepton1 = []

genLepton1.append( Plot(
    name      = 'genLepton1_pt',
    texX      = 'p_{T}(l_{1}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenLepton_pt[1],
    binning   = [ 20, 0, 300 ],
))

genLepton1.append( Plot(
    name      = 'genLepton1_eta',
    texX      = '#eta(l_{1})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenLepton_eta[1],
    binning   = [ 20, -6, 6 ],
))

genLepton1.append( Plot(
    name      = 'genLepton1_phi',
    texX      = '#phi(l_{1})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenLepton_phi[1],
    binning   = [ 10, -pi, pi ],
))
