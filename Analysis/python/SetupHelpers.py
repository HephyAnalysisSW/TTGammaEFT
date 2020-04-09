import os, copy

from Analysis.Tools.u_float      import u_float

from TTGammaEFT.Tools.user       import results_directory, cache_directory
from TTGammaEFT.Analysis.regions import *
from TTGammaEFT.Samples.color    import color

lepChannels   = ["e", "mu"]
dilepChannels = ["eetight", "mumutight"]
allChannels   = ["all", "e", "mu", "eetight", "mumutight", "SFtight"]

# processes
signal      = ["TTG_gen","TTG_misID"]
DY_misID    = ["DY_LO_misID"]
DY          = ["DY_LO_gen","DY_LO_had"]
TT_misID    = ["TT_pow_misID"]
TT          = ["TT_pow_gen","TT_pow_had","TTG_had"]
WG          = ["WG_gen","WG_had"]
ZG          = ["ZG_gen","ZG_had"]
VG          = ["WG_gen","WG_had","ZG_gen","ZG_had"]
other_misID = ["WJets_misID","other_misID","WG_misID","ZG_misID"]
other       = ["other_gen","other_had"]
WJets       = ["WJets_gen","WJets_had"]
QCD         = ["QCD-DD"]
PU          = ["TTG_magic","DY_LO_magic","TT_pow_magic","WG_magic","ZG_magic","WJets_magic","other_magic"]

default_sampleList            = ["TTG","TT_pow","DY_LO","ZG","WG","WJets","other","QCD-DD"]
default_systematicList        = ["TTG_TuneUp","TTG_TuneDown","TTG_erdOn"]
default_photonSampleList      = signal + DY_misID + DY + TT_misID + TT + WG + ZG + other_misID + other + WJets + QCD + PU

processes = {
             "signal":      { "process":signal,      "color":color.TTG,          "texName":"tt#gamma (gen, misID)" },
             "DY":          { "process":DY,          "color":color.DY,           "texName":"DY (gen, had)"         },
             "DY_misID":    { "process":DY_misID,    "color":color.DY_misID,     "texName":"DY (misID)"            },
             "TT":          { "process":TT,          "color":color.TT,           "texName":"tt+tt#gamma (had)"     },
             "TT_misID":    { "process":TT_misID,    "color":color.TT_misID,     "texName":"tt (misID)"            },
             "WG":          { "process":WG,          "color":color.WGamma,       "texName":"W#gamma (gen, had)"    },
             "ZG":          { "process":ZG,          "color":color.ZGamma,       "texName":"Z#gamma (gen, had)"    },
#             "VG":          { "process":VG,          "color":color.VGamma,       "texName":"V#gamma (gen, had)"    },
             "WJets":       { "process":WJets,       "color":color.WJets,        "texName":"WJets (gen, had)"      },
             "other":       { "process":other,       "color":color.Other,        "texName":"other (gen, had)"      },
             "other_misID": { "process":other_misID, "color":color.Other_misID,  "texName":"WJets+V#gamma+other (misID)" },
             "QCD":         { "process":QCD,         "color":color.QCD,          "texName":"multijets"             },
             "PU":          { "process":PU,          "color":color.PU,           "texName":"PU #gamma (all)"      },
}

processesNoPhoton = {
                     "signal":      { "process":["TTG"],      "color":color.TTG,          "texName":"tt#gamma (gen, misID)" },
                     "DY":          { "process":["DY_LO"],    "color":color.DY,           "texName":"DY (gen, had)"         },
                     "DY_misID":    { "process":[],           "color":color.DY_misID,     "texName":"DY (misID)"            },
                     "TT":          { "process":["TT_pow"],   "color":color.TT,           "texName":"tt+tt#gamma (had)"     },
                     "TT_misID":    { "process":[],           "color":color.TT_misID,     "texName":"tt (misID)"            },
                     "WG":          { "process":["WG"],       "color":color.WGamma,       "texName":"W#gamma (gen, had)"    },
                     "ZG":          { "process":["ZG"],       "color":color.ZGamma,       "texName":"Z#gamma (gen, had)"    },
#                     "VG":          { "process":["WG","ZG"],  "color":color.VGamma,       "texName":"V#gamma (gen, had)"    },
                     "WJets":       { "process":["WJets"],    "color":color.WJets,        "texName":"WJets (gen, had)"      },
                     "other":       { "process":["other"],    "color":color.Other,        "texName":"other (gen, had)"      },
                     "other_misID": { "process":[],           "color":color.Other_misID,  "texName":"WJets+V#gamma+other (misID)" },
                     "QCD":         { "process":QCD,          "color":color.QCD,          "texName":"multijets"             },
                     "PU":          { "process":[],           "color":color.PU,           "texName":"PU #gamma (all)"      },
}

default_processes = {
             "signal":      { "process":["TTG"]+signal,  "color":color.TTG,          "texName":"tt#gamma (gen, misID)" },
             "DY":          { "process":["DY_LO"]+DY,    "color":color.DY,           "texName":"DY  (gen, had)"        },
             "DY_misID":    { "process":DY_misID,        "color":color.DY_misID,     "texName":"DY (misID)"            },
             "TT":          { "process":["TT_pow"]+TT,   "color":color.TT,           "texName":"tt+tt#gamma (had)"     },
             "TT_misID":    { "process":TT_misID,        "color":color.TT_misID,     "texName":"tt (misID)"            },
             "WG":          { "process":["WG"]+WG,       "color":color.WGamma,       "texName":"W#gamma (gen, had)"    },
             "ZG":          { "process":["ZG"]+ZG,       "color":color.ZGamma,       "texName":"Z#gamma (gen, had)"    },
#             "VG":          { "process":["WG","ZG"]+VG,  "color":color.VGamma,       "texName":"V#gamma (gen, had)"    },
             "WJets":       { "process":["WJets"]+WJets, "color":color.WJets,        "texName":"WJets (gen, had)"      },
             "other":       { "process":["other"]+other, "color":color.Other,        "texName":"other (gen, had)"      },
             "other_misID": { "process":other_misID,     "color":color.Other_misID,  "texName":"WJets+V#gamma+other (misID)" },
             "QCD":         { "process":QCD,             "color":color.QCD,          "texName":"multijets"             },
             "PU":          { "process":PU,          "color":color.PU,           "texName":"PU #gamma (all)"      },
}

processesMisIDPOI = {
             "signal":      { "process":other_misID+TT_misID+DY_misID, "color":color.DY_misID,     "texName":"misID (tt+DY+V#gamma+other)" },
             "TTG":         { "process":signal,                        "color":color.TTG,          "texName":"tt#gamma (gen, misID)" },
             "DY":          { "process":DY,                            "color":color.DY,           "texName":"DY (gen, had)"         },
             "TT":          { "process":TT,                            "color":color.TT,           "texName":"tt+tt#gamma (had)"     },
             "WG":          { "process":WG,                            "color":color.WGamma,       "texName":"W#gamma (gen, had)"    },
             "ZG":          { "process":ZG,                            "color":color.ZGamma,       "texName":"Z#gamma (gen, had)"    },
#             "VG":          { "process":VG,                            "color":color.VGamma,       "texName":"V#gamma (gen, had)"    },
             "WJets":       { "process":WJets,                         "color":color.WJets,        "texName":"WJets (gen, had)"      },
             "other":       { "process":other,                         "color":color.Other,        "texName":"other (gen, had)"      },
             "QCD":         { "process":QCD,                           "color":color.QCD,          "texName":"multijets"             },
             "PU":          { "process":PU,                            "color":color.PU,           "texName":"PU #gamma (all)"      },
}

