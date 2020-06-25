#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

# plotList
jetGood0 = []
    
jetGood0.append( Plot(
    name      = 'jetGood0_pt_wide',
    texX      = 'p_{T}(jet_{0}) (GeV)',
    texY      = 'Number of Events / 30 GeV',
    attribute = TreeVariable.fromString( "JetGood0_pt/F" ),
    binning   = [ 20, 0, 600 ],
))

jetGood0.append( Plot(
    name      = 'jetGood0_pt',
    texX      = 'p_{T}(jet_{0}) (GeV)',
    texY      = 'Number of Events / 10 GeV',
    attribute = TreeVariable.fromString( "JetGood0_pt/F" ),
    binning   = [ 20, 0, 200 ],
))

jetGood0.append( Plot(
    name      = 'jetGood0_eta',
    texX      = '#eta(jet_{0})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "JetGood0_eta/F" ),
    binning   = [ 20, -3, 3 ],
))

jetGood0.append( Plot(
    name      = 'jetGood0_phi',
    texX      = '#phi(jet_{0})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "JetGood0_phi/F" ),
    binning   = [ 10, -pi, pi ],
))



jetGood0.append( Plot(
    name      = 'jetGoodinv0_pt_wide',
    texX      = 'p_{T}(jet_{0}) (GeV)',
    texY      = 'Number of Events / 30 GeV',
    attribute = TreeVariable.fromString( "JetGoodInvLepIso0_pt/F" ),
    binning   = [ 20, 0, 600 ],
))

jetGood0.append( Plot(
    name      = 'jetGoodinv0_pt',
    texX      = 'p_{T}(jet_{0}) (GeV)',
    texY      = 'Number of Events / 10 GeV',
    attribute = TreeVariable.fromString( "JetGoodInvLepIso0_pt/F" ),
    binning   = [ 20, 0, 200 ],
))

jetGood0.append( Plot(
    name      = 'jetGoodinv0_eta',
    texX      = '#eta(jet_{0})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "JetGoodInvLepIso0_eta/F" ),
    binning   = [ 20, -3, 3 ],
))

jetGood0.append( Plot(
    name      = 'jetGoodinv0_phi',
    texX      = '#phi(jet_{0})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "JetGoodInvLepIso0_phi/F" ),
    binning   = [ 10, -pi, pi ],
))
