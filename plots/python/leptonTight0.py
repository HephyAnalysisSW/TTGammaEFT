#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

# plotList
leptonTight0 = []

leptonTight0.append( Plot(
    name      = 'leptonTight0_pt',
    texX      = 'p_{T}(l_{0}) (GeV)',
    texY      = 'Number of Events / 15 GeV',
    attribute = TreeVariable.fromString( "LeptonTight0_pt/F" ),
    binning   = [ 20, 0, 300 ],
))

leptonTight0.append( Plot(
    name      = 'leptonTight0_eta',
    texX      = '#eta(l_{0})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "LeptonTight0_eta/F" ),
    binning   = [ 30, -3, 3 ],
))

leptonTight0.append( Plot(
    name      = 'leptonTight0_phi',
    texX      = '#phi(l_{0})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "LeptonTight0_phi/F" ),
    binning   = [ 10, -pi, pi ],
))


leptonTight0.append( Plot(
    name      = 'leptonTightInvIso0_pt',
    texX      = 'p_{T}(l_{0}) (GeV)',
    texY      = 'Number of Events / 15 GeV',
    attribute = TreeVariable.fromString( "LeptonTightInvIso0_pt/F" ),
    binning   = [ 20, 0, 300 ],
))

leptonTight0.append( Plot(
    name      = 'leptonTightInvIso0_eta',
    texX      = '#eta(l_{0})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "LeptonTightInvIso0_eta/F" ),
    binning   = [ 30, -3, 3 ],
))

leptonTight0.append( Plot(
    name      = 'leptonTightInvIso0_phi',
    texX      = '#phi(l_{0})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "LeptonTightInvIso0_phi/F" ),
    binning   = [ 10, -pi, pi ],
))
