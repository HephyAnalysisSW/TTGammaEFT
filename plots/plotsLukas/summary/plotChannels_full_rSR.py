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

## with 3+4jet CR
res = [\
    {   'name': 'e+jets, 3 jets',
        'tex': 'e+jets',
        'limits': {'total':0.091, 'stat':0.009, 'syst':0.091, 'center':0.990, 'theory':0.167}
    },
    {   'name': 'mu+jets, 3 jets',
        'tex': '#mu+jets',
        'limits': {'total':0.078, 'stat':0.009, 'syst':0.077, 'center':0.952, 'theory':0.175}
    },
    {   'name': 'l+jets, 3 jets',
        'tex': 'l+jets',
        'limits': {'total':0.076, 'stat':0.009, 'syst':0.075, 'center':0.958, 'theory':0.175}
    },
    {   'name': 'e+jets, 4 jets',
        'tex': 'e+jets',
        'limits': {'total':0.072, 'stat':0.009, 'syst':0.071, 'center':1.030, 'theory':0.175}
    },
    {   'name': 'mu+jets, 4 jets',
        'tex': '#mu+jets',
        'limits': {'total':0.067, 'stat':0.009, 'syst':0.066, 'center':1.055, 'theory':0.175}
    },
    {   'name': 'l+jets, 4 jets',
        'tex': 'l+jets',
        'limits': {'total':0.065, 'stat':0.009, 'syst':0.064, 'center':1.043, 'theory':0.175}
    },
    {   'name': 'e+jets, combined',
        'tex': 'e+jets',
        'limits': {'total':0.067, 'stat':0.009, 'syst':0.066, 'center':1.027, 'theory':0.175}
    },
    {   'name': 'mu+jets, combined',
        'tex': '#mu+jets',
        'limits': {'total':0.063, 'stat':0.009, 'syst':0.062, 'center':1.033, 'theory':0.175}
    },
    {   'name': 'l+jets, combined',
        'tex': 'l+jets',
        'limits': {'total':0.062, 'stat':0.009, 'syst':0.062, 'center':1.032, 'theory':0.175}
    },
]

## define all the results. BSM
# with 3 OR 4 jet CR for 3/4jet channel
#res = [\
#    {   'name': 'e+jets, 3 jets',
#        'tex': 'e+jets',
#        'limits': {'total':(+0.109,-0.107), 'stat':(+0.024, -0.024), 'syst':(+0.106, -0.104), 'center':1.126, 'theory':0.167}
#    },
#    {   'name': 'mu+jets, 3 jets',
#        'tex': '#mu+jets',
#        'limits': {'total':(+0.091,-0.090), 'stat':(+0.018, -0.018), 'syst':(+0.089, -0.088), 'center':0.991, 'theory':0.167}
#    },
#    {   'name': 'l+jets, 3 jets',
#        'tex': 'l+jets',
#        'limits': {'total':(+0.089,-0.088), 'stat':(+0.015, -0.015), 'syst':(+0.087, -0.087), 'center':1.006, 'theory':0.167}
#    },
#    {   'name': 'e+jets, 4 jets',
#        'tex': 'e+jets',
#        'limits': {'total':(+0.084,-0.080), 'stat':(+0.018, -0.018), 'syst':(+0.082, -0.078), 'center':1.056, 'theory':0.179}
#    },
#    {   'name': 'mu+jets, 4 jets',
#        'tex': '#mu+jets',
#        'limits': {'total':(+0.075,-0.072), 'stat':(+0.015, -0.015), 'syst':(+0.073, -0.070), 'center':1.079, 'theory':0.179}
#    },
#    {   'name': 'l+jets, 4 jets',
#        'tex': 'l+jets',
#        'limits': {'total':(+0.073,-0.070), 'stat':(+0.012, -0.012), 'syst':(+0.072, -0.069), 'center':1.065, 'theory':0.179}
#    },
#    {   'name': 'e+jets, 3+4 jets',
#        'tex': 'e+jets',
#        'limits': {'total':(+0.075,-0.072), 'stat':(+0.014, -0.014), 'syst':(+0.073, -0.070), 'center':1.048, 'theory':0.175}
#    },
#    {   'name': 'mu+jets, 3+4 jets',
#        'tex': '#mu+jets',
#        'limits': {'total':(+0.063, -0.061), 'stat':(+0.011, -0.011), 'syst':(+0.062, -0.060), 'center':1.052, 'theory':0.175}
#    },
#    {   'name': 'l+jets, 3+4 jets',
#        'tex': 'l+jets',
#        'limits': {'total':(+0.060, -0.058), 'stat':(+0.009, -0.009), 'syst':(+0.059, -0.057), 'center':1.034, 'theory':0.175}
#    },
#]

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

