import ROOT
import os
import ctypes
import copy
import shutil
from functools                      import partial
from array                          import array

from RootTools.core.standard        import *

from TTGammaEFT.Tools.user              import plot_directory


# Plot style
ROOT.gROOT.LoadMacro('$CMSSW_BASE/src/Analysis/Tools/scripts/tdrstyle.C')
ROOT.setTDRStyle()

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--testGrayscale",   action='store_true',            help="Because of  reasons...")
argParser.add_argument("--preliminary",     action='store_true',            help="Because of  reasons...")
args = argParser.parse_args()

## define all the results. BSM
res = [\
    {   'name': 'e+jets',
        'tex': 'e+jets',
        'limits': {'total':(+0.085,-0.081), 'stat':(+0.015, -0.015), 'syst':(+0.083, -0.080), 'center':1.109, 'theory':0.16}
    },
    {   'name': 'mu+jets',
        'tex': '#mu+jets',
        'limits': {'total':(+0.071, -0.069), 'stat':(+0.011, -0.011), 'syst':(+0.070, -0.068), 'center':1.076, 'theory':0.16}
    },
    {   'name': 'l+jets',
        'tex': 'l+jets',
        'limits': {'total':(+0.069, -0.067), 'stat':(+0.009, -0.009), 'syst':(+0.068, -0.066), 'center':1.064, 'theory':0.16}
    },
]

ordering = ['total', 'stat']

styles = {
    'total': {'color':ROOT.kBlack, 'style':1, 'width':4},
    'stat':  {'color':ROOT.kRed+1, 'style':1, 'width':4},
    }

cans = ROOT.TCanvas("cans","",10,10,700,700)
cans.Range(-10,-1,10,1)

if args.testGrayscale:
    cans.SetGrayscale()

# draw the axis
upper = 1.55
lower = 0.7

axis = ROOT.TGaxis(-9.5,-0.75,9.5,-0.75,lower,upper,505,"")
axisUpper = ROOT.TGaxis(-9.5,0.85,9.5,0.85,lower,upper,505,"-")
axisUpper.SetLabelOffset(10)
axis.SetName("axis")
axis.SetLabelSize(0.035)
axis.SetTitleOffset(0.9)
axis.SetTitle("#sigma_{t#bar{t}#gamma}/#sigma^{NLO}_{t#bar{t}#gamma}")
axis.Draw()
axisUpper.Draw()

zero_point = -2.794 #1 #-0.5 #(((upper-1)+(lower-1))*0.5)*19
print zero_point
zero = ROOT.TLine(zero_point,-0.75,zero_point,0.85)
zero.SetLineStyle(1)

box1 = ROOT.TLine(-9.5, -0.75, -9.5, 0.85)
box2 = ROOT.TLine(9.5, -0.75, 9.5, 0.85)
box3 = ROOT.TLine(-9.5, 0.85, 9.5, 0.85)

pads = []

### Get all the pads ###
points = []
boxes = []
text  = []
fillColor = ROOT.kOrange-9

for p in range(len(res)):
    y_lo = 0.9-0.7*((p+1.)/len(res))
    y_hi = 0.9-0.7*(float(p)/len(res))

    pads.append(ROOT.TPad("pad_%s"%p,"pad_%s"%p, 0.5/20, y_lo, 19.5/20, y_hi ))
    pads[-1].Range(lower,0,upper,5)
    pads[-1].SetFillColor(0)
    pads[-1].Draw()
    pads[-1].cd()
    
    box = ROOT.TBox( 1-res[p]['limits']['theory'], 0, 1+res[p]['limits']['theory'], 2 )
    box.SetLineColor(fillColor)
    box.SetLineWidth(0)
    box.SetFillColor(fillColor)
    boxes.append(box)
    box.Draw()

    latex2 = ROOT.TLatex()
#    latex2.SetNDC()
    latex2.SetTextSize(0.1)
    latex2.SetTextAlign(11)
    text.append(latex2)
    latex2.DrawLatex(lower+0.05, 0.8, res[p]['tex'])

    latex3 = ROOT.TLatex()
