import os, sys

from Analysis.Tools.u_float import u_float

tables = [
    "logsPaper/fakeFactors_2016_SR3PtUnfoldEFT.log",
    "logsPaper/fakeFactors_2016_SR4pPtUnfoldEFT.log",
    "logsPaper/fakeFactors_2017_SR3PtUnfoldEFT.log",
    "logsPaper/fakeFactors_2017_SR4pPtUnfoldEFT.log",
    "logsPaper/fakeFactors_2018_SR3PtUnfoldEFT.log",
    "logsPaper/fakeFactors_2018_SR4pPtUnfoldEFT.log",
]

def convertLine( line ):
# inclusive & 4134.95 $\pm$ 77.81 & \textbf{592.30 $\pm$ 27.19} & \textbf{587.32 $\pm$ 12.50}
# & 6494.72 $\pm$ 96.86 & \textbf{926.98 $\pm$ 34.25} & \textbf{951.09 $\pm$ 16.20}

    l = line.replace(" ", "").split("&")
    header = l[0] if l[0] else None
    norm   = u_float( float(l[1].split("$")[0]), float(l[1].split("$")[2]) )
    dd = l[2].split("{")[1].split("}")[0]
    ddfakes   = u_float( float(dd.split("$")[0]), float(dd.split("$")[2]) )
    mc = l[3].split("{")[1].split("}")[0]
    mcfakes   = u_float( float(mc.split("$")[0]), float(mc.split("$")[2]) )

    return header, norm, ddfakes, mcfakes

def readTable( file ):
    data = []
    with open( file, "r" ) as f:
        lines = f.readlines()[4:]
    for line in lines:
        header, norm, ddfakes, mcfakes = convertLine( line )
        if not header:
            header = data[-1][0]
        data.append( (header, norm, ddfakes, mcfakes) )
    return data

numbers = {}
for table in tables:
    dat = readTable( table )
    for (head, norm, dd, mc) in dat:
        if head not in numbers.keys():
            numbers[head] = {"norm":u_float(0), "dd":u_float(0), "mc":u_float(0)}
        numbers[head]["norm"] += norm
        numbers[head]["dd"]   += dd
        numbers[head]["mc"]   += mc

for key, val in numbers.iteritems():
    print key, val["norm"], "&", val["dd"], "&", val["mc"], "&", val["dd"]/ val["mc"], "\\\\"
