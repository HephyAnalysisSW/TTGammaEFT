import numpy as np
from hepdata_lib import Submission, Table, Variable, RootFileReader, Uncertainty
from helpers import *

submission = Submission()

###
### Fig 2a
###

tableF2a = convertSRHistToYaml("../systPlots/SR3p_PhotonGood0_pt_all.root", "Figure 2a", "$p_{T}(\gamma)$", "GeV")
tableF2a.description = "Distribution of $p_{T}(\gamma)$ in the SR3p signal region."
tableF2a.location = "Data from Figure 2 (top left) "
tableF2a.add_image("../figures/PhotonGood0_pt.png")
tableF2a.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tableF2a.keywords["cmenergies"] = [13000.0]
tableF2a.keywords["observables"] = ["N"]
tableF2a.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
submission.add_table(tableF2a)


###
### Fig 2b
###

tableF2b = convertSRHistToYaml("../systPlots/SR3p_mT_all.root", "Figure 2b", "$m_{T}(W)$", "GeV")
tableF2b.description = "Distribution of $m_{T}(W)$ in the SR3p signal region."
tableF2b.location = "Data from Figure 2 (top center)"
tableF2b.add_image("../figures/mT.png")
tableF2b.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tableF2b.keywords["cmenergies"] = [13000.0]
tableF2b.keywords["observables"] = ["N"]
tableF2b.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
#tableF2b.keywords()
submission.add_table(tableF2b)


###
### Fig 2c
###

tableF2c = convertSRHistToYaml("../systPlots/SR3p_m3_all.root", "Figure 2c", "$M_{3}$", "GeV")
tableF2c.description = "Distribution of $M_{3}$ in the SR3p signal region."
tableF2c.location = "Data from Figure 2 (top right)"
tableF2c.add_image("../figures/m3.png")
tableF2c.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tableF2c.keywords["cmenergies"] = [13000.0]
tableF2c.keywords["observables"] = ["N"]
tableF2c.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
#tableF2c.keywords()
submission.add_table(tableF2c)


###
### Fig 2d
###

tableF2d = convertSRHistToYaml("../systPlots/SR3p_mLtight0Gamma_all.root", "Figure 2d", "$m(l,\gamma)$", "GeV")
tableF2d.description = "Distribution of $m(l,\gamma)$ in the SR3p signal region."
tableF2d.location = "Data from Figure 2 (bottom left)"
tableF2d.add_image("../figures/mLtight0Gamma.png")
tableF2d.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tableF2d.keywords["cmenergies"] = [13000.0]
tableF2d.keywords["observables"] = ["N"]
tableF2d.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
#tableF2d.keywords()
submission.add_table(tableF2d)


###
### Fig 2e
###

tableF2e = convertSRHistToYaml("../systPlots/SR3p_ltight0GammadR_all.root", "Figure 2e", "$\Delta R(l,\gamma)$", "")
tableF2e.description = "Distribution of $\Delta R(l,\gamma)$ in the SR3p signal region."
tableF2e.location = "Data from Figure 2 (bottom center)"
tableF2e.add_image("../figures/ltight0GammadR.png")
tableF2e.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tableF2e.keywords["cmenergies"] = [13000.0]
tableF2e.keywords["observables"] = ["N"]
tableF2e.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
#tableF2e.keywords()
submission.add_table(tableF2e)


###
### Fig 2f
###

tableF2f = convertSRHistToYaml("../systPlots/SR3p_photonJetdR_all.root", "Figure 2f", "$\Delta R(j,\gamma)$", "")
tableF2f.description = "Distribution of $\Delta R(j,\gamma)$ in the SR3p signal region."
tableF2f.location = "Data from Figure 2 (bottom right)"
tableF2f.add_image("../figures/photonJetdR.png")
tableF2f.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tableF2f.keywords["cmenergies"] = [13000.0]
tableF2f.keywords["observables"] = ["N"]
tableF2f.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
#tableF2f.keywords()
submission.add_table(tableF2f)


###
### Fig 3a
###

