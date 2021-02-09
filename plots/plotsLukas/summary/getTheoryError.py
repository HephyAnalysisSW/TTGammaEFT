#!/usr/bin/env python

""" 
Extraction of PDF and scale uncertainties in the SRs
"""

# Standard imports
import ROOT
import os
import sys
import math

# RootTools
from RootTools.core.standard           import *

# TTGammaEFT
from TTGammaEFT.Analysis.SetupHelpers    import *
from TTGammaEFT.Analysis.Setup           import Setup
from TTGammaEFT.Analysis.EstimatorList   import EstimatorList
from TTGammaEFT.Analysis.regions         import *
from TTGammaEFT.Analysis.MCBasedEstimate import MCBasedEstimate

# Analysis
from Analysis.Tools.u_float            import u_float

# use this for job splitting
from RootTools.core.helpers            import partition
#

inclEstimate = "TTG_NLO"

# setup and sample
parameters       = allRegions["SR3p"]["parameters"]
channels         = allRegions["SR3p"]["channels"]
photonSelection  = not allRegions["SR3p"]["noPhotonCR"]
allPhotonRegions = allRegions["SR3p"]["inclRegion"] + allRegions["SR3p"]["regions"] if photonSelection else allRegions["SR3p"]["regions"]

setup            = Setup( year="RunII", photonSelection=photonSelection, private=True ) #photonselection always false for qcd es$
setup            = setup.sysClone( parameters=parameters )
estimates        = EstimatorList( setup, processes=["TTG_NLO_gen", inclEstimate] )
estimate         = getattr( estimates, "TTG_NLO_gen" )
estimate.initCache( setup.defaultCacheDir() + "/PDF")

scale_indices       = [0,1,3,5,7,8] #4 central?
pdf_indices         = range(100)
aS_variations = ["abs(LHEPdfWeight[101])", "abs(LHEPdfWeight[102])"]
scale_variations    = [ "abs(LHEScaleWeight[%i])"%i for i in scale_indices ]
PDF_variations      = [ "abs(LHEPdfWeight[%i])"%i for i in pdf_indices ]

PDF_unc     = []
Scale_unc   = []
PS_unc      = []
ISR_unc      = []
FSR_unc      = []

c = "all"
sigma_central            = estimate.cachedEstimate(noRegions[0], c, setup)
print sigma_central
# Scale
scales        = []
for var in scale_variations:
    sigma_reweight     = estimate.cachedEstimate(noRegions[0], c, setup.sysClone(sys={'reweight':[var]}))
    unc = abs(sigma_reweight - sigma_central) / sigma_central if sigma_central > 0 else u_float(0)
    scales.append(unc.val)
scale_rel = max(scales)
print scales

# PDF
deltas = []
delta_squared = 0
for var in PDF_variations:
    sigma_reweight     = estimate.cachedEstimate(noRegions[0], c, setup.sysClone(sys={'reweight':[var]}))
    deltas.append(sigma_reweight.val)
deltas = sorted(deltas)
print deltas

upper = len(deltas)*84/100 - 1
lower = len(deltas)*16/100 - 1
delta_sigma = (deltas[upper]-deltas[lower])/2.

deltas_as = []
for var in aS_variations:
    sigma_reweight  = estimate.cachedEstimate(noRegions[0], c, setup.sysClone(sys={'reweight':[var]}))
    deltas_as.append(sigma_reweight.val)

delta_sigma_rel = delta_sigma / sigma_central.val if sigma_central.val > 0 else 0.
print delta_sigma_rel

delta_sigma_alphaS = ( deltas_as[1] - deltas_as[0] ) * 0.5
delta_sigma_alphaS_rel = delta_sigma_alphaS / sigma_central.val if sigma_central.val > 0 else 0.
# add alpha_s and PDF in quadrature
delta_sigma_rel = math.sqrt( delta_sigma_rel**2 + delta_sigma_alphaS_rel**2 )
print delta_sigma_rel


print "SR3p", "TTG_NLO_gen", c, "PDF+alphaS", delta_sigma_rel
print "SR3p", "TTG_NLO_gen", c, "Scale", scale_rel
print "SR3p", "TTG_NLO_gen", c, "Total Theory", math.sqrt( scale_rel**2 + delta_sigma_rel**2 )

