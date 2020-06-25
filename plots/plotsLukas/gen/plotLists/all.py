#!/usr/bin/env python
''' Define list of plots for plot script
'''

# Standard Imports
from math                             import pi

# RootTools
from RootTools.core.standard          import *

from TTGammaEFT.plots.genMet          import genMet
from TTGammaEFT.plots.genPhoton0      import genPhoton0
from TTGammaEFT.plots.genLepton0      import genLepton0
from TTGammaEFT.plots.genLepton1      import genLepton1
from TTGammaEFT.plots.genJet0         import genJet0
from TTGammaEFT.plots.genJet1         import genJet1
from TTGammaEFT.plots.genBJet0        import genBJet0
from TTGammaEFT.plots.genBJet1        import genBJet1
from TTGammaEFT.plots.genTop0         import genTop0
from TTGammaEFT.plots.genTop1         import genTop1
from TTGammaEFT.plots.genMultiplicity import genMultiplicity
from TTGammaEFT.plots.genMass         import genMass
from TTGammaEFT.plots.genIso          import genIso

# plotList
plotListData  = []
plotListData += genMet
#plotListData += genPhoton0
plotListData += genLepton0
plotListData += genLepton1
plotListData += genJet0
plotListData += genJet1
plotListData += genBJet0
plotListData += genBJet1
plotListData += genTop0
plotListData += genTop1
plotListData += genMultiplicity
plotListData += genMass
#plotListData += genIso

plotListDataMC = plotListData

