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
TT_misID    = ["Top_misID"]
other_misID = ["WJets_misID","other_misID","WG_misID","ZG_misID"]
WG          = ["WG_gen"]
ZG          = ["ZG_gen"]
other       = ["other_gen","Top_gen","DY_LO_gen","WJets_gen"]
QCD         = ["QCD-DD"]
fakes       = ["DY_LO_had","Top_had","TTG_had","WG_had","ZG_had","other_had","WJets_had"]

default_sampleList            = ["TTG","Top","DY_LO","ZG","WG","WJets","other","QCD-DD"]
default_systematicList        = ["TTG_TuneUp","TTG_TuneDown","TTG_erdOn"]
default_photonSampleList      = signal + DY_misID + TT_misID + other_misID + WG + ZG + other + QCD + fakes + ["fakes-DD"]

processes = {
             "signal":      { "process":signal,      "color":color.TTG,          "texName":"tt#gamma (gen#gamma, misID)" },
             "DY_misID":    { "process":DY_misID,    "color":color.DY_misID,     "texName":"DY (misID)"            },
             "TT_misID":    { "process":TT_misID,    "color":color.TT_misID,     "texName":"t/tt (misID)"            },
             "other_misID": { "process":other_misID, "color":color.Other_misID,  "texName":"WJets+W#gamma+Z#gamma+other (misID)" },
             "WG":          { "process":WG,          "color":color.WGamma,       "texName":"W#gamma (gen#gamma)"    },
             "ZG":          { "process":ZG,          "color":color.ZGamma,       "texName":"Z#gamma (gen#gamma)"    },
             "other":       { "process":other,       "color":color.Other,        "texName":"t/tt+DY+WJets+other (gen#gamma)"      },
             "QCD":         { "process":QCD,         "color":color.QCD,          "texName":"multijets"             },
             "fakes":       { "process":fakes,       "color":color.fakes,        "texName":"non-prompt #gamma" },
}

processesSR = {
               "signal":      { "process":signal,       "color":color.TTG,          "texName":"tt#gamma (gen#gamma, misID)" },
               "DY_misID":    { "process":DY_misID,     "color":color.DY_misID,     "texName":"DY (misID)"            },
               "TT_misID":    { "process":TT_misID,     "color":color.TT_misID,     "texName":"t/tt (misID)"            },
               "other_misID": { "process":other_misID,  "color":color.Other_misID,  "texName":"WJets+W#gamma+Z#gamma+other (misID)" },
               "WG":          { "process":WG,           "color":color.WGamma,       "texName":"W#gamma (gen#gamma)"    },
               "ZG":          { "process":ZG,           "color":color.ZGamma,       "texName":"Z#gamma (gen#gamma)"    },
               "other":       { "process":other,        "color":color.Other,        "texName":"t/tt+DY+WJets+other (gen#gamma)"      },
               "QCD":         { "process":QCD,          "color":color.QCD,          "texName":"multijets"             },
               "fakes":       { "process":["fakes-DD"], "color":color.fakes,        "texName":"non-prompt #gamma" },
}

processesNoPhoton = {
                     "signal":      { "process":["TTG"],      "color":color.TTG,          "texName":"tt#gamma" },
                     "DY":          { "process":["DY_LO"],    "color":color.DY,           "texName":"DY"         },
                     "TT":          { "process":["Top"],      "color":color.TT,           "texName":"t/tt"     },
                     "WG":          { "process":["WG"],       "color":color.WGamma,       "texName":"W#gamma"    },
                     "ZG":          { "process":["ZG"],       "color":color.ZGamma,       "texName":"Z#gamma"    },
                     "WJets":       { "process":["WJets"],    "color":color.WJets,        "texName":"WJets"      },
                     "other":       { "process":["other"],    "color":color.Other,        "texName":"other"      },
                     "QCD":         { "process":QCD,          "color":color.QCD,          "texName":"multijets"             },
}

default_processes = {
             "signal":      { "process":["TTG"]+signal,  "color":color.TTG,          "texName":"tt#gamma (gen#gamma, misID)" },
             "DY":          { "process":["DY_LO"],       "color":color.DY,           "texName":"DY"        },
             "DY_misID":    { "process":DY_misID,        "color":color.DY_misID,     "texName":"DY (misID)"            },
             "TT":          { "process":["Top"],         "color":color.TT,           "texName":"t/tt"     },
             "TT_misID":    { "process":TT_misID,        "color":color.TT_misID,     "texName":"t/tt (misID)"            },
             "WG":          { "process":["WG"]+WG,       "color":color.WGamma,       "texName":"W#gamma (gen#gamma)"    },
             "ZG":          { "process":["ZG"]+ZG,       "color":color.ZGamma,       "texName":"Z#gamma (gen#gamma)"    },
             "WJets":       { "process":["WJets"],       "color":color.WJets,        "texName":"WJets (gen#gamma)"      },
             "other":       { "process":["other"]+other, "color":color.Other,        "texName":"t/tt+DY+WJets+other (gen#gamma)"      },
             "other_misID": { "process":other_misID,     "color":color.Other_misID,  "texName":"WJets+W#gamma+Z#gamma+other (misID)" },
             "QCD":         { "process":QCD,             "color":color.QCD,          "texName":"multijets"             },
             "fakes":       { "process":fakes,           "color":color.fakes,        "texName":"non-prompt #gamma" },
}

