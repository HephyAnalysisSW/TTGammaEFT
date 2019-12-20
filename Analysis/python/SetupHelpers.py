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
TT          = ["TT_pow_gen","TT_pow_had", "TTG_had"]
WG          = ["WG_gen","WG_had"]
ZG          = ["ZG_gen","ZG_had"]
VG          = ["WG_gen","WG_had","ZG_gen","ZG_had"]
other_misID = ["WJets_misID","other_misID","WG_misID","ZG_misID"]
other       = ["other_gen","other_had"]
WJets       = ["WJets_gen","WJets_had"]
QCD         = ["QCD-DD"]

default_sampleList            = ["TTG","TT_pow","DY_LO","ZG","WG","WJets","other","QCD-DD"]
default_photonSampleList      = signal + DY_misID + DY + TT_misID + TT + WG + ZG + other_misID + other + WJets + QCD

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
}


signalRegions = {}
# Signal Regions Settings
# processes.keys() will be the proc visible in the combine card
# processes.values() is a list of processes that will be combined for the entry in combine
signalRegions["SR3"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1) },
                          "channels":   lepChannels,
                          "regions":    regionsTTG,
                          "inclRegion": inclRegionsTTG,
                          "noPhotonCR": False,
                          "processes":  processes,
                         }

signalRegions["SR4p"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1) },
                          "channels":   lepChannels,
                          "regions":    regionsTTG,
                          "inclRegion": inclRegionsTTG,
                          "noPhotonCR": False,
                          "processes":  processes,
                         }

signalRegions["SR3Fine"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1) },
                              "channels":   lepChannels,
                              "regions":    regionsTTGFine,
                              "inclRegion": inclRegionsTTG,
                              "noPhotonCR": False,
                              "processes":  processes,
                             }

signalRegions["SR4pFine"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1) },
                              "channels":   lepChannels,
                              "regions":    regionsTTGFine,
                              "inclRegion": inclRegionsTTG,
                              "noPhotonCR": False,
                              "processes":  processes,
                             }

signalRegions["SR3M3"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1) },
                          "channels":   lepChannels,
                          "regions":    m3PtRegions,
                          "inclRegion": m3Regions,
                          "noPhotonCR": False,
                          "processes":  processes,
                         }

signalRegions["SR4pM3"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1) },
                          "channels":   lepChannels,
                          "regions":    m3PtRegions,
                          "inclRegion": m3Regions,
                          "noPhotonCR": False,
                          "processes":  processes,
                         }

signalRegions["SR3Eta"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1) },
                             "channels":   lepChannels,
                             "regions":    regionsTTGEta,
                             "inclRegion": inclRegionsTTG,
                             "noPhotonCR": False,
                             "processes":  processes,
                            }

signalRegions["SR4pEta"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1) },
                             "channels":   lepChannels,
                             "regions":    regionsTTGEta,
                             "inclRegion": inclRegionsTTG,
                             "noPhotonCR": False,
                             "processes":  processes,
                            }

signalRegions["SR3EtaFine"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1) },
                                 "channels":   lepChannels,
                                 "regions":    regionsTTGEtaFine,
                                 "inclRegion": inclRegionsTTG,
                                 "noPhotonCR": False,
                                 "processes":  processes,
                               }

signalRegions["SR4pEtaFine"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1) },
                                 "channels":   lepChannels,
                                 "regions":    regionsTTGEtaFine,
                                 "inclRegion": inclRegionsTTG,
                                 "noPhotonCR": False,
                                 "processes":  processes,
                                }

signalRegions["SR3EtaM3"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1) },
                               "channels":   lepChannels,
                               "regions":    m3EtaRegions,
                               "inclRegion": m3Regions,
                               "noPhotonCR": False,
                               "processes":  processes,
                              }

signalRegions["SR4pEtaM3"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1) },
                               "channels":   lepChannels,
                               "regions":    m3EtaRegions,
                               "inclRegion": m3Regions,
                               "noPhotonCR": False,
                               "processes":  processes,
                              }

