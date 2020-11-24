from TTGammaEFT.Analysis.SetupHelpers    import *

com = "python run_limit.py --overwrite --inclRegion --year 2016 --expected --useRegions VG3 VG4p misDY3 misDY4p SR3M3 SR4pM3 --parameters ctZ CTZVAL ctZI CTZIVAL"

for ctZ in eftParameterRange["ctZ"]:
    for ctZI in eftParameterRange["ctZI"]:
        print com.replace("CTZVAL", str(ctZ)).replace("CTZIVAL", str(ctZI))
