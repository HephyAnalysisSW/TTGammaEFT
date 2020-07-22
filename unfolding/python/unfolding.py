# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, copy, array
from   math import log, sqrt
# RootTools
from RootTools.core.standard          import *

# Analysis
from Analysis.Tools.MergingDirDB      import MergingDirDB
from Analysis.Tools.metFilters        import getFilterCut
import Analysis.Tools.syncer

# Internal Imports
from TTGammaEFT.Tools.user            import plot_directory, cache_directory
from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter

from TTGammaEFT.Analysis.SetupHelpers import *
from TTGammaEFT.Analysis.Setup        import Setup
from TTGammaEFT.Analysis.EstimatorList   import EstimatorList
from TTGammaEFT.Analysis.regions      import *

import TTGammaEFT.unfolding.scanner as scanner

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                        help="Log level for logging")
argParser.add_argument("--plot_directory",     action="store",      default="102X_TTG_ppv1_v1",                                              help="plot sub-directory")
argParser.add_argument("--prefix",             action="store",      default=None,  type=str,                                                 help="for debugging")
argParser.add_argument("--small",              action="store_true",                                                                          help="Run only on a small subset of the data?")
argParser.add_argument("--overwrite",          action="store_true",                                                                          help="overwrite cache?")
argParser.add_argument('--settings',           action='store',      type=str, default="ptG_unfolding_closure",                               help="Settings.")

args = argParser.parse_args()

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
    line = (0.8, 0.95, "(13 TeV)") 
    lines = [
      (0.15, 0.95, "CMS #bf{#it{Preliminary}}"), 
      line
    ]
    return [tex.DrawLatex(*l) for l in lines]

if args.small: args.plot_directory += "_small"

import TTGammaEFT.unfolding.settings as settings_module
logger.info( "Unfolding settings: %s", args.settings)
settings = getattr( settings_module, args.settings )

# database
year_str        = "_".join(settings.years) + ('_'+args.prefix if args.prefix is not None else '')
cache_dir = os.path.join(cache_directory, "unfolding", year_str, "matrix")
dirDB     = MergingDirDB(cache_dir)

# specifics from the arguments
plot_directory_ = os.path.join( plot_directory, "unfolding", args.plot_directory, args.settings)
cfg_key         = ( args.small, year_str, args.settings)

read_variables = [ "weight/F", "year/I",
                   "triggered/I", "overlapRemoval/I",
                   "nPhotonGood/I", "nJetGood/I", "nBTagGood/I", "nLeptonTight/I", "nLeptonVetoIsoCorr/I", "nPhotonNoChgIsoNoSieie/I",
                   "PhotonGood0_pt/F", "PhotonGood0_eta/F","PhotonGood0_phi/F",
                   "GenPhotonCMSUnfold0_pt/F", "GenPhotonCMSUnfold0_eta/F", "GenPhotonCMSUnfold0_phi/F",
                   "genLCMStight0GammadR/F",
                   "LeptonTight0_eta/F", "LeptonTight0_phi/F", "LeptonTight0_pt/F",

                   "nGenLeptonCMSUnfold/I", "nGenPhotonCMSUnfold/I", "nGenBJetCMSUnfold/I", "nGenJetsCMSUnfold/I",
                   "reweightHEM/F", "reweightTrigger/F", "reweightL1Prefire/F", "reweightPU/F", "reweightLeptonTightSF/F", "reweightLeptonTrackingTightSF/F", "reweightPhotonSF/F", "reweightPhotonElectronVetoSF/F", "reweightBTag_SF/F",
                    "Flag_goodVertices/I", "Flag_globalSuperTightHalo2016Filter/I", "Flag_HBHENoiseFilter/I", "Flag_HBHENoiseIsoFilter/I", "Flag_EcalDeadCellTriggerPrimitiveFilter/I", "Flag_BadPFMuonFilter/I", "PV_ndof/F", "PV_x/F", "PV_y/F", "PV_z/F"
                ]

extra_read_variables = {
    "2016":[],
    "2017":["Flag_ecalBadCalibFilter/I", "Flag_ecalBadCalibFilterV2/I"],
    "2018":["Flag_ecalBadCalibFilter/I", "Flag_ecalBadCalibFilterV2/I"],
}

