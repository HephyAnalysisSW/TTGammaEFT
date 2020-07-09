# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy, array
from   math import log
# RootTools
from RootTools.core.standard          import *

# Analysis
from Analysis.Tools.MergingDirDB      import MergingDirDB
from Analysis.Tools.metFilters        import getFilterCut

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
argParser.add_argument("--prefix",             action="store",      default=None,  type=str,                                                 help="for debugging")
argParser.add_argument("--small",              action="store_true",                                                                          help="Run only on a small subset of the data?")
argParser.add_argument("--overwrite",          action="store_true",                                                                          help="overwrite cache?")
argParser.add_argument('--years',              action='store',      nargs='*',  type=str, default=['RunII'],                                 help="List of years to be unfolded.")

args = argParser.parse_args()

if "RunII" in args.years: args.years = ["2016", "2017", "2018"] 

# Logger
import Analysis.Tools.logger as logger
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
    #pt_reco_thresholds  = range(20, 50,5)+range(50,100,10)+range(100,200,20)+range(200,500,50) 
    reco_thresholds         = range(20, 430, 15) #range(20, 430, 10)

    reco_variable_underflow = -1
    # appending reco thresholds for multiple years
    max_reco_val         = reco_thresholds[-1]
    max_reco_bincenter   = 0.5*sum(reco_thresholds[-2:])

    reco_thresholds_years = copy.deepcopy(reco_thresholds)
    for i_year in range(1, len(args.years)):
        reco_thresholds_years += [t + i_year*max_reco_val for t in reco_thresholds]

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
year_str        = "_".join(args.years) + ('_'+args.prefix if args.prefix is not None else '')
cache_dir = os.path.join(cache_directory, "unfolding", year_str, "matrix")
dirDB     = MergingDirDB(cache_dir)

# specifics from the arguments
plot_directory_ = os.path.join( plot_directory, "unfolding", year_str, args.plot_directory, args.fiducialSelection, args.recoSelection, args.mode )
cfg_key         = ( args.small, year_str, args.fiducialSelection, args.recoSelection, args.mode, args.variable)

read_variables = [ "weight/F", "year/I",
                   "nPhotonGood/I", "nJetGood/I", "nBTagGood/I", "nLeptonTight/I", "nLeptonVetoIsoCorr/I", "nPhotonNoChgIsoNoSieie/I",
                   "PhotonGood0_pt/F", "triggered/I", "overlapRemoval/I",
                   "GenPhotonATLASUnfold0_pt/F", "GenPhotonCMSUnfold0_pt/F",
                   "nGenLeptonATLASUnfold/I", "nGenPhotonATLASUnfold/I", "nGenBJetATLASUnfold/I", "nGenJetsATLASUnfold/I",
                   "nGenLeptonCMSUnfold/I", "nGenPhotonCMSUnfold/I", "nGenBJetCMSUnfold/I", "nGenJetsCMSUnfold/I",
                   "reweightHEM/F", "reweightTrigger/F", "reweightL1Prefire/F", "reweightPU/F", "reweightLeptonTightSF/F", "reweightLeptonTrackingTightSF/F", "reweightPhotonSF/F", "reweightPhotonElectronVetoSF/F", "reweightBTag_SF/F",
                    "Flag_goodVertices/I", "Flag_globalSuperTightHalo2016Filter/I", "Flag_HBHENoiseFilter/I", "Flag_HBHENoiseIsoFilter/I", "Flag_EcalDeadCellTriggerPrimitiveFilter/I", "Flag_BadPFMuonFilter/I", "PV_ndof/F", "PV_x/F", "PV_y/F", "PV_z/F"
                ]