processesMisIDPOI = {
             "signal":      { "process":other_misID+TT_misID+DY_misID, "color":color.DY_misID,     "texName":"misID (tt+DY+V#gamma+other)" },
             "TTG":         { "process":signal,                        "color":color.TTG,          "texName":"tt#gamma (gen#gamma, misID)" },
             "DY_misID":    { "process":DY_misID,                      "color":color.DY_misID,     "texName":"DY (misID)"            },
             "TT_misID":    { "process":TT_misID,                      "color":color.TT_misID,     "texName":"t/tt (misID)"            },
             "WG":          { "process":WG,                            "color":color.WGamma,       "texName":"W#gamma (gen#gamma)"    },
             "ZG":          { "process":ZG,                            "color":color.ZGamma,       "texName":"Z#gamma (gen#gamma)"    },
             "other":       { "process":other,                         "color":color.Other,        "texName":"other (gen#gamma)"      },
             "other_misID": { "process":other_misID,                   "color":color.Other_misID,  "texName":"WJets+V#gamma+other (misID)" },
             "QCD":         { "process":QCD,                           "color":color.QCD,          "texName":"multijets"             },
             "fakes":       { "process":fakes,                         "color":color.fakes,        "texName":"non-prompt #gamma" },
}

processesDYPOI = {
                  "signal":      { "process":["DY_LO"],    "color":color.DY,           "texName":"DY"         },
                  "DY":          { "process":["TTG"],      "color":color.TTG,          "texName":"tt#gamma"   },
                  "TT":          { "process":["Top"],      "color":color.TT,           "texName":"t/tt"         },
                  "WG":          { "process":["WG"],       "color":color.WGamma,       "texName":"W#gamma"    },
                  "ZG":          { "process":["ZG"],       "color":color.ZGamma,       "texName":"Z#gamma"    },
                  "WJets":       { "process":["WJets"],    "color":color.WJets,        "texName":"WJets"      },
                  "other":       { "process":["other"],    "color":color.Other,        "texName":"other"      },
                  "QCD":         { "process":QCD,          "color":color.QCD,          "texName":"multijets"  },
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

signalRegions["SR3p"]  = { "parameters": { "zWindow":"all", "nJet":(3,-1), "nBTag":(1,-1), "nPhoton":(1,1) },
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
                                "processes":  processesSR,
                                "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood == 3 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                               }

signalRegions["SR4pUnfold"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1) },
                                "channels":   lepChannels,
                                "regions":    regionsTTGlooseUnfolding,
                                "inclRegion": inclRegionsTTGloose,
                                "noPhotonCR": False,
                                "processes":  processesSR,
                                "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood >= 4 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                               }

signalRegions["SR3EtaUnfold"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1) },
                                   "channels":   lepChannels,
                                   "regions":    regionsTTGlooseEtaUnfolding,
                                   "inclRegion": inclRegionsTTGloose,
                                   "noPhotonCR": False,
                                   "processes":  processesSR,
                                   "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood == 3 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                                  }

signalRegions["SR4pEtaUnfold"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1) },
                                   "channels":   lepChannels,
                                   "regions":    regionsTTGlooseEtaUnfolding,
                                   "inclRegion": inclRegionsTTGloose,
                                   "noPhotonCR": False,
                                   "processes":  processesSR,
                                   "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood >= 4 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                                  }

signalRegions["SR3M3"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1) },
                            "channels":   lepChannels,
                            "regions":    m3PtlooseRegions,
                            "inclRegion": m3Regions,
                            "noPhotonCR": False,
                            "processes":  processesSR,
                            "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood == 3 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                         }

signalRegions["SR3pM3"]  = { "parameters": { "zWindow":"all", "nJet":(3,-1), "nBTag":(1,-1), "nPhoton":(1,1) },
                            "channels":   lepChannels,
                            "regions":    m3PtlooseRegions,
                            "inclRegion": m3Regions,
                            "noPhotonCR": False,
                            "processes":  processesSR,
                            "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood >= 3 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                         }

signalRegions["SR4pM3"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1) },
                            "channels":   lepChannels,
                            "regions":    m3PtlooseRegions,
                            "inclRegion": m3Regions,
                            "noPhotonCR": False,
                            "processes":  processesSR,
                            "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood >= 4 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                         }

