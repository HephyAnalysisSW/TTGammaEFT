import ROOT
import os, copy
from Analysis.Tools.u_float import u_float
from Analysis.Tools.helpers import getObjFromFile

basedir = "$CMSSW_BASE/src/TTGammaEFT/Tools/data/triggerEff/"

# 2016 Lumi Ratios
lumiRatio2016_BCDEF = 19.695422959 / 35.921875595
lumiRatio2016_GH    = 16.226452636 / 35.921875595

#2016
e_trigger2016_SF      = basedir + "sf_ele_2016_trig_v5.root"
mu_trigger2016BtoF_SF = basedir + "mu_2016BCDEF_EfficienciesAndSF.root"
mu_trigger2016GH_SF   = basedir + "mu_2016GH_EfficienciesAndSF.root"

#2017
e_trigger2017_SF   = basedir + "sf_ele_2017_trig_v5.root"
mu_trigger2017_SF  = basedir + "mu_2017_EfficienciesAndSF.root"

#2018
e_trigger2018_SF   = basedir + "sf_ele_2018_trig_v5.root"
mu_trigger2018_SF  = basedir + "mu_2018_EfficienciesAndSF.root"

class TriggerEfficiency:
    def __init__( self, year=2016 ):

        if year not in [ 2016, 2017, 2018 ]:
            raise Exception("Trigger SF for year %i not known"%year)

        self.year = year

        if year == 2016:
            self.mu_SF   = getObjFromFile( os.path.expandvars(mu_trigger2016BtoF_SF), "abseta_pt_ratio" )
            self.muGH_SF = getObjFromFile( os.path.expandvars(mu_trigger2016GH_SF),   "abseta_pt_ratio" )
            self.e_SF    = getObjFromFile(os.path.expandvars(e_trigger2016_SF),       "EGamma_SF2D")
            for effMap in [self.mu_SF,self.muGH_SF,self.e_SF]: assert effMap

        elif year == 2017:
            self.mu_SF = getObjFromFile(os.path.expandvars(mu_trigger2017_SF), "abseta_pt_ratio")
            self.e_SF  = getObjFromFile(os.path.expandvars(e_trigger2017_SF),  "EGamma_SF2D")
            for effMap in [self.mu_SF,self.e_SF]: assert effMap

        elif year == 2018:
            self.mu_SF = getObjFromFile(os.path.expandvars(mu_trigger2018_SF), "abseta_pt_ratio")
            self.e_SF  = getObjFromFile(os.path.expandvars(e_trigger2018_SF),  "EGamma_SF2D")
            for effMap in [self.mu_SF,self.e_SF]: assert effMap

        self.e_ptMax       = self.e_SF.GetYaxis().GetXmax()
        self.e_ptMin       = self.e_SF.GetYaxis().GetXmin()
        self.e_etaMax      = self.e_SF.GetXaxis().GetXmax()
        self.e_etaMin      = self.e_SF.GetXaxis().GetXmin()

        self.mu_ptMax       = self.mu_SF.GetYaxis().GetXmax()
        self.mu_ptMin       = self.mu_SF.GetYaxis().GetXmin()
        self.mu_etaMax      = self.mu_SF.GetXaxis().GetXmax()
        self.mu_etaMin      = self.mu_SF.GetXaxis().GetXmin()

        print self.e_ptMax, self.e_ptMin, self.e_etaMax, self.e_etaMin, self.mu_ptMax, self.mu_ptMin, self.mu_etaMax, self.mu_etaMin

    def __getSF(self, map_, pt, eta):
        val    = map_.GetBinContent( map_.FindBin(eta, pt) )
        valErr = map_.GetBinError(   map_.FindBin(eta, pt) )
        return u_float(val, valErr)

    def getSF(self, pdgId, pt, eta, sigma=0):

        pdgId = abs(pdgId)
        if pdgId not in [11,13]: raise Exception("Trigger SF for pdgId %i not known"%pdgId)

        if pdgId == 11:
            if pt  > self.e_ptMax:   pt  = self.e_ptMax  - 1 
            if pt  < self.e_ptMin:   pt  = self.e_ptMin  + 1 
            if eta > self.e_etaMax:  eta = self.e_etaMax - 0.1
            if eta < self.e_etaMin:  eta = self.e_etaMin + 0.1

        if pdgId == 13:
            eta = abs(eta)
            if pt  > self.mu_ptMax:  pt  = self.mu_ptMax  - 1 
            if pt  < self.mu_ptMin:  pt  = self.mu_ptMin  + 1 
            if eta > self.mu_etaMax: eta = self.mu_etaMax - 0.1
            if eta < self.mu_etaMin: eta = self.mu_etaMin + 0.1

        if self.year == 2016 and pdgId == 13:
            sf_BCDEF = self.__getSF( self.mu_SF,   pt, eta )
            sf_GH    = self.__getSF( self.muGH_SF, pt, eta )
            sf       = sf_BCDEF*lumiRatio2016_BCDEF + sf_GH*lumiRatio2016_GH
            return sf.val + sigma*sf.sigma

        elif pdgId == 13:
            sf = self.__getSF( self.mu_SF, pt, eta )
            return sf.val + sigma*sf.sigma

        elif pdgId == 11:
            sf = self.__getSF( self.e_SF, pt, eta )
            return sf.val + sigma*sf.sigma

        raise ValueError( "Did not find trigger SF for pt %3.2f eta %3.2f pdgId %i"%( p["pt"], p["eta"], p["pdgId"] ) )