#    latex3.SetNDC()
    latex3.SetTextSize(0.1)
    latex3.SetTextAlign(11)
    text.append(latex3)

    if p==0:
        latex3.DrawLatex(1.30, 2.2, " Total")
        latex3.DrawLatex(1.37, 2.2, "#bf{  (Stat}")
        latex3.DrawLatex(1.44, 2.2, "#bf{ Syst)}")

    latex3.DrawLatex(1.23, 0.8, "%.3f"%(res[p]['limits']['center']))
    latex3.DrawLatex(1.30, 0.8-0.25, " %.3f"%(res[p]['limits']['total'][1]))
    latex3.DrawLatex(1.30, 0.8+0.25, "+%.3f"%(res[p]['limits']['total'][0]))
    latex3.DrawLatex(1.37, 0.8-0.25, "#bf{( %.3f}"%(res[p]['limits']['stat'][1]))
    latex3.DrawLatex(1.37, 0.8+0.25, "#bf{(+%.3f}"%(res[p]['limits']['stat'][0]))
    latex3.DrawLatex(1.44, 0.8-0.25, "#bf{ %.3f)}"%(res[p]['limits']['syst'][1]))
    latex3.DrawLatex(1.44, 0.8+0.25, "#bf{+%.3f)}"%(res[p]['limits']['syst'][0]))

    # put the stuff
    graphs  = []
    res[p]['lines'] = []
    for i, o in enumerate(ordering):
        limits = [(res[p]['limits']['center']+res[p]['limits'][o][1],res[p]['limits']['center']+res[p]['limits'][o][0])]
        print o, limits
        x = []
        y = []
        y_err = []
        x_plus = []
        x_minus = []

        for j,l in enumerate(limits):
            start = 1
            newLines = []
            newLines += [   ROOT.TLine(l[0], start,       l[1], start),
                            ROOT.TLine(l[0], start+0.15,  l[0], start-0.15),
                            ROOT.TLine(l[1], start+0.15,  l[1], start-0.15)]
            for k,line in enumerate(newLines):
                line.SetLineColor(styles[o]['color'])
                line.SetLineWidth(styles[o]['width'])
                if k == 0:
                    line.SetLineStyle(styles[o]['style'])
            
            res[p]['lines'] += copy.deepcopy(newLines)
    
    for l in res[p]['lines']:
        l.Draw()

    point = ROOT.TGraph(1)
    point.SetName("point"+str(p))
    point.SetPoint(1,res[p]['limits']['center'],1)
    point.SetMarkerColor(ROOT.kBlack)
    points.append(point)
    points[-1].Draw("psame")

    cans.cd()


cans.cd()


## need a legend
leg = ROOT.TLegend(0.05,0.9-0.04*(len(ordering)+1),0.40,0.9)
leg.SetFillColor(ROOT.kWhite)
leg.SetShadowColor(ROOT.kWhite)
leg.SetBorderSize(0)
leg.SetTextSize(0.035)
leg.AddEntry(res[0]['lines'][0],  "#bf{Total Error}", 'l')
leg.AddEntry(res[2]['lines'][3],  "#bf{Statistical Error}", 'l')
leg.AddEntry(boxes[0],  "#bf{Theory Error}", 'f')

leg.Draw()

zero.Draw()
box1.Draw()
box2.Draw()
box3.Draw()


l1 = ROOT.TLine()
l1.SetLineColor(ROOT.kBlack)
l1.SetLineWidth(3)
l1.DrawLineNDC(0.063,0.873,0.063,0.887)
l1.DrawLineNDC(0.125,0.873,0.125,0.887)

l2 = ROOT.TLine()
l2.SetLineColor(ROOT.kRed+1)
l2.SetLineWidth(3)
l2.DrawLineNDC(0.063,0.833,0.063,0.847)
l2.DrawLineNDC(0.125,0.833,0.125,0.847)

## finish it off

latex1 = ROOT.TLatex()
latex1.SetNDC()
latex1.SetTextSize(0.035)
latex1.SetTextAlign(11)

#if args.preliminary:
latex1.DrawLatex(0.03,0.94,'CMS #bf{#it{Preliminary}}')
latex1.DrawLatex(0.7,0.94, "137.2 fb{}^{-1} (13 TeV)")
#else:
#    latex1.DrawLatex(0.03,0.94,'CMS')

plotDir = plot_directory + "summary/"

if not os.path.isdir(plotDir):
    os.makedirs(plotDir)

if args.testGrayscale:
    postFix += '_gray'

for e in [".png",".pdf",".root"]:
    cans.Print(plotDir+"summaryResult"+e)

