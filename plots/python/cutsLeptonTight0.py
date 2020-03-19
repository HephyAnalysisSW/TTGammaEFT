#!/usr/bin/env python
""" Define list of plots for plot script
"""

# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

# plotList
cutsLeptonTight0 = []
    
cutsLeptonTight0.append( Plot(
    name      = "leptonTight0_sip3d",
    texX      = "SIP3D(l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTight0_sip3d/F" ),
    binning   = [ 20, 0, 6 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTight0_lostHits",
    texX      = "lost hits (l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTight0_lostHits/I" ),
    binning   = [ 4, 0, 4 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTight0_dr03EcalRecHitSumEt",
    texX      = "dr03EcalRecHitSumEt (l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTight0_dr03EcalRecHitSumEt/F" ),
    binning   = [ 20, 0, 3 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTight0_dr03HcalDepth1TowerSumEt",
    texX      = "dr03HcalDepth1TowerSumEt (l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTight0_dr03HcalDepth1TowerSumEt/F" ),
    binning   = [ 20, 0, 3 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTight0_dr03TkSumPt",
    texX      = "dr03TkSumPt (l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTight0_dr03TkSumPt/F" ),
    binning   = [ 20, 0, 2.5 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTight0_dxy",
    texX      = "dxy (l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTight0_dxy/F" ),
    binning   = [ 20, 0, 0.15 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTight0_dz",
    texX      = "dz (l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTight0_dz/F" ),
    binning   = [ 20, 0, 0.3 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTight0_ip3d",
    texX      = "ip3d (l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTight0_ip3d/F" ),
    binning   = [ 20, 0, 0.1 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTight0_r9",
    texX      = "R9 (l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTight0_r9/F" ),
    binning   = [ 20, 0, 1 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTight0_hoe",
    texX      = "H/E(l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTight0_hoe/F" ),
    binning   = [ 20, 0, 0.12 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTight0_eInvMinusPInv",
    texX      = "1/E - 1/p (l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTight0_eInvMinusPInv/F" ),
    binning   = [ 50, -0.05, 0.05 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTight0_convVeto",
    texX      = "conversion veto (l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTight0_convVeto/I" ),
    binning   = [ 2, 0, 2 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTight0_sieie",
    texX      = "#sigma_{i#etai#eta}(l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTight0_sieie/F" ),
    binning   = [ 20, 0, 0.02 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTight0_pfRelIso03_chg",
    texX      = "charged relIso_{0.3}(l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTight0_pfRelIso03_chg/F" ),
    binning   = [ 20, 0, 0.12 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTight0_pfRelIso03_all",
    texX      = "relIso_{0.3}(l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTight0_pfRelIso03_all/F" ),
    binning   = [ 20, 0, 0.12 ],
))





cutsLeptonTight0.append( Plot(
    name      = "leptonTightinv0_sip3d",
    texX      = "SIP3D(l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTightInvIso0_sip3d/F" ),
    binning   = [ 20, 0, 6 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTightinv0_lostHits",
    texX      = "lost hits (l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTightInvIso0_lostHits/I" ),
    binning   = [ 4, 0, 4 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTightinv0_dr03EcalRecHitSumEt",
    texX      = "dr03EcalRecHitSumEt (l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTightInvIso0_dr03EcalRecHitSumEt/F" ),
    binning   = [ 20, 0, 3 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTightinv0_dr03HcalDepth1TowerSumEt",
    texX      = "dr03HcalDepth1TowerSumEt (l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTightInvIso0_dr03HcalDepth1TowerSumEt/F" ),
    binning   = [ 20, 0, 3 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTightinv0_dr03TkSumPt",
    texX      = "dr03TkSumPt (l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTightInvIso0_dr03TkSumPt/F" ),
    binning   = [ 20, 0, 2.5 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTightinv0_dxy",
    texX      = "dxy (l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTightInvIso0_dxy/F" ),
    binning   = [ 20, 0, 0.15 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTightinv0_dz",
    texX      = "dz (l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTightInvIso0_dz/F" ),
    binning   = [ 20, 0, 0.3 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTightinv0_ip3d",
    texX      = "ip3d (l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTightInvIso0_ip3d/F" ),
    binning   = [ 20, 0, 0.1 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTightinv0_r9",
    texX      = "R9 (l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTightInvIso0_r9/F" ),
    binning   = [ 20, 0, 1 ],
))


cutsLeptonTight0.append( Plot(
    name      = "leptonTightinv0_hoe",
    texX      = "H/E(l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTightInvIso0_hoe/F" ),
    binning   = [ 20, 0, 0.12 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTightinv0_eInvMinusPInv",
    texX      = "1/E - 1/p (l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTightInvIso0_eInvMinusPInv/F" ),
    binning   = [ 50, -0.05, 0.05 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTightinv0_convVeto",
    texX      = "conversion veto (l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTightInvIso0_convVeto/I" ),
    binning   = [ 2, 0, 2 ],
))

cutsLeptonTight0.append( Plot(
    name      = "leptonTightinv0_sieie",
    texX      = "#sigma_{i#etai#eta}(l_{0})",
    texY      = "Number of Events",
    attribute = TreeVariable.fromString( "LeptonTightInvIso0_sieie/F" ),
    binning   = [ 20, 0, 0.02 ],
))