tableF3a = convertWJetsHistToYaml("../systPlots/WJets2_mT_e.root", "Figure 3a", "e+jets")
tableF3a.description = "Fit result of the multijet template obtained with loosely isolated leptons and the electroweak background to the measured $m_{T}(W)$ distribution with isolated leptons in the $N_{jet}=2$, $N_{b jet}=0$ selection for electrons."
tableF3a.location = "Data from Figure 3 (left)"
tableF3a.add_image("../figures/mT_e.png")
tableF3a.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tableF3a.keywords["cmenergies"] = [13000.0]
tableF3a.keywords["observables"] = ["N"]
tableF3a.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
#tableF3a.keywords()
submission.add_table(tableF3a)


###
### Fig 3b
###

tableF3b = convertWJetsHistToYaml("../systPlots/WJets2_mT_mu.root", "Figure 3b", "$\mu$+jets")
tableF3b.description = "Fit result of the multijet template obtained with loosely isolated leptons and the electroweak background to the measured $m_{T}(W)$ distribution with isolated leptons in the $N_{jet}=2$, $N_{b jet}=0$ selection for muons."
tableF3b.location = "Data from Figure 3 (right)"
tableF3b.add_image("../figures/mT_mu.png")
tableF3b.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tableF3b.keywords["cmenergies"] = [13000.0]
tableF3b.keywords["observables"] = ["N"]
tableF3b.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
#tableF3b.keywords()
submission.add_table(tableF3b)


###
### Fig 4a
###

tableF4a = convertMlgHistToYaml("../systPlots/VGmis3p_mLtight0Gamma_e.root", "Figure 4a", "$m(e,\gamma)$", "e+jets")
tableF4a.description = "Distribution of the invariant mass of the lepton and the photon ($m(l,\gamma)$) in the $N_{jet}\geq 3$, $N_{b jet}=0$ selection for the e channel."
tableF4a.location = "Data from Figure 4 (left)"
tableF4a.add_image("../figures/mLtight0Gamma_e.png")
tableF4a.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tableF4a.keywords["cmenergies"] = [13000.0]
tableF4a.keywords["observables"] = ["N"]
tableF4a.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
#tableF4a.keywords()
submission.add_table(tableF4a)


###
### Fig 4b
###

tableF4b = convertMlgHistToYaml("../systPlots/VGmis3p_mLtight0Gamma_mu.root", "Figure 4b", "$m(\mu,\gamma)$", "$\mu$+jets")
tableF4b.description = "Distribution of the invariant mass of the lepton and the photon ($m(l,\gamma)$) in the $N_{jet}\geq 3$, $N_{b jet}=0$ selection for the $\mu$ channel."
tableF4b.location = "Data from Figure 4 (right)"
tableF4b.add_image("../figures/mLtight0Gamma_mu.png")
tableF4b.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tableF4b.keywords["cmenergies"] = [13000.0]
tableF4b.keywords["observables"] = ["N"]
tableF4b.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
#tableF4b.keywords()
submission.add_table(tableF4b)


###
### SF table
###
tabSF = Table("Table 4")

tabSF.description = "Extracted scale factors for the contribution from misidentified electrons for the three data-taking periods, and the Z$\gamma$, W$\gamma$ simulations."
tabSF.location = "Table 4"

sfType = Variable( "Scale factor", is_independent=True, is_binned=False, units="")
sfType.values = ["Misidentified electrons 2016", "Misidentified electrons 2017", "Misidentified electrons 2018", "Z$\gamma$ normalization", "W$\gamma$ normalization"]
value     = Variable( "Value", is_independent=False, is_binned=False, units="")
value.values = [2.22, 1.83, 1.59, 0.83, 1.2]
value.add_qualifier("SQRT(S)","13","TeV")
value.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
unc = Uncertainty( "total" )
unc.is_symmetric = True
unc.values = [0.28, 0.24, 0.18, 0.10, 0.09]
value.uncertainties.append( unc )

tabSF.add_variable(sfType)
tabSF.add_variable(value)

