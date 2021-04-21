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
tableF2a.add_image("../figures/systematics/RunII/102X_TTG_ppv49_v6/SR3p/postfit/all_cat/lin/PhotonGood0_pt.png")
#tableF2a.keywords()
submission.add_table(tableF2a)


###
### Fig 2b
###

tableF2b = convertSRHistToYaml("../systPlots/SR3p_mT_all.root", "Figure 2b", "$m_{T}(W)$", "GeV")
tableF2b.description = "Distribution of $m_{T}(W)$ in the SR3p signal region."
tableF2b.location = "Data from Figure 2 (top center)"
tableF2b.add_image("../figures/systematics/RunII/102X_TTG_ppv49_v6/SR3p/postfit/all_cat/lin/mT.png")
#tableF2b.keywords()
submission.add_table(tableF2b)


###
### Fig 2c
###

tableF2c = convertSRHistToYaml("../systPlots/SR3p_m3_all.root", "Figure 2c", "$M_{3}$", "GeV")
tableF2c.description = "Distribution of $M_{3}$ in the SR3p signal region."
tableF2c.location = "Data from Figure 2 (top right)"
tableF2c.add_image("../figures/systematics/RunII/102X_TTG_ppv49_v6/SR3p/postfit/all_cat/lin/m3.png")
#tableF2c.keywords()
submission.add_table(tableF2c)


###
### Fig 2d
###

tableF2d = convertSRHistToYaml("../systPlots/SR3p_mLtight0Gamma_all.root", "Figure 2d", "$m(l,\gamma)$", "GeV")
tableF2d.description = "Distribution of $m(l,\gamma)$ in the SR3p signal region."
tableF2d.location = "Data from Figure 2 (bottom left)"
tableF2d.add_image("../figures/systematics/RunII/102X_TTG_ppv49_v6/SR3p/postfit/all_cat/lin/mLtight0Gamma.png")
#tableF2d.keywords()
submission.add_table(tableF2d)


###
### Fig 2e
###

tableF2e = convertSRHistToYaml("../systPlots/SR3p_ltight0GammadR_all.root", "Figure 2e", "$\Delta R(l,\gamma)$", "")
tableF2e.description = "Distribution of $\Delta R(l,\gamma)$ in the SR3p signal region."
tableF2e.location = "Data from Figure 2 (bottom center)"
tableF2e.add_image("../figures/systematics/RunII/102X_TTG_ppv49_v6/SR3p/postfit/all_cat/lin/ltight0GammadR.png")
#tableF2e.keywords()
submission.add_table(tableF2e)


###
### Fig 2f
###

tableF2f = convertSRHistToYaml("../systPlots/SR3p_photonJetdR_all.root", "Figure 2f", "$\Delta R(j,\gamma)$", "")
tableF2f.description = "Distribution of $\Delta R(j,\gamma)$ in the SR3p signal region."
tableF2f.location = "Data from Figure 2 (bottom right)"
tableF2f.add_image("../figures/systematics/RunII/102X_TTG_ppv49_v6/SR3p/postfit/all_cat/lin/photonJetdR.png")
#tableF2f.keywords()
submission.add_table(tableF2f)


###
### Fig 3a
###

tableF3a = convertWJetsHistToYaml("../systPlots/WJets2_mT_e.root", "Figure 3a")
tableF3a.description = "Fit result of the multijet template obtained with loosely isolated leptons and the electroweak background to the measured $m_{T}(W)$ distribution with isolated leptons in the $N_{jet}=2$, $N_{b jet}=0$ selection for electrons."
tableF3a.location = "Data from Figure 3 (left)"
tableF3a.add_image("../figures/systematics/RunII/102X_TTG_ppv49_v6/WJets2/postfit/e/lin/mT_e.png")
#tableF3a.keywords()
submission.add_table(tableF3a)


###
### Fig 3b
###

tableF3b = convertWJetsHistToYaml("../systPlots/WJets2_mT_mu.root", "Figure 3b")
tableF3b.description = "Fit result of the multijet template obtained with loosely isolated leptons and the electroweak background to the measured $m_{T}(W)$ distribution with isolated leptons in the $N_{jet}=2$, $N_{b jet}=0$ selection for muons."
tableF3b.location = "Data from Figure 3 (right)"
tableF3b.add_image("../figures/systematics/RunII/102X_TTG_ppv49_v6/WJets2/postfit/mu/lin/mT_mu.png")
#tableF3b.keywords()
submission.add_table(tableF3b)


