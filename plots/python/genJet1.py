#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

# plotList
genJet1 = []
    
genJet1.append( Plot(
    name      = 'genJet1_pt',
    texX      = 'p_{T}(jet_{1}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenJet_pt[1],
    binning   = [ 20, 0, 600 ],
))

genJet1.append( Plot(
    name      = 'genJet1_pt_tight',
    texX      = 'p_{T}(jet_{1}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenJet_pt[1],
    binning   = [ 20, 0, 200 ],
))

genJet1.append( Plot(
    name      = 'genJet1_eta',
    texX      = '#eta(jet_{1})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenJet_eta[1],
    binning   = [ 20, -6, 6 ],
))

genJet1.append( Plot(
    name      = 'genJet1_phi',
    texX      = '#phi(jet_{1})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenJet_phi[1],
    binning   = [ 10, -pi, pi ],
))