tabSF.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tabSF.keywords["cmenergies"] = [13000.0]
tabSF.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
submission.add_table(tabSF)


###
### Fig 5
###

tableF5 = convertCRPlotToYaml()
tableF5.description = "Predicted and observed yields in the control regions in the $N_{jet}= 3$ and $\geq 4$ seletions using the post-fit values of the nuisance parameters."
tableF5.location = "Data from Figure 5"
tableF5.add_image("../figures/regions_VG3e_VG3mu_VG4pe_VG4pmu_misDY3_misDY4p.png")
#tableF5.keywords()
tableF5.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tableF5.keywords["cmenergies"] = [13000.0]
tableF5.keywords["observables"] = ["N"]
tableF5.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
submission.add_table(tableF5)


###
### Fig 6
###

tableF6 = convertSRPlotToYaml()
tableF6.description = "Predicted and observed yields in the signal regions in the $N_{jet}= 3$ and $\geq 4$ seletions using the post-fit values of the nuisance parameters."
tableF6.location = "Data from Figure 6"
tableF6.add_image("../figures/regions_SR3eM3_SR3muM3_SR4peM3_SR4pmuM3.png")
#tableF6.keywords()
tableF6.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tableF6.keywords["cmenergies"] = [13000.0]
tableF6.keywords["observables"] = ["N"]
tableF6.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
submission.add_table(tableF6)


###
### inclusive cross section
###
tabXSec = Table("Equation 2")

tabXSec.description = "The measured inclusive ttgamma cross section in the fiducial phase space compared to the prediction from simulation using Madgraph_aMC@NLO at a center-of-mass energy of 13 TeV."
tabXSec.location = "Equation 2"

data = np.loadtxt("../xsec/xsec.txt", skiprows=1, dtype=int)

xsecType = Variable( "", is_independent=True, is_binned=False, units="")
xsecType.values = ["Experimental", "Theoretical (MG5_aMC@NLO + Pythia8)"]
xsec     = Variable( "Cross section", is_independent=False, is_binned=False, units="fb")
xsec.values = [str(int(data[0][0])), str(int(data[1][0]))]
xsec.add_qualifier("CHANNEL","l+jets")
xsec.add_qualifier("SQRT(S)","13","TeV")
xsec.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
tot     = Variable( "Total uncertainty", is_independent=False, is_binned=False, units="fb")
tot.values = ["$\pm$"+str(int(data[0][1])), "$\pm$"+str(int(data[1][1]))]
tot.add_qualifier("CHANNEL","l+jets")
tot.add_qualifier("SQRT(S)","13","TeV")
tot.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
stat     = Variable( "Stat. uncertainty", is_independent=False, is_binned=False, units="fb")
stat.values = ["$\pm$"+str(int(data[0][2])), ""]
stat.add_qualifier("CHANNEL","l+jets")
stat.add_qualifier("SQRT(S)","13","TeV")
stat.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
syst     = Variable( "Syst. uncertainty", is_independent=False, is_binned=False, units="fb")
syst.values = ["$\pm$"+str(int(data[0][3])), ""]
syst.add_qualifier("CHANNEL","l+jets")
syst.add_qualifier("SQRT(S)","13","TeV")
syst.add_qualifier("LUMINOSITY","137","fb$^{-1}$")

tabXSec.add_variable(xsecType)
tabXSec.add_variable(xsec)
tabXSec.add_variable(tot)
tabXSec.add_variable(stat)
tabXSec.add_variable(syst)

tabXSec.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tabXSec.keywords["cmenergies"] = [13000.0]
tabXSec.keywords["observables"] = ["SIG"]
tabXSec.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
submission.add_table(tabXSec)


###
### SSM
###
tabssm = Table("Figure 7")

tabssm.description = "Summary of the measured cross section ratios with respect to the NLO cross section prediction for signal regions binned in the electron channel, muon channel and the combined single lepton measurement."
tabssm.location = "Data from Figure 7"