#signalRegions["SR3onM3"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1), "m3Window":"onM3" },
#                              "channels":   lepChannels,
#                              "regions":    regionsTTG,
#                              "inclRegion": inclRegionsTTG,
#                              "noPhotonCR": False,
#                              "processes":  processes,
#                            }

#signalRegions["SR3offM3"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1), "m3Window":"offM3" },
#                               "channels":   lepChannels,
#                               "regions":    regionsTTG,
#                               "inclRegion": inclRegionsTTG,
#                               "noPhotonCR": False,
#                               "processes":  processes,
#                             }

#signalRegions["SR4ponM3"]  = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1), "m3Window":"onM3" },
#                              "channels":   lepChannels,
#                              "regions":    regionsTTG,
#                              "inclRegion": inclRegionsTTG,
#                              "noPhotonCR": False,
#                              "processes":  processes,
#                            }

#signalRegions["SR4poffM3"]  = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1), "m3Window":"offM3" },
#                               "channels":   lepChannels,
#                               "regions":    regionsTTG,
#                               "inclRegion": inclRegionsTTG,
#                               "noPhotonCR": False,
#                               "processes":  processes,
#                             }

default_SR = signalRegions["SR4pM3"]

#Define defaults here
default_nJet         = (4,-1)
default_nBTag        = (1,-1)
default_nPhoton      = (1,1)
default_MET          = (0,-1)
default_zWindow      = "all"
default_dileptonic   = False
default_invLepIso    = False
default_addMisIDSF   = False
default_photonCat    = "all"
default_m3Window     = "all"
default_photonIso    = "lowChgIsolowSieie"

SSMSF_val = {}
SSMSF_val[2016] = u_float( 0.8, 0.07 )
SSMSF_val[2017] = u_float( 0.8, 0.07 )
SSMSF_val[2018] = u_float( 0.8, 0.07 )

QCDSF_val = {}
QCDSF_val[2016] = u_float( 1.0, 0.05 )
QCDSF_val[2017] = u_float( 1.0, 0.05 )
QCDSF_val[2018] = u_float( 1.0, 0.05 )

WJetsSF_val = {}
WJetsSF_val[2016] = u_float( 0.89, 0.05 )
WJetsSF_val[2017] = u_float( 0.89, 0.05 )
WJetsSF_val[2018] = u_float( 0.89, 0.05 )

TTSF_val = {}
TTSF_val[2016] = u_float( 0.95, 0.04 )
TTSF_val[2017] = u_float( 0.95, 0.04 )
TTSF_val[2018] = u_float( 0.95, 0.04 )

misIDSF_val = {}
misIDSF_val[2016] = u_float( 2.18, 0.30 )
misIDSF_val[2017] = u_float( 2.03, 0.20 )
misIDSF_val[2018] = u_float( 1.43, 0.14 )

fakeSF_val = {}
fakeSF_val[2016] = u_float( 0.92, 0.09 )
fakeSF_val[2017] = u_float( 0.92, 0.09 )
fakeSF_val[2018] = u_float( 0.92, 0.09 )

DYSF_val = {}
DYSF_val[2016] = u_float( 1.0, 0.05 )
DYSF_val[2017] = u_float( 1.0, 0.05 )
DYSF_val[2018] = u_float( 1.0, 0.05 )

VGSF_val = {}
VGSF_val[2016] = u_float( 0.95, 0.1 )
VGSF_val[2017] = u_float( 0.95, 0.1 )
VGSF_val[2018] = u_float( 0.95, 0.1 )

WGSF_val = {}
WGSF_val[2016] = u_float( 0.83, 0.09 )
WGSF_val[2017] = u_float( 0.83, 0.09 )
WGSF_val[2018] = u_float( 0.83, 0.09 )

ZGSF_val = {}
ZGSF_val[2016] = u_float( 1.17, 0.16 )
ZGSF_val[2017] = u_float( 1.17, 0.16 )
ZGSF_val[2018] = u_float( 1.17, 0.16 )

