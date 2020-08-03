import ROOT
import os

from Analysis.Tools.helpers import getObjFromFile
from Analysis.Tools.u_float import u_float

# Logging
import logging
logger = logging.getLogger(__name__)

g16_keys_Scaleup = ( "photon_2016_Scale.root", "pt_eta_ScaleUp" )
g17_keys_Scaleup = ( "photon_2017_Scale.root", "pt_eta_ScaleUp" )
g18_keys_Scaleup = ( "photon_2018_Scale.root", "pt_eta_ScaleUp" )

g16_keys_Scaledown = ( "photon_2016_Scale.root", "pt_eta_ScaleDown" )
g17_keys_Scaledown = ( "photon_2017_Scale.root", "pt_eta_ScaleDown" )
g18_keys_Scaledown = ( "photon_2018_Scale.root", "pt_eta_ScaleDown" )

g16_keys_Resup = ( "photon_2016_Res.root", "pt_eta_ResUp" )
g17_keys_Resup = ( "photon_2017_Res.root", "pt_eta_ResUp" )
g18_keys_Resup = ( "photon_2018_Res.root", "pt_eta_ResUp" )

g16_keys_Resdown = ( "photon_2016_Res.root", "pt_eta_ResDown" )
g17_keys_Resdown = ( "photon_2017_Res.root", "pt_eta_ResDown" )
g18_keys_Resdown = ( "photon_2018_Res.root", "pt_eta_ResDown" )

e16_keys_Scaleup = ( "electron_2016_Scale.root", "pt_eta_ScaleUp" )
e17_keys_Scaleup = ( "electron_2017_Scale.root", "pt_eta_ScaleUp" )
e18_keys_Scaleup = ( "electron_2018_Scale.root", "pt_eta_ScaleUp" )

e16_keys_Scaledown = ( "electron_2016_Scale.root", "pt_eta_ScaleDown" )
e17_keys_Scaledown = ( "electron_2017_Scale.root", "pt_eta_ScaleDown" )
e18_keys_Scaledown = ( "electron_2018_Scale.root", "pt_eta_ScaleDown" )

e16_keys_Resup = ( "electron_2016_Res.root", "pt_eta_ResUp" )
e17_keys_Resup = ( "electron_2017_Res.root", "pt_eta_ResUp" )
e18_keys_Resup = ( "electron_2018_Res.root", "pt_eta_ResUp" )

e16_keys_Resdown = ( "electron_2016_Res.root", "pt_eta_ResDown" )
e17_keys_Resdown = ( "electron_2017_Res.root", "pt_eta_ResDown" )
e18_keys_Resdown = ( "electron_2018_Res.root", "pt_eta_ResDown" )

class EcalPtUncertainty:
    def __init__( self, year ):

        if year not in [ 2016, 2017, 2018 ]:
            raise Exception("Photon Veto SF for year %i not known"%year)

        self.year = year

        if self.year == 2016:
            e_keys_Scaleup = e16_keys_Scaleup
            e_keys_Scaledown = e16_keys_Scaledown
            e_keys_Resup = e16_keys_Resup
            e_keys_Resdown = e16_keys_Resdown

            g_keys_Scaleup = g16_keys_Scaleup
            g_keys_Scaledown = g16_keys_Scaledown
            g_keys_Resup = g16_keys_Resup
            g_keys_Resdown = g16_keys_Resdown

        elif self.year == 2017:
            e_keys_Scaleup = e17_keys_Scaleup
            e_keys_Scaledown = e17_keys_Scaledown
            e_keys_Resup = e17_keys_Resup
            e_keys_Resdown = e17_keys_Resdown

            g_keys_Scaleup = g17_keys_Scaleup
            g_keys_Scaledown = g17_keys_Scaledown
            g_keys_Resup = g17_keys_Resup
            g_keys_Resdown = g17_keys_Resdown

        elif self.year == 2018:
            e_keys_Scaleup = e18_keys_Scaleup
            e_keys_Scaledown = e18_keys_Scaledown
            e_keys_Resup = e18_keys_Resup
            e_keys_Resdown = e18_keys_Resdown

            g_keys_Scaleup = g18_keys_Scaleup
            g_keys_Scaledown = g18_keys_Scaledown
            g_keys_Resup = g18_keys_Resup
            g_keys_Resdown = g18_keys_Resdown

        self.dataDir = "$CMSSW_BASE/src/TTGammaEFT/Tools/data/ecalUncertainty"
        self.g_Scaleup   = getObjFromFile(os.path.expandvars(os.path.join(self.dataDir, g_keys_Scaleup[0])),   g_keys_Scaleup[1])
        self.g_Scaledown = getObjFromFile(os.path.expandvars(os.path.join(self.dataDir, g_keys_Scaledown[0])), g_keys_Scaledown[1])
        self.g_Resup     = getObjFromFile(os.path.expandvars(os.path.join(self.dataDir, g_keys_Resup[0])),     g_keys_Resup[1])
        self.g_Resdown   = getObjFromFile(os.path.expandvars(os.path.join(self.dataDir, g_keys_Resdown[0])),   g_keys_Resdown[1])

        self.e_Scaleup   = getObjFromFile(os.path.expandvars(os.path.join(self.dataDir, e_keys_Scaleup[0])),   e_keys_Scaleup[1])
        self.e_Scaledown = getObjFromFile(os.path.expandvars(os.path.join(self.dataDir, e_keys_Scaledown[0])), e_keys_Scaledown[1])
        self.e_Resup     = getObjFromFile(os.path.expandvars(os.path.join(self.dataDir, e_keys_Resup[0])),     e_keys_Resup[1])
        self.e_Resdown   = getObjFromFile(os.path.expandvars(os.path.join(self.dataDir, e_keys_Resdown[0])),   e_keys_Resdown[1])

        for gmap in [self.g_Scaleup, self.g_Scaledown, self.g_Resup, self.g_Resdown]: assert gmap
        for emap in [self.e_Scaleup, self.e_Scaledown, self.e_Resup, self.e_Resdown]: assert emap

    def getPartialSF( self, ptmap, pt, eta ):
        bin = ptmap.FindBin(pt,abs(eta))
        sf  = ptmap.GetBinContent( bin )
        return sf

    def getSF( self, pt, eta, pdgId, unc ):

        pdgId = abs(pdgId)
        eta   = abs(eta)

        if unc not in ["Scale","Res"]:
            raise ValueError("Uncertainty not known: %s. Please enter Scale or Res!"%unc)

        if pdgId not in [11,22]:
            raise ValueError("Uncertainty only valid for electrons and photons! Got pdgId %i"%pdgId)

        if pt >= 300: pt  = 299

        if pdgId == 22:
            if pt       <= 10:  pt  = 11
            if abs(eta) >= 1.4442: eta = 1.4441

            if unc == "Scale":
                mapUp   = self.g_Scaleup
                mapDown = self.g_Scaledown
            elif unc == "Res":
                mapUp   = self.g_Resup
                mapDown = self.g_Resdown

        elif pdgId == 11:
            if pt       <= 15:  pt  = 16
            if abs(eta) >= 2.4: eta = 2.39

            if unc == "Scale":
                mapUp   = self.e_Scaleup
                mapDown = self.e_Scaledown
            elif unc == "Res":
                mapUp   = self.e_Resup
                mapDown = self.e_Resdown

        sfUp   = self.getPartialSF( mapUp,   pt, abs(eta) )
        sfDown = self.getPartialSF( mapDown, pt, abs(eta) )

        return sfUp, sfDown


