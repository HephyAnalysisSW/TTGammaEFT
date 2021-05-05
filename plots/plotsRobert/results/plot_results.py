import ROOT
import os
import ctypes
import copy
import shutil
from functools                      import partial
from array                          import array
import Analysis.Tools.syncer        
from RootTools.core.standard        import *
from math import sqrt
from TTGammaEFT.Tools.user          import  plot_directory


# Plot style
ROOT.gROOT.LoadMacro('$CMSSW_BASE/src/Analysis/Tools/scripts/tdrstyle.C')
ROOT.setTDRStyle()

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--testGrayscale",   action='store_true',            help="Because of  reasons...")
argParser.add_argument("--preliminary",     action='store_true',            help="Because of  reasons...")
args = argParser.parse_args()

## define all the results. EFT
results_EFT = [\
    {   'name': 'ctZ',
        'tex': 'C_{tZ} /#Lambda^{2}',
        'limits': { 'new':[(-0.42, 0.38)], 'TOP-18-009': [(-1.1, 1.1)], 'TOP-17-005': [(-2.6,2.6)], 'TOP-19-001':[(-2.14, 2.19)], 'ATLAS': [(-2.4, 2.4)], 'Sanz': [(-4.5*sqrt(0.2229), 1.2*sqrt(0.2229))], 'direct': [(-2.2, 3.3)], 'maltoni':[(-7.2, 7.7)]}
    },
    {   'name': 'ctZI',
        'tex': 'C_{tZ}^{I} /#Lambda^{2}',
        'limits': {'new':[(-0.42, 0.42)], 'TOP-18-009': [(-1.2, 1.2)], 'TOP-17-005': [], 'TOP-19-001':[], 'ATLAS': [], 'Sanz': [], 'direct': [], 'maltoni':[]} #nothing else?!
    },
]

ordering_EFT = ['new', 'TOP-18-009', 'TOP-17-005', 'TOP-19-001', 'ATLAS', 'Sanz']

res = results_EFT
ordering = ordering_EFT
#leg.AddEntry(res[0]['lines'][0],  "t#overline{t}#gamma #bf{CMS 137 fb^{-1} (95% CL)}", 'l')
#leg.AddEntry(res[0]['lines'][3],  "#bf{CMS 35.9 fb^{-1} (95% CL)}", 'l')
#leg.AddEntry(res[0]['lines'][6],  "#bf{ATLAS 36.1 fb^{-1} (95% CL)}", 'l')
#leg.AddEntry(res[0]['lines'][9],  "#bf{SMEFiT (95% CL)}", 'l')
#leg.AddEntry(res[0]['lines'][12], "#bf{TopFitter (95% CL)}", 'l')
#leg.AddEntry(res[0]['lines'][15], "#bf{Indirect (68% CL)}", 'l')

styles = {
    'new':        {'color': ROOT.kBlack,   'style':1, 'width':4, 'legendText':' CMS 137 fb^{-1} t#bar{t}#gamma'},
    'TOP-18-009': {'color': ROOT.kRed+1,   'style':1, 'width':3, 'legendText':'#splitline{ CMS 77.5 fb^{-1} t#bar{t}Z}{ JHEP 03 (2020) 056}'},
    'TOP-17-005': {'color': ROOT.kBlue-6,  'style':1, 'width':3, 'legendText':'#splitline{ CMS 36 fb^{-1} t#bar{t}Z}{ JHEP 08 (2018) 011}'},
    'TOP-19-001': {'color': ROOT.kOrange-2,'style':1, 'width':3, 'legendText':'#splitline{ CMS 41.5 fb^{-1} t#bar{t}+leptons}{ JHEP 03 (2021) 095}'},
    'ATLAS':      {'color': ROOT.kSpring+6,'style':1, 'width':3, 'legendText':'#splitline{ ATLAS 36 fb^{-1} t#bar{t}Z}{ Phys. Rev. D 99, 072009}'},
    'Sanz':       {'color': ROOT.kBlack,   'style':2, 'width':2, 'legendText':'#splitline{ global fit}{ JHEP 04 (2021) 279}'}
    }