if __name__ == "__main__":

    sigma = 0
    print "2016"
    LSF = TriggerEfficiency(year=2016)
    print LSF.getSF(13, 56.047538, -0.020153, sigma=sigma)
    exit()


    print LSF.getSF(11, 10, 1, sigma=sigma)
    print LSF.getSF(11, 10, -1, sigma=sigma)
    print LSF.getSF(13, 10, 1, sigma=sigma)
    print LSF.getSF(13, 10, -1, sigma=sigma)

    print LSF.getSF(11, 200, 1, sigma=sigma)
    print LSF.getSF(11, 200, -1, sigma=sigma)
    print LSF.getSF(13, 200, 1, sigma=sigma)
    print LSF.getSF(13, 200, -1, sigma=sigma)

    print LSF.getSF(11, 600, 1, sigma=sigma)
    print LSF.getSF(11, 600, -1, sigma=sigma)
    print LSF.getSF(13, 600, 1, sigma=sigma)
    print LSF.getSF(13, 600, -1, sigma=sigma)

    print LSF.getSF(11, 10, 2.0, sigma=sigma)
    print LSF.getSF(11, 10, -2.0, sigma=sigma)
    print LSF.getSF(13, 10, 2.0, sigma=sigma)
    print LSF.getSF(13, 10, -2.0, sigma=sigma)

    print LSF.getSF(11, 200, 2.0, sigma=sigma)
    print LSF.getSF(11, 200, -2.0, sigma=sigma)
    print LSF.getSF(13, 200, 2.0, sigma=sigma)
    print LSF.getSF(13, 200, -2.0, sigma=sigma)

    print LSF.getSF(11, 600, 2.0, sigma=sigma)
    print LSF.getSF(11, 600, -2.0, sigma=sigma)
    print LSF.getSF(13, 600, 2.0, sigma=sigma)
    print LSF.getSF(13, 600, -2.0, sigma=sigma)

    print "2017"
    LSF = TriggerEfficiency(year=2017)
    print LSF.getSF(11, 10, 1, sigma=sigma)
    print LSF.getSF(11, 10, -1, sigma=sigma)
    print LSF.getSF(13, 10, 1, sigma=sigma)
    print LSF.getSF(13, 10, -1, sigma=sigma)

    print LSF.getSF(11, 200, 1, sigma=sigma)
    print LSF.getSF(11, 200, -1, sigma=sigma)
    print LSF.getSF(13, 200, 1, sigma=sigma)
    print LSF.getSF(13, 200, -1, sigma=sigma)

    print LSF.getSF(11, 10, 2.0, sigma=sigma)
    print LSF.getSF(11, 10, -2.0, sigma=sigma)
    print LSF.getSF(13, 10, 2.0, sigma=sigma)
    print LSF.getSF(13, 10, -2.0, sigma=sigma)

    print LSF.getSF(11, 200, 2.0, sigma=sigma)
    print LSF.getSF(11, 200, -2.0, sigma=sigma)
    print LSF.getSF(13, 200, 2.0, sigma=sigma)
    print LSF.getSF(13, 200, -2.0, sigma=sigma)

    print "2018"
    LSF = TriggerEfficiency(year=2018)
    print LSF.getSF(11, 10, 1, sigma=sigma)
    print LSF.getSF(11, 10, -1, sigma=sigma)
    print LSF.getSF(13, 10, 1, sigma=sigma)
    print LSF.getSF(13, 10, -1, sigma=sigma)

    print LSF.getSF(11, 200, 1, sigma=sigma)
    print LSF.getSF(11, 200, -1, sigma=sigma)
    print LSF.getSF(13, 200, 1, sigma=sigma)
    print LSF.getSF(13, 200, -1, sigma=sigma)

    print LSF.getSF(11, 10, 2.0, sigma=sigma)
    print LSF.getSF(11, 10, -2.0, sigma=sigma)
    print LSF.getSF(13, 10, 2.0, sigma=sigma)
    print LSF.getSF(13, 10, -2.0, sigma=sigma)

    print LSF.getSF(11, 200, 2.0, sigma=sigma)
    print LSF.getSF(11, 200, -2.0, sigma=sigma)
    print LSF.getSF(13, 200, 2.0, sigma=sigma)
    print LSF.getSF(13, 200, -2.0, sigma=sigma)