signalRegions["SR3Eta"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1) },
                             "channels":   lepChannels,
                             "regions":    regionsTTGlooseEta,
                             "inclRegion": inclRegionsTTGloose,
                             "noPhotonCR": False,
                             "processes":  processesSR,
                             "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood == 3 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                            }

signalRegions["SR4pEta"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1) },
                             "channels":   lepChannels,
                             "regions":    regionsTTGlooseEta,
                             "inclRegion": inclRegionsTTGloose,
                             "noPhotonCR": False,
                             "processes":  processesSR,
                             "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood >= 4 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                            }

signalRegions["SR3EtaFine"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1) },
                                 "channels":   lepChannels,
                                 "regions":    regionsTTGlooseEtaFine,
                                 "inclRegion": inclRegionsTTGloose,
                                 "noPhotonCR": False,
                                 "processes":  processesSR,
                                 "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood == 3 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                               }

signalRegions["SR4pEtaFine"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1) },
                                 "channels":   lepChannels,
                                 "regions":    regionsTTGlooseEtaFine,
                                 "inclRegion": inclRegionsTTGloose,
                                 "noPhotonCR": False,
                                 "processes":  processesSR,
                                 "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood >= 4 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                                }

signalRegions["SR3EtaM3"]  = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1) },
                               "channels":   lepChannels,
                               "regions":    m3EtaRegions,
                               "inclRegion": m3Regions,
                               "noPhotonCR": False,
                               "processes":  processesSR,
                               "lambda":     lambda event, sample: event.nPhotonGood == 1 and event.nJetGood == 3 and event.nBTagGood >= 1 and event.nLeptonTight == 1 and event.nLeptonVetoIsoCorr == 1,
                              }

signalRegions["SR4pEtaM3"] = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1) },
                               "channels":   lepChannels,
                               "regions":    m3EtaRegions,
                               "inclRegion": m3Regions,
                               "noPhotonCR": False,
                               "processes":  processesSR,
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
SSMSF_val[2016]    = u_float( 0.78, 0.08 ) #26012020
SSMSF_val[2017]    = u_float( 0.78, 0.08 ) #26012020
SSMSF_val[2018]    = u_float( 0.78, 0.08 ) #26012020
SSMSF_val["RunII"] = u_float( 0.78, 0.08 ) #26012020

WJetsSF_val = {}
WJetsSF_val[2016]    = u_float( 1.14, 0.13 )
WJetsSF_val[2017]    = u_float( 1.09, 0.13 )
WJetsSF_val[2018]    = u_float( 1.09, 0.13 )
WJetsSF_val["RunII"] = u_float( 1.09, 0.13 )

QCDSF_val = {}
QCDSF_val[2016]    = u_float( 1.45, 0.0 )
QCDSF_val[2017]    = u_float( 1.07, 0.0 )
QCDSF_val[2018]    = u_float( 1.35, 0.0 )
QCDSF_val["RunII"] = u_float( 1.35, 0.0 )

QCD2SF_val = {}
QCD2SF_val[2016]    = u_float( 1.21, 0.0 )
QCD2SF_val[2017]    = u_float( 1.28, 0.0 )
QCD2SF_val[2018]    = u_float( 0.95, 0.0 )
QCD2SF_val["RunII"] = u_float( 0.95, 0.0 )

QCD3SF_val = {}
QCD3SF_val[2016]    = u_float( 1.45, 0.0 )
QCD3SF_val[2017]    = u_float( 1.07, 0.0 )
QCD3SF_val[2018]    = u_float( 1.35, 0.0 )
QCD3SF_val["RunII"] = u_float( 1.35, 0.0 )

QCD4SF_val = {}
QCD4SF_val[2016]    = u_float( 1.26, 0.0 )
QCD4SF_val[2017]    = u_float( 0.70, 0.0 )
QCD4SF_val[2018]    = u_float( 1.16, 0.0 )
QCD4SF_val["RunII"] = u_float( 1.16, 0.0 )

QCD5SF_val = {}
QCD5SF_val[2016]    = u_float( 1.12, 0.0 )
QCD5SF_val[2017]    = u_float( 1.05, 0.0 )
QCD5SF_val[2018]    = u_float( 1.08, 0.0 )
QCD5SF_val["RunII"] = u_float( 1.08, 0.0 )

QCD2pSF_val = {}
QCD2pSF_val[2016]    = u_float( 1.28, 0.0 )
QCD2pSF_val[2017]    = u_float( 1.20, 0.0 )
QCD2pSF_val[2018]    = u_float( 0.73, 0.0 ) #
QCD2pSF_val["RunII"] = u_float( 0.73, 0.0 ) #

QCD3pSF_val = {}
QCD3pSF_val[2016]    = u_float( 1.50, 0.0 )
QCD3pSF_val[2017]    = u_float( 1.08, 0.0 )
QCD3pSF_val[2018]    = u_float( 1.32, 0.0 )
QCD3pSF_val["RunII"] = u_float( 1.32, 0.0 )

