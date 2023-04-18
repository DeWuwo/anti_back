import os

from algorithm.script.script import Script
from script.intrusive import IntrusiveCompare
from script.facade_filter import FacadeFilter
from script.data_to_latex import ToLatex
from script.intrusive_type import IntrusiveType
from script.facade_top_file import FileTop
from script.intrusive_filter import IntrusiveFilter
from script.file_move import FileMove
from algorithm.utils import Constant, FileCSV

import sys
import time

if __name__ == '__main__':
    Script('D:\\Honor\\source_code\\utils\\bin').run_command()
    lineage = [('lineage_lineage18.1-16.0', 'D:\\Honor\\match_res\\LineageOS\\base\\lineage_lineage18.1-16.0'),
               ('lineage_lineage18.1-17.1', 'D:\\Honor\\match_res\\LineageOS\\base\\lineage_lineage18.1-17.1'),
               ('lineage_lineage18.1-18.1', 'D:\\Honor\\match_res\\LineageOS\\base\\lineage_lineage18.1-18.1'),
               ('lineage_lineage18.1-19.1', 'D:\\Honor\\match_res\\LineageOS\\base\\lineage_lineage18.1-19.1')]
    calyx = [('CalyxOS-12', 'D:\\Honor\\match_res\\CalyxOS\\base\\android12'),
             ('CalyxOS-11', 'D:\\Honor\\match_res\\CalyxOS\\base\\android11')]
    omni = [('OmniROM-12', 'D:\\Honor\\match_res\\OmniROM\\base\\android-12.0'),
            ('OmniROM-11', 'D:\\Honor\\match_res\\OmniROM\\base\\android-11'),
            ('OmniROM-10', 'D:\\Honor\\match_res\\OmniROM\\base\\android-10'),
            ('OmniROM-9', 'D:\\Honor\\match_res\\OmniROM\\base\\android-9')]
    aospa = [
        ('aospa-quartz', 'D:\\Honor\\match_res\\aospa\\base\\quartz-dev'),
        ('aospa-ruby', 'D:\\Honor\\match_res\\aospa\\base\\ruby-staging'),
        ('aospa-sapphire', 'D:\\Honor\\match_res\\aospa\\base\\sapphire')
    ]
    honor = [
        ('honor_r', 'D:\\Honor\\match_res\\Honor\\base\\honor_r'),
        ('honor_s', 'D:\\Honor\\match_res\\Honor\\base\\honor_s'),
    ]
    # ins_a = IntrusiveCompare()
    # ins_a.get_intrusive_commit(lineage_lineage18.1 + calyx + omni + aospa)

    # ins_a = IntrusiveCompare()
    # ins_a.start_analysis(2, 1, lineage_s=lineage_lineage18.1[2:], omnirom_s=omni[2:], calyx=calyx, aospa=aospa, honor=honor)
    # lineage_lineage18.1=lineage_lineage18.1, omnirom=omni, calyx=calyx,aospa=aospa, honor=honor

    # 筛选切面依赖
    # res = []
    # for proj in aospa + calyx + lineage_lineage18.1 + omni + honor:
    #     f_f = FacadeFilter(proj[1], 'facade.json',
    #                        [Constant.implement, Constant.inherit, Constant.call, Constant.override, Constant.R_cast,
    #                         Constant.R_annotate, Constant.reflect]).get_facade_conf(proj[0])
    #     res.append(f_f)
    # FileCSV.write_dict_to_csv('D:\\Honor\\match_res\\analysis\\intrusive_conf\\', 'res', res, 'w')
    # 切面top file
    # FT = FileTop('facade_file_filter.csv', ['e2n_e', 'e2n_n', 'n2e_n', 'n2e_e'],
    #              "D:\\Honor\\match_res\\facade_analysis")
    # FT.start_analysis(['e2n_e', 'e2n_n', 'n2e_n', 'n2e_e'], 1, lineage_s=lineage_lineage18.1, omnirom_s=omni, calyx=calyx,
    #                   aospa=aospa, honor=honor)

    # file_set = ['services/core/java/com/android/server/pm/PackageManagerService.java', 'core/java/android/provider/Settings.java']
    # IntrusiveFilter('final_ownership.csv').get_inter_api(lineage_lineage18.1, file_set)

    # honor_int = [
    #     ('D:\\Honor\\match_res\\Honor\\base\\honor_r', 'D:\\Honor\\dep_res\\android\\base\\android-11.0.0_r38.json'),
    #     ('D:\\Honor\\match_res\\Honor\\base\\honor_s', 'D:\\Honor\\dep_res\\android\\base\\android-12.1.0_r4.json'),
    # ]
    #
    # IntrusiveType().run_filter(honor_int)

    # latex表格数据格式847330820
    # ToLatex('E:\\2022ASE\\data.csv').to_latex(False)

    # 移动文件
    # method_file = ['']
    #
    # result_data = ['D:\\Honor\\项目交付材料\\数据集核对',
    #                ['coupling-patterns\\res.json']]
    #
    # for proj in aospa + calyx + lineage_lineage18.1 + omni:
    #     FileMove.file_move(proj[1], os.path.join(result_data[0], proj[0]),
    #                        result_data[1])
