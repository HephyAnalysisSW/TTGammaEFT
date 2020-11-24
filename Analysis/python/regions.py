from math import pi
import numpy as np

from TTGammaEFT.Analysis.Region      import Region
from TTGammaEFT.Analysis.Region      import texString
from TTGammaEFT.Tools.cutInterpreter import mLgThresh

def getRegionsFromThresholds(var, vals, gtLastThreshold = True):
    return [Region(var, (vals[i], vals[i+1])) for i in range(len(vals)-1)]

def getRegions2D(varOne, varOneThresholds, varTwo, varTwoThresholds):
    regions_varOne  = getRegionsFromThresholds(varOne,  varOneThresholds)
    regions_varTwo  = getRegionsFromThresholds(varTwo, varTwoThresholds)

    regions2D = []
    for r1 in regions_varOne:
        for r2 in regions_varTwo:
            regions2D.append(r1+r2)

    return regions2D

#Put all sets of regions that are used in the analysis, closure, tables, etc.

#inclusive
thresholds = [ 20, -999 ]
genTTGammaRegionsIncl  = getRegionsFromThresholds( "GenPhoton_pt[0]", thresholds )
recoTTGammaRegionsIncl = getRegionsFromThresholds( "PhotonGood0_pt", thresholds )

#differencial EFT
thresholds = [ 20, 120, 220, 320, 420, -999 ]
genTTGammaRegionsEFT  = getRegionsFromThresholds( "GenPhoton_pt[0]", thresholds )
recoTTGammaRegionsEFT = getRegionsFromThresholds( "PhotonGood0_pt", thresholds )

#differencial
gammaPT_thresholds = [ 20, 120, 220, -999 ]
genTTGammaRegions  = getRegionsFromThresholds( "GenPhoton_pt[0]", gammaPT_thresholds )
recoTTGammaRegions = getRegionsFromThresholds( "PhotonGood0_pt", gammaPT_thresholds )

thresholdsSmall = [ 20, 120 ]
genTTGammaRegionsSmall  = getRegionsFromThresholds( "GenPhoton_pt[0]", thresholdsSmall )
recoTTGammaRegionsSmall = getRegionsFromThresholds( "PhotonGood0_pt", thresholdsSmall )

#prefiring plots sum(jets)
preFiringSumJetEta    = getRegionsFromThresholds( "Jet_eta", [-5., -4.5, -4., -3.5, -3., -2.5, -2., -1.5, -1., -0.5, 0., 0.5, 1., 1.5, 2., 2.5, 3., 3.5, 4., 4.5, 5.], gtLastThreshold=False )
preFiringSumJetPt     = getRegionsFromThresholds( "Jet_pt",  [30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, -999] )
preFiringSumJetPtLog  = getRegionsFromThresholds( "Jet_pt",  [30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, -999] )
preFiringSumJet       = getRegionsFromThresholds( "Jet_phi", [-pi, -pi*(4./5), -pi*(3./5), -pi*(2./5), -pi*(1./5), 0., pi*(1./5), pi*(2./5), pi*(3./5), pi*(4./5), pi], gtLastThreshold=False )

#pTG_thresh         = [ 20, 70, 120, 170, 220, 270, 320, -999 ]
pTG_thresh = [ 20, 35, 50, 65, 80, 120, 160, -999 ]
#pTG_thresh         = [ 20, 120, 220, -999 ]
etaG_thresh        = [ -1.5, -0.5, 0.5, 1.5 ]
regionsTTG         = getRegionsFromThresholds( "PhotonGood0_pt", pTG_thresh )
regionsTTGEta      = getRegionsFromThresholds( "PhotonGood0_eta", etaG_thresh )
inclRegionsTTG     = [Region( "PhotonGood0_pt", (20,-999) )]

#200, 260, 320,
regionsTTGloose         = getRegionsFromThresholds( "PhotonNoChgIsoNoSieie0_pt", [20, 35, 50, 65, 80, 120, 160, 200, 260, 320, -999] )
regionsTTGlooseEta      = getRegionsFromThresholds( "PhotonNoChgIsoNoSieie0_eta", etaG_thresh )
inclRegionsTTGloose     = [Region( "PhotonNoChgIsoNoSieie0_pt", (20,-999) )]

