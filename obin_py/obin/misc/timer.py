class Timer(object):
    def __init__(self, msg, verbose=True):
        self.verbose = verbose
        self.msg = msg

    def __enter__(self):
        import time
        self.start = time.time()
        return self

    def __exit__(self, *args):
        import time
        self.end = time.time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        if self.verbose:
            print 'Timer %s elapsed time: %d sec %f ms' % (self.msg, self.secs, self.msecs)

