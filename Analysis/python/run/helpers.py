import json

def chunks( l, n ):
    # split list in chuncs
    for i in range( 0, len(l), n ):
        yield l[i:i + n]

def splitList( l, n ):
    k, m = divmod(len(l), n)
    return list(l[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in xrange(n))

def uniqueKey( name, region, channel, setup ):
    sysForKey = setup.sys.copy()
    sysForKey["reweight"] = "TEMP"
    reweightKey = '["' + '", "'.join(sorted([i for i in setup.sys['reweight']])) + '"]' # little hack to preserve order of list when being dumped into json
    key = name, region, channel, json.dumps(sysForKey, sort_keys=True).replace('"TEMP"',reweightKey), json.dumps(setup.parameters, sort_keys=True), json.dumps(setup.lumi, sort_keys=True)
    return key

