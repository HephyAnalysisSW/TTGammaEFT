# TTGammaEFT
Repository for work on top quark coupling measurements (EFT) in ttgamma

#### Gridpacks:  
  
Code taken from the TTXPheno/gridpacks repository. Cards available there!  
Available gridpacks, pkl files, customize cards and STDOUTs stored at:  
```  
/afs/hephy.at/data/llechner01/TopEFT/gridpacks/<date>/<process>/order<poly order>/  
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
