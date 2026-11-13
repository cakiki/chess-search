from lark.lexer import PatternStr

from chess_search.query.parser import parser

print("<x> required   [x] optional   newline = and\n")
for rule in parser.rules:
    if rule.origin.name not in ("expr", "predicate"):
        continue
    parts = []
    for sym in rule.expansion:
        term = parser.get_terminal(sym.name) if sym.is_term else None
        if term is not None and isinstance(term.pattern, PatternStr):
            parts.append(term.pattern.value)
        elif term is not None and term.pattern.value.startswith("(?:"):
            parts.append(f"<{'|'.join(sorted(term.pattern.value[3:-1].split('|')))}>")
        elif sym.name == "piece":
            parts.append("[<color>] <piece>")
        else:
            parts.append(f"<{sym.name.lower()}>")
    print(f"{rule.alias or rule.origin.name:14} {' '.join(parts).replace(' -', '-')}")
