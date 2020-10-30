from TTGammaEFT.Analysis.SetupHelpers import *

misID2SF_val["RunII"] = "-"
misID3SF_val["RunII"] = "-"
misID4SF_val["RunII"] = "-"
misID5SF_val["RunII"] = "-"
misID2pSF_val["RunII"] = "-"
misID3pSF_val["RunII"] = "-"
misID4pSF_val["RunII"] = "-"

lines = []
lines.append("\\begin{tabular}{|c|r||c|c|c|c|c|} ")
lines.append("\\hline ")
lines.append(" & \\textbf{\\nJet} & \\textbf{\\misIDSF} & \\textbf{Z$\\gamma$ SF} & \\textbf{W$\\gamma$ SF} & \\textbf{multijets SF} & \\textbf{\\DYJets SF}\\\\ ")
lines.append("\\hline ")

for year in [2016, 2017, 2018]:
    lines.append("\\hline ")
    lines.append("\\multirow{7}{*}{\\rotatebox{90}{\\textbf{%s}}} & \\textbf{2j} & $%s$ & $%s$ & $%s$ & $%s$ & $%s$ \\\\  "%(str(year), str(misID2SF_val[year]).replace("+-"," \\pm "), str(ZG2SF_val[year]).replace("+-"," \\pm "), str(WG2SF_val[year]).replace("+-"," \\pm "), str(QCD2SF_val[year]).replace("+-"," \\pm "), str(DY2SF_val[year]).replace("+-"," \\pm ")) )
    lines.append("\\cline{2-7} ")
    lines.append("& \\textbf{3j} & $%s$ & $%s$ & $%s$ & $%s$ & $%s$  \\\\ "%( str(misID3SF_val[year]).replace("+-"," \\pm "), str(ZG3SF_val[year]).replace("+-"," \\pm "), str(WG3SF_val[year]).replace("+-"," \\pm "), str(QCD3SF_val[year]).replace("+-"," \\pm "), str(DY3SF_val[year]).replace("+-"," \\pm ")) )
    lines.append("\\cline{2-7} ")
    lines.append("& \\textbf{4j} & $%s$ & $%s$ & $%s$ & $%s$ & $%s$ \\\\ "%( str(misID4SF_val[year]).replace("+-"," \\pm "), str(ZG4SF_val[year]).replace("+-"," \\pm "), str(WG4SF_val[year]).replace("+-"," \\pm "), str(QCD4SF_val[year]).replace("+-"," \\pm "), str(DY4SF_val[year]).replace("+-"," \\pm ")) )
    lines.append("\\cline{2-7} ")
    lines.append("& \\textbf{5j} & $%s$ & $%s$ & $%s$ & $%s$ & $%s$ \\\\ "%( str(misID5SF_val[year]).replace("+-"," \\pm "), str(ZG5SF_val[year]).replace("+-"," \\pm "), str(WG5SF_val[year]).replace("+-"," \\pm "), str(QCD5SF_val[year]).replace("+-"," \\pm "), str(DY5SF_val[year]).replace("+-"," \\pm ")) )
    lines.append("\\cline{2-7} ")
    lines.append("& \\textbf{$\\geq$2j} & $%s$ & $%s$ & $%s$ & $%s$ & $%s$  \\\\ "%( str(misID2pSF_val[year]).replace("+-"," \\pm "), str(ZG2pSF_val[year]).replace("+-"," \\pm "), str(WG2pSF_val[year]).replace("+-"," \\pm "), str(QCD2pSF_val[year]).replace("+-"," \\pm "), str(DY2pSF_val[year]).replace("+-"," \\pm ")) )
    lines.append("\\cline{2-7} ")
    lines.append("& \\textbf{$\\geq$3j} & $%s$ & $%s$ & $%s$ & $%s$ & $%s$  \\\\ "%( str(misID3pSF_val[year]).replace("+-"," \\pm "), str(ZG3pSF_val[year]).replace("+-"," \\pm "), str(WG3pSF_val[year]).replace("+-"," \\pm "), str(QCD3pSF_val[year]).replace("+-"," \\pm "), str(DY3pSF_val[year]).replace("+-"," \\pm ")) )
    lines.append("\\cline{2-7} ")
    lines.append("& \\textbf{$\\geq$4j} & $%s$ & $%s$ & $%s$ & $%s$ & $%s$  \\\\ "%( str(misID4pSF_val[year]).replace("+-"," \\pm "), str(ZG4pSF_val[year]).replace("+-"," \\pm "), str(WG4pSF_val[year]).replace("+-"," \\pm "), str(QCD4pSF_val[year]).replace("+-"," \\pm "), str(DY4pSF_val[year]).replace("+-"," \\pm ")) )
    lines.append("\\hline ")

lines.append("\\end{tabular} ")


with open("scalefactorTable.tex", "w") as f:
    for line in lines:
        f.write(line+"\n")