axis = ROOT.TGaxis(-9.5,-0.73,9.5,-0.73,lower,upper,505,"+S")
axisUpper = ROOT.TGaxis(-9.5,0.85,9.5,0.85,lower,upper,505,"-S")
axisUpper.SetLabelOffset(10)
axisUpper.SetTickSize(0.02)
axis.SetTickSize(0.02)
axis.SetName("axis")
axis.SetLabelSize(0.038)
axis.SetTitleSize(0.045)
axis.SetTitleOffset(0.9)
axis.SetTitle("#sigma_{t#bar{t}#gamma}/#sigma^{NLO}_{t#bar{t}#gamma}")
axis.Draw()
axisUpper.Draw()

zero_point = -2.794 #1 #-0.5 #(((upper-1)+(lower-1))*0.5)*19
zero = ROOT.TLine(zero_point,-0.73,zero_point,0.58)
zero.SetLineWidth(2)
zero.SetLineStyle(1)

box1 = ROOT.TLine(-9.5, -0.73, -9.5, 0.85)
box2 = ROOT.TLine(9.5, -0.73, 9.5, 0.85)
box3 = ROOT.TLine(-9.5, 0.85, 9.5, 0.85)

pads = []
### Get all the pads ###
points = []
boxes = []
text  = []

fillColor = ROOT.kOrange-9

gap = 0
for p in range(len(res)):
    if (p>0 and not p%3) or p==len(res)-1:
        print p
        gap +=0.02

    y_lo = 0.99-0.58*((p+1.)/len(res))-0.18-gap
    y_hi = 0.99-0.58*(float(p)/len(res))-0.18-gap

    pads.append(ROOT.TPad("pad_%s"%p,"pad_%s"%p, 0.5/20, y_lo, 19.5/20, y_hi ))
    pads[-1].Range(lower,0,upper,2.5)
    pads[-1].SetFillColor(0)
    pads[-1].Draw()
    pads[-1].cd()
    
    boxes.append( ROOT.TBox( 1-res[p]['limits']['theory'], -0.5, 1+res[p]['limits']['theory'], 2.5 ) )
    boxes[-1].SetLineColor(fillColor)
    boxes[-1].SetLineWidth(0)
    boxes[-1].SetFillColor(fillColor)
    boxes[-1].Draw()

    latex2 = ROOT.TLatex()
#    latex2.SetNDC()
    latex2.SetTextSize(0.45)
    latex2.SetTextAlign(11)
    text.append(latex2)
    latex2.DrawLatex(lower+0.05, 0.8, res[p]['tex'])

    latex3 = ROOT.TLatex()
#    latex3.SetNDC()
    latex3.SetTextSize(0.45)
    latex3.SetTextAlign(11)
    text.append(latex3)

#    if p==0:
#        latex3.DrawLatex(1.30, 2.1, " Total")
#        latex3.DrawLatex(1.38, 2.1, "#bf{  (Stat}")
#        latex3.DrawLatex(1.46, 2.1, "#bf{ Syst)}")

    latex3.DrawLatex(1.23, 0.8, "%.3f"%(res[p]['limits']['center']))
#    latex3.DrawLatex(1.30, 0.8-0.45, " %.3f"%(res[p]['limits']['total'][1]))
    latex3.DrawLatex(1.30, 0.8, "#pm%.3f"%(res[p]['limits']['total']))
#    latex3.DrawLatex(1.38, 0.8-0.45, "#bf{( %.3f}"%(res[p]['limits']['stat'][1]))
    latex3.DrawLatex(1.38, 0.8, "#bf{(#pm%.3f}"%(res[p]['limits']['stat']))
