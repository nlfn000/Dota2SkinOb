class Individualized:
    """
        basic individualize prototype.
        (the last man been fucked. XD
    """

    def __init__(self):
        self._indiv = {}

    def set(self, **kwargs):
        self._indiv.update(kwargs)

    def indiv(self, key):
        return self._indiv.get(key)
