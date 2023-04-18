class PatternType:
    ident: str
    patterns: list
    rules: list
    filter_list: list

    def __init__(self, ident: str, patterns: list, rules: list, filter_list: list):
        self.ident = ident
        self.patterns = patterns
        self.rules = rules
        self.filter_list = filter_list
