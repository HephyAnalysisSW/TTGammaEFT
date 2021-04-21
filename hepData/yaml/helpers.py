import numpy as np
import ROOT
from hepdata_lib import Submission, Table, Variable, RootFileReader, Uncertainty

def convertSRHistToYaml( rootfile, label, variable, unit ):

    tab = Table(label)

    reader = RootFileReader(rootfile)

    data = reader.read_hist_1d("dataAR")
    gen = reader.read_hist_1d("TTG_centralnoChgIsoNoSieiephotoncat0")
    had = reader.read_hist_1d("TTG_centralnoChgIsoNoSieiephotoncat134")
    misID = reader.read_hist_1d("TTG_centralnoChgIsoNoSieiephotoncat2")
    qcd = reader.read_hist_1d("QCD")
    uncUp = reader.read_hist_1d("totalUncertainty_up")
    uncDown = reader.read_hist_1d("totalUncertainty_down")

    rootfile = ROOT.TFile(rootfile,"READ")
    statHist = rootfile.Get("dataAR")

    unc = []
    statunc = []
    relunc = []
    tot = []
    for i, i_up in enumerate(uncUp["y"]):
        stat = statHist.GetBinError(i+1)
        u = abs(i_up-uncDown["y"][i])*0.5
        sim = sum([ gen["y"][i], had["y"][i], misID["y"][i], qcd["y"][i] ])
        unc.append(u)
        statunc.append(stat)
        tot.append(sim)
        relunc.append(u*100./sim)

    xbins = Variable( variable, is_independent=True, is_binned=True, units=unit)
    xbins.values = data["x_edges"]
    ydata = Variable( "Observed", is_independent=False, is_binned=False)
    ydata.values = data["y"]
    ydata.add_qualifier("SQRT(S)","13","TeV")
    ydata.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    ytot = Variable( "Total simulation", is_independent=False, is_binned=False)
    ytot.values = tot
    ytot.add_qualifier("SQRT(S)","13","TeV")
    ytot.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    ygen = Variable( "Genuine $\gamma$", is_independent=False, is_binned=False)
    ygen.values = gen["y"]
    ygen.add_qualifier("SQRT(S)","13","TeV")
    ygen.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    yhad = Variable( "Hadronic $\gamma$", is_independent=False, is_binned=False)
    yhad.values = had["y"]
    yhad.add_qualifier("SQRT(S)","13","TeV")
    yhad.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    ymisID = Variable( "Misid. e", is_independent=False, is_binned=False)
    ymisID.values = misID["y"]
    ymisID.add_qualifier("SQRT(S)","13","TeV")
    ymisID.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    yqcd = Variable( "Multijet", is_independent=False, is_binned=False)
    yqcd.values = qcd["y"]
    yqcd.add_qualifier("SQRT(S)","13","TeV")
    yqcd.add_qualifier("LUMINOSITY","137","fb$^{-1}$")

    yunc = Uncertainty( "syst" )
    yunc.is_symmetric = True
    yunc.values = unc

    ystatunc = Uncertainty( "stat" )
    ystatunc.is_symmetric = True
    ystatunc.values = statunc

    ydata.uncertainties.append(ystatunc)
    ytot.uncertainties.append(yunc)

    tab.add_variable(xbins)
    tab.add_variable(ydata)
    tab.add_variable(ytot)
    tab.add_variable(ygen)
    tab.add_variable(yhad)
    tab.add_variable(ymisID)
    tab.add_variable(yqcd)

    return tab



