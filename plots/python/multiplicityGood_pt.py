#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

# plotList
multiplicityGood_pt = []
    
multiplicityGood_pt.append( Plot(
    name      = 'nJetGood_20ptG120',
    texX      = 'N_{jet}',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.nJetGood if event.PhotonGood0_pt >= 20 and event.PhotonGood0_pt < 120 else -999,
    binning   = [ 10, 0, 10 ],
))

multiplicityGood_pt.append( Plot(
    name      = 'nBJetGood_20ptG120',
    texX      = 'N_{bJet}',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.nBTagGood if event.PhotonGood0_pt >= 20 and event.PhotonGood0_pt < 120 else -999,
    binning   = [ 6, 0, 6 ],
))

multiplicityGood_pt.append( Plot(
    name      = 'nJetGood_120ptG220',
    texX      = 'N_{jet}',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.nJetGood if event.PhotonGood0_pt >= 120 and event.PhotonGood0_pt < 220 else -999,
    binning   = [ 10, 0, 10 ],
))

multiplicityGood_pt.append( Plot(
    name      = 'nBJetGood_120ptG220',
    texX      = 'N_{bJet}',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.nBTagGood if event.PhotonGood0_pt >= 120 and event.PhotonGood0_pt < 220 else -999,
    binning   = [ 6, 0, 6 ],
))

multiplicityGood_pt.append( Plot(
    name      = 'nJetGood_220ptGinf',
    texX      = 'N_{jet}',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.nJetGood if event.PhotonGood0_pt >= 220 else -999,
    binning   = [ 10, 0, 10 ],
))

multiplicityGood_pt.append( Plot(
    name      = 'nBJetGood_220ptGinf',
    texX      = 'N_{bJet}',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.nBTagGood if event.PhotonGood0_pt >= 220 else -999,
    binning   = [ 6, 0, 6 ],
))






multiplicityGood_pt.append( Plot(
    name      = 'nJetGoodInvIso_20ptG120',
    texX      = 'N_{jet}',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.nJetGoodInvLepIso if event.PhotonGoodInvLepIso0_pt >= 20 and event.PhotonGoodInvLepIso0_pt < 120 else -999,
    binning   = [ 10, 0, 10 ],
))

multiplicityGood_pt.append( Plot(
    name      = 'nBJetGoodInvIso_20ptG120',
    texX      = 'N_{bJet}',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.nBTagGoodInvLepIso if event.PhotonGoodInvLepIso0_pt >= 20 and event.PhotonGoodInvLepIso0_pt < 120 else -999,
    binning   = [ 6, 0, 6 ],
))

multiplicityGood_pt.append( Plot(
    name      = 'nJetGoodInvIso_120ptG220',
    texX      = 'N_{jet}',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.nJetGoodInvLepIso if event.PhotonGoodInvLepIso0_pt >= 120 and event.PhotonGoodInvLepIso0_pt < 220 else -999,
    binning   = [ 10, 0, 10 ],
))

multiplicityGood_pt.append( Plot(
    name      = 'nBJetGoodInvIso_120ptG220',
    texX      = 'N_{bJet}',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.nBTagGoodInvLepIso if event.PhotonGoodInvLepIso0_pt >= 120 and event.PhotonGoodInvLepIso0_pt < 220 else -999,
    binning   = [ 6, 0, 6 ],
))

multiplicityGood_pt.append( Plot(
    name      = 'nJetGoodInvIso_220ptGinf',
    texX      = 'N_{jet}',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.nJetGoodInvLepIso if event.PhotonGoodInvLepIso0_pt >= 220 else -999,
    binning   = [ 10, 0, 10 ],
))

multiplicityGood_pt.append( Plot(
    name      = 'nBJetGoodInvIso_220ptGinf',
    texX      = 'N_{bJet}',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.nBTagGoodInvLepIso if event.PhotonGoodInvLepIso0_pt >= 220 else -999,
    binning   = [ 6, 0, 6 ],
))

