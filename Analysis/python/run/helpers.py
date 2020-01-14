def chunks( l, n ):
    # split list in chuncs
    for i in range( 0, len(l), n ):
        yield l[i:i + n]

def splitList( l, n ):
    k, m = divmod(len(l), n)
    return list(l[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in xrange(n))