if __name__ == "__main__":

    print "2016"
    LSF = EcalPtUncertainty(year=2016)
    print LSF.getSF(20, 1, 11, "Scale")
    print LSF.getSF(20, -1, 11, "Scale")
    print LSF.getSF(20, 1, 11, "Scale")
    print LSF.getSF(20, -1, 11, "Scale")

    print LSF.getSF(300, 1, 11, "Scale")
    print LSF.getSF(300, -1, 11, "Scale")
    print LSF.getSF(300, 1, 11, "Scale")
    print LSF.getSF(300, -1, 11, "Scale")

    print LSF.getSF(20, 1.4, 11, "Scale")
    print LSF.getSF(20, -1.4, 11, "Scale")
    print LSF.getSF(20, 1.4, 11, "Scale")
    print LSF.getSF(20, -1.4, 11, "Scale")

    print LSF.getSF(300, 1.4, 11, "Scale")
    print LSF.getSF(300, -1.4, 11, "Scale")
    print LSF.getSF(300, 1.4, 11, "Scale")
    print LSF.getSF(300, -1.4, 11, "Scale")

    print "2017"
    LSF = EcalPtUncertainty(year=2017)
    print LSF.getSF(20, 1, 11, "Scale")
    print LSF.getSF(20, -1, 11, "Scale")
    print LSF.getSF(20, 1, 11, "Scale")
    print LSF.getSF(20, -1, 11, "Scale")

    print LSF.getSF(300, 1, 11, "Scale")
    print LSF.getSF(300, -1, 11, "Scale")
    print LSF.getSF(300, 1, 11, "Scale")
    print LSF.getSF(300, -1, 11, "Scale")

    print LSF.getSF(20, 1.4, 11, "Scale")
    print LSF.getSF(20, -1.4, 11, "Scale")
    print LSF.getSF(20, 1.4, 11, "Scale")
    print LSF.getSF(20, -1.4, 11, "Scale")

    print LSF.getSF(300, 1.4, 11, "Scale")
    print LSF.getSF(300, -1.4, 11, "Scale")
    print LSF.getSF(300, 1.4, 11, "Scale")
    print LSF.getSF(300, -1.4, 11, "Scale")

    print "2018"
    LSF = EcalPtUncertainty(year=2018)
    print LSF.getSF(20, 1, 11, "Scale")
    print LSF.getSF(20, -1, 11, "Scale")
    print LSF.getSF(20, 1, 11, "Scale")
    print LSF.getSF(20, -1, 11, "Scale")

    print LSF.getSF(300, 1, 11, "Scale")
    print LSF.getSF(300, -1, 11, "Scale")
    print LSF.getSF(300, 1, 11, "Scale")
    print LSF.getSF(300, -1, 11, "Scale")

    print LSF.getSF(20, 1.4, 11, "Scale")
    print LSF.getSF(20, -1.4, 11, "Scale")
    print LSF.getSF(20, 1.4, 11, "Scale")
    print LSF.getSF(20, -1.4, 11, "Scale")

    print LSF.getSF(300, 1.4, 11, "Scale")
    print LSF.getSF(300, -1.4, 11, "Scale")
    print LSF.getSF(300, 1.4, 11, "Scale")
    print LSF.getSF(300, -1.4, 11, "Scale")