def convertWJetsHistToYaml( rootfile, label ):

    tab = Table(label)

    reader = RootFileReader(rootfile)

    data = reader.read_hist_1d("dataAR")
    ttg = reader.read_hist_1d("TTG_centralall")
    top = reader.read_hist_1d("Top_centralall")
    dy = reader.read_hist_1d("DY_LO_centralall")
    wjets = reader.read_hist_1d("WJets_centralall")
    wg = reader.read_hist_1d("WG_centralall")
    zg = reader.read_hist_1d("ZG_centralall")
    other = reader.read_hist_1d("other_centralall")
    qcd = reader.read_hist_1d("QCD")

    uncUp = reader.read_hist_1d("totalUncertainty_up")
    uncDown = reader.read_hist_1d("totalUncertainty_down")

    rootfile = ROOT.TFile(rootfile,"READ")
    statHist = rootfile.Get("dataAR")

    unc = []
    statunc = []
    relunc = []
    tot = []
    for i, i_up in enumerate(uncUp["y"]):
        stat = statHist.GetBinError(i+1)
        u = abs(i_up-uncDown["y"][i])*0.5
        all = [ ttg["y"][i], top["y"][i], dy["y"][i], wjets["y"][i], wg["y"][i], zg["y"][i], other["y"][i], qcd["y"][i] ]
        sim = sum(all)
        unc.append(u)
        statunc.append(stat)
        tot.append(sim)
        relunc.append(u*100./sim)

    xbins = Variable( "$m_{T}(W)$", is_independent=True, is_binned=True, units="GeV")
    xbins.values = data["x_edges"]
    ydata = Variable( "Observed", is_independent=False, is_binned=False)
    ydata.values = data["y"]
    ydata.add_qualifier("SQRT(S)","13","TeV")
    ydata.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    ytot = Variable( "Total simulation", is_independent=False, is_binned=False)
    ytot.values = tot
    ytot.add_qualifier("SQRT(S)","13","TeV")
    ytot.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    yttg = Variable( "tt$\gamma$", is_independent=False, is_binned=False)
    yttg.values = ttg["y"]
    yttg.add_qualifier("SQRT(S)","13","TeV")
    yttg.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    ytop = Variable( "t/tt", is_independent=False, is_binned=False)
    ytop.values = top["y"]
    ytop.add_qualifier("SQRT(S)","13","TeV")
    ytop.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    ydy = Variable( "Drell-Yan", is_independent=False, is_binned=False)
    ydy.values = dy["y"]
    ydy.add_qualifier("SQRT(S)","13","TeV")
    ydy.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    ywjets = Variable( "W+jets", is_independent=False, is_binned=False)
    ywjets.values = wjets["y"]
    ywjets.add_qualifier("SQRT(S)","13","TeV")
    ywjets.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    ywg = Variable( "W$\gamma$", is_independent=False, is_binned=False)
    ywg.values = wg["y"]
    ywg.add_qualifier("SQRT(S)","13","TeV")
    ywg.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    yzg = Variable( "Z$\gamma$", is_independent=False, is_binned=False)
    yzg.values = zg["y"]
    yzg.add_qualifier("SQRT(S)","13","TeV")
    yzg.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    yother = Variable( "Other", is_independent=False, is_binned=False)
    yother.values = other["y"]
    yother.add_qualifier("SQRT(S)","13","TeV")
    yother.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    yqcd = Variable( "Multijet", is_independent=False, is_binned=False)
    yqcd.values = qcd["y"]
    yqcd.add_qualifier("SQRT(S)","13","TeV")
    yqcd.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
#    yunc = Variable( "Total systematic uncertainty", is_independent=False, is_binned=False)
#    yunc.values = unc
#    yunc.add_qualifier("SQRT(S)","13","TeV")
#    yunc.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    #yrelunc = Variable( "Rel. uncertainty (%)", is_independent=False, is_binned=False)
    #yrelunc.values = relunc

    yunc = Uncertainty( "syst" )
    yunc.is_symmetric = True
    yunc.values = unc

    ystatunc = Uncertainty( "stat" )
    ystatunc.is_symmetric = True
    ystatunc.values = statunc

    ydata.uncertainties.append(ystatunc)
    ytot.uncertainties.append(yunc)

    tab.add_variable(xbins)
    tab.add_variable(ydata)
    tab.add_variable(ytot)
    tab.add_variable(ywjets)
    tab.add_variable(yqcd)
    tab.add_variable(ydy)
    tab.add_variable(ytop)
    tab.add_variable(yother)
    tab.add_variable(ywg)
    tab.add_variable(yzg)
    tab.add_variable(yttg)
#    tab.add_variable(yunc)

    return tab