QCD4pSF_val = {}
QCD4pSF_val[2016]    = u_float( 1.39, 0.0 )
QCD4pSF_val[2017]    = u_float( 0.93, 0.0 )
QCD4pSF_val[2018]    = u_float( 1.34, 0.0 )
QCD4pSF_val["RunII"] = u_float( 1.34, 0.0 )

# SF with systematics, pull from JEC
DYSF_val = {}
DYSF_val[2016]    = u_float( 1.20, 0.09 )
DYSF_val[2017]    = u_float( 1.17, 0.12 )
DYSF_val[2018]    = u_float( 1.14, 0.12 )
DYSF_val["RunII"] = u_float( 1.14, 0.12 )

DY2SF_val = {}
DY2SF_val[2016]    = u_float( 1.18, 0.07 )
DY2SF_val[2017]    = u_float( 1.16, 0.09 )
DY2SF_val[2018]    = u_float( 1.16, 0.10 )
DY2SF_val["RunII"] = u_float( 1.16, 0.10 )

DY3SF_val = {}
DY3SF_val[2016]    = u_float( 1.20, 0.08 )
DY3SF_val[2017]    = u_float( 1.17, 0.12 )
DY3SF_val[2018]    = u_float( 1.14, 0.12 )
DY3SF_val["RunII"] = u_float( 1.14, 0.12 )

DY4SF_val = {}
DY4SF_val[2016]    = u_float( 1.08, 0.09 )
DY4SF_val[2017]    = u_float( 1.12, 0.12 )
DY4SF_val[2018]    = u_float( 1.08, 0.13 )
DY4SF_val["RunII"] = u_float( 1.08, 0.13 )

DY5SF_val = {}
DY5SF_val[2016]    = u_float( 1.01, 0.10 )
DY5SF_val[2017]    = u_float( 1.19, 0.16 )
DY5SF_val[2018]    = u_float( 1.13, 0.17 )
DY5SF_val["RunII"] = u_float( 1.13, 0.17 )

DY2pSF_val = {}
DY2pSF_val[2016]    = u_float( 1.18, 0.08 )
DY2pSF_val[2017]    = u_float( 1.16, 0.10 )
DY2pSF_val[2018]    = u_float( 1.16, 0.10 )
DY2pSF_val["RunII"] = u_float( 1.16, 0.10 )

DY3pSF_val = {}
DY3pSF_val[2016]    = u_float( 1.17, 0.09 )
DY3pSF_val[2017]    = u_float( 1.16, 0.12 )
DY3pSF_val[2018]    = u_float( 1.13, 0.12 )
DY3pSF_val["RunII"] = u_float( 1.13, 0.12 )

DY4pSF_val = {}
DY4pSF_val[2016]    = u_float( 1.07, 0.09 )
DY4pSF_val[2017]    = u_float( 1.14, 0.13 )
DY4pSF_val[2018]    = u_float( 1.09, 0.14 )
DY4pSF_val["RunII"] = u_float( 1.09, 0.14 )




misIDSF_val = {}
misIDSF_val[2016]    = u_float( 2.23, 0.39 )
misIDSF_val[2017]    = u_float( 2.60, 0.50 )
misIDSF_val[2018]    = u_float( 1.55, 0.27 )

misID2SF_val = {}
misID2SF_val[2016]    = u_float( 2.32, 0.35 )
misID2SF_val[2017]    = u_float( 2.90, 0.50 )
misID2SF_val[2018]    = u_float( 1.62, 0.24 )

misID3SF_val = {}
misID3SF_val[2016]    = u_float( 2.23, 0.39 )
misID3SF_val[2017]    = u_float( 2.60, 0.50 )
misID3SF_val[2018]    = u_float( 1.55, 0.27 )

misID4SF_val = {}
misID4SF_val[2016]    = u_float( 1.93, 0.40 )
misID4SF_val[2017]    = u_float( 3.20, 1.00 )
misID4SF_val[2018]    = u_float( 1.80, 0.41 )

misID5SF_val = {}
misID5SF_val[2016]    = u_float( 1.50, 1.00 )
misID5SF_val[2017]    = u_float( 2.10, 1.40 )
misID5SF_val[2018]    = u_float( 1.10, 0.60 )

misID2pSF_val = {}
misID2pSF_val[2016]    = u_float( 2.27, 0.33 ) #
misID2pSF_val[2017]    = u_float( 3.10, 0.50 )
misID2pSF_val[2018]    = u_float( 1.50, 0.23 ) #

misID3pSF_val = {}
misID3pSF_val[2016]    = u_float( 2.14, 0.36 )
misID3pSF_val[2017]    = u_float( 2.80, 0.50 )
misID3pSF_val[2018]    = u_float( 1.61, 0.28 )

