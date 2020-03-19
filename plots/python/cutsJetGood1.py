#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

# plotList
cutsJetGood1 = []
    
cutsJetGood1.append( Plot(
    name      = 'jetGood1_neHEF',
    texX      = 'neHEF(jet_{1})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "JetGood1_neHEF/F" ),
    binning   = [ 30, 0., 1 ],
))

cutsJetGood1.append( Plot(
    name      = 'jetGood1_neEmEF',
    texX      = 'neEmEF(jet_{1})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "JetGood1_neEmEF/F" ),
    binning   = [ 30, 0., 1 ],
))

cutsJetGood1.append( Plot(
    name      = 'jetGood1_chEmHEF',
    texX      = 'chEmEF(jet_{1})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "JetGood1_chEmEF/F" ),
    binning   = [ 30, 0., 1 ],
))

cutsJetGood1.append( Plot(
    name      = 'jetGood1_chHEF',
    texX      = 'chHEF(jet_{1})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "JetGood1_chHEF/F" ),
    binning   = [ 30, 0, 1 ],
))




cutsJetGood1.append( Plot(
    name      = 'jetGoodinv1_neHEF',
    texX      = 'neHEF(jet_{1})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "JetGoodInvLepIso1_neHEF/F" ),
    binning   = [ 30, 0., 1 ],
))

cutsJetGood1.append( Plot(
    name      = 'jetGoodinv1_neEmEF',
    texX      = 'neEmEF(jet_{1})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "JetGoodInvLepIso1_neEmEF/F" ),
    binning   = [ 30, 0., 1 ],
))

cutsJetGood1.append( Plot(
    name      = 'jetGoodinv1_chEmHEF',
    texX      = 'chEmEF(jet_{1})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "JetGoodInvLepIso1_chEmEF/F" ),
    binning   = [ 30, 0., 1 ],
))

cutsJetGood1.append( Plot(
    name      = 'jetGoodinv1_chHEF',
    texX      = 'chHEF(jet_{1})',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "JetGoodInvLepIso1_chHEF/F" ),
    binning   = [ 30, 0, 1 ],
))