###
### Fig 4a
###

tableF4a = convertMlgHistToYaml("../systPlots/VGmis3p_mLtight0Gamma_e.root", "Figure 4a", "$m(e,\gamma)$")
tableF4a.description = "Distribution of the invariant mass of the lepton and the photon ($m(l,\gamma)$) in the $N_{jet}\geq 3$, $N_{b jet}=0$ selection for the e channel."
tableF4a.location = "Data from Figure 4 (left)"
tableF4a.add_image("../figures/systematics/RunII/102X_TTG_ppv49_v6a/VGmis3p/postfit/e_cat/lin/mLtight0Gamma_e.png")
#tableF4a.keywords()
submission.add_table(tableF4a)


###
### Fig 4b
###

tableF4b = convertMlgHistToYaml("../systPlots/VGmis3p_mLtight0Gamma_mu.root", "Figure 4b", "$m(\mu,\gamma)$")
tableF4b.description = "Distribution of the invariant mass of the lepton and the photon ($m(l,\gamma)$) in the $N_{jet}\geq 3$, $N_{b jet}=0$ selection for the $\mu$ channel."
tableF4b.location = "Data from Figure 4 (right)"
tableF4b.add_image("../figures/systematics/RunII/102X_TTG_ppv49_v6a/VGmis3p/postfit/mu_cat/lin/mLtight0Gamma_mu.png")
#tableF4b.keywords()
submission.add_table(tableF4b)


###
### SF table
###
tabSF = Table("Table 4")

tabSF.description = "Extracted scale factors for the contribution from misidentified electrons for the three data-taking periods, and the Z$\gamma$ ,W$\gamma$ simulations."
tabSF.location = "Table 4"

sfType = Variable( "Scale factor", is_independent=True, is_binned=False, units="")
sfType.values = ["Misidentified electrons 2016", "Misidentified electrons 2017", "Misidentified electrons 2018", "Z$\gamma$ normalization", "W$\gamma$ normalization"]
value     = Variable( "Value", is_independent=False, is_binned=False, units="")
value.values = [2.22, 1.83, 1.59, 0.83, 1.2]
unc = Uncertainty( "total" )
unc.is_symmetric = True
unc.values = [0.28, 0.24, 0.18, 0.10, 0.09]
value.uncertainties.append( unc )

tabSF.add_variable(sfType)
tabSF.add_variable(value)

submission.add_table(tabSF)


###
### Fig 5
###

tableF5 = convertCRPlotToYaml()
tableF5.description = "Predicted and observed yields in the control regions in the $N_{jet}= 3$ and $\geq 4$ seletions using the post-fit values of the nuisance parameters."
tableF5.location = "Data from Figure 5"
tableF5.add_image("../figures/fitpostCWR/combined/postFit_addDYSF_incl/SR3eM3_SR3muM3_SR4peM3_SR4pmuM3_VG3e_VG3mu_VG4pe_VG4pmu_misDY3_misDY4p/regions_VG3e_VG3mu_VG4pe_VG4pmu_misDY3_misDY4p.png")
#tableF5.keywords()
submission.add_table(tableF5)


###
### Fig 6
###

tableF6 = convertSRPlotToYaml()
tableF6.description = "Predicted and observed yields in the signal regions in the $N_{jet}= 3$ and $\geq 4$ seletions using the post-fit values of the nuisance parameters."
tableF6.location = "Data from Figure 6"
tableF6.add_image("../figures/fitpostCWR/combined/postFit_addDYSF_incl/SR3eM3_SR3muM3_SR4peM3_SR4pmuM3_VG3e_VG3mu_VG4pe_VG4pmu_misDY3_misDY4p/regions_SR3eM3_SR3muM3_SR4peM3_SR4pmuM3.png")
#tableF6.keywords()
submission.add_table(tableF6)


###
### inclusive cross section
###
tabXSec = Table("Equation 2")

tabXSec.description = "The measured inclusive ttgamma cross section in the fiducial phase space compared to the prediction from simulation using Madgraph_aMC@NLO at a center-of-mass energy of 13 TeV"
tabXSec.location = "Equation 2"

data = np.loadtxt("../xsec/xsec.txt", skiprows=1)