cans = ROOT.TCanvas("cans","",10,10,700,700)
cans.Range(-10,-1,10,1)

if args.testGrayscale:
    cans.SetGrayscale()

lower = -12
upper =  6

axis = ROOT.TGaxis(-9.5,-0.85,9.5,-0.85,lower,upper,505,"")
axisUpper = ROOT.TGaxis(-9.5,0.85,9.5,0.85,lower,upper,505,"-")
axisUpper.SetLabelOffset(10)
axis.SetName("axis")
axis.SetLabelSize(0.05)
axis.Draw()
axisUpper.Draw()

zero_point = 3.15#3.5 
zero = ROOT.TLine(zero_point,-0.85,zero_point,0.85)
zero.SetLineStyle(1)

box1 = ROOT.TLine(-9.5, -0.85, -9.5, 0.85)
box2 = ROOT.TLine(9.5, -0.85, 9.5, 0.85)
box3 = ROOT.TLine(-9.5, 0.85, 9.5, 0.85)

pads = []

leg = ROOT.TLegend(0.05,0.87-0.057*(len(ordering)*2+1),0.40,0.87)
leg.SetFillColor(ROOT.kWhite)
leg.SetShadowColor(ROOT.kWhite)
leg.SetBorderSize(0)
leg.SetTextSize(0.035)

### Get all the pads ###
for p in range(len(res)):
    y_lo = 0.9-0.8*((p+1.)/len(res))
    y_hi = 0.9-0.8*(float(p)/len(res))

    pads.append(ROOT.TPad("pad_%s"%p,"pad_%s"%p, 0.5/20, y_lo, 19.5/20, y_hi ))
    pads[-1].Range(lower,0,upper,5)
    pads[-1].SetFillColor(0)
    pads[-1].Draw()
    pads[-1].cd()
    
    # put the stuff
    graphs  = []
    res[p]['lines'] = []
    for i, o in enumerate(ordering):
        limits = res[p]['limits'][o]
        x = []
        y = []
        y_err = []
        x_plus = []
        x_minus = []
        for j,l in enumerate(limits):
            start = 3.5 
            newLines = []
            newLines += [   ROOT.TLine(l[0], start-0.5*i,       l[1], start-0.5*i),
                            ROOT.TLine(l[0], start-0.5*i+0.15,  l[0], start-0.5*i-0.15),
                            ROOT.TLine(l[1], start-0.5*i+0.15,  l[1], start-0.5*i-0.15)    
                        ]
            for k,line in enumerate(newLines):
                line.SetLineColor(styles[o]['color'])
                line.SetLineWidth(styles[o]['width'])
                if k == 0:
                    line.SetLineStyle(styles[o]['style'])
            
            res[p]['lines'] += copy.deepcopy(newLines)
        if p==0:
            leg.AddEntry(res[0]['lines'][i*3],  styles[o]['legendText'], 'l')
    
    for l in res[p]['lines']:
        l.Draw()
    cans.cd()

cans.cd()

zero.Draw()
box1.Draw()
box2.Draw()
box3.Draw()

leg.AddEntry(zero, ' SM', 'l')

leg.Draw()

## finish it off

latex1 = ROOT.TLatex()
latex1.SetNDC()
latex1.SetTextSize(0.06)
latex1.SetTextAlign(11)

if args.preliminary:
    latex1.DrawLatex(0.03,0.94,'CMS #bf{#it{Preliminary}}')
else:
    latex1.DrawLatex(0.03,0.94,'CMS')

latex2 = ROOT.TLatex()
latex2.SetNDC()
latex2.SetTextSize(0.045)
latex2.SetTextAlign(11)
for i,r in enumerate(res):
    latex2.DrawLatex(0.83, 0.665-0.62*(i/2.), '#bf{%s}'%r['tex'])

plotDir = plot_directory + "summary/"

if not os.path.isdir(plotDir):
    os.makedirs(plotDir)

if args.preliminary: 
    postFix  = 'preliminary'
else:
    postFix = ""

if args.testGrayscale:
    postFix += '_gray'

for e in [".png",".pdf",".root"]:
    cans.Print(plotDir+"summaryResult"+postFix+e)