datassm = np.loadtxt("../xsec/ssm.txt", skiprows=1)

ssmType = Variable( "Channel", is_independent=True, is_binned=False)
ssmType.values = ["e+jets", "$\mu$+jets", "l+jets"]
ssm     = Variable( "$\sigma/\sigma_{NLO}$", is_independent=False, is_binned=False)
ssm.values = ["%.3f"%datassm[0][0], "%.3f"%datassm[1][0], "%.3f"%datassm[2][0]]
ssm.add_qualifier("SQRT(S)","13","TeV")
ssm.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
tot     = Variable( "Total uncertainty", is_independent=False, is_binned=False)
tot.values = ["$^{+%.3f}_{%.3f}$"%(datassm[0][1],datassm[0][2]), "$^{+%.3f}_{%.3f}$"%(datassm[1][1],datassm[1][2]), "$^{+%.3f}_{%.3f}$"%(datassm[2][1],datassm[2][2])]
tot.add_qualifier("SQRT(S)","13","TeV")
tot.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
stat     = Variable( "Stat. uncertainty", is_independent=False, is_binned=False)
stat.values = ["$\pm$%.3f"%datassm[0][3], "$\pm$%.3f"%datassm[1][3], "$\pm$%.3f"%datassm[2][3]]
stat.add_qualifier("SQRT(S)","13","TeV")
stat.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
syst     = Variable( "Syst. uncertainty", is_independent=False, is_binned=False)
syst.values = ["$^{+%.3f}_{%.3f}$"%(datassm[0][4],datassm[0][5]), "$^{+%.3f}_{%.3f}$"%(datassm[1][4],datassm[1][5]), "$^{+%.3f}_{%.3f}$"%(datassm[2][4],datassm[2][5])]
syst.add_qualifier("SQRT(S)","13","TeV")
syst.add_qualifier("LUMINOSITY","137","fb$^{-1}$")

tabssm.add_variable(ssmType)
tabssm.add_variable(ssm)
tabssm.add_variable(tot)
tabssm.add_variable(stat)
tabssm.add_variable(syst)

tabssm.add_image("../figures/summaryResult.png")
#tablessm.keywords()

tabssm.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tabssm.keywords["cmenergies"] = [13000.0]
tabssm.keywords["observables"] = ["SIG/SIG"]
tabssm.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
submission.add_table(tabssm)


###
### Fig 8a
###

tableUnfPt = convertUnfoldingHistToYaml( "../unfolding/unfolded_observed_ptG_RunII.root", "Figure 8a", "$p_{T}(\gamma)$", "GeV" )
tableUnfPt.description = "The unfolded differential cross sections for $p_{T}(\gamma)$ and the comparison to simulations."
tableUnfPt.location = "Data from Figure 8 (top left)"
tableUnfPt.add_image("../figures/unfolded_spectrum_fromSyst_log_ptg.png")
#tableUnfPt.keywords()
tableUnfPt.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tableUnfPt.keywords["cmenergies"] = [13000.0]
tableUnfPt.keywords["observables"] = ["N"]
tableUnfPt.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
submission.add_table(tableUnfPt)


###
### Fig 8b
###

tableUnfEta = convertUnfoldingHistToYaml( "../unfolding/unfolded_observed_absEta_RunII.root", "Figure 8b", "$|\eta(\gamma)|$", "" )
tableUnfEta.description = "The unfolded differential cross sections for $|\eta(\gamma)|$ and the comparison to simulations."
tableUnfEta.location = "Data from Figure 8 (top right)"
tableUnfEta.add_image("../figures/unfolded_spectrum_fromSyst_eta.png")
#tableUnfEta.keywords()
tableUnfEta.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tableUnfEta.keywords["cmenergies"] = [13000.0]
tableUnfEta.keywords["observables"] = ["N"]
tableUnfEta.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
submission.add_table(tableUnfEta)


###
### Fig 8c
###

