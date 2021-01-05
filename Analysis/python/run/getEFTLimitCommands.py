from TTGammaEFT.Analysis.SetupHelpers    import *

com = "python run_limit.py --overwrite --useTxt --inclRegion --year 2016 --addDYSF --addMisIDSF --expected --useRegions VG3 VG4p misDY3 misDY4p SR3M3 SR4pM3 --parameters ctZ CTZVAL ctZI CTZIVAL"

ctZI = 0
for ctZ in eftParameterRange["ctZ"]:
    print com.replace("CTZVAL", str(ctZ)).replace("CTZIVAL", str(ctZI))
ctZ = 0
for ctZI in eftParameterRange["ctZI"]:
    print com.replace("CTZVAL", str(ctZ)).replace("CTZIVAL", str(ctZI))

com = "python run_limit.py --overwrite --useTxt --inclRegion --year 2016 --addDYSF --addMisIDSF --useRegions VG3 VG4p misDY3 misDY4p SR3M3 SR4pM3 --parameters ctZ CTZVAL ctZI CTZIVAL"

ctZI = 0
for ctZ in eftParameterRange["ctZ"]:
    print com.replace("CTZVAL", str(ctZ)).replace("CTZIVAL", str(ctZI))
ctZ = 0
for ctZI in eftParameterRange["ctZI"]:
    print com.replace("CTZVAL", str(ctZ)).replace("CTZIVAL", str(ctZI))


com = "python run_limit.py --overwrite --useTxt --year 2016 --addDYSF --addMisIDSF --expected --useRegions VG3 VG4p misDY3 misDY4p SR3PtUnfold SR4pPtUnfold --parameters ctZ CTZVAL ctZI CTZIVAL"

ctZI = 0
for ctZ in eftParameterRange["ctZ"]:
        print com.replace("CTZVAL", str(ctZ)).replace("CTZIVAL", str(ctZI))
ctZ = 0
for ctZI in eftParameterRange["ctZI"]:
        print com.replace("CTZVAL", str(ctZ)).replace("CTZIVAL", str(ctZI))

com = "python run_limit.py --overwrite --useTxt --year 2016 --addDYSF --addMisIDSF --useRegions VG3 VG4p misDY3 misDY4p SR3PtUnfold SR4pPtUnfold --parameters ctZ CTZVAL ctZI CTZIVAL"

ctZI = 0
for ctZ in eftParameterRange["ctZ"]:
        print com.replace("CTZVAL", str(ctZ)).replace("CTZIVAL", str(ctZI))
ctZ = 0
for ctZI in eftParameterRange["ctZI"]:
        print com.replace("CTZVAL", str(ctZ)).replace("CTZIVAL", str(ctZI))
