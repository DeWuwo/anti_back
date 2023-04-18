from algorithm.model.patterns.pattern_rules import PatternRules
from algorithm.utils import Constant
from algorithm.model.metric.metric_constant import MetricCons

filter_list = ['android.util', 'android.os.Message', 'com.android.internal.logging',
               'com.android.internal.os', 'android.os', 'com.android.server.utils',
               'hihonor.android.utils', 'android.os.ServiceManager', 'com.android.server.LocalServices',
               'android.provider.Settings.Secure', 'android.provider.Settings.System',
               'com.android.telephony.Rlog']


class PatternCons:
    pattern_intrusive = PatternRules('IntrusiveModify', {
        'class_intrusive_add_method': {
            'aggre': [[1, 0], [0]],
            'metrics': {MetricCons.Me_stability: [0, 0]},
            'metrics_filter': [],
            'rules': [
                {
                    'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {'intrusive': True}},
                    'rel': {'type': Constant.define, 'attrs': {}},
                    'dest': {'id': [-1], 'category': Constant.E_method,
                             'attrs': {}, 'filter': {}},
                    'direction': '01'
                }
            ]
        },
        'method_intrusive': {
            'aggre': [[], []],
            'metrics': {MetricCons.Me_stability: [0, 0]},
            'metrics_filter': [],
            'rules': [
                {
                    'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {'intrusive': True}},
                    'rel': {'type': Constant.define, 'attrs': {}},
                    'dest': {'id': [-1], 'category': Constant.E_method,
                             'attrs': {'intrusive': True}, 'filter': {}},
                    'direction': '00'
                }
            ]
        },
    })
    pattern_final = PatternRules(
        'FinalDel',
        {
            'del_class_final_for_inherit': {
                'aggre': [[], []],
                'metrics': {MetricCons.Me_is_inherit: [0, 1], MetricCons.Me_stability: [0, 1]},
                'metrics_filter': [],
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_file,
                                'attrs': {}},
                        'rel': {'type': Constant.contain, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_class,
                                 'attrs': {'final': True, 'intrusive': True}},
                        'direction': '00'
                    }
                ]
            },
            'del_method_final_for_override': {
                'aggre': [[], []],
                'metrics': {MetricCons.Me_is_override: [0, 1], MetricCons.Me_stability: [0, 1]},
                'metrics_filter': [],
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class,
                                'attrs': {}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_method,
                                 'attrs': {'final': True, 'intrusive': True}},
                        'direction': '00'
                    },
                ]},
            'del_class_final_for_var': {
                'aggre': [[1, 0], [0]],
                'metrics': {MetricCons.Me_is_inherit: [0, 0], MetricCons.Me_stability: [0, 0],
                            MetricCons.Me_interface_number: [0, 0]},
                'metrics_filter': [],
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class,
                                'attrs': {'final': True, 'intrusive': True}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_variable,
                                 'attrs': {'final': True, 'intrusive': True}},
                        'direction': '00'
                    },
                ]
            },
            'del_class_final_for_inherit_and_override': {
                'aggre': [[1, 1, 0, 0, 0, 0, 0, 0], [1, 2, 3]],
                'metrics': {MetricCons.Me_stability: [0, 1], MetricCons.Me_extensive_access_frequency: [2, 1]},
                'metrics_filter': [],
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class,
                                'attrs': {}},
                        'rel': {'type': Constant.inherit, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_class,
                                 'attrs': {'final': True, 'intrusive': True}},
                        'direction': '10'
                    },
                    {
                        'src': {'id': ['id', 0, 0], 'category': Constant.E_class,
                                'attrs': {}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_method,
                                 'attrs': {}},
                        'direction': '11'
                    },
                    {
                        'src': {'id': ['id', 1, 1], 'category': Constant.E_method,
                                'attrs': {}},
                        'rel': {'type': Constant.override, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_method,
                                 'attrs': {}},
                        'direction': '10'
                    },
                    {
                        'src': {'id': ['id', 0, 1], 'category': Constant.E_class,
                                'attrs': {}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': ['id', 2, 1], 'category': Constant.E_method,
                                 'attrs': {}},
                        'direction': '00'
                    },
                ]
            },
            # 'del_method_final_for_var': {
            #     'metrics': {},
            #     'metrics_filter': [],
            #     'rules': [
            #         {
            #             'src': {'id': [-1], 'category': Constant.E_method,
            #                     'attrs': {'final': True, 'intrusive': True}},
            #             'rel': {'type': Constant.define, 'attrs': {}},
            #             'dest': {'id': [-1], 'category': Constant.E_variable,
            #                      'attrs': {'final': True, 'intrusive': True}},
            #             'direction': '00'
            #         },
            #     ]
            # }
        })

    pattern_access = PatternRules('AccessibilityModify', {
        'class_access_modify': {
            'aggre': [[], []],
            'metrics': {MetricCons.Me_native_used_frequency: [0, 1], MetricCons.Me_stability: [0, 1]},
            'metrics_filter': [{MetricCons.Me_native_used_frequency: [0, 1]}],
            'rules': [
                {
                    'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                    'rel': {'type': Constant.define, 'attrs': {}},
                    'dest': {'id': [-1], 'category': Constant.E_class,
                             'attrs': {'accessible_up': True, 'intrusive': True},
                             'filter': {}},
                    'direction': '00'
                }
            ]
        },
        'method_access_modify': {
            'aggre': [[], []],
            'metrics': {MetricCons.Me_native_used_frequency: [0, 1], MetricCons.Me_native_used_effectiveness: [0, 1],
                        MetricCons.Me_stability: [0, 1]},
            'metrics_filter': [
                {MetricCons.Me_native_used_frequency: [0, 1], MetricCons.Me_native_used_effectiveness: [0, 1]}],
            'rules': [
                {
                    'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                    'rel': {'type': Constant.define, 'attrs': {}},
                    'dest': {'id': [-1], 'category': Constant.E_method,
                             'attrs': {'accessible_up': True, 'intrusive': True},
                             'filter': {}},
                    'direction': '00'
                },
            ]
        }
    })

    pattern_hidden = PatternRules(
        'HiddenApi', {
            'call_method': {
                'aggre': [[1, 0], [0]],
                'metrics': {MetricCons.Me_acceptable_hidden: [0, 1], MetricCons.Me_stability: [0, 1]},
                'metrics_filter': [{MetricCons.Me_acceptable_hidden: [0, 1]}],
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_method,
                                'attrs': {}},
                        'rel': {'type': Constant.call, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_method,
                                 'attrs': {'hidden': [Constant.HD_blacklist,
                                                      Constant.HD_greylist] + Constant.HD_greylist_max_list},
                                 'filter': {'qualified_name': filter_list}},
                        'direction': '10'
                    }
                ]},
            'use_variable': {
                'aggre': [[1, 0], [0]],
                'metrics': {MetricCons.Me_acceptable_hidden: [0, 1], MetricCons.Me_stability: [0, 1]},
                'metrics_filter': [{MetricCons.Me_acceptable_hidden: [0, 1]}],
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_method,
                                'attrs': {}},
                        'rel': {'type': Constant.use, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_variable,
                                 'attrs': {'hidden': [Constant.HD_blacklist,
                                                      Constant.HD_greylist] + Constant.HD_greylist_max_list},
                                 'filter': {'qualified_name': filter_list}},
                        'direction': '10'
                    }

                ]
            },
            # 'call_special_hidden': {
            #     'aggre': [[1, 0], [0]],
            #     'metrics': {},
            #     'metrics_filter': [],
            #     'rules': [
            #         {
            #             'src': {'id': [-1], 'category': Constant.E_method,
            #                     'attrs': {}},
            #             'rel': {'type': Constant.call, 'attrs': {}},
            #             'dest': {'id': [-1], 'category': Constant.E_method,
            #                      'attrs': {'hidden': [Constant.HD_hidden]},
            #                      'filter': {'qualified_name': filter_list}},
            #             'direction': '10'
            #         }
            #
            #     ]
            # }
        })

    pattern_param_modify = PatternRules(
        'ParameterListModifyDep', {
            'add_parameter': {
                'aggre': [[1, 0], [0]],
                'metrics': {MetricCons.Me_add_param: [0, 1], MetricCons.Me_native_used_frequency: [0, 0],
                            MetricCons.Me_stability: [0, 0]},
                'metrics_filter': [{MetricCons.Me_native_used_frequency: [0, 0]}, {MetricCons.Me_add_param: [0, 1]}],
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {'intrusive': True},
                                'filter': {'qualified_name': filter_list}},
                        'rel': {'type': Constant.param, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_variable,
                                 'attrs': {}},
                        'direction': '01'
                    }
                ]
            }
        }
    )

    pattern_inner_class = PatternRules(
        'InnerExtensionClassUseDep',
        {
            'inner_class': {
                'aggre': [[1, 1, 1, 0, 0, 0, 1, 0], [1, 2, 3]],
                'metrics': {MetricCons.Me_inner_scale: [0, 1], MetricCons.Me_extensive_access_frequency: [2, 1],
                            MetricCons.Me_anonymous_class: [0, 1], MetricCons.Me_stability: [0, 0]},
                'metrics_filter': [{MetricCons.Me_inner_scale: [0, 1], MetricCons.Me_anonymous_class: [0, 1]},
                                   {MetricCons.Me_extensive_access_frequency: [2, 1]}],
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {},
                                'filter': {'qualified_name': filter_list}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                        'direction': '01'
                    },
                    {
                        'src': {'id': ['id', 0, 1], 'category': Constant.E_class,
                                'attrs': {}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                        'direction': '11'
                    },
                    {
                        'src': {'id': ['id', 1, 1], 'category': Constant.E_method,
                                'attrs': {}},
                        'rel': {'type': Constant.call, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {},
                                 'filter': {}},
                        'direction': '10'
                    },
                    {
                        'src': {'id': ['id', 0, 0], 'category': Constant.E_class,
                                'attrs': {}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': ['id', 2, 1], 'category': Constant.E_method,
                                 'attrs': {}},
                        'direction': '00'
                    },
                ]
            }
        }
    )

    pattern_inherit_extensive = PatternRules(
        'InheritExtension', {
            'inherit_extensive_class': {
                'aggre': [[1, 0], [0], ],
                'metrics': {MetricCons.Me_is_new_inherit: [0, 0], MetricCons.Me_is_inherit: [0, 0],
                            MetricCons.Me_stability: [0, 0]},
                'metrics_filter': [],
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class,
                                'attrs': {'accessible': []}, 'filter': {'qualified_name': filter_list}},
                        'rel': {'type': Constant.inherit, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_class,
                                 'attrs': {'accessible': []}},
                        'direction': '01'
                    }
                ]
            }
        }
    )

    pattern_implement_extensive = PatternRules(
        'ImplementExtension', {
            'implement_extensive_interface': {
                'aggre': [[1, 0], [0]],
                'metrics': {MetricCons.Me_is_new_implement: [0, 0], MetricCons.Me_stability: [0, 0]},
                'metrics_filter': [],
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class,
                                'attrs': {'accessible': []}, 'filter': {'qualified_name': filter_list}},
                        'rel': {'type': Constant.implement, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_interface,
                                 'attrs': {'accessible': []}},
                        'direction': '01'
                    }
                ]
            }
        }
    )

    pattern_aggre_extensive = PatternRules(
        'AggregationExtensionInterfaceClassDep',
        {
            'aggregate_interface': {
                'aggre': [[1, 1, 1, 0, 1, 1, 1, 1, 1, 0], [1, 4], ],
                'metrics': {MetricCons.Me_stability: [0, 1], MetricCons.Me_native_access_frequency: [1, 1]},
                'metrics_filter': [{MetricCons.Me_stability: [0, 1]}],
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_method,
                                 'attrs': {}},
                        'direction': '00'
                    },
                    {
                        'src': {'id': ['id', 0, 1], 'category': Constant.E_method,
                                'attrs': {}},
                        'rel': {'type': Constant.call, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_method,
                                 'attrs': {}, 'filter': {}},
                        'direction': '01'
                    },
                    {
                        'src': {'id': ['id', 0, 0], 'category': Constant.E_class,
                                'attrs': {}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': ['bindVar', 1], 'category': Constant.E_variable, 'attrs': {}},
                        'direction': '01'
                    },
                    {
                        'src': {'id': ['id', 2, 1], 'category': Constant.E_variable, 'attrs': {}},
                        'rel': {'type': Constant.typed, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_interface,
                                 'attrs': {}},
                        'direction': '11'
                    },
                    {
                        'src': {'id': ['id', 3, 1], 'category': Constant.E_interface,
                                'attrs': {}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': ['id', 1, 1], 'category': Constant.E_method,
                                 'attrs': {}},
                        'direction': '11'
                    }
                ]},
            'aggregate_class': {
                'aggre': [[1, 1, 1, 0, 1, 1, 1, 1, 1, 0], [1, 4]],
                'metrics': {MetricCons.Me_stability: [0, 1],
                            MetricCons.Me_native_access_frequency: [1, 1]},
                'metrics_filter': [{MetricCons.Me_stability: [0, 1]}],
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_method,
                                 'attrs': {}},
                        'direction': '00'
                    },
                    {
                        'src': {'id': ['id', 0, 1], 'category': Constant.E_method,
                                'attrs': {}},
                        'rel': {'type': Constant.call, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_method,
                                 'attrs': {}, 'filter': {}},
                        'direction': '01'
                    },
                    {
                        'src': {'id': ['id', 0, 0], 'category': Constant.E_class,
                                'attrs': {}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': ['bindVar', 1], 'category': Constant.E_variable, 'attrs': {}},
                        'direction': '01'
                    },
                    {
                        'src': {'id': ['id', 2, 1], 'category': Constant.E_variable, 'attrs': {}},
                        'rel': {'type': Constant.typed, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_class,
                                 'attrs': {}},
                        'direction': '11'
                    },
                    {
                        'src': {'id': ['id', 3, 1], 'category': Constant.E_class,
                                'attrs': {}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': ['id', 1, 1], 'category': Constant.E_method,
                                 'attrs': {}},
                        'direction': '11'
                    }
                ]
            }
        }
    )

    pattern_inherit_native = PatternRules(
        'InheritanceNative',
        {
            'inherit_native_class': {
                'aggre': [[1, 1, 1, 1, 1, 0, 1, 0], [2, 3], ],
                'metrics': {MetricCons.Me_stability: [3, 1], MetricCons.Me_extensive_access_frequency: [3, 1]},
                'metrics_filter': [{MetricCons.Me_stability: [3, 1]}],
                'rules': [
                    {
                        'src': {'id': [-1], 'category': 'Class',
                                'attrs': {'accessible': []}},
                        'rel': {'type': Constant.inherit, 'attrs': {}},
                        'dest': {'id': [-1], 'category': 'Class',
                                 'attrs': {'accessible': []}},
                        'direction': '10'
                    },
                    {
                        'src': {'id': ['id', 0, 0], 'category': 'Class',
                                'attrs': {'accessible': []}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': [-1], 'category': 'Method',
                                 'attrs': {'accessible': []}},
                        'direction': '11'
                    },
                    {
                        'src': {'id': ['id', 1, 1], 'category': 'Method',
                                'attrs': {'accessible': []}},
                        'rel': {'type': Constant.call, 'attrs': {}},
                        'dest': {'id': [-1], 'category': 'Method',
                                 'attrs': {'accessible': ['protected']},
                                 'filter': {}},
                        'direction': '10'
                    },
                    {
                        'src': {'id': ['id', 0, 1], 'category': 'Class',
                                'attrs': {'accessible': []}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': ['id', 2, 1], 'category': 'Method',
                                 'attrs': {'accessible': ['protected']}},
                        'direction': '00'
                    }
                ]
            }
        }
    )

    pattern_implement_native = PatternRules(
        'ImplementNative', {
            'implement_native_interface': {
                'aggre': [[1, 0], [0], ],
                'metrics': {MetricCons.Me_stability: [0, 1]},
                'metrics_filter': [],
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class,
                                'attrs': {'accessible': []}},
                        'rel': {'type': Constant.implement, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_interface,
                                 'attrs': {'accessible': []}, 'filter': {}},
                        'direction': '10'
                    }]
            }
        }
    )

    pattern_aggre_native = PatternRules(
        'AggregationAOSPClassDep',
        {
            'aggregate_interface': {
                'aggre': [[1, 1, 1, 0, 1, 1, 1, 1, 1, 0], [1, 4], ],
                'metrics': {MetricCons.Me_stability: [3, 1]},
                # 'metrics_filter': [{MetricCons.Me_stability: [3, 1]}],
                'metrics_filter': [],
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                        'direction': '11'
                    },
                    {
                        'src': {'id': ['id', 0, 1], 'category': Constant.E_method,
                                'attrs': {}},
                        'rel': {'type': Constant.call, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {},
                                 'filter': {}},
                        'direction': '10'
                    },
                    {
                        'src': {'id': ['id', 0, 0], 'category': Constant.E_class,
                                'attrs': {}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': ['bindVar', 1], 'category': Constant.E_variable,
                                 'attrs': {}},
                        'direction': '11'
                    },
                    {
                        'src': {'id': ['id', 2, 1], 'category': Constant.E_variable,
                                'attrs': {}},
                        'rel': {'type': Constant.typed, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_interface, 'attrs': {}},
                        'direction': '10'
                    },
                    {
                        'src': {'id': ['id', 3, 1], 'category': Constant.E_interface,
                                'attrs': {}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': ['id', 1, 1], 'category': Constant.E_method,
                                 'attrs': {}},
                        'direction': '00'
                    },
                ]},
            'aggregate_class': {
                'aggre': [[1, 1, 1, 0, 1, 1, 1, 1, 1, 0], [1, 4], ],
                'metrics': {MetricCons.Me_stability: [3, 1]},
                'metrics_filter': [],
                # 'metrics_filter': [{MetricCons.Me_stability: [3, 1]}],
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                        'direction': '11'
                    },
                    {
                        'src': {'id': ['id', 0, 1], 'category': Constant.E_method,
                                'attrs': {}},
                        'rel': {'type': Constant.call, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {},
                                 'filter': {}},
                        'direction': '10'
                    },
                    {
                        'src': {'id': ['id', 0, 0], 'category': Constant.E_class,
                                'attrs': {}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': ['bindVar', 1], 'category': Constant.E_variable,
                                 'attrs': {}},
                        'direction': '11'
                    },
                    {
                        'src': {'id': ['id', 2, 1], 'category': Constant.E_variable,
                                'attrs': {}},
                        'rel': {'type': Constant.typed, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                        'direction': '10'
                    },
                    {
                        'src': {'id': ['id', 3, 1], 'category': Constant.E_class,
                                'attrs': {}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': ['id', 1, 1], 'category': Constant.E_method,
                                 'attrs': {}},
                        'direction': '00'
                    },
                ],
            }
        }
    )

    pattern_public_interface = PatternRules(
        'PublicInterfaceUseDep', {
            'call_public': {
                'aggre': [[1, 0], [0], ],
                'metrics': {},
                'metrics_filter': [],
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                        'rel': {'type': Constant.call, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_method,
                                 'attrs': {
                                     'accessible': [Constant.accessible_list[2]]},
                                 'filter': {'qualified_name': filter_list}
                                 },
                        'direction': '10'
                    },
                ]
            }
        }
    )

    pattern_reflect = PatternRules(
        'ReflectUse', {
            'reflect_method': {
                'aggre': [[1, 0], [0], ],
                'metrics': {MetricCons.Me_open_in_sdk: [0, 1], MetricCons.Me_module: [0, 0],
                            MetricCons.Me_extensive_access_frequency: [0, 1], MetricCons.Me_stability: [0, 1]},
                'metrics_filter': [{MetricCons.Me_open_in_sdk: [0, 1]}, {MetricCons.Me_module: [0, 0]}],
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                        'rel': {'type': Constant.reflect, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {},
                                 'filter': {}},
                        'direction': '10'
                    }
                ]},
            'reflect_class': {
                'aggre': [[1, 0], [0], ],
                'metrics': {MetricCons.Me_open_in_sdk: [0, 1], MetricCons.Me_module: [0, 0],
                            MetricCons.Me_extensive_access_frequency: [0, 1], MetricCons.Me_stability: [0, 1]},
                'metrics_filter': [{MetricCons.Me_open_in_sdk: [0, 1]}, {MetricCons.Me_module: [0, 0]}],
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                        'rel': {'type': Constant.reflect, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_class, 'attrs': {},
                                 'filter': {}},
                        'direction': '10'
                    }
                ],
            }
        }
    )