tableUnfdR = convertUnfoldingHistToYaml( "../unfolding/unfolded_observed_dRlg_RunII.root", "Figure 8c", "$\Delta R(l,\gamma)$", "" )
tableUnfdR.description = "The unfolded differential cross sections for $\Delta R(l,\gamma)$ and the comparison to simulations."
tableUnfdR.location = "Data from Figure 8 (bottom)"
tableUnfdR.add_image("../figures/unfolded_spectrum_fromSyst_dR.png")
#tableUnfdR.keywords()
tableUnfdR.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tableUnfdR.keywords["cmenergies"] = [13000.0]
tableUnfdR.keywords["observables"] = ["N"]
tableUnfdR.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
submission.add_table(tableUnfdR)


###
### Covmatrix pt
###

tableCov = convertCovMatrixToYaml("../unfolding/covMatrix_observed_ptG_RunII.root", "Covariance matrix $p_{T}(\gamma)$", "$p_{T}(\gamma)$", "$p_{T}(\gamma)$ ", "GeV")
tableCov.description = "The covariance matrix of the unfolded differential measurement for $p_{T}(\gamma)$."
tableCov.location = "Additional material: Covariance matrix to Figure 9 (top left)"
tableCov.add_image("../figures/covMatrix_ptg.png")
#tableCov.keywords()
tableCov.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tableCov.keywords["cmenergies"] = [13000.0]
tableCov.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
submission.add_table(tableCov)


###
### Covmatrix eta
###

tableCovEta = convertCovMatrixToYaml("../unfolding/covMatrix_observed_absEta_RunII.root", "Covariance matrix $|\eta(\gamma)|$", "$|\eta(\gamma)|$", "$|\eta(\gamma)|$ ", "")
tableCovEta.description = "The covariance matrix of the unfolded differential measurement for $|\eta(\gamma)|$."
tableCovEta.location = "Additional material: Covariance matrix to Figure 9 (top right)"
tableCovEta.add_image("../figures/covMatrix_eta.png")
#tableCovEta.keywords()
tableCovEta.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tableCovEta.keywords["cmenergies"] = [13000.0]
tableCovEta.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
submission.add_table(tableCovEta)


###
### Covmatrix dR
###

tableCovdR = convertCovMatrixToYaml("../unfolding/covMatrix_observed_dRlg_RunII.root", "Covariance matrix $\Delta R(l,\gamma)$", "$\Delta R(l,\gamma)$", "$\Delta R(l,\gamma)$ ", "")
tableCovdR.description = "The covariance matrix of the unfolded differential measurement for $\Delta R(l,\gamma)$."
tableCovdR.location = "Additional material: Covariance matrix to Figure 9 (bottom)"
tableCovdR.add_image("../figures/covMatrix_dR.png")
#tableCovdR.keywords()
tableCovdR.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tableCovdR.keywords["cmenergies"] = [13000.0]
tableCovdR.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
submission.add_table(tableCovdR)


###
### Fig 9a
###

tableCorr = convertCorrMatrixToYaml("../unfolding/corrMatrix_observed_ptG_RunII.root", "Figure 9a", "$p_{T}(\gamma)$", "$p_{T}(\gamma)$ ", "GeV")
tableCorr.description = "The correlation matrix of the unfolded differential measurement for $p_{T}(\gamma)$."
tableCorr.location = "Data from Figure 9 (top left)"
tableCorr.add_image("../figures/corrMatrix_ptg.png")
#tableCorr.keywords()
tableCorr.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tableCorr.keywords["cmenergies"] = [13000.0]
tableCorr.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
submission.add_table(tableCorr)


###
### Fig 9b
###

tableCorrEta = convertCorrMatrixToYaml("../unfolding/corrMatrix_observed_absEta_RunII.root", "Figure 9b", "$|\eta(\gamma)|$", "$|\eta(\gamma)|$ ", "")
tableCorrEta.description = "The correlation matrix of the unfolded differential measurement for $|\eta(\gamma)|$."
tableCorrEta.location = "Data from Figure 9 (top right)"
tableCorrEta.add_image("../figures/corrMatrix_eta.png")
#tableCorrEta.keywords()
tableCorrEta.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tableCorrEta.keywords["cmenergies"] = [13000.0]
tableCorrEta.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
submission.add_table(tableCorrEta)


