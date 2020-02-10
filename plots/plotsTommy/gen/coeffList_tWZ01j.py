from Analysis.Tools.WeightInfo          import WeightInfo



# Polynomial parametrization
w = WeightInfo("/afs/hephy.at/data/rschoefbeck01/gridpacks/dim6top/tWZ01j_rwgt_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.pkl")
w.set_order(2)

coeffList = [0.00021851709087720354,
 -9.472892877801823e-10,
 8.652143015639314e-11,
 3.680539584423671e-06,
 4.087903651805576e-05,
 2.6274605092501532e-08,
 2.5573100404338952e-08,
 -2.1926998169054047e-05,
 3.018552611413942e-07,
 -9.133449610916224e-07,
 2.2485967137869028e-08,
 3.611126916229432e-06,
 2.1134813589872996e-09,
 1.0962817494819566e-10,
 9.331277080568635e-11,
 1.2972883094477964e-08,
 4.0596852185296585e-12,
 3.879796010930543e-12,
 -8.5194501583099e-09,
 1.5328934390084072e-09,
 3.77907334677029e-09,
 -2.4054793152054925e-09,
 -2.782077652833855e-10,
 1.6251621149854063e-09,
 -2.605930718989348e-11,
 -1.3785117213743656e-09,
 7.789568108154926e-12,
 -6.306191214786165e-13,
 -4.383921876657152e-09,
 -5.046961905185436e-09,
 2.5079634205246182e-09,
 1.8891493791400738e-09,
 5.171337727081099e-11,
 8.876288750849271e-07,
 2.764535425567582e-06,
 -2.2937870817670645e-10,
 7.877522771286015e-10,
 -4.621797971252824e-08,
 -6.269944625112214e-09,
 2.9662009139359443e-07,
 2.9570350357738487e-08,
 -6.299608216364632e-07,
 1.0568777132220581e-05,
 -2.575752355497477e-08,
 4.439874939221963e-09,
 1.4558902181697776e-06,
 1.4607172314256233e-07,
 6.59351264254367e-07,
 -1.0491015016306697e-08,
 -4.893849355913038e-07,
 1.5282411754937861e-06,
 -1.4071385751867696e-14,
 -4.8681927250593194e-08,
 3.1077278588403606e-09,
 2.3201269625574973e-09,
 -1.1867889154441744e-08,
 -1.2202170675191848e-08,
 1.5282410984457018e-06,
 2.5819190152296137e-09,
 4.871964577523511e-08,
 -6.773455745038871e-09,
 -6.435556788133892e-09,
 3.400722072945199e-09,
 3.922961628215619e-05,
 1.3484018808215844e-08,
 -2.4758976914841877e-05,
 5.583337957514964e-07,
 -1.898754103754632e-07,
 3.909767072006596e-05,
 -5.710852804743346e-07,
 -2.40124297511079e-05,
 -7.145963755534071e-09,
 1.0838550390946357e-05,
 2.0298654688353154e-08,
 -3.566566818697662e-07,
 1.1334672415977828e-05,
 9.694004531105883e-09,
 4.004471615059617e-07]


# no reference point

print [w.get_weight_yield(coeffList,ctp=i)/w.get_weight_yield(coeffList) for i in range(-4,5)]