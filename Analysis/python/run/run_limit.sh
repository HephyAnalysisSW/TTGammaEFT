python run_limit.py --overwrite --year 2016 --plot --bkgOnly --useRegions WJets3
python run_limit.py --overwrite --year 2016 --plot --bkgOnly --useRegions WJets3p
python run_limit.py --overwrite --year 2016 --plot --bkgOnly --useRegions WJets4p
python run_limit.py --overwrite --year 2016 --plot --bkgOnly --useRegions WJets3 WJets4p

python run_limit.py --overwrite --year 2016 --plot --bkgOnly --useRegions DY3
python run_limit.py --overwrite --year 2016 --plot --bkgOnly --useRegions DY3p
python run_limit.py --overwrite --year 2016 --plot --bkgOnly --useRegions DY4p
python run_limit.py --overwrite --year 2016 --plot --bkgOnly --useRegions DY3 DY4p

python run_limit.py --overwrite --year 2016 --plot --bkgOnly --useRegions ZG3
python run_limit.py --overwrite --year 2016 --plot --bkgOnly --useRegions ZG3p
python run_limit.py --overwrite --year 2016 --plot --bkgOnly --useRegions ZG4p
python run_limit.py --overwrite --year 2016 --plot --bkgOnly --useRegions ZG3 ZG4p

python run_limit.py --overwrite --year 2016 --plot --bkgOnly --useRegions TT3
python run_limit.py --overwrite --year 2016 --plot --bkgOnly --useRegions TT3p
python run_limit.py --overwrite --year 2016 --plot --bkgOnly --useRegions TT4p
python run_limit.py --overwrite --year 2016 --plot --bkgOnly --useRegions TT3 TT4p

python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misDY3 VG3 SR3M3
python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misDY3p VG3p SR3pM3
python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misDY4p VG4p SR4pM3
python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misDY3 misDY4p VG3 VG4p SR3M3 SR4pM3

python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misDY3 VG3 SR3M3 --addSSM
python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misDY3p VG3p SR3pM3 --addSSM
python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misDY4p VG4p SR4pM3 --addSSM
python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misDY3 misDY4p VG3 VG4p SR3M3 SR4pM3 --addSSM

python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misDY3 VG3 SR3M3 --addSSM --addMisIDSF
python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misDY3p VG3p SR3pM3 --addSSM --addMisIDSF
python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misDY4p VG4p SR4pM3 --addSSM --addMisIDSF
python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misDY3 misDY4p VG3 VG4p SR3M3 SR4pM3 --addSSM --addMisIDSF

python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY3 VG3 SR3M3
python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY3p VG3p SR3pM3
python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY4p VG4p SR4pM3
python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY3 misDY4p VG3 VG4p SR3M3 SR4pM3

python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY3 VG3 SR3M3 --addSSM
python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY3p VG3p SR3pM3 --addSSM
python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY4p VG4p SR4pM3 --addSSM
python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY3 misDY4p VG3 VG4p SR3M3 SR4pM3 --addSSM

python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY3 VG3 SR3M3 --addSSM --addMisIDSF
python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY3p VG3p SR3pM3 --addSSM --addMisIDSF
python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY4p VG4p SR4pM3 --addSSM --addMisIDSF
python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY3 misDY4p VG3 VG4p SR3M3 SR4pM3 --addSSM --addMisIDSF

#python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY3 VG3 SR3M3 fake3low fake3high
#python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY3p VG3p SR3pM3 fake3plow fake3phigh
#python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY4p VG4p SR4pM3 fake4plow fake4phigh
#python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY3 misDY4p VG3 VG4p SR3M3 SR4pM3 fake3low fake3high fake4plow fake4phigh

#python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY3 VG3 SR3M3 --addMisIDSF --addDYSF --addSSM --addWJetsSF --addTTSF
#python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY3p VG3p SR3pM3 --addMisIDSF --addDYSF --addSSM --addWJetsSF --addTTSF
#python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY4p VG4p SR4pM3 --addMisIDSF --addDYSF --addSSM --addWJetsSF --addTTSF
#python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY3 misDY4p VG3 VG4p SR3M3 SR4pM3 --addMisIDSF --addDYSF --addSSM --addWJetsSF --addTTSF

#python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY3 VG3 SR3M3 --addWJetsSF --addDYSF --addTTSF
#python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY3p VG3p SR3pM3 --addWJetsSF --addDYSF --addTTSF
#python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY4p VG4p SR4pM3 --addWJetsSF --addDYSF --addTTSF
#python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY3 misDY4p VG3 VG4p SR3M3 SR4pM3 --addWJetsSF --addDYSF --addTTSF

#python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY3 VG3 SR3M3 --addWJetsSF --addDYSF --addTTSF
#python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY3p VG3p SR3pM3 --addWJetsSF --addDYSF --addTTSF
#python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY4p VG4p SR4pM3 --addWJetsSF --addDYSF --addTTSF
#python run_limit.py --overwrite --year 2016 --plot --inclRegion --useRegions misTT2 misDY3 misDY4p VG3 VG4p SR3M3 SR4pM3 --addWJetsSF --addDYSF --addTTSF

#python run_limit.py --overwrite --year 2016 --plot --useRegions misTT2 misDY3 VG3 SR3M3
#python run_limit.py --overwrite --year 2016 --plot --useRegions misTT2 misDY3p VG3p SR3pM3
#python run_limit.py --overwrite --year 2016 --plot --useRegions misTT2 misDY4p VG4p SR4pM3
#python run_limit.py --overwrite --year 2016 --plot --useRegions misTT2 misDY3 misDY4p VG3 VG4p SR3M3 SR4pM3

#python run_limit.py --overwrite --year 2016 --plot --useRegions misTT2 misDY3 VG3 SR3M3 --addSSM
#python run_limit.py --overwrite --year 2016 --plot --useRegions misTT2 misDY3p VG3p SR3pM3 --addSSM
#python run_limit.py --overwrite --year 2016 --plot --useRegions misTT2 misDY4p VG4p SR4pM3 --addSSM
#python run_limit.py --overwrite --year 2016 --plot --useRegions misTT2 misDY3 misDY4p VG3 VG4p SR3M3 SR4pM3 --addSSM

#python run_limit.py --overwrite --year 2016 --plot --useRegions misTT2 misDY3 VG3 SR3M3 fake3low fake3high
#python run_limit.py --overwrite --year 2016 --plot --useRegions misTT2 misDY3p VG3p SR3pM3 fake3plow fake3phigh
#python run_limit.py --overwrite --year 2016 --plot --useRegions misTT2 misDY4p VG4p SR4pM3 fake4plow fake4phigh
#python run_limit.py --overwrite --year 2016 --plot --useRegions misTT2 misDY3 misDY4p VG3 VG4p SR3M3 SR4pM3 fake3low fake3high fake4plow fake4phigh

#python run_limit.py --overwrite --year 2016 --plot --useRegions misTT2 misDY3 VG3 SR3M3 --addWJetsSF --addDYSF --addTTSF
#python run_limit.py --overwrite --year 2016 --plot --useRegions misTT2 misDY3p VG3p SR3pM3 --addWJetsSF --addDYSF --addTTSF
#python run_limit.py --overwrite --year 2016 --plot --useRegions misTT2 misDY4p VG4p SR4pM3 --addWJetsSF --addDYSF --addTTSF
#python run_limit.py --overwrite --year 2016 --plot --useRegions misTT2 misDY3 misDY4p VG3 VG4p SR3M3 SR4pM3 --addWJetsSF --addDYSF --addTTSF
