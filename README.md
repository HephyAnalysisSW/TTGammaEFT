# TTGammaEFT
Repository for work on top quark coupling measurements (EFT) in ttgamma

#### Samples:  

Samples are defined in in the Samples repository and are used in the postprocessing via:  
```  
Samples/python/Summer16/Fall17/Autumn18_nanoAODv6.py  
```  

After postprocessing, the samples are used in  
```  
TTGammaEFT/Samples/python/nanoTuples_Summer16/Fall17/Autumn18_private_semilep_postProcessed.py  
```  

#### PostProcessing:  

Postprocessing is defined in   
```  
postprocessing/nanoPostProcessing.py
```  

and is run via the .sh files for the nominal analysis   
```  
postprocessing/nanoPostProcessing_Summer16/Fall17/Autumn18_private_semilep.sh   
```  

or with a photon skim via   
```  
postprocessing/nanoPostProcessing_Summer16/Fall17/Autumn18_private_semilepGamma.sh   
```  

In principle one needs the one without the photon skim for the QCD estimation and with the photon skim for almost everything else.
However, the photon skim is just an extra for faster processing and can be neglected.

For unfolding, one needs the inclusive skip of the ttgamma samples   
```  
postprocessing/nanoPostProcessing_unfolding.sh   
```  

#### Analysis setup:  

Selection regions for the fit setup are defined in   
```  
Analysis/python/SetupHelpers.py   
```  
where a naming of regions (e.g. VG3, SR3) and the underlying selections are defined.

The selection scripts and weightstring scripts are defined in   
```  
Analysis/python/Setup.py   
```  

Systematic uncertainties and estimators for datadriven-fakes, QCD, data and MC are defined in   
```  
Analysis/python/   
```  

##### Caching:     

To run the fit, event yields and syst. uncertainties are cached.   
The samples are defined in 
```  
Analysis/python/Setup.py   
```  
and endings like gen, misID, had, add the photon category selection.

The yields are cached in running scripts in 
```  
Analysis/python/run/   
```  

To speed up the process, the pt and eta binned QCD transfer factors for all years are cached first in running
```  
Analysis/python/run/cache_transferFactor.sh
```  

Once this is done, one can run the caches with
```  
Analysis/python/run/cache_estimates.sh
```  
in adapting the year and regions.   
For the inclusive fit, the regions are VG3, VG4p, misDY3, misDY4p, SR3M3, and SR4pM3 defined in 
```  
Analysis/python/SetupHelpers.py   
```  

The differential (EFT) fit uses instead of SR3M3 and SR4pM3 the regions SR3PtUnfoldEFT, SR4pPtUnfoldEFT, SR3AbsEtaUnfold, SR4pAbsEtaUnfold, SR3dRUnfold, and SR4pdRUnfold, (SR3PtUnfoldEFT, SR4pPtUnfoldEFT) for the differential fits in pT, abs(eta), and dR(l,g).
The fits are combined to a Nj>=3p regions and thus also yields for SR3pPtUnfoldEFT, SR3pAbsEtaUnfold, and SR3pdRUnfold must be cached for each process, photon category, and data-driven backgrounds

The data-driven fakes are cached using the process fakes-DD (observed) and fakes-DDMC (expected) with the commands defined in   
```  
Analysis/python/run/cache_fakes.sh
```  

PDF and Scale uncertainties are run on the NLO samples and are cached in running
```  
Analysis/python/run/runPDFandScale.sh
```  
first without --combine to cache all yields and then with --combine to get the PDF/Scale/PS uncertainties.


##### Fit:     

Once the yields are cached one can run the fit using   
```  
Analysis/python/run/run_limit.py
```  

The cardfiles need to be created for each year. Examples are shown in   
```  
Analysis/python/run/run_limit.sh
```  

The nominal inclusive fit is performed with the command
```  
python run_limit.py --inclRegion --overwrite --year 201X --plot --useRegions misDY3 VG3 SR3M3 misDY4p VG4p SR4pM3 --addDYSF --splitScale
```  
The --plot command automatically creates plots for the card and can be neglected for the fits if not needed.   
The nominal differential fits are performed with the command
```  
python run_limit.py --overwrite --year 201X --plot --useRegions misDY3 VG3 SR3PtUnfoldEFT misDY4p VG4p SR4pPtUnfoldEFT --addDYSF --splitScale   
python run_limit.py --overwrite --year 201X --plot --useRegions misDY3 VG3 SR3dRUnfold misDY4p VG4p SR4pdRUnfold --addDYSF --splitScale   
python run_limit.py --overwrite --year 201X --plot --useRegions misDY3 VG3 SR3AbsEtaUnfold misDY4p VG4p SR4pAbsEtaUnfold --addDYSF --splitScale   
```  
The cardfiled for the jet-combined differential fits are created with the command
```  
python run_limit.py --overwrite --year 201X --plot --useRegions SR3pPtUnfoldEFT --addDYSF --splitScale   
python run_limit.py --overwrite --year 201X --plot --useRegions SR3pdRUnfold --addDYSF --splitScale   
python run_limit.py --overwrite --year 201X --plot --useRegions SR3pAbsEtaUnfold --addDYSF --splitScale   
```  
The combined RunII results are created with the same commands but running the run_limit_combined.py script without the --year, e.g.
```  
Analysis/python/run/run_limit_combined.sh
```  

Plots are created in
```  
plots/plotsLukas/regions/
```  


##### EFT:   
For EFT, the same caches are used as above, however additional gen-level caches are needed for the reweighting of the affected yields.
Commands for caching EFT yields are found in
```  
Analysis/python/run/run_EFTestimate.sh
```  
PDF and Scale uncertainties without normalization (acceptence effects) are needed for EFT fits. These caches are filled in running the same PDF/Scale command as above, with the additional --notNormalized command
```  
Analysis/python/run/runPDFandScale.sh
```  

Once this is done, EFT cardfiles can be created using the regions VG3, VG4p, misDY3, misDY4p, SR3PtUnfoldEFT, and SR4pPtUnfoldEFT and the same run_limit.py scripts as above. In adding --parameters ctZ X ctZI X, the script runs the EFT fit. Adding --withbkg also reweights the single-top background. The commands are found in  
```  
Analysis/python/run/run_limit_EFT_2lcomb_1D.sh   
Analysis/python/run/run_limit_EFT_2lcomb_2D.sh   
```  
And in 
```  
Analysis/python/run/run_limit_EFT_2lcomb_1D_comb.sh   
Analysis/python/run/run_limit_EFT_2lcomb_2D_comb.sh   
```  
for the combined RunII fit.

The NLL values are cached and are extracted in the plot scripts found in
```  
plots/plotsLukas/nll/
```  


#### Instructions for CMSSW

```
cmsrel CMSSW_10_2_22
cd CMSSW_10_2_22/src
cmsenv
git cms-init

# This repository
git clone https://github.com/HephyAnalysisSW/TTGammaEFT
cd $CMSSW_BASE/src/TTGammaEFT
./setup10X.sh
cd $CMSSW_BASE/src/
scram b -j9
```