# all processes are all samples + them splitted in photon categories
allProcesses            = copy.copy(default_sampleList)
allProcesses           += [ s+"_gen"   for s in default_sampleList ]
allProcesses           += [ s+"_misID" for s in default_sampleList ]
allProcesses           += [ s+"_had"   for s in default_sampleList ]

analysis_results = os.path.join( results_directory, "analysis" )
cache_dir        = os.path.join( cache_directory,   "analysis" )
jmeVariations    = ["jer", "jerUp", "jerDown", "jesTotalUp", "jesTotalDown"]
metVariations    = ["unclustEnUp", "unclustEnDown"]

# Control Regions Settings
controlRegions = {}
#hadronic fakes
controlRegions["fake3high"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1), "photonIso":"highSieie" },
                          "channels":   lepChannels,
                          "regions":    chgIsoPtRegions,
                          "inclRegion": chgIsoRegions,
                          "noPhotonCR": False,
                          "processes":  processes,
                         }

controlRegions["fake4phigh"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1), "photonIso":"highSieie" },
                          "channels":   lepChannels,
                          "regions":    chgIsoPtRegions,
                          "inclRegion": chgIsoRegions,
                          "noPhotonCR": False,
                          "processes":  processes,
                         }

controlRegions["fake3low"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1), "photonIso":"lowSieie" },
                          "channels":   lepChannels,
                          "regions":    chgIsoNoSRPtRegions,
                          "inclRegion": chgIsoNoSRRegions,
                          "noPhotonCR": False,
                          "processes":  processes,
                         }

controlRegions["fake4plow"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1), "photonIso":"lowSieie" },
                          "channels":   lepChannels,
                          "regions":    chgIsoNoSRPtRegions,
                          "inclRegion": chgIsoNoSRRegions,
                          "noPhotonCR": False,
                          "processes":  processes,
                         }

#controlRegions["SR3lowIso"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1), "photonIso":"lowChgIsohighSieie" },
#                                "channels":   lepChannels,
#                                "regions":    regionsTTGfake,
#                                "inclRegion": inclRegionsTTGfake,
#                                "noPhotonCR": False,
#                                "processes":  processes,
#                              }

#controlRegions["SR3highIso"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1), "photonIso":"highChgIsohighSieie" },
#                                 "channels":   lepChannels,
#                                 "regions":    regionsTTGfake,
#                                 "inclRegion": inclRegionsTTGfake,
#                                 "noPhotonCR": False,
#                                 "processes":  processes,
#                               }

#controlRegions["SR4plowIso"]  = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1), "photonIso":"lowChgIsohighSieie" },
#                                "channels":   lepChannels,
#                                "regions":    regionsTTGfake,
#                                "inclRegion": inclRegionsTTGfake,
#                                "noPhotonCR": False,
#                                "processes":  processes,
#                              }

