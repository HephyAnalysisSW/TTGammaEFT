from Analysis.Tools.WeightInfo          import WeightInfo

# Polynomial parametrization
w = WeightInfo("/afs/hephy.at/data/cms04/ttschida/gridpacks/Yt/tWZ01j_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl")
w.set_order(2)

coeffList = [0.00026670329502486237, 2.081775489528767e-06, 1.3883718118586788e-06]

# reference point: cu = 0.66666

# (f-1)/0.246**2 = ctp --> f = ctp * 0.246**2 + 1

#    f  |      yt       | dim6top
# -------------------------------
#  1    | 2/3           |   0 
#  2    | 2/3 *  2      |  16.5
#  1.60 | 2/3 *  1.60   |  10 
# -2.63 | 2/3 * -2.63   | -60

print [w.get_weight_yield(coeffList,cu=i)/w.get_weight_yield(coeffList, cu=0.66666) for i in range(-4,5)]