regionsTTGfake     = getRegionsFromThresholds( "PhotonNoChgIsoNoSieie0_pt", pTG_thresh )
inclRegionsTTGfake = [Region( "PhotonNoChgIsoNoSieie0_pt", (20,-999) )]

regionsTTGlshc     = getRegionsFromThresholds( "PhotonInvChgIso0_pt", pTG_thresh )
inclRegionsTTGlshc = [Region( "PhotonInvChgIso0_pt", (20,-999) )]

regionsTTGhslc     = getRegionsFromThresholds( "PhotonInvSieie0_pt", pTG_thresh )
inclRegionsTTGhslc = [Region( "PhotonInvSieie0_pt", (20,-999) )]

regionsTTGhshc     = getRegionsFromThresholds( "PhotonInvChgIsoInvSieie0_pt", pTG_thresh )
inclRegionsTTGhshc = [Region( "PhotonInvChgIsoInvSieie0_pt", (20,-999) )]

noPhotonRegionTTG  = [Region( "nPhotonGood", (0,1) )]

regionsTTG20To120  = getRegionsFromThresholds( "PhotonGood0_pt", ( 20,   120 ) )
regionsTTG120To220 = getRegionsFromThresholds( "PhotonGood0_pt", ( 120,  220 ) )
regionsTTG220      = getRegionsFromThresholds( "PhotonGood0_pt", ( 220, -999 ) )

pTG_thresh_fine = [ 20, 35, 50, 65, 80, 120, 160, 200, 260, 320, -999 ]
etaG_thresh_fine   = [ -1.4442, -0.9, -0.3, 0.3, 0.9, 1.4442 ]
regionsTTGFine     = getRegionsFromThresholds( "PhotonGood0_pt", pTG_thresh_fine )
regionsTTGEtaFine  = getRegionsFromThresholds( "PhotonGood0_eta", etaG_thresh_fine )
regionsTTGlooseFine     = getRegionsFromThresholds( "PhotonNoChgIsoNoSieie0_pt", pTG_thresh_fine )
regionsTTGlooseEtaFine  = getRegionsFromThresholds( "PhotonNoChgIsoNoSieie0_eta", etaG_thresh_fine )

pTG_thresh = [ 20, 65, 160 ]
highpTG_thresh = [ 160, -999 ]
mlg_tresh = [ mLgThresh, -999 ]
highmLgPtRegions = getRegions2D( "PhotonGood0_pt", pTG_thresh, "mLtight0Gamma", mlg_tresh ) + getRegionsFromThresholds( "PhotonGood0_pt", highpTG_thresh )
highmLgRegions   = getRegionsFromThresholds( "mLtight0Gamma", mlg_tresh )

mlg_tresh = [ 0, mLgThresh ]
lowmLgPtRegions = getRegions2D( "PhotonGood0_pt", pTG_thresh, "mLtight0Gamma", mlg_tresh ) + getRegionsFromThresholds( "PhotonGood0_pt", highpTG_thresh )
lowmLgRegions   = getRegionsFromThresholds( "mLtight0Gamma", mlg_tresh )

mlg_tresh = [ 0, mLgThresh, -999 ]
mLgPtRegions = getRegions2D( "PhotonGood0_pt", pTG_thresh, "mLtight0Gamma", mlg_tresh ) + getRegionsFromThresholds( "PhotonGood0_pt", highpTG_thresh )
mLgRegions   = getRegionsFromThresholds( "mLtight0Gamma", mlg_tresh )

pTG_thresh = [ 20, 35, 50, 65, 80 ]
highpTG_thresh = [ 80, 120, 160, 200, 260, 320, -999 ]
#m3_thresh    = [0, 140, 210, 280, 350, -999]
#m3_thresh    = [0, 250, 350, -999]
m3_thresh    = [0, 280, 420, -999]
m3Regions    = getRegionsFromThresholds( "m3", m3_thresh )
m3PtRegions  = getRegions2D( "PhotonGood0_pt",  pTG_thresh,  "m3", m3_thresh ) + getRegionsFromThresholds( "PhotonGood0_pt", highpTG_thresh )
m3EtaRegions = getRegions2D( "PhotonGood0_eta", etaG_thresh, "m3", m3_thresh )
m3PtlooseRegions  = getRegions2D( "PhotonNoChgIsoNoSieie0_pt",  pTG_thresh,  "m3", m3_thresh ) + getRegionsFromThresholds( "PhotonNoChgIsoNoSieie0_pt", highpTG_thresh )
m3EtalooseRegions = getRegions2D( "PhotonNoChgIsoNoSieie0_eta", etaG_thresh, "m3", m3_thresh )