processesWJetsPOI = {
             "signal":      { "process":WJets,                         "color":color.WJets,        "texName":"WJets" },
             "TTG":         { "process":signal,                        "color":color.TTG,          "texName":"tt#gamma" },
             "DY":          { "process":DY,                            "color":color.DY,           "texName":"DY"         },
             "TT":          { "process":TT,                            "color":color.TT,           "texName":"tt"     },
             "WG":          { "process":WG,                            "color":color.WGamma,       "texName":"W#gamma"    },
             "ZG":          { "process":ZG,                            "color":color.ZGamma,       "texName":"Z#gamma"    },
             "other":       { "process":other,                         "color":color.Other,        "texName":"other"      },
             "QCD":         { "process":QCD,                           "color":color.QCD,          "texName":"multijets"             },
}

processesTTPOI = {
             "signal":      { "process":TT,                         "color":color.TT,        "texName":"tt" },
             "TTG":         { "process":signal,                        "color":color.TTG,          "texName":"tt#gamma" },
             "DY":          { "process":DY,                            "color":color.DY,           "texName":"DY"         },
             "WJets":       { "process":WJets,                            "color":color.WJets,           "texName":"WJets"     },
             "WG":          { "process":WG,                            "color":color.WGamma,       "texName":"W#gamma"    },
             "ZG":          { "process":ZG,                            "color":color.ZGamma,       "texName":"Z#gamma"    },
             "other":       { "process":other,                         "color":color.Other,        "texName":"other"      },
             "QCD":         { "process":QCD,                           "color":color.QCD,          "texName":"multijets"             },
}

processesDYPOI = {
             "signal":      { "process":DY,                         "color":color.DY,        "texName":"DY" },
             "TTG":         { "process":signal,                        "color":color.TTG,          "texName":"tt#gamma" },
             "TT":          { "process":TT,                            "color":color.TT,           "texName":"tt"         },
             "WJets":       { "process":WJets,                            "color":color.WJets,           "texName":"WJets"     },
             "WG":          { "process":WG,                            "color":color.WGamma,       "texName":"W#gamma"    },
             "ZG":          { "process":ZG,                            "color":color.ZGamma,       "texName":"Z#gamma"    },
             "other":       { "process":other,                         "color":color.Other,        "texName":"other"      },
             "QCD":         { "process":QCD,                           "color":color.QCD,          "texName":"multijets"             },
}


signalRegions = {}
# Signal Regions Settings
# processes.keys() will be the proc visible in the combine card
# processes.values() is a list of processes that will be combined for the entry in combine
signalRegions["SR2"]  = { "parameters": { "zWindow":"all", "nJet":(2,2), "nBTag":(1,-1), "nPhoton":(1,1) },
                          "channels":   lepChannels,
                          "regions":    regionsTTGloose,
                          "inclRegion": inclRegionsTTGloose,
                          "noPhotonCR": False,
                          "processes":  processes,
                          "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood == 2 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                         }

signalRegions["SR3"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1) },
                          "channels":   lepChannels,
                          "regions":    regionsTTGloose,
                          "inclRegion": inclRegionsTTGloose,
                          "noPhotonCR": False,
                          "processes":  processes,
                          "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood == 3 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                         }

signalRegions["SR4p"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1) },
                          "channels":   lepChannels,
                          "regions":    regionsTTGloose,
                          "inclRegion": inclRegionsTTGloose,
                          "noPhotonCR": False,
                          "processes":  processes,
                          "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood >= 4 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                         }

signalRegions["SR3Fine"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1) },
                              "channels":   lepChannels,
                              "regions":    regionsTTGlooseFine,
                              "inclRegion": inclRegionsTTGloose,
                              "noPhotonCR": False,
                              "processes":  processes,
                              "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood == 3 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                             }

signalRegions["SR4pFine"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1) },
                              "channels":   lepChannels,
                              "regions":    regionsTTGlooseFine,
                              "inclRegion": inclRegionsTTGloose,
                              "noPhotonCR": False,
                              "processes":  processes,
                              "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood >= 4 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                             }

signalRegions["SR3Unfold"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1) },
                                "channels":   lepChannels,
                                "regions":    regionsTTGlooseUnfolding,
                                "inclRegion": inclRegionsTTGloose,
                                "noPhotonCR": False,
                                "processes":  processes,
                                "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood == 3 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                               }

signalRegions["SR4pUnfold"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1) },
                                "channels":   lepChannels,
                                "regions":    regionsTTGlooseUnfolding,
                                "inclRegion": inclRegionsTTGloose,
                                "noPhotonCR": False,
                                "processes":  processes,
                                "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood >= 4 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                               }

signalRegions["SR3EtaUnfold"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1) },
                                   "channels":   lepChannels,
                                   "regions":    regionsTTGlooseEtaUnfolding,
                                   "inclRegion": inclRegionsTTGloose,
                                   "noPhotonCR": False,
                                   "processes":  processes,
                                   "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood == 3 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                                  }

signalRegions["SR4pEtaUnfold"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1) },
                                   "channels":   lepChannels,
                                   "regions":    regionsTTGlooseEtaUnfolding,
                                   "inclRegion": inclRegionsTTGloose,
                                   "noPhotonCR": False,
                                   "processes":  processes,
                                   "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood >= 4 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                                  }

signalRegions["SR3M3"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1) },
                            "channels":   lepChannels,
                            "regions":    m3PtlooseRegions,
                            "inclRegion": m3Regions,
                            "noPhotonCR": False,
                            "processes":  processes,
                            "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood == 3 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                         }

signalRegions["SR3pM3"]  = { "parameters": { "zWindow":"all", "nJet":(3,-1), "nBTag":(1,-1), "nPhoton":(1,1) },
                            "channels":   lepChannels,
                            "regions":    m3PtlooseRegions,
                            "inclRegion": m3Regions,
                            "noPhotonCR": False,
                            "processes":  processes,
                            "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood >= 3 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                         }

signalRegions["SR4pM3"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1) },
                            "channels":   lepChannels,
                            "regions":    m3PtlooseRegions,
                            "inclRegion": m3Regions,
                            "noPhotonCR": False,
                            "processes":  processes,
                            "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood >= 4 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                         }

signalRegions["SR3Eta"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1) },
                             "channels":   lepChannels,
                             "regions":    regionsTTGlooseEta,
                             "inclRegion": inclRegionsTTGloose,
                             "noPhotonCR": False,
                             "processes":  processes,
                             "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood == 3 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                            }

signalRegions["SR4pEta"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1) },
                             "channels":   lepChannels,
                             "regions":    regionsTTGlooseEta,
                             "inclRegion": inclRegionsTTGloose,
                             "noPhotonCR": False,
                             "processes":  processes,
                             "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood >= 4 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                            }

signalRegions["SR3EtaFine"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1) },
                                 "channels":   lepChannels,
                                 "regions":    regionsTTGlooseEtaFine,
                                 "inclRegion": inclRegionsTTGloose,
                                 "noPhotonCR": False,
                                 "processes":  processes,
                                 "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood == 3 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                               }

signalRegions["SR4pEtaFine"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1) },
                                 "channels":   lepChannels,
                                 "regions":    regionsTTGlooseEtaFine,
                                 "inclRegion": inclRegionsTTGloose,
                                 "noPhotonCR": False,
                                 "processes":  processes,
                                 "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood >= 4 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                                }

