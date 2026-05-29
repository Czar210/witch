"""witch — traduz Python para os glifos mágicos de Witch Hat Atelier.

Cada token do Python vira um glifo SVG desenhado proceduralmente:
  - palavras-chave e funções  -> selos (círculos mágicos completos)
  - operadores                -> marcas
  - nomes, números, strings   -> runas (alfabeto)

Os glifos são determinísticos: o mesmo token gera sempre o mesmo desenho.
"""

__version__ = "0.1.0"
