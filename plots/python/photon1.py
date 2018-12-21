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
photon1 = []
    
photon1.append( Plot(
    name      = 'gamma1_pt',
    texX      = 'p_{T}(#gamma_{1}) (GeV)',
    texY      = 'Number of Events / 5 GeV',
    attribute = lambda event, sample: event.Photon_pt[1] if event.nPhoton > 1 else defaultValue,
    binning   = [ 19, 20, 115 ],
))

photon1.append( Plot(
    name      = 'gamma1_eta_tight',
    texX      = '#eta(#gamma_{1})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.Photon_eta[1] if event.nPhoton > 1 else defaultValue,
    binning   = [ 24, -1.8, 1.8 ],
))

photon1.append( Plot(
    name      = 'gamma1_eta',
    texX      = '#eta(#gamma_{1})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.Photon_eta[1] if event.nPhoton > 1 else defaultValue,
    binning   = [ 24, -4, 4 ],
))

photon1.append( Plot(
    name      = 'gamma1_absEta_tight',
    texX      = '|#eta|(#gamma_{1})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: abs(event.Photon_eta[1]) if event.nPhoton > 1 else defaultValue,
    binning   = [ 9, 0, 1.8 ],
))

photon1.append( Plot(
    name      = 'gamma1_absEta',
    texX      = '|#eta|(#gamma_{1})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: abs(event.Photon_eta[1]) if event.nPhoton > 1 else defaultValue,
    binning   = [ 9, 0, 4 ],
))

photon1.append( Plot(
    name      = 'gamma1_phi',
    texX      = '#phi(#gamma_{1})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.Photon_phi[1] if event.nPhoton > 1 else defaultValue,
    binning   = [ 20, -pi, pi ],
))