signalRegions["SR3EtaM3"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1) },
                               "channels":   lepChannels,
                               "regions":    m3EtaRegions,
                               "inclRegion": m3Regions,
                               "noPhotonCR": False,
                               "processes":  processes,
                               "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood == 3 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                              }

signalRegions["SR4pEtaM3"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1) },
                               "channels":   lepChannels,
                               "regions":    m3EtaRegions,
                               "inclRegion": m3Regions,
                               "noPhotonCR": False,
                               "processes":  processes,
                               "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood >= 4 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                              }

default_SR = signalRegions["SR4pM3"]

#Define defaults here
default_nJet         = (4,-1)
default_nBTag        = (1,-1)
default_nPhoton      = (1,1)
default_MET          = (0,-1)
default_leptonEta    = (0,-1)
default_leptonPt     = (0,-1)
default_zWindow      = "all"
default_dileptonic   = False
default_invLepIso    = False
default_addMisIDSF   = False
default_photonCat    = "all"
default_m3Window     = "all"
default_photonIso    = None

SSMSF_val = {}
SSMSF_val[2016] = u_float( 0.8, 0.08 ) #26012020
SSMSF_val[2017] = u_float( 0.8, 0.08 ) #26012020
SSMSF_val[2018] = u_float( 0.8, 0.08 ) #26012020

WJetsSF_val = {}
WJetsSF_val[2016] = u_float( 1.14, 0.13 ) #12022020
WJetsSF_val[2017] = u_float( 1.09, 0.13 )
WJetsSF_val[2018] = u_float( 1.09, 0.13 )

QCDSF_val = {}
QCDSF_val[2016] = u_float( 1.00, 0.1 ) #12022020
QCDSF_val[2017] = u_float( 1.00, 0.1 )
QCDSF_val[2018] = u_float( 1.00, 0.1 )

TTSF_val = {}
TTSF_val[2016] = u_float( 1.00, 0.07 ) #12022020
TTSF_val[2017] = u_float( 1.00, 0.06 )
TTSF_val[2018] = u_float( 1.02, 0.08 )

DYSF_val = {}
DYSF_val[2016] = u_float( 1.19, 0.05 ) #12022020
DYSF_val[2017] = u_float( 1.14, 0.04 )
DYSF_val[2018] = u_float( 1.18, 0.05 )



misIDSF_val = {}
misIDSF_val[2016] = u_float( 2.13, 0.32 ) #12022020
misIDSF_val[2017] = u_float( 2.55, 0.34 )
misIDSF_val[2018] = u_float( 1.50, 0.16 )

fakeSF_val = {}
fakeSF_val[2016] = u_float( 1.00, 0.09 )
fakeSF_val[2017] = u_float( 1.00, 0.09 )
fakeSF_val[2018] = u_float( 1.00, 0.09 )

WGSF_val = {}
WGSF_val[2016] = u_float( 0.96, 0.17 ) #12022020
WGSF_val[2017] = u_float( 1.20, 0.12 ) # currently 1.07 in 3jets, 1.35 in 4jets
WGSF_val[2018] = u_float( 1.17, 0.15 ) #2020 01 20

otherSF_val = {}
otherSF_val[2016] = u_float( 1.00, 0.2 ) #12022020
otherSF_val[2017] = u_float( 1.00, 0.2 ) #2020 01 20
otherSF_val[2018] = u_float( 1.00, 0.2 ) #2020 01 20

ZGSF_val = {}
ZGSF_val[2016] = u_float( 0.93, 0.19 )  # currently 0.9 in 3jets, 1.05 in 4jets
ZGSF_val[2017] = u_float( 0.84, 0.12 )  #2020 01 20
ZGSF_val[2018] = u_float( 0.97, 0.19 )  #2020 01 20

# all processes are all samples + them splitted in photon categories
allProcesses            = copy.copy(default_sampleList)
allProcesses           += [ s+"_gen"   for s in default_sampleList ]
allProcesses           += [ s+"_misID" for s in default_sampleList ]
allProcesses           += [ s+"_had"   for s in default_sampleList ]
allProcesses           += [ s+"_magic" for s in default_sampleList ]

analysis_results = os.path.join( results_directory, "analysis" )
cache_dir        = os.path.join( cache_directory,   "analysis" )
jmeVariations    = ["jer", "jerUp", "jerDown", "jesTotalUp", "jesTotalDown"]
metVariations    = ["unclustEnUp", "unclustEnDown"]

# Control Regions Settings
controlRegions = {}
#hadronic fakes

controlRegions["fake3"]     = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1), "photonIso":"noChgIsoNoSieie" },
                                 "channels":   lepChannels,
                                 "regions":    chgIsoPtRegions,
                                 "inclRegion": chgIsoRegions,
                                 "noPhotonCR": False,
                                 "processes":  processes,
                               }
 
controlRegions["fake3high"] = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1), "photonIso":"highSieieNoChgIso" },
                                 "channels":   lepChannels,
                                 "regions":    chgIsoPtRegions,
                                 "inclRegion": chgIsoRegions,
                                 "noPhotonCR": False,
                                 "processes":  processes,
                               }
 
controlRegions["fake3phigh"] = { "parameters": { "zWindow":"all", "nJet":(3,-1), "nBTag":(1,-1), "nPhoton":(1,1), "photonIso":"highSieieNoChgIso" },
                                 "channels":   lepChannels,
                                 "regions":    chgIsoPtRegions,
                                 "inclRegion": chgIsoRegions,
                                 "noPhotonCR": False,
                                 "processes":  processes,
                               }
 
controlRegions["fake4p"]     = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1), "photonIso":"noChgIsoNoSieie" },
                                 "channels":   lepChannels,
                                 "regions":    chgIsoPtRegions,
                                 "inclRegion": chgIsoRegions,
                                 "noPhotonCR": False,
                                 "processes":  processes,
                               }
 
controlRegions["fake4phigh"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1), "photonIso":"highSieieNoChgIso" },
                                 "channels":   lepChannels,
                                 "regions":    chgIsoPtRegions,
                                 "inclRegion": chgIsoRegions,
                                 "noPhotonCR": False,
                                 "processes":  processes,
                               }
 
controlRegions["fake3low"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1), "photonIso":"lowSieieNoChgIso" },
                                "channels":   lepChannels,
                                "regions":    chgIsoNoSRPtRegions,
                                "inclRegion": chgIsoNoSRRegions,
                                "noPhotonCR": False,
                                "processes":  processes,
                              }
 
controlRegions["fake3plow"]  = { "parameters": { "zWindow":"all", "nJet":(3,-1), "nBTag":(1,-1), "nPhoton":(1,1), "photonIso":"lowSieieNoChgIso" },
                                "channels":   lepChannels,
                                "regions":    chgIsoNoSRPtRegions,
                                "inclRegion": chgIsoNoSRRegions,
                                "noPhotonCR": False,
                                "processes":  processes,
                              }
 
controlRegions["fake4plow"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1), "photonIso":"lowSieieNoChgIso" },
                                "channels":   lepChannels,
                                "regions":    chgIsoNoSRPtRegions,
                                "inclRegion": chgIsoNoSRRegions,
                                "noPhotonCR": False,
                                "processes":  processes,
                              }

# dileptonic ee/mumu all m(l,l) nBTag0 nPhoton0 CR for DY ScaleFactor
controlRegions["DY2"]  = { "parameters": { "dileptonic":True, "zWindow":"onZSFllTight", "nJet":(2,2),  "nBTag":(0,0), "nPhoton":(0,0) },
                           "channels":   dilepChannels,
                           "regions":    noPhotonRegionTTG,
                           "inclRegion": noPhotonRegionTTG,
                           "noPhotonCR": True,
                           "processes":  processesNoPhoton,
                         }
                            
