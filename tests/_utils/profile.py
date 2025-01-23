import cProfile, pstats, io


def profile(fnc):
    """A decorator that uses cProfile to profile a function. https://osf.io/upav8"""

    def inner(*args, **kwargs):

        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = "cumulative"
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats(100)
        print(s.getvalue())
        return retval

    return inner