extra_read_variables = {
    "2016":[],
    "2017":["Flag_ecalBadCalibFilter/I", "Flag_ecalBadCalibFilterV2/I"],
    "2018":["Flag_ecalBadCalibFilter/I", "Flag_ecalBadCalibFilterV2/I"],
}

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

    counter_tot      = 0
    counter_reco     = 0
    counter_fid      = 0
    counter_fid_reco = 0
    yield_tot        = 0
    yield_reco       = 0
    yield_fid        = 0
    yield_fid_reco   = 0

    for i_year, year in enumerate(args.years):
        setup         = Setup( year=int(year), photonSelection=False, checkOnly=True, runOnLxPlus=False ) 
        setup         = setup.sysClone( parameters=allRegions[args.recoSelection]["parameters"] )
        # reco selection
        recoSelection = setup.selection( "MC", channel="all", **setup.defaultParameters() )

        MET_filter_cut   = "(year==%s&&"%year+getFilterCut(isData=False, year=int(year), skipBadChargedCandidate=True)+")"
        reco_selection_str = MET_filter_cut+"&&triggered&&overlapRemoval==1&&"+cutInterpreter.cutString(recoSelection['prefix'])

        # fiducial seletion
        fiducial_selection_str = cutInterpreter.cutString(args.fiducialSelection)+"&&overlapRemoval==1"

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

        sample = Sample.combine( "ttg_%s"%year, [ttg1l, ttg2l, ttg0l] )

        # Apply 'small'
        if args.small:           
            sample.normalization=1.
            sample.reduceFiles( to=2 )
       
        r = sample.treeReader( 
            variables = map(TreeVariable.fromString, read_variables+extra_read_variables[year]), 
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
            shift_year =  i_year*max_reco_val

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
                    #matrix.Fill(reco_variable_underflow, underflow_fiducial_val, gen_weight_val*(1-reco_reweight_val))
            else:
                # inefficiency according to the selection
                if  r.event.is_fiducial:
                    matrix.Fill(reco_variable_underflow, fiducial_variable_val, gen_weight_val)

            if r.event.is_fiducial: # note: there is no reco_reweight_val because we construct the gen spectrum
                # counter
                counter_fid += 1
                yield_fid   += gen_weight_val

                fiducial_spectrum.Fill( fiducial_variable_val, gen_weight_val ) 

        logger.info("total: %6.2f (%6.2f) fiducial: %6.2f (%6.2f) fiducial+reco %6.2f (%6.2f) reco-total: %6.2f (%6.2f)", yield_tot, counter_tot, yield_fid, counter_fid, yield_fid_reco, counter_fid_reco, yield_reco, counter_reco)

    dirDB.add( loop_key, (matrix, fiducial_spectrum, reco_spectrum), overwrite=True )

    # Unfolding matrix
    plot_matrix = Plot2D.fromHisto("unfolding_matrix", [[matrix]], texY = tex_gen, texX = tex_reco + " +%i*(year-2016)"%max_reco_val )
    plotting.draw2D( plot_matrix,
                     plot_directory = plot_directory_,
                     logX = False, logY = False, logZ = True,
                     drawObjects = drawObjects(),
                     widths = {'x_width':500*len(args.years)},
                     copyIndexPHP = True,
                    )

    # checking the matrix
    logger.info( "Matrix Integral: %6.2f fiducial+reco, weighted: %6.2f <- these numbers should agree.", matrix.Integral(), yield_fid_reco )

    tot_reco_underflow = 0.
    tot_reco_overflow  = 0.
    tot_fid            = 0
    for j_fid in range(0, matrix.GetNbinsY()+2):
        reco_underflow = matrix.GetBinContent( 0, j_fid )
        reco_overflow  = matrix.GetBinContent( matrix.GetNbinsX()+1, j_fid )
        reco_in_fid_bin = matrix.ProjectionX("x",j_fid,j_fid).Integral()
        tot_in_fid_bin  = reco_in_fid_bin+reco_underflow+reco_overflow 

        if j_fid==0: 
            s_str="(underflow)"
        elif j_fid==matrix.GetNbinsY()+1:
            s_str="(overflow)"
        else:
            s_str=""
            tot_reco_underflow += reco_underflow 
            tot_reco_overflow  += reco_overflow

            tot_fid         += tot_in_fid_bin

        logger.info( "Gen-bin %i has reco-UF %6.2f and reco-OF %6.2f reco'd: %6.2f and a tot: %6.2f %s", j_fid, reco_underflow, reco_overflow, reco_in_fid_bin, tot_in_fid_bin, s_str)

    logger.info("Total over all matrix fiducial bins (including reco overflows): %6.2f. yield in fiducial space: %6.2f <- these numbers should agree.", tot_fid, yield_fid)

    tot_fid_underflow = 0.
    tot_fid_overflow  = 0.
    tot_reco          = 0
    for i_reco in range(0, matrix.GetNbinsX()+2):
        fid_underflow = matrix.GetBinContent( i_reco, 0 )
        fid_overflow  = matrix.GetBinContent( i_reco, matrix.GetNbinsX()+1 )
        fid_in_reco_bin = matrix.ProjectionY("y",i_reco,i_reco).Integral()
        tot_in_reco_bin = fid_in_reco_bin+fid_underflow+fid_overflow 

        if i_reco==0: 
            s_str="(underflow)"
        elif i_reco==matrix.GetNbinsX()+1:
            s_str="(overflow)"
        else:
            s_str=""
            tot_fid_underflow += fid_underflow 
            tot_fid_overflow  += fid_overflow

            tot_reco          += tot_in_reco_bin

        logger.info( "Reco-bin %i has fid-UF %6.2f and fid-OF %6.2f in fid: %6.2f and a tot: %6.2f %s", i_reco, fid_underflow, fid_overflow, fid_in_reco_bin, tot_in_reco_bin, s_str)

    logger.info("Total over all matrix reco bins (including fid overflows): %6.2f. yield in fiducial space: %6.2f <- these numbers should agree.", tot_reco, yield_reco)

#matrix_norm = matrix.Clone()
#for n_gen in range( matrix_norm.GetNbinsX()):
#    tot = 0
#    for n_reco in range( matrix_norm.GetNbinsX()):
#        tot+=matrix_norm.GetBinContent(n_gen+1,n_reco+1)
#    if tot>0:
#        for n_reco in range( matrix_norm.GetNbinsY()):
#            matrix_norm.SetBinContent(n_gen+1,n_reco+1, matrix_norm.GetBinContent(n_gen+1,n_reco+1)/tot)

# regularization
#regMode = ROOT.TUnfold.kRegModeNone
#regMode = ROOT.TUnfold.kRegModeSize
#regMode = ROOT.TUnfold.kRegModeDerivative
regMode = ROOT.TUnfold.kRegModeCurvature
#regMode = ROOT.TUnfold.kRegModeMixed

# extra contrains
#constraintMode = ROOT.TUnfold.kEConstraintNone
constraintMode = ROOT.TUnfold.kEConstraintArea

mapping = ROOT.TUnfold.kHistMapOutputVert
#mapping = ROOT.TUnfold.kHistMapOutputHoriz

#densityFlags = ROOT.TUnfoldDensity.kDensityModeNone
#densityFlags = ROOT.TUnfoldDensity.kDensityModeUser
densityFlags = ROOT.TUnfoldDensity.kDensityModeBinWidth
#densityFlags = ROOT.TUnfoldDensity.kDensityModeBinWidthAndUser

#for regMode in [ ROOT.TUnfold.kRegModeNone, ROOT.TUnfold.kRegModeSize, ROOT.TUnfold.kRegModeDerivative, ROOT.TUnfold.kRegModeCurvature ]:
#    for constraintMode in [ROOT.TUnfold.kEConstraintNone, ROOT.TUnfold.kEConstraintArea] :
#        for densityFlags in [ROOT.TUnfoldDensity.kDensityModeNone, ROOT.TUnfoldDensity.kDensityModeUser, ROOT.TUnfoldDensity.kDensityModeBinWidth, ROOT.TUnfoldDensity.kDensityModeBinWidthAndUser ]:
postfix = "_".join(map(str, [ regMode, constraintMode, densityFlags]))

unfold = ROOT.TUnfoldDensity( matrix, mapping, regMode, constraintMode, densityFlags )
unfold.SetInput( reco_spectrum )

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

hs = []
for i_factor, factor in enumerate( reversed([ 0, 0.01, 0.1, 0.5, 1, 1.5, 10, 100 ]) ):
    unfold.DoUnfold(10**(best_logtau)*factor)
    h = unfold.GetOutput("unfoldedMC")
    h.legendText = ( "log(#tau) = %6.4f" % (best_logtau + log(factor,10)) + ("(best)" if factor==1 else "") if factor > 0 else  "log(#tau) = -#infty" )
    h.style = styles.lineStyle( 1+ i_factor)
    hs.append( h )

for logY in [True, False]:
    plot = Plot.fromHisto( name = 'unfolding_comparison' + '_'+postfix + ('_log' if logY else ''),  histos = [[ h ] for h in hs], texX = "p_{T}", texY = "Events" )
    plot.stack = None
    plotting.draw(plot,
        plot_directory = plot_directory_,
        #ratio          = {'yRange':(0.6,1.4)} if len(plot.stack)>=2 else None,
        logX = False, logY = logY, sorting = False,
        #yRange         = (0.5, 1.5) ,
        #scaling        = {0:1} if len(plot.stack)==2 else {},
        legend         = [ (0.15,0.91-0.05*len(plot.histos)/2,0.95,0.91), 2 ],
      )

# closure 
unfold.DoUnfold(0)
unfolded_reco_spectrum = unfold.GetOutput("unfolded_reco_spectrum")

for logY in [True, False]:
    unfolded_reco_spectrum  .style =  styles.lineStyle( ROOT.kRed, width = 1 )
    fiducial_spectrum       .style =  styles.lineStyle( ROOT.kBlack, width = 2 )
    unfolded_reco_spectrum  .legendText = "unfolded (%6.2f)" % unfolded_reco_spectrum.Integral()
    fiducial_spectrum       .legendText = "fiducial (%6.2f)" % fiducial_spectrum.Integral()
    
    plot = Plot.fromHisto( name = 'unfolding_closure' + ('_log' if logY else ''),  histos = [[ h ] for h in [unfolded_reco_spectrum, fiducial_spectrum]], texX = "p_{T}", texY = "Events" )
    plot.stack = None
    plotting.draw(plot,
        plot_directory = plot_directory_,
        #ratio          = {'yRange':(0.6,1.4)} if len(plot.stack)>=2 else None,
        logX = False, logY = logY, sorting = False,
        #yRange         = (0.5, 1.5) ,
        #scaling        = {0:1} if len(plot.stack)==2 else {},
        legend         = [ (0.15,0.91-0.05*len(plot.histos)/2,0.95,0.91), 2 ],
      )

