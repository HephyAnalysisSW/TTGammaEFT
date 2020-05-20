''' Implementation of b-tagging reweighting
'''

# Standard imports
import ROOT, pickle, itertools, os

from Analysis.Tools.helpers import getObjFromFile

from operator import mul

# Logging
import logging
logger = logging.getLogger(__name__)

#binning in pt and eta
ptBorders = [ 30, 50, 70, 100, 140, 200, 500, 800 ]

ptBins    = [ [ptBorders[i], ptBorders[i+1]] for i in range(len(ptBorders)-1) ]
ptBins   += [ [ptBorders[-1], -1] ]

etaBorders = [0, 0.6, 1.2, 1.8, 2.4]
etaBins    = [ [etaBorders[i], etaBorders[i+1]] for i in range(len(etaBorders)-1) ]

def toFlavourKey(pdgId):
    if abs(pdgId)==5: return ROOT.BTagEntry.FLAV_B
    if abs(pdgId)==4: return ROOT.BTagEntry.FLAV_C
    return ROOT.BTagEntry.FLAV_UDSG

keys_2016   = { "Top":{"other":  ( "btag_efficiencies_2016.root",  "Top_l_efficiency" ),
                       "c":      ( "btag_efficiencies_2016.root",  "Top_c_efficiency" ),
                       "b":      ( "btag_efficiencies_2016.root",  "Top_b_efficiency" )},
                "Other":{"other":( "btag_efficiencies_2016.root",  "Other_l_efficiency" ),
                         "c":    ( "btag_efficiencies_2016.root",  "Other_c_efficiency" ),
                         "b":    ( "btag_efficiencies_2016.root",  "Other_b_efficiency" )}
              }
keys_2017   = { "Top":{"other":  ( "btag_efficiencies_2017.root",  "Top_l_efficiency" ),
                       "c":      ( "btag_efficiencies_2017.root",  "Top_c_efficiency" ),
                       "b":      ( "btag_efficiencies_2017.root",  "Top_b_efficiency" )},
                "Other":{"other":( "btag_efficiencies_2017.root",  "Other_l_efficiency" ),
                         "c":    ( "btag_efficiencies_2017.root",  "Other_c_efficiency" ),
                         "b":    ( "btag_efficiencies_2017.root",  "Other_b_efficiency" )}
              }
keys_2018   = { "Top":{"other":  ( "btag_efficiencies_2018.root",  "Top_l_efficiency" ),
                       "c" :     ( "btag_efficiencies_2018.root",  "Top_c_efficiency" ),
                       "b":      ( "btag_efficiencies_2018.root",  "Top_b_efficiency" )},
                "Other":{"other":( "btag_efficiencies_2018.root",  "Other_l_efficiency" ),
                         "c":    ( "btag_efficiencies_2018.root",  "Other_c_efficiency" ),
                         "b":    ( "btag_efficiencies_2018.root",  "Other_b_efficiency" )}
              }
#Method 1ab

# https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation2016Legacy
#sfFile2016DeepCSV  = 'b2016_DeepCSV_2016LegacySF_V1_TuneCP5.csv'
sfFile2016DeepCSV  = 'b2016_DeepCSV_2016LegacySF_V1.csv'
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X
sfFile2017DeepCSV  = 'b2017_DeepCSV_94XSF_V5_B_F.csv'
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation102X
sfFile2018DeepCSV  = 'b2018_DeepCSV_102XSF_V1.csv'

class BTagEfficiency:

