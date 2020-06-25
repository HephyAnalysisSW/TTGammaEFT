#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi
import copy

# RootTools
from RootTools.core.standard          import *

from TTGammaEFT.plots.photonGood0              import photonGood0
#from TTGammaEFT.plots.cutsPhotonMVA0           import cutsPhotonMVA0
#from TTGammaEFT.plots.PhotonMVA0               import PhotonMVA0

from TTGammaEFT.plots.cutsPhotonGood0          import cutsPhotonGood0
from TTGammaEFT.plots.cutsPhotonNoIdCuts0      import cutsPhotonNoIdCuts0
from TTGammaEFT.plots.cutsPhotonNoIdCuts0_nPV  import cutsPhotonNoIdCuts0_nPV
from TTGammaEFT.plots.cutsPhotonNoIdCuts0_pt   import cutsPhotonNoIdCuts0_pt
from TTGammaEFT.plots.cutsPhotonNoIdCuts0_invChgIso  import cutsPhotonNoIdCuts0_invChgIso
from TTGammaEFT.plots.cutsPhotonNoIdCuts0_nPV_invChgIso  import cutsPhotonNoIdCuts0_nPV_invChgIso
from TTGammaEFT.plots.cutsPhotonNoIdCuts0_pt_invChgIso   import cutsPhotonNoIdCuts0_pt_invChgIso
from TTGammaEFT.plots.cutsPhotonNoIdCuts0_invSieie  import cutsPhotonNoIdCuts0_invSieie
from TTGammaEFT.plots.cutsPhotonNoIdCuts0_nPV_invSieie  import cutsPhotonNoIdCuts0_nPV_invSieie
from TTGammaEFT.plots.cutsPhotonNoIdCuts0_pt_invSieie   import cutsPhotonNoIdCuts0_pt_invSieie

# plotList
plotListData  = []

plotListData += photonGood0
#plotListData += cutsPhotonMVA0
#plotListData += PhotonMVA0

plotListData += cutsPhotonGood0
plotListData += cutsPhotonNoIdCuts0
plotListData += cutsPhotonNoIdCuts0_nPV
plotListData += cutsPhotonNoIdCuts0_pt
plotListData += cutsPhotonNoIdCuts0_invSieie
plotListData += cutsPhotonNoIdCuts0_nPV_invSieie
plotListData += cutsPhotonNoIdCuts0_pt_invSieie
plotListData += cutsPhotonNoIdCuts0_invChgIso
plotListData += cutsPhotonNoIdCuts0_nPV_invChgIso
plotListData += cutsPhotonNoIdCuts0_pt_invChgIso

plotListDataMC  = copy.copy(plotListData)

