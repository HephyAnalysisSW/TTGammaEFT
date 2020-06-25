#!/usr/bin/env python
''' Define list of plots for plot script
'''
# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

# plotList
cutsPhotonNoIdCuts0_noPhoton_pt = []
    

cutsPhotonNoIdCuts0_noPhoton_pt.append( Plot(
    name      = 'PhotonNoChgIsoNoSieie0_pfIso03_chg_20ptG120_wide',
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.PhotonNoChgIsoNoSieie0_pfRelIso03_chg * event.PhotonNoChgIsoNoSieie0_pt if event.PhotonNoChgIsoNoSieie0_pt >= 20 and event.PhotonNoChgIsoNoSieie0_pt < 120 else -999,
    binning   = [ 45, 2, 20 ],
))

cutsPhotonNoIdCuts0_noPhoton_pt.append( Plot(
    name      = 'PhotonNoChgIsoNoSieie0_pfIso03_chg_120ptG220_wide',
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.PhotonNoChgIsoNoSieie0_pfRelIso03_chg * event.PhotonNoChgIsoNoSieie0_pt if event.PhotonNoChgIsoNoSieie0_pt >= 120 and event.PhotonNoChgIsoNoSieie0_pt < 220 else -999,
    binning   = [ 45, 2, 20 ],
))

cutsPhotonNoIdCuts0_noPhoton_pt.append( Plot(
    name      = 'PhotonNoChgIsoNoSieie0_pfIso03_chg_220ptGinf_wide',
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.PhotonNoChgIsoNoSieie0_pfRelIso03_chg * event.PhotonNoChgIsoNoSieie0_pt if event.PhotonNoChgIsoNoSieie0_pt >= 220 else -999,
    binning   = [ 45, 2, 20 ],
))


cutsPhotonNoIdCuts0_noPhoton_pt.append( Plot(
    name      = 'PhotonNoChgIso0_pfIso03_chg_20ptG120_wide',
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.PhotonNoChgIso0_pfRelIso03_chg * event.PhotonNoChgIso0_pt if event.PhotonNoChgIso0_pt < 120 else -999,
    binning   = [ 45, 2, 20 ],
))

cutsPhotonNoIdCuts0_noPhoton_pt.append( Plot(
    name      = 'PhotonNoChgIso0_pfIso03_chg_120ptG220_wide',
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.PhotonNoChgIso0_pfRelIso03_chg * event.PhotonNoChgIso0_pt if event.PhotonNoChgIso0_pt >= 120 and event.PhotonNoChgIso0_pt < 220 else -999,
    binning   = [ 45, 2, 20 ],
))

cutsPhotonNoIdCuts0_noPhoton_pt.append( Plot(
    name      = 'PhotonNoChgIso0_pfIso03_chg_220ptGinf_wide',
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.PhotonNoChgIso0_pfRelIso03_chg * event.PhotonNoChgIso0_pt if event.PhotonNoChgIso0_pt >= 220 else -999,
    binning   = [ 45, 2, 20 ],
))


cutsPhotonNoIdCuts0_noPhoton_pt.append( Plot(
    name      = 'PhotonNoChgIsoNoSieie0_pfIso03_chg_20ptG120_wide_coarse',
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.PhotonNoChgIsoNoSieie0_pfRelIso03_chg * event.PhotonNoChgIsoNoSieie0_pt if event.PhotonNoChgIsoNoSieie0_pt >= 20 and event.PhotonNoChgIsoNoSieie0_pt < 120 else -999,
    binning   = [ 18, 2, 20 ],
))

cutsPhotonNoIdCuts0_noPhoton_pt.append( Plot(
    name      = 'PhotonNoChgIsoNoSieie0_pfIso03_chg_120ptG220_wide_coarse',
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.PhotonNoChgIsoNoSieie0_pfRelIso03_chg * event.PhotonNoChgIsoNoSieie0_pt if event.PhotonNoChgIsoNoSieie0_pt >= 120 and event.PhotonNoChgIsoNoSieie0_pt < 220 else -999,
    binning   = [ 18, 2, 20 ],
))

cutsPhotonNoIdCuts0_noPhoton_pt.append( Plot(
    name      = 'PhotonNoChgIsoNoSieie0_pfIso03_chg_220ptGinf_wide_coarse',
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.PhotonNoChgIsoNoSieie0_pfRelIso03_chg * event.PhotonNoChgIsoNoSieie0_pt if event.PhotonNoChgIsoNoSieie0_pt >= 220 else -999,
    binning   = [ 18, 2, 20 ],
))


cutsPhotonNoIdCuts0_noPhoton_pt.append( Plot(
    name      = 'PhotonNoChgIso0_pfIso03_chg_20ptG120_wide_coarse',
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.PhotonNoChgIso0_pfRelIso03_chg * event.PhotonNoChgIso0_pt if event.PhotonNoChgIso0_pt < 120 else -999,
    binning   = [ 18, 2, 20 ],
))

cutsPhotonNoIdCuts0_noPhoton_pt.append( Plot(
    name      = 'PhotonNoChgIso0_pfIso03_chg_120ptG220_wide_coarse',
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.PhotonNoChgIso0_pfRelIso03_chg * event.PhotonNoChgIso0_pt if event.PhotonNoChgIso0_pt >= 120 and event.PhotonNoChgIso0_pt < 220 else -999,
    binning   = [ 18, 2, 20 ],
))

cutsPhotonNoIdCuts0_noPhoton_pt.append( Plot(
    name      = 'PhotonNoChgIso0_pfIso03_chg_220ptGinf_wide_coarse',
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.PhotonNoChgIso0_pfRelIso03_chg * event.PhotonNoChgIso0_pt if event.PhotonNoChgIso0_pt >= 220 else -999,
    binning   = [ 18, 2, 20 ],
))
