"""Categorização de tokens: decide qual tipo de glifo cada token vira."""

import keyword

KEYWORDS = set(keyword.kwlist) | set(getattr(keyword, "softkwlist", []))

# Funções/tipos embutidos que ganham selo próprio. Qualquer outro nome vira runa.
COMMON_BUILTINS = {
    "print", "len", "range", "int", "str", "float", "bool", "list", "dict",
    "set", "tuple", "input", "type", "enumerate", "zip", "map", "filter",
    "open", "abs", "min", "max", "sum", "sorted", "reversed", "round", "any",
    "all", "isinstance", "issubclass", "super", "repr", "format", "ord", "chr",
    "hash", "iter", "next", "object", "bytes", "frozenset", "divmod", "pow",
    "vars", "dir", "getattr", "setattr", "hasattr", "callable", "id", "slice",
    "staticmethod", "classmethod", "property", "bytearray", "complex",
    "issubclass", "memoryview", "bin", "hex", "oct", "ascii", "globals", "locals",
}

# Nomes especiais de POO que ganham uma marca própria (não são keyword/builtin).
SPECIAL_NAMES = {"self", "cls"}

# Papel (semântica) de cada palavra-chave -> define a FORMA do selo.
ROLE_GROUPS = {
    "control": ["if", "elif", "else", "for", "while", "match", "case"],
    "definition": ["def", "class", "lambda", "async", "type"],
    "jump": ["return", "yield", "break", "continue", "pass", "raise", "await"],
    "value": ["True", "False", "None", "and", "or", "not", "is", "in"],
    "binding": ["import", "from", "as", "global", "nonlocal", "del"],
    "context": ["with", "try", "except", "finally", "assert"],
}
ROLE_LABELS = {
    "control": "controle de fluxo",
    "definition": "definição",
    "jump": "salto / fluxo",
    "value": "valor / lógica",
    "binding": "ligação / escopo",
    "context": "contexto / erro",
    "builtin": "função embutida",
    "function": "sua função",
    "class": "sua classe",
}
_KW_ROLE = {name: role for role, names in ROLE_GROUPS.items() for name in names}


def role_of_keyword(name):
    return _KW_ROLE.get(name, "value")


def is_dunder(name):
    return len(name) > 4 and name.startswith("__") and name.endswith("__")


def is_private(name):
    return name.startswith("_") and not is_dunder(name) and name not in ("_",)
