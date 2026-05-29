"""Fluxo pseudo-aleatório determinístico.

A mesma chave (string) sempre produz a mesma sequência de números. É isso
que garante que o selo da palavra `if` seja idêntico toda vez que for gerado.
"""

import hashlib


class Stream:
    def __init__(self, key):
        self.key = str(key)
        self._buf = hashlib.sha256(self.key.encode("utf-8")).digest()
        self._i = 0
        self._round = 0

    def _byte(self):
        if self._i >= len(self._buf):
            self._round += 1
            self._buf = hashlib.sha256(f"{self.key}#{self._round}".encode("utf-8")).digest()
            self._i = 0
        b = self._buf[self._i]
        self._i += 1
        return b

    def rand(self):
        """float em [0, 1]."""
        return self._byte() / 255.0

    def randint(self, a, b):
        """inteiro em [a, b] (inclusivo)."""
        return a + self._byte() % (b - a + 1)

    def choice(self, seq):
        return seq[self._byte() % len(seq)]