#controlRegions["SR4phighIso"]  = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1), "photonIso":"highChgIsohighSieie" },
#                                 "channels":   lepChannels,
#                                 "regions":    regionsTTGfake,
#                                 "inclRegion": inclRegionsTTGfake,
#                                 "noPhotonCR": False,
#                                 "processes":  processes,
#                               }

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
controlRegions["TT3"]  = { "parameters": { "zWindow":"all", "nJet":(3,3),  "nBTag":(1,-1), "nPhoton":(0,0) },
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
controlRegions["WJets3"]  = { "parameters": { "zWindow":"all", "nJet":(3,3),  "nBTag":(0,0), "nPhoton":(0,0) },
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


# nPhoton1p nBTag0 offZeg m(e,gamma) CR for V+Gamma
controlRegions["VG2"]  = { "parameters": { "zWindow":"offZeg", "nJet":(2,2), "nBTag":(0,0), "nPhoton":(1,1) },
                           "channels":   lepChannels,
                           "regions":    mLgPtRegions,
                           "inclRegion": mLgRegions,
#                           "regions":    mLgPtRegions,
#                           "inclRegion": mLgRegions,
                           "noPhotonCR": False,
                           "processes":  processes,
                         }

controlRegions["VG3"]  = { "parameters": { "zWindow":"offZeg", "nJet":(3,3), "nBTag":(0,0), "nPhoton":(1,1) },
                           "channels":   lepChannels,
                           "regions":    mLgPtRegions,
                           "inclRegion": mLgRegions,
#                           "regions":    mLgPtRegions,
#                           "inclRegion": mLgRegions,
                           "noPhotonCR": False,
                           "processes":  processes,
                         }

controlRegions["VG4"]  = { "parameters": { "zWindow":"offZeg", "nJet":(4,4), "nBTag":(0,0), "nPhoton":(1,1) },
                           "channels":   lepChannels,
                           "regions":    mLgPtRegions,
                           "inclRegion": mLgRegions,
#                           "regions":    mLgPtRegions,
#                           "inclRegion": mLgRegions,
                           "noPhotonCR": False,
                           "processes":  processes,
                         }

controlRegions["VG5"]  = { "parameters": { "zWindow":"offZeg", "nJet":(5,5), "nBTag":(0,0), "nPhoton":(1,1) },
                           "channels":   lepChannels,
                           "regions":    mLgPtRegions,
                           "inclRegion": mLgRegions,
#                           "regions":    mLgPtRegions,
#                           "inclRegion": mLgRegions,
                           "noPhotonCR": False,
                           "processes":  processes,
                         }

controlRegions["VG4p"] = { "parameters": { "zWindow":"offZeg", "nJet":(4,-1), "nBTag":(0,0), "nPhoton":(1,1)  },
                           "channels":   lepChannels,
                           "regions":    mLgPtRegions,
                           "inclRegion": mLgRegions,
#                           "regions":    mLgPtRegions,
#                           "inclRegion": mLgRegions,
                           "noPhotonCR": False,
                           "processes":  processes,
                         }


# both VG + misID
controlRegions["VGmis3"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(0,0), "nPhoton":(1,1) },
                              "channels":   lepChannels,
                              "regions":    regionsTTG,
                              "inclRegion": inclRegionsTTG,
#                           "regions":    mLgPtRegions,
#                           "inclRegion": mLgRegions,
                              "noPhotonCR": False,
                              "processes":  processes,
                            }

controlRegions["VGmis4p"]  = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(0,0), "nPhoton":(1,1) },
                               "channels":   lepChannels,
                               "regions":    regionsTTG,
                               "inclRegion": inclRegionsTTG,
#                           "regions":    mLgPtRegions,
#                           "inclRegion": mLgRegions,
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

controlRegions["misDY3"]  = { "parameters": { "zWindow":"onZeg", "nJet":(3,3), "nBTag":(0,0), "nPhoton":(1,1) },
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


# nPhoton1p nBTag2 nJet2 offZeg m(e,gamma) CR for misID ScaleFactor TTbar
controlRegions["misTT2"] = { "parameters": { "zWindow":"offZeg", "nJet":(2,2), "nBTag":(2,2), "nPhoton":(1,1) },
                             "channels":   lepChannels,
                             "regions":    regionsTTG,
                             "inclRegion": inclRegionsTTG,
                             "noPhotonCR": False,
                             "processes":  processes,
                           }


# updates for QCD estimation (else same settings)
QCD_updates         = { "invertLepIso":True,               "nBTag":(0,0),               "addMisIDSF":True, "zWindow":"offZeg" }

QCDTF_updates       = {}
#QCDTF_updates["CR"] = { "invertLepIso":True, "nJet":(2,2), "nBTag":(0,0), "MET":(0,30), "addMisIDSF":True, "zWindow":"offZeg" }
#QCDTF_updates["SR"] = {                      "nJet":(2,2),                "MET":(0,30), "addMisIDSF":True }
QCDTF_updates["CR"] = { "invertLepIso":True, "nJet":(2,2), "nBTag":(0,0),               "addMisIDSF":True, "zWindow":"offZeg" }
QCDTF_updates["SR"] = {                      "nJet":(2,2),                              "addMisIDSF":True }

QCD_cutReplacements = {
                        "mLtight0Gamma":     "mLinvtight0Gamma",
}


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
