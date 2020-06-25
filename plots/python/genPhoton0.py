#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

# plotList
genPhoton0 = []
    
genPhoton0.append( Plot(
    name      = 'genPhoton0_pt',
    texX      = 'p_{T}(#gamma_{0}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenMGPhoton_pt[0],# if event.GenMGPhoton_status[0] > 1 else -999,
    binning   = [ 20, 0, 120 ],
))

genPhoton0.append( Plot(
    name      = 'genPhoton0_pt_100To200',
    texX      = 'p_{T}(#gamma_{0}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenMGPhoton_pt[0],# if event.GenMGPhoton_status[0] > 1 else -999,
    binning   = [ 20, 80, 220 ],
))

genPhoton0.append( Plot(
    name      = 'genPhoton0_pt_gt200',
    texX      = 'p_{T}(#gamma_{0}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenMGPhoton_pt[0],# if event.GenMGPhoton_status[0] > 1 else -999,
    binning   = [ 20, 180, 420 ],
))

genPhoton0.append( Plot(
    name      = 'genPhoton0_eta',
    texX      = '#eta(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenMGPhoton_eta[0],# if event.GenMGPhoton_status[0] > 1 else -999,
    binning   = [ 40, -4, 4 ],
))

genPhoton0.append( Plot(
    name      = 'genPhoton0_phi',
    texX      = '#phi(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenMGPhoton_phi[0],# if event.GenMGPhoton_status[0] > 1 else -999,
    binning   = [ 10, -pi, pi ],
))


genPhoton0.append( Plot(
    name      = 'genPhoton0_pt_statusGT1',
    texX      = 'p_{T}(#gamma_{0}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenMGPhoton_pt[0] if event.GenMGPhoton_status[0] > 1 else -999,
    binning   = [ 20, 0, 120 ],
))

genPhoton0.append( Plot(
    name      = 'genPhoton0_pt_100To200_statusGT1',
    texX      = 'p_{T}(#gamma_{0}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenMGPhoton_pt[0] if event.GenMGPhoton_status[0] > 1 else -999,
    binning   = [ 20, 80, 220 ],
))

genPhoton0.append( Plot(
    name      = 'genPhoton0_pt_gt200_statusGT1',
    texX      = 'p_{T}(#gamma_{0}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.GenMGPhoton_pt[0] if event.GenMGPhoton_status[0] > 1 else -999,
    binning   = [ 20, 180, 420 ],
))

