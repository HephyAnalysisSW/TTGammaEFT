#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

# plotList
cutsLepton0 = []
    
cutsLepton0.append( Plot(
    name      = 'lepton0_hoe',
    texX      = 'H/E(l_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.Lepton_hoe[0],
    binning   = [ 20, 0, 0.12 ],
))

cutsLepton0.append( Plot(
    name      = 'lepton0_eInvMinusPInv',
    texX      = '1/E - 1/p (l_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.Lepton_eInvMinusPInv[0],
    binning   = [ 50, -0.05, 0.05 ],
))

cutsLepton0.append( Plot(
    name      = 'lepton0_sip3d',
    texX      = 'sip3D(l_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.Lepton_sip3d[0],
    binning   = [ 20, 0, 4.5 ],
))

cutsLepton0.append( Plot(
    name      = 'lepton0_sieie',
    texX      = '#sigma_{i#etai#eta}(l_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.Lepton_sieie[0],
    binning   = [ 20, 0, 0.02 ],
))

cutsLepton0.append( Plot(
    name      = 'lepton0_pfRelIso03_chg',
    texX      = 'charged relIso_{0.3}(l_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.Lepton_pfRelIso03_chg[0],
    binning   = [ 20, 0, 0.12 ],
))

cutsLepton0.append( Plot(
    name      = 'lepton0_pfRelIso03_all_narrow',
    texX      = 'relIso_{0.3}(l_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.Lepton_pfRelIso03_all[0] if event.Lepton_pt[0]>30 else -999,
    binning   = [ 40, 0, 0.12 ],
))


cutsLepton0.append( Plot(
    name      = 'lepton0_pfRelIso03_all_wide',
    texX      = 'relIso_{0.3}(l_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.Lepton_pfRelIso03_all[0] if event.Lepton_pt[0]>30 else -999,
    binning   = [ 40, 0, 1 ],
))

cutsLepton0.append( Plot(
    name      = 'lepton0_pfRelIso03_all',
    texX      = 'relIso_{0.3}(l_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.Lepton_pfRelIso03_all[0] if event.Lepton_pt[0]>30 else -999,
    binning   = [ 40, 0, 0.5 ],
))


cutsLepton0.append( Plot(
    name      = 'lepton0_pfRelIso03_all_narrow_coarse',
    texX      = 'relIso_{0.3}(l_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.Lepton_pfRelIso03_all[0] if event.Lepton_pt[0]>30 else -999,
    binning   = [ 20, 0, 0.12 ],
))


cutsLepton0.append( Plot(
    name      = 'lepton0_pfRelIso03_all_wide_coarse',
    texX      = 'relIso_{0.3}(l_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.Lepton_pfRelIso03_all[0] if event.Lepton_pt[0]>30 else -999,
    binning   = [ 20, 0, 1 ],
))

cutsLepton0.append( Plot(
    name      = 'lepton0_pfRelIso03_all_coarse',
    texX      = 'relIso_{0.3}(l_{0})',
    texY      = 'Number of Events',
    attribute = lambda event, sample: event.Lepton_pfRelIso03_all[0] if event.Lepton_pt[0]>30 else -999,
    binning   = [ 20, 0, 0.5 ],
))