def draw( plot, **kwargs):
    plotting.draw(plot,
        plot_directory = plot_directory_,
        #ratio          = {'yRange':(0.6,1.4)} if len(plot.stack)>=2 else None,
        logX = False, sorting = False,
        #yRange         = (0.5, 1.5) ,
        #scaling        = {0:1} if len(plot.stack)==2 else {},
        legend         = [ (0.15,0.91-0.05*len(plot.histos)/2,0.95,0.91), 2 ],
        drawObjects    = drawObjects(),
        copyIndexPHP   = True, 
        **kwargs
      )
def draw2D( plot, **kwargs):
    plotting.draw2D( plot,
                     plot_directory = plot_directory_,
                     logX = False, logY = False, logZ = True,
                     copyIndexPHP = True,  
                     drawObjects    = drawObjects(),
                     **kwargs
                    )

loop_key = ( cfg_key, "result")
if dirDB.contains( loop_key ) and not args.overwrite:
    matrix, fiducial_spectrum, reco_spectrum, reco_fout_spectrum, yield_fid, yield_fid_reco, yield_reco = dirDB.get( loop_key )
else:

    # spectrum in fiducial region 
    fiducial_spectrum = ROOT.TH1D("fiducial_spectrum", "fiducial_spectrum", len(settings.fiducial_thresholds)-1, array.array('d', settings.fiducial_thresholds) )
    fiducial_spectrum.GetXaxis().SetTitle(settings.tex_gen)

    # spectrum in reco region 
    reco_spectrum = ROOT.TH1D("reco_spectrum", "reco_spectrum", len(settings.reco_thresholds_years)-1, array.array('d', settings.reco_thresholds_years) )
    reco_spectrum.GetXaxis().SetTitle(settings.tex_reco)

    # spectrum in reco region that is not from fiducial region
    reco_fout_spectrum = ROOT.TH1D("reco_fout_spectrum", "reco_fout_spectrum", len(settings.reco_thresholds_years)-1, array.array('d', settings.reco_thresholds_years) )
    reco_fout_spectrum.GetXaxis().SetTitle(settings.tex_reco)

    matrix = ROOT.TH2D("unfolding_matrix", "unfolding_matrix", len(settings.reco_thresholds_years)-1, array.array('d', settings.reco_thresholds_years), len(settings.fiducial_thresholds)-1, array.array('d', settings.fiducial_thresholds) )

    matrix.GetXaxis().SetTitle(settings.tex_reco)
    matrix.GetYaxis().SetTitle(settings.tex_gen)

    counter_tot      = 0
    counter_reco     = 0
    counter_fid      = 0
    counter_fid_reco = 0
    yield_tot        = 0
    yield_reco       = 0
    yield_fid        = 0
    yield_fid_reco   = 0

    for i_year, year in enumerate(settings.years):
        setup         = Setup( year=int(year), photonSelection=False, checkOnly=True, runOnLxPlus=False ) 
        setup         = setup.sysClone( parameters=allRegions[settings.reco_selection]["parameters"] )
        # reco selection
        reco_selection = setup.selection( "MC", channel="all", **setup.defaultParameters() )

        MET_filter_cut   = "(year==%s&&"%year+getFilterCut(isData=False, year=int(year), skipBadChargedCandidate=True)+")"
        reco_selection_str = MET_filter_cut+"&&triggered&&overlapRemoval==1&&"+cutInterpreter.cutString(reco_selection['prefix'])

        # fiducial seletion
        fiducial_selection_str = cutInterpreter.cutString(settings.fiducial_selection)+"&&overlapRemoval==1"

        ttreeFormulas = {
                    'is_fiducial': fiducial_selection_str, 
                    'is_reco':     reco_selection_str, 
                    'gen_weight'    : 'weight*(35.92*(year==2016)+41.53*(year==2017)+59.74*(year==2018))', 
                    'reco_reweight' : 'reweightHEM*reweightTrigger*reweightPU*reweightL1Prefire*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF', 
                }

        # Sample for this year (fix)
        ttg0l = Sample.fromDirectory("ttg0l_%s"%year, directory = ["/scratch/lukas.lechner/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_{year}_TTG_private_v48/inclusive/TTGHad_LO/".format(year=year)])
        ttg1l = Sample.fromDirectory("ttg1l_%s"%year, directory = ["/scratch/lukas.lechner/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_{year}_TTG_private_v48/inclusive/TTGSingleLep_LO/".format(year=year)])
        ttg2l = Sample.fromDirectory("ttg2l_%s"%year, directory = ["/scratch/lukas.lechner/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_{year}_TTG_private_v48/inclusive/TTGLep_LO/".format(year=year)])

        sample = Sample.combine( "ttg_%s"%year, [ttg1l, ttg2l, ttg0l] )

        # check if variables are TTreeFormulas
        if type( settings.reco_variable ) == type({}) and len(settings.reco_variable)==1:
            reco_variable_name = settings.reco_variable.keys()[0]
            ttreeFormulas.update( settings.reco_variable )
        else:
            reco_variable_name = settings.reco_variable
        if type( settings.fiducial_variable ) == type({}) and len(settings.fiducial_variable)==1:
            fiducial_variable_name = settings.fiducial_variable.keys()[0]
            ttreeFormulas.update( settings.fiducial_variable )
        else:
            fiducial_variable_name = settings.fiducial_variable
 

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
            shift_year =  i_year*settings.max_reco_val

            # reco observable 
            reco_variable_val       = getattr( r.event, reco_variable_name )

            # put reco overflow in the last bin
            if reco_variable_val >= settings.max_reco_val and (settings.reco_overflow in ["upper","both"]):
                reco_variable_val = settings.max_reco_bincenter 

            # fiducial observable 
            fiducial_variable_val   = getattr( r.event, fiducial_variable_name ) 

            # put fiducial overflow in the last bin
            if fiducial_variable_val >= settings.max_fiducial_val and (settings.fiducial_overflow in ["upper", "both"] ):
                fiducial_variable_val = settings.max_fiducial_bincenter 

            # Sanity check: A fiducial event should have a fiducial_variable_val that is within the fiducial thresholds
            val_in_fiducial = ( fiducial_variable_val>=settings.fiducial_thresholds[0] and fiducial_variable_val<settings.fiducial_thresholds[-1] )
            assert val_in_fiducial or not r.event.is_fiducial, "Fiducial variable %s=%f not in fiducial regions %r"%( settings.fiducial_variable, fiducial_variable_val, settings.fiducial_thresholds )
            # Sanity check: A reco event should have a reco_variable_val that is within the reco thresholds
            val_in_reco = ( reco_variable_val>=settings.reco_thresholds[0] and reco_variable_val<settings.reco_thresholds[-1] )
            assert val_in_reco or not r.event.is_reco, "reco variable %s=%f not in reco regions %r"%( settings.reco_variable, reco_variable_val, settings.reco_thresholds )
                 
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
                    matrix.Fill(settings.reco_variable_underflow, fiducial_variable_val, gen_weight_val*(1-reco_reweight_val))

                # f_out / fakes / backgrounds (signal events generated outside the fiducial region but reconstructed in the reco phase space)
                else:
                    # should not go in the matrix according to S. Schmitt 20/08/16
                    # matrix.Fill(reco_variable_val+shift_year, settings.underflow_fiducial_val, gen_weight_val*reco_reweight_val)
                    reco_fout_spectrum.Fill( reco_variable_val+shift_year, gen_weight_val*reco_reweight_val )

                    # inefficiency of the background according to reco_reweight -> should not be needed 
                    #matrix.Fill(settings.reco_variable_underflow, underflow_fiducial_val, gen_weight_val*(1-reco_reweight_val))
            else:
                # inefficiency according to the selection
                if  r.event.is_fiducial:
                    matrix.Fill(settings.reco_variable_underflow, fiducial_variable_val, gen_weight_val)

            if r.event.is_fiducial: # note: there is no reco_reweight_val because we construct the gen spectrum
                # counter
                counter_fid += 1
                yield_fid   += gen_weight_val

                fiducial_spectrum.Fill( fiducial_variable_val, gen_weight_val ) 

        logger.info("total: %6.2f (%6.2f) fiducial: %6.2f (%6.2f) fiducial+reco %6.2f (%6.2f) reco-total: %6.2f (%6.2f)", yield_tot, counter_tot, yield_fid, counter_fid, yield_fid_reco, counter_fid_reco, yield_reco, counter_reco)

    dirDB.add( loop_key, (matrix, fiducial_spectrum, reco_spectrum, reco_fout_spectrum, yield_fid, yield_fid_reco, yield_reco), overwrite=True )

