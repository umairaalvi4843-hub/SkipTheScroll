"""Programmatic verbatim quote check. Whitespace-normalised substring match."""
import re

def normalise(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())

def verify_quote(quote: str, source: str) -> bool:
    if not quote or not source:
        return False
    return normalise(quote) in normalise(source)

def verify_all(clauses: list, source: str) -> list:
    for c in clauses:
        c["quote_verified"] = verify_quote(c.get("quote", ""), source)
    return clauses
