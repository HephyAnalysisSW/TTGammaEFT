import math
import copy

def getCorrelationMatrixEntryByNuisances( correlationFitObject, n1, n2 ):
    if n1 == n2: return 1.

#    all_pars = correlationFitObject.floatParsFinal()
#    all_pars = [ all_pars.at(i).GetName() for i in range(all_pars.getSize()) ]

#    if n1 not in all_pars or n2 not in all_pars: return 0.

    return float( correlationFitObject.correlation( n1, n2 ) )

def sumNuisanceHistos( hists, corrObj, refHist ):

    if not hists: return { "ref":None, "up":None, "down":None }

    allNuisances = hists.keys()

    hists = copy.deepcopy(hists)

    refUp   = refHist.Clone()
    refDown = refHist.Clone()
    refUp.Scale(0)
    refDown.Scale(0)

    for i_n, n in enumerate(allNuisances):
        hists[n]["up"].Add( hists[n]["ref"], -1 )
        hists[n]["down"].Add( hists[n]["ref"], -1 )
        hists[n]["down"].Scale(-1)

    for i_n, ni in enumerate(allNuisances):
        for j_n, nj in enumerate(allNuisances):

            tmpHistUp_i = hists[ni]["up"].Clone()
            tmpHistUp_j = hists[nj]["up"].Clone()
            tmpHistUp_i.Multiply( tmpHistUp_j )

            tmpHistDown_i = hists[ni]["down"].Clone()
            tmpHistDown_j = hists[nj]["down"].Clone()
            tmpHistDown_i.Multiply( tmpHistDown_j )

            if i_n != j_n:
#                print ni, nj, getCorrelationMatrixEntryByNuisances( corrObj, ni, nj )

                corr = getCorrelationMatrixEntryByNuisances( corrObj, ni, nj )
                tmpHistUp_i.Scale( corr )
                tmpHistDown_i.Scale( corr )

            refUp.Add(   tmpHistUp_i   )
            refDown.Add( tmpHistDown_i )

    for i in range( refUp.GetNbinsX() ):
        refUp.SetBinContent( i+1, math.sqrt( refUp.GetBinContent( i+1 ) ) )
        refDown.SetBinContent( i+1, math.sqrt( refDown.GetBinContent( i+1 ) ) )

    refDown.Scale( -1 )
    refUp.Add( refHist )
    refDown.Add( refHist )

    return { "ref":refHist, "up":refUp, "down":refDown }