###
### Fig 9c
###

tableCorrdR = convertCorrMatrixToYaml("../unfolding/corrMatrix_observed_dRlg_RunII.root", "Figure 9c", "$\Delta R(l,\gamma)$", "$\Delta R(l,\gamma)$ ", "")
tableCorrdR.description = "The correlation matrix of the unfolded differential measurement for $\Delta R(l,\gamma)$."
tableCorrdR.location = "Data from Figure 9 (bottom)"
tableCorrdR.add_image("../figures/corrMatrix_dR.png")
#tableCorrdR.keywords()
tableCorrdR.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tableCorrdR.keywords["cmenergies"] = [13000.0]
tableCorrdR.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
submission.add_table(tableCorrdR)


###
### EFT interval
###
tabcl = Table("Table 7")

tabcl.description = "Summary of the one-dimensional intervals at 68 and 95% CL."
tabcl.location = "Table 7"

clType = Variable( "Wilson coefficient", is_independent=True, is_binned=False)
clType.values = ["$c_{tZ}$ (expected)", "$c^{I}_{tZ}$ (expected)", "$c_{tZ}$ (observed)", "$c^{I}_{tZ}$ (observed)"]
cl68     = Variable( "68% CL interval", is_independent=False, is_binned=False)
cl68.values = ["[-0.19, 0.21]", "[-0.20, 0.20]", "[-0.35, -0.16]", "[-0.35, -0.16], [0.17, 0.35]"]
cl68.add_qualifier("SQRT(S)","13","TeV")
cl68.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
cl95     = Variable( "95% CL interval", is_independent=False, is_binned=False)
cl95.values = ["[-0.29, 0.32]", "[-0.30, 0.31]", "[-0.42, 0.38]", "[-0.42, 0.42]"]
cl95.add_qualifier("SQRT(S)","13","TeV")
cl95.add_qualifier("LUMINOSITY","137","fb$^{-1}$")

tabcl.add_variable(clType)
tabcl.add_variable(cl68)
tabcl.add_variable(cl95)

tabcl.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tabcl.keywords["cmenergies"] = [13000.0]
tabcl.keywords["observables"] = ["CLS"]
tabcl.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
submission.add_table(tabcl)



###
### EFT 1D
###
tabctZ = Table("Figure 10a")

tabctZ.description = "Negative log-likelihood ratio values with respect to the best fit value of the one-dimensional scan for the Wilson coefficient $c_{tZ}$."
tabctZ.location = "Data from Figure 10 (top left)"

datactZexp = np.loadtxt("../eft/ctZ_1D_exp.dat", skiprows=1)
datactZobs = np.loadtxt("../eft/ctZ_1D_obs.dat", skiprows=1)

wcctZ     = Variable( "$c_{tZ}$", is_independent=True, is_binned=False, units="$\Lambda$/TeV$^2$")
wcctZ.values = datactZobs[:,0]
nllctZexp     = Variable( "-2$\Delta$ L (expected)", is_independent=False, is_binned=False)
nllctZexp.values = datactZexp[:,1]
nllctZexp.add_qualifier("SQRT(S)","13","TeV")
nllctZexp.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
nllctZobs     = Variable( "-2$\Delta$ L (observed)", is_independent=False, is_binned=False)
nllctZobs.values = datactZobs[:,1]
nllctZobs.add_qualifier("SQRT(S)","13","TeV")
nllctZobs.add_qualifier("LUMINOSITY","137","fb$^{-1}$")

tabctZ.add_variable(wcctZ)
tabctZ.add_variable(nllctZexp)
tabctZ.add_variable(nllctZobs)

tabctZ.add_image("../figures/ctZ_wExp_wBkg.png")
#tabctZ.keywords()
tabctZ.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tabctZ.keywords["cmenergies"] = [13000.0]
tabctZ.keywords["observables"] = ["CLS"]
tabctZ.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
submission.add_table(tabctZ)


