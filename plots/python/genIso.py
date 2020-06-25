#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

#plotList
genIso = []

genIso.append( Plot(
    name      = 'minDRjj',
    texX      = 'min( #DeltaR(jet, jet) )',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.minDRjj,
    binning   = [ 10, 0, 5 ],
))

genIso.append( Plot(
    name      = 'minDRbb',
    texX      = 'min( #DeltaR(b-jet, b-jet) )',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.minDRbb,
    binning   = [ 10, 0, 5 ],
))

genIso.append( Plot(
    name      = 'minDRll',
    texX      = 'min( #DeltaR(lep, lep) )',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.minDRll,
    binning   = [ 10, 0, 5 ],
))

genIso.append( Plot(
    name      = 'minDRaa',
    texX      = 'min( #DeltaR(#gamma, #gamma) )',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.minDRaa,
    binning   = [ 10, 0, 1 ],
))

genIso.append( Plot(
    name      = 'minDRbj',
    texX      = 'min( #DeltaR(b-jet, jet) )',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.minDRbj,
    binning   = [ 10, 0, 5 ],
))

genIso.append( Plot(
    name      = 'minDRaj',
    texX      = 'min( #DeltaR(#gamma, jet) )',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.minDRaj,
    binning   = [ 10, 0, 5 ],
))

genIso.append( Plot(
    name      = 'minDRjl',
    texX      = 'min( #DeltaR(jet, lep) )',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.minDRjl,
    binning   = [ 10, 0, 5 ],
))

genIso.append( Plot(
    name      = 'minDRab',
    texX      = 'min( #DeltaR(#gamma, b-jet) )',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.minDRab,
    binning   = [ 10, 0, 5 ],
))

genIso.append( Plot(
    name      = 'minDRbl',
    texX      = 'min( #DeltaR(b-jet, lep) )',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.minDRbl,
    binning   = [ 10, 0, 5 ],
))

genIso.append( Plot(
    name      = 'minDRal',
    texX      = 'min( #DeltaR(#gamma, lep) )',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.minDRal,
    binning   = [ 10, 0, 5 ],
))



genIso.append( Plot(
    name      = 'minDRjj_close',
    texX      = 'min( #DeltaR(jet, jet) )',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.minDRjj,
    binning   = [ 10, 0, 1 ],
))

genIso.append( Plot(
    name      = 'minDRbb_close',
    texX      = 'min( #DeltaR(b-jet, b-jet) )',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.minDRbb,
    binning   = [ 10, 0, 1 ],
))

genIso.append( Plot(
    name      = 'minDRll_close',
    texX      = 'min( #DeltaR(lep, lep) )',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.minDRll,
    binning   = [ 10, 0, 1 ],
))

genIso.append( Plot(
    name      = 'minDRbj_close',
    texX      = 'min( #DeltaR(b-jet, jet) )',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.minDRbj,
    binning   = [ 10, 0, 1 ],
))

genIso.append( Plot(
    name      = 'minDRjl_close',
    texX      = 'min( #DeltaR(jet, lep) )',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.minDRjl,
    binning   = [ 10, 0, 1 ],
))

genIso.append( Plot(
    name      = 'minDRbl_close',
    texX      = 'min( #DeltaR(b-jet, lep) )',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.minDRbl,
    binning   = [ 10, 0, 1 ],
))

