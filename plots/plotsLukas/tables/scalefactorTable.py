from TTGammaEFT.Analysis.SetupHelpers import *

lines = []

lines.append("\\begin{tabular}{|c|c||c|c|c|c|c|} ")
lines.append("\\hline ")
lines.append(" & \\textbf{selection} & \\textbf{\\misIDSF} & \\textbf{Z$\\gamma$ SF} & \\textbf{W$\\gamma$ SF} & \\textbf{QCD SF} & \\textbf{DY+Jets SF}\\\\ ")
lines.append("\\hline ")

misID2SF_val["RunII"] = "-"
misID3SF_val["RunII"] = "-"
misID4SF_val["RunII"] = "-"
misID5SF_val["RunII"] = "-"
misID2pSF_val["RunII"] = "-"
misID3pSF_val["RunII"] = "-"
misID4pSF_val["RunII"] = "-"
for year in [2016, 2017, 2018, "RunII"]:
    lines.append("\\hline ")
    lines.append("\\multirow{7}{*}{\\rotatebox{90}{\\textbf{%s}}} & \\textbf{2 Jets, 0-tag} & $%s$ & $%s$ & $%s$ & $%s$ & $%s$ \\\\  "%(str(year), str(misID2SF_val[year]).replace("+-"," \\pm "), str(ZG2SF_val[year]).replace("+-"," \\pm "), str(WG2SF_val[year]).replace("+-"," \\pm "), str(QCD2SF_val[year]).replace("+-"," \\pm "), str(DY2SF_val[year]).replace("+-"," \\pm ")) )
    lines.append("\\cline{2-7} ")
    lines.append("& \\textbf{3 Jets, 0-tag} & $%s$ & $%s$ & $%s$ & $%s$ & $%s$  \\\\ "%( str(misID3SF_val[year]).replace("+-"," \\pm "), str(ZG3SF_val[year]).replace("+-"," \\pm "), str(WG3SF_val[year]).replace("+-"," \\pm "), str(QCD3SF_val[year]).replace("+-"," \\pm "), str(DY3SF_val[year]).replace("+-"," \\pm ")) )
    lines.append("\\cline{2-7} ")
    lines.append("& \\textbf{4 Jets, 0-tag} & $%s$ & $%s$ & $%s$ & $%s$ & $%s$ \\\\ "%( str(misID4SF_val[year]).replace("+-"," \\pm "), str(ZG4SF_val[year]).replace("+-"," \\pm "), str(WG4SF_val[year]).replace("+-"," \\pm "), str(QCD4SF_val[year]).replace("+-"," \\pm "), str(DY4SF_val[year]).replace("+-"," \\pm ")) )
    lines.append("\\cline{2-7} ")
    lines.append("& \\textbf{5 Jets, 0-tag} & $%s$ & $%s$ & $%s$ & $%s$ & $%s$ \\\\ "%( str(misID5SF_val[year]).replace("+-"," \\pm "), str(ZG5SF_val[year]).replace("+-"," \\pm "), str(WG5SF_val[year]).replace("+-"," \\pm "), str(QCD5SF_val[year]).replace("+-"," \\pm "), str(DY5SF_val[year]).replace("+-"," \\pm ")) )
    lines.append("\\cline{2-7} ")
    lines.append("& \\textbf{$\\geq$2 Jets, 0-tag} & $%s$ & $%s$ & $%s$ & $%s$ & $%s$  \\\\ "%( str(misID2pSF_val[year]).replace("+-"," \\pm "), str(ZG2pSF_val[year]).replace("+-"," \\pm "), str(WG2pSF_val[year]).replace("+-"," \\pm "), str(QCD2pSF_val[year]).replace("+-"," \\pm "), str(DY2pSF_val[year]).replace("+-"," \\pm ")) )
    lines.append("\\cline{2-7} ")
    lines.append("& \\textbf{$\\geq$3 Jets, 0-tag} & $%s$ & $%s$ & $%s$ & $%s$ & $%s$  \\\\ "%( str(misID3pSF_val[year]).replace("+-"," \\pm "), str(ZG3pSF_val[year]).replace("+-"," \\pm "), str(WG3pSF_val[year]).replace("+-"," \\pm "), str(QCD3pSF_val[year]).replace("+-"," \\pm "), str(DY3pSF_val[year]).replace("+-"," \\pm ")) )
    lines.append("\\cline{2-7} ")
    lines.append("& \\textbf{$\\geq$4 Jets, 0-tag} & $%s$ & $%s$ & $%s$ & $%s$ & $%s$  \\\\ "%( str(misID4pSF_val[year]).replace("+-"," \\pm "), str(ZG4pSF_val[year]).replace("+-"," \\pm "), str(WG4pSF_val[year]).replace("+-"," \\pm "), str(QCD4pSF_val[year]).replace("+-"," \\pm "), str(DY4pSF_val[year]).replace("+-"," \\pm ")) )
    lines.append("\\hline ")

lines.append("\\end{tabular} ")


with open("scalefactorTable.tex", "w") as f:
    for line in lines:
        f.write(line+"\n")
