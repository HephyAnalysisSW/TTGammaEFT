# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy, array
from   math import log
# RootTools
from RootTools.core.standard          import *

# Analysis
from Analysis.Tools.MergingDirDB      import MergingDirDB

# Internal Imports
from TTGammaEFT.Tools.user            import plot_directory, cache_directory
from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter

from TTGammaEFT.Analysis.SetupHelpers import *
from TTGammaEFT.Analysis.Setup        import Setup
from TTGammaEFT.Analysis.EstimatorList   import EstimatorList
from TTGammaEFT.Analysis.regions      import *

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                        help="Log level for logging")
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv1_v1",                                              help="plot sub-directory")
argParser.add_argument("--recoSelection",      action="store",      default="SR3p",                                                          help="reco region")
argParser.add_argument("--variable",           action="store",      default="ptG", choices = ["ptG"],                                        help="whichvariable?")
argParser.add_argument("--fiducialSelection",       action="store",      default="nGenLepCMS1-nGenJetCMS3p-nGenBTagCMS1p-nGenPhotonCMS1",         help="define fiducial phase space")
#argParser.add_argument("--genBinning",         action="store",      default=[10,20,220], type=int, nargs=3,                                  help="binning gen: nBins, lowPt, highPt")
#argParser.add_argument("--recoBinning",        action="store",      default=[30,20,220], type=int, nargs=3,                                  help="binning reco: nBins, lowPt, highPt")
argParser.add_argument("--mode",               action="store",      default="all",  type=str,  choices=["mu", "e", "all"],                   help="lepton selection")
argParser.add_argument("--small",              action="store_true",                                                                          help="Run only on a small subset of the data?")
argParser.add_argument("--overwrite",          action="store_true",                                                                          help="overwrite cache?")
argParser.add_argument('--years',              action='store',      nargs='*',  type=str, default=['RunII'],                                 help="List of years to be unfolded.")

args = argParser.parse_args()

if "RunII" in args.years: args.years = ["2016", "2017", "2018"] 

# Logger
import Analysis.Tools.logger as logger_an
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile=None )
logger_rt = logger_rt.get_logger( args.logLevel, logFile=None )