misID4pSF_val = {}
misID4pSF_val[2016]    = u_float( 1.93, 0.38 )
misID4pSF_val[2017]    = u_float( 3.00, 0.90 )
misID4pSF_val[2018]    = u_float( 1.78, 0.41 )

WGSF_val = {}
WGSF_val[2016]    = u_float( 0.98, 0.15 )
WGSF_val[2017]    = u_float( 1.17, 0.16 )
WGSF_val[2018]    = u_float( 1.09, 0.21 )
WGSF_val["RunII"] = u_float( 1.09, 0.21 )

WG2SF_val = {}
WG2SF_val[2016]    = u_float( 1.14, 0.10 )
WG2SF_val[2017]    = u_float( 1.08, 0.10 )
WG2SF_val[2018]    = u_float( 1.07, 0.14 )
WG2SF_val["RunII"] = u_float( 1.07, 0.14 )

WG3SF_val = {}
WG3SF_val[2016]    = u_float( 0.98, 0.15 )
WG3SF_val[2017]    = u_float( 1.17, 0.16 )
WG3SF_val[2018]    = u_float( 1.09, 0.21 )
WG3SF_val["RunII"] = u_float( 1.09, 0.21 )

WG4SF_val = {}
WG4SF_val[2016]    = u_float( 1.16, 0.19 )
WG4SF_val[2017]    = u_float( 1.38, 0.27 )
WG4SF_val[2018]    = u_float( 1.11, 0.29 )
WG4SF_val["RunII"] = u_float( 1.11, 0.29 )

WG5SF_val = {}
WG5SF_val[2016]    = u_float( 1.18, 0.38 )
WG5SF_val[2017]    = u_float( 1.70, 0.4 )
WG5SF_val[2018]    = u_float( 1.37, 0.42 )
WG5SF_val["RunII"] = u_float( 1.37, 0.42 )

WG2pSF_val = {}
WG2pSF_val[2016]    = u_float( 1.14, 0.10 ) #
WG2pSF_val[2017]    = u_float( 1.16, 0.10 )
WG2pSF_val[2018]    = u_float( 1.23, 0.22 ) #
WG2pSF_val["RunII"] = u_float( 1.23, 0.22 ) #

WG3pSF_val = {}
WG3pSF_val[2016]    = u_float( 1.02, 0.14 )
WG3pSF_val[2017]    = u_float( 1.26, 0.16 )
WG3pSF_val[2018]    = u_float( 1.18, 0.22 )
WG3pSF_val["RunII"] = u_float( 1.18, 0.22 )

WG4pSF_val = {}
WG4pSF_val[2016]    = u_float( 1.17, 0.20 )
WG4pSF_val[2017]    = u_float( 1.44, 0.28 )
WG4pSF_val[2018]    = u_float( 1.31, 0.30 )
WG4pSF_val["RunII"] = u_float( 1.31, 0.30 )

ZGSF_val = {}
ZGSF_val[2016]    = u_float( 1.08, 0.0 )
ZGSF_val[2017]    = u_float( 0.94, 0.0 )
ZGSF_val[2018]    = u_float( 1.05, 0.0 )
ZGSF_val["RunII"] = u_float( 1.05, 0.0 )

ZG2SF_val = {}
ZG2SF_val[2016]    = u_float( 0.91, 0.0 )
ZG2SF_val[2017]    = u_float( 0.91, 0. )
ZG2SF_val[2018]    = u_float( 1.01, 0.0 )
ZG2SF_val["RunII"] = u_float( 1.01, 0.0 )

ZG3SF_val = {}
ZG3SF_val[2016]    = u_float( 1.08, 0.0 )
ZG3SF_val[2017]    = u_float( 0.94, 0.0 )
ZG3SF_val[2018]    = u_float( 1.05, 0.0 )
ZG3SF_val["RunII"] = u_float( 1.05, 0.0 )

ZG4SF_val = {}
ZG4SF_val[2016]    = u_float( 1.10, 0.0 )
ZG4SF_val[2017]    = u_float( 1.04, 0.0 )
ZG4SF_val[2018]    = u_float( 1.12, 0.0 )
ZG4SF_val["RunII"] = u_float( 1.12, 0.0 )

ZG5SF_val = {}
ZG5SF_val[2016]    = u_float( 1.02, 0.0 )
ZG5SF_val[2017]    = u_float( 1.07, 0.0 )
ZG5SF_val[2018]    = u_float( 1.03, 0.0)
ZG5SF_val["RunII"] = u_float( 1.03, 0.0)

ZG2pSF_val = {}
ZG2pSF_val[2016]    = u_float( 0.93, 0. ) #
ZG2pSF_val[2017]    = u_float( 0.95, 0. )
ZG2pSF_val[2018]    = u_float( 1.00, 0. ) #
ZG2pSF_val["RunII"] = u_float( 1.00, 0. ) #