# Unfolding matrix
plot_matrix = Plot2D.fromHisto("unfolding_matrix", [[matrix]], texY = settings.tex_gen, texX = settings.tex_reco + " +%i*(year-2016)"%settings.max_reco_val )
draw2D( plot_matrix, widths = {'x_width':500*len(settings.years)} )

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

logger.info("Total over all matrix reco bins (including fid overflows and f_out of %6.2f): %6.2f. yield in fiducial space: %6.2f <- these numbers should agree.", reco_fout_spectrum.Integral(), tot_reco+reco_fout_spectrum.Integral(), yield_reco)

# fout subtraction
def fout_subtraction( histo ):
    histo_ = histo.Clone(histo.GetName()+'_fout_subtracted')
    histo_.Scale(-1)
    histo_.Add(reco_fout_spectrum)
    histo_.Scale(-1)
    return histo_

reco_spectrum_subtracted = fout_subtraction( reco_spectrum )

reco_spectrum_subtracted.legendText = "reco (f_{out} subtracted)"
reco_fout_spectrum.legendText = "reco f_{out}"
reco_spectrum.legendText = "reco before subtraction"
reco_spectrum_subtracted.style = styles.lineStyle( ROOT.kRed) 
reco_fout_spectrum.style       = styles.lineStyle( ROOT.kGreen)       
reco_spectrum.style            = styles.lineStyle( ROOT.kBlue)      

