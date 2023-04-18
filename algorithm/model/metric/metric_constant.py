class MetricCons:
    Me_called: str = 'called_times'
    Me_access: str = 'access_metrics'
    Me_module: str = 'func_metrics'

    Me_stability: str = 'stability'
    Me_is_inherit: str = 'is_inherit'
    Me_is_implement: str = 'is_implement'
    Me_is_override: str = 'is_override'

    Me_native_used_frequency: str = 'native_used_frequency'
    Me_native_used_effectiveness: str = 'native_used_effectiveness'
    Me_extensive_used_frequency: str = 'extensive_used_frequency'
    Me_acceptable_hidden: str = 'acceptable_hidden'
    Me_unacceptable_non_hidden: str = 'unacceptable_non_hidden'
    Me_extensive_access_frequency: str = 'extensive_access_frequency'
    Me_native_access_frequency: str = 'native_access_frequency'
    Me_functional_similarity: str = 'functional_similarity'
    Me_inner_scale: str = 'inner_scale'
    Me_add_param: str = 'add_param'
    Me_avoid_cd: str = 'avoid_cd'
    Me_open_in_sdk: str = 'open_in_sdk'
    Me_destruction_of_access: str = 'destruction_of_access'
    Me_interface_number: str = 'interface_number'
    Me_anonymous_class: str = 'anonymous_class'
    Me_is_new_inherit: str = 'is_new_inherit'
    Me_is_new_implement: str = 'is_new_implement'
    Type_complex: list = ['String', 'int', 'boolean', 'byte', 'short', 'long', 'float', 'double', 'char']
    mc_rank = ['top_10', 'top_50', 'top_100', 'top_10%', 'top_25%', 'top_50%', 'top_100%']
    mc_rank_level = {'top_10': 0, 'top_50': 1, 'top_100': 2, 'top_10%': 3, 'top_25%': 4, 'top_50%': 5, 'top_100%': 6}