#    latex3.DrawLatex(1.46, 0.8-0.45, "#bf{ %.3f)}"%(res[p]['limits']['syst'][1]))
    latex3.DrawLatex(1.46, 0.8, "#bf{#pm%.3f)}"%(res[p]['limits']['syst']))

    # put the stuff
    graphs  = []
    res[p]['lines'] = []
    for i, o in enumerate(ordering):
        limits = [(res[p]['limits']['center']-res[p]['limits'][o],res[p]['limits']['center']+res[p]['limits'][o])]
        x = []
        y = []
        y_err = []
        x_plus = []
        x_minus = []

        for j,l in enumerate(limits):
            start = 1
            newLines = []
            newLines += [   ROOT.TLine(l[0], start,       l[1], start),
                            ROOT.TLine(l[0], start+0.28,  l[0], start-0.28),
                            ROOT.TLine(l[1], start+0.28,  l[1], start-0.28)]
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


y_lo = 0.97-0.5*(1./len(res))-0.14
y_hi = 0.97-0.14
pads.append(ROOT.TPad("pad_-1","pad_-1", 0.5/20, y_lo, 19.5/20, y_hi ))
pads[-1].Range(lower,0,upper,2.5)
pads[-1].SetFillStyle(0)
pads[-1].Draw()
pads[-1].cd()
latex3 = ROOT.TLatex()
latex3.SetTextSize(0.5)
latex3.SetTextAlign(11)
text.append(latex3)

latex3.DrawLatex(1.30, 1.6, " Total")
latex3.DrawLatex(1.38, 1.6, "#bf{  (Stat}")
latex3.DrawLatex(1.46, 1.6, "#bf{ Syst)}")
cans.cd()

latex4 = ROOT.TLatex()
#latex4.SetNDC()
latex4.SetTextSize(0.034)
latex4.SetTextAlign(11)
latex4.SetTextAngle(90)

latex4.DrawLatex(-8.9, 0.32, "3 jets")
latex4.DrawLatex(-8.9, -0.12, "#geq4 jets")
latex4.DrawLatex(-8.9, -0.62, "combined")


## need a legend
leg = ROOT.TLegend(0.08,0.85,0.91,0.89)
leg.SetNColumns(3);
#leg.SetFillColor(ROOT.kWhite)
leg.SetFillStyle(0)
#leg.SetShadowColor(ROOT.kWhite)
leg.SetBorderSize(0)
leg.SetTextSize(0.032)
leg.AddEntry(res[2]['lines'][3],  "#bf{Stat. uncertainty}", 'l')
leg.AddEntry(res[0]['lines'][0],  "#bf{Total uncertainty}", 'l')
leg.AddEntry(boxes[0],  "#bf{Theory uncertainty}", 'f')

leg.Draw()

zero.Draw()
box1.Draw()
box2.Draw()
box3.Draw()

#sep1 = ROOT.TLine(-9.5, 0.146, 9.5, 0.146)
#sep2 = ROOT.TLine(-9.5, -0.185, 9.5, -0.185)
#sep1.Draw()
#sep2.Draw()

l1 = ROOT.TLine()
l1.SetLineColor(ROOT.kRed+1)
l1.SetLineWidth(3)
l1.DrawLineNDC(0.09,0.86,0.09,0.88)
l1.DrawLineNDC(0.14,0.86,0.14,0.88)

l2 = ROOT.TLine()
l2.SetLineColor(ROOT.kBlack)
l2.SetLineWidth(3)
l2.DrawLineNDC(0.355,0.86,0.355,0.88)
l2.DrawLineNDC(0.405,0.86,0.405,0.88)


## finish it off

latex1 = ROOT.TLatex()
latex1.SetNDC()
latex1.SetTextSize(0.037)
latex1.SetTextAlign(11)

latex2 = ROOT.TLatex()
latex2.SetNDC()
latex2.SetTextSize(0.055)
latex2.SetTextAlign(11)

#if args.preliminary:
#latex1.DrawLatex(0.03,0.94,'CMS #bf{#it{Preliminary}}')
latex2.DrawLatex(0.03,0.94,'CMS')
latex1.DrawLatex(0.76,0.94, "137 fb^{-1} (13 TeV)")
#else:
#    latex1.DrawLatex(0.03,0.94,'CMS')

plotDir = plot_directory + "summaryJHEP/"

if not os.path.isdir(plotDir):
    os.makedirs(plotDir)

if args.testGrayscale:
    postFix += '_gray'

for e in [".png",".pdf",".root"]:
    cans.Print(plotDir+"summaryResult_full_rSR"+e)