controlRegions["DY3"]  = { "parameters": { "dileptonic":True, "zWindow":"onZSFllTight", "nJet":(3,3),  "nBTag":(0,0), "nPhoton":(0,0) },
                           "channels":   dilepChannels,
                           "regions":    noPhotonRegionTTG,
                           "inclRegion": noPhotonRegionTTG,
                           "noPhotonCR": True,
                           "processes":  processesNoPhoton,
                         }

controlRegions["DY3p"]  = { "parameters": { "dileptonic":True, "zWindow":"onZSFllTight", "nJet":(3,-1),  "nBTag":(0,0), "nPhoton":(0,0) },
                           "channels":   dilepChannels,
                           "regions":    noPhotonRegionTTG,
                           "inclRegion": noPhotonRegionTTG,
                           "noPhotonCR": True,
                           "processes":  processesNoPhoton,
                         }

controlRegions["DY4"]  = { "parameters":{"dileptonic":True, "zWindow":"onZSFllTight", "nJet":(4,4),  "nBTag":(0,0), "nPhoton":(0,0) },
                           "channels":   dilepChannels,
                           "regions":    noPhotonRegionTTG,
                           "inclRegion": noPhotonRegionTTG,
                           "noPhotonCR": True,
                           "processes":  processesNoPhoton,
                         }

controlRegions["DY5"]  = { "parameters": { "dileptonic":True, "zWindow":"onZSFllTight", "nJet":(5,5),  "nBTag":(0,0), "nPhoton":(0,0) },
                           "channels":   dilepChannels,
                           "regions":    noPhotonRegionTTG,
                           "inclRegion": noPhotonRegionTTG,
                           "noPhotonCR": True,
                           "processes":  processesNoPhoton,
                         }

controlRegions["DY4p"] = { "parameters": { "dileptonic":True, "zWindow":"onZSFllTight", "nJet":(4,-1), "nBTag":(0,0), "nPhoton":(0,0) },
                           "channels":   dilepChannels,
                           "regions":    noPhotonRegionTTG,
                           "inclRegion": noPhotonRegionTTG,
                           "noPhotonCR": True,
                           "processes":  processesNoPhoton,
                         }


# nPhoton0 nBTag1p CR for TTbar
controlRegions["TT2"]  = { "parameters": { "zWindow":"all", "nJet":(2,2),  "nBTag":(1,-1), "nPhoton":(0,0) },
                           "channels":   lepChannels,
                           "regions":    noPhotonRegionTTG,
                           "inclRegion": noPhotonRegionTTG,
                           "noPhotonCR": True,
                           "processes":  processesNoPhoton,
                         }

controlRegions["TT3"]  = { "parameters": { "zWindow":"all", "nJet":(3,3),  "nBTag":(1,-1), "nPhoton":(0,0) },
                           "channels":   lepChannels,
                           "regions":    noPhotonRegionTTG,
                           "inclRegion": noPhotonRegionTTG,
                           "noPhotonCR": True,
                           "processes":  processesNoPhoton,
                         }

controlRegions["TT3p"]  = { "parameters": { "zWindow":"all", "nJet":(3,-1),  "nBTag":(1,-1), "nPhoton":(0,0) },
                           "channels":   lepChannels,
                           "regions":    noPhotonRegionTTG,
                           "inclRegion": noPhotonRegionTTG,
                           "noPhotonCR": True,
                           "processes":  processesNoPhoton,
                         }

controlRegions["TT4p"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(0,0) },
                           "channels":   lepChannels,
                           "regions":    noPhotonRegionTTG,
                           "inclRegion": noPhotonRegionTTG,
                           "noPhotonCR": True,
                           "processes":  processesNoPhoton,
                         }


# nPhoton0 nBTag0 CR for W+Jets
controlRegions["WJets2"]  = { "parameters": { "zWindow":"all", "nJet":(2,2),  "nBTag":(0,0), "nPhoton":(0,0) },
                              "channels":   lepChannels,
                              "regions":    noPhotonRegionTTG,
                              "inclRegion": noPhotonRegionTTG,
                              "noPhotonCR": True,
                              "processes":  processesNoPhoton,
                         }

controlRegions["WJets2p"]  = { "parameters": { "zWindow":"all", "nJet":(2,-1),  "nBTag":(0,0), "nPhoton":(0,0) },
                              "channels":   lepChannels,
                              "regions":    noPhotonRegionTTG,
                              "inclRegion": noPhotonRegionTTG,
                              "noPhotonCR": True,
                              "processes":  processesNoPhoton,
                         }

controlRegions["WJets3"]  = { "parameters": { "zWindow":"all", "nJet":(3,3),  "nBTag":(0,0), "nPhoton":(0,0) },
                              "channels":   lepChannels,
                              "regions":    noPhotonRegionTTG,
                              "inclRegion": noPhotonRegionTTG,
                              "noPhotonCR": True,
                              "processes":  processesNoPhoton,
                         }

controlRegions["WJets3p"]  = { "parameters": { "zWindow":"all", "nJet":(3,-1),  "nBTag":(0,0), "nPhoton":(0,0) },
                              "channels":   lepChannels,
                              "regions":    noPhotonRegionTTG,
                              "inclRegion": noPhotonRegionTTG,
                              "noPhotonCR": True,
                              "processes":  processesNoPhoton,
                         }

controlRegions["WJets4p"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(0,0), "nPhoton":(0,0) },
                              "channels":   lepChannels,
                              "regions":    noPhotonRegionTTG,
                              "inclRegion": noPhotonRegionTTG,
                              "noPhotonCR": True,
                              "processes":  processesNoPhoton,
                         }


controlRegions["WJets2Eta0003"]  = { "parameters": { "zWindow":"all", "nJet":(2,2),  "nBTag":(0,0), "nPhoton":(0,0), "leptonEta":(0.0,0.3) },
                                     "channels":   lepChannels,
                                     "regions":    noPhotonRegionTTG,
                                     "inclRegion": noPhotonRegionTTG,
                                     "noPhotonCR": True,
                                     "processes":  processesNoPhoton,
                                   }

controlRegions["WJets2Eta0306"]  = { "parameters": { "zWindow":"all", "nJet":(2,2),  "nBTag":(0,0), "nPhoton":(0,0), "leptonEta":(0.3,0.6) },
                                     "channels":   lepChannels,
                                     "regions":    noPhotonRegionTTG,
                                     "inclRegion": noPhotonRegionTTG,
                                     "noPhotonCR": True,
                                     "processes":  processesNoPhoton,
                                   }


controlRegions["WJets2Eta0609"]  = { "parameters": { "zWindow":"all", "nJet":(2,2),  "nBTag":(0,0), "nPhoton":(0,0), "leptonEta":(0.6,0.9) },
                                     "channels":   lepChannels,
                                     "regions":    noPhotonRegionTTG,
                                     "inclRegion": noPhotonRegionTTG,
                                     "noPhotonCR": True,
                                     "processes":  processesNoPhoton,
                                   }


controlRegions["WJets2Eta0912"]  = { "parameters": { "zWindow":"all", "nJet":(2,2),  "nBTag":(0,0), "nPhoton":(0,0), "leptonEta":(0.9,1.2) },
                                     "channels":   lepChannels,
                                     "regions":    noPhotonRegionTTG,
                                     "inclRegion": noPhotonRegionTTG,
                                     "noPhotonCR": True,
                                     "processes":  processesNoPhoton,
                                   }


