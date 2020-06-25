#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi
import copy

# RootTools
from RootTools.core.standard          import *

from TTGammaEFT.plots.beam                     import beam
from TTGammaEFT.plots.bjetGood0                import bjetGood0
from TTGammaEFT.plots.bjetGood1                import bjetGood1
from TTGammaEFT.plots.checksGood               import checksGood
from TTGammaEFT.plots.cutsJetGood0             import cutsJetGood0
from TTGammaEFT.plots.cutsJetGood1             import cutsJetGood1
#from TTGammaEFT.plots.cutsLeptonGood0          import cutsLeptonGood0
#from TTGammaEFT.plots.cutsLeptonGood1          import cutsLeptonGood1
from TTGammaEFT.plots.cutsLeptonTight0         import cutsLeptonTight0
from TTGammaEFT.plots.cutsLeptonTight1         import cutsLeptonTight1
#from TTGammaEFT.plots.cutsPhotonGood0          import cutsPhotonGood0
#from TTGammaEFT.plots.cutsPhotonNoIdCuts0      import cutsPhotonNoIdCuts0
#from TTGammaEFT.plots.cutsPhotonNoIdCuts0_nPV  import cutsPhotonNoIdCuts0_nPV
#from TTGammaEFT.plots.cutsPhotonNoIdCuts0_pt   import cutsPhotonNoIdCuts0_pt
from TTGammaEFT.plots.cutsPhotonNoIdCuts0_noPhoton   import cutsPhotonNoIdCuts0_noPhoton
from TTGammaEFT.plots.cutsPhotonNoIdCuts0_noPhoton_pt   import cutsPhotonNoIdCuts0_noPhoton_pt
from TTGammaEFT.plots.cutsPhotonNoIdCuts0_invChgIso  import cutsPhotonNoIdCuts0_invChgIso
from TTGammaEFT.plots.cutsPhotonNoIdCuts0_nPV_invChgIso  import cutsPhotonNoIdCuts0_nPV_invChgIso
from TTGammaEFT.plots.cutsPhotonNoIdCuts0_pt_invChgIso   import cutsPhotonNoIdCuts0_pt_invChgIso
from TTGammaEFT.plots.cutsPhotonNoIdCuts0_invSieie  import cutsPhotonNoIdCuts0_invSieie
from TTGammaEFT.plots.cutsPhotonNoIdCuts0_nPV_invSieie  import cutsPhotonNoIdCuts0_nPV_invSieie
from TTGammaEFT.plots.cutsPhotonNoIdCuts0_pt_invSieie   import cutsPhotonNoIdCuts0_pt_invSieie
from TTGammaEFT.plots.ht                       import ht
#from TTGammaEFT.plots.isolationGood            import isolationGood
from TTGammaEFT.plots.isolationTight           import isolationTight
from TTGammaEFT.plots.jetGood0                 import jetGood0
from TTGammaEFT.plots.jetGood1                 import jetGood1
#from TTGammaEFT.plots.leptonGood0              import leptonGood0
#from TTGammaEFT.plots.leptonGood1              import leptonGood1
from TTGammaEFT.plots.leptonTight0             import leptonTight0
from TTGammaEFT.plots.leptonTight1             import leptonTight1
#from TTGammaEFT.plots.massGood                 import massGood
#from TTGammaEFT.plots.massGood_pt              import massGood_pt
from TTGammaEFT.plots.massTight_noPhoton       import massTight_noPhoton
#from TTGammaEFT.plots.massTight_pt             import massTight_pt
from TTGammaEFT.plots.met                      import met
from TTGammaEFT.plots.metSig                   import metSig
from TTGammaEFT.plots.mll                      import mll
from TTGammaEFT.plots.mll_pt                   import mll_pt
#from TTGammaEFT.plots.multiplicityGood         import multiplicityGood
from TTGammaEFT.plots.multiplicityGoodNoPhoton import multiplicityGoodNoPhoton
#from TTGammaEFT.plots.photonGood0              import photonGood0

# plotList
plotListData  = []

plotListData += beam
plotListData += bjetGood0
plotListData += bjetGood1
plotListData += cutsJetGood0
plotListData += cutsJetGood1
#plotListData += cutsLeptonGood0
#plotListData += cutsLeptonGood1
plotListData += cutsLeptonTight0
plotListData += cutsLeptonTight1
#plotListData += cutsPhotonGood0
#plotListData += cutsPhotonNoIdCuts0
#plotListData += cutsPhotonNoIdCuts0_nPV
#plotListData += cutsPhotonNoIdCuts0_pt
plotListData += cutsPhotonNoIdCuts0_noPhoton_pt
plotListData += cutsPhotonNoIdCuts0_noPhoton
plotListData += ht
#plotListData += isolationGood
plotListData += isolationTight
plotListData += jetGood0
plotListData += jetGood1
#plotListData += leptonGood0
#plotListData += leptonGood1
plotListData += leptonTight0
plotListData += leptonTight1
#plotListData += massGood
#plotListData += massGood_pt
plotListData += massTight_noPhoton
#plotListData += massTight
#plotListData += massTight_pt
plotListData += met
plotListData += metSig
plotListData += mll
plotListData += mll_pt
#plotListData += multiplicityGood
plotListData += multiplicityGoodNoPhoton
#plotListData += photonGood0
#plotListData += photonGood1

plotListData += cutsPhotonNoIdCuts0_invChgIso
plotListData += cutsPhotonNoIdCuts0_nPV_invChgIso
plotListData += cutsPhotonNoIdCuts0_pt_invChgIso

plotListData += cutsPhotonNoIdCuts0_invSieie
plotListData += cutsPhotonNoIdCuts0_nPV_invSieie
plotListData += cutsPhotonNoIdCuts0_pt_invSieie

plotListDataMC  = copy.copy(plotListData)