for logY in [True]:
    plot = Plot.fromHisto( name = 'fout_subtraction' + ('_log' if logY else ''),  histos = [[ reco_spectrum ], [reco_spectrum_subtracted], [reco_fout_spectrum] ], texX = "p_{T}", texY = "Events" )
    plot.stack = None
    draw(plot, logY = logY)

stuff = []
def getOutput( input_spectrum, name = "unfolded_spectrum", tau = 0.): #Why should TUnfold and TUnfoldDensity have the same interface???
    if isinstance( unfold, ROOT.TUnfoldDensity ):
        unfold.SetInput( input_spectrum, 1.0)
        unfold.DoUnfold(tau)
        return unfold.GetOutput(name)
    elif isinstance( unfold, ROOT.TUnfold ):
        unfolded_mc_spectrum = matrix.ProjectionY(name)
        stuff.append( unfolded_mc_spectrum )
        unfolded_mc_spectrum.Clear()
        unfold.SetInput( input_spectrum, 1.0)
        unfold.DoUnfold(tau)
        unfold.GetOutput(unfolded_mc_spectrum)
        return unfolded_mc_spectrum

# regularization
#regMode = ROOT.TUnfold.kRegModeNone
#regMode = ROOT.TUnfold.kRegModeSize
#regMode = ROOT.TUnfold.kRegModeDerivative
regMode = ROOT.TUnfold.kRegModeCurvature
#regMode = ROOT.TUnfold.kRegModeMixed

# extra contrains
constraintMode = ROOT.TUnfold.kEConstraintNone
#constraintMode = ROOT.TUnfold.kEConstraintArea

mapping = ROOT.TUnfold.kHistMapOutputVert
#mapping = ROOT.TUnfold.kHistMapOutputHoriz

#unfold = ROOT.TUnfoldDensity( matrix, mapping, regMode, constraintMode, densityFlags)
unfold = ROOT.TUnfold( matrix, mapping, regMode, constraintMode)

unfolded_mc_spectrum = getOutput( reco_spectrum_subtracted, "unfolded_mc_spectrum_subtracted", tau=0)

