# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import uuid
import os, sys, copy, array
from   math import log, sqrt
# RootTools
from RootTools.core.standard          import *
from RootTools.plot.helpers    import copyIndexPHP

# Analysis
from Analysis.Tools.MergingDirDB      import MergingDirDB
from Analysis.Tools.metFilters        import getFilterCut
import Analysis.Tools.syncer

# Internal Imports
from TTGammaEFT.Tools.user            import plot_directory, cache_directory
from TTGammaEFT.Tools.cutInterpreter  import cutInterpreter

from TTGammaEFT.unfolding.settings_uncertainty import all_systematics, systematic_pairs

from TTGammaEFT.Analysis.SetupHelpers import *
from TTGammaEFT.Analysis.Setup        import Setup
from TTGammaEFT.Analysis.EstimatorList   import EstimatorList
from TTGammaEFT.Analysis.regions      import *

import TTGammaEFT.unfolding.scanner as scanner

from helpers import sumNuisanceHistos

# Default Parameter
loggerChoices = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--logLevel",           action="store",      default="INFO", nargs="?", choices=loggerChoices,                        help="Log level for logging")
argParser.add_argument("--plot_directory",     action="store",      default="v49_uncertainty",                                               help="plot sub-directory")
argParser.add_argument("--prefix",             action="store",      default=None,  type=str,                                                 help="for debugging")
argParser.add_argument("--small",              action="store_true",                                                                          help="Run only on a small subset of the data?")
argParser.add_argument("--inclusive_samples",  action="store_true",                                                                          help="use inclusive samples?")
argParser.add_argument("--extended",           action="store_true",                                                                          help="Write extended output?")
argParser.add_argument("--overwrite",          action="store_true",                                                                          help="overwrite cache?")
argParser.add_argument('--settings',           action='store',      type=str, default="ptG_unfolding_closure",                               help="Settings.")
argParser.add_argument('--systematic',         action='store',      type=str, default=None, choices = all_systematics,                  help="Run a systematic?")


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

import TTGammaEFT.unfolding.settings_uncertainty as settings_module
logger.info( "Unfolding settings: %s", args.settings)
settings = getattr( settings_module, args.settings )

# database
year_str        = "_".join(settings.years) + ('_'+args.prefix if args.prefix is not None else '')
run2 = all( y in year_str for y in ["2016", "2017", "2018"] )
cache_dir = os.path.join(cache_directory, "unfolding", year_str, "matrix")
dirDB     = MergingDirDB(cache_dir)

# specifics from the arguments
plot_directory_ = os.path.join( plot_directory, "unfolding", args.plot_directory, args.settings)
copyIndexPHP( plot_directory_ )
copyIndexPHP( plot_directory_ + "/uncertainties/" )
copyIndexPHP( plot_directory_ + "/uncertainties_unfolded/" )
cfg_key         = ( args.small, year_str, args.settings, args.plot_directory)