xsecType = Variable( "", is_independent=True, is_binned=False, units="")
xsecType.values = ["Experimental", "Theoretical-Madgraph-aMC@NLO"]
xsec     = Variable( "Cross section", is_independent=False, is_binned=False, units="fb")
xsec.values = [data[0][0], data[1][0]]
tot     = Variable( "Total uncertainty", is_independent=False, is_binned=False, units="fb")
tot.values = [data[0][1], data[1][1]]
stat     = Variable( "Stat. uncertainty", is_independent=False, is_binned=False, units="fb")
stat.values = [data[0][2], ""]
syst     = Variable( "Syst. uncertainty", is_independent=False, is_binned=False, units="fb")
syst.values = [data[0][3], ""]

tabXSec.add_variable(xsecType)
tabXSec.add_variable(xsec)
tabXSec.add_variable(tot)
tabXSec.add_variable(stat)
tabXSec.add_variable(syst)

submission.add_table(tabXSec)


###
### SSM
###
tabssm = Table("Figure 7")

tabssm.description = "Summary of the measured cross section ratios with respect to the NLO cross section prediction for signal regions binned in the electron channel, muon channel and the combined single lepton measurement."
tabssm.location = "Data from Figure 7"

datassm = np.loadtxt("../xsec/ssm.txt", skiprows=1)

ssmType = Variable( "", is_independent=True, is_binned=False)
ssmType.values = ["e+jets", "$\mu$+jets", "l+jets"]
ssm     = Variable( "Signal strength modifier", is_independent=False, is_binned=False)
ssm.values = ["%.3f"%datassm[0][0], "%.3f"%datassm[1][0], "%.3f"%datassm[2][0]]
tot     = Variable( "Total uncertainty", is_independent=False, is_binned=False)
tot.values = ["$^{+%.3f}_{%.3f}$"%(datassm[0][1],datassm[0][2]), "$^{+%.3f}_{%.3f}$"%(datassm[1][1],datassm[1][2]), "$^{+%.3f}_{%.3f}$"%(datassm[2][1],datassm[2][2])]
stat     = Variable( "Stat. uncertainty", is_independent=False, is_binned=False)
stat.values = ["$\pm$%.3f"%datassm[0][3], "$\pm$%.3f"%datassm[1][3], "$\pm$%.3f"%datassm[2][3]]
syst     = Variable( "Syst. uncertainty", is_independent=False, is_binned=False)
syst.values = ["$^{+%.3f}_{%.3f}$"%(datassm[0][4],datassm[0][5]), "$^{+%.3f}_{%.3f}$"%(datassm[1][4],datassm[1][5]), "$^{+%.3f}_{%.3f}$"%(datassm[2][4],datassm[2][5])]

tabssm.add_variable(ssmType)
tabssm.add_variable(ssm)
tabssm.add_variable(tot)
tabssm.add_variable(stat)
tabssm.add_variable(syst)

tabssm.add_image("../figures/summary/summaryResult.png")
#tablessm.keywords()

submission.add_table(tabssm)


###
### Fig 8a
###

tableUnfPt = convertUnfoldingHistToYaml( "../unfolding/unfolded_observed_ptG_RunII.root", "Figure 8a", "$p_{T}(\gamma)$", "GeV" )
tableUnfPt.description = "The unfolded differential cross sections for $p_{T}(\gamma)$ and the comparison to simulations."
tableUnfPt.location = "Data from Figure 8 (top left)"
tableUnfPt.add_image("../figures/unfolding/v49_uncertainty_Herwigv3/observed_ptG_RunII/unfolded_spectrum_fromSyst_log_ptg.png")
#tableUnfPt.keywords()
submission.add_table(tableUnfPt)


###
### Fig 8b
###

tableUnfEta = convertUnfoldingHistToYaml( "../unfolding/unfolded_observed_absEta_RunII.root", "Figure 8b", "$|\eta(\gamma)|$", "" )
tableUnfEta.description = "The unfolded differential cross sections for $|\eta(\gamma)|$ and the comparison to simulations."
tableUnfEta.location = "Data from Figure 8 (top right)"
tableUnfEta.add_image("../figures/unfolding/v49_uncertainty_Herwigv2/observed_absEta_RunII/unfolded_spectrum_fromSyst_eta.png")
#tableUnfEta.keywords()
submission.add_table(tableUnfEta)


###
### Fig 8c
###

