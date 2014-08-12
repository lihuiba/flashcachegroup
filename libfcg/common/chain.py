import threading


class Chain(object):
    def __init__(self):
        self._chain = []

    def add_step(self, do, undo):
        assert callable(do) and callable(undo), "%s and %s must be callable" % (do, undo)
        self._chain.append((do, undo))

    def do(self):
        for i in range(len(self._chain)):
            try:
                self._chain[i][0]()
            except Exception:
                i -= 1
                while i >= 0:
                    self._chain[i][1]()
                    i -= 1
                raise


class AtomicChain(Chain):
    def __init__(self, lock=None):
        if not lock:
            self._lock = threading.Lock()
        else:
            self._lock = lock
        super(AtomicChain, self).__init__()

    def do(self):
        with self._lock:
            super(AtomicChain, self).do()

if __name__ == "__main__":
    " Test and demostrate Chain itself "
    c = AtomicChain()
    def asdf(n): print(n)
    def qwer(n): raise OverflowError()
    c.add_step(lambda: asdf(1), lambda: asdf(-1))
    c.add_step(lambda: asdf(2), lambda: asdf(-2))
    c.add_step(lambda: qwer(3), lambda: asdf(-3))
    c.do()