controlRegions["WJets2Eta1215"]  = { "parameters": { "zWindow":"all", "nJet":(2,2),  "nBTag":(0,0), "nPhoton":(0,0), "leptonEta":(1.2,1.5) },
                                     "channels":   lepChannels,
                                     "regions":    noPhotonRegionTTG,
                                     "inclRegion": noPhotonRegionTTG,
                                     "noPhotonCR": True,
                                     "processes":  processesNoPhoton,
                                   }


controlRegions["WJets2Eta1518"]  = { "parameters": { "zWindow":"all", "nJet":(2,2),  "nBTag":(0,0), "nPhoton":(0,0), "leptonEta":(1.5,1.8) },
                                     "channels":   lepChannels,
                                     "regions":    noPhotonRegionTTG,
                                     "inclRegion": noPhotonRegionTTG,
                                     "noPhotonCR": True,
                                     "processes":  processesNoPhoton,
                                   }


controlRegions["WJets2Eta1821"]  = { "parameters": { "zWindow":"all", "nJet":(2,2),  "nBTag":(0,0), "nPhoton":(0,0), "leptonEta":(1.8,2.1) },
                                     "channels":   lepChannels,
                                     "regions":    noPhotonRegionTTG,
                                     "inclRegion": noPhotonRegionTTG,
                                     "noPhotonCR": True,
                                     "processes":  processesNoPhoton,
                                   }


controlRegions["WJets2Eta2124"]  = { "parameters": { "zWindow":"all", "nJet":(2,2),  "nBTag":(0,0), "nPhoton":(0,0), "leptonEta":(2.1,2.4) },
                                     "channels":   lepChannels,
                                     "regions":    noPhotonRegionTTG,
                                     "inclRegion": noPhotonRegionTTG,
                                     "noPhotonCR": True,
                                     "processes":  processesNoPhoton,
                                   }


controlRegions["WJetsEC2"]  = { "parameters": { "zWindow":"all", "nJet":(2,2),  "nBTag":(0,0), "nPhoton":(0,0), "leptonEta":(1.479,-1) },
                              "channels":   lepChannels,
                              "regions":    noPhotonRegionTTG,
                              "inclRegion": noPhotonRegionTTG,
                              "noPhotonCR": True,
                              "processes":  processesNoPhoton,
                         }

controlRegions["WJetsEC3"]  = { "parameters": { "zWindow":"all", "nJet":(3,3),  "nBTag":(0,0), "nPhoton":(0,0), "leptonEta":(1.479,-1) },
                              "channels":   lepChannels,
                              "regions":    noPhotonRegionTTG,
                              "inclRegion": noPhotonRegionTTG,
                              "noPhotonCR": True,
                              "processes":  processesNoPhoton,
                         }

controlRegions["WJetsEC3p"]  = { "parameters": { "zWindow":"all", "nJet":(3,-1),  "nBTag":(0,0), "nPhoton":(0,0), "leptonEta":(1.479,-1) },
                              "channels":   lepChannels,
                              "regions":    noPhotonRegionTTG,
                              "inclRegion": noPhotonRegionTTG,
                              "noPhotonCR": True,
                              "processes":  processesNoPhoton,
                         }

controlRegions["WJetsEC4p"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(0,0), "nPhoton":(0,0), "leptonEta":(1.479,-1) },
                              "channels":   lepChannels,
                              "regions":    noPhotonRegionTTG,
                              "inclRegion": noPhotonRegionTTG,
                              "noPhotonCR": True,
                              "processes":  processesNoPhoton,
                         }

controlRegions["WJetsBarrel2"]  = { "parameters": { "zWindow":"all", "nJet":(2,2),  "nBTag":(0,0), "nPhoton":(0,0), "leptonEta":(0,1.479) },
                              "channels":   lepChannels,
                              "regions":    noPhotonRegionTTG,
                              "inclRegion": noPhotonRegionTTG,
                              "noPhotonCR": True,
                              "processes":  processesNoPhoton,
                         }

controlRegions["WJetsBarrel3"]  = { "parameters": { "zWindow":"all", "nJet":(3,3),  "nBTag":(0,0), "nPhoton":(0,0), "leptonEta":(0,1.479) },
                              "channels":   lepChannels,
                              "regions":    noPhotonRegionTTG,
                              "inclRegion": noPhotonRegionTTG,
                              "noPhotonCR": True,
                              "processes":  processesNoPhoton,
                         }

controlRegions["WJetsBarrel3p"]  = { "parameters": { "zWindow":"all", "nJet":(3,-1),  "nBTag":(0,0), "nPhoton":(0,0), "leptonEta":(0,1.479) },
                              "channels":   lepChannels,
                              "regions":    noPhotonRegionTTG,
                              "inclRegion": noPhotonRegionTTG,
                              "noPhotonCR": True,
                              "processes":  processesNoPhoton,
                         }

controlRegions["WJetsBarrel4p"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(0,0), "nPhoton":(0,0), "leptonEta":(0,1.479) },
                              "channels":   lepChannels,
                              "regions":    noPhotonRegionTTG,
                              "inclRegion": noPhotonRegionTTG,
                              "noPhotonCR": True,
                              "processes":  processesNoPhoton,
                         }

#controlRegions["WJets3MET"]  = { "parameters": { "zWindow":"all", "nJet":(3,3),  "nBTag":(0,0), "nPhoton":(0,0), "MET":(80,-1) },
#                                 "channels":   lepChannels,
#                                 "regions":    noPhotonRegionTTG,
#                                 "inclRegion": noPhotonRegionTTG,
#                                 "noPhotonCR": True,
#                                 "processes":  processesNoPhoton,
#                            }

#controlRegions["WJets4pMET"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(0,0), "nPhoton":(0,0), "MET":(80,-1) },
#                                 "channels":   lepChannels,
#                                 "regions":    noPhotonRegionTTG,
#                                 "inclRegion": noPhotonRegionTTG,
#                                 "noPhotonCR": True,
#                                 "processes":  processesNoPhoton,
#                             }


controlRegions["ZG3"]  = { "parameters": { "dileptonic":True, "zWindow":"onZSFllgTight", "nJet":(3,3),  "nBTag":(0,0), "nPhoton":(1,1) },
                           "channels":   dilepChannels,
                           "regions":    inclRegionsTTG,
                           "inclRegion": inclRegionsTTG,
                           "noPhotonCR": False,
                           "processes":  processesNoPhoton,
                         }

controlRegions["ZG3p"]  = { "parameters": { "dileptonic":True, "zWindow":"onZSFllgTight", "nJet":(3,-1),  "nBTag":(0,0), "nPhoton":(1,1) },
                           "channels":   dilepChannels,
                           "regions":    inclRegionsTTG,
                           "inclRegion": inclRegionsTTG,
                           "noPhotonCR": False,
                           "processes":  processesNoPhoton,
                         }

controlRegions["ZG4p"]  = { "parameters":{"dileptonic":True, "zWindow":"onZSFllgTight", "nJet":(4,-1),  "nBTag":(0,0), "nPhoton":(1,1) },
                           "channels":   dilepChannels,
                           "regions":    inclRegionsTTG,
                           "inclRegion": inclRegionsTTG,
                           "noPhotonCR": False,
                           "processes":  processesNoPhoton,
                         }

# nPhoton1 nBTag0 offZeg m(e,gamma) CR for V+Gamma
controlRegions["VG2p"]  = { "parameters": { "zWindow":"offZeg", "nJet":(2,-1), "nBTag":(0,0), "nPhoton":(1,1) },
                           "channels":   lepChannels,
                           "regions":    mLgPtRegions,
                           "inclRegion": mLgRegions,
                           "noPhotonCR": False,
                           "processes":  processes,
                         }