tableUnfdR = convertUnfoldingHistToYaml( "../unfolding/unfolded_observed_dRlg_RunII.root", "Figure 8c", "$\Delta R(l,\gamma)$", "" )
tableUnfdR.description = "The unfolded differential cross sections for $\Delta R(l,\gamma)$ and the comparison to simulations."
tableUnfdR.location = "Data from Figure 8 (bottom)"
tableUnfdR.add_image("../figures/unfolding/v49_uncertainty_Herwigv2/observed_dRlg_RunII/unfolded_spectrum_fromSyst_dR.png")
#tableUnfdR.keywords()
submission.add_table(tableUnfdR)


###
### Fig 9a
###

tableCov = convertCovMatrixToYaml("../unfolding/covMatrix_observed_ptG_RunII.root", "Figure 9a", "$p_{T}(\gamma)$", "GeV")
tableCov.description = "The covariance matrix of the unfolded differential measurement for $p_{T}(\gamma)$."
tableCov.location = "Data from Figure 9 (top left)"
tableCov.add_image("../figures/unfolding/v49_uncertainty_Herwigv2/observed_ptG_RunII/covMatrix_ptg.png")
#tableCov.keywords()
submission.add_table(tableCov)


###
### Fig 9b
###

tableCovEta = convertCovMatrixToYaml("../unfolding/covMatrix_observed_absEta_RunII.root", "Figure 9b", "$|\eta(\gamma)|$", "")
tableCovEta.description = "The covariance matrix of the unfolded differential measurement for $|\eta(\gamma)|$."
tableCovEta.location = "Data from Figure 9 (top right)"
tableCovEta.add_image("../figures/unfolding/v49_uncertainty_Herwigv2/observed_absEta_RunII/covMatrix_eta.png")
#tableCovEta.keywords()
submission.add_table(tableCovEta)


###
### Fig 9c
###

tableCovdR = convertCovMatrixToYaml("../unfolding/covMatrix_observed_dRlg_RunII.root", "Figure 9c", "$\Delta R(l,\gamma)$", "")
tableCovdR.description = "The covariance matrix of the unfolded differential measurement for $\Delta R(l,\gamma)$."
tableCovdR.location = "Data from Figure 9 (bottom)"
tableCovdR.add_image("../figures/unfolding/v49_uncertainty_Herwigv2/observed_dRlg_RunII/covMatrix_dR.png")
#tableCovdR.keywords()
submission.add_table(tableCovdR)


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
cl95     = Variable( "95% CL interval", is_independent=False, is_binned=False)
cl95.values = ["[-0.29, 0.32]", "[-0.30, 0.31]", "[-0.42, 0.38]", "[-0.42, 0.42]"]

tabcl.add_variable(clType)
tabcl.add_variable(cl68)
tabcl.add_variable(cl95)

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
nllctZobs     = Variable( "-2$\Delta$ L (observed)", is_independent=False, is_binned=False)
nllctZobs.values = datactZobs[:,1]

tabctZ.add_variable(wcctZ)
tabctZ.add_variable(nllctZexp)
tabctZ.add_variable(nllctZobs)

tabctZ.add_image("../figures/nllPlotsPostCWR/RunII/SR3PtUnfoldEFT_SR4pPtUnfoldEFT_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF/comb/ctZ_wExp_wBkg.png")
#tabctZ.keywords()
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
nllctZIobs     = Variable( "-2$\Delta$ L (observed)", is_independent=False, is_binned=False)
nllctZIobs.values = datactZIobs[:,1]

tabctZI.add_variable(wcctZI)
tabctZI.add_variable(nllctZIexp)
tabctZI.add_variable(nllctZIobs)

tabctZI.add_image("../figures/nllPlotsPostCWR/RunII/SR3PtUnfoldEFT_SR4pPtUnfoldEFT_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF/comb/ctZI_wExp_wBkg.png")
#tabctZI.keywords()
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

tabctZctZI.add_variable(wcctZ)
tabctZctZI.add_variable(wcctZI)
tabctZctZI.add_variable(nllctZctZIobs)

tabctZctZI.add_image("../figures/nllPlotsCWR/RunII/SR3PtUnfoldEFT_SR4pPtUnfoldEFT_VG3_VG4p_misDY3_misDY4p_addDYSF_addMisIDSF/observed/ctZ_ctZI_wBkg.png")
#tabctZctZI.keywords()
submission.add_table(tabctZctZI)


###
### write files
###

submission.create_files()
