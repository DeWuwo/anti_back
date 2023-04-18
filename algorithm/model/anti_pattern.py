from algorithm.model.pattern_type import PatternType
from algorithm.utils import Constant


class AntiPattern(PatternType):
    def __init__(self):
        filter_list = ['android.util', 'android.os.Message', 'com.android.internal.logging',
                       'com.android.internal.os', 'android.os', 'com.android.server.utils',
                       'hihonor.android.utils', 'android.os.ServiceManager', 'com.android.server.LocalServices',
                       'android.provider.Settings.Secure', 'android.provider.Settings.System',
                       'com.android.telephony.Rlog']
        ident = 'anti-patterns'
        patterns = ['FinalDel', 'AccessibilityModify', 'HiddenApi', 'HiddenModify',
                    'ParamListModify', 'InheritDestroy', 'ReflectUse']
        rules = [
            {
                'FinalDel': {
                    'style1': [
                        {
                            'src': {'id': [-1], 'category': Constant.E_class,
                                    'attrs': {}},
                            'rel': {'type': Constant.inherit, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_class,
                                     'attrs': {'final': True, 'intrusive': True},
                                     'filter': {'qualified_name': filter_list}},
                            'direction': '10'
                        }
                    ],
                    'style2': [
                        {
                            'src': {'id': [-1], 'category': Constant.E_method,
                                    'attrs': {}},
                            'rel': {'type': Constant.override, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method,
                                     'attrs': {'final': True, 'intrusive': True},
                                     'filter': {'qualified_name': filter_list}},
                            'direction': '10'
                        },
                    ]
                }
            },
            {
                'AccessibilityModify': {
                    'style1': [
                        {
                            'src': {'id': [-1], 'category': Constant.E_class,
                                    'attrs': {}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_class,
                                     'attrs': {'accessible_modify': True, 'intrusive': True},
                                     'filter': {'qualified_name': filter_list}},
                            'direction': '00'
                        }
                    ],
                    'style2':[
                        {
                            'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method,
                                     'attrs': {
                                         'accessible': [Constant.accessible_list[2]], 'accessible_modify': True,
                                         'intrusive': True},
                                     'filter': {'qualified_name': filter_list}
                                     },
                            'direction': '00'
                        },
                    ],
                    'style3':[
                        {
                            'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method,
                                     'attrs': {
                                         'accessible_modify': True, 'intrusive': True},
                                     'filter': {'qualified_name': filter_list}
                                     },
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
                    'style2':[
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
                'ParamListModify': {
                    'style1':[
                        {
                            'src': {'id': [-1], 'category': Constant.E_method,
                                    'attrs': {'intrusive': True},
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
                'InheritDestroy': {
                    'style1':[
                        {
                            'src': {'id': [-1], 'category': Constant.E_class,
                                    'attrs': {}, 'filter': {'qualified_name': filter_list}},
                            'rel': {'type': Constant.inherit, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_class,
                                     'attrs': {}},
                            'direction': '01'
                        }
                    ]
                }
            },
            {
                'ReflectUse': {
                    'style1':[
                        {
                            'src': {'id': [-1], 'category': Constant.E_method,
                                    'attrs': {}},
                            'rel': {'type': Constant.reflect,
                                    'attrs': {'set_accessible': True,
                                              'invoke': True}},
                            'dest': {'id': [-1], 'category': Constant.E_method,
                                     'attrs': {
                                         'accessible': [Constant.accessible_list[0], Constant.accessible_list[1],
                                                        Constant.un_define]},
                                     'filter': {'qualified_name': filter_list}},
                            'direction': '10'
                        }
                    ],
                    'style2':[
                        {
                            'src': {'id': [-1], 'category': Constant.E_class,
                                    'attrs': {}},
                            'rel': {'type': Constant.reflect,
                                    'attrs': {'set_accessible': True,
                                              'invoke': True}},
                            'dest': {'id': [-1], 'category': Constant.E_method,
                                     'attrs': {
                                         'accessible': [Constant.accessible_list[0], Constant.accessible_list[1],
                                                        Constant.un_define]},
                                     'filter': {'qualified_name': filter_list}},
                            'direction': '10'
                        }
                    ],
                }
            }
        ]
        PatternType.__init__(self, ident, patterns, rules, filter_list)
