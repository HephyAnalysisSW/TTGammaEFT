#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

# plotList
genLepton0 = []

genLepton0.append( Plot(
    name      = 'genLepton0_pt',
    texX      = 'p_{T}(l_{0}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenLepton_pt[0],
    binning   = [ 20, 0, 300 ],
))

genLepton0.append( Plot(
    name      = 'genLepton0_eta',
    texX      = '#eta(l_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenLepton_eta[0],
    binning   = [ 20, -6, 6 ],
))

genLepton0.append( Plot(
    name      = 'genLepton0_phi',
    texX      = '#phi(l_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenLepton_phi[0],
    binning   = [ 10, -pi, pi ],
))