## L Curve scanning
#lCurveScanner = scanner.LCurveScanner()
#lCurveScanner.scan_L( unfold, 200, 5*10**-5, 5)
#lCurveScanner.plot_scan_L_curve(plot_directory_)
#lCurveScanner.plot_scan_L_curvature(plot_directory_)
#
#best_logtau = log(lCurveScanner.tau, 10)
#
#hs = []
#for i_factor, factor in enumerate( reversed([  0, 0.5, 1, 1.5, 2 ]) ):
#    h = getOutput(reco_spectrum_subtracted, tau=10**(best_logtau)*factor)
#    h.legendText = ( "log(#tau) = %6.4f" % (best_logtau + log(factor,10)) + ("(best)" if factor==1 else "") if factor > 0 else  "log(#tau) = -#infty" )
#    h.style = styles.lineStyle( 1+ i_factor)
#    hs.append( h )
#for logY in [True]:
#    plot = Plot.fromHisto( name = 'unfolding_comparison' + ('_log' if logY else ''),  histos = [[ h ] for h in hs], texX = "p_{T}", texY = "Events" )
#    plot.stack = None
#    draw(plot, logY = logY)

# closure 

for logY in [True, False]:
    unfolded_mc_spectrum  .style =  styles.lineStyle( ROOT.kRed, width = 1, errors=True)
    fiducial_spectrum     .style =  styles.lineStyle( ROOT.kBlack, width = 2, errors=True)
    unfolded_mc_spectrum  .legendText = "unfolded (%6.2f)" % unfolded_mc_spectrum.Integral()
    fiducial_spectrum     .legendText = "fiducial (%6.2f)" % fiducial_spectrum.Integral()
    
    plot = Plot.fromHisto( name = 'unfolding_closure' + ('_log' if logY else ''),  histos = [[ h ] for h in [fiducial_spectrum, unfolded_mc_spectrum]], texX = "p_{T}", texY = "Events" )
    plot.stack = None
    draw(plot, logY = logY)

if not hasattr(settings, "unfolding_data_input"):
    sys.exit(0)

# input plot unsubtracted
boxes = []
ratio_boxes = []
for band in reversed(settings.systematic_bands):
    for i in range(1, band['ref'].GetNbinsX()+1):
        box = ROOT.TBox( band['ref'].GetXaxis().GetBinLowEdge(i),  
                         band['down'].GetBinContent(i),
                         band['ref'].GetXaxis().GetBinUpEdge(i),
                         band['up'].GetBinContent(i),
             )
        box.SetLineColor(band['color'])
        box.SetFillStyle(3244)
        box.SetFillColor(band['color'])
        boxes.append(box)

        if band['ref'].GetBinContent(i)!=0: 
            ratio_box = ROOT.TBox( band['ref'].GetXaxis().GetBinLowEdge(i),  
                             band['down'].GetBinContent(i)/band['ref'].GetBinContent(i),
                             band['ref'].GetXaxis().GetBinUpEdge(i),
                             band['up'].GetBinContent(i)/band['ref'].GetBinContent(i),
                 )
            ratio_box.SetLineColor(band['color'])
            ratio_box.SetFillStyle(3244)
            ratio_box.SetFillColor(band['color'])
            ratio_boxes.append(ratio_box)

settings.unfolding_data_input.style = styles.errorStyle( ROOT.kBlack )
settings.unfolding_mc_input.style   = styles.lineStyle( ROOT.kBlue, width = 2)

settings.unfolding_data_input.legendText = settings.data_legendText 
settings.unfolding_mc_input.legendText   = settings.mc_legendText

plotting.draw(
    Plot.fromHisto( "input_spectrum",
                [[settings.unfolding_mc_input],[settings.unfolding_data_input]],
                texX = settings.tex_reco,
                texY = "Number of events",
            ),
    plot_directory = plot_directory_,
    logX = False, logY = True, sorting = False,
    #legend = None,
    legend         = [ (0.15,0.91-0.05*len(plot.histos)/2,0.95,0.91), 2 ],
    yRange = settings.y_range,
    ratio = {'yRange': (0.3, 1.7), 'texY':'Data / Sim.', 'histos':[(1,0)], 'drawObjects':ratio_boxes} ,
    drawObjects = drawObjects()+boxes,
    #drawObjects = boxes,
    redrawHistos = True,
)

