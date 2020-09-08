file = open("mlp.sh","w")
file.write("python train_MVA_Top_vs_TTG.py --mva bdt --variables varlist1  --NTrees 25 --maxdepth 1 --ncuts 50 --overwrite \n")
for i in range(1,6):
    NTrees = 25
    for j in range(5):
        ncuts = 50
        for k in range(4):
            file.write("python train_MVA_Top_vs_TTG.py --mva bdt --variables varlist1 --NTrees "+str(NTrees)+" --maxdepth "+str(i)+" --ncuts "+str(ncuts)+"\n")
            ncuts *= 2
        NTrees *= 2

file.close()