controlRegions["VG2"]  = { "parameters": { "zWindow":"offZeg", "nJet":(2,2), "nBTag":(0,0), "nPhoton":(1,1) },
                           "channels":   lepChannels,
                           "regions":    mLgPtRegions,
                           "inclRegion": mLgRegions,
                           "noPhotonCR": False,
                           "processes":  processes,
                         }

controlRegions["VG3"]  = { "parameters": { "zWindow":"offZeg", "nJet":(3,3), "nBTag":(0,0), "nPhoton":(1,1) },
                           "channels":   lepChannels,
                           "regions":    mLgPtRegions,
                           "inclRegion": mLgRegions,
                           "noPhotonCR": False,
                           "processes":  processes,
                         }

controlRegions["VGBarrel3"]  = { "parameters": { "zWindow":"offZeg", "nJet":(3,3), "nBTag":(0,0), "nPhoton":(1,1), "leptonEta":(0,1.479) },
                           "channels":   lepChannels,
                           "regions":    mLgPtRegions,
                           "inclRegion": mLgRegions,
                           "noPhotonCR": False,
                           "processes":  processes,
                         }

controlRegions["VGEC3"]  = { "parameters": { "zWindow":"offZeg", "nJet":(3,3), "nBTag":(0,0), "nPhoton":(1,1), "leptonEta":(1.479,-1) },
                           "channels":   lepChannels,
                           "regions":    mLgPtRegions,
                           "inclRegion": mLgRegions,
                           "noPhotonCR": False,
                           "processes":  processes,
                         }

controlRegions["VG3p"]  = { "parameters": { "zWindow":"offZeg", "nJet":(3,-1), "nBTag":(0,0), "nPhoton":(1,1) },
                           "channels":   lepChannels,
                           "regions":    mLgPtRegions,
                           "inclRegion": mLgRegions,
                           "noPhotonCR": False,
                           "processes":  processes,
                         }

controlRegions["VGBarrel3p"]  = { "parameters": { "zWindow":"offZeg", "nJet":(3,-1), "nBTag":(0,0), "nPhoton":(1,1), "leptonEta":(0,1.479) },
                           "channels":   lepChannels,
                           "regions":    mLgPtRegions,
                           "inclRegion": mLgRegions,
                           "noPhotonCR": False,
                           "processes":  processes,
                         }

controlRegions["VGEC3p"]  = { "parameters": { "zWindow":"offZeg", "nJet":(3,-1), "nBTag":(0,0), "nPhoton":(1,1), "leptonEta":(1.479,-1) },
                           "channels":   lepChannels,
                           "regions":    mLgPtRegions,
                           "inclRegion": mLgRegions,
                           "noPhotonCR": False,
                           "processes":  processes,
                         }

controlRegions["VG4"]  = { "parameters": { "zWindow":"offZeg", "nJet":(4,4), "nBTag":(0,0), "nPhoton":(1,1) },
                           "channels":   lepChannels,
                           "regions":    mLgPtRegions,
                           "inclRegion": mLgRegions,
                           "noPhotonCR": False,
                           "processes":  processes,
                         }

controlRegions["VG5"]  = { "parameters": { "zWindow":"offZeg", "nJet":(5,5), "nBTag":(0,0), "nPhoton":(1,1) },
                           "channels":   lepChannels,
                           "regions":    mLgPtRegions,
                           "inclRegion": mLgRegions,
                           "noPhotonCR": False,
                           "processes":  processes,
                         }

controlRegions["VG4p"] = { "parameters": { "zWindow":"offZeg", "nJet":(4,-1), "nBTag":(0,0), "nPhoton":(1,1)  },
                           "channels":   lepChannels,
                           "regions":    mLgPtRegions,
                           "inclRegion": mLgRegions,
                           "noPhotonCR": False,
                           "processes":  processes,
                         }

controlRegions["VGBarrel4p"] = { "parameters": { "zWindow":"offZeg", "nJet":(4,-1), "nBTag":(0,0), "nPhoton":(1,1), "leptonEta":(0,1.479) },
                           "channels":   lepChannels,
                           "regions":    mLgPtRegions,
                           "inclRegion": mLgRegions,
                           "noPhotonCR": False,
                           "processes":  processes,
                         }

controlRegions["VGEC4p"] = { "parameters": { "zWindow":"offZeg", "nJet":(4,-1), "nBTag":(0,0), "nPhoton":(1,1), "leptonEta":(1.479,-1) },
                           "channels":   lepChannels,
                           "regions":    mLgPtRegions,
                           "inclRegion": mLgRegions,
                           "noPhotonCR": False,
                           "processes":  processes,
                         }

controlRegions["VG3MET"]  = { "parameters": { "zWindow":"offZeg", "nJet":(3,3), "nBTag":(0,0), "nPhoton":(1,1), "MET":(50,-1) },
                              "channels":   lepChannels,
                              "regions":    mLgPtRegions,
                              "inclRegion": mLgRegions,
                              "noPhotonCR": False,
                              "processes":  processes,
                            }

controlRegions["VG4pMET"] = { "parameters": { "zWindow":"offZeg", "nJet":(4,-1), "nBTag":(0,0), "nPhoton":(1,1), "MET":(50,-1)  },
                              "channels":   lepChannels,
                              "regions":    mLgPtRegions,
                              "inclRegion": mLgRegions,
                              "noPhotonCR": False,
                              "processes":  processes,
                            }


# both VG + misID
controlRegions["VGmis2p"]  = { "parameters": { "zWindow":"all", "nJet":(2,-1), "nBTag":(0,0), "nPhoton":(1,1) },
                              "channels":   lepChannels,
                              "regions":    regionsTTG,
                              "inclRegion": inclRegionsTTG,
                              "noPhotonCR": False,
                              "processes":  processes,
                            }

controlRegions["VGmis2"]  = { "parameters": { "zWindow":"all", "nJet":(2,2), "nBTag":(0,0), "nPhoton":(1,1) },
                              "channels":   lepChannels,
                              "regions":    regionsTTG,
                              "inclRegion": inclRegionsTTG,
                              "noPhotonCR": False,
                              "processes":  processes,
                            }

controlRegions["VGmis3"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(0,0), "nPhoton":(1,1) },
                              "channels":   lepChannels,
                              "regions":    regionsTTG,
                              "inclRegion": inclRegionsTTG,
                              "noPhotonCR": False,
                              "processes":  processes,
                            }

controlRegions["VGmis4"]  = { "parameters": { "zWindow":"all", "nJet":(4,4), "nBTag":(0,0), "nPhoton":(1,1) },
                              "channels":   lepChannels,
                              "regions":    regionsTTG,
                              "inclRegion": inclRegionsTTG,
                              "noPhotonCR": False,
                              "processes":  processes,
                            }

controlRegions["VGmis5"]  = { "parameters": { "zWindow":"all", "nJet":(5,5), "nBTag":(0,0), "nPhoton":(1,1) },
                              "channels":   lepChannels,
                              "regions":    regionsTTG,
                              "inclRegion": inclRegionsTTG,
                              "noPhotonCR": False,
                              "processes":  processes,
                            }

controlRegions["VGmis4p"]  = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(0,0), "nPhoton":(1,1) },
                               "channels":   lepChannels,
                               "regions":    regionsTTG,
                               "inclRegion": inclRegionsTTG,
                               "noPhotonCR": False,
                               "processes":  processes,
                             }

