"""Executor: roda o código (rodar os glifos = rodar o Python que eles traduzem)."""

import subprocess
import sys


def run_file(path):
    """Executa o arquivo .py num subprocesso, herdando stdin/stdout/stderr."""
    return subprocess.call([sys.executable, str(path)])
