# TTGammaEFT
Repository for work on top quark coupling measurements (EFT) in ttgamma

#### Gridpacks:  
  
Code taken from the TTXPheno/gridpacks repository. Cards available there!  
Available gridpacks, pkl files, customize cards and STDOUTs stored at:  
```  
/afs/hephy.at/data/llechner01/TopEFT/gridpacks/<date>/<process>/order<poly order>/  
```  

#### Installation CMSSW_9_4_X

```
cmsrel CMSSW_9_4_10
cd CMSSW_9_4_10/src
cmsenv
git cms-init

# This repository
git clone https://github.com/HephyAnalysisSW/TTGammaEFT
#cd $CMSSW_BASE/src/TTGammaEFT/Tools/external/TUnfold
#make lib
cd $CMSSW_BASE/src
```

#### Samples repository

```
git clone https://github.com/HephyAnalysisSW/Samples.git
```

#### RootTools (needed for nanoAOD sample handling. If you just plan to produce nanoAOD tuples from miniAOD, this is not needed)

```
git clone https://github.com/HephyAnalysisSW/RootTools.git
cd $CMSSW_BASE/src

scram b -j 8
```