ZG3pSF_val = {}
ZG3pSF_val[2016]    = u_float( 1.10, 0.0 )
ZG3pSF_val[2017]    = u_float( 1.02, 0.0 )
ZG3pSF_val[2018]    = u_float( 1.08, 0.0 )
ZG3pSF_val["RunII"] = u_float( 1.08, 0.0 )

ZG4pSF_val = {}
ZG4pSF_val[2016]    = u_float( 1.11, 0.0 )
ZG4pSF_val[2017]    = u_float( 1.08, 0.0 )
ZG4pSF_val[2018]    = u_float( 1.06, 0.0 )
ZG4pSF_val["RunII"] = u_float( 1.06, 0.0 )

# all processes are all samples + them splitted in photon categories
allProcesses            = copy.copy(default_sampleList)
allProcesses           += [ s+"_gen"   for s in default_sampleList if not "DD" in s ]
allProcesses           += [ s+"_misID" for s in default_sampleList if not "DD" in s ]
allProcesses           += [ s+"_had"   for s in default_sampleList if not "DD" in s ]
allProcesses           += [ s+"_hp"    for s in default_sampleList if not "DD" in s ]
allProcesses           += [ s+"_fake"  for s in default_sampleList if not "DD" in s ]
allProcesses           += [ s+"_PU"    for s in default_sampleList if not "DD" in s ]
allProcesses           += [ s+"_np"    for s in default_sampleList if not "DD" in s ]
allProcesses           += [ "fakes-DD" ]

analysis_results = os.path.join( results_directory, "analysis" )
cache_dir        = os.path.join( cache_directory,   "analysis" )
jmeVariations    = ["jer", "jerUp", "jerDown", "jesTotalUp", "jesTotalDown"]
metVariations    = ["unclustEnUp", "unclustEnDown"]
eVariations      = ["eTotalUp", "eTotalDown"]
muVariations     = ["muTotalUp", "muTotalDown"]

# Control Regions Settings
controlRegions = {}
#hadronic fakes

controlRegions["fake2"]     = { "parameters": { "zWindow":"all", "nJet":(2,2), "nBTag":(1,-1), "nPhoton":(1,1), "photonIso":"noChgIsoNoSieie" },
                                 "channels":   lepChannels,
                                 "regions":    chgIsoPtRegions,
                                 "inclRegion": chgIsoRegions,
                                 "noPhotonCR": False,
                                 "processes":  processes,
                               }
 
controlRegions["fake3"]     = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1), "photonIso":"noChgIsoNoSieie" },
                                 "channels":   lepChannels,
                                 "regions":    chgIsoPtRegions,
                                 "inclRegion": chgIsoRegions,
                                 "noPhotonCR": False,
                                 "processes":  processes,
                               }
 
controlRegions["fakeHS3"]     = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(1,-1), "nPhoton":(1,1), "photonIso":"highSieie" },
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
 
controlRegions["fake4"]     = { "parameters": { "zWindow":"all", "nJet":(4,4), "nBTag":(1,-1), "nPhoton":(1,1), "photonIso":"noChgIsoNoSieie" },
                                 "channels":   lepChannels,
                                 "regions":    chgIsoPtRegions,
                                 "inclRegion": chgIsoRegions,
                                 "noPhotonCR": False,
                                 "processes":  processes,
                               }
 
controlRegions["fake5"]     = { "parameters": { "zWindow":"all", "nJet":(5,5), "nBTag":(1,-1), "nPhoton":(1,1), "photonIso":"noChgIsoNoSieie" },
                                 "channels":   lepChannels,
                                 "regions":    chgIsoPtRegions,
                                 "inclRegion": chgIsoRegions,
                                 "noPhotonCR": False,
                                 "processes":  processes,
                               }
 
controlRegions["fake3p"]     = { "parameters": { "zWindow":"all", "nJet":(3,-1), "nBTag":(1,-1), "nPhoton":(1,1), "photonIso":"noChgIsoNoSieie" },
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
 
controlRegions["fakeHS4p"]     = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(1,-1), "nPhoton":(1,1), "photonIso":"highSieie" },
                                 "channels":   lepChannels,
                                 "regions":    chgIsoPtRegions,
                                 "inclRegion": chgIsoRegions,
                                 "noPhotonCR": False,
                                 "processes":  processes,
                               }
 
controlRegions["VGfake3"]     = { "parameters": { "zWindow":"offZeg", "nJet":(3,3), "nBTag":(0,0), "nPhoton":(1,1), "photonIso":"noChgIsoNoSieie" },
                                 "channels":   lepChannels,
                                 "regions":    chgIsoPtRegions,
                                 "inclRegion": chgIsoRegions,
                                 "noPhotonCR": False,
                                 "processes":  processes,
                               }
 
