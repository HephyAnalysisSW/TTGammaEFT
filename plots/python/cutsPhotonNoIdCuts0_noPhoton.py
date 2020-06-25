#!/usr/bin/env python
''' Define list of plots for plot script
'''
# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

# plotList
cutsPhotonNoIdCuts0_noPhoton = []
    
cutsPhotonNoIdCuts0_noPhoton.append( Plot(
    name      = 'PhotonNoChgIsoNoSieie0_pfIso03_chg_wide',
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.PhotonNoChgIsoNoSieie0_pfRelIso03_chg * event.PhotonNoChgIsoNoSieie0_pt,
    binning   = [ 45, 2, 20 ],
))

cutsPhotonNoIdCuts0_noPhoton.append( Plot(
    name      = 'PhotonNoChgIsoNoSieie0_pfIso03_chg_wide_coarse',
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.PhotonNoChgIsoNoSieie0_pfRelIso03_chg * event.PhotonNoChgIsoNoSieie0_pt,
    binning   = [ 18, 2, 20 ],
))

cutsPhotonNoIdCuts0_noPhoton.append( Plot(
    name      = 'PhotonNoChgIso0_pfIso03_chg_wide',
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.PhotonNoChgIso0_pfRelIso03_chg * event.PhotonNoChgIso0_pt,
    binning   = [ 45, 2, 20 ],
))

cutsPhotonNoIdCuts0_noPhoton.append( Plot(
    name      = 'PhotonNoChgIso0_pfIso03_chg_wide_coarse',
    texX      = 'charged Iso_{0.3}(#gamma_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.PhotonNoChgIso0_pfRelIso03_chg * event.PhotonNoChgIso0_pt,
    binning   = [ 18, 2, 20 ],
))