def convertMlgHistToYaml( rootfile, label, variable ):

    tab = Table(label)

    reader = RootFileReader(rootfile)

    data = reader.read_hist_1d("dataAR")
    misID = reader.read_hist_1d("TTG_centralnoChgIsoNoSieiephotoncat2")
    wg = reader.read_hist_1d("WG_centralnoChgIsoNoSieiephotoncat0")
    zg = reader.read_hist_1d("ZG_centralnoChgIsoNoSieiephotoncat0")
    other = reader.read_hist_1d("TTG_centralnoChgIsoNoSieiephotoncat0")
    had = reader.read_hist_1d("TTG_centralnoChgIsoNoSieiephotoncat134")
    qcd = reader.read_hist_1d("QCD")

    uncUp = reader.read_hist_1d("totalUncertainty_up")
    uncDown = reader.read_hist_1d("totalUncertainty_down")

    rootfile = ROOT.TFile(rootfile,"READ")
    statHist = rootfile.Get("dataAR")

    unc = []
    statunc = []
    relunc = []
    tot = []
    for i, i_up in enumerate(uncUp["y"]):
        stat = statHist.GetBinError(i+1)
        u = abs(i_up-uncDown["y"][i])*0.5
        all = [ misID["y"][i], wg["y"][i], zg["y"][i], other["y"][i], had["y"][i], qcd["y"][i] ]
        sim = sum(all)
        unc.append(u)
        statunc.append(stat)
        tot.append(sim)
        relunc.append(u*100./sim)

    xbins = Variable( variable, is_independent=True, is_binned=True, units="GeV")
    xbins.values = data["x_edges"]
    ydata = Variable( "Observed", is_independent=False, is_binned=False)
    ydata.values = data["y"]
    ydata.add_qualifier("SQRT(S)","13","TeV")
    ydata.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    ytot = Variable( "Total simulation", is_independent=False, is_binned=False)
    ytot.values = tot
    ytot.add_qualifier("SQRT(S)","13","TeV")
    ytot.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    ymisID = Variable( "Misid. e", is_independent=False, is_binned=False)
    ymisID.values = misID["y"]
    ymisID.add_qualifier("SQRT(S)","13","TeV")
    ymisID.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    yhad = Variable( "Hadronic $\gamma$", is_independent=False, is_binned=False)
    yhad.values = had["y"]
    yhad.add_qualifier("SQRT(S)","13","TeV")
    yhad.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    ywg = Variable( "W$\gamma$", is_independent=False, is_binned=False)
    ywg.values = wg["y"]
    ywg.add_qualifier("SQRT(S)","13","TeV")
    ywg.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    yzg = Variable( "Z$\gamma$", is_independent=False, is_binned=False)
    yzg.values = zg["y"]
    yzg.add_qualifier("SQRT(S)","13","TeV")
    yzg.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    yother = Variable( "Other", is_independent=False, is_binned=False)
    yother.values = other["y"]
    yother.add_qualifier("SQRT(S)","13","TeV")
    yother.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    yqcd = Variable( "Multijet", is_independent=False, is_binned=False)
    yqcd.values = qcd["y"]
    yqcd.add_qualifier("SQRT(S)","13","TeV")
    yqcd.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
#    yunc = Variable( "Total systematic uncertainty", is_independent=False, is_binned=False)
#    yunc.values = unc
#    yunc.add_qualifier("SQRT(S)","13","TeV")
#    yunc.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    #yrelunc = Variable( "Rel. uncertainty (%)", is_independent=False, is_binned=False)
    #yrelunc.values = relunc

    yunc = Uncertainty( "syst" )
    yunc.is_symmetric = True
    yunc.values = unc

    ystatunc = Uncertainty( "stat" )
    ystatunc.is_symmetric = True
    ystatunc.values = statunc

    ydata.uncertainties.append(ystatunc)
    ytot.uncertainties.append(yunc)

    tab.add_variable(xbins)
    tab.add_variable(ydata)
    tab.add_variable(ytot)
    tab.add_variable(ymisID)
    tab.add_variable(ywg)
    tab.add_variable(yzg)
    tab.add_variable(yother)
    tab.add_variable(yhad)
    tab.add_variable(yqcd)
#    tab.add_variable(yunc)

    return tab