controlRegions["VGfake3p"]     = { "parameters": { "zWindow":"offZeg", "nJet":(3,-1), "nBTag":(0,0), "nPhoton":(1,1), "photonIso":"noChgIsoNoSieie" },
                                 "channels":   lepChannels,
                                 "regions":    chgIsoPtRegions,
                                 "inclRegion": chgIsoRegions,
                                 "noPhotonCR": False,
                                 "processes":  processes,
                               }
 
controlRegions["VGfake4p"]     = { "parameters": { "zWindow":"offZeg", "nJet":(4,-1), "nBTag":(0,0), "nPhoton":(1,1), "photonIso":"noChgIsoNoSieie" },
                                 "channels":   lepChannels,
                                 "regions":    chgIsoPtRegions,
                                 "inclRegion": chgIsoRegions,
                                 "noPhotonCR": False,
                                 "processes":  processes,
                               }
 
controlRegions["VGmisfake3"]     = { "parameters": { "zWindow":"all", "nJet":(3,3), "nBTag":(0,0), "nPhoton":(1,1), "photonIso":"noChgIsoNoSieie" },
                                 "channels":   lepChannels,
                                 "regions":    chgIsoPtRegions,
                                 "inclRegion": chgIsoRegions,
                                 "noPhotonCR": False,
                                 "processes":  processes,
                               }
 
controlRegions["VGmisfake3p"]     = { "parameters": { "zWindow":"all", "nJet":(3,-1), "nBTag":(0,0), "nPhoton":(1,1), "photonIso":"noChgIsoNoSieie" },
                                 "channels":   lepChannels,
                                 "regions":    chgIsoPtRegions,
                                 "inclRegion": chgIsoRegions,
                                 "noPhotonCR": False,
                                 "processes":  processes,
                               }
 
controlRegions["VGmisfake4p"]     = { "parameters": { "zWindow":"all", "nJet":(4,-1), "nBTag":(0,0), "nPhoton":(1,1), "photonIso":"noChgIsoNoSieie" },
                                 "channels":   lepChannels,
                                 "regions":    chgIsoPtRegions,
                                 "inclRegion": chgIsoRegions,
                                 "noPhotonCR": False,
                                 "processes":  processes,
                               }
 
controlRegions["misfake3"]     = { "parameters": { "zWindow":"onZeg", "nJet":(3,3), "nBTag":(0,0), "nPhoton":(1,1), "photonIso":"noChgIsoNoSieie" },
                                 "channels":   lepChannels,
                                 "regions":    chgIsoPtRegions,
                                 "inclRegion": chgIsoRegions,
                                 "noPhotonCR": False,
                                 "processes":  processes,
                               }
 
controlRegions["misfake3p"]     = { "parameters": { "zWindow":"onZeg", "nJet":(3,-1), "nBTag":(0,0), "nPhoton":(1,1), "photonIso":"noChgIsoNoSieie" },
                                 "channels":   lepChannels,
                                 "regions":    chgIsoPtRegions,
                                 "inclRegion": chgIsoRegions,
                                 "noPhotonCR": False,
                                 "processes":  processes,
                               }
 
controlRegions["misfake4p"]     = { "parameters": { "zWindow":"onZeg", "nJet":(4,-1), "nBTag":(0,0), "nPhoton":(1,1), "photonIso":"noChgIsoNoSieie" },
                                 "channels":   lepChannels,
                                 "regions":    chgIsoPtRegions,
                                 "inclRegion": chgIsoRegions,
                                 "noPhotonCR": False,
                                 "processes":  processes,
                               }
 
controlRegions["DLfake3"]  = { "parameters": { "dileptonic":True, "zWindow":"onZSFllTight", "nJet":(3,3),  "nBTag":(0,0), "nPhoton":(1,1) },
                                "channels":   dilepChannels,
                                "regions":    regionsTTG,
                                "inclRegion": inclRegionsTTG,
                                "noPhotonCR": False,
                                "processes":  processes,
                              }
                            
controlRegions["DLfake3p"]  = { "parameters": { "dileptonic":True, "zWindow":"onZSFllTight", "nJet":(3,-1),  "nBTag":(0,0), "nPhoton":(1,1) },
                                "channels":   dilepChannels,
                                "regions":    regionsTTG,
                                "inclRegion": inclRegionsTTG,
                                "noPhotonCR": False,
                                "processes":  processes,
                              }
                            
controlRegions["DLfake4p"]  = { "parameters": { "dileptonic":True, "zWindow":"onZSFllTight", "nJet":(4,-1),  "nBTag":(0,0), "nPhoton":(1,1) },
                                "channels":   dilepChannels,
                                "regions":    regionsTTG,
                                "inclRegion": inclRegionsTTG,
                                "noPhotonCR": False,
                                "processes":  processes,
                              }
                            