#    @staticmethod
    def getBTagSF_1a(self, var, bJets, nonBJets):
        if var not in self.btagWeightNames:
            raise ValueError( "Don't know what to do with b-tag variation %s" %var )
        if var != 'MC':
            ref = reduce(mul, [j['beff']['MC'] for j in bJets] + [1-j['beff']['MC'] for j in nonBJets], 1 )
            if ref>0:
                return reduce(mul, [j['beff'][var] for j in bJets] + [1-j['beff'][var] for j in nonBJets], 1 )/ref
            else:
                logger.warning( "getBTagSF_1a: MC efficiency is zero. Return SF 1. MC efficiencies: %r "% (  [j['beff']['MC'] for j in bJets] + [1-j['beff']['MC'] for j in nonBJets] ) )
                return 1


    def __init__( self, year, isTopSample, WP=ROOT.BTagEntry.OP_MEDIUM ):

        if year not in [ 2016, 2017, 2018 ]:
            raise Exception("Lepton SF for year %i not known"%year)

        self.dataDir = "$CMSSW_BASE/src/TTGammaEFT/Tools/data/btagEfficiencyData/"
        self.year        = year
        self.isTopSample = isTopSample

        # All btag weight names per jet
        self.btagWeightNames = [ 'MC', 'SF', 'SF_b_Down', 'SF_b_Up', 'SF_l_Down', 'SF_l_Up' ]

        # Input files
        if year == 2016:
            self.scaleFactorFile = os.path.expandvars( os.path.join( self.dataDir, sfFile2016DeepCSV ) )
            keys                 = keys_2016
        if year == 2017:
            self.scaleFactorFile = os.path.expandvars( os.path.join( self.dataDir, sfFile2017DeepCSV ) )
            keys                 = keys_2016
        if year == 2018:
            self.scaleFactorFile = os.path.expandvars( os.path.join( self.dataDir, sfFile2018DeepCSV ) )
            keys                 = keys_2016

        self.mcEff = {}
        for s in ["Top","Other"]:
            self.mcEff[s] = {}
            for f in ["other","c","b"]:
                self.mcEff[s][f] = getObjFromFile( os.path.expandvars( os.path.join( self.dataDir, keys[s][f][0] ) ), keys[s][f][1] )

        logger.info ( "Loading scale factors from %s", self.scaleFactorFile )
        ROOT.gSystem.Load( 'libCondFormatsBTauObjects' ) 
        ROOT.gSystem.Load( 'libCondToolsBTau' )
        self.calib = ROOT.BTagCalibration( "deepcsv", self.scaleFactorFile )

        # Get readers
        #recommended measurements for different jet flavours given here: https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation80X#Data_MC_Scale_Factors
        v_sys = getattr(ROOT, 'vector<string>')()
        v_sys.push_back('up')
        v_sys.push_back('down')
        self.reader = ROOT.BTagCalibrationReader(WP, "central", v_sys)
        self.reader.load(self.calib, 0, "comb")
        self.reader.load(self.calib, 1, "comb")
        self.reader.load(self.calib, 2, "incl")

    def getMCEff(self, pdgId, pt, eta):
        ''' Get MC efficiency for jet
        '''
        s = "Top" if self.isTopSample else "Other"
        if   abs(pdgId)==5: flav = "b"
        elif abs(pdgId)==4: flav = "c"
        else:               flav = "other"

        effMap = self.mcEff[s][flav]

        if pt > 800:       pt = 799
        if abs(eta) > 2.4: eta = 2.4

        return effMap.GetBinContent( effMap.FindBin(pt, abs(eta)) )

    def getSF(self, pdgId, pt, eta):
        # BTag SF Not implemented below 20 GeV
        if pt<20: 
            return (1,1,1,1,1)

        # BTag SF Not implemented above absEta 2.4
        if abs(eta)>=2.4: 
            return (1,1,1,1,1)

        #autobounds are implemented now, no doubling of uncertainties necessary anymore
        flavKey = toFlavourKey(pdgId)
        
        #FullSim SFs (times FSSF)
        if abs(pdgId)==5 or abs(pdgId)==4: #SF for b/c
            sf      = self.reader.eval_auto_bounds('central', flavKey, eta, pt)
            sf_b_d  = self.reader.eval_auto_bounds('down',    flavKey, eta, pt)
            sf_b_u  = self.reader.eval_auto_bounds('up',      flavKey, eta, pt)
            sf_l_d  = 1.
            sf_l_u  = 1.
        else: #SF for light flavours
            sf      = self.reader.eval_auto_bounds('central', flavKey, eta, pt)
            sf_b_d  = 1.
            sf_b_u  = 1.
            sf_l_d  = self.reader.eval_auto_bounds('down',    flavKey, eta, pt)
            sf_l_u  = self.reader.eval_auto_bounds('up',      flavKey, eta, pt)

        return (sf, sf_b_d, sf_b_u, sf_l_d, sf_l_u)

    def addBTagEffToJet(self, j):
        mcEff = self.getMCEff( j['hadronFlavour'], j['pt'], j['eta'] )
        sf    = self.getSF( j['hadronFlavour'],    j['pt'], j['eta'] )
        j['beff'] = {'MC':mcEff, 'SF':mcEff*sf[0], 'SF_b_Down':mcEff*sf[1], 'SF_b_Up':mcEff*sf[2], 'SF_l_Down':mcEff*sf[3], 'SF_l_Up':mcEff*sf[4]}

if __name__ == "__main__":

    print "2016"
    BTagEff = BTagEfficiency( year=2016, isTopSample=False )
    print BTagEff.getMCEff(5, 100, 1.5)
    print BTagEff.getMCEff(5, 100, -1.5)
    print BTagEff.getMCEff(5, 100, 2)
    print BTagEff.getMCEff(5, 100, -2)
    print BTagEff.getMCEff(5, 400, 1.5)
    print BTagEff.getMCEff(5, 400, -1.5)
    print BTagEff.getMCEff(5, 400, 2)
    print BTagEff.getMCEff(5, 400, -2)
    del BTagEff

    print "2017"
    BTagEff = BTagEfficiency( year=2017, isTopSample=False )
    print BTagEff.getMCEff(5, 100, 1.5)
    print BTagEff.getMCEff(5, 100, -1.5)
    print BTagEff.getMCEff(5, 100, 2)
    print BTagEff.getMCEff(5, 100, -2)
    print BTagEff.getMCEff(5, 400, 1.5)
    print BTagEff.getMCEff(5, 400, -1.5)
    print BTagEff.getMCEff(5, 400, 2)
    print BTagEff.getMCEff(5, 400, -2)
    del BTagEff

    print "2018"
    BTagEff = BTagEfficiency( year=2018, isTopSample=False )
    print BTagEff.getMCEff(5, 100, 1.5)
    print BTagEff.getMCEff(5, 100, -1.5)
    print BTagEff.getMCEff(5, 100, 2)
    print BTagEff.getMCEff(5, 100, -2)
    print BTagEff.getMCEff(5, 400, 1.5)
    print BTagEff.getMCEff(5, 400, -1.5)
    print BTagEff.getMCEff(5, 400, 2)
    print BTagEff.getMCEff(5, 400, -2)
    del BTagEff

