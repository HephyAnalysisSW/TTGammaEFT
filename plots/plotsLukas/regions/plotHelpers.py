# helpers functions for fit plots

import ROOT

def convPTLabel( lab ):
    # PhotonGood0_pt20To120_m370To140
    # PhotonNoChgIsoNoSieie0_pt20To120_(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)0To1
    rang = lab.split("_pt")[1].split("_")[0].split("To")
    if len(rang) > 1:
        low, high = rang[0], rang[1]
        return "%s #leq p_{T}(#gamma) < %s GeV"%(low, high)
    else:
        low = rang[0]
        return "p_{T}(#gamma) #geq %s GeV"%(low)

def convM3Label( lab ):
    # PhotonGood0_pt20To120_m370To140
    rang = lab.split("m3")[1].split("To")
    if len(rang) > 1:
        low, high = rang[0], rang[1]
        return "%s #leq M_{3} < %s GeV"%(low, high)
    else:
        low = rang[0]
        return "M_{3} #geq %s GeV"%(low)

def convChgIsoLabel( lab ):
    # PhotonNoChgIsoNoSieie0_pt20To120_(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)0To1
    rang = lab.split("(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)")[1].split("To")
    if len(rang) > 1:
        low, high = rang[0], rang[1]
        return "%s #leq chg.Iso(#gamma) < %s GeV"%(low, high)
    else:
        low = rang[0]
        return "chg.Iso(#gamma) #geq %s GeV"%(low)

def convNPhotonLabel( lab ):
    rang = lab.split("nPhotonGood")[1].split("To")
    if len(rang) > 1 and not (rang[0]=="0" and rang[1]=="1"):
        low, high = rang[0], rang[1]
        return "%s #leq N_{#gamma} < %s"%(low, high)
    else:
        low = rang[0]
        return "N_{#gamma} = %s"%(low)

def convLabel( lab ):
    # summary function for all separate label formating functions
    if "nPhotonGood" in lab:
        return convNPhotonLabel( lab )
    elif "pt" in lab:
        label = convPTLabel( lab )
        if "m3" in lab:
            label += ", " + convM3Label( lab )
        if "pfRelIso" in lab:
            label += ", " + convChgIsoLabel( lab )
        return label
    elif "m3" in lab:
        label = convM3Label( lab )
        if "pfRelIso" in lab:
            label += ", " + convChgIsoLabel( lab )
        return label
    else:
        return ""

def drawDivisions( labels, misIDPOI=False ):
    nBins = len(labels)
    min = 0.15
    max = 0.95
    diff = (max-min) / nBins
    line = ROOT.TLine()
    line.SetLineWidth(2)
    line.SetLineStyle(9)
    line2 = ROOT.TLine()
    line2.SetLineWidth(3)
    line2.SetLineStyle(1)
    lines  = []
    lines2 = []
    done = False
    for i_reg, reg in enumerate(labels):
        if i_reg != nBins-1 and ("SR" in labels[i_reg+1] or ("mis" in labels[i_reg+1] and misIDPOI)) and not done:
            if not any( [(("SR" in lab) or ("mis" in lab and misIDPOI)) for lab in labels] ) or all( ["SR" in lab for lab in labels] ): continue
            lines2.append( (min+(i_reg+1)*diff,  0., min+(i_reg+1)*diff, formatSettings(nBins)["legylower"]) )
            done = True
        if i_reg != nBins-1 and reg.split(",")[0] != labels[i_reg+1].split(",")[0]:
            lines.append( (min+(i_reg+1)*diff,  0., min+(i_reg+1)*diff, formatSettings(nBins)["legylower"]) )
    return [line.DrawLineNDC(*l) for l in lines] + [line2.DrawLineNDC(*l) for l in lines2]

def drawPTDivisions( labels, ptLabels ):
    nBins = len(labels)
    min = 0.15
    max = 0.95
    diff = (max-min) / nBins
    lines = []
    lines2 = []
    line = ROOT.TLine()
    line.SetLineWidth(1)
    line.SetLineStyle(5)
    lines = []
    for i_pt, pt in enumerate(ptLabels):
        if i_pt != nBins-1 and pt != ptLabels[i_pt+1] and labels[i_pt].split(",")[0] == labels[i_pt+1].split(",")[0]:
            lines.append( (min+(i_pt+1)*diff,  0., min+(i_pt+1)*diff, formatSettings(nBins)["legylower"]) )
    return [line.DrawLineNDC(*l) for l in lines]

