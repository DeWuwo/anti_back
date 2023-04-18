from typing import List, Dict


class RelationRule:
    src: dict
    dest: dict
    rel: dict
    direction: str

    def __init__(self, relation: dict):
        self.src = relation['src']
        self.rel = relation['rel']
        self.dest = relation['dest']
        self.direction = relation['direction']


class GraphRule:
    name: str
    rules: List[RelationRule]
    union_point: list
    union_edge: list
    metrics: dict
    metrics_filter: list

    def __init__(self, name, rules: List[dict], union_point, union_edge, metrics: dict, metrics_filter: List[dict]):
        self.name = name
        self.rules = []
        for rule in rules:
            self.rules.append(RelationRule(rule))
        self.union_point = union_point
        self.union_edge = union_edge
        self.metrics = metrics
        self.metrics_filter = metrics_filter


class PatternRules:
    name: str
    styles: List[GraphRule]

    def __init__(self, name, styles: Dict[str, dict]):
        self.name = name
        self.styles = []
        for style_name, style_rules in styles.items():
            self.styles.append(
                GraphRule(style_name, style_rules['rules'], style_rules['aggre'][0], style_rules['aggre'][1],
                          style_rules['metrics'], style_rules['metrics_filter']))
