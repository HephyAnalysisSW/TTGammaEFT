#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

# plotList
jetGood1 = []
    
jetGood1.append( Plot(
    name      = 'jetGood1_pt_wide',
    texX      = 'p_{T}(jet_{1}) (GeV)',
    texY      = 'Number of Events / 30 GeV',
    attribute = TreeVariable.fromString( "JetGood1_pt/F" ),
    binning   = [ 20, 0, 600 ],
))

jetGood1.append( Plot(
    name      = 'jetGood1_pt',
    texX      = 'p_{T}(jet_{1}) (GeV)',
    texY      = 'Number of Events / 10 GeV',
    attribute = TreeVariable.fromString( "JetGood1_pt/F" ),
    binning   = [ 20, 0, 200 ],
))

jetGood1.append( Plot(
    name      = 'jetGood1_eta',
    texX      = '#eta(jet_{1})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "JetGood1_eta/F" ),
    binning   = [ 20, -3, 3 ],
))

jetGood1.append( Plot(
    name      = 'jetGood1_phi',
    texX      = '#phi(jet_{1})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "JetGood1_phi/F" ),
    binning   = [ 10, -pi, pi ],
))




jetGood1.append( Plot(
    name      = 'jetGoodinv1_pt_wide',
    texX      = 'p_{T}(jet_{1}) (GeV)',
    texY      = 'Number of Events / 30 GeV',
    attribute = TreeVariable.fromString( "JetGoodInvLepIso1_pt/F" ),
    binning   = [ 20, 0, 600 ],
))

jetGood1.append( Plot(
    name      = 'jetGoodinv1_pt',
    texX      = 'p_{T}(jet_{1}) (GeV)',
    texY      = 'Number of Events / 10 GeV',
    attribute = TreeVariable.fromString( "JetGoodInvLepIso1_pt/F" ),
    binning   = [ 20, 0, 200 ],
))

jetGood1.append( Plot(
    name      = 'jetGoodinv1_eta',
    texX      = '#eta(jet_{1})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "JetGoodInvLepIso1_eta/F" ),
    binning   = [ 20, -3, 3 ],
))

jetGood1.append( Plot(
    name      = 'jetGoodinv1_phi',
    texX      = '#phi(jet_{1})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "JetGoodInvLepIso1_phi/F" ),
    binning   = [ 10, -pi, pi ],
))