chgIso_thresh = [0, 1.141, 4, 9, 16, -999]
chgIsoRegions   = getRegionsFromThresholds( "(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)", chgIso_thresh )
chgIsoPtRegions = getRegions2D( "PhotonNoChgIsoNoSieie0_pt", pTG_thresh, "(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)", chgIso_thresh )

chgIso_thresh = chgIso_thresh[1:]
chgIsoNoSRRegions   = getRegionsFromThresholds( "(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)", chgIso_thresh )
chgIsoNoSRPtRegions = getRegions2D( "PhotonNoChgIsoNoSieie0_pt", pTG_thresh, "(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)", chgIso_thresh )

finepTG_thresh         = [ 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 150, 180, 210, -999 ]
photonBinRegions   = getRegionsFromThresholds( "PhotonGood0_pt", finepTG_thresh )

#unfoldpTG_thresh = [ 20, 35, 50, 65, 80, 100, 120, 140, 160, 180, 200, 230, 260, 290, 320, -999 ]
unfoldpTG_thresh = [ 20, 35, 50, 65, 80, 120, 160, 200, 260, 320, -999 ]
regionsTTGUnfolding = getRegionsFromThresholds( "PhotonGood0_pt", unfoldpTG_thresh )
regionsTTGlooseUnfolding = getRegionsFromThresholds( "PhotonNoChgIsoNoSieie0_pt", unfoldpTG_thresh )

etaG_thresh            = [-1.4442] + list(np.linspace(start=-1.35, stop=1.35, num=13)) + [1.4442]
regionsTTGEtaUnfolding = getRegionsFromThresholds( "PhotonGood0_eta", etaG_thresh )
regionsTTGlooseEtaUnfolding = getRegionsFromThresholds( "PhotonNoChgIsoNoSieie0_eta", etaG_thresh )

absetaG_thresh            = list(np.linspace(start=0, stop=1.35, num=10)) + [1.4442]
regionsTTGAbsEtaUnfolding = getRegionsFromThresholds( "abs(PhotonGood0_eta)", absetaG_thresh )
regionsTTGlooseAbsEtaUnfolding = getRegionsFromThresholds( "abs(PhotonNoChgIsoNoSieie0_eta)", absetaG_thresh )

dRG_thresh            = [ 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, -999 ]
#dRG_thresh            = [ 0.4, 0.7, 1.0, 1.3, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 4.2, -999 ]
regionsTTGdRUnfolding = getRegionsFromThresholds( "ltight0GammadR", dRG_thresh )
regionsTTGloosedRUnfolding = getRegionsFromThresholds( "ltight0GammaNoSieieNoChgIsodR", dRG_thresh )

dPhiG_thresh            = list(np.linspace(start=0, stop=3.2, num=17))
regionsTTGdPhiUnfolding = getRegionsFromThresholds( "ltight0GammadPhi", dPhiG_thresh )
regionsTTGloosedPhiUnfolding = getRegionsFromThresholds( "ltight0GammaNoSieieNoChgIsodPhi", dPhiG_thresh )

regionsTTGdRJetUnfolding = getRegionsFromThresholds( "photonJetdR", dRG_thresh )
regionsTTGloosedRJetUnfolding = getRegionsFromThresholds( "photonNoSieieNoChgIsoJetdR", dRG_thresh )


noRegions = [Region("nPhotonGood", (0, -999))]

regionsTTGtable = getRegionsFromThresholds( "PhotonNoChgIsoNoSieie0_pt", [20, 120, 220, -999] )

if __name__ == "__main__":
    for p in mLgPtRegions: print p.vals, str(p), p.cutString( selectionModifier="jesFlavorQCDUp")

