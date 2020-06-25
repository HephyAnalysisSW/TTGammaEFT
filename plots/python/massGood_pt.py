#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

# plotList
massGood_pt = []
    
massGood_pt.append( Plot(
    name      = 'mL0PhotonGood_20ptG120',
    texX      = 'M(#gamma,l_{0}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.mL0Gamma if event.PhotonGood0_pt < 120 else -999,
    binning   = [ 50, 0, 200 ],
))

massGood_pt.append( Plot(
    name      = 'mL0PhotonGood_120ptG220',
    texX      = 'M(#gamma,l_{0}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.mL0Gamma if event.PhotonGood0_pt > 120 and event.PhotonGood0_pt < 220 else -999,
    binning   = [ 50, 0, 200 ],
))

massGood_pt.append( Plot(
    name      = 'mL0PhotonGood_220ptGinf',
    texX      = 'M(#gamma,l_{0}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.mL0Gamma if event.PhotonGood0_pt > 220 else -999,
    binning   = [ 50, 0, 200 ],
))

massGood_pt.append( Plot(
    name      = 'mL1PhotonGood_20ptG120',
    texX      = 'M(#gamma,l_{1}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.mL1Gamma if event.PhotonGood0_pt < 120 else -999,
    binning   = [ 50, 0, 200 ],
))

massGood_pt.append( Plot(
    name      = 'mL1PhotonGood_120ptG220',
    texX      = 'M(#gamma,l_{1}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.mL1Gamma if event.PhotonGood0_pt > 120 and event.PhotonGood0_pt < 220 else -999,
    binning   = [ 50, 0, 200 ],
))

massGood_pt.append( Plot(
    name      = 'mL1PhotonGood_220ptGinf',
    texX      = 'M(#gamma,l_{1}) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.mL1Gamma if event.PhotonGood0_pt > 220 else -999,
    binning   = [ 50, 0, 200 ],
))

massGood_pt.append( Plot(
    name      = 'mllPhotonGood_20ptG120',
    texX      = 'M(ll#gamma) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.mllgamma if event.PhotonGood0_pt < 120 else -999,
    binning   = [ 50, 0, 200 ],
))

massGood_pt.append( Plot(
    name      = 'mllPhotonGood_120ptG220',
    texX      = 'M(ll#gamma) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.mllgamma if event.PhotonGood0_pt > 120 and event.PhotonGood0_pt < 220 else -999,
    binning   = [ 50, 0, 200 ],
))

massGood_pt.append( Plot(
    name      = 'mllPhotonGood_220ptGinf',
    texX      = 'M(ll#gamma) (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.mllgamma if event.PhotonGood0_pt > 220 else -999,
    binning   = [ 50, 0, 200 ],
))

massGood_pt.append( Plot(
    name      = 'm3_20ptG120',
    texX      = 'M_{3} (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.m3 if event.PhotonGood0_pt < 120 else -999,
    binning   = [ 50, 0, 250 ],
))

massGood_pt.append( Plot(
    name      = 'm3_120ptG220',
    texX      = 'M_{3} (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.m3 if event.PhotonGood0_pt > 120 and event.PhotonGood0_pt < 220 else -999,
    binning   = [ 50, 0, 250 ],
))

massGood_pt.append( Plot(
    name      = 'm3_220ptGinf',
    texX      = 'M_{3} (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.m3 if event.PhotonGood0_pt > 220 else -999,
    binning   = [ 50, 0, 250 ],
))

massGood_pt.append( Plot(
    name      = 'm3gamma_20ptG120',
    texX      = 'M_{3} (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.m3gamma if event.PhotonGood0_pt < 120 else -999,
    binning   = [ 100, 0, 500 ],
))

massGood_pt.append( Plot(
    name      = 'm3gamma_120ptG220',
    texX      = 'M_{3} (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.m3gamma if event.PhotonGood0_pt > 120 and event.PhotonGood0_pt < 220 else -999,
    binning   = [ 100, 0, 500 ],
))

massGood_pt.append( Plot(
    name      = 'm3gamma_220ptGinf',
    texX      = 'M_{3} (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.m3gamma if event.PhotonGood0_pt > 220 else -999,
    binning   = [ 100, 0, 500 ],
))



massGood_pt.append( Plot(
    name      = 'm3inv_20ptG120',
    texX      = 'M_{3} (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.m3inv if event.PhotonGoodInvLepIso0_pt < 120 else -999,
    binning   = [ 50, 0, 250 ],
))

massGood_pt.append( Plot(
    name      = 'm3inv_120ptG220',
    texX      = 'M_{3} (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.m3inv if event.PhotonGoodInvLepIso0_pt > 120 and event.PhotonGoodInvLepIso0_pt < 220 else -999,
    binning   = [ 50, 0, 250 ],
))

massGood_pt.append( Plot(
    name      = 'm3inv_220ptGinf',
    texX      = 'M_{3} (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.m3inv if event.PhotonGoodInvLepIso0_pt > 220 else -999,
    binning   = [ 50, 0, 250 ],
))

massGood_pt.append( Plot(
    name      = 'm3gammainv_20ptG120',
    texX      = 'M_{3} (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.m3gammainv if event.PhotonGoodInvLepIso0_pt < 120 else -999,
    binning   = [ 100, 0, 500 ],
))

massGood_pt.append( Plot(
    name      = 'm3gammainv_120ptG220',
    texX      = 'M_{3} (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.m3gammainv if event.PhotonGoodInvLepIso0_pt > 120 and event.PhotonGoodInvLepIso0_pt < 220 else -999,
    binning   = [ 100, 0, 500 ],
))

massGood_pt.append( Plot(
    name      = 'm3gammainv_220ptGinf',
    texX      = 'M_{3} (GeV)',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.m3gammainv if event.PhotonGoodInvLepIso0_pt > 220 else -999,
    binning   = [ 100, 0, 500 ],
))

