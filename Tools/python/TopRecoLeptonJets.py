import ROOT
from math import sin, cos, sinh, cosh, sqrt

ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/Analysis/Tools/scripts/NeutrinoSolver.cc")

#NeutrinoSolver ns(lepton, bjet);
#double dnu;
#TLorentzVector neutrino = ns.GetBest(met->Px(), met->Py(), 1., 1., 0., dnu);

def TL_from_dict( d ):
    t = ROOT.TLorentzVector()
    t.SetPxPyPzE( d['pt']*cos(d['phi']), d['pt']*sin(d['phi']), d['pt']*sinh(d['eta']), d['pt']*cosh(d['eta']) )
    return t

#def mass( solution ):
    

class TopRecoLeptonJets:

    def __init__( self, met, lepton, bJets, nonBJets ):
        self.solutions_withBJets = []
        for bJet in bJets:
            ns = ROOT.NeutrinoSolver( TL_from_dict(lepton), TL_from_dict(bJet) )  
            D2 = ROOT.Double()
            ns.GetBest( met['pt']*cos(met['phi']), met['pt']*sin(met['phi']), 1., 1., 0., D2 )
            self.solutions_withBJets.append({'D2':D2, 'lepton':lepton, 'bJet':bJet})
        self.solutions_nonBJets = []
        for bJet in nonBJets:
            ns = ROOT.NeutrinoSolver( TL_from_dict(lepton), TL_from_dict(bJet) )  
            D2 = ROOT.Double()
            ns.GetBest( met['pt']*cos(met['phi']), met['pt']*sin(met['phi']), 1., 1., 0., D2 )
            self.solutions_nonBJets.append({'D2':D2, 'lepton':lepton, 'bJet':bJet})

        self.best_solution_withBJets = max( self.solutions_withBJets, key = lambda s:s['D2'] ) if self.solutions_withBJets else None
        self.best_solution_nonBJets  = max( self.solutions_nonBJets, key = lambda s:s['D2'] ) if self.solutions_nonBJets else None


if __name__=='__main__':
    from events import events
    c_rec_best_b = 0
    c_rec_hardest_jet = 0
    for met, lepton, bjets, nonBJets in events:

        btag_vals = [j['btagDeepB'] for j in bjets + nonBJets]
        btag_vals.sort(key = lambda k:-k)
        pt_vals = [j['pt'] for j in bjets + nonBJets]
        pt_vals.sort(key = lambda k:-k)

        tr = TopRecoLeptonJets( met, lepton, bjets, nonBJets )

        best_b, best_nonB = None, None
        for i_sols, sols in enumerate([ tr.solutions_withBJets, tr.solutions_withBJets ]):
            sols_ = filter( lambda s:s['D2']>=0, sols )
            if sols_:
                best = max( sols_, key = lambda s:s['D2'] )

                if i_sols==0: 
                    best_b = sqrt(best['D2'])
                elif i_sols==1: 
                    best_nonB = sqrt(best['D2'])
                print sqrt(best['D2']), best['bJet']['btagDeepB'],
                has_best_disc = False
                if best['bJet']['btagDeepB'] in btag_vals[:2]:
                    has_best_disc = True
                    print "among best 2 b-jets",
                has_hardest_jet = False
                if best['bJet']['pt'] in pt_vals[:2]:
                    has_hardest_jet = True
                    print "among hardest 2 jets",
                print
        if best_b and best_nonB:
            if best_nonB<best_b:
                print "Can recover with non-bjets!", "from best b", has_best_disc, "from hardest jet", has_hardest_jet
                if has_best_disc: c_rec_best_b+=1
                if has_hardest_jet: c_rec_hardest_jet+=1

        print
        break

print "Recovered best b", c_rec_best_b, "hardest jet", c_rec_hardest_jet