def convertCRPlotToYaml():

    tab = Table("Figure 5")

    reader = RootFileReader("../regionPlots/CR_incl.root")

    data = reader.read_hist_1d("0dc_2016data")
    tot = reader.read_hist_1d("0dc_2016total")
    totbkg = reader.read_hist_1d("0dc_2016total_background")
    wg = reader.read_hist_1d("0dc_2016WG")
    zg = reader.read_hist_1d("0dc_2016ZG")
    misID = reader.read_hist_1d("0dc_2016misID")
    had = reader.read_hist_1d("0dc_2016fakes")
    qcd = reader.read_hist_1d("0dc_2016QCD")
    ttg = reader.read_hist_1d("0dc_2016signal")
    other = reader.read_hist_1d("0dc_2016other")

    rootfile = ROOT.TFile("../regionPlots/CR_incl.root","READ")
    totHist = rootfile.Get("0dc_2016total")

    unc = []
    relunc = []
    for i, i_tot in enumerate(tot["y"]):
        u = totHist.GetBinError(i+1)
        unc.append(u)
        relunc.append(u*100./i_tot)

    crBinLabel = [
            "ZG3, e, 20 $\leq$ $p_{T}(\gamma)$ $<$ 65 GeV",
            "WG3, e, 20 $\leq$ $p_{T}(\gamma)$ $<$ 65 GeV",
            "ZG3, e, 65 $\leq$ $p_{T}(\gamma)$ $<$ 160 GeV",
            "WG3, e, 65 $\leq$ $p_{T}(\gamma)$ $<$ 160 GeV",
            "ZG+WG3, e, $p_{T}(\gamma)$ $\geq$ 160 GeV",
            "ZG3, $\mu$, 20 $\leq$ $p_{T}(\gamma)$ $<$ 65 GeV",
            "WG3, $\mu$, 20 $\leq$ $p_{T}(\gamma)$ $<$ 65 GeV",
            "ZG3, $\mu$, 65 $\leq$ $p_{T}(\gamma)$ $<$ 160 GeV",
            "WG3, $\mu$, 65 $\leq$ $p_{T}(\gamma)$ $<$ 160 GeV",
            "ZG+WG3, $\mu$, $p_{T}(\gamma)$ $\geq$ 160 GeV",
            "ZG4p, e, 20 $\leq$ $p_{T}(\gamma)$ $<$ 65 GeV",
            "WG4p, e, 20 $\leq$ $p_{T}(\gamma)$ $<$ 65 GeV",
            "ZG4p, e, 65 $\leq$ $p_{T}(\gamma)$ $<$ 160 GeV",
            "WG4p, e, 65 $\leq$ $p_{T}(\gamma)$ $<$ 160 GeV",
            "ZG+WG4p, e, $p_{T}(\gamma)$ $\geq$ 160 GeV",
            "ZG4p, $\mu$, 20 $\leq$ $p_{T}(\gamma)$ $<$ 65 GeV",
            "WG4p, $\mu$, 20 $\leq$ $p_{T}(\gamma)$ $<$ 65 GeV",
            "ZG4p, $\mu$, 65 $\leq$ $p_{T}(\gamma)$ $<$ 160 GeV",
            "WG4p, $\mu$, 65 $\leq$ $p_{T}(\gamma)$ $<$ 160 GeV",
            "ZG+WG4p, $\mu$, $p_{T}(\gamma)$ $\geq$ 160 GeV",
            "misDY3, e, 20 $\leq$ $p_{T}(\gamma)$ $<$ 35 GeV",
            "misDY3, e, 35 $\leq$ $p_{T}(\gamma)$ $<$ 50 GeV",
            "misDY3, e, 50 $\leq$ $p_{T}(\gamma)$ $<$ 65 GeV",
            "misDY3, e, 65 $\leq$ $p_{T}(\gamma)$ $<$ 80 GeV",
            "misDY3, e, 80 $\leq$ $p_{T}(\gamma)$ $<$ 120 GeV",
            "misDY3, e, 120 $\leq$ $p_{T}(\gamma)$ $<$ 160 GeV",
            "misDY3, e, $p_{T}(\gamma)$ $\geq$ 160 GeV",
            "misDY4p, e, 20 $\leq$ $p_{T}(\gamma)$ $<$ 35 GeV",
            "misDY4p, e, 35 $\leq$ $p_{T}(\gamma)$ $<$ 50 GeV",
            "misDY4p, e, 50 $\leq$ $p_{T}(\gamma)$ $<$ 65 GeV",
            "misDY4p, e, 65 $\leq$ $p_{T}(\gamma)$ $<$ 80 GeV",
            "misDY4p, e, 80 $\leq$ $p_{T}(\gamma)$ $<$ 120 GeV",
            "misDY4p, e, 160 $\leq$ $p_{T}(\gamma)$ $<$ 160 GeV",
            "misDY4p, e, $p_{T}(\gamma)$ $\geq$ 160 GeV",
            ]
    xbins = Variable( "Bin", is_independent=True, is_binned=False)
    xbins.values = crBinLabel
    ydata = Variable( "Observed", is_independent=False, is_binned=False)
    ydata.values = data["y"]
    ydata.add_qualifier("SQRT(S)","13","TeV")
    ydata.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    ytot = Variable( "Total simulation", is_independent=False, is_binned=False)
    ytot.values = tot["y"]
    ytot.add_qualifier("SQRT(S)","13","TeV")
    ytot.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    ytotbkg = Variable( "Total background", is_independent=False, is_binned=False)
    ytotbkg.values = totbkg["y"]
    ytotbkg.add_qualifier("SQRT(S)","13","TeV")
    ytotbkg.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    ywg = Variable( "$W\gamma$", is_independent=False, is_binned=False)
    ywg.values = wg["y"]
    ywg.add_qualifier("SQRT(S)","13","TeV")
    ywg.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    yzg = Variable( "$Z\gamma$", is_independent=False, is_binned=False)
    yzg.values = zg["y"]
    yzg.add_qualifier("SQRT(S)","13","TeV")
    yzg.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    ymisID = Variable( "Misid. e", is_independent=False, is_binned=False)
    ymisID.values = misID["y"]
    ymisID.add_qualifier("SQRT(S)","13","TeV")
    ymisID.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    yhad = Variable( "Hadronic $\gamma$", is_independent=False, is_binned=False)
    yhad.values = had["y"]
    yhad.add_qualifier("SQRT(S)","13","TeV")
    yhad.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    yqcd = Variable( "Multijet", is_independent=False, is_binned=False)
    yqcd.values = qcd["y"]
    yqcd.add_qualifier("SQRT(S)","13","TeV")
    yqcd.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    yttg = Variable( "tt$\gamma$", is_independent=False, is_binned=False)
    yttg.values = ttg["y"]
    yttg.add_qualifier("SQRT(S)","13","TeV")
    yttg.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    yother = Variable( "Other", is_independent=False, is_binned=False)
    yother.values = other["y"]
    yother.add_qualifier("SQRT(S)","13","TeV")
    yother.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    yunc = Variable( "Total uncertainty", is_independent=False, is_binned=False)
    yunc.values = unc
    yunc.add_qualifier("SQRT(S)","13","TeV")
    yunc.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    #yrelunc = Variable( "Rel. uncertainty (%)", is_independent=False, is_binned=False)
    #yrelunc.values = relunc

    tab.add_variable(xbins)
    tab.add_variable(ydata)
    tab.add_variable(ytot)
    tab.add_variable(ytotbkg)
    tab.add_variable(ywg)
    tab.add_variable(yzg)
    tab.add_variable(ymisID)
    tab.add_variable(yhad)
    tab.add_variable(yqcd)
    tab.add_variable(yttg)
    tab.add_variable(yother)
    tab.add_variable(yunc)

    return tab