# Text on the plots
def drawObjects( ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    line = (0.65, 0.95, "(13 TeV)") 
    lines = [
      (0.15, 0.95, "CMS #bf{#it{Preliminary}}"), 
      line
    ]
    return [tex.DrawLatex(*l) for l in lines]

if args.small:        args.plot_directory += "_small"


# observable
if args.variable == "ptG":
    reco_variable           = "PhotonGood0_pt"
    reco_thresholds         = range(20, 520, 10)
    reco_variable_underflow = -1
    # appending reco thresholds for multiple years
    max_reco_val         = reco_thresholds[-1]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    reco_thresholds_years = copy.deepcopy(reco_thresholds)
    for i_year in range(1, len(args.years)):
        reco_thresholds_years += [t + i_year*max_reco_val for t in reco_thresholds]

    #pt_reco_thresholds  = range(20, 50,5)+range(50,100,10)+range(100,200,20)+range(200,500,50) 
    fiducial_variable = "GenPhotonCMSUnfold0_pt"
    fiducial_thresholds     = reco_thresholds[::3]
    max_fiducial_val        = fiducial_thresholds[-1]
    max_fiducial_bincenter  = 0.5*sum(fiducial_thresholds[-2:])
    underflow_fiducial_val  = -1
    #gen_match_photon = "sqrt(acos(cos(GenPhotonCMSUnfold0_phi-PhotonGood0_phi))**2+(GenPhotonCMSUnfold0_eta-PhotonGood0_eta)**2)<0.1"
    tex_reco = "p^{reco}_{T}(#gamma) (GeV)"
    tex_gen  = "p^{gen}_{T}(#gamma) (GeV)"
else:
    raise RuntimeError("Can't unfold without variable. Don't know '%s'." % args.variable) 

# database
year_str        = "_".join(args.years)
cache_dir = os.path.join(cache_directory, "unfolding", year_str, "matrix")
dirDB     = MergingDirDB(cache_dir)

# specifics from the arguments
plot_directory_ = os.path.join( plot_directory, "unfolding", year_str, args.plot_directory, args.fiducialSelection, args.recoSelection, args.mode )
cfg_key         = ( args.small, year_str, args.fiducialSelection, args.recoSelection, args.mode, args.variable)

read_variables = [ "weight/F", "year/I",
                   "nPhotonGood/I", "nJetGood/I", "nBTagGood/I", "nLeptonTight/I", "nLeptonVetoIsoCorr/I", "nPhotonNoChgIsoNoSieie/I",
                   "PhotonGood0_pt/F",
                   "GenPhotonATLASUnfold0_pt/F", "GenPhotonCMSUnfold0_pt/F",
                   "nGenLeptonATLASUnfold/I", "nGenPhotonATLASUnfold/I", "nGenBJetATLASUnfold/I", "nGenJetsATLASUnfold/I",
                   "nGenLeptonCMSUnfold/I", "nGenPhotonCMSUnfold/I", "nGenBJetCMSUnfold/I", "nGenJetsCMSUnfold/I",
                   "reweightHEM/F", "reweightTrigger/F", "reweightL1Prefire/F", "reweightPU/F", "reweightLeptonTightSF/F", "reweightLeptonTrackingTightSF/F", "reweightPhotonSF/F", "reweightPhotonElectronVetoSF/F", "reweightBTag_SF/F",
                    "Flag_goodVertices/I", "Flag_globalSuperTightHalo2016Filter/I", "Flag_HBHENoiseFilter/I", "Flag_HBHENoiseIsoFilter/I", "Flag_EcalDeadCellTriggerPrimitiveFilter/I", "Flag_BadPFMuonFilter/I", "PV_ndof/F", "PV_x/F", "PV_y/F", "PV_z/F"
                ]

MET_filter_cut   = "(year==2016&&Flag_goodVertices&&Flag_globalSuperTightHalo2016Filter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_BadPFMuonFilter&&PV_ndof>4&&sqrt(PV_x*PV_x+PV_y*PV_y)<=2&&abs(PV_z)<=24)"

loop_key = ( cfg_key, "result")
if dirDB.contains( loop_key ) and not args.overwrite:
    matrix, fiducial_spectrum, reco_spectrum = dirDB.get( loop_key )
else:

    # Define stuff 
    fiducial_spectrum = ROOT.TH1D("fiducial_spectrum", "fiducial_spectrum", len(fiducial_thresholds)-1, array.array('d', fiducial_thresholds) )
    fiducial_spectrum.GetXaxis().SetTitle(tex_gen)

    reco_spectrum = ROOT.TH1D("reco_spectrum", "reco_spectrum", len(reco_thresholds_years)-1, array.array('d', reco_thresholds_years) )
    reco_spectrum.GetXaxis().SetTitle(tex_gen)

    matrix = ROOT.TH2D("unfolding_matrix", "unfolding_matrix", len(reco_thresholds_years)-1, array.array('d', reco_thresholds_years), len(fiducial_thresholds)-1, array.array('d', fiducial_thresholds) )

    matrix.GetXaxis().SetTitle(tex_reco)
    matrix.GetYaxis().SetTitle(tex_gen)

    for year in args.years:
        setup         = Setup( year=int(year), photonSelection=False, checkOnly=True, runOnLxPlus=False ) 
        setup         = setup.sysClone( parameters=allRegions[args.recoSelection]["parameters"] )
        # reco selection
        recoSelection = setup.selection( "MC", channel="all", **setup.defaultParameters() )
        reco_selection_str = MET_filter_cut+"&&"+cutInterpreter.cutString(recoSelection['prefix'])

        # fiducial seletion
        fiducial_selection_str = cutInterpreter.cutString(args.fiducialSelection)

        ttreeFormulas = {
                    'is_fiducial': fiducial_selection_str, 
                    'is_reco':     reco_selection_str, 
                    'gen_weight'    : 'weight*(35.92*(year==2016)+41.53*(year==2017)+59.74*(year==2018))', 
                    'reco_reweight' : 'reweightHEM*reweightTrigger*reweightPU*reweightL1Prefire*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF', 
                }

        # Sample for this year (fix)
        ttg0l = Sample.fromDirectory("ttg0l_%s"%year, directory = ["/scratch/robert.schoefbeck/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_{year}_TTG_private_v47/inclusive/TTGHad_LO/".format(year=year)])
        ttg1l = Sample.fromDirectory("ttg1l_%s"%year, directory = ["/scratch/robert.schoefbeck/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_{year}_TTG_private_v47/inclusive/TTGSingleLep_LO/".format(year=year)])
        ttg2l = Sample.fromDirectory("ttg2l_%s"%year, directory = ["/scratch/robert.schoefbeck/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_{year}_TTG_private_v47/inclusive/TTGLep_LO/".format(year=year)])

        # FIXME
        # sample = Sample.combine( "ttg_%s"%year, [ttg1l, ttg2l, ttg0l] )
        sample = ttg1l 

        # Apply 'small'
        norm = 1.
        if args.small:           
            sample.normalization=1.
            sample.reduceFiles( to=2 )
            norm = 1./sample.normalization
       
        counter_tot      = 0
        counter_reco     = 0
        counter_fid      = 0
        counter_fid_reco = 0
        yield_tot        = 0
        yield_reco       = 0
        yield_fid        = 0
        yield_fid_reco   = 0
         
        r = sample.treeReader( 
            variables = map(TreeVariable.fromString, read_variables), 
            ttreeFormulas=ttreeFormulas, 
            selectionString= "(({reco})||({fiducial}))".format(reco=reco_selection_str,fiducial=fiducial_selection_str),
            )

        logger.info( "Processing year %s", year)
        r.start()
        while r.run():

            # weights
            gen_weight_val    = r.event.gen_weight 
            reco_reweight_val = r.event.reco_reweight 

            # counter
            counter_tot += 1
            yield_tot   += gen_weight_val*reco_reweight_val 

            # shift the reco variable to the correct block
            shift_year =  (int(year)-2016)*max_reco_val

            # reco observable 
            reco_variable_val       = getattr( r.event, reco_variable )

            # put reco overflow in the last bin
            if reco_variable_val >= max_reco_val:
                reco_variable_val = max_reco_bincenter 

            # fiducial observable 
            fiducial_variable_val   = getattr( r.event, fiducial_variable ) 

            # put fiducial overflow in the last bin
            if fiducial_variable_val >= max_fiducial_val:
                fiducial_variable_val = max_fiducial_bincenter 

            # Sanity check: A fiducial event should have a fiducial_variable_val that is within the fiducial thresholds
            val_in_fiducial = ( fiducial_variable_val>=fiducial_thresholds[0] and fiducial_variable_val<fiducial_thresholds[-1] )
            assert val_in_fiducial or not r.event.is_fiducial, "Fiducial variable %s=%f not in fiducial regions %r"%( fiducial_variable, fiducial_variable_val, fiducial_thresholds )
                 
            if r.event.is_reco:
                # counter
                counter_reco += 1
                yield_reco   += gen_weight_val*reco_reweight_val 

                reco_spectrum.Fill( reco_variable_val+shift_year, gen_weight_val*reco_reweight_val )
                # signal 
                if  r.event.is_fiducial:
                    # counter
                    counter_fid_reco += 1
                    yield_fid_reco   += gen_weight_val*reco_reweight_val 

                    matrix.Fill(reco_variable_val+shift_year, fiducial_variable_val, gen_weight_val*reco_reweight_val)
                    # inefficiency according to reco_reweight
                    matrix.Fill(reco_variable_underflow, fiducial_variable_val, gen_weight_val*(1-reco_reweight_val))

                # backgrounds (signal events generated outside the fiducial region but reconstructed in the reco phase space)
                else:
                    matrix.Fill(reco_variable_val+shift_year, underflow_fiducial_val, gen_weight_val*reco_reweight_val)
                    # inefficiency of the background according to reco_reweight -> should not be needed 
                    # matrix.Fill(reco_variable_underflow, underflow_fiducial_val, gen_weight_val*(1-reco_reweight_val))
            else:
                # inefficiency according to the selection
                if  r.event.is_fiducial:
                    matrix.Fill(reco_variable_underflow, fiducial_variable_val, gen_weight_val*reco_reweight_val)

            if r.event.is_fiducial: # note: there is no reco_reweight_val because we construct the gen spectrum
                # counter
                counter_fid += 1
                yield_fid   += gen_weight_val*reco_reweight_val 

                fiducial_spectrum.Fill( fiducial_variable_val, gen_weight_val ) 

        logger.info("total: %6.2f (%6.2f) fiducial: %6.2f (%6.2f) fiducial+reco %6.2f (%6.2f) reco-total: %6.2f (%6.2f)", yield_tot, counter_tot, yield_fid, counter_fid, yield_fid_reco, counter_fid_reco, yield_reco, counter_reco)

    dirDB.add( loop_key, (matrix, fiducial_spectrum, reco_spectrum), overwrite=True )

# Unfolding matrix
plot_matrix = Plot2D.fromHisto( "unfolding_matrix", [[matrix]], texY = "p^{gen}_{T}(#gamma) [GeV]", texX = "p^{reco}_{T}(#gamma) [GeV]" )
plotting.draw2D( plot_matrix,
                 plot_directory = plot_directory_,
                 logX = False, logY = False, logZ = True,
                 drawObjects = drawObjects(),
                 copyIndexPHP = True,
                )

assert False, ""

#matrix_norm = matrix.Clone()
#for n_gen in range( matrix_norm.GetNbinsX()):
#    tot = 0
#    for n_reco in range( matrix_norm.GetNbinsX()):
#        tot+=matrix_norm.GetBinContent(n_gen+1,n_reco+1)
#    if tot>0:
#        for n_reco in range( matrix_norm.GetNbinsY()):
#            matrix_norm.SetBinContent(n_gen+1,n_reco+1, matrix_norm.GetBinContent(n_gen+1,n_reco+1)/tot)

#histos               = {}
#histos["gen"]        = matrix.ProjectionX("gen")
#histos["efficiency"] = ROOT.TH1D( "efficiency", "efficiency", len(pt_fiducial_thresholds)-1, array.array('d', pt_fiducial_thresholds))
#histos["purity"]     = ROOT.TH1D( "purity",     "purity",     len(pt_reco_thresholds)-1, array.array('d', pt_reco_thresholds))
#histos["recoMC"]     = matrix.ProjectionY("reco")
#if args.noData: histos["reco"] = histos["recoMC"]
#else:           histos["reco"] = dataHisto
#
#for i in range( len(pt_fiducial_thresholds)+1 ):
#    genPt   = histos["gen"].GetBinCenter( i+1 )
#    recoBin = histos["recoMC"].FindBin( genPt )
#    gen     = histos["gen"].GetBinContent( i+1 )
#    eff     = matrix.GetBinContent( i+1, recoBin ) / gen if gen else 0.
#    histos["efficiency"].SetBinContent( i+1, eff )
#    
#for i in range( len(pt_reco_thresholds)+1 ):
#    recoPt = histos["recoMC"].GetBinCenter( i+1 )
#    genBin = histos["gen"].FindBin( recoPt )
#    reco   = histos["recoMC"].GetBinContent( i+1 )
#    pur    = matrix.GetBinContent( genBin, i+1 ) / reco if reco else 0.
#    histos["purity"].SetBinContent( i+1, pur )


# UNFOLDING

# regularization
#regMode = ROOT.TUnfold.kRegModeNone
#regMode = ROOT.TUnfold.kRegModeSize
#regMode = ROOT.TUnfold.kRegModeDerivative
regMode = ROOT.TUnfold.kRegModeCurvature
#regMode = ROOT.TUnfold.kRegModeMixed

# extra contrains
#constraintMode = ROOT.TUnfold.kEConstraintNone
constraintMode = ROOT.TUnfold.kEConstraintArea

#mapping = ROOT.TUnfold.kHistMapOutputVert
mapping = ROOT.TUnfold.kHistMapOutputHoriz

#densityFlags = ROOT.TUnfoldDensity.kDensityModeNone
#densityFlags = ROOT.TUnfoldDensity.kDensityModeUser
densityFlags = ROOT.TUnfoldDensity.kDensityModeBinWidth
#densityFlags = ROOT.TUnfoldDensity.kDensityModeBinWidthAndUser

unfold = ROOT.TUnfoldDensity( matrix, mapping, regMode, constraintMode, densityFlags )
unfold.SetInput( histos["reco"] )

nScan       = 200
rhoLogTau   = ROOT.TSpline3()
#iBest = unfold.ScanTau(nScan, 10**-6, 0.5, rhoLogTau, ROOT.TUnfoldDensity.kEScanTauRhoMax, "signal", SCAN_AXISSTEERING, lCurve);
iBest = unfold.ScanTau(nScan, 10**-6, 2, rhoLogTau, ROOT.TUnfoldDensity.kEScanTauRhoSquareAvg)
#iBest = unfold.ScanTau(nScan, 10**-6, 2, rhoLogTau, ROOT.TUnfoldDensity.kEScanTauRhoMax)
# create graphs with one point to visualize best choice of tau
t   = ROOT.Double()
rho = ROOT.Double()
rhoLogTau.GetKnot(iBest,t,rho)
bestRhoLogTau = ROOT.TGraph(1,array.array('d',[t]),array.array('d',[rho]))
tAll   = []
rhoAll = []
for i in range(nScan):
    rhoLogTau.GetKnot(i,t,rho)
    tAll.append( t )
    rhoAll.append( rho )

knots = ROOT.TGraph(nScan,array.array('d',tAll), array.array('d',rhoAll))
print "chi**2=", unfold.GetChi2A(), "+", unfold.GetChi2L(), " / ",unfold.GetNdf()
c = ROOT.TCanvas("ScanTau","ScanTau")
knots.SetTitle("#rho ( log(#tau) )")
rhoLogTau.SetTitle("#rho ( log(#tau) )")
bestRhoLogTau.SetTitle("#rho ( log(#tau) )")
knots.Draw("*")

rhoLogTau.Draw()
bestRhoLogTau.SetMarkerColor(ROOT.kRed)
bestRhoLogTau.Draw("*")
for s in [ knots, bestRhoLogTau ]:
    s.GetXaxis().SetTitle("log(#tau)")
    s.GetYaxis().SetTitle("#rho")

c.RedrawAxis()
c.Print(os.path.join(plot_directory_, "ScanTau.png"))
c.Print(os.path.join(plot_directory_, "ScanTau.pdf"))

best_logtau = bestRhoLogTau.GetX()[0]
print "Found best tau at",  best_logtau

unfold.DoUnfold(0)
histos["unfoldedMC"] = unfold.GetOutput("unfoldedMC")

hs = []
for i_factor, factor in enumerate( reversed([ 0, 0.01, 0.1, 0.5, 1, 1.5, 10, 100 ]) ):
    unfold.DoUnfold(10**(best_logtau)*factor)
    h = unfold.GetOutput("unfoldedMC")
    h.legendText = ( "log(#tau) = %6.4f" % (best_logtau + log(factor,10)) + ("(best)" if factor==1 else "") if factor > 0 else  "log(#tau) = -#infty" )
    h.style = styles.lineStyle( 1+ i_factor)
    hs.append( h )

for logY in [True, False]:
    plot = Plot.fromHisto( name = 'unfolding_comparison' + ('_log' if logY else ''),  histos = [[ h ] for h in hs], texX = "p_{T}", texY = "Events" )
    plot.stack = None
    plotting.draw(plot,
        plot_directory = plot_directory_,
        #ratio          = {'yRange':(0.6,1.4)} if len(plot.stack)>=2 else None,
        logX = False, logY = logY, sorting = False,
        #yRange         = (0.5, 1.5) ,
        #scaling        = {0:1} if len(plot.stack)==2 else {},
        legend         = [ (0.15,0.91-0.05*len(plot.histos)/2,0.95,0.91), 2 ],
      )

# PLOT 

histos["gen"].style        = styles.lineStyle( ROOT.kBlack, width = 2 )
histos["efficiency"].style = styles.lineStyle( ROOT.kBlue, width = 2 )
histos["purity"].style     = styles.lineStyle( ROOT.kRed, width = 2 )
histos["reco"].style       = styles.errorStyle( ROOT.kBlack, width = 2 )
histos["recoMC"].style     = styles.errorStyle( ROOT.kBlack, width = 2 )
#histos["unfolded"].style   = styles.errorStyle( ROOT.kBlack, width = 2 )
histos["unfoldedMC"].style = styles.errorStyle( ROOT.kBlack, width = 2 )

addons = []
if args.noData:        addons.append("MC")
else:                  addons.append("Data")
if args.mode != "all": addons.append(args.mode.replace("mu","#mu"))

histos["gen"].legendText        = "Generated Events (%s)"%", ".join(addons).replace(", Data",", MC")
#histos["unfolded"].legendText   = "Particle Level (%s)"%", ".join(addons)
histos["unfoldedMC"].legendText = "Particle Level (%s)"%", ".join(addons).replace(", Data",", MC")
histos["efficiency"].legendText = "Efficiency"
histos["purity"].legendText     = "Purity"
histos["reco"].legendText       = "Detector Level (%s)"%", ".join(addons)
histos["recoMC"].legendText     = "Detector Level (%s)"%", ".join(addons).replace(", Data",", MC")

# remove the defaults again
Plot.setDefaults()
Plot2D.setDefaults()

# Unfolding matrix
unfold2D = Plot2D.fromHisto( "unfoldingMatrix", [[matrix]], texX = "p^{gen}_{T}(#gamma) [GeV]", texY = "p^{reco}_{T}(#gamma) [GeV]" )
plotting.draw2D( unfold2D,
                 plot_directory = plot_directory_,
                 logX = False, logY = False, logZ = True,
                 drawObjects = drawObjects( not args.noData, lumi_scale ),
                 copyIndexPHP = True,
                )
unfold2D_norm = Plot2D.fromHisto( "unfoldingMatrix_norm", [[matrix_norm]], texX = "p^{gen}_{T}(#gamma) [GeV]", texY = "p^{reco}_{T}(#gamma) [GeV]")
unfold2D_norm.drawOption = "COLZTEXT"
unfold2D_norm.histModifications = [ lambda h: ROOT.gStyle.SetPaintTextFormat("4.2f") ]
plotting.draw2D( unfold2D_norm,
                 plot_directory = plot_directory_,
                 logX = True, logY = True, logZ = True,
                 drawObjects = drawObjects( not args.noData, lumi_scale ),
                 copyIndexPHP = True,
                )

plots = []
# gen pt
plots.append( Plot.fromHisto( args.fiducialVariable, [[histos["gen"]]], texX = "p^{gen}_{T}(#gamma) [GeV]", texY = "Number of Events" ) )
# reco pt
plots.append( Plot.fromHisto( "PhotonGood0_pt", [[histos["reco"]]], texX = "p^{reco}_{T}(#gamma) [GeV]", texY = "Number of Events" ) )
# reco MC pt
plots.append( Plot.fromHisto( "PhotonGood0_pt_MC", [[histos["recoMC"]]], texX = "p^{reco}_{T}(#gamma) [GeV]", texY = "Number of Events" ) )
# unfolded pt
#plots.append( Plot.fromHisto( "unfolded_pt", [[histos["unfolded"]]], texX = "p^{unfolded}_{T}(#gamma) [GeV]", texY = "Number of Events" ) )
# unfolded MC pt
plots.append( Plot.fromHisto( "unfolded_pt_MC", [[histos["unfoldedMC"]]], texX = "p^{unfolded}_{T}(#gamma) [GeV]", texY = "Number of Events" ) )
# unfolded pt + gen
plots.append( Plot.fromHisto( "closure", [[histos["unfoldedMC"]],[histos["gen"]]], texX = "p^{gen,unfolded}_{T}(#gamma) [GeV]", texY = "Number of Events" ) )
# efficiency
plots.append( Plot.fromHisto( "efficiency", [[histos["efficiency"]]], texX = "p^{reco}_{T}(#gamma) [GeV]", texY = "Efficiency" ) )
# purity
plots.append( Plot.fromHisto( "purity", [[histos["purity"]]], texX = "p^{gen}_{T}(#gamma) [GeV]", texY = "Purity" ) )
# purity and efficiency
plots.append( Plot.fromHisto( "purity_efficiency", [[histos["purity"]],[histos["efficiency"]]], texX = "p^{gen,reco}_{T}(#gamma) [GeV]", texY = "Purity, Efficiency" ) )

for plot in plots:
    xShift = plot.name in ["efficiency","purity","purity_efficiency"]
    plotting.draw( plot,
                   plot_directory = plot_directory_,
                   logX = False, logY = False, sorting = False,
                   yRange = (0.01, "auto"),
                   drawObjects = drawObjects( not args.noData, lumi_scale ),
                   legend = [ (0.3+0.3*xShift,0.88-0.04*len(plot.histos),0.88,0.88), 1 ],
                   copyIndexPHP = True,
                   )


