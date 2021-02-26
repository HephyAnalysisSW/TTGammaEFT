""" 
run combine -M GoodnessOfFit datacard.txt --algo=saturated --fixedSignalStrength=1 -t 1000 --toysFreq and plot the output with this script
or parallelized:
for seed in {1234..1243}; do combine -M GoodnessOfFit datacard.txt --algo=saturated --fixedSignalStrength --toysFreq -t 1000 -s ${seed} & done; wait
"""

import ROOT, os, uuid
import numpy as np
from RootTools.core.standard          import *
from RootTools.plot.helpers    import copyIndexPHP
from TTGammaEFT.Tools.user            import plot_directory
import Analysis.Tools.syncer


""" 
mean   expected limit: r < 99.8064 +/- 0.446639 @ 95%CL (1000 toyMC)
median expected limit: r < 98.9029 @ 95%CL (1000 toyMC)
   68% expected band : 85.559 < r < 113.684
   95% expected band : 74.6301 < r < 129.843
"""

plot_directory_ = os.path.join( plot_directory, "gof", "v2")

filename = "data.root"
object = "limit"
n = 10000
measured = 109.439

rootFile = ROOT.TFile( filename, "READ")
print rootFile
ttree = rootFile.Get(object)
print ttree
tmp=str(uuid.uuid4())
hist = ROOT.TH1D(tmp, tmp, 20, 50, 160)
ttree.Draw("limit>>"+tmp)

q=np.array([0.])
prob=np.array([0.5])
hist.GetQuantiles(1, q, prob)
medVal = q[0]
print medVal

prob=np.array([0.16])
hist.GetQuantiles(1, q, prob)
low1s = q[0]
print low1s

prob=np.array([0.84])
hist.GetQuantiles(1, q, prob)
high1s = q[0]
print high1s

prob=np.array([0.025])
hist.GetQuantiles(1, q, prob)
low2s = q[0]
print low2s

prob=np.array([0.975])
hist.GetQuantiles(1, q, prob)
high2s = q[0]
print high2s

hist.legendText = "Goodness of Fit Test, N_{toys} = %i"%n
hist.style = styles.lineStyle( ROOT.kBlue, width=3)

legEntry = hist.Clone()
legEntry.Scale(0)
legEntry.legendText = "Median = %.1f"%medVal
legEntry.style = styles.lineStyle( ROOT.kBlack, width=2)

measlegEntry = hist.Clone()
measlegEntry.Scale(0)
measlegEntry.legendText = "Measured = %.1f"%measured
measlegEntry.style = styles.lineStyle( ROOT.kBlack, width=2, dashed=True)

sig1legEntry = hist.Clone()
sig1legEntry.Scale(0)
sig1legEntry.legendText = "68% CL"
sig1legEntry.style = styles.lineStyle( ROOT.kSpring-1, width=2)

sig2legEntry = hist.Clone()
sig2legEntry.Scale(0)
sig2legEntry.legendText = "95% CL"
sig2legEntry.style = styles.lineStyle( ROOT.kOrange+7, width=2)

maxH = hist.GetMaximum()*1.2

med = ROOT.TLine(medVal, 0, medVal , maxH)
med.SetLineWidth(3)
#med.SetLineStyle(7)
med.SetLineColor(ROOT.kBlack)

meas = ROOT.TLine(measured, 0, measured , maxH)
meas.SetLineWidth(3)
meas.SetLineStyle(7)
meas.SetLineColor(ROOT.kBlack)

low1sig = ROOT.TLine(low1s, 0, low1s , maxH)
low1sig.SetLineWidth(3)
#low1sig.SetLineStyle(7)
low1sig.SetLineColor(ROOT.kSpring-1)

high1sig = ROOT.TLine(high1s, 0, high1s , maxH)
high1sig.SetLineWidth(3)
#high1sig.SetLineStyle(7)
high1sig.SetLineColor(ROOT.kSpring-1)

low2sig = ROOT.TLine(low2s, 0, low2s , maxH)
low2sig.SetLineWidth(3)
#low2sig.SetLineStyle(7)
low2sig.SetLineColor(ROOT.kOrange+7)

high2sig = ROOT.TLine(high2s, 0, high2s , maxH)
high2sig.SetLineWidth(3)
#high2sig.SetLineStyle(7)
high2sig.SetLineColor(ROOT.kOrange+7)

allLines = [low1sig, high1sig, low2sig, high2sig, med, meas]

histModifications  = []
histModifications += [lambda h: h.GetYaxis().SetTitleOffset(1.5)]

# Text on the plots
def drawObjects( offset=0 ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    line = (0.8-offset, 0.95, "(13 TeV)") 
    lines = [
      (0.15, 0.95, "CMS #bf{#it{Preliminary}}"), 
      line
    ]
    return [tex.DrawLatex(*l) for l in lines]

def draw( plot, **kwargs):
    plotting.draw(plot,
        plot_directory = plot_directory_,
        logX = False, sorting = False,
        drawObjects    = drawObjects() + allLines,
        yRange = (0.1,2600),
        legend         = (0.20,0.7,0.7,0.91),
        copyIndexPHP   = True,
        histModifications=histModifications,
        **kwargs
      )

for logY in [True, False]:
    plot = Plot.fromHisto( name = 'gof' + ('_log' if logY else ''),  histos = [[hist], [measlegEntry], [legEntry], [sig1legEntry], [sig2legEntry] ], texX = "test statistics", texY = "Entries")
    plot.stack = None
    draw(plot, logY = logY, 
        )

