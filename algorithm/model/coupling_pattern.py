from algorithm.model.pattern_type import PatternType
from algorithm.utils import Constant


class CouplingPattern(PatternType):
    def __init__(self):
        filter_list = ['android.util', 'android.os.Message', 'com.android.internal.logging',
                       'com.android.internal.os', 'android.os', 'com.android.server.utils',
                       'hihonor.android.utils', 'android.os.ServiceManager', 'com.android.server.LocalServices',
                       'android.provider.Settings.Secure', 'android.provider.Settings.System',
                       'com.android.telephony.Rlog']
        ident = 'coupling-patterns'
        patterns = ['FinalDel', 'AccessibilityModify',
                    'HiddenApi', 'HiddenModify',
                    'ParameterListModifyDep',
                    'InnerExtensionClassUseDep',
                    'InheritExtension',
                    'ImplementExtension',
                    'AggregationExtensionInterfaceClassDep',

                    'InheritanceNative',
                    'ImplementNative',
                    'AggregationAOSPClassDep',
                    'PublicInterfaceUseDep',
                    'ReflectUse']
        rules = [
            {
                'FinalDel': {
                    'style1': [
                        {
                            'src': {'id': [-1], 'category': Constant.E_class,
                                    'attrs': {}},
                            'rel': {'type': Constant.inherit, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_class,
                                     'attrs': {'final': True, 'intrusive': True}},
                            'direction': '10'
                        }
                    ],
                    'style2': [
                        {
                            'src': {'id': [-1], 'category': Constant.E_method,
                                    'attrs': {}},
                            'rel': {'type': Constant.override, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method,
                                     'attrs': {'final': True, 'intrusive': True}},
                            'direction': '10'
                        },
                    ],
                    'style3': [
                        {
                            'src': {'id': [-1], 'category': Constant.E_class,
                                    'attrs': {}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method,
                                     'attrs': {'final': True, 'intrusive': True}},
                            'direction': '00'
                        },
                    ]
                }
            },
            {
                'AccessibilityModify': {
                    'style1': [
                        {
                            'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_class,
                                     'attrs': {'accessible_modify': True, 'intrusive': True},
                                     'filter': {'qualified_name': filter_list}},
                            'direction': '00'
                        }
                    ],
                    # [
                    #     {
                    #         'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                    #         'rel': {'type': Constant.define, 'attrs': {}},
                    #         'dest': {'id': [-1], 'category': Constant.E_method,
                    #                  'attrs': {
                    #                      'accessible': [Constant.accessible_list[2]], 'accessible_modify': True,
                    #                      'intrusive': True}
                    #                  },
                    #         'direction': '00'
                    #     },
                    # ],
                    'style2': [
                        {
                            'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method,
                                     'attrs': {'accessible_modify': True, 'intrusive': True},
                                     'filter': {'qualified_name': filter_list}},
                            'direction': '00'
                        },
                    ]
                }
            },
            {
                'HiddenApi': {
                    'style1': [
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
                    ],
                    'style2': [
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
                }
            },
            # {
            #     'HiddenModify': [
            #         [
            #             {
            #                 'src': {'id': [-1], 'category': Constant.E_method,
            #                         'attrs': {}},
            #                 'rel': {'type': Constant.call, 'attrs': {}},
            #                 'dest': {'id': [-1], 'category': Constant.E_method,
            #                          'attrs': {'hidden_modify': True}},
            #                 'direction': '10'
            #             }
            #         ],
            #         [
            #             {
            #                 'src': {'id': [-1], 'category': Constant.E_method,
            #                         'attrs': {}},
            #                 'rel': {'type': Constant.use, 'attrs': {}},
            #                 'dest': {'id': [-1], 'category': Constant.E_variable,
            #                          'attrs': {'hidden_modify': True}},
            #                 'direction': '10'
            #             }
            #
            #         ]
            #     ]
            # },
            {
                'ParameterListModifyDep': {
                    'add_parameter': [
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
            },
            {
                'InnerExtensionClassUseDep': {
                    'style1': [
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
                                     'filter': {'accessible': [Constant.accessible_list[2]]}},
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
            },
            {
                'InheritExtension': {
                    'style2': [
                        {
                            'src': {'id': [-1], 'category': Constant.E_class,
                                    'attrs': {'accessible': []}, 'filter': {'qualified_name': filter_list}},
                            'rel': {'type': Constant.inherit, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_class,
                                     'attrs': {'accessible': []}},
                            'direction': '01'
                        }]
                }
            },
            {
                'ImplementExtension': {
                    'style2': [
                        {
                            'src': {'id': [-1], 'category': Constant.E_class,
                                    'attrs': {'accessible': []}, 'filter': {'qualified_name': filter_list}},
                            'rel': {'type': Constant.implement, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_interface,
                                     'attrs': {'accessible': []}},
                            'direction': '01'
                        }]
                }
            },
            {
                'AggregationExtensionInterfaceClassDep': {
                    'style2': [
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
                                     'attrs': {}, 'filter': {'qualified_name': filter_list}},
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
                    ],
                    'style3': [
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
                                     'attrs': {}, 'filter': {'qualified_name': filter_list}},
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
            },
            {
                'InheritanceNative': {
                    'style2': [
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
                                     'attrs': {'accessible': ['protected', '']},
                                     'filter': {'qualified_name': filter_list}},
                            'direction': '10'
                        },
                        {
                            'src': {'id': ['id', 0, 1], 'category': 'Class',
                                    'attrs': {'accessible': []}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': ['id', 2, 1], 'category': 'Method',
                                     'attrs': {'accessible': ['protected', '']}},
                            'direction': '00'
                        }
                    ]
                }
            },
            {
                'ImplementNative': {
                    'style2': [
                        {
                            'src': {'id': [-1], 'category': Constant.E_class,
                                    'attrs': {'accessible': []}},
                            'rel': {'type': Constant.implement, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_interface,
                                     'attrs': {'accessible': []}, 'filter': {'qualified_name': filter_list}},
                            'direction': '10'
                        }]
                }
            },
            {
                'AggregationAOSPClassDep': {
                    'class': [
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
                                     'filter': {'qualified_name': filter_list}},
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
                    ],
                    'interface': [
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
                                     'filter': {'qualified_name': filter_list}},
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
            },
            {
                'PublicInterfaceUseDep': {
                    'style2': [
                        {
                            'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                            'rel': {'type': Constant.call, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method,
                                     'attrs': {
                                         'accessible': [Constant.accessible_list[2]], 'accessible_modify': False},
                                     'filter': {'qualified_name': filter_list}
                                     },
                            'direction': '10'
                        },
                    ]
                }
            },
            {
                'ReflectUse': {
                    'style2': [
                        {
                            'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                            'rel': {'type': Constant.reflect, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {},
                                     'filter': {'qualified_name': filter_list}},
                            'direction': '10'
                        }
                    ],
                    'style3': [
                        {
                            'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                            'rel': {'type': Constant.reflect, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_class, 'attrs': {},
                                     'filter': {'qualified_name': filter_list}},
                            'direction': '10'
                        }
                    ],
                }
            }
        ]

        PatternType.__init__(self, ident, patterns, rules, filter_list)
