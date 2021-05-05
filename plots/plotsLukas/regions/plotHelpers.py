# helpers functions for fit plots

import ROOT

def convPTLabel( lab ):
    # PhotonGood0_pt20To120_m370To140
    # PhotonNoChgIsoNoSieie0_pt20To120_(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)0To1
    rang = lab.split("_pt")[1].split("_")[0].split("To")
    if len(rang) > 1:
        low, high = rang[0], rang[1]
        if low != "0":
            return "%s #leq p_{T}(#gamma) < %s GeV"%(low, high)
        else:
            return "p_{T}(#gamma) < %s GeV"%(high)
    else:
        low = rang[0]
        return "p_{T}(#gamma) #geq %s GeV"%(low)

def convEtaLabel( lab ):
    # PhotonGood0_eta-1.5To1.5_m370To140
    # PhotonNoChgIsoNoSieie0_pt20To120_(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)0To1
    rang = lab.split("_eta")[1].split("_")[0].split("To")
    if len(rang) > 1:
        low, high = rang[0], rang[1]
        if low.startswith(")"):
            l = "|#eta(#gamma)|"
            low = low.replace(")","")
        else:
            l = "#eta(#gamma)"
        return "%.2f #leq %s < %.2f"%(float(low), l, float(high))
    else:
        low = rang[0]
        if low.startswith(")"):
            l = "|#eta(#gamma)|"
            low = low.replace(")","")
        else:
            l = "#eta(#gamma)"
        return "%s #geq %.2f"%(l, float(low))

def convM3Label( lab ):
    # PhotonGood0_pt20To120_m370To140
    rang = lab.split("m3")[1].split("To")
    if len(rang) > 1:
        low, high = rang[0], rang[1]
        if low != "0":
            return "%s #leq M_{3} < %s GeV"%(low, high)
        else:
            return "M_{3} < %s GeV"%(high)
    else:
        low = rang[0]
        return "M_{3} #geq %s GeV"%(low)

def convMlgLabel( lab ):
    # mLtight0Gamma0To101.1876_PhotonGood0_pt120To220
    # mLtight0Gamma101.1876_PhotonGood0_pt120To220
    rang = lab.split("_")[0].split("mLtight0Gamma")[1].split("To")
    if len(rang) > 1:
        low, high = rang[0], rang[1]
        if low != "0":
            return "%s #leq M_{l,#gamma} < %s GeV"%(low, high)
        else:
            return "M_{l,#gamma} < %s GeV"%(high)
    else:
        low = rang[0]
        return "M_{l,#gamma} #geq %s GeV"%(low)

def convDRLabel( lab ):
    rang = lab.split("_")[0].split("ltight0GammaNoSieieNoChgIsodR")[1].split("To")
    if len(rang) > 1:
        low, high = rang[0], rang[1]
        if low != "0":
            return "%.2f #leq #Delta R(l,#gamma) < %.2f"%(float(low), float(high))
        else:
            return "#Delta R(l,#gamma) < %.2f"%float(high)
    else:
        low = rang[0]
        return "#Delta R(l,#gamma) #geq %.2f"%float(low)

def convDRpLabel( lab ):
    rang = lab.split("_")[0].split("ltight0GammadR")[1].split("To")
    if len(rang) > 1:
        low, high = rang[0], rang[1]
        if low != "0":
            return "%.2f #leq #Delta R(l,#gamma) < %.2f"%(float(low), float(high))
        else:
            return "#Delta R(l,#gamma) < %.2f"%float(high)
    else:
        low = rang[0]
        return "#Delta R(l,#gamma) #geq %.2f"%float(low)

def convDPhiLabel( lab ):
    rang = lab.split("_")[0].split("ltight0GammaNoSieieNoChgIsodPhi")[1].split("To")
    if len(rang) > 1:
        low, high = rang[0], rang[1]
        if low != "0":
            return "%.2f #leq #Delta #phi(l,#gamma) < %.2f"%(float(low), float(high))
        else:
            return "#Delta #phi(l,#gamma) < %.2f"%float(high)
    else:
        low = rang[0]
        return "#Delta #phi(l,#gamma) #geq %.2f"%float(low)

def convChgIsoLabel( lab ):
    # PhotonNoChgIsoNoSieie0_pt20To120_(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)0To1
    rang = lab.split("(PhotonNoChgIsoNoSieie0_pfRelIso03_chg*PhotonNoChgIsoNoSieie0_pt)")[1].split("To")
    if len(rang) > 1:
        low, high = rang[0], rang[1]
        if low != "0":
            return "%s #leq chg.Iso(#gamma) < %s GeV"%(low, high)
        else:
            return "chg.Iso(#gamma) < %s GeV"%(high)
    else:
        low = rang[0]
        return "chg.Iso(#gamma) #geq %s GeV"%(low)

def convNPhotonLabel( lab ):
    rang = lab.split("nPhotonGood")[1].split("To")
    if len(rang) > 1 and not (rang[0]=="0" and rang[1]=="1"):
        low, high = rang[0], rang[1]
        if low != "0":
            return "%s #leq N_{#gamma} < %s"%(low, high)
        else:
            return "N_{#gamma} < %s"%(high)
    else:
        low = rang[0]
        return "N_{#gamma} = %s"%(low)

def convLabel( lab ):
    # summary function for all separate label formating functions
    if "nPhotonGood" in lab:
        return convNPhotonLabel( lab )
    elif "ltight0GammaNoSieieNoChgIsodR" in lab:
        return convDRLabel( lab )
    elif "ltight0GammadR" in lab:
        return convDRpLabel( lab )
    elif "ltight0GammaNoSieieNoChgIsodPhi" in lab:
        return convDPhiLabel( lab )
    elif "eta" in lab:
        label = convEtaLabel( lab )
        if "m3" in lab:
            label += ", " + convM3Label( lab )
        if "pfRelIso" in lab:
            label += ", " + convChgIsoLabel( lab )
#        if "mLtight0Gamma" in lab:
#            label += ", " + convMlgLabel( lab )
        return label
    elif "pt" in lab:
        label = convPTLabel( lab )
        if "m3" in lab:
            label += ", " + convM3Label( lab )
        if "pfRelIso" in lab:
            label += ", " + convChgIsoLabel( lab )
#        if "mLtight0Gamma" in lab:
#            label += ", " + convMlgLabel( lab )
        return label
    elif "m3" in lab:
        label = convM3Label( lab )
        if "pfRelIso" in lab:
            label += ", " + convChgIsoLabel( lab )
        return label
    elif "mLtight0Gamma" in lab:
        label = convMlgLabel( lab )
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
        if i_reg != nBins-1 and ("SR" in labels[i_reg+1] or ("mis" in labels[i_reg+1] and misIDPOI)) and not ("SR" in labels[i_reg] or ("mis" in labels[i_reg] and misIDPOI)) and not done:
            if not any( [(("SR" in lab) or ("mis" in lab and misIDPOI)) for lab in labels] ) or all( ["SR" in lab for lab in labels] ): continue
            lines2.append( (min+(i_reg+1)*diff,  0., min+(i_reg+1)*diff, formatSettings(nBins)["divupper"]) )
            done = True
        if i_reg != nBins-1 and reg.split(",")[0].replace("WG","VG").replace("ZG","VG").replace("ZG+WG","VG") != labels[i_reg+1].split(",")[0].replace("WG","VG").replace("ZG","VG").replace("ZG+WG","VG"):
            lines.append( (min+(i_reg+1)*diff,  0., min+(i_reg+1)*diff, formatSettings(nBins)["divupper"]) )
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
        if i_pt != nBins-1 and pt != ptLabels[i_pt+1] and labels[i_pt].split(",")[0].replace("WG","VG").replace("ZG","VG").replace("ZG+WG","VG") == labels[i_pt+1].split(",")[0].replace("WG","VG").replace("ZG","VG").replace("ZG+WG","VG"):
            lines.append( (min+(i_pt+1)*diff,  0., min+(i_pt+1)*diff, formatSettings(nBins)["divupper"]) )
    return [line.DrawLineNDC(*l) for l in lines]

