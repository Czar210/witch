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


def is_dunder(name):
    return len(name) > 4 and name.startswith("__") and name.endswith("__")


def is_private(name):
    return name.startswith("_") and not is_dunder(name) and name not in ("_",)