def convertSRPlotToYaml():

    tab = Table("Figure 6")

    reader = RootFileReader("../regionPlots/SR_incl.root")

    data = reader.read_hist_1d("0dc_2016data")
    tot = reader.read_hist_1d("0dc_2016total")
    totbkg = reader.read_hist_1d("0dc_2016total_background")
    ttg = reader.read_hist_1d("0dc_2016signal")
    misID = reader.read_hist_1d("0dc_2016misID")
    had = reader.read_hist_1d("0dc_2016fakes")
    other = reader.read_hist_1d("0dc_2016other")
    wg = reader.read_hist_1d("0dc_2016WG")
    qcd = reader.read_hist_1d("0dc_2016QCD")
    zg = reader.read_hist_1d("0dc_2016ZG")

    rootfile = ROOT.TFile("../regionPlots/SR_incl.root","READ")
    totHist = rootfile.Get("0dc_2016total")

    unc = []
    relunc = []
    for i, i_tot in enumerate(tot["y"]):
        u = totHist.GetBinError(i+1)
        unc.append(u)
        relunc.append(u*100./i_tot)

    crBinLabel = [
            "SR3, e, $M_{3}$ $<$ 280 GeV",
            "SR3, e, 280 $\leq$ $M_{3}$ $<$ 420 GeV",
            "SR3, e, $M_{3}$ $\geq$ 420 GeV",
            "SR3, $\mu$, $M_{3}$ $<$ 280 GeV",
            "SR3, $\mu$, 280 $\leq$ $M_{3}$ $<$ 420 GeV",
            "SR3, $\mu$, $M_{3}$ $\geq$ 420 GeV",
            "SR4p, e, $M_{3}$ $<$ 280 GeV",
            "SR4p, e, 280 $\leq$ $M_{3}$ $<$ 420 GeV",
            "SR4p, e, $M_{3}$ $\geq$ 420 GeV",
            "SR4p, $\mu$, $M_{3}$ $<$ 280 GeV",
            "SR4p, $\mu$, 280 $\leq$ $M_{3}$ $<$ 420 GeV",
            "SR4p, $\mu$, $M_{3}$ $\geq$ 420 GeV",
            ]
    xbins = Variable( "Bin", is_independent=True, is_binned=False)
    xbins.values = crBinLabel
    ydata = Variable( "Observed", is_independent=False, is_binned=False)
    ydata.values = data["y"]
    ydata.add_qualifier("SQRT(S)","13","TeV")
    ydata.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    ytot = Variable( "Total simulation", is_independent=False, is_binned=False)
    ytot.values = tot["y"]
    ytot.add_qualifier("SQRT(S)","13","TeV")
    ytot.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    ytotbkg = Variable( "Total background", is_independent=False, is_binned=False)
    ytotbkg.values = totbkg["y"]
    ytotbkg.add_qualifier("SQRT(S)","13","TeV")
    ytotbkg.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    ywg = Variable( "$W\gamma$", is_independent=False, is_binned=False)
    ywg.values = wg["y"]
    ywg.add_qualifier("SQRT(S)","13","TeV")
    ywg.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    yzg = Variable( "$Z\gamma$", is_independent=False, is_binned=False)
    yzg.values = zg["y"]
    yzg.add_qualifier("SQRT(S)","13","TeV")
    yzg.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    ymisID = Variable( "Misid. e", is_independent=False, is_binned=False)
    ymisID.values = misID["y"]
    ymisID.add_qualifier("SQRT(S)","13","TeV")
    ymisID.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    yhad = Variable( "Hadronic $\gamma$", is_independent=False, is_binned=False)
    yhad.values = had["y"]
    yhad.add_qualifier("SQRT(S)","13","TeV")
    yhad.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    yqcd = Variable( "Multijet", is_independent=False, is_binned=False)
    yqcd.values = qcd["y"]
    yqcd.add_qualifier("SQRT(S)","13","TeV")
    yqcd.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    yttg = Variable( "tt$\gamma$", is_independent=False, is_binned=False)
    yttg.values = ttg["y"]
    yttg.add_qualifier("SQRT(S)","13","TeV")
    yttg.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    yother = Variable( "Other", is_independent=False, is_binned=False)
    yother.values = other["y"]
    yother.add_qualifier("SQRT(S)","13","TeV")
    yother.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    yunc = Variable( "Total uncertainty", is_independent=False, is_binned=False)
    yunc.values = unc
    yunc.add_qualifier("SQRT(S)","13","TeV")
    yunc.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    #yrelunc = Variable( "Rel. uncertainty (%)", is_independent=False, is_binned=False)
    #yrelunc.values = relunc

    tab.add_variable(xbins)
    tab.add_variable(ydata)
    tab.add_variable(ytot)
    tab.add_variable(ytotbkg)
    tab.add_variable(yttg)
    tab.add_variable(ymisID)
    tab.add_variable(yhad)
    tab.add_variable(yother)
    tab.add_variable(ywg)
    tab.add_variable(yqcd)
    tab.add_variable(yzg)
    tab.add_variable(yunc)

    return tab



