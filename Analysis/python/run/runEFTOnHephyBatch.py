# create a sh file for all eft parameters to cache the nll value

from TTGammaEFT.Analysis.SetupHelpers import eftParameterRange

with open( "run_nll.sh", "w" ) as f:
    for i in eftParameterRange["ctZ"]:
        for j in eftParameterRange["ctZI"]: 
            f.write("python run_nll.py --overwrite --addDYSF --year 2016 --expected --inclRegion --useRegions misDY3 VG3 SR3M3 --parameters ctZ " +  str(i)  + " ctZI " + str(j) + "\n")
            f.write("python run_nll.py --overwrite --addDYSF --year 2016 --expected --inclRegion --useRegions misDY3p VG3p SR3pM3 --parameters ctZ " +  str(i)  + " ctZI " + str(j) + "\n")
            f.write("python run_nll.py --overwrite --addDYSF --year 2016 --expected --inclRegion --useRegions misDY4p VG4p SR4pM3 --parameters ctZ " +  str(i)  + " ctZI " + str(j) + "\n")
            f.write("python run_nll.py --overwrite --addDYSF --year 2016 --expected --inclRegion --useRegions misDY3 VG3 SR3M3 misDY4p VG4p SR4pM3 --parameters ctZ " +  str(i)  + " ctZI " + str(j) + "\n")
