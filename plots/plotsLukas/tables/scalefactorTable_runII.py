from TTGammaEFT.Analysis.SetupHelpers import *

misID2SF_val["RunII"] = "-"
misID3SF_val["RunII"] = "-"
misID4SF_val["RunII"] = "-"
misID5SF_val["RunII"] = "-"
misID2pSF_val["RunII"] = "-"
misID3pSF_val["RunII"] = "-"
misID4pSF_val["RunII"] = "-"

lines = []
lines.append("\\begin{tabular}{|c|r||ccc|c|c|c|c|} ")
lines.append("\\hline ")
lines.append(" & \\textbf{\\nJet} & \\multicolumn{3}{c|}{\\textbf{\\misIDSF 16/17/18}} & \\textbf{\\ZGamma SF} & \\textbf{\\WGamma SF} & \\textbf{multijets SF} & \\textbf{\\DYJets SF}\\\\ ")
lines.append("\\hline ")

lines.append("\\hline ")
lines.append("\\multirow{8}{*}{\\rotatebox{90}{\\textbf{RunII}}} & \\textbf{2j} & $\\pm$ & $\\pm$ & $\\pm$ & $%s$ & $%s$ & $%s$ & $%s$ \\\\  "%(str(ZG2SF_val["RunII"]).replace("+-"," \\pm "), str(WG2SF_val["RunII"]).replace("+-"," \\pm "), str(QCD2SF_val["RunII"]).replace("+-"," \\pm "), str(DY2SF_val["RunII"]).replace("+-"," \\pm ")) )
lines.append("\\cline{2-9} ")
lines.append("& \\textbf{3j} & $\\pm$ & $\\pm$ & $\\pm$ & $%s$ & $%s$ & $%s$ & $%s$ \\\\ "%( str(ZG3SF_val["RunII"]).replace("+-"," \\pm "), str(WG3SF_val["RunII"]).replace("+-"," \\pm "), str(QCD3SF_val["RunII"]).replace("+-"," \\pm "), str(DY3SF_val["RunII"]).replace("+-"," \\pm ")) )
lines.append("\\cline{2-9} ")
lines.append("& \\textbf{4j} & $\\pm$ & $\\pm$ & $\\pm$ & $%s$ & $%s$ & $%s$ & $%s$ \\\\ "%( str(ZG4SF_val["RunII"]).replace("+-"," \\pm "), str(WG4SF_val["RunII"]).replace("+-"," \\pm "), str(QCD4SF_val["RunII"]).replace("+-"," \\pm "), str(DY4SF_val["RunII"]).replace("+-"," \\pm ")) )
lines.append("\\cline{2-9} ")
lines.append("& \\textbf{5j} & $\\pm$ & $\\pm$ & $\\pm$ & $%s$ & $%s$ & $%s$ & $%s$ \\\\ "%( str(ZG5SF_val["RunII"]).replace("+-"," \\pm "), str(WG5SF_val["RunII"]).replace("+-"," \\pm "), str(QCD5SF_val["RunII"]).replace("+-"," \\pm "), str(DY5SF_val["RunII"]).replace("+-"," \\pm ")) )
lines.append("\\cline{2-9} ")
lines.append("& \\textbf{$\\geq$2j} & $\\pm$ & $\\pm$ & $\\pm$ & $%s$ & $%s$ & $%s$ & $%s$  \\\\ "%( str(ZG2pSF_val["RunII"]).replace("+-"," \\pm "), str(WG2pSF_val["RunII"]).replace("+-"," \\pm "), str(QCD2pSF_val["RunII"]).replace("+-"," \\pm "), str(DY2pSF_val["RunII"]).replace("+-"," \\pm ")) )
lines.append("\\cline{2-9} ")
lines.append("& \\textbf{$\\geq$3j} & $\\pm$ & $\\pm$ & $\\pm$ & $%s$ & $%s$ & $%s$ & $%s$ \\\\ "%( str(ZG3pSF_val["RunII"]).replace("+-"," \\pm "), str(WG3pSF_val["RunII"]).replace("+-"," \\pm "), str(QCD3pSF_val["RunII"]).replace("+-"," \\pm "), str(DY3pSF_val["RunII"]).replace("+-"," \\pm ")) )
lines.append("\\cline{2-9} ")
lines.append("& \\textbf{$\\geq$4j} & $\\pm$ & $\\pm$ & $\\pm$ & $%s$ & $%s$ & $%s$ & $%s$ \\\\ "%( str(ZG4pSF_val["RunII"]).replace("+-"," \\pm "), str(WG4pSF_val["RunII"]).replace("+-"," \\pm "), str(QCD4pSF_val["RunII"]).replace("+-"," \\pm "), str(DY4pSF_val["RunII"]).replace("+-"," \\pm ")) )
lines.append("\\cline{2-9} ")
lines.append("& \\textbf{3j$\\otimes\\geq$4j} & $\\pm$ & $\\pm$ & $\\pm$ & $\\pm$ & $\\pm$ & $\\pm$ & $\\pm$ \\\\ " )
lines.append("\\hline ")

lines.append("\\end{tabular} ")


with open("scalefactorTable_RunII.tex", "w") as f:
    for line in lines:
        f.write(line+"\n")