# input plot subtracted
boxes = []
ratio_boxes = []
for band in reversed(settings.systematic_bands):
    # subtraction of nominal f_out 
    band['ref_subtracted']  = fout_subtraction(band['ref'])
    band['down_subtracted'] = fout_subtraction(band['down'])
    band['up_subtracted']   = fout_subtraction(band['up'])

    for i in range(1, band['ref'].GetNbinsX()+1):
        box = ROOT.TBox( band['ref_subtracted'].GetXaxis().GetBinLowEdge(i),  
                         band['down_subtracted'].GetBinContent(i),
                         band['ref_subtracted'].GetXaxis().GetBinUpEdge(i),
                         band['up_subtracted'].GetBinContent(i),
             )
        box.SetLineColor(band['color'])
        box.SetFillStyle(3244)
        box.SetFillColor(band['color'])
        boxes.append(box)

        if band['ref_subtracted'].GetBinContent(i)!=0: 
            ratio_box = ROOT.TBox( band['ref_subtracted'].GetXaxis().GetBinLowEdge(i),  
                             band['down_subtracted'].GetBinContent(i)/band['ref_subtracted'].GetBinContent(i),
                             band['ref_subtracted'].GetXaxis().GetBinUpEdge(i),
                             band['up_subtracted'].GetBinContent(i)/band['ref_subtracted'].GetBinContent(i),
                 )
            ratio_box.SetLineColor(band['color'])
            ratio_box.SetFillStyle(3244)
            ratio_box.SetFillColor(band['color'])
            ratio_boxes.append(ratio_box)

unfolding_data_input_subtracted = fout_subtraction( settings.unfolding_data_input )
unfolding_mc_input_subtracted   = fout_subtraction( settings.unfolding_mc_input )

unfolding_data_input_subtracted.style = styles.errorStyle( ROOT.kBlack )
unfolding_mc_input_subtracted.style   = styles.lineStyle( ROOT.kBlue, width = 2)

unfolding_data_input_subtracted.legendText = settings.data_legendText 
unfolding_mc_input_subtracted.legendText   = settings.mc_legendText

plotting.draw(
    Plot.fromHisto( "input_spectrum_subtracted",
                [[unfolding_mc_input_subtracted],[unfolding_data_input_subtracted]],
                texX = settings.tex_reco,
                texY = "Number of events",
            ),
    plot_directory = plot_directory_,
    logX = False, logY = True, sorting = False,
    #legend = None,
    legend         = [ (0.15,0.91-0.05*len(plot.histos)/2,0.95,0.91), 2 ],
    yRange = settings.y_range,
    ratio = {'yRange': (0.3, 1.7), 'texY':'Data / Sim.', 'histos':[(1,0)], 'drawObjects':ratio_boxes} ,
    drawObjects = drawObjects()+boxes,
    #drawObjects = boxes,
    redrawHistos = True,
)

# unfolding the data

unfolding_data_output = getOutput(unfolding_data_input_subtracted, "unfolding_data_input_subtracted")
unfolding_data_output.Scale(1./settings.lumi_factor)

# unfolding the mc
unfolding_mc_output = getOutput(unfolding_mc_input_subtracted, "unfolding_mc_input_subtracted")
unfolding_mc_output.Scale(1./settings.lumi_factor)

# unfolding the error bands
boxes = []
ratio_boxes = []
for band in reversed(settings.systematic_bands):
    band['up_unfolded']   = getOutput(band['up_subtracted'], "band_%s_up_unfolded"%band['name'])
    band['down_unfolded'] = getOutput(band['down_subtracted'], "band_%s_down_unfolded"%band['name'])
    band['ref_unfolded']  = getOutput(band['ref_subtracted'], "band_%s_ref_unfolded"%band['name'])

    for h in [ band['up_unfolded'], band['down_unfolded'], band['ref_unfolded']]:
       h.Scale(1./settings.lumi_factor)

    for i in range(1, band['ref_unfolded'].GetNbinsX()+1):
        box = ROOT.TBox( band['ref_unfolded'].GetXaxis().GetBinLowEdge(i),  
                         band['down_unfolded'].GetBinContent(i),
                         band['ref_unfolded'].GetXaxis().GetBinUpEdge(i),
                         band['up_unfolded'].GetBinContent(i),
             )
        box.SetLineColor(band['color'])
        box.SetFillStyle(3244)
        box.SetFillColor(band['color'])
        boxes.append(box)

        if band['ref_unfolded'].GetBinContent(i)!=0: 
            ratio_box = ROOT.TBox( band['ref_unfolded'].GetXaxis().GetBinLowEdge(i),  
                             band['down_unfolded'].GetBinContent(i)/band['ref_unfolded'].GetBinContent(i),
                             band['ref_unfolded'].GetXaxis().GetBinUpEdge(i),
                             band['up_unfolded'].GetBinContent(i)/band['ref_unfolded'].GetBinContent(i),
                 )
            ratio_box.SetLineColor(band['color'])
            ratio_box.SetFillStyle(3244)
            ratio_box.SetFillColor(band['color'])
            ratio_boxes.append(ratio_box)

