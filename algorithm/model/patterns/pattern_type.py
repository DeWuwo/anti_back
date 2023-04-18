from typing import List
from algorithm.model.patterns.pattern_rules import PatternRules


class PatternType:
    ident: str
    patterns: list
    rules: List[PatternRules]

    def __init__(self, ident: str, patterns: list, rules: list):
        self.ident = ident
        self.patterns = patterns
        self.rules = rules
