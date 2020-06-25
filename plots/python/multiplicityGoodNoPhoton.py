#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

# plotList
multiplicityGoodNoPhoton = []
    
multiplicityGoodNoPhoton.append( Plot(
    name      = 'nLeptonGoodInvIso',
    texX      = 'N_{l}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nLeptonTightInvIso/I" ),
    binning   = [ 4, 0, 4 ],
))

multiplicityGoodNoPhoton.append( Plot(
    name      = 'nElectronGoodInvIso',
    texX      = 'N_{e}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nElectronTightInvIso/I" ),
    binning   = [ 4, 0, 4 ],
))

multiplicityGoodNoPhoton.append( Plot(
    name      = 'nMuonGoodInvIso',
    texX      = 'N_{#mu}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nMuonTightInvIso/I" ),
    binning   = [ 4, 0, 4 ],
))

multiplicityGoodNoPhoton.append( Plot(
    name      = 'nLeptonTightInvIso',
    texX      = 'N_{l}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nLeptonTightInvIso/I" ),
    binning   = [ 4, 0, 4 ],
))

multiplicityGoodNoPhoton.append( Plot(
    name      = 'nElectronTightInvIso',
    texX      = 'N_{e}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nElectronTightInvIso/I" ),
    binning   = [ 4, 0, 4 ],
))

multiplicityGoodNoPhoton.append( Plot(
    name      = 'nMuonTightInvIso',
    texX      = 'N_{#mu}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nMuonTightInvIso/I" ),
    binning   = [ 4, 0, 4 ],
))

multiplicityGoodNoPhoton.append( Plot(
    name      = 'nLeptonGood',
    texX      = 'N_{l}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nLeptonGood/I" ),
    binning   = [ 4, 0, 4 ],
))

multiplicityGoodNoPhoton.append( Plot(
    name      = 'nElectronGood',
    texX      = 'N_{e}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nElectronGood/I" ),
    binning   = [ 4, 0, 4 ],
))

multiplicityGoodNoPhoton.append( Plot(
    name      = 'nMuonGood',
    texX      = 'N_{#mu}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nMuonGood/I" ),
    binning   = [ 4, 0, 4 ],
))

multiplicityGoodNoPhoton.append( Plot(
    name      = 'nLeptonTight',
    texX      = 'N_{l}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nLeptonTight/I" ),
    binning   = [ 4, 0, 4 ],
))

multiplicityGoodNoPhoton.append( Plot(
    name      = 'nElectronTight',
    texX      = 'N_{e}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nElectronTight/I" ),
    binning   = [ 4, 0, 4 ],
))

multiplicityGoodNoPhoton.append( Plot(
    name      = 'nMuonTight',
    texX      = 'N_{#mu}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nMuonTight/I" ),
    binning   = [ 4, 0, 4 ],
))

multiplicityGoodNoPhoton.append( Plot(
    name      = 'nJetGood_wide',
    texX      = 'N_{jet}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nJetGood/I" ),
    binning   = [ 15, 0, 15 ],
))

multiplicityGoodNoPhoton.append( Plot(
    name      = 'nJetGood',
    texX      = 'N_{jet}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nJetGood/I" ),
    binning   = [ 6, 0, 6 ],
))

multiplicityGoodNoPhoton.append( Plot(
    name      = 'nJetGood_semi',
    texX      = 'N_{jet}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nJetGood/I" ),
    binning   = [ 6, 4, 10 ],
))

multiplicityGoodNoPhoton.append( Plot(
    name      = 'nBJetGood',
    texX      = 'N_{bJet}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nBTagGood/I" ),
    binning   = [ 4, 0, 4 ],
))


multiplicityGoodNoPhoton.append( Plot(
    name      = 'nJetGoodInvIso_wide',
    texX      = 'N_{jet}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nJetGoodInvLepIso/I" ),
    binning   = [ 15, 0, 15 ],
))

multiplicityGoodNoPhoton.append( Plot(
    name      = 'nJetGoodInvIso',
    texX      = 'N_{jet}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nJetGoodInvLepIso/I" ),
    binning   = [ 6, 0, 6 ],
))

multiplicityGoodNoPhoton.append( Plot(
    name      = 'nJetGoodInvIso_semi',
    texX      = 'N_{jet}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nJetGoodInvLepIso/I" ),
    binning   = [ 6, 4, 10 ],
))

multiplicityGoodNoPhoton.append( Plot(
    name      = 'nBJetGoodInvIso',
    texX      = 'N_{bJet}',
    texY      = 'Number of Events',
    attribute = TreeVariable.fromString( "nBTagGoodInvLepIso/I" ),
    binning   = [ 4, 0, 4 ],
))

