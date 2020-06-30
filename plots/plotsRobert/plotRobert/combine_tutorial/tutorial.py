import ROOT, math, os, sys, re, random
import numpy as np
from subprocess import call
ROOT.gStyle.SetOptStat(0)

#init random engine
random.seed = os.urandom(10)
myseed=random.randint(0,999999)
myseed=123001

def makeSignalTree(k=1):
   '''create signal shapes and templates. x is ~ pT from 0 to 10.
   A second dimension is added (~mass). (mass range is yet 0 to 10)'''

   Nexp=10000*k
   Nobs=ROOT.gRandom.Poisson(Nexp)

   #truth function is: exp(-c*pt)
   #resolution function is: ptreco=ptgen*exp(gaus(0,1))+gaus(0,1)
   sigma1=0.1
   sigma2=0.1
   events=[]

   print "-> Generating ",Nobs, "events for signal"

   for ievt in range(0,Nobs):
       xtrue=-1
       while xtrue<0 or xtrue>10: xtrue=ROOT.gRandom.Exp(8.)
       xreco=xtrue*ROOT.TMath.Exp(ROOT.gRandom.Gaus(0,sigma1))+ROOT.gRandom.Gaus(0,sigma2)
       xmass=ROOT.gRandom.Gaus(5,1.)
       events.append((xtrue,xreco,xmass))

   return events

def makeBackgroundTree(k=1):
   '''as signal, but no smearing assume is alerady reco level'''

   Nexp=10000*k
   Nobs=ROOT.gRandom.Poisson(Nexp)
   events=[]

   print "-> Generating ",Nobs, "events for background"

   for ievt in range(0,Nobs):
       xtrue=-1
       while xtrue<0 or xtrue>10: xtrue=ROOT.gRandom.Uniform(0,10)
       # xtrue = xreco for background
       xmass=ROOT.gRandom.Uniform(0,10)
       events.append((xtrue,xtrue,xmass))

   return events

shapes={}
def makeObs():
   global shapes
   hData=ROOT.TH1D("hdata","hdata",10,0,10)
   hData.Sumw2()
   for xtrue,xreco,xmass in makeSignalTree(1) + makeBackgroundTree(1):
       #print "DEBUG","filling data", xtrue,xreco,xmass
       hData.Fill(xreco)
       #shapes
       recobin=hData.FindBin(xreco)
       if(recobin>0 and recobin< hData.GetNbinsX()+1):
           #no over/underflows
           BookAndFill(shapes,"DataObs_Reco_%d"%recobin,100,0,10,xmass)## mass
           removeOverflows(hData)
   return hData

def removeOverflows(h):
    '''overflows and underflows are there to mimic efficiency. make sure they are removed'''
    if h.InheritsFrom("TH2D"):
        h.SetBinContent(0,0,0)
        h.SetBinContent(h.GetNbinsX()+1,h.GetNbinsY()+1,0)
        for x in range(0,h.GetNbinsX()+1):
            h.SetBinContent(x,0,0)
            h.SetBinContent(x,h.GetNbinsY()+1,0)
        for y in range(0,h.GetNbinsY()+1):
            h.SetBinContent(0,y,0)
            h.SetBinContent(h.GetNbinsX()+1,y,0)
        return
        if h.InheritsFrom("TH1D"):
            h.SetBinContent(0,0)
            h.SetBinContent(h.GetNbinsX()+1,0)
    return

def BookAndFill(d,name, nBins,xmin,xmax,value,weight=1.):
 if name not in d:
     d[name]=ROOT.TH1D(name,name,nBins,xmin,xmax)
 d[name].Fill(value,weight)