def drawObjects( nBins, isData, lumi_scale, postFit, cardfile, preliminary ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    addon = "post-fit" if postFit else "pre-fit"
    if "incl" in cardfile: addon += ", inclusive"
    lines = [
      (0.15, 0.945, "CMS Simulation (%s)"%addon) if not isData else ( (0.15, 0.945, "CMS (%s)"%addon) if not preliminary else (0.15, 0.945, "CMS #bf{#it{Preliminary}} #bf{(%s)}"%addon)),
      (0.84 if nBins>25 else formatSettings(nBins)["legylower"], 0.945, "#bf{%3.1f fb^{-1} (13 TeV)}"%lumi_scale )
    ]
    return [tex.DrawLatex(*l) for l in lines]


def drawCoObjects( lumi_scale, bkgOnly, postFit, incl, preliminary ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.03)
    tex.SetTextAlign(11) # align right
    addon = "post-fit" if postFit else "pre-fit"
    if incl: addon += ", inclusive"
    lines = [
      ( (0.25, 0.945, "CMS (%s)"%addon) if not preliminary else (0.25, 0.945, "CMS #bf{#it{Preliminary}} #bf{(%s)}"%addon)),
      (0.7, 0.945, "#bf{%3.1f fb^{-1} (13 TeV)}"%lumi_scale )
    ]
    return [tex.DrawLatex(*l) for l in lines]


def setPTBinLabels( labels, names, fac=1. ):
    nBins = len(labels)
    def setBinLabel( hist ):
        tex = ROOT.TLatex()
        tex.SetTextSize(formatSettings(nBins)["ptlabelsize"])
        tex.SetTextAlign(32)
        tex.SetTextAngle(90)
        dEntry = False
        for i in range(hist.GetNbinsX()):
            if dEntry:
                dEntry = False
                continue
            elif i == nBins-1 or labels[i] != labels[i+1] or names[i] != names[i+1]:
                x = 0.5 + hist.GetXaxis().GetBinUpEdge(i)
                dEntry = False
            else:
                x = 0.5 + (hist.GetXaxis().GetBinUpEdge(i)+hist.GetXaxis().GetBinUpEdge(i+1))*0.5
                dEntry = True

            tex.DrawLatex( x, fac, labels[i] )
    return setBinLabel


def getUncertaintyBoxes( totalHist ):
    nBins = totalHist.GetNbinsX()
    boxes = []
    ratio_boxes = []
    r_max = 999
    r_min = 0
    for ib in range(1, 1 + nBins ):
        val = totalHist.GetBinContent(ib)
        if val<0: continue
        syst = totalHist.GetBinError(ib)
        if val > 0:
            sys_rel = syst/val
        else:
            sys_rel = 1.

        # uncertainty box in main histogram
        box = ROOT.TBox( totalHist.GetXaxis().GetBinLowEdge(ib),  max([0.006, val-syst]), totalHist.GetXaxis().GetBinUpEdge(ib), max([0.006, val+syst]) )
        box.SetLineColor(ROOT.kGray+3)
        box.SetFillStyle(formatSettings(nBins)["hashcode"])
        box.SetFillColor(ROOT.kGray+3)

        # uncertainty box in ratio histogram
        r_min = max( [ 1-sys_rel, r_min ])
        r_max = min( [ 1+sys_rel, r_max ])
        r_box = ROOT.TBox( totalHist.GetXaxis().GetBinLowEdge(ib),  max(0.11, 1-sys_rel), totalHist.GetXaxis().GetBinUpEdge(ib), min(1.9, 1+sys_rel) )
        r_box.SetLineColor(ROOT.kGray+3)
        r_box.SetFillStyle(formatSettings(nBins)["hashcode"])
        r_box.SetFillColor(ROOT.kGray+3)

        boxes.append( box )
        totalHist.SetBinError(ib, 0)
        ratio_boxes.append( r_box )

        #pt text in main histogram
        box = ROOT.TBox( totalHist.GetXaxis().GetBinLowEdge(ib),  max([0.006, val-syst]), totalHist.GetXaxis().GetBinUpEdge(ib), max([0.006, val+syst]) )
        box.SetLineColor(ROOT.kGray+3)
        box.SetFillStyle(formatSettings(nBins)["hashcode"])
        box.SetFillColor(ROOT.kGray+3)

    return boxes, ratio_boxes

def formatSettings( nBins ):
    settings = {}
    if nBins>45:
        settings["textsize"] = 40
        settings["xlabelsize"] = 20
        settings["ylabelsize"] = 30
        settings["padwidth"] = 3000
        settings["padheight"] = 1200
        settings["padratio"] = 350
        settings["hashcode"] = 3144
        settings["legcolumns"] = 6
        settings["legylower"] = 0.83
        settings["textoffset"] = 0.8
        settings["offsetfactor"] = 8
        settings["ptlabelsize"] = 0.015
        settings["heightFactor"] = 100
    elif nBins>25:
        settings["textsize"] = 40
        settings["xlabelsize"] = 20
        settings["ylabelsize"] = 30
        settings["padwidth"] = 2500
        settings["padheight"] = 1200
        settings["padratio"] = 350
        settings["hashcode"] = 3144
        settings["legcolumns"] = 6
        settings["legylower"] = 0.8
        settings["textoffset"] = 1
        settings["offsetfactor"] = 40
        settings["ptlabelsize"] = 0.022
        settings["heightFactor"] = 1000
    else:
        settings["textsize"] = 20
        settings["xlabelsize"] = 16
        settings["ylabelsize"] = 20
        settings["padwidth"] = 1000
        settings["padheight"] = 700
        settings["padratio"] = 250
        settings["hashcode"] = 3344
        settings["legcolumns"] = 5
        settings["legylower"] = 0.77
        settings["textoffset"] = 1.5
        settings["offsetfactor"] = 42
        settings["ptlabelsize"] = 0.022
        settings["heightFactor"] = 1000

    return settings