# nPhoton1p nBTag0 onZeg m(e,gamma) CR for misID ScaleFactor DY
controlRegions["misDY2"]  = { "parameters": { "zWindow":"onZeg", "nJet":(2,2), "nBTag":(0,0), "nPhoton":(1,1) },
                              "channels":   ["e"],
                              "regions":    regionsTTG,
                              "inclRegion": inclRegionsTTG,
                              "noPhotonCR": False,
                              "processes":  processes,
                            }

controlRegions["misDY2p"]  = { "parameters": { "zWindow":"onZeg", "nJet":(2,-1), "nBTag":(0,0), "nPhoton":(1,1) },
                               "channels":   ["e"],
                               "regions":    regionsTTG,
                               "inclRegion": inclRegionsTTG,
                               "noPhotonCR": False,
                               "processes":  processes,
                             }

controlRegions["misDY3"]  = { "parameters": { "zWindow":"onZeg", "nJet":(3,3), "nBTag":(0,0), "nPhoton":(1,1) },
                              "channels":   ["e"],
                              "regions":    regionsTTG,
                              "inclRegion": inclRegionsTTG,
                              "noPhotonCR": False,
                              "processes":  processes,
                            }

controlRegions["misDYBarrel3"]  = { "parameters": { "zWindow":"onZeg", "nJet":(3,3), "nBTag":(0,0), "nPhoton":(1,1) },
                              "channels":   ["e"],
                              "regions":    regionsTTG,
                              "inclRegion": inclRegionsTTG,
                              "noPhotonCR": False,
                              "processes":  processes,
                            }

controlRegions["misDYEC3"]  = { "parameters": { "zWindow":"onZeg", "nJet":(3,3), "nBTag":(0,0), "nPhoton":(1,1) },
                              "channels":   ["e"],
                              "regions":    regionsTTG,
                              "inclRegion": inclRegionsTTG,
                              "noPhotonCR": False,
                              "processes":  processes,
                            }

controlRegions["misDY3p"]  = { "parameters": { "zWindow":"onZeg", "nJet":(3,-1), "nBTag":(0,0), "nPhoton":(1,1) },
                              "channels":   ["e"],
                              "regions":    regionsTTG,
                              "inclRegion": inclRegionsTTG,
                              "noPhotonCR": False,
                              "processes":  processes,
                            }

controlRegions["misDYBarrel3p"]  = { "parameters": { "zWindow":"onZeg", "nJet":(3,-1), "nBTag":(0,0), "nPhoton":(1,1) },
                              "channels":   ["e"],
                              "regions":    regionsTTG,
                              "inclRegion": inclRegionsTTG,
                              "noPhotonCR": False,
                              "processes":  processes,
                            }

controlRegions["misDYEC3p"]  = { "parameters": { "zWindow":"onZeg", "nJet":(3,-1), "nBTag":(0,0), "nPhoton":(1,1) },
                              "channels":   ["e"],
                              "regions":    regionsTTG,
                              "inclRegion": inclRegionsTTG,
                              "noPhotonCR": False,
                              "processes":  processes,
                            }

controlRegions["misDY4"]  = { "parameters": { "zWindow":"onZeg", "nJet":(4,4), "nBTag":(0,0), "nPhoton":(1,1) },
                              "channels":   ["e"],
                              "regions":    regionsTTG,
                              "inclRegion": inclRegionsTTG,
                              "noPhotonCR": False,
                              "processes":  processes,
                            }

controlRegions["misDY5"]  = { "parameters": { "zWindow":"onZeg", "nJet":(5,5), "nBTag":(0,0), "nPhoton":(1,1) },
                              "channels":   ["e"],
                              "regions":    regionsTTG,
                              "inclRegion": inclRegionsTTG,
                              "noPhotonCR": False,
                              "processes":  processes,
                            }

controlRegions["misDY4p"] = { "parameters": { "zWindow":"onZeg", "nJet":(4,-1), "nBTag":(0,0), "nPhoton":(1,1) },
                              "channels":   ["e"],
                              "regions":    regionsTTG,
                              "inclRegion": inclRegionsTTG,
                              "noPhotonCR": False,
                              "processes":  processes,
                            }


controlRegions["misDYBarrel4p"] = { "parameters": { "zWindow":"onZeg", "nJet":(4,-1), "nBTag":(0,0), "nPhoton":(1,1) },
                              "channels":   ["e"],
                              "regions":    regionsTTG,
                              "inclRegion": inclRegionsTTG,
                              "noPhotonCR": False,
                              "processes":  processes,
                            }


controlRegions["misDYEC4p"] = { "parameters": { "zWindow":"onZeg", "nJet":(4,-1), "nBTag":(0,0), "nPhoton":(1,1) },
                              "channels":   ["e"],
                              "regions":    regionsTTG,
                              "inclRegion": inclRegionsTTG,
                              "noPhotonCR": False,
                              "processes":  processes,
                            }


#controlRegions["misDY3MET"]  = { "parameters": { "zWindow":"onZeg", "nJet":(3,3), "nBTag":(0,0), "nPhoton":(1,1), "MET":(50,-1) },
#                                 "channels":   ["e"],
#                                 "regions":    regionsTTG,
#                                 "inclRegion": inclRegionsTTG,
#                                 "noPhotonCR": False,
#                                 "processes":  processes,
#                               }

#controlRegions["misDY4pMET"] = { "parameters": { "zWindow":"onZeg", "nJet":(4,-1), "nBTag":(0,0), "nPhoton":(1,1), "MET":(50,-1) },
#                                 "channels":   ["e"],
#                                 "regions":    regionsTTG,
#                                 "inclRegion": inclRegionsTTG,
#                                 "noPhotonCR": False,
#                                 "processes":  processes,
#                               }


# nPhoton1p nBTag2 nJet2 offZeg m(e,gamma) CR for misID ScaleFactor TTbar
controlRegions["misTT2"] = { "parameters": { "zWindow":"offZeg", "nJet":(2,2), "nBTag":(2,2), "nPhoton":(1,1) },
                             "channels":   lepChannels,
                             "regions":    regionsTTG,
                             "inclRegion": inclRegionsTTG,
                             "noPhotonCR": False,
                             "processes":  processes,
                           }


# updates for QCD estimation (else same settings)
QCD_updates               = { "invertLepIso":True,               "nBTag":(0,0),                  "addMisIDSF":True }#, "zWindow":"offZeg" }
QCDTF_updates             = {}
QCDTF_updates["CR"]       = { "invertLepIso":True, "nJet":(2,2), "nBTag":(0,0), "nPhoton":(0,0), "MET":(0,-1), "m3Window":"all", "zWindow":"all" }
QCDTF_updates["SR"]       = {                      "nJet":(2,2),                "nPhoton":(0,0), "MET":(0,-1), "m3Window":"all", "zWindow":"all" }
QCDTF_updates["CRBarrel"] = { "invertLepIso":True, "nJet":(2,2), "nBTag":(0,0), "nPhoton":(0,0), "MET":(0,-1), "m3Window":"all", "zWindow":"all", "leptonEta":(0,1.479) }
QCDTF_updates["SRBarrel"] = {                      "nJet":(2,2),                "nPhoton":(0,0), "MET":(0,-1), "m3Window":"all", "zWindow":"all", "leptonEta":(0,1.479) }
QCDTF_updates["CREC"]     = { "invertLepIso":True, "nJet":(2,2), "nBTag":(0,0), "nPhoton":(0,0), "MET":(0,-1), "m3Window":"all", "zWindow":"all", "leptonEta":(1.479,-1) }
QCDTF_updates["SREC"]     = {                      "nJet":(2,2),                "nPhoton":(0,0), "MET":(0,-1), "m3Window":"all", "zWindow":"all", "leptonEta":(1.479,-1) }
#QCDTF_updates["CR"]       = { "invertLepIso":True, "nJet":(2,2), "nBTag":(0,0),                  "MET":(0,-1), "m3Window":"all", "zWindow":"offZeg", "addMisIDSF":True }
#QCDTF_updates["SR"]       = {                      "nJet":(2,2),                                 "MET":(0,-1), "m3Window":"all", "zWindow":"offZeg", "addMisIDSF":True }
#QCDTF_updates["CRBarrel"] = { "invertLepIso":True, "nJet":(2,2), "nBTag":(0,0),                  "MET":(0,-1), "m3Window":"all", "zWindow":"offZeg", "addMisIDSF":True, "leptonEta":(0,1.479) }
#QCDTF_updates["SRBarrel"] = {                      "nJet":(2,2),                                 "MET":(0,-1), "m3Window":"all", "zWindow":"offZeg", "addMisIDSF":True, "leptonEta":(0,1.479) }
#QCDTF_updates["CREC"]     = { "invertLepIso":True, "nJet":(2,2), "nBTag":(0,0),                  "MET":(0,-1), "m3Window":"all", "zWindow":"offZeg", "addMisIDSF":True, "leptonEta":(1.479,-1) }
#QCDTF_updates["SREC"]     = {                      "nJet":(2,2),                                 "MET":(0,-1), "m3Window":"all", "zWindow":"offZeg", "addMisIDSF":True, "leptonEta":(1.479,-1) }

customQCDTF_updates               = {}
customQCDTF_updates["2J0P"]       = {}
customQCDTF_updates["2J0P"]["CR"] = { "invertLepIso":True, "nJet":(2,2), "nBTag":(0,0), "nPhoton":(0,0), "MET":(0,-1), "m3Window":"all", "zWindow":"all" }
customQCDTF_updates["2J0P"]["SR"] = {                      "nJet":(2,2),                "nPhoton":(0,0), "MET":(0,-1), "m3Window":"all", "zWindow":"all" }
customQCDTF_updates["3J0P"]       = {}
customQCDTF_updates["3J0P"]["CR"] = { "invertLepIso":True, "nJet":(3,3), "nBTag":(0,0), "nPhoton":(0,0), "MET":(0,-1), "m3Window":"all", "zWindow":"all" }
customQCDTF_updates["3J0P"]["SR"] = {                      "nJet":(3,3),                "nPhoton":(0,0), "MET":(0,-1), "m3Window":"all", "zWindow":"all" }
customQCDTF_updates["4J0P"]       = {}
customQCDTF_updates["4J0P"]["CR"] = { "invertLepIso":True, "nJet":(4,4), "nBTag":(0,0), "nPhoton":(0,0), "MET":(0,-1), "m3Window":"all", "zWindow":"all" }
customQCDTF_updates["4J0P"]["SR"] = {                      "nJet":(4,4),                "nPhoton":(0,0), "MET":(0,-1), "m3Window":"all", "zWindow":"all" }
customQCDTF_updates["5J0P"]       = {}
customQCDTF_updates["5J0P"]["CR"] = { "invertLepIso":True, "nJet":(5,5), "nBTag":(0,0), "nPhoton":(0,0), "MET":(0,-1), "m3Window":"all", "zWindow":"all" }
customQCDTF_updates["5J0P"]["SR"] = {                      "nJet":(5,5),                "nPhoton":(0,0), "MET":(0,-1), "m3Window":"all", "zWindow":"all" }

customQCDTF_updates["2J1P"]       = {}
customQCDTF_updates["2J1P"]["CR"] = { "invertLepIso":True, "nJet":(2,2), "nBTag":(0,0), "nPhoton":(1,1), "MET":(0,-1), "m3Window":"all", "zWindow":"offZeg", "addMisIDSF":True }
customQCDTF_updates["2J1P"]["SR"] = {                      "nJet":(2,2),                "nPhoton":(1,1), "MET":(0,-1), "m3Window":"all", "zWindow":"offZeg", "addMisIDSF":True }
customQCDTF_updates["3J1P"]       = {}
customQCDTF_updates["3J1P"]["CR"] = { "invertLepIso":True, "nJet":(3,3), "nBTag":(0,0), "nPhoton":(1,1), "MET":(0,-1), "m3Window":"all", "zWindow":"offZeg", "addMisIDSF":True }
customQCDTF_updates["3J1P"]["SR"] = {                      "nJet":(3,3),                "nPhoton":(1,1), "MET":(0,-1), "m3Window":"all", "zWindow":"offZeg", "addMisIDSF":True }
customQCDTF_updates["4J1P"]       = {}
customQCDTF_updates["4J1P"]["CR"] = { "invertLepIso":True, "nJet":(4,4), "nBTag":(0,0), "nPhoton":(1,1), "MET":(0,-1), "m3Window":"all", "zWindow":"offZeg", "addMisIDSF":True }
customQCDTF_updates["4J1P"]["SR"] = {                      "nJet":(4,4),                "nPhoton":(1,1), "MET":(0,-1), "m3Window":"all", "zWindow":"offZeg", "addMisIDSF":True }
customQCDTF_updates["5J1P"]       = {}
customQCDTF_updates["5J1P"]["CR"] = { "invertLepIso":True, "nJet":(5,5), "nBTag":(0,0), "nPhoton":(1,1), "MET":(0,-1), "m3Window":"all", "zWindow":"offZeg", "addMisIDSF":True }
customQCDTF_updates["5J1P"]["SR"] = {                      "nJet":(5,5),                "nPhoton":(1,1), "MET":(0,-1), "m3Window":"all", "zWindow":"offZeg", "addMisIDSF":True }

QCD_cutReplacements = {
                        "mLtight0Gamma":     "mLinvtight0Gamma",
                        "PhotonGood0":       "PhotonGoodInvLepIso0",
#                        "m3":                "m3inv",
}

# specific region cuts that should not be considered in the TF calculation as they are specifically set by the QCDTF_updates (e.g. no photon_pt cut as QCDTF_updates require 0 photons)
QCDTF_regionCutRemovals = [
                            "mLtight0Gamma",
                            "PhotonGood",
                            "PhotonNoChgIsoNoSieie",
                            "nJetGood",
                            "m3",
]


allRegions = copy.copy(controlRegions)
allRegions.update(signalRegions)

# RegionPlot ordering
limitOrdering  = []

noPCR = [ key for key, val in allRegions.items() if val["noPhotonCR"] ]
noPCR.sort()
limitOrdering += noPCR

pCR = [ key for key, val in controlRegions.items() if not val["noPhotonCR"] and not "fake" in key]
pCR.sort()
limitOrdering += pCR

pCRfake = [ key for key, val in controlRegions.items() if not val["noPhotonCR"] and "fake" in key]
pCRfake.sort()
limitOrdering += pCRfake

pSR = [ key for key, val in signalRegions.items() ]
pSR.sort()
limitOrdering += pSR


# EFT parameter ranges:
# 20 bins from -1 to 1 + the SM value 0, calc value in the middle of the bin
xRange       = np.linspace( -1, 1, 20, endpoint=False)
halfstepsize = 0.5 * ( xRange[1] - xRange[0] )
xRange       = [ round(el + halfstepsize, 3) for el in xRange ] + [0]
xRange.sort()

eftParameterRange = {}
eftParameterRange["ctZ"]  = xRange
eftParameterRange["ctZI"] = xRange
#print xRange