unfolding_data_output.style = styles.errorStyle( ROOT.kBlack )
unfolding_mc_output.style   = styles.lineStyle( ROOT.kBlue, width = 2)

unfolding_data_output.legendText = settings.data_legendText 
unfolding_mc_output.legendText   = settings.mc_legendText

plotting.draw(
    Plot.fromHisto( "unfolded_spectrum",
                [[unfolding_mc_output],[unfolding_data_output]],
                texX = settings.tex_unf,
                texY = settings.texY,
            ),
    plot_directory = plot_directory_,
    logX = False, logY = True, sorting = False, 
    #legend = None,
    legend         = [ (0.15,0.91-0.05*len(plot.histos)/2,0.95,0.91), 2 ],
    yRange = settings.y_range,
    ratio = {'yRange': settings.y_range_ratio, 'texY':'Data / Sim.', 'histos':[(1,0)], 'drawObjects':ratio_boxes} ,
    drawObjects = drawObjects()+boxes,
    #drawObjects = boxes,
    redrawHistos = True,
)

def get_TMatrixD( histo ):
    Tmatrix = ROOT.TMatrixD(histo.GetNbinsX(),histo.GetNbinsY())
    for i in range( histo.GetNbinsX() ): 
        for j in range( histo.GetNbinsY() ):
            Tmatrix[i][j] = histo.GetBinContent(i+1,j+1)
    return Tmatrix

# probability matrix

# Do it once again!
unfolding_data_output = getOutput(settings.unfolding_data_input, "unfolding_data_input")

probability_matrix = matrix.Clone()
probability_matrix.Clear()
unfold.GetProbabilityMatrix(probability_matrix,mapping)
probability_TMatrix = get_TMatrixD( probability_matrix )
plot_probability_matrix = Plot2D.fromHisto("probability_matrix", [[probability_matrix]], texY = plot_matrix.texY, texX = plot_matrix.texX )
draw2D( plot_probability_matrix )

# output covariance matrix
output_covariance_matrix = ROOT.TH2D("output_covariance_matrix", "output_covariance_matrix", len(settings.fiducial_thresholds)-1, array.array('d', settings.fiducial_thresholds), len(settings.fiducial_thresholds)-1, array.array('d', settings.fiducial_thresholds) )
unfold.GetEmatrix( output_covariance_matrix )
output_covariance_TMatrix = get_TMatrixD( output_covariance_matrix )

plot_output_covariance_matrix = Plot2D.fromHisto("output_covariance_matrix", [[output_covariance_matrix]], texY = settings.tex_gen, texX = settings.tex_gen )
draw2D( plot_output_covariance_matrix )

# output correlation matrix
output_correlation_matrix = output_covariance_matrix.Clone("output_correlation_matrix")
for i in range( 1, output_correlation_matrix.GetNbinsX()+1 ): 
    for j in range( 1, output_correlation_matrix.GetNbinsY()+1 ): 
        if output_correlation_matrix.GetBinContent(i,i)!=0 and output_correlation_matrix.GetBinContent(j,j)!=0:
            output_correlation_matrix.SetBinContent(i, j, output_covariance_matrix.GetBinContent(i,j)/sqrt(output_covariance_matrix.GetBinContent(i,i)*output_covariance_matrix.GetBinContent(j,j)))
        else:
            output_correlation_matrix.SetBinContent(i, j, 0.)

plot_output_correlation_matrix = Plot2D.fromHisto("output_correlation_matrix", [[output_correlation_matrix]], texY = settings.tex_gen, texX = settings.tex_gen )
draw2D( plot_output_correlation_matrix )

