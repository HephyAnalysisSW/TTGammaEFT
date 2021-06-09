import math, sys
import copy

def getCorrelationMatrixEntryByNuisances( correlationFitObject, n1, n2 ):
    if n1 == n2: return 1.
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
        hists[n]["up"].Add( hists[n]["down"], -1 )
        hists[n]["up"].Scale(0.5)

        for i_b in range( 1, hists[n]["up"].GetNbinsX()+1 ):
            hists[n]["up"].SetBinContent( i_b, abs(hists[n]["up"].GetBinContent( i_b )) )

    for i_n, ni in enumerate(allNuisances):
        for j_n, nj in enumerate(allNuisances):

            tmpHistUp_i = hists[ni]["up"].Clone()
            tmpHistUp_j = hists[nj]["up"].Clone()
            tmpHistUp_i.Multiply( tmpHistUp_j )

            if ni != nj:
                corr = getCorrelationMatrixEntryByNuisances( corrObj, ni, nj )
                tmpHistUp_i.Scale( corr )

            refUp.Add(   tmpHistUp_i   )

    for i in range( refUp.GetNbinsX() ):
        refUp.SetBinContent( i+1, math.sqrt( refUp.GetBinContent( i+1 ) ) )
        refUp.SetBinError( i+1, 0 )
        refHist.SetBinError( i+1, 0 )

    refDown.Add( refUp )
    refDown.Scale( -1 )
    refUp.Add( refHist )
    refDown.Add( refHist )

    return { "ref":refHist, "up":refUp, "down":refDown }




def fillCovarianceHisto( hists, diagHistos, corrObj, covMatrix ):

    if not hists: return covMatrix

    allNuisances = hists.keys()

    hists = copy.deepcopy(hists)
    diagHistos = copy.deepcopy(diagHistos)
    covMatrix = copy.deepcopy(covMatrix)
    covMatrix.Scale(0)

    for i_n, n in enumerate(allNuisances):
        hists[n]["up"].Add( hists[n]["down"], -1 )
        hists[n]["up"].Scale(0.5)

    for i_n, ni in enumerate(allNuisances):
        for j_n, nj in enumerate(allNuisances):
            tmpHistUp_i = hists[ni]["up"].Clone()
            tmpHistUp_j = hists[nj]["up"].Clone()


            corr = getCorrelationMatrixEntryByNuisances( corrObj, ni, nj )
            for i_b in range( 1, tmpHistUp_i.GetNbinsX()+1 ):
                for j_b in range( 1, tmpHistUp_i.GetNbinsX()+1 ):
                    binEntry = abs(tmpHistUp_i.GetBinContent( i_b )) * abs(tmpHistUp_j.GetBinContent( j_b )) * corr
                    covMatrix.SetBinContent( i_b, j_b, covMatrix.GetBinContent( i_b, j_b ) + binEntry )

    for h_dict in diagHistos:
        h = h_dict["up"].Clone()
        h.Add( h_dict["ref"], -1 )
        for i_b in range( 1, h.GetNbinsX()+1 ):
            binEntry = h.GetBinContent( i_b )**2
            covMatrix.SetBinContent( i_b, i_b, covMatrix.GetBinContent( i_b, i_b ) + binEntry )

    return covMatrix





def fillCovarianceHistoMCStat( hists, mcStat, corrObj, covMatrix ):

    if not hists: return covMatrix

    allNuisances = hists.keys()

    hists = copy.deepcopy(hists)
    mcStat = copy.deepcopy(mcStat)
    mcStat["up"].Add( mcStat["ref"], -1 )
#    mcStat["down"].Add( mcStat["ref"], -1 )
#    mcStat["down"].Scale(-1)

    for i_n, n in enumerate(allNuisances):
        hists[n]["up"].Add( hists[n]["ref"], -1 )
#        hists[n]["down"].Add( hists[n]["ref"], -1 )
#        hists[n]["down"].Scale(-1)

    for i_n, ni in enumerate(["MCStat"]+allNuisances):
        for j_n, nj in enumerate(["MCStat"]+allNuisances):

            if ni == "MCStat":
                tmpHistUp_i = mcStat["up"].Clone()
            else:
                tmpHistUp_i = hists[ni]["up"].Clone()

            if nj == "MCStat":
                tmpHistUp_j = mcStat["up"].Clone()
            else:
                tmpHistUp_j = hists[nj]["up"].Clone()

            if ni == "MCStat" and nj.startswith("Signal"):
                corr = -1
            elif nj == "MCStat" and ni.startswith("Signal"):
                corr = -1
            elif ni == nj:
                corr = 1
            elif "MCStat" in [ni,nj]:
                corr = 0
            else:
                corr = getCorrelationMatrixEntryByNuisances( corrObj, ni, nj )

            for i_b in range( 1, tmpHistUp_i.GetNbinsX()+1 ):
                for j_b in range( 1, tmpHistUp_i.GetNbinsX()+1 ):

                    # anti-correlate each MCStat bin with each signal POI
                    if ni == "MCStat" and nj.startswith("Signal") and not "Bin%i"%(i_b-1) in nj:   continue
                    elif nj == "MCStat" and ni.startswith("Signal") and not "Bin%i"%(j_b-1) in ni: continue
                    elif nj == "MCStat" and ni == "MCStat" and not i_b==j_b:                   continue

                    binEntry = abs(tmpHistUp_i.GetBinContent( i_b )) * abs(tmpHistUp_j.GetBinContent( j_b )) * corr
                    covMatrix.SetBinContent( i_b, j_b, covMatrix.GetBinContent( i_b, j_b ) + binEntry )

    return covMatrix