###
### EFT 1D
###
tabctZI = Table("Figure 10b")

tabctZI.description = "Negative log-likelihood ratio values with respect to the best fit value of the one-dimensional scan for the Wilson coefficient $c^{I}_{tZ}$."
tabctZI.location = "Data from Figure 10 (top right)"

datactZIexp = np.loadtxt("../eft/ctZI_1D_exp.dat", skiprows=1)
datactZIobs = np.loadtxt("../eft/ctZI_1D_obs.dat", skiprows=1)

wcctZI     = Variable( "$c^{I}_{tZ}$", is_independent=True, is_binned=False, units="$\Lambda$/TeV$^2$")
wcctZI.values = datactZIobs[:,0]
nllctZIexp     = Variable( "-2$\Delta$ L (expected)", is_independent=False, is_binned=False)
nllctZIexp.values = datactZIexp[:,1]
nllctZIexp.add_qualifier("SQRT(S)","13","TeV")
nllctZIexp.add_qualifier("LUMINOSITY","137","fb$^{-1}$")
nllctZIobs     = Variable( "-2$\Delta$ L (observed)", is_independent=False, is_binned=False)
nllctZIobs.values = datactZIobs[:,1]
nllctZIobs.add_qualifier("SQRT(S)","13","TeV")
nllctZIobs.add_qualifier("LUMINOSITY","137","fb$^{-1}$")

tabctZI.add_variable(wcctZI)
tabctZI.add_variable(nllctZIexp)
tabctZI.add_variable(nllctZIobs)

tabctZI.add_image("../figures/ctZI_wExp_wBkg.png")
#tabctZI.keywords()
tabctZI.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tabctZI.keywords["cmenergies"] = [13000.0]
tabXSec.keywords["observables"] = ["CLS"]
tabXSec.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
submission.add_table(tabctZI)


###
### EFT 2D
###
tabctZctZI = Table("Figure 10c")

tabctZctZI.description = "Negative log-likelihood ratio values with respect to the best fit value of the two-dimensional scan for the Wilson coefficients $c_{tZ}$ and $c^{I}_{tZ}$."
tabctZctZI.location = "Data from Figure 10 (bottom)"

datactZctZIobs = np.loadtxt("../eft/ctZ_ctZI_2D_obs.dat", skiprows=1)

wcctZ     = Variable( "$c_{tZ}$", is_independent=True, is_binned=False, units="$\Lambda$/TeV$^2$")
wcctZ.values = datactZctZIobs[:,0]
wcctZI     = Variable( "$c^{I}_{tZ}$", is_independent=True, is_binned=False, units="$\Lambda$/TeV$^2$")
wcctZI.values = datactZctZIobs[:,1]
nllctZctZIobs     = Variable( "-2$\Delta$ L (observed)", is_independent=False, is_binned=False)
nllctZctZIobs.values = datactZctZIobs[:,2]
nllctZctZIobs.add_qualifier("SQRT(S)","13","TeV")
nllctZctZIobs.add_qualifier("LUMINOSITY","137","fb$^{-1}$")

tabctZctZI.add_variable(wcctZ)
tabctZctZI.add_variable(wcctZI)
tabctZctZI.add_variable(nllctZctZIobs)

tabctZctZI.add_image("../figures/ctZ_ctZI_wBkg.png")
#tabctZctZI.keywords()
tabctZctZI.keywords["reactions"] = ["P P --> TOP TOPBAR X", "P P --> TOP TOPBAR GAMMA"]
tabctZctZI.keywords["cmenergies"] = [13000.0]
tabctZctZI.keywords["observables"] = ["CLS"]
tabctZctZI.keywords["phrases"] = ["Top", "Quark", "Photon", "lepton+jets", "semileptonic", "Cross Section", "Proton-Proton Scattering", "Inclusive", "Differential"]
submission.add_table(tabctZctZI)


###
### write files
###

submission.create_files()
