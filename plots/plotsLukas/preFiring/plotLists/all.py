#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

# TTGammaEFT
from TTGammaEFT.Tools.constants       import defaultValue

from TTGammaEFT.plots.photon0      import photon0
from TTGammaEFT.plots.photon1      import photon1
from TTGammaEFT.plots.lepton0      import lepton0
from TTGammaEFT.plots.lepton1      import lepton1
from TTGammaEFT.plots.jet0         import jet0
from TTGammaEFT.plots.jet1         import jet1
from TTGammaEFT.plots.bjet0        import bjet0
from TTGammaEFT.plots.bjet1        import bjet1
from TTGammaEFT.plots.multiplicity import multiplicity
from TTGammaEFT.plots.mass         import mass
from TTGammaEFT.plots.isolation    import isolation
from TTGammaEFT.plots.met          import met
from TTGammaEFT.plots.beam         import beam
#from TTGammaEFT.plots.checks       import checks

from TTGammaEFT.plots.cutsPhoton0  import cutsPhoton0
from TTGammaEFT.plots.cutsLepton0  import cutsLepton0
from TTGammaEFT.plots.cutsLepton1  import cutsLepton1
from TTGammaEFT.plots.cutsJet0     import cutsJet0
from TTGammaEFT.plots.cutsJet1     import cutsJet1

# plotList
plotListData  = []
plotListData += photon0
plotListData += photon1
plotListData += lepton0
plotListData += lepton1
plotListData += jet0
plotListData += jet1
plotListData += bjet0
plotListData += bjet1
plotListData += multiplicity
plotListData += mass
plotListData += isolation
plotListData += met
plotListData += beam

plotListData += cutsPhoton0
plotListData += cutsLepton0
plotListData += cutsLepton1
plotListData += cutsJet0
plotListData += cutsJet1

plotListDataMC  = plotListData
#plotListDataMC += checks
