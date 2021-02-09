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
        'limits': {'total':(+0.075,-0.072), 'stat':(+0.014, -0.014), 'syst':(+0.073, -0.070), 'center':1.048, 'theory':0.175}
    },
    {   'name': 'mu+jets',
        'tex': '#mu+jets',
        'limits': {'total':(+0.063, -0.061), 'stat':(+0.011, -0.011), 'syst':(+0.062, -0.060), 'center':1.052, 'theory':0.175}
    },
    {   'name': 'l+jets',
        'tex': 'l+jets',
        'limits': {'total':(+0.060, -0.058), 'stat':(+0.009, -0.009), 'syst':(+0.059, -0.057), 'center':1.034, 'theory':0.175}
    },
]

ordering = ['total', 'stat']

styles = {
    'total': {'color':ROOT.kBlack, 'style':1, 'width':4},
    'stat':  {'color':ROOT.kRed+1, 'style':1, 'width':4},
    }

cans = ROOT.TCanvas("cans","",10,10,700,600)
cans.Range(-10,-1,10,1)

if args.testGrayscale:
    cans.SetGrayscale()

# draw the axis
upper = 1.55
lower = 0.7

axis = ROOT.TGaxis(-9.5,-0.65,9.5,-0.65,lower,upper,505,"")
axisUpper = ROOT.TGaxis(-9.5,0.85,9.5,0.85,lower,upper,505,"-")
axisUpper.SetLabelOffset(10)
axis.SetName("axis")
axis.SetLabelSize(0.04)
axis.SetTitleSize(0.045)
axis.SetTitleOffset(0.8)
axis.SetTitle("#sigma_{t#bar{t}#gamma}/#sigma^{NLO}_{t#bar{t}#gamma}")
axis.Draw()
axisUpper.Draw()

zero_point = -2.794 #1 #-0.5 #(((upper-1)+(lower-1))*0.5)*19
zero = ROOT.TLine(zero_point,-0.65,zero_point,0.85)
zero.SetLineWidth(2)
zero.SetLineStyle(1)

box1 = ROOT.TLine(-9.5, -0.65, -9.5, 0.85)
box2 = ROOT.TLine(9.5, -0.65, 9.5, 0.85)
box3 = ROOT.TLine(-9.5, 0.85, 9.5, 0.85)

pads = []

### Get all the pads ###
points = []
boxes = []
text  = []
fillColor = ROOT.kOrange-9

for p in range(len(res)):
    y_lo = 0.9-0.5*((p+1.)/len(res))-0.16
    y_hi = 0.9-0.5*(float(p)/len(res))-0.16

    print y_lo, y_hi
    pads.append(ROOT.TPad("pad_%s"%p,"pad_%s"%p, 0.5/20, y_lo, 19.5/20, y_hi ))
    pads[-1].Range(lower,0,upper,2.5)
    pads[-1].SetFillColor(0)
    pads[-1].Draw()
    pads[-1].cd()
    
    boxes.append( ROOT.TBox( 1-res[p]['limits']['theory'], 0, 1+res[p]['limits']['theory'], 2 ) )
    boxes[-1].SetLineColor(fillColor)
    boxes[-1].SetLineWidth(0)
    boxes[-1].SetFillColor(fillColor)
    boxes[-1].Draw()

    latex2 = ROOT.TLatex()
#    latex2.SetNDC()
    latex2.SetTextSize(0.18)
    latex2.SetTextAlign(11)
    text.append(latex2)
    latex2.DrawLatex(lower+0.05, 0.8, res[p]['tex'])

    latex3 = ROOT.TLatex()
#    latex3.SetNDC()
    latex3.SetTextSize(0.18)
    latex3.SetTextAlign(11)
    text.append(latex3)

    if p==0:
        latex3.DrawLatex(1.30, 2.2, " Total")
        latex3.DrawLatex(1.38, 2.2, "#bf{  (Stat}")
        latex3.DrawLatex(1.46, 2.2, "#bf{ Syst)}")

    latex3.DrawLatex(1.23, 0.8, "%.3f"%(res[p]['limits']['center']))
    latex3.DrawLatex(1.30, 0.8-0.25, " %.3f"%(res[p]['limits']['total'][1]))
    latex3.DrawLatex(1.30, 0.8+0.25, "+%.3f"%(res[p]['limits']['total'][0]))
    latex3.DrawLatex(1.38, 0.8-0.25, "#bf{( %.3f}"%(res[p]['limits']['stat'][1]))
    latex3.DrawLatex(1.38, 0.8+0.25, "#bf{(+%.3f}"%(res[p]['limits']['stat'][0]))
    latex3.DrawLatex(1.46, 0.8-0.25, "#bf{ %.3f)}"%(res[p]['limits']['syst'][1]))
    latex3.DrawLatex(1.46, 0.8+0.25, "#bf{+%.3f)}"%(res[p]['limits']['syst'][0]))

    # put the stuff
    graphs  = []
    res[p]['lines'] = []
    for i, o in enumerate(ordering):
        limits = [(res[p]['limits']['center']+res[p]['limits'][o][1],res[p]['limits']['center']+res[p]['limits'][o][0])]
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
leg = ROOT.TLegend(0.03,0.88-0.04*(len(ordering)+1),0.40,0.88)
leg.SetFillColor(ROOT.kWhite)
leg.SetShadowColor(ROOT.kWhite)
leg.SetBorderSize(0)
leg.SetTextSize(0.035)
leg.AddEntry(res[0]['lines'][0],  "#bf{Total Uncertainty}", 'l')
leg.AddEntry(res[2]['lines'][3],  "#bf{Stat. Uncertainty}", 'l')
leg.AddEntry(boxes[0],  "#bf{Theory Uncertainty}", 'f')

leg.Draw()

zero.Draw()
box1.Draw()
box2.Draw()
box3.Draw()


l1 = ROOT.TLine()
l1.SetLineColor(ROOT.kBlack)
l1.SetLineWidth(3)
l1.DrawLineNDC(0.043,0.853,0.043,0.867)
l1.DrawLineNDC(0.11,0.853,0.11,0.867)

l2 = ROOT.TLine()
l2.SetLineColor(ROOT.kRed+1)
l2.SetLineWidth(3)
l2.DrawLineNDC(0.043,0.813,0.043,0.827)
l2.DrawLineNDC(0.11,0.813,0.11,0.827)

## finish it off

latex1 = ROOT.TLatex()
latex1.SetNDC()
latex1.SetTextSize(0.045)
latex1.SetTextAlign(11)

#if args.preliminary:
latex1.DrawLatex(0.03,0.94,'CMS #bf{#it{Preliminary}}')
latex1.DrawLatex(0.68,0.94, "137.2 fb{}^{-1} (13 TeV)")
#else:
#    latex1.DrawLatex(0.03,0.94,'CMS')

plotDir = plot_directory + "summary/"

if not os.path.isdir(plotDir):
    os.makedirs(plotDir)

if args.testGrayscale:
    postFix += '_gray'

for e in [".png",".pdf",".root"]:
    cans.Print(plotDir+"summaryResult"+e)