read_variables = [ "weight/F", "year/I",
                   "triggered/I", "overlapRemoval/I", "pTStitching/I",
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
        legend         = [ (0.20,0.75,0.9,0.91), 2 ],
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

# We'r doing the full thing. Try to load systemtic variations
if args.systematic is None:

    # load the variations
    missing = []
    sys_matrix = {}
    for systematic in all_systematics:

        loop_key = ( cfg_key, systematic )

        if dirDB.contains( loop_key ) and not args.overwrite:
            sys_matrix[systematic],_,_,_,_,_,_  = dirDB.get( loop_key )
            # load the nominal if args.systematic is None:
            if systematic =='nominal':
                matrix, fiducial_spectrum, reco_spectrum, reco_fout_spectrum, yield_fid, yield_fid_reco, yield_reco = dirDB.get( loop_key )
        else:
            sys_matrix['systematic']            = None
            missing.append( ['python', 'unfolding_uncertainty.py', '--settings', args.settings, '--systematic', systematic] )
            if args.overwrite:
                missing[-1].append('--overwrite')
    if len(missing)>0:
        with open("missing.sh", "a") as file_object:
            #file_object.write("#!/bin/sh\n") 
            # Append 'hello' at the end of file
            for m in missing:
                file_object.write(" ".join(m)+'\n') 
            file_object.close()
        logger.info("You need to run systematic variations: %s. Added them to missing.sh.", ",".join([ m[-1] for m in missing] ))
        sys.exit(0)

loop_key = ( cfg_key, args.systematic )
if not args.systematic is None and dirDB.contains( loop_key ) and not args.overwrite:
    matrix, fiducial_spectrum, reco_spectrum, reco_fout_spectrum, yield_fid, yield_fid_reco, yield_reco = dirDB.get( loop_key )
    logger.info("Foung results for systematic %s in cache.", args.systematic)
elif not args.systematic is None:
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

        # skip years with no effect (for jes)
        useSystematic = args.systematic
        if any(y in args.systematic for y in ["2016","2017","2018"]) and not year in args.systematic:
            useSystematic = "nominal"

        setup         = Setup( year=int(year), photonSelection=False, checkOnly=True, runOnLxPlus=False ) 
        setup         = setup.sysClone( parameters=allRegions[settings.reco_selection]["parameters"] )
        # reco selection
        reco_selection = setup.selection( "MC", channel="all", **setup.defaultParameters() )

        MET_filter_cut     = "(year==%s&&"%year+getFilterCut(isData=False, year=int(year), skipBadChargedCandidate=True)+")"
        reco_selection_str = MET_filter_cut+"&&triggered==1&&overlapRemoval==1&&"+cutInterpreter.cutString(reco_selection['prefix'])
        if not args.inclusive_samples and useSystematic not in ["TuneUp","TuneDown","erdOn","GluonMove","QCDbased"]:
            reco_selection_str+="&&pTStitching==1"
        reco_reweight_str  = 'reweightHEM*reweightTrigger*reweightPU*reweightL1Prefire*reweightLeptonTightSF*reweightLeptonTrackingTightSF*reweightPhotonSF*reweightPhotonElectronVetoSF*reweightBTag_SF'
    
        jesSystematics  = [("jes"+v+"Up","jes"+v+"Down") for v in ['FlavorQCD', 'RelativeBal', 'HF', 'BBEC1', 'EC2', 'Absolute', 'Absolute_%i'%int(year), 'HF_%i'%int(year), 'EC2_%i'%int(year), 'RelativeSample_%i'%int(year), 'BBEC1_%i'%int(year)]]
        jesSystematics += [("jerUp","jerDown")]
        jesSystematics  = sum([list(p) for p in jesSystematics],[])

        # apply systematic variations
        if useSystematic in ['nominal','TuneUp','TuneDown','erdOn','GluonMove','QCDbased']:
            pass
        # weight based
        elif useSystematic == 'photonSFUp':
            reco_reweight_str = reco_reweight_str.replace('reweightPhotonSF','reweightPhotonSFUp')
            read_variables.append( "reweightPhotonSFUp/F" )
        elif useSystematic == 'photonSFDown':
            reco_reweight_str = reco_reweight_str.replace('reweightPhotonSF','reweightPhotonSFDown')
            read_variables.append( "reweightPhotonSFDown/F" )

        elif useSystematic == 'photonElectronVetoSFUp':
            reco_reweight_str = reco_reweight_str.replace('reweightPhotonElectronVetoSF','reweightPhotonElectronVetoSFUp')
            read_variables.append( "reweightPhotonElectronVetoSFUp/F" )
        elif useSystematic == 'photonElectronVetoSFDown':
            reco_reweight_str = reco_reweight_str.replace('reweightPhotonElectronVetoSF','reweightPhotonElectronVetoSFDown')
            read_variables.append( "reweightPhotonElectronVetoSFDown/F" )

        elif useSystematic == 'reweightTopPt':
            reco_reweight_str = reco_reweight_str + "*reweightTopPt"
            read_variables.append( "reweightTopPt/F" )

        elif useSystematic == 'TriggerUp':
            reco_reweight_str = reco_reweight_str.replace('reweightTrigger','reweightTriggerUp')
            read_variables.append( "reweightTriggerUp/F" )
        elif useSystematic == 'TriggerDown':
            reco_reweight_str = reco_reweight_str.replace('reweightTrigger','reweightTriggerDown')
            read_variables.append( "reweightTriggerDown/F" )

        elif useSystematic == 'BTag_SF_b_Up':
            reco_reweight_str = reco_reweight_str.replace('reweightBTag_SF','reweightBTag_SF_b_Up')
            read_variables.append( "reweightBTag_SF_b_Up/F" )
        elif useSystematic == 'BTag_SF_b_Down':
            reco_reweight_str = reco_reweight_str.replace('reweightBTag_SF','reweightBTag_SF_b_Down')
            read_variables.append( "reweightBTag_SF_b_Down/F" )

        elif useSystematic == 'BTag_SF_l_Up':
            reco_reweight_str = reco_reweight_str.replace('reweightBTag_SF','reweightBTag_SF_l_Up')
            read_variables.append( "reweightBTag_SF_l_Up/F" )
        elif useSystematic == 'BTag_SF_l_Down':
            reco_reweight_str = reco_reweight_str.replace('reweightBTag_SF','reweightBTag_SF_l_Down')
            read_variables.append( "reweightBTag_SF_l_Down/F" )

        elif useSystematic == 'LeptonTrackingTightSFUp':
            reco_reweight_str = reco_reweight_str.replace('reweightLeptonTrackingTightSF','reweightLeptonTrackingTightSFUp')
            read_variables.append( "reweightLeptonTrackingTightSFUp/F" )
        elif useSystematic == 'LeptonTrackingTightSFDown':
            reco_reweight_str = reco_reweight_str.replace('reweightLeptonTrackingTightSF','reweightLeptonTrackingTightSFDown')
            read_variables.append( "reweightLeptonTrackingTightSFDown/F" )

        elif useSystematic == 'LeptonTightSFUp':
            reco_reweight_str = reco_reweight_str.replace('reweightLeptonTightSF','reweightLeptonTightSFUp')
            read_variables.append( "reweightLeptonTightSFUp/F" )
        elif useSystematic == 'LeptonTightSFDown':
            reco_reweight_str = reco_reweight_str.replace('reweightLeptonTightSF','reweightLeptonTightSFDown')
            read_variables.append( "reweightLeptonTightSFDown/F" )

        elif useSystematic == 'LeptonTightSFStatUp':
            reco_reweight_str = reco_reweight_str.replace('reweightLeptonTightSF','reweightLeptonTightSFStatUp')
            read_variables.append( "reweightLeptonTightSFStatUp/F" )
        elif useSystematic == 'LeptonTightSFStatDown':
            reco_reweight_str = reco_reweight_str.replace('reweightLeptonTightSF','reweightLeptonTightSFStatDown')
            read_variables.append( "reweightLeptonTightSFStatDown/F" )

        elif useSystematic == 'LeptonTightSFSystUp':
            reco_reweight_str = reco_reweight_str.replace('reweightLeptonTightSF','reweightLeptonTightSFSystUp')
            read_variables.append( "reweightLeptonTightSFSystUp/F" )
        elif useSystematic == 'LeptonTightSFSystDown':
            reco_reweight_str = reco_reweight_str.replace('reweightLeptonTightSF','reweightLeptonTightSFSystDown')
            read_variables.append( "reweightLeptonTightSFSystDown/F" )

        elif useSystematic == 'L1PrefireUp':
            reco_reweight_str = reco_reweight_str.replace('reweightL1Prefire','reweightL1PrefireUp')
            read_variables.append( "reweightL1PrefireUp/F" )
        elif useSystematic == 'L1PrefireDown':
            reco_reweight_str = reco_reweight_str.replace('reweightL1Prefire','reweightL1PrefireDown')
            read_variables.append( "reweightL1PrefireDown/F" )

        elif useSystematic == 'PUUp':
            reco_reweight_str = reco_reweight_str.replace('reweightPU','reweightPUUp')
            read_variables.append( "reweightPUUp/F" )
        elif useSystematic == 'PUDown':
            reco_reweight_str = reco_reweight_str.replace('reweightPU','reweightPUDown')
            read_variables.append( "reweightPUDown/F" )

        # selection based
        elif useSystematic in ["eResUp", "eResDown", "eScaleUp", "eScaleDown"]:
            # changing the reco variable
            replacements = [(var, var+'_'+useSystematic) for var in ["nLeptonTight", "nElectronTight", "nLeptonVetoIsoCorr", "nPhotonGood", "nPhotonNoChgIsoNoSieie", "triggered"]]
            replacements.append( ("PhotonGood0_pt",  "PhotonGood0_%s_pt"%useSystematic) )
            replacements.append( ("PhotonGood0_eta", "PhotonGood0_%s_eta"%useSystematic) )
            replacements.append( ("PhotonGood0_phi", "PhotonGood0_%s_phi"%useSystematic) )
            replacements.append( ("LeptonTight0_pt",  "LeptonTight0_%s_pt"%useSystematic) )
            replacements.append( ("LeptonTight0_eta", "LeptonTight0_%s_eta"%useSystematic) )
            replacements.append( ("LeptonTight0_phi", "LeptonTight0_%s_phi"%useSystematic) )
            read_variables.extend( map( lambda x:(x%useSystematic),
               ["PhotonGood0_%s_pt/F", "PhotonGood0_%s_eta/F", "PhotonGood0_%s_phi/F",
                "LeptonTight0_%s_pt/F", "LeptonTight0_%s_eta/F", "LeptonTight0_%s_phi/F", "nLeptonTight_%s/I", "nElectronTight_%s/I",
                "nLeptonVetoIsoCorr_%s/I", "nPhotonGood_%s/I", "nPhotonNoChgIsoNoSieie_%s/I", "triggered_%s/I"]))
            for replacement in replacements:
                reco_selection_str = reco_selection_str.replace(*replacement)
                if type(settings.reco_variable) == type(""):
                    settings.reco_variable = settings.reco_variable.replace(*replacement)
                elif type(settings.reco_variable) == type({}):
                    settings.reco_variable[settings.reco_variable.keys()[0]] = settings.reco_variable[settings.reco_variable.keys()[0]].replace(*replacement)

        elif useSystematic in jesSystematics:
            # changing the reco variable
            replacements = [(var, var+'_'+useSystematic) for var in ["nJetGood", "nBTagGood"]]
            read_variables.append( "nJetGood_"+useSystematic+"/I" )
            read_variables.append( "nBTagGood_"+useSystematic+"/I" )
            for replacement in replacements:
                reco_selection_str = reco_selection_str.replace(*replacement)
                if type(settings.reco_variable) == type(""):
                    settings.reco_variable = settings.reco_variable.replace(*replacement)
                elif type(settings.reco_variable) == type({}):
                    settings.reco_variable[settings.reco_variable.keys()[0]] = settings.reco_variable[settings.reco_variable.keys()[0]].replace(*replacement)

        else:
            raise NotImplementedError( "Systematic %s not known!" % useSystematic )

        logger.info( "working on systematic: %s", useSystematic )
        logger.info( "    reco_reweight_str: %s", reco_reweight_str )
        logger.info( "        reco_variable: %s", settings.reco_variable[settings.reco_variable.keys()[0]] if type(settings.reco_variable) == type({}) else settings.reco_variable)
        logger.info( "   reco_selection_str: %s", reco_selection_str)

#        sys.exit()
        # fiducial seletion
        fiducial_selection_str = cutInterpreter.cutString(settings.fiducial_selection)+"&&overlapRemoval==1"
        if not args.inclusive_samples and useSystematic not in ["TuneUp","TuneDown","erdOn","GluonMove","QCDbased"]:
            fiducial_selection_str+="&&pTStitching==1"

        ttreeFormulas = {
                    'is_fiducial':    fiducial_selection_str, 
                    'is_reco':        reco_selection_str, 
                    'gen_weight'    : 'weight*(35.92*(year==2016)+41.53*(year==2017)+59.74*(year==2018))', 
                    'reco_reweight' : reco_reweight_str,
                }

        # Sample for this year (fix)

        data_dir = "/scratch-cbe/users/lukas.lechner/TTGammaEFT/nanoTuples/postprocessed/TTGammaEFT_PP_{year}_TTG_private_v49/inclusive".format(year=year)

        if useSystematic == 'TuneUp':
            ttg1l = Sample.fromDirectory("ttg1l_%s"%year, directory = [os.path.join(data_dir, "TTGSingleLep_TuneUp_LO")])
            ttg2l = Sample.fromDirectory("ttg2l_%s"%year, directory = [os.path.join(data_dir, "TTGLep_TuneUp_LO")])
            sample = Sample.combine( "ttg_%s"%year, [ttg1l, ttg2l] )
        elif useSystematic == 'TuneDown':
            ttg1l = Sample.fromDirectory("ttg1l_%s"%year, directory = [os.path.join(data_dir, "TTGSingleLep_TuneDown_LO")])
            ttg2l = Sample.fromDirectory("ttg2l_%s"%year, directory = [os.path.join(data_dir, "TTGLep_TuneDown_LO")])
            sample = Sample.combine( "ttg_%s"%year, [ttg1l, ttg2l] )
        elif useSystematic == 'erdOn':
            ttg1l = Sample.fromDirectory("ttg1l_%s"%year, directory = [os.path.join(data_dir, "TTGSingleLep_erdOn_LO")])
            ttg2l = Sample.fromDirectory("ttg2l_%s"%year, directory = [os.path.join(data_dir, "TTGLep_erdOn_LO")])
            sample = Sample.combine( "ttg_%s"%year, [ttg1l, ttg2l] )
        elif useSystematic == 'GluonMove':
            ttg1l = Sample.fromDirectory("ttg1l_%s"%year, directory = [os.path.join(data_dir, "TTGSingleLep_GluonMove_LO")])
            ttg2l = Sample.fromDirectory("ttg2l_%s"%year, directory = [os.path.join(data_dir, "TTGLep_GluonMove_LO")])
            sample = Sample.combine( "ttg_%s"%year, [ttg1l, ttg2l] )
        elif useSystematic == 'QCDbased':
            ttg1l = Sample.fromDirectory("ttg1l_%s"%year, directory = [os.path.join(data_dir, "TTGSingleLep_QCDbased_LO")])
            ttg2l = Sample.fromDirectory("ttg2l_%s"%year, directory = [os.path.join(data_dir, "TTGLep_QCDbased_LO")])
            sample = Sample.combine( "ttg_%s"%year, [ttg1l, ttg2l] )
        elif args.inclusive_samples:
            ttg0l = Sample.fromDirectory("ttg0l_%s"%year, directory = [os.path.join(data_dir, "TTGHad_LO")])
            ttg1l = Sample.fromDirectory("ttg1l_%s"%year, directory = [os.path.join(data_dir, "TTGSingleLep_LO")])
            ttg2l = Sample.fromDirectory("ttg2l_%s"%year, directory = [os.path.join(data_dir, "TTGLep_LO")])
            sample = Sample.combine( "ttg_%s"%year, [ttg1l, ttg2l, ttg0l] )
        else:
            ttg0l = Sample.fromDirectory("ttg0l_%s"%year, directory = [os.path.join(data_dir, name) for name in ["TTGHad_LO","TTGHad_ptG100To200_LO","TTGHad_ptG200_LO"]])
            ttg1l = Sample.fromDirectory("ttg1l_%s"%year, directory = [os.path.join(data_dir, name) for name in ["TTGSingleLep_LO","TTGSingleLep_ptG100To200_LO","TTGSingleLep_ptG200_LO"]])
            ttg2l = Sample.fromDirectory("ttg2l_%s"%year, directory = [os.path.join(data_dir, name) for name in ["TTGLep_LO","TTGLep_ptG100To200_LO","TTGLep_ptG200_LO"]])
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
            shift_year =  i_year*(settings.max_reco_val - settings.min_reco_val)

            # reco observable 
            reco_variable_val       = getattr( r.event, reco_variable_name )

            # put reco overflow in the last bin
            if reco_variable_val   >= settings.max_reco_val and (settings.reco_overflow in ["upper","both"]):
                reco_variable_val   = settings.max_reco_bincenter
            #elif reco_variable_val >= settings.max_reco_val and settings.reco_overflow is None:
            #    reco_variable_val   = settings.reco_variable_underflow 

            # fiducial observable 
            fiducial_variable_val   = getattr( r.event, fiducial_variable_name ) 

            # put fiducial overflow in the last bin
            if fiducial_variable_val   >= settings.max_fiducial_val and (settings.fiducial_overflow in ["upper", "both"] ):
                fiducial_variable_val   = settings.max_fiducial_bincenter
            #elif fiducial_variable_val >= settings.max_fiducial_val and settings.fiducial_overflow is None:
            #    fiducial_variable_val   = settings.underflow_fiducial_val  

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
                    if "wrong" not in args.settings:
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
# Exit here if you were only doing a systematic variation
if not args.systematic is None:
    sys.exit()

# Unfolding matrix
delta = settings.max_reco_val-settings.min_reco_val
if delta==int(delta):
    s_str = " +%i*(year-2016)"%(settings.max_reco_val-settings.min_reco_val)
else:
    s_str = " +%3.2f*(year-2016)"%(settings.max_reco_val-settings.min_reco_val)

plot_matrix = Plot2D.fromHisto("unfolding_matrix", [[matrix]], texY = settings.tex_gen, texX = settings.tex_reco + s_str )
draw2D( plot_matrix, widths = {'x_width':500+250*(len(settings.years)-1)} )

# Efficiency Histogram
efficiency_base = matrix.ProjectionY()
efficiency      = matrix.ProjectionY("efficiency", 1, -1)
efficiency.Divide( efficiency_base )

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
#    histo_ = histo.Clone(histo.GetName()+'_fout_subtracted')
    histo_ = histo.Clone()
#    histo_.Scale(-1)
    histo_.Add(reco_fout_spectrum, -1)
#    histo_.Scale(-1)
    return histo_

reco_spectrum_subtracted = fout_subtraction( reco_spectrum )
#reco_spectrum_unc_subtracted = {u:fout_subtraction( reco_spectrum )

reco_spectrum_subtracted.legendText = "reco (f_{out} subtracted)"
reco_fout_spectrum.legendText = "reco f_{out}"
reco_spectrum.legendText = "Reco before subtraction"
reco_spectrum_subtracted.style = styles.lineStyle( ROOT.kRed, width=2) 
reco_fout_spectrum.style       = styles.lineStyle( ROOT.kGreen+1, width=2)       
reco_spectrum.style            = styles.lineStyle( ROOT.kBlue, width=2)      

for logY in [True, False]:
    plot = Plot.fromHisto( name = 'fout_subtraction' + ('_log' if logY else ''),  histos = [[ reco_spectrum ], [reco_spectrum_subtracted], [reco_fout_spectrum] ], texX = settings.tex_reco, texY = "Events")
    plot.stack = None
    draw(plot, logY = logY, 
#            ratio = {'histos':[(1,0)], 
#                    'yRange':(0.5,1.1), 
#                    'texY':'purity'}
        )

    purity = reco_spectrum_subtracted.Clone()
    purity.Divide(reco_spectrum)

for logY in [False]:

    purity     . style =  styles.lineStyle( ROOT.kRed, width = 2, errors=False)
    efficiency . style =  styles.lineStyle( ROOT.kBlue, width = 2, errors=True)
    purity     . legendText = "purity" 
    efficiency . legendText = "efficiency" 
    
    plot = Plot.fromHisto( name = 'pur_eff' + ('_log' if logY else ''),  histos = [[ h ] for h in [efficiency, purity]], texX = settings.tex_pur, texY = "fraction" )
    plot.stack = None
    draw(plot, logY = logY)

stuff = []
def getOutput( unfold, input_spectrum, name = "unfolded_spectrum", tau = 0.): 
    #if isinstance( unfold, ROOT.TUnfoldDensity ):
    #    #unfold.SetInput( input_spectrum )
    #    #unfold.DoUnfold(tau)
    #    raise NotImplementedError
    #    return unfold.GetOutput(name)
    #elif isinstance( unfold, ROOT.TUnfold ):
    unfolded_spectrum = matrix.ProjectionY(name)
    stuff.append( unfolded_spectrum )
    unfolded_spectrum.SetName(str(uuid.uuid4()))
    unfold.SetInput( input_spectrum )
    unfold.DoUnfold(tau)
    unfold.GetOutput(unfolded_spectrum)
    return unfolded_spectrum

# regularization
regMode = ROOT.TUnfold.kRegModeNone
#regMode = ROOT.TUnfold.kRegModeSize
#regMode = ROOT.TUnfold.kRegModeDerivative
#regMode = ROOT.TUnfold.kRegModeCurvature
#regMode = ROOT.TUnfold.kRegModeMixed

# extra contrains
constraintMode = ROOT.TUnfold.kEConstraintNone
#constraintMode = ROOT.TUnfold.kEConstraintArea

mapping = ROOT.TUnfold.kHistMapOutputVert
#mapping = ROOT.TUnfold.kHistMapOutputHoriz

unfold               = {key:ROOT.TUnfold( sys_matrix[key], mapping, regMode, constraintMode) for key in all_systematics}
unfolded_mc_spectrum = getOutput( unfold['nominal'], reco_spectrum_subtracted, "unfolded_mc_spectrum_subtracted", tau=0)


# tau scan (on foot)
unfold_nom_sys = ROOT.TUnfold( sys_matrix['nominal'], mapping, ROOT.TUnfold.kRegModeCurvature, constraintMode)
list_logtau, list_rho = [], []
for ilogtau in range(-50,1):
    logtau = ilogtau/10.
    #unfold_nom_sys.DoUnfold(10**(logtau))
    getOutput( unfold_nom_sys, reco_spectrum_subtracted, "unfolded_mc_spectrum_subtracted", tau=10**(logtau)) 
    rho_avg = unfold_nom_sys.GetRhoAvg()
    list_logtau.append( logtau )
    list_rho.append( rho_avg )

pos_min     = list_rho.index(min(list_rho))
best_logtau = list_logtau[pos_min]
scan_tgraph      = ROOT.TGraph(len(list_logtau), array.array('d', list_logtau), array.array('d', list_rho) )
scan_tgraph_best = ROOT.TGraph(1, array.array('d', [ best_logtau ]), array.array('d', [ list_rho[pos_min] ]) )

canv = ROOT.TCanvas("canv_tau")

scan_tgraph.SetTitle("Optimization of Regularization Parameter, #tau : Scan of correlation coefficient")
scan_tgraph.SetLineColor(ROOT.kBlue+3)
scan_tgraph.Draw()
scan_tgraph.GetXaxis().SetTitle("log_{10}(#tau)")
scan_tgraph.GetYaxis().SetTitle("Avg. correlation coefficient")

scan_tgraph_best.SetLineColor(ROOT.kRed)
scan_tgraph_best.SetMarkerColor(ROOT.kRed)
scan_tgraph_best.Draw("* same")

leg = ROOT.TLegend(0.2, 0.6, 0.7, 0.89)
leg.SetFillColor(0)
leg.SetFillStyle(0)
leg.SetBorderSize(0)
leg.SetTextSize(0.026)
leg.AddEntry(scan_tgraph, '#rho', 'l')
leg.AddEntry(scan_tgraph_best, 'minimum #tau = %6.4f'% list_rho[pos_min], 'P')
leg.Draw()

for ext in ['pdf','png','root']:
    canv.Print(os.path.join(plot_directory_, 'scan_tau.'+ext))

hs = []
colors = [ROOT.kBlue, ROOT.kRed, ROOT.kGreen+1]
for i_tau, tau in enumerate( [  0, 10**best_logtau, 10**-1] ):
    h = getOutput(unfold_nom_sys, reco_spectrum_subtracted, tau=tau)
    h.legendText = ( "log(#tau) = %6.4f" % log(tau,10) if tau > 0 else  "log(#tau) = -#infty" )
    h.style = styles.lineStyle( colors[i_tau], width=2 )
    hs.append( h )
for logY in [True]:
    plot = Plot.fromHisto( name = 'unfolding_tau_comparison' + ('_log' if logY else ''),  histos = [[ h ] for h in hs], texX = "p_{T}", texY = "Events" )
    plot.stack = None
    draw(plot, logY = logY,
         ratio = {'yRange': (0.92, 1.08), 'texY':'wrt #tau=0', 'histos':[(1,0)]},
        )

# closure 
for logY in [True, False]:

    unfolded_mc_spectrum_ = unfolded_mc_spectrum.Clone()
    unfolded_mc_spectrum_ . Scale(1./settings.lumi_factor) 
    fiducial_spectrum_    = fiducial_spectrum.Clone()
    fiducial_spectrum_    . Scale(1./settings.lumi_factor) 

    unfolded_mc_spectrum_ . style =  styles.lineStyle( ROOT.kRed, width = 2, errors=True)
    fiducial_spectrum_    . style =  styles.lineStyle( ROOT.kBlack, width = 2, errors=True)
    unfolded_mc_spectrum_ . legendText = "unfolded (%6.2f fb)" % (unfolded_mc_spectrum_.Integral())
    fiducial_spectrum_    . legendText = "fiducial (%6.2f fb)" % (fiducial_spectrum_.Integral())
    
    plot = Plot.fromHisto( name = 'unfolding_closure' + ('_log' if logY else ''),  histos = [[ h ] for h in [fiducial_spectrum_, unfolded_mc_spectrum_]], texX = "p_{T}", texY = "Fiducial cross section (fb)" )
    plot.stack = None
    draw(plot, logY = logY)

if not hasattr(settings, "unfolding_data_input"):
    sys.exit(0)

# input plot unsubtracted
empty = settings.unfolding_signal_input.Clone()
for i in range(1, empty.GetNbinsX()+1):
    empty.SetBinContent( i, 0 )
    empty.SetBinError( i, 0 )

empties = []
for band in settings.unfolding_signal_input_systematic_bands:
    empty_ = empty.Clone()
    empty_.SetLineColor(band['color'])
    empty_.SetLineWidth(0)
    #empty_.SetFillStyle(3244)
    empty_.SetFillColor(band['color'])
    empties.append(empty_)
    empty_.legendText = band["label"]

boxes = []
ratio_boxes = []
for band in reversed(settings.unfolding_signal_input_systematic_bands):
    for i in range(1, band['ref'].GetNbinsX()+1):
        box = ROOT.TBox( band['ref'].GetXaxis().GetBinLowEdge(i),  
                         band['down'].GetBinContent(i),
                         band['ref'].GetXaxis().GetBinUpEdge(i),
                         band['up'].GetBinContent(i),
             )
        box.SetLineColor(band['color'])
        #box.SetFillStyle(3244)
        box.SetFillColor(band['color'])
        if hasattr( settings, "plot_range_x_fiducial") and band['ref'].GetXaxis().GetBinUpEdge(i) > settings.plot_range_x_fiducial[1]:
            pass
        else:
            boxes.append(copy.deepcopy(box))
            stuff.append(copy.deepcopy(box))
        if band['ref'].GetBinContent(i)!=0: 
            ratio_box = ROOT.TBox( band['ref'].GetXaxis().GetBinLowEdge(i),  
                             band['down'].GetBinContent(i)/band['ref'].GetBinContent(i),
                             band['ref'].GetXaxis().GetBinUpEdge(i),
                             band['up'].GetBinContent(i)/band['ref'].GetBinContent(i),
                 )
            ratio_box.SetLineColor(band['color'])
            #ratio_box.SetFillStyle(3244)
            ratio_box.SetFillColor(band['color'])
            if hasattr( settings, "plot_range_x_fiducial") and band['ref'].GetXaxis().GetBinUpEdge(i) > settings.plot_range_x_fiducial[1]:
                pass
            else:
                ratio_boxes.append(copy.deepcopy(ratio_box))
                stuff.append(copy.deepcopy(ratio_box))

#settings.unfolding_data_input.style = styles.errorStyle( ROOT.kBlack )
settings.unfolding_signal_input.style   = styles.lineStyle( ROOT.kBlue, width = 2)
reco_spectrum.style = styles.lineStyle( ROOT.kRed+1, width = 2)

#settings.unfolding_data_input.legendText = settings.data_legendText 
settings.unfolding_signal_input.legendText   = settings.signal_legendText
reco_spectrum.legendText = "Simulation"
ratio_line = ROOT.TLine(reco_spectrum.GetXaxis().GetXmin(), 1, reco_spectrum.GetXaxis().GetXmax(),1)
for logY in [True, False]:
    plot = Plot.fromHisto( "input_spectrum" + ('_log' if logY else ''),
                    [
                        [reco_spectrum],
                        [settings.unfolding_signal_input],
                    ] + [[e] for e in empties],
                    texX = settings.tex_reco,
                    texY = "Number of events",
                )
    plotting.draw( plot, 
        plot_directory = plot_directory_,
        logX = False, logY = logY, sorting = False,
        #legend = None,
        legend         = [ (0.20,0.75,0.9,0.91), 2 ],
        yRange = settings.y_range,
        ratio = {'yRange': (0.1, 1.9), 'texY':'Sim. / Obs.', 'histos':[(0,1)], 'drawObjects':ratio_boxes+[ratio_line]} ,
        drawObjects = drawObjects()+boxes,
        #drawObjects = boxes,
        redrawHistos = True,
    )

# input plot subtracted
boxes_sb = []
ratio_boxes_sb = []
for band in reversed(settings.unfolding_signal_input_systematic_bands):
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
        #box.SetFillStyle(3244)
        box.SetFillColor(band['color'])
        if hasattr( settings, "plot_range_x_fiducial") and band['ref'].GetXaxis().GetBinUpEdge(i) > settings.plot_range_x_fiducial[1]:
            pass
        else:
            boxes_sb.append(copy.deepcopy(box))
            stuff.append(copy.deepcopy(box))
        if band['ref'].GetBinContent(i)!=0:
            ratio_box = ROOT.TBox( band['ref_subtracted'].GetXaxis().GetBinLowEdge(i),
                             band['down_subtracted'].GetBinContent(i)/band['ref_subtracted'].GetBinContent(i),
                             band['ref_subtracted'].GetXaxis().GetBinUpEdge(i),
                             band['up_subtracted'].GetBinContent(i)/band['ref_subtracted'].GetBinContent(i),
                 )
            ratio_box.SetLineColor(band['color'])
            #ratio_box.SetFillStyle(3244)
            ratio_box.SetFillColor(band['color'])
            if hasattr( settings, "plot_range_x_fiducial") and band['ref_subtracted'].GetXaxis().GetBinUpEdge(i) > settings.plot_range_x_fiducial[1]:
                pass
            else:
                ratio_boxes_sb.append(copy.deepcopy(ratio_box))
                stuff.append(copy.deepcopy(ratio_box))

unfolding_signal_input_subtracted   = fout_subtraction( settings.unfolding_signal_input )
unfolding_signal_input_subtracted.style   = styles.lineStyle( ROOT.kBlue, width = 2)
unfolding_signal_input_subtracted.legendText   = settings.signal_legendText
reco_spectrum_subtracted.style = styles.lineStyle( ROOT.kRed+1, width = 2)
reco_spectrum_subtracted.legendText = "Simulation"
ratio_line = ROOT.TLine(reco_spectrum_subtracted.GetXaxis().GetXmin(), 1, reco_spectrum_subtracted.GetXaxis().GetXmax(),1)


for logY in [True, False]:
    plotting.draw(
        Plot.fromHisto( "input_spectrum_subtracted" + ('_log' if logY else ''),
                    [
                        [reco_spectrum_subtracted],
                        [unfolding_signal_input_subtracted],
                    ] + [[e] for e in empties],
                    texX = settings.tex_reco,
                    texY = "Number of events",
                ),
        plot_directory = plot_directory_,
        logX = False, logY = logY, sorting = False,
        #legend = None,
        legend         = [ (0.20,0.75,0.9,0.91), 2 ],
        yRange = settings.y_range,
        ratio = {'yRange': (0.3, 1.7), 'texY':'Sim. / Obs.', 'histos':[(0,1)], 'drawObjects':ratio_boxes_sb+[ratio_line]},
        drawObjects = drawObjects()+boxes_sb,
        #drawObjects = boxes_sb,
        redrawHistos = True,
    )

#########

# unfolding the data
unfolding_signal_output = getOutput(unfold['nominal'], unfolding_signal_input_subtracted, "unfolding_signal_input_subtracted_x")
unfolding_signal_output.Scale(1./settings.lumi_factor)
unfolding_signal_output.style = styles.lineStyle( ROOT.kBlue, width = 2)
unfolding_signal_output.legendText = settings.signal_legendText 

fiducial_spectrum.Scale(1./settings.lumi_factor)
fiducial_spectrum.style = styles.lineStyle( ROOT.kRed+1, width = 2)
fiducial_spectrum.legendText = "Simulation"
ratio_line = ROOT.TLine(fiducial_spectrum.GetXaxis().GetXmin(), 1, fiducial_spectrum.GetXaxis().GetXmax(),1)

# subtraction of nominal f_out for all uncertainties
for band in settings.unfolding_signal_input_systematics + [settings.unfolding_signal_input_MCStat, settings.unfolding_data_input_systematic]:
    band['ref_subtracted']  = fout_subtraction(band['ref'])
    band['down_subtracted'] = fout_subtraction(band['down'])
    band['up_subtracted']   = fout_subtraction(band['up'])

    band['ref_unfolded']  = getOutput(unfold[band['matrix']], band['ref_subtracted'],  "unfolding_%s_output"%band['name'])
    band['down_unfolded'] = getOutput(unfold[band['matrix']], band['down_subtracted'], "unfolding_%s_down_output"%band['name'])
    band['up_unfolded']   = getOutput(unfold[band['matrix']], band['up_subtracted'],   "unfolding_%s_up_output"%band['name'])

    band['ref_unfolded'].Scale(1./settings.lumi_factor)
    band['down_unfolded'].Scale(1./settings.lumi_factor)
    band['up_unfolded'].Scale(1./settings.lumi_factor)

if args.extended:
  for band in settings.unfolding_signal_input_systematics + [settings.unfolding_signal_input_MCStat]:
    boxes_in = []
    ratio_boxes_in = []
    for i in range(1, band['ref'].GetNbinsX()+1):
        box = ROOT.TBox( band['ref'].GetXaxis().GetBinLowEdge(i),  
                         band['down'].GetBinContent(i),
                         band['ref'].GetXaxis().GetBinUpEdge(i),
                         band['up'].GetBinContent(i),
             )
        box.SetLineColor(band['color'])
        #box.SetFillStyle(3244)
        box.SetFillColor(band['color'])
        if hasattr( settings, "plot_range_x_fiducial") and band['ref'].GetXaxis().GetBinUpEdge(i) > settings.plot_range_x_fiducial[1]:
            pass
        else:
            boxes_in.append(copy.deepcopy(box))
            stuff.append(copy.deepcopy(box))
        if band['ref'].GetBinContent(i)!=0: 
            ratio_box = ROOT.TBox( band['ref'].GetXaxis().GetBinLowEdge(i),  
                             band['down'].GetBinContent(i)/band['ref'].GetBinContent(i),
                             band['ref'].GetXaxis().GetBinUpEdge(i),
                             band['up'].GetBinContent(i)/band['ref'].GetBinContent(i),
                 )
            ratio_box.SetLineColor(band['color'])
            #ratio_box.SetFillStyle(3244)
            ratio_box.SetFillColor(band['color'])
            if hasattr( settings, "plot_range_x_fiducial") and band['ref'].GetXaxis().GetBinUpEdge(i) > settings.plot_range_x_fiducial[1]:
                pass
            else:
                ratio_boxes_in.append(copy.deepcopy(ratio_box))
                stuff.append(copy.deepcopy(ratio_box))

    #settings.unfolding_data_input.style = styles.errorStyle( ROOT.kBlack )
    settings.unfolding_signal_input.style   = styles.lineStyle( ROOT.kBlue, width = 2)
    reco_spectrum.style = styles.lineStyle( ROOT.kRed+1, width = 2)

    #settings.unfolding_data_input.legendText = settings.data_legendText 
    settings.unfolding_signal_input.legendText   = settings.signal_legendText
    reco_spectrum.legendText = "Simulation"
    ratio_line = ROOT.TLine(reco_spectrum.GetXaxis().GetXmin(), 1, reco_spectrum.GetXaxis().GetXmax(),1)
    for logY in [True, False]:
        plot = Plot.fromHisto( "input_spectrum_%s"%band['name'] + ('_log' if logY else ''),
                        [
                            [reco_spectrum],
                            [settings.unfolding_signal_input],
                        ] + [[e] for e in empties],
                        texX = settings.tex_reco,
                        texY = "Number of events",
                    )
        plotting.draw( plot, 
            plot_directory = plot_directory_ + "/uncertainties/",
            logX = False, logY = logY, sorting = False,
            #legend = None,
            legend         = [ (0.20,0.75,0.9,0.91), 2 ],
            yRange = settings.y_range,
            ratio = {'yRange': (0.9, 1.1), 'texY':'Sim. / Obs.', 'histos':[(0,1)], 'drawObjects':ratio_boxes_in+[ratio_line]} ,
            drawObjects = drawObjects()+boxes_in,
            #drawObjects = boxes,
            redrawHistos = True,
        )
copyIndexPHP( plot_directory_ + "/uncertainties/" )

# input plot subtracted
if args.extended:
  for band in settings.unfolding_signal_input_systematics + [settings.unfolding_signal_input_MCStat]:
    boxes_sub = []
    ratio_boxes_sub = []
    for i in range(1, band['ref'].GetNbinsX()+1):
        box = ROOT.TBox( band['ref_subtracted'].GetXaxis().GetBinLowEdge(i),  
                         band['down_subtracted'].GetBinContent(i),
                         band['ref_subtracted'].GetXaxis().GetBinUpEdge(i),
                         band['up_subtracted'].GetBinContent(i),
             )
        box.SetLineColor(band['color'])
        #box.SetFillStyle(3244)
        box.SetFillColor(band['color'])
        if hasattr( settings, "plot_range_x_fiducial") and band['ref'].GetXaxis().GetBinUpEdge(i) > settings.plot_range_x_fiducial[1]:
            pass
        else:
            boxes_sub.append(copy.deepcopy(box))
            stuff.append(copy.deepcopy(box))
        if band['ref'].GetBinContent(i)!=0:
            ratio_box = ROOT.TBox( band['ref_subtracted'].GetXaxis().GetBinLowEdge(i),
                             band['down_subtracted'].GetBinContent(i)/band['ref_subtracted'].GetBinContent(i),
                             band['ref_subtracted'].GetXaxis().GetBinUpEdge(i),
                             band['up_subtracted'].GetBinContent(i)/band['ref_subtracted'].GetBinContent(i),
                 )
            ratio_box.SetLineColor(band['color'])
            #ratio_box.SetFillStyle(3244)
            ratio_box.SetFillColor(band['color'])
            if hasattr( settings, "plot_range_x_fiducial") and band['ref_subtracted'].GetXaxis().GetBinUpEdge(i) > settings.plot_range_x_fiducial[1]:
                pass
            else:
                ratio_boxes_sub.append(copy.deepcopy(ratio_box))
                stuff.append(copy.deepcopy(ratio_box))

    ratio_line = ROOT.TLine(reco_spectrum_subtracted.GetXaxis().GetXmin(), 1, reco_spectrum_subtracted.GetXaxis().GetXmax(),1)

    for logY in [True, False]:
        plotting.draw(
            Plot.fromHisto( "input_spectrum_subtracted_%s"%band['name'] + ('_log' if logY else ''),
                        [
                            [reco_spectrum_subtracted],
                            [unfolding_signal_input_subtracted],
                        ] + [[e] for e in empties],
                        texX = settings.tex_reco,
                        texY = "Number of events",
                    ),
            plot_directory = plot_directory_ + "/uncertainties/",
            logX = False, logY = logY, sorting = False,
            #legend = None,
            legend         = [ (0.20,0.75,0.9,0.91), 2 ],
            yRange = settings.y_range,
            ratio = {'yRange': (0.9, 1.1), 'texY':'Sim. / Obs.', 'histos':[(0,1)], 'drawObjects':ratio_boxes_sub+[ratio_line]},
            drawObjects = drawObjects()+boxes_sub,
            #drawObjects = boxes,
            redrawHistos = True,
        )


#########


if args.extended:
  for band in settings.unfolding_signal_input_systematics + [settings.unfolding_signal_input_MCStat]:

    boxes_unf = []
    ratio_boxes_unf = []
    for i in range(1, band['ref_unfolded'].GetNbinsX()+1):
        box = ROOT.TBox( band['ref_unfolded'].GetXaxis().GetBinLowEdge(i),
                         band['down_unfolded'].GetBinContent(i),
                         band['ref_unfolded'].GetXaxis().GetBinUpEdge(i),
                         band['up_unfolded'].GetBinContent(i),
             )
        box.SetLineColor(band['color'])
        #box.SetFillStyle(3244)
        box.SetFillColor(band['color'])
        if hasattr( settings, "plot_range_x_fiducial") and band['ref_unfolded'].GetXaxis().GetBinUpEdge(i) > settings.plot_range_x_fiducial[1]:
            pass
        else:
            boxes_unf.append(copy.deepcopy(box))
            stuff.append(copy.deepcopy(box))
        if band['ref_unfolded'].GetBinContent(i)!=0:
            ratio_box = ROOT.TBox( band['ref_unfolded'].GetXaxis().GetBinLowEdge(i),
                             band['down_unfolded'].GetBinContent(i)/band['ref_unfolded'].GetBinContent(i),
                             band['ref_unfolded'].GetXaxis().GetBinUpEdge(i),
                             band['up_unfolded'].GetBinContent(i)/band['ref_unfolded'].GetBinContent(i),
                 )
            ratio_box.SetLineColor(band['color'])
            #ratio_box.SetFillStyle(3244)
            ratio_box.SetFillColor(band['color'])
            if hasattr( settings, "plot_range_x_fiducial") and band['ref_unfolded'].GetXaxis().GetBinUpEdge(i) > settings.plot_range_x_fiducial[1]:
                pass
            else:
                ratio_boxes_unf.append(copy.deepcopy(ratio_box))
                stuff.append(copy.deepcopy(ratio_box))

    ratio_line = ROOT.TLine(unfolding_signal_output.GetXaxis().GetXmin(), 1, unfolding_signal_output.GetXaxis().GetXmax(),1)

    for logY in [True, False]:
        plotting.draw(
            Plot.fromHisto( "unfolded_spectrum_subtracted_%s"%band['name'] + ('_log' if logY else ''),
                        [
                            [fiducial_spectrum],
                            [unfolding_signal_output],
                        ] + [[e] for e in empties],
                        texX = settings.tex_unf,
                        texY = settings.texY,
                    ),
            plot_directory = plot_directory_ + "/uncertainties_unfolded/",
            logX = False, logY = logY, sorting = False,
            #legend = None,
            legend         = [ (0.20,0.75,0.9,0.91), 2 ],
            yRange = settings.y_range,
            ratio = {'yRange': (0.9, 1.1), 'texY':'Sim. / Obs.', 'histos':[(0,1)], 'drawObjects':ratio_boxes_unf+[ratio_line]},
            drawObjects = drawObjects()+boxes_unf,
            #drawObjects = boxes,
            redrawHistos = True,
        )
copyIndexPHP( plot_directory_ + "/uncertainties_unfolded/" )

systHists = { h["name"]:{ "up":h["up_unfolded"], "down":h["down_unfolded"], "ref":h["ref_unfolded"] } for h in settings.unfolding_signal_input_systematics }
totalUncertainty_unfolded = sumNuisanceHistos( systHists, settings.corrFitObj, refHist=unfolding_signal_output )
mcStat_unfolded = {"up":settings.unfolding_signal_input_MCStat["up_unfolded"], "down":settings.unfolding_signal_input_MCStat["down_unfolded"], "ref":settings.unfolding_signal_input_MCStat["ref_unfolded"]}
stat_unfolded = {"up":settings.unfolding_data_input_systematic["up_unfolded"], "down":settings.unfolding_data_input_systematic["down_unfolded"], "ref":settings.unfolding_data_input_systematic["ref_unfolded"]}
#totalUncertainty_unfolded = mcStat_unfolded
totalUncertainty_unfolded_color = ROOT.kOrange-9
unfolding_signal_output_color = ROOT.kBlue -10

# unfolding the error bands
boxes_syst = []
ratio_boxes_syst = []
for i in range(1, totalUncertainty_unfolded['ref'].GetNbinsX()+1):

#    total_sys_uncertainty = ( sqrt(  ( 0.5*( totalUncertainty_unfolded['up'].GetBinContent(i)-totalUncertainty_unfolded['down'].GetBinContent(i) ) )**2
#                                 + ( 0.5*( mcStat_unfolded['up'].GetBinContent(i)-mcStat_unfolded['down'].GetBinContent(i) ) )**2 )
#                                 + ( 0.5*abs( stat_unfolded['up'].GetBinContent(i)-stat_unfolded['down'].GetBinContent(i) ) ) )

#    total_sys_uncertainty = sqrt(  ( 0.5*( totalUncertainty_unfolded['up'].GetBinContent(i)-totalUncertainty_unfolded['down'].GetBinContent(i) ) )**2
#                                 + ( 0.5*( mcStat_unfolded['up'].GetBinContent(i)-mcStat_unfolded['down'].GetBinContent(i) ) )**2
#                                 + ( 0.5*( stat_unfolded['up'].GetBinContent(i)-stat_unfolded['down'].GetBinContent(i) ) )**2 )

    total_sys_uncertainty = sqrt(  ( 0.5*( totalUncertainty_unfolded['up'].GetBinContent(i)-totalUncertainty_unfolded['down'].GetBinContent(i) ) )**2
                                 + ( 0.5*( mcStat_unfolded['up'].GetBinContent(i)-mcStat_unfolded['down'].GetBinContent(i) ) )**2
                                 + ( 0.5*( stat_unfolded['up'].GetBinContent(i)-stat_unfolded['down'].GetBinContent(i) ) )**2 )

    box = ROOT.TBox( totalUncertainty_unfolded['ref'].GetXaxis().GetBinLowEdge(i),  
                     max(0, unfolding_signal_output.GetBinContent(i) - total_sys_uncertainty),
                     totalUncertainty_unfolded['ref'].GetXaxis().GetBinUpEdge(i),
                     unfolding_signal_output.GetBinContent(i) + total_sys_uncertainty,
                 )

    box.SetLineColor(totalUncertainty_unfolded_color)
    #box.SetFillStyle(3244)
    box.SetFillColor(totalUncertainty_unfolded_color)
    boxes_syst.append(copy.deepcopy(box))
    stuff.append(copy.deepcopy(box))

    box = ROOT.TBox( totalUncertainty_unfolded['ref'].GetXaxis().GetBinLowEdge(i),
                     max(0, stat_unfolded['down'].GetBinContent(i)),
                     totalUncertainty_unfolded['ref'].GetXaxis().GetBinUpEdge(i),
                     stat_unfolded['up'].GetBinContent(i)
                 )

    box.SetLineColor(unfolding_signal_output_color)
    #box.SetFillStyle(3244)
    box.SetFillColor(unfolding_signal_output_color)
    boxes_syst.append(copy.deepcopy(box))
    stuff.append(copy.deepcopy(box))

    if unfolding_signal_output.GetBinContent(i)!=0: 
        ratio_box = ROOT.TBox( 
                              totalUncertainty_unfolded['ref'].GetXaxis().GetBinLowEdge(i),  
                              max(0, unfolding_signal_output.GetBinContent(i) - total_sys_uncertainty)/unfolding_signal_output.GetBinContent(i),
                              totalUncertainty_unfolded['ref'].GetXaxis().GetBinUpEdge(i),
                              (unfolding_signal_output.GetBinContent(i) + total_sys_uncertainty)/unfolding_signal_output.GetBinContent(i),
                   )
        ratio_box.SetLineColor(totalUncertainty_unfolded_color)
        #ratio_box.SetFillStyle(3244)
        ratio_box.SetFillColor(totalUncertainty_unfolded_color)
        ratio_boxes_syst.append(copy.deepcopy(ratio_box))
        stuff.append(copy.deepcopy(ratio_box))

        ratio_box = ROOT.TBox( 
                              totalUncertainty_unfolded['ref'].GetXaxis().GetBinLowEdge(i),
                              stat_unfolded['down'].GetBinContent(i)/stat_unfolded['ref'].GetBinContent(i),
                              totalUncertainty_unfolded['ref'].GetXaxis().GetBinUpEdge(i),
                              stat_unfolded['up'].GetBinContent(i)/stat_unfolded['ref'].GetBinContent(i)
                  )

        ratio_box.SetLineColor(unfolding_signal_output_color)
        #ratio_box.SetFillStyle(3244)
        ratio_box.SetFillColor(unfolding_signal_output_color)
        ratio_boxes_syst.append(copy.deepcopy(ratio_box))
        stuff.append(copy.deepcopy(ratio_box))

#######

# systematics in unfolding -> compute the variances from the variied unfolding matrix
## make a copy of the mc output and remove the uncertainty
unfolding_systematic = unfolding_signal_output.Clone()
unfolding_systematic.style = styles.lineStyle(ROOT.kRed, errors=True) 
for i_bin in range(unfolding_systematic.GetNbinsX()+2):
    unfolding_systematic.SetBinError( i_bin, 0 )

# do not add extra uncertainties for now FIXME
#for pair in systematic_pairs: 
#    unfolding_signal_output_systematic_up   = getOutput(unfold[pair[0]], unfolding_signal_input_subtracted, "unfolding_signal_input_subtracted_"+pair[0])
#    unfolding_signal_output_systematic_up.Scale(1./settings.lumi_factor)
#    unfolding_signal_output_systematic_down = getOutput(unfold[pair[1]], unfolding_signal_input_subtracted, "unfolding_signal_input_subtracted_"+pair[1])
#    unfolding_signal_output_systematic_down.Scale(1./settings.lumi_factor)
#    # Add unfolding systematics quadrature

#    for i_bin in range(unfolding_systematic.GetNbinsX()+2):
#        unfolding_systematic.SetBinError( i_bin, 
#            sqrt( unfolding_systematic.GetBinError(i_bin)**2 # what it was before
#                 +(0.5*(unfolding_signal_output_systematic_up.GetBinContent(i_bin)-unfolding_signal_output_systematic_down.GetBinContent(i_bin)))**2 # contribution from pair
#                ))

# Make a plot of the unfolding systematics on the unfolded MC spectrum
for logY in [True, False]:
    plotting.draw(
    Plot.fromHisto( "unfolding_systematic" + ('_log' if logY else ''),
                    [[unfolding_systematic]],
                    texX = settings.tex_reco,
                    texY = "Number of events",
                ),
        plot_directory = plot_directory_,
        logX = False, logY = logY, sorting = False,
        #legend = None,
        legend         = [ (0.20,0.75,0.9,0.91), 2 ],
        yRange = settings.y_range,
        drawObjects = drawObjects(),
    )

# unfolding the error bands
boxes_uf = []
ratio_boxes_uf = []
for band in reversed(settings.unfolding_signal_input_systematic_bands):
    band['ref_unfolded']  = getOutput(unfold['nominal'], band['ref_subtracted'], "band_%s_ref_unfolded"%band['name'])
    band['up_unfolded']   = getOutput(unfold['nominal'], band['up_subtracted'],   "band_%s_up_unfolded"%band['name'])
    band['down_unfolded'] = getOutput(unfold['nominal'], band['down_subtracted'], "band_%s_down_unfolded"%band['name'])

    for h in [ band['up_unfolded'], band['down_unfolded'], band['ref_unfolded']]:
       h.Scale(1./settings.lumi_factor)

    for i in range(1, band['ref_unfolded'].GetNbinsX()+1):

        # add the unfolding-systematic to the total
        if band['name'] == 'total':

            total_sys_uncertainty = 0.5*abs(band['up_unfolded'].GetBinContent(i)-band['down_unfolded'].GetBinContent(i))
#            total_sys_uncertainty = sqrt( (0.5*(band['up_unfolded'].GetBinContent(i)-band['down_unfolded'].GetBinContent(i)))**2
#                                     + unfolding_systematic.GetBinError(i)**2 )

            box = ROOT.TBox( band['ref_unfolded'].GetXaxis().GetBinLowEdge(i),  
                             max(0, band['ref_unfolded'].GetBinContent(i) - total_sys_uncertainty),
                             band['ref_unfolded'].GetXaxis().GetBinUpEdge(i),
                             band['ref_unfolded'].GetBinContent(i) + total_sys_uncertainty,
                 )
       
        else: # don't add the unfolding-systematic to the other systematic bands 
            box = ROOT.TBox( band['ref_unfolded'].GetXaxis().GetBinLowEdge(i),  
                             band['down_unfolded'].GetBinContent(i),
                             band['ref_unfolded'].GetXaxis().GetBinUpEdge(i),
                             band['up_unfolded'].GetBinContent(i),
                 )
        box.SetLineColor(band['color'])
        #box.SetFillStyle(3244)
        box.SetFillColor(band['color'])
        if hasattr( settings, "plot_range_x_fiducial") and band['ref_unfolded'].GetXaxis().GetBinUpEdge(i) > settings.plot_range_x_fiducial[1]:
            pass
        else:
            boxes_uf.append(copy.deepcopy(box))
            stuff.append(copy.deepcopy(box))

        if band['ref_unfolded'].GetBinContent(i)!=0: 
            if band['name'] == 'total':

                total_sys_uncertainty = 0.5*abs(band['up_unfolded'].GetBinContent(i)-band['down_unfolded'].GetBinContent(i))
#                total_sys_uncertainty = sqrt( (0.5*(band['up_unfolded'].GetBinContent(i)-band['down_unfolded'].GetBinContent(i)))**2 )
#                                         + unfolding_systematic.GetBinError(i)**2 )
                ratio_box = ROOT.TBox( 
                                 band['ref_unfolded'].GetXaxis().GetBinLowEdge(i),  
                                 max(0, band['ref_unfolded'].GetBinContent(i) - total_sys_uncertainty)/band['ref_unfolded'].GetBinContent(i),
                                 band['ref_unfolded'].GetXaxis().GetBinUpEdge(i),
                                 (band['ref_unfolded'].GetBinContent(i) + total_sys_uncertainty)/band['ref_unfolded'].GetBinContent(i),
                     )
            else:
                ratio_box = ROOT.TBox( 
                                 band['ref_unfolded'].GetXaxis().GetBinLowEdge(i),  
                                 band['down_unfolded'].GetBinContent(i)/band['ref_unfolded'].GetBinContent(i),
                                 band['ref_unfolded'].GetXaxis().GetBinUpEdge(i),
                                 band['up_unfolded'].GetBinContent(i)/band['ref_unfolded'].GetBinContent(i),
                     )
            ratio_box.SetLineColor(band['color'])
            #ratio_box.SetFillStyle(3244)
            ratio_box.SetFillColor(band['color'])
            if hasattr( settings, "plot_range_x_fiducial") and band['ref_unfolded'].GetXaxis().GetBinUpEdge(i) > settings.plot_range_x_fiducial[1]:
                pass
            else:
                ratio_boxes_uf.append(copy.deepcopy(ratio_box))
                stuff.append(copy.deepcopy(ratio_box))

empty = unfolding_signal_output.Clone()
for i in range(1, empty.GetNbinsX()+1):
    empty.SetBinContent( i, 0 )
    empty.SetBinError( i, 0 )

empties = []
for band in settings.unfolding_signal_input_systematic_bands:
    empty_ = empty.Clone()
    empty_.SetLineColor(band['color'])
    empty_.SetLineWidth(0)
    #empty_.SetFillStyle(3244)
    empty_.SetFillColor(band['color'])
    empties.append(empty_)
    empty_.legendText = band["label"]

for logY in [True,False]:
    if hasattr( settings, "plot_range_x_fiducial"):
        hist_mod = [lambda h:h.GetXaxis().SetRangeUser(*settings.plot_range_x_fiducial)]
    else:
        hist_mod = []

    plot = Plot.fromHisto( "unfolded_spectrum"+ ('_log' if logY else ''),
                    [
                        [fiducial_spectrum],
                        [unfolding_signal_output],
                    ] + [[e] for e in empties],
                    texX = settings.tex_unf,
                    texY = settings.texY,
                )
    plotting.draw(plot,
        plot_directory = plot_directory_,
        logX = False, logY = logY, sorting = False, 
        #legend = None,
        histModifications = hist_mod,
        legend         = [ (0.20,0.75,0.9,0.91), 2 ],
        yRange = settings.y_range,
        ratio = {'yRange': settings.y_range_ratio, 'texY':'Sim. / Obs.', 'histos':[(0,1)], 'drawObjects':ratio_boxes_uf+[ratio_line]} ,
        drawObjects = drawObjects()+boxes_uf,
        #drawObjects = boxes_uf,
        redrawHistos = True,
    )

for logY in [True,False]:
    if hasattr( settings, "plot_range_x_fiducial"):
        hist_mod = [lambda h:h.GetXaxis().SetRangeUser(*settings.plot_range_x_fiducial)]
    else:
        hist_mod = []

    plot = Plot.fromHisto( "unfolded_spectrum_fromSyst"+ ('_log' if logY else ''),
                    [
                        [fiducial_spectrum],
                        [unfolding_signal_output],
                    ] + [[e] for e in empties],
                    texX = settings.tex_unf,
                    texY = settings.texY,
                )
    plotting.draw(plot,
        plot_directory = plot_directory_,
        logX = False, logY = logY, sorting = False, 
        #legend = None,
        histModifications = hist_mod,
        legend         = [ (0.20,0.75,0.9,0.91), 2 ],
        yRange = settings.y_range,
        ratio = {'yRange': settings.y_range_ratio, 'texY':'Sim. / Obs.', 'histos':[(0,1)], 'drawObjects':ratio_boxes_syst+[ratio_line]} ,
        drawObjects = drawObjects()+boxes_syst,
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

if not args.extended:
    sys.exit(0)
 
# Do it once again for the extra plots!
unfolding_data_output = getOutput(unfold['nominal'], settings.unfolding_data_input, "unfolding_data_input")

probability_matrix = matrix.Clone()
unfold['nominal'].GetProbabilityMatrix(probability_matrix,mapping)
probability_TMatrix = get_TMatrixD( probability_matrix )
plot_probability_matrix = Plot2D.fromHisto("probability_matrix", [[probability_matrix]], texY = plot_matrix.texY, texX = plot_matrix.texX )
draw2D( plot_probability_matrix )

# output covariance matrix
output_covariance_matrix = ROOT.TH2D("output_covariance_matrix", "output_covariance_matrix", len(settings.fiducial_thresholds)-1, array.array('d', settings.fiducial_thresholds), len(settings.fiducial_thresholds)-1, array.array('d', settings.fiducial_thresholds) )
unfold['nominal'].GetEmatrix( output_covariance_matrix )
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
unfold['nominal'].GetInputInverseEmatrix( input_inverse_covariance_matrix )
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

# check condition number # https://www.youtube.com/watch?v=AULOC--qUOI

matrix_TMatrix  = get_TMatrixD( matrix )
svd             = ROOT.TDecompSVD( matrix_TMatrix )
singulars       = svd.GetSig()
singulars.Print()

Analysis.Tools.syncer.sync()

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