# input inverse covariance matrix
input_inverse_covariance_matrix = ROOT.TH2D("input_inverse_covariance_matrix", "input_inverse_covariance_matrix", len(settings.reco_thresholds)-1, array.array('d', settings.reco_thresholds), len(settings.reco_thresholds)-1, array.array('d', settings.reco_thresholds) )
unfold.GetInputInverseEmatrix( input_inverse_covariance_matrix )
input_inverse_covariance_TMatrix = get_TMatrixD( input_inverse_covariance_matrix )

plot_input_inverse_covariance_matrix = Plot2D.fromHisto("input_inverse_covariance_matrix", [[input_inverse_covariance_matrix]], texY = settings.tex_reco, texX = settings.tex_reco )
draw2D( plot_input_inverse_covariance_matrix )

# input covariance matrix
input_inverse_covariance_TMatrix = get_TMatrixD( input_inverse_covariance_matrix )
input_covariance_TMatrix = input_inverse_covariance_TMatrix.Clone() 
input_covariance_TMatrix.Invert()
input_covariance_matrix = ROOT.TH2D("input_covariance_matrix", "input_covariance_matrix", len(settings.reco_thresholds)-1, array.array('d', settings.reco_thresholds), len(settings.reco_thresholds)-1, array.array('d', settings.reco_thresholds) )
for i in range( input_covariance_matrix.GetNbinsX() ): 
    for j in range( input_covariance_matrix.GetNbinsY() ):
        input_covariance_matrix.SetBinContent(i+1,j+1,input_covariance_TMatrix[i][j]) 
plot_input_covariance_matrix = Plot2D.fromHisto("input_covariance_matrix", [[input_covariance_matrix]], texY = settings.tex_reco, texX = settings.tex_reco )
draw2D( plot_input_covariance_matrix )

input_correlation_matrix = input_covariance_matrix.Clone("input_correlation_matrix")
for i in range( 1, input_correlation_matrix.GetNbinsX()+1 ): 
    for j in range( 1, input_correlation_matrix.GetNbinsY()+1 ): 
        if input_correlation_matrix.GetBinContent(i,i)!=0 and input_correlation_matrix.GetBinContent(j,j)!=0:
            input_correlation_matrix.SetBinContent(i, j, input_covariance_matrix.GetBinContent(i,j)/sqrt(input_covariance_matrix.GetBinContent(i,i)*input_covariance_matrix.GetBinContent(j,j)))
        else:
            input_correlation_matrix.SetBinContent(i, j, 0.)

plot_input_correlation_matrix = Plot2D.fromHisto("input_correlation_matrix", [[input_correlation_matrix]], texY = settings.tex_reco, texX = settings.tex_reco )
draw2D( plot_input_correlation_matrix )


##Vxx_Inv = ROOT.TMatrixD( ROOT.TMatrixD(probability_TMatrix, ROOT.TMatrixD.kMult, input_inverse_covariance_TMatrix), ROOT.TMatrixD.kMult, ROOT.TMatrixD(ROOT.TMatrixD.kTransposed,probability_TMatrix) )
#Vxx_Inv = ROOT.TMatrixD( ROOT.TMatrixD(ROOT.TMatrixD(ROOT.TMatrixD.kTransposed,probability_TMatrix), ROOT.TMatrixD.kMult, input_inverse_covariance_TMatrix), ROOT.TMatrixD.kMult, probability_TMatrix )
#
#Vxx = ROOT.TMatrixD( ROOT.TMatrixD.kInverted, Vxx_Inv )


#Vxx = Dxy Vyy^-1 Dxy^T
#    = (E A^T Vyy^-1) Vyy (E A^T Vyy^-1)^T
#    = (A^T V_yy^-1 A)^-1 A^T Vyy^-1 Vyy ((A^T V_yy^-1 A)^-1 A^T Vyy^-1)^T 
#    = (A^T V_yy^-1 A)^-1 A^T Vyy^-1 A (A^T V_yy^-1 A)^-1^T
#    = (A^T V_yy^-1 A)^-1^T
#    = (A^T V_yy^-1 A)^-1
#
#
#
#NR: E A^T Vyy^-1 = (A^T V_yy^-1 A)^-1 A^T Vyy^-1
#                 (= A^-1)