def makeResponseMatrix():
    '''MC stat is ~10x data stat.'''

    global shapes

    hGen=ROOT.TH1D("hgen","hgen",10,0,10)
    hReco=ROOT.TH1D("hreco","hreco",10,0,10)
    hBkg=ROOT.TH1D("hbkg","hbkg",10,0,10)
    hResp=ROOT.TH2D("hresp","hresp",10,0,10,10,0,10)
    nMC=10.

    for xtrue,xreco,xmass in makeSignalTree(nMC):
        #print "filling sig", xtrue, xreco, xmass
        hReco.Fill(xreco,1./nMC)
        hGen.Fill(xtrue,1./nMC)
        hResp.Fill(xreco,xtrue,1./nMC)
        recobin=hData.FindBin(xreco)
        genbin=hGen.FindBin(xtrue) ## this should be ok
        if(recobin>0 and recobin< hData.GetNbinsX()+1):
            #no over/underflows
            BookAndFill(shapes,"Reco_%d_Gen_%d"%(recobin,genbin),100,0,10,xmass,1./nMC)

    for xtrue,xreco,xmass in makeBackgroundTree(nMC):
        hBkg.Fill(xreco,1./nMC)
        if(recobin>0 and recobin< hData.GetNbinsX()+1):
            #no over/underflows
            BookAndFill(shapes,"Bkg_%d"%(recobin),100,0,10,xmass,1./nMC)

    #hReco.Add(hBkg)
    removeOverflows(hGen)
    removeOverflows(hReco)
    removeOverflows(hResp)
    removeOverflows(hBkg)
    return hGen,hReco,hResp,hBkg

gc=[]
## make them global for further usage
print "-> Setting seed", myseed
ROOT.gRandom.SetSeed(myseed)
hData=makeObs()
hGen,hReco,hResp,hBkg = makeResponseMatrix()
gc.extend([hGen,hReco,hResp,hBkg,hData])

def makeSimpleDatacard():
    '''make a binned datacard to match the 1D ML unfolding.
    This are C&C datacards no syst.'''
    global hGen,hReco,hResp,hBkg
   
    datacard=open("datacard.txt","w")
   
    datacard.write("## Automatically generated. Simple C&C datacard model.\n")
    datacard.write("## Original author: Andrea Carlo Marini\n")
    datacard.write("* imax\n")
    datacard.write("* jmax\n")
    datacard.write("* kmax\n")
    datacard.write("----------------\n")
    datacard.write("bin ") 
   
    for ireco in range(1,hReco.GetNbinsX()+1):
        datacard.write("Reco_%d "%ireco)
    datacard.write("\n")
   
    datacard.write("observation ")
   
    for ireco in range(1,hReco.GetNbinsX()+1):
        datacard.write("%d "%(hData.GetBinContent(ireco)))
    datacard.write("\n")
    datacard.write("----------------\n")
   
    cleanup=True
   
    datacard.write("bin ")
    for ireco in range(1,hReco.GetNbinsX()+1):
        for igen in range(1,hGen.GetNbinsX()+1):
            # remove un-necessary processes
            if cleanup and hResp.GetBinContent(ireco,igen)<0.01: continue
            datacard.write("Reco_%d "%ireco) ##sig igen, in reco ireco
        datacard.write("Reco_%d "%ireco)## bkg
    datacard.write("\n")

    datacard.write("process ")
    for ireco in range(1,hReco.GetNbinsX()+1):
        for igen in range(1,hGen.GetNbinsX()+1):
            if cleanup and hResp.GetBinContent(ireco,igen)<0.01: continue
            datacard.write("Gen_%d "%igen) ##sig igen, in reco ireco
        datacard.write("Bkg ")## bkg
    datacard.write("\n")

    datacard.write("process ")
    for ireco in range(1,hReco.GetNbinsX()+1):
        for igen in range(1,hGen.GetNbinsX()+1):
            if cleanup and hResp.GetBinContent(ireco,igen)<0.01: continue
            datacard.write("%d "%(-igen)) ## 0 -1, -2 --> for signal
        datacard.write("1 ")## bkg >0 for bkg
    datacard.write("\n")

    datacard.write("rate ")
    for ireco in range(1,hReco.GetNbinsX()+1):
        for igen in range(1,hGen.GetNbinsX()+1):
            if cleanup and hResp.GetBinContent(ireco,igen)<0.01: continue
            datacard.write("%.2f "% (hResp.GetBinContent(ireco,igen)))
        datacard.write("%.2f "%(hBkg.GetBinContent(ireco)))##
    datacard.write("\n")
    datacard.write("----------------\n")

    ## syst
    po=' '.join(["--PO map='.*/Gen_%d:r_bin%d[1,0,20]'"%(igen,igen) for igen in range(1,hGen.GetNbinsX()+1)])
    datacard.write("### RUN WITH COMMANDS: ####\n")
    datacard.write("# text2workspace.py datacard.txt -o datacard.root -PHiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel "+po+"\n")
    datacard.write("# Run with command: combine -M MultiDimFit --algo singles -d datacard.root -t 0 \n")
    datacard.write("############################\n")

makeSimpleDatacard()