# dileptonic ee/mumu all m(l,l) nBTag0 nPhoton0 CR for DY ScaleFactor
controlRegions["DY2"]  = { "parameters": { "dileptonic":True, "zWindow":"onZSFllTight", "nJet":(2,2),  "nBTag":(0,0), "nPhoton":(0,0) },
                           "channels":   ["SFtight"],
                           "regions":    noPhotonRegionTTG,
                           "inclRegion": noPhotonRegionTTG,
                           "noPhotonCR": True,
                           "processes":  processesNoPhoton,
                         }
                            
controlRegions["DY2p"]  = { "parameters": { "dileptonic":True, "zWindow":"onZSFllTight", "nJet":(2,-1),  "nBTag":(0,0), "nPhoton":(0,0) },
                           "channels":   ["SFtight"],
                           "regions":    noPhotonRegionTTG,
                           "inclRegion": noPhotonRegionTTG,
                           "noPhotonCR": True,
                           "processes":  processesNoPhoton,
                         }
                            
controlRegions["DY3"]  = { "parameters": { "dileptonic":True, "zWindow":"onZSFllTight", "nJet":(3,3),  "nBTag":(0,0), "nPhoton":(0,0) },
                           "channels":   ["SFtight"],
                           "regions":    noPhotonRegionTTG,
                           "inclRegion": noPhotonRegionTTG,
                           "noPhotonCR": True,
                           "processes":  processesNoPhoton,
                         }

controlRegions["DY3p"]  = { "parameters": { "dileptonic":True, "zWindow":"onZSFllTight", "nJet":(3,-1),  "nBTag":(0,0), "nPhoton":(0,0) },
                           "channels":   ["SFtight"],
                           "regions":    noPhotonRegionTTG,
                           "inclRegion": noPhotonRegionTTG,
                           "noPhotonCR": True,
                           "processes":  processesNoPhoton,
                         }

controlRegions["DY4"]  = { "parameters":{"dileptonic":True, "zWindow":"onZSFllTight", "nJet":(4,4),  "nBTag":(0,0), "nPhoton":(0,0) },
                           "channels":   ["SFtight"],
                           "regions":    noPhotonRegionTTG,
                           "inclRegion": noPhotonRegionTTG,
                           "noPhotonCR": True,
                           "processes":  processesNoPhoton,
                         }

controlRegions["DY5"]  = { "parameters": { "dileptonic":True, "zWindow":"onZSFllTight", "nJet":(5,5),  "nBTag":(0,0), "nPhoton":(0,0) },
                           "channels":   ["SFtight"],
                           "regions":    noPhotonRegionTTG,
                           "inclRegion": noPhotonRegionTTG,
                           "noPhotonCR": True,
                           "processes":  processesNoPhoton,
                         }

controlRegions["DY4p"] = { "parameters": { "dileptonic":True, "zWindow":"onZSFllTight", "nJet":(4,-1), "nBTag":(0,0), "nPhoton":(0,0) },
                           "channels":   ["SFtight"],
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

controlRegions["VG3p"]  = { "parameters": { "zWindow":"offZeg", "nJet":(3,-1), "nBTag":(0,0), "nPhoton":(1,1) },
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

controlRegions["misDY3p"]  = { "parameters": { "zWindow":"onZeg", "nJet":(3,-1), "nBTag":(0,0), "nPhoton":(1,1) },
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
controlRegions["misTT2"] = { "parameters": { "zWindow":"all", "nJet":(2,2), "nBTag":(2,2), "nPhoton":(1,1) },
                             "channels":   lepChannels,
                             "regions":    regionsTTG,
                             "inclRegion": inclRegionsTTG,
                             "noPhotonCR": False,
                             "processes":  processes,
                           }

controlRegions["misTT1"] = { "parameters": { "zWindow":"all", "nJet":(2,2), "nBTag":(1,1), "nPhoton":(1,1) },
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

pCR = [ key for key, val in controlRegions.items() if not val["noPhotonCR"] and not "fake" in key]
pCR.sort()
limitOrdering += pCR

pCRfake = [ key for key, val in controlRegions.items() if not val["noPhotonCR"] and "fake" in key]
pCRfake.sort()
limitOrdering += pCRfake

noPCR = [ key for key, val in allRegions.items() if val["noPhotonCR"] ]
noPCR.sort()
limitOrdering += noPCR

pSR = [ key for key, val in signalRegions.items() ]
pSR.sort()
limitOrdering += pSR


# EFT parameter ranges:
# 30 bins from -1.5 to 1.5 + the SM value 0, calc value in the middle of the bin
xRange       = np.linspace( -1.5, 1.5, 30, endpoint=False)
halfstepsize = 0.5 * ( xRange[1] - xRange[0] )
xRange       = [ round(el + halfstepsize, 3) for el in xRange ] + [0]
xRange.sort()

eftParameterRange = {}
eftParameterRange["ctZ"]  = xRange
eftParameterRange["ctZI"] = xRange
#print xRange