def convertCovMatrixToYaml( rootfile, label, variable, unit ):

    tab = Table(label)

    reader = RootFileReader(rootfile)

    cov = reader.read_hist_2d("output_covMatrix")

    xbins = Variable( variable, is_independent=True, is_binned=True, units=unit)
    xbins.values = cov["x_edges"]
    ybins = Variable( variable, is_independent=True, is_binned=True, units=unit)
    ybins.values = cov["y_edges"]

    data = Variable( "Covariance", is_independent=False, is_binned=False, units="events$^2$")
    data.values = [abs(z) for z in cov["z"]]
    data.add_qualifier("SQRT(S)","13","TeV")
    data.add_qualifier("LUMINOSITY","137","fb$^{-1}$")

    tab.add_variable(xbins)
    tab.add_variable(ybins)
    tab.add_variable(data)

    return tab




def convertUnfoldingHistToYaml( rootfile, label, variable, unit ):

    tab = Table(label)

    reader = RootFileReader(rootfile)

    data = reader.read_hist_1d("unfoled_spectrum")
    simP8 = reader.read_hist_1d("fiducial_spectrum")
    simHpp = reader.read_hist_1d("fiducial_spectrum_Hpp")
    simH7 = reader.read_hist_1d("fiducial_spectrum_H7")
    totalUncUp = reader.read_hist_1d("totalUncertainty_up")
    totalUncDown = reader.read_hist_1d("totalUncertainty_down")
    statUncUp = reader.read_hist_1d("totalUncertaintySource_up")
    statUncDown = reader.read_hist_1d("totalUncertaintySource_down")

    totunc = []
    reltotunc = []
    statunc = []
    relstatunc = []
    for i, i_up in enumerate(totalUncUp["y"]):
        utot = abs(i_up-totalUncDown["y"][i])*0.5
        ustat = abs(statUncUp["y"][i]-statUncDown["y"][i])*0.5
        tot = data["y"][i]
        totunc.append(utot)
        statunc.append(ustat)
        reltotunc.append(utot*100./tot)
        relstatunc.append(ustat*100./tot)

    xbins = Variable( variable, is_independent=True, is_binned=True, units=unit)
    xbins.values = data["x_edges"]
    ydata = Variable( "Observed", is_independent=False, is_binned=False)
    ydata.values = data["y"]
    ydata.add_qualifier("SQRT(S)","13","TeV")
    ydata.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    ysimP8 = Variable( "Simulation MG5_aMC + Pythia8", is_independent=False, is_binned=False)
    ysimP8.values = simP8["y"]
    ysimP8.add_qualifier("SQRT(S)","13","TeV")
    ysimP8.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    ysimH7 = Variable( "Simulation MG5_aMC + Herwig7", is_independent=False, is_binned=False)
    ysimH7.values = simH7["y"]
    ysimH7.add_qualifier("SQRT(S)","13","TeV")
    ysimH7.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    ysimHpp = Variable( "Simulation MG5_aMC + Herwig++", is_independent=False, is_binned=False)
    ysimHpp.values = simHpp["y"]
    ysimHpp.add_qualifier("SQRT(S)","13","TeV")
    ysimHpp.add_qualifier("LUMINOSITY","137","fb$^{-1}$")

    ytotunc = Variable( "Total uncertainty", is_independent=False, is_binned=False)
    ytotunc.values = totunc
    ytotunc.add_qualifier("SQRT(S)","13","TeV")
    ytotunc.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    ystatunc = Variable( "Stat. uncertainty", is_independent=False, is_binned=False)
    ystatunc.values = statunc
    ystatunc.add_qualifier("SQRT(S)","13","TeV")
    ystatunc.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
    #yrelunc = Variable( "Rel. uncertainty (%)", is_independent=False, is_binned=False)
    #yrelunc.values = relunc

    tab.add_variable(xbins)
    tab.add_variable(ydata)
    tab.add_variable(ysimP8)
    tab.add_variable(ysimH7)
    tab.add_variable(ysimHpp)
    tab.add_variable(ystatunc)
    tab.add_variable(ytotunc)

    return tab

