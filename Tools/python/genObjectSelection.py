''' ObjectSelections
'''

def genFraction( fwlite_jet, pdgId ):
    return sum( [ fwlite_jet.getGenConstituent(i).pt() for i in range(fwlite_jet.numberOfSourceCandidatePtrs()) if abs(fwlite_jet.getGenConstituent(i).pdgId()) == pdgId ], 0 )/fwlite_jet.pt()

def genJetId( fwlite_jet ):
    return genFraction(fwlite_jet, 13)<0.8 and genFraction(fwlite_jet, 11)<0.8

def isGoodGenJet( j ):
    ''' jet object selection
    '''
    return j['pt'] > 30 and abs( j['eta'] ) < 2.4
#    return j['pt'] > 0 and abs( j['eta'] ) < 5.

def isGoodGenPhoton( j ):
    ''' photon object selection
    '''
    return j['pt'] > 20 and abs( j['eta'] ) < 1.479
#    return j['pt'] > 15 and abs( j['eta'] ) < 5.

def isGoodGenLepton( l ):
    ''' lepton object selection
    '''
    return l['pt'] > 20 and abs( l['eta'] ) < 2.4 and abs( int(l['pdgId']) ) in [11,13] #eta < 2.5
#    return l['pt'] > 0 and abs( l['eta'] ) < 5. and abs( int(l['pdgId']) ) in [11,13] #eta < 2.5
