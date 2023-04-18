from algorithm.model.patterns.pattern_type import PatternType
from algorithm.model.patterns.pattern_constant import PatternCons


class CouplingPattern(PatternType):
    def __init__(self):
        ident = 'coupling-patterns'
        patterns = [
            'IntrusiveModify',
            'FinalDel', 'AccessibilityModify',
            'HiddenApi',
            'ParameterListModifyDep',
            'InnerExtensionClassUseDep',
            'InheritExtension',
            'ImplementExtension',
            'AggregationExtensionInterfaceClassDep',

            'InheritanceNative',
            'ImplementNative',
            'AggregationAOSPClassDep',
            'PublicInterfaceUseDep',
            'ReflectUse'
        ]
        rules = [
            PatternCons.pattern_intrusive,
            PatternCons.pattern_final, PatternCons.pattern_access, PatternCons.pattern_hidden,
            PatternCons.pattern_param_modify, PatternCons.pattern_inner_class,
            PatternCons.pattern_inherit_extensive, PatternCons.pattern_implement_extensive,
            PatternCons.pattern_aggre_extensive,
            PatternCons.pattern_inherit_native,
            PatternCons.pattern_implement_native, PatternCons.pattern_aggre_native,
            PatternCons.pattern_public_interface, PatternCons.pattern_reflect
        ]

        PatternType.__init__(self, ident, patterns, rules)
