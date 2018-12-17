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
lepton1 = []

lepton1.append( Plot(
    name      = 'l1_pt',
    texX      = 'p_{T}(l_{1}) (GeV)',
    texY      = 'Number of Events / 15 GeV',
    attribute = lambda event, sample: event.Lepton_pt[1] if event.nLepton > 1 else defaultValue,
    binning   = [ 20, 0, 300 ],
))

lepton1.append( Plot(
    name      = 'l1_eta',
    texX      = '#eta(l_{1})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.Lepton_eta[1] if event.nLepton > 1 else defaultValue,
    binning   = [ 30, -4, 4 ],
))

lepton1.append( Plot(
    name      = 'l1_absEta',
    texX      = '|#eta|(l_{1})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: abs(event.Lepton_eta[1]) if event.nLepton > 1 else defaultValue,
    binning   = [ 15, 0, 4 ],
))

lepton1.append( Plot(
    name      = 'l1_phi',
    texX      = '#phi(l_{1})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.Lepton_phi[1] if event.nLepton > 1 else defaultValue,
    binning   = [ 10, -pi, pi ],
))