def drawObjectsDiff( lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right

    tex2 = ROOT.TLatex()
    tex2.SetNDC()
    tex2.SetTextSize(0.05)
    tex2.SetTextAlign(11) # align right

    if isinstance(lumi_scale, int):
        line = (0.70, 0.95, '%i fb^{-1} (13 TeV)' % lumi_scale)
    else:
        line = (0.68, 0.95, '%3.1f fb^{-1} (13 TeV)' % lumi_scale)
    line2 = (0.15, 0.95, 'CMS')
    return [tex2.DrawLatex(*line2), tex.DrawLatex(*line)]

def drawObjects( nBins, isData, lumi_scale, postFit, cardfile, preliminary ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right

    tex2 = ROOT.TLatex()
    tex2.SetNDC()
    tex2.SetTextSize(0.06)
    tex2.SetTextAlign(11) # align right

    addon = "post-fit" if postFit else "pre-fit"
    line2 = (0.15, 0.945, "CMS") if not preliminary else (0.15, 0.945, "CMS #bf{#it{Preliminary}}")

    if isinstance(lumi_scale, int):
        line = (formatSettings(nBins)["laboff"]+0.01, 0.945, "%i fb^{-1} (13 TeV)"%lumi_scale )
    else:
        line = (formatSettings(nBins)["laboff"], 0.945, "%3.1f fb^{-1} (13 TeV)"%lumi_scale )
    return [tex2.DrawLatex(*line2), tex.DrawLatex(*line)]


def drawCoObjects( lumi_scale, bkgOnly, postFit, incl, preliminary ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.03)
    tex.SetTextAlign(11) # align right
    addon = "post-fit" if postFit else "pre-fit"
    if incl: addon += ", inclusive"
    lines = [
#      ( (0.25, 0.945, "CMS (%s)"%addon) if not preliminary else (0.25, 0.945, "CMS #bf{#it{Preliminary}} #bf{(%s)}"%addon)),
      ( (0.25, 0.945, "CMS") if not preliminary else (0.25, 0.945, "CMS #bf{#it{Preliminary}}")),
#      (0.7, 0.945, "#bf{%3.1f fb^{-1} (13 TeV)}"%lumi_scale )
      (0.7, 0.945, "%i fb^{-1} (13 TeV)"%lumi_scale )
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

def getUncertaintyBoxes( totalHist, minMax=0.3, lineColor=ROOT.kGray+3, fillColor=ROOT.kGray+3, hashcode=3144 ):
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
        box.SetLineColor(lineColor)
        if hashcode: box.SetFillStyle(hashcode)
        box.SetFillColor(fillColor)

        # uncertainty box in ratio histogram
        r_min = max( [ 1-sys_rel, r_min ])
        r_max = min( [ 1+sys_rel, r_max ])
        r_box = ROOT.TBox( totalHist.GetXaxis().GetBinLowEdge(ib),  max(1-minMax, 1-sys_rel), totalHist.GetXaxis().GetBinUpEdge(ib), min(1+minMax, 1+sys_rel) )
        r_box.SetLineColor(lineColor)
        if hashcode: r_box.SetFillStyle(hashcode)
        r_box.SetFillColor(fillColor)

        boxes.append( box )
        totalHist.SetBinError(ib, 0)
        ratio_boxes.append( r_box )

        #pt text in main histogram
        box = ROOT.TBox( totalHist.GetXaxis().GetBinLowEdge(ib),  max([0.006, val-syst]), totalHist.GetXaxis().GetBinUpEdge(ib), max([0.006, val+syst]) )
        box.SetLineColor(lineColor)
        if hashcode: box.SetFillStyle(hashcode)
        box.SetFillColor(fillColor)

    return boxes, ratio_boxes

def getErrorBoxes( totalHist, minMax=0.3, lineColor=ROOT.kGray+3, fillColor=ROOT.kGray+3, hashcode=3144, ratioCenter=None ):
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

        rCenter = 1.
        if ratioCenter:
            rCenter = ratioCenter.GetBinContent(ib)

        width = (totalHist.GetXaxis().GetBinUpEdge(ib) - totalHist.GetXaxis().GetBinLowEdge(ib))*0.5 #0.015*nBins #0.007*nBins
        # uncertainty box in main histogram
        box = ROOT.TBox( totalHist.GetXaxis().GetBinCenter(ib)-width,  max([0.006, val-syst]), totalHist.GetXaxis().GetBinCenter(ib)+width, max([0.006, val+syst]) )
        box.SetLineColor(lineColor)
        if hashcode: box.SetFillStyle(hashcode)
        box.SetFillColor(fillColor)

        # uncertainty box in ratio histogram
        r_min = max( [ rCenter-sys_rel, r_min ])
        r_max = min( [ rCenter+sys_rel, r_max ])
        r_box = ROOT.TBox( totalHist.GetXaxis().GetBinCenter(ib)-width,  max(1-minMax, rCenter-sys_rel), totalHist.GetXaxis().GetBinCenter(ib)+width, min(1+minMax, rCenter+sys_rel) )
        r_box.SetLineColor(lineColor)
        if hashcode: r_box.SetFillStyle(hashcode)
        r_box.SetFillColor(fillColor)

        boxes.append( box )
        totalHist.SetBinError(ib, 0)
        ratio_boxes.append( r_box )

        #pt text in main histogram
        box = ROOT.TBox( totalHist.GetXaxis().GetBinCenter(ib)-width,  max([0.006, val-syst]), totalHist.GetXaxis().GetBinCenter(ib)+width, max([0.006, val+syst]) )
        box.SetLineColor(lineColor)
        if hashcode: box.SetFillStyle(hashcode)
        box.SetFillColor(fillColor)

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
        settings["divupper"] = 0.77
        settings["laboff"] = 0.83
        settings["textoffset"] = 0.8
        settings["offsetfactor"] = 20
        settings["ptlabelsize"] = 0.015
        settings["heightFactor"] = 100
        settings["ticksize"] = 0.005
    elif nBins>31:
        settings["textsize"] = 36
        settings["xlabelsize"] = 27
        settings["ylabelsize"] = 34
        settings["padwidth"] = 2200
        settings["padheight"] = 1000
        settings["padratio"] = 300
        settings["hashcode"] = 3244
        settings["legcolumns"] = 5
        settings["legylower"] = 0.8
        settings["divupper"] = 0.79
        settings["laboff"] = 0.815
        settings["textoffset"] = 1
#        settings["offsetfactor"] = 20 # bkg only
        settings["offsetfactor"] = 70 # SR
        settings["ptlabelsize"] = 0.028
#        settings["heightFactor"] = 300 #bkg only
        settings["heightFactor"] = 600 #SR
        settings["ticksize"] = 0.008
    elif nBins>25:
        settings["textsize"] = 32
        settings["xlabelsize"] = 26
        settings["ylabelsize"] = 30
        settings["padwidth"] = 1500
        settings["padheight"] = 1000
        settings["padratio"] = 300
        settings["hashcode"] = 3244
        settings["legcolumns"] = 5
        settings["legylower"] = 0.8
        settings["divupper"] = 0.77
        settings["laboff"] = 0.75
        settings["textoffset"] = 1.5
#        settings["offsetfactor"] = 20 # bkg only
        settings["offsetfactor"] = 90 # SR
        settings["ptlabelsize"] = 0.03
#        settings["heightFactor"] = 300 #bkg only
        settings["heightFactor"] = 1500 #SR
        settings["ticksize"] = 0.02
    else:
        settings["textsize"] = 28
        settings["xlabelsize"] = 24
        settings["ylabelsize"] = 26
        settings["padwidth"] = 1000
        settings["padheight"] = 700
        settings["padratio"] = 250
        settings["hashcode"] = 3344
        settings["legcolumns"] = 5
        settings["legylower"] = 0.8
        settings["divupper"] = 0.77
        settings["laboff"] = 0.75
        settings["textoffset"] = 1.5
        settings["offsetfactor"] = 11 #52
        settings["ptlabelsize"] = 0.03 #0.022
        settings["heightFactor"] = 70
        settings["ticksize"] = 0.016
    return settings
