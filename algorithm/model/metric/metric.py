import os.path
from typing import List
from collections import defaultdict
from functools import partial

from algorithm.model.dependency.relation import Relation
from algorithm.model.dependency.entity import Entity, get_accessible_domain
from algorithm.model.metric.metric_constant import MetricCons
from algorithm.utils import FileCSV, Constant, FileCommon
from algorithm.model.metric.sdk_api import SDKApi
from algorithm.model.metric.conflicts.conflict import Conflict


class Metric:
    src_relation: defaultdict
    dest_relation: defaultdict
    mc_data: defaultdict
    mc_data_rank: defaultdict
    conflict_info: dict
    query_relation: defaultdict
    entity_native: List[Entity]
    entity_extensive: List[Entity]
    hidden_filter_list: List[str]
    sdk_apis: defaultdict

    def __init__(self, relations: List[Relation], data_path: str, query_relation, entity_native: List[Entity],
                 entity_extensive: List[Entity], hidden_filter_list: List[str], code_extension: str):
        self.src_relation = defaultdict(partial(defaultdict, list))
        self.dest_relation = defaultdict(partial(defaultdict, list))
        self.mc_data = defaultdict(partial(defaultdict))
        self.mc_data_rank = defaultdict(partial(defaultdict))
        for rel in relations:
            self.src_relation[rel.src][rel.rel].append(rel)
            self.dest_relation[rel.dest][rel.rel].append(rel)
        try:
            mc_data_nat = FileCSV.read_dict_from_csv(os.path.join(data_path, 'mc/file-mc_nat.csv'))
            mc_data_ext = FileCSV.read_dict_from_csv(os.path.join(data_path, 'mc/file-mc_ext.csv'))
        except FileNotFoundError:
            mc_data_nat = []
            mc_data_ext = []
        for data in mc_data_nat:
            self.mc_data['nat'][str(data['filename']).replace('\\', '/')] = data
        for data in mc_data_ext:
            self.mc_data['ext'][str(data['filename']).replace('\\', '/')] = data
        try:
            mc_data_rank_nat = FileCSV.read_dict_from_csv(os.path.join(data_path, 'mc/file-mc_rank_nat.csv'))
            mc_data_rank_ext = FileCSV.read_dict_from_csv(os.path.join(data_path, 'mc/file-mc_rank_ext.csv'))
        except FileNotFoundError:
            mc_data_rank_nat = []
            mc_data_rank_ext = []
        for data in mc_data_rank_nat:
            self.mc_data_rank['nat'][str(data['filename']).replace('\\', '/')] = data
        for data in mc_data_rank_ext:
            self.mc_data_rank['ext'][str(data['filename']).replace('\\', '/')] = data
        self.conflict_info = Conflict(data_path).get_conf_files()
        self.query_relation = query_relation
        self.entity_native = entity_native
        self.entity_extensive = entity_extensive
        self.hidden_filter_list = hidden_filter_list
        self.sdk_apis = SDKApi(code_extension, data_path).get_apis()

    def handle_metrics(self, metrics: dict, rels: List[Relation], **kwargs):
        for key, val in kwargs.items():
            method = getattr(self, f'handle_metrics_{key}', None)
            method(metrics, rels, val)

    def handle_metrics_filter(self, metrics: dict, l_kwargs: List[dict]):
        if not l_kwargs:
            return True
        for kwargs in l_kwargs:
            flag = True
            for key, val in kwargs.items():
                method = getattr(self, f'handle_metrics_filter_{key}', None)
                if not method(metrics, val):
                    flag = False
                    break
            if flag:
                return True
        return False

    def handle_metrics_statistics(self, metrics: dict, metrics_statistic: dict, **kwargs):
        for key, _ in kwargs.items():
            method = getattr(self, f'handle_metrics_statistics_{key}', None)
            method(metrics, metrics_statistic)

    def handle_metrics_init(self, **kwargs):
        metrics = {}
        for key, val in kwargs.items():
            if key == MetricCons.Me_native_used_frequency or key == MetricCons.Me_extensive_used_frequency or \
                    key == MetricCons.Me_native_used_effectiveness:
                metrics[key] = {}
            elif key == MetricCons.Me_extensive_access_frequency or key == MetricCons.Me_native_access_frequency:
                metrics[key] = {}
                metrics[key]['total'] = 0
                for access in Constant.accessible_list:
                    metrics[key][access] = 0
            elif key == MetricCons.Me_stability:
                metrics[key] = {}
            elif key == MetricCons.Me_module:
                metrics[key] = ''
            elif key == MetricCons.Me_acceptable_hidden:
                metrics[key] = []
            elif key == MetricCons.Me_add_param:
                metrics[key] = {}
                metrics[key]['count'] = 0
                metrics[key]['complex_count'] = 0
                metrics[key]['detail'] = []
            elif key == MetricCons.Me_inner_scale:
                metrics[key] = {}
                metrics[key]['inner_class_loc'] = 0
            elif key == MetricCons.Me_interface_number:
                metrics[key] = {}
                metrics[key]['total'] = 0
                metrics[key]['native'] = 0
                metrics[key]['extensive'] = 0
                metrics[key]['final'] = 0
                for access in Constant.accessible_list:
                    metrics[key][access] = 0
                # metrics[key][Constant.E_variable] = 0
                # metrics[key][Constant.E_method] = 0
                # metrics[key][Constant.E_class] = 0
            elif key == MetricCons.Me_anonymous_class:
                metrics[key] = {}
            elif key == MetricCons.Me_open_in_sdk:
                metrics[key] = {}
                metrics[key]['in_sdk'] = []
                metrics[key]['not_in_sdk'] = []
        return metrics

    def handle_metrics_statistics_init(self, **kwargs):
        metrics_statistic = {}
        for key, val in kwargs.items():
            if key == MetricCons.Me_native_used_frequency or key == MetricCons.Me_extensive_used_frequency:
                metrics_statistic[key] = {}
                indicates = ['n0_e0', 'n1_e0', 'n0_e1', 'n1_e1']
                for indicate in indicates:
                    metrics_statistic[key][indicate] = 0
            elif key == MetricCons.Me_native_used_effectiveness:
                metrics_statistic[key] = {}
                indicates = ['0', '0-0.2', '0.2-0.5', '0.5-1']
                for indicate in indicates:
                    metrics_statistic[key][indicate] = 0
            elif key == MetricCons.Me_extensive_access_frequency or key == MetricCons.Me_native_access_frequency:
                metrics_statistic[key] = {}
                indicates = ['per_private_0', 'per_private_0-0.2', 'per_private_0.2-0.5', 'per_private_0.5-1']
                for indicate in indicates:
                    metrics_statistic[key][indicate] = 0
            elif key == MetricCons.Me_stability:
                metrics_statistic[key] = {}
                metrics_statistic[key]['history_commits'] = {}
                metrics_statistic[key]['maintenance_cost'] = {}
                metrics_statistic[key]['maintenance_cost_rank'] = {}
                indicates = ['0-10', '10-30', '30-50', '50-']
                for indicate in indicates:
                    metrics_statistic[key]['history_commits'][indicate] = 0
                indicates = ['per_of_changloc_loc_1', 'per_of_changloc_loc_2', 'per_of_changloc_loc_5',
                             'per_of_changloc_loc_~']
                for indicate in indicates:
                    metrics_statistic[key]['maintenance_cost'][indicate] = 0
                indicates = ['top_10', 'top_50', 'top_100', 'top_10%', 'top_25%', 'top_50%', 'top_100%']
                for indicate in indicates:
                    metrics_statistic[key]['maintenance_cost_rank'][indicate] = 0
            elif key == MetricCons.Me_module:
                metrics_statistic[key] = {}
                indicates = ['test', 'not test']
                for indicate in indicates:
                    metrics_statistic[key][indicate] = 0
            elif key == MetricCons.Me_acceptable_hidden:
                metrics_statistic[key] = {}
                indicates = ['no_acceptable_hidden', 'all_acceptable_hidden', 'mix_acceptable_hidden']
                for indicate in indicates:
                    metrics_statistic[key][indicate] = 0
            elif key == MetricCons.Me_add_param:
                metrics_statistic[key] = {}
                indicates = ['single_simple_param', 'single_complex_param', 'multi_simple_param', 'multi_complex_param']
                for indicate in indicates:
                    metrics_statistic[key][indicate] = 0
            elif key == MetricCons.Me_inner_scale:
                metrics_statistic[key] = {}
                indicates = ['per_inner_class_loc_0.05', 'per_inner_class_loc_0.1', 'per_inner_class_loc_0.2',
                             'per_inner_class_loc_~']
                for indicate in indicates:
                    metrics_statistic[key][indicate] = 0
            elif key == MetricCons.Me_interface_number:
                metrics_statistic[key] = {}
                indicates = []
                for indicate in indicates:
                    metrics_statistic[key][indicate] = 0
            elif key == MetricCons.Me_anonymous_class:
                metrics_statistic[key] = {}
                indicates = ['is_anonymous_class', 'is_not_anonymous_class']
                for indicate in indicates:
                    metrics_statistic[key][indicate] = 0
            elif key == MetricCons.Me_open_in_sdk:
                metrics_statistic[key] = {}
                indicates = ['all_not_in_sdk', 'all_in_sdk', 'mix_in_sdk']
                for indicate in indicates:
                    metrics_statistic[key][indicate] = 0
            elif key == MetricCons.Me_is_inherit:
                metrics_statistic[key] = {}
                indicates = ['is_inherit', 'no_inherit']
                for indicate in indicates:
                    metrics_statistic[key][indicate] = 0
            elif key == MetricCons.Me_is_new_inherit:
                metrics_statistic[key] = {}
                indicates = ['new_add_inherit', 'modify_inherit']
                for indicate in indicates:
                    metrics_statistic[key][indicate] = 0
            elif key == MetricCons.Me_is_new_implement:
                metrics_statistic[key] = {}
                indicates = ['new_add_implement', 'modify_implement']
                for indicate in indicates:
                    metrics_statistic[key][indicate] = 0
            elif key == MetricCons.Me_is_override:
                metrics_statistic[key] = {}
                indicates = ['is_override', 'no_override']
                for indicate in indicates:
                    metrics_statistic[key][indicate] = 0
        return metrics_statistic

    def handle_metrics_native_used_frequency(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        used_frequency = {}
        if self.entity_extensive[entity_id].category == Constant.E_method:
            res = self.query_relation[Constant.call]['10'][Constant.E_method][entity_id]
            used_frequency = {
                'used_by_extension': len(res),
                'used_by_native': self.entity_extensive[entity_id].called - len(res)
            }
        elif self.entity_extensive[entity_id].category == Constant.E_class:
            res = self.query_relation[Constant.typed]['10'][Constant.E_variable][entity_id]
            used_frequency = {
                'used_by_extension': len(res),
                'used_by_native': len(self.dest_relation[entity_id][Constant.typed]) - len(res)
            }
        metrics[MetricCons.Me_native_used_frequency] = used_frequency

    def handle_metrics_filter_native_used_frequency(self, metrics: dict, indicate: list):
        if metrics[MetricCons.Me_native_used_frequency]['used_by_extension'] == 0 and \
                metrics[MetricCons.Me_native_used_frequency]['used_by_native'] == 0:
            return True
        if metrics[MetricCons.Me_native_used_frequency]['used_by_extension'] != 0 or \
                metrics[MetricCons.Me_native_used_frequency]['used_by_native'] > 9:
            return True
        return False

    def handle_metrics_statistics_native_used_frequency(self, metrics: dict, metrics_statistics: dict):
        if metrics[MetricCons.Me_native_used_frequency]['used_by_native'] == 0:
            if metrics[MetricCons.Me_native_used_frequency]['used_by_extension'] == 0:
                metrics_statistics[MetricCons.Me_native_used_frequency]['n0_e0'] += 1
            else:
                metrics_statistics[MetricCons.Me_native_used_frequency]['n0_e1'] += 1
        elif metrics[MetricCons.Me_native_used_frequency]['used_by_native'] != 0:
            if metrics[MetricCons.Me_native_used_frequency]['used_by_extension'] == 0:
                metrics_statistics[MetricCons.Me_native_used_frequency]['n1_e0'] += 1
            else:
                metrics_statistics[MetricCons.Me_native_used_frequency]['n1_e1'] += 1

    # 对于修改访问权限的有效访问
    def handle_metrics_native_used_effectiveness(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        current_entity = self.entity_extensive[entity_id]
        metrics[MetricCons.Me_native_used_effectiveness]['used_by_extension_effectively'] = 0
        metrics[MetricCons.Me_native_used_effectiveness]['used_by_extension_saturatedly'] = 0
        source_domain = Constant.accessible_level[current_entity.intrusive_modify['access_modify'].split('-')[0]]
        target_domain = Constant.accessible_level[current_entity.intrusive_modify['access_modify'].split('-')[1]]
        for rel in self.query_relation[Constant.call]['10'][Constant.E_method][entity_id]:
            access_domain = get_accessible_domain(current_entity, self.entity_extensive[rel.src], self.entity_extensive)
            if access_domain == target_domain:
                metrics[MetricCons.Me_native_used_effectiveness]['used_by_extension_saturatedly'] += 1
            elif source_domain < access_domain < target_domain:
                metrics[MetricCons.Me_native_used_effectiveness]['used_by_extension_effectively'] += 1

    def handle_metrics_filter_native_used_effectiveness(self, metrics: dict, indicate: list):
        if metrics[MetricCons.Me_native_used_frequency]['used_by_extension'] == 0:
            return True
        res = metrics[MetricCons.Me_native_used_effectiveness]['used_by_extension_effectively'] / \
              metrics[MetricCons.Me_native_used_frequency]['used_by_extension']
        if float(res) < 0.5:
            return True
        return False

    def handle_metrics_statistics_native_used_effectiveness(self, metrics: dict, metrics_statistics: dict):
        if metrics[MetricCons.Me_native_used_frequency]['used_by_extension'] == 0:
            metrics_statistics[MetricCons.Me_native_used_effectiveness]['0'] += 1
        else:
            res = (metrics[MetricCons.Me_native_used_effectiveness]['used_by_extension_effectively'] +
                   metrics[MetricCons.Me_native_used_effectiveness]['used_by_extension_saturatedly']) / \
                  metrics[MetricCons.Me_native_used_frequency]['used_by_extension']
            if float(res) == 0:
                metrics_statistics[MetricCons.Me_native_used_effectiveness]['0'] += 1
            elif 0 < float(res) < 0.2:
                metrics_statistics[MetricCons.Me_native_used_effectiveness]['0-0.2'] += 1
            elif float(res) < 0.5:
                metrics_statistics[MetricCons.Me_native_used_effectiveness]['0.2-0.5'] += 1
            else:
                metrics_statistics[MetricCons.Me_native_used_effectiveness]['0.5-1'] += 1
        return False

    def handle_metrics_extensive_used_frequency(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        used_frequency = {}
        if self.entity_extensive[entity_id].category == Constant.E_method:
            res = self.query_relation[Constant.call]['01'][Constant.E_method][entity_id]
            used_frequency = {
                'used_by_extension': self.entity_extensive[entity_id].called - len(res),
                'used_by_native': len(res)
            }
        elif self.entity_extensive[entity_id].category == Constant.E_class:
            res = self.query_relation[Constant.R_import]['01'][Constant.E_file][entity_id]
            used_frequency = {
                'used_by_extension': len(self.dest_relation[entity_id][Constant.R_import]) - len(res),
                'used_by_native': len(res)
            }
        metrics[MetricCons.Me_extensive_used_frequency] = used_frequency

    def handle_metrics_filter_extensive_used_frequency(self, metrics: dict, indicate: list):
        if metrics[MetricCons.Me_extensive_used_frequency]['used_by_native'] != 0:
            return True
        return False

    def handle_metrics_statistics_extensive_used_frequency(self, metrics: dict, metrics_statistics: dict):
        if metrics[MetricCons.Me_native_used_frequency]['used_by_native'] == 0:
            if metrics[MetricCons.Me_native_used_frequency]['used_by_extension'] == 0:
                metrics_statistics[MetricCons.Me_native_used_frequency]['n0_e0'] += 1
            else:
                metrics_statistics[MetricCons.Me_native_used_frequency]['n0_e1'] += 1
        elif metrics[MetricCons.Me_native_used_frequency]['used_by_native'] == 1:
            if metrics[MetricCons.Me_native_used_frequency]['used_by_extension'] == 0:
                metrics_statistics[MetricCons.Me_native_used_frequency]['n1_e0'] += 1
            else:
                metrics_statistics[MetricCons.Me_native_used_frequency]['n1_e1'] += 1

    def handle_metrics_extensive_access_frequency(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        metrics[MetricCons.Me_extensive_access_frequency]['total'] += 1
        metrics[MetricCons.Me_extensive_access_frequency][self.entity_extensive[entity_id].accessible] += 1

    def handle_metrics_filter_extensive_access_frequency(self, metrics: dict, indicate: list):
        return metrics[MetricCons.Me_extensive_access_frequency][Constant.accessible_list[0]] == 0 or \
               (metrics[MetricCons.Me_extensive_access_frequency][Constant.accessible_list[0]] /
                metrics[MetricCons.Me_extensive_access_frequency]['total']) < 0.5

    def handle_metrics_statistics_extensive_access_frequency(self, metrics: dict, metrics_statistics: dict):
        if metrics[MetricCons.Me_extensive_access_frequency][Constant.accessible_list[0]] == 0:
            metrics_statistics[MetricCons.Me_extensive_access_frequency]['per_private_0'] += 1
        else:
            indicate = (metrics[MetricCons.Me_extensive_access_frequency][Constant.accessible_list[0]] /
                        metrics[MetricCons.Me_extensive_access_frequency]['total'])
            if indicate < 0.2:
                metrics_statistics[MetricCons.Me_extensive_access_frequency]['per_private_0-0.2'] += 1
            elif indicate < 0.5:
                metrics_statistics[MetricCons.Me_extensive_access_frequency]['per_private_0.2-0.5'] += 1
            else:
                metrics_statistics[MetricCons.Me_extensive_access_frequency]['per_private_0.5-1'] += 1

    # 用于原生聚合扩展时，记录调用扩展的数量
    def handle_metrics_native_access_frequency(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        metrics[MetricCons.Me_native_access_frequency]['total'] += 1
        metrics[MetricCons.Me_native_access_frequency][self.entity_extensive[entity_id].accessible] += 1

    def handle_metrics_filter_native_access_frequency(self, metrics: dict, indicate: list):
        return metrics[MetricCons.Me_native_access_frequency][Constant.accessible_list[2]] != 0

    def handle_metrics_statistics_native_access_frequency(self, metrics: dict, metrics_statistics: dict):
        if metrics[MetricCons.Me_native_access_frequency][Constant.accessible_list[0]] == 0:
            metrics_statistics[MetricCons.Me_native_access_frequency]['per_private_0'] += 1
        else:
            indicate = (metrics[MetricCons.Me_native_access_frequency][Constant.accessible_list[0]] /
                        metrics[MetricCons.Me_native_access_frequency]['total'])
            if indicate < 0.2:
                metrics_statistics[MetricCons.Me_native_access_frequency]['per_private_0-0.2'] += 1
            elif indicate < 0.5:
                metrics_statistics[MetricCons.Me_native_access_frequency]['per_private_0.2-0.5'] += 1
            else:
                metrics_statistics[MetricCons.Me_native_access_frequency]['per_private_0.5-1'] += 1

    def handle_metrics_func_metrics(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        metrics[MetricCons.Me_module] = 'test' \
            if 'test' in self.entity_extensive[entity_id].qualifiedName else 'not test'

    def handle_metrics_filter_func_metrics(self, metrics: dict, indicate: list):
        if metrics[MetricCons.Me_module] == 'test':
            return False
        return True

    def handle_metrics_statistics_func_metrics(self, metrics: dict, metrics_statistics: dict):
        if metrics[MetricCons.Me_module] == 'test':
            metrics_statistics[MetricCons.Me_module]['test'] += 1
        else:
            metrics_statistics[MetricCons.Me_module]['not test'] += 1

    def handle_metrics_stability(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        metrics[MetricCons.Me_stability]['entity'] = self.entity_extensive[entity_id].to_string()
        metrics[MetricCons.Me_stability]['history_commits'] = self.entity_extensive[entity_id].commits_count
        try:
            metrics[MetricCons.Me_stability]['maintenance_cost'] = {
                'native': self.mc_data['nat'][self.entity_extensive[entity_id].file_path],
                'extensive': self.mc_data['ext'][self.entity_extensive[entity_id].file_path]
            }
        except KeyError:
            pass
        try:
            metrics[MetricCons.Me_stability]['maintenance_cost_rank'] = {
                'native': self.mc_data_rank['nat'][self.entity_extensive[entity_id].file_path],
                'extensive': self.mc_data_rank['ext'][self.entity_extensive[entity_id].file_path]
            }
        except KeyError:
            pass

        try:
            metrics[MetricCons.Me_stability]['conflicts'] = self.conflict_info[
                self.entity_extensive[entity_id].file_path]
        except KeyError:
            pass

    def handle_metrics_filter_stability(self, metrics: dict, indicate: list):
        entity = self.entity_extensive[int(metrics[MetricCons.Me_stability]['entity'].split('#')[0])]
        if metrics[MetricCons.Me_stability]['entity'].split('#')[1] == Constant.E_method:
            try:
                if metrics[MetricCons.Me_stability]['history_commits']['actively_native'] > int(
                        (entity.end_line - entity.start_line) / 10):
                    return True
            except KeyError:
                return True
        elif metrics[MetricCons.Me_stability]['entity'].split('#')[1] in [Constant.E_class, Constant.E_interface]:
            return float(metrics[MetricCons.Me_stability]['maintenance_cost']['native']['changeloc']) > (
                    entity.end_line - entity.start_line)

        return False

    def handle_metrics_statistics_stability(self, metrics: dict, metrics_statistics: dict):
        entity = self.entity_extensive[int(metrics[MetricCons.Me_stability]['entity'].split('#')[0])]
        # if metrics[MetricCons.Me_stability]['entity'].split('#')[1] == Constant.E_method:
        try:
            if metrics[MetricCons.Me_stability]['history_commits']['actively_native'] < 10:
                metrics_statistics[MetricCons.Me_stability]['history_commits']['0-10'] += 1
            elif 10 <= metrics[MetricCons.Me_stability]['history_commits']['actively_native'] < 30:
                metrics_statistics[MetricCons.Me_stability]['history_commits']['10-30'] += 1
            elif 30 <= metrics[MetricCons.Me_stability]['history_commits']['actively_native'] < 50:
                metrics_statistics[MetricCons.Me_stability]['history_commits']['30-50'] += 1
            else:
                metrics_statistics[MetricCons.Me_stability]['history_commits']['50-'] += 1
        except KeyError:
            pass
        try:
            code_size = entity.end_line - entity.start_line + 1
            if float(metrics[MetricCons.Me_stability]['maintenance_cost']['changeloc']) < code_size:
                metrics_statistics[MetricCons.Me_stability]['maintenance_cost']['per_of_changloc_loc_1'] += 1
            else:
                chang_loc_loc_per = float(
                    float(metrics[MetricCons.Me_stability]['maintenance_cost']['changeloc']) / code_size)
                if chang_loc_loc_per < 2:
                    metrics_statistics[MetricCons.Me_stability]['maintenance_cost']['per_of_changloc_loc_2'] += 1
                elif chang_loc_loc_per < 5:
                    metrics_statistics[MetricCons.Me_stability]['maintenance_cost']['per_of_changloc_loc_5'] += 1
                else:
                    metrics_statistics[MetricCons.Me_stability]['maintenance_cost']['per_of_changloc_loc_~'] += 1
        except KeyError:
            pass
        try:
            average = 0
            file_count = int(metrics[MetricCons.Me_stability]['maintenance_cost_rank']['native']['file_count'])
            for key, mc in metrics[MetricCons.Me_stability]['maintenance_cost_rank']['native'].items():
                if key == 'filename' or key == 'file_count':
                    continue
                index = int(mc)
                if 0 <= index <= 10:
                    mc_rank = 'top_10'
                elif 10 < index <= 50:
                    mc_rank = 'top_50'
                elif 50 < index <= 100:
                    mc_rank = 'top_100'
                elif 100 < index <= file_count // 10:
                    mc_rank = 'top_10%'
                elif file_count // 10 < index <= file_count // 4:
                    mc_rank = 'top_25%'
                elif file_count // 4 < index <= file_count // 2:
                    mc_rank = 'top_50%'
                else:
                    mc_rank = 'top_100%'
                average += MetricCons.mc_rank_level[mc_rank]
            average = int(round(average / 6))
            metrics_statistics[MetricCons.Me_stability]['maintenance_cost_rank'][MetricCons.mc_rank[average]] += 1
        except KeyError:
            pass

    def handle_metrics_is_inherit(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        metrics[MetricCons.Me_is_inherit] = [self.entity_extensive[rel.src].qualifiedName for rel in
                                             self.query_relation[Constant.inherit]['10'][Constant.E_class][entity_id]]

    def handle_metrics_filter_is_inherit(self, metrics: dict, indicate: list):
        if metrics[MetricCons.Me_is_inherit]:
            return True
        return False

    def handle_metrics_statistics_is_inherit(self, metrics: dict, metrics_statistics: dict):
        if metrics[MetricCons.Me_is_inherit]:
            metrics_statistics[MetricCons.Me_is_inherit]['is_inherit'] += 1
        else:
            metrics_statistics[MetricCons.Me_is_inherit]['no_inherit'] += 1

    def handle_metrics_is_implement(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        metrics[MetricCons.Me_is_implement] = [self.entity_extensive[rel.src].qualifiedName for rel in
                                               self.query_relation[Constant.implement]['01'][Constant.E_class][
                                                   entity_id]]

    def handle_metrics_filter_is_implement(self, metrics: dict, indicate: list):
        if metrics[MetricCons.Me_is_implement]:
            return True
        return False

    def handle_metrics_statistics_is_implement(self, metrics: dict, metrics_statistics: dict):
        if metrics[MetricCons.Me_is_implement]:
            metrics_statistics[MetricCons.Me_is_implement]['is_implement'] += 1
        else:
            metrics_statistics[MetricCons.Me_is_implement]['no_implement'] += 1

    def handle_metrics_is_new_inherit(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        metrics[MetricCons.Me_is_new_inherit] = (self.entity_extensive[entity_id].parent_class == [])

    def handle_metrics_filter_is_new_inherit(self, metrics: dict, indicate: list):
        if metrics[MetricCons.Me_is_new_inherit]:
            return False
        return True

    def handle_metrics_statistics_is_new_inherit(self, metrics: dict, metrics_statistics: dict):
        if metrics[MetricCons.Me_is_new_inherit]:
            metrics_statistics[MetricCons.Me_is_new_inherit]['new_add_inherit'] += 1
        else:
            metrics_statistics[MetricCons.Me_is_new_inherit]['modify_inherit'] += 1

    def handle_metrics_is_new_implement(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        for interface in self.entity_native[self.entity_extensive[entity_id].entity_mapping].parent_interface:
            if interface not in self.entity_extensive[entity_id].parent_interface:
                metrics[MetricCons.Me_is_new_implement] = False
                break
        metrics[MetricCons.Me_is_new_implement] = True

    def handle_metrics_filter_is_new_implement(self, metrics: dict, indicate: list):
        if metrics[MetricCons.Me_is_new_implement]:
            return False
        return True

    def handle_metrics_statistics_is_new_implement(self, metrics: dict, metrics_statistics: dict):
        if metrics[MetricCons.Me_is_new_implement]:
            metrics_statistics[MetricCons.Me_is_new_implement]['new_add_implement'] += 1
        else:
            metrics_statistics[MetricCons.Me_is_new_implement]['modify_implement'] += 1

    def handle_metrics_is_override(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        metrics[MetricCons.Me_is_override] = [self.entity_extensive[rel.src].qualifiedName for rel in
                                              self.query_relation[Constant.override]['10'][Constant.E_method][
                                                  entity_id]]

    def handle_metrics_filter_is_override(self, metrics: dict, indicate: list):
        if metrics[MetricCons.Me_is_override]:
            return True
        return False

    def handle_metrics_statistics_is_override(self, metrics: dict, metrics_statistics: dict):
        if metrics[MetricCons.Me_is_override]:
            metrics_statistics[MetricCons.Me_is_override]['is_override'] += 1
        else:
            metrics_statistics[MetricCons.Me_is_override]['no_override'] += 1

    def handle_metrics_acceptable_hidden(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        for name in self.hidden_filter_list:
            if self.entity_extensive[entity_id].qualifiedName.startswith(name):
                metrics[MetricCons.Me_acceptable_hidden].append(True)
                break
        metrics[MetricCons.Me_acceptable_hidden].append(False)

    def handle_metrics_filter_acceptable_hidden(self, metrics: dict, indicate: list):
        if False in metrics[MetricCons.Me_acceptable_hidden]:
            return True
        return False

    def handle_metrics_statistics_acceptable_hidden(self, metrics: dict, metrics_statistics: dict):
        if True not in metrics[MetricCons.Me_acceptable_hidden]:
            metrics_statistics[MetricCons.Me_acceptable_hidden]['no_acceptable_hidden'] += 1
        elif False not in metrics[MetricCons.Me_acceptable_hidden]:
            metrics_statistics[MetricCons.Me_acceptable_hidden]['all_acceptable_hidden'] += 1
        else:
            metrics_statistics[MetricCons.Me_acceptable_hidden]['mix_acceptable_hidden'] += 1

    def handle_metrics_unacceptable_non_hidden(self, metrics: dict, rels: List[Relation], target_entity: list):
        pass

    def handle_metrics_inner_scale(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        if not metrics[MetricCons.Me_inner_scale]['inner_class_loc']:
            metrics[MetricCons.Me_inner_scale]['inner_class_loc'] = \
                self.entity_extensive[entity_id].end_line - self.entity_extensive[entity_id].start_line

            parent_outer_class = self.entity_extensive[self.entity_extensive[entity_id].parentId]
            metrics[MetricCons.Me_inner_scale]['outer_class_loc'] = \
                parent_outer_class.end_line - parent_outer_class.start_line

    def handle_metrics_filter_inner_scale(self, metrics: dict, indicate: list):
        per = metrics[MetricCons.Me_inner_scale]['inner_class_loc'] / metrics[MetricCons.Me_inner_scale][
            'outer_class_loc']
        if float(per) >= 0.05:
            return True
        return False

    def handle_metrics_statistics_inner_scale(self, metrics: dict, metrics_statistics: dict):
        per = metrics[MetricCons.Me_inner_scale]['inner_class_loc'] / metrics[MetricCons.Me_inner_scale][
            'outer_class_loc']
        if float(per) < 0.05:
            metrics_statistics[MetricCons.Me_inner_scale]['per_inner_class_loc_0.05'] += 1
        elif float(per) < 0.1:
            metrics_statistics[MetricCons.Me_inner_scale]['per_inner_class_loc_0.1'] += 1
        elif float(per) < 0.2:
            metrics_statistics[MetricCons.Me_inner_scale]['per_inner_class_loc_0.2'] += 1
        else:
            metrics_statistics[MetricCons.Me_inner_scale]['per_inner_class_loc_~'] += 1

    def handle_metrics_interface_number(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        ownership = ['native', 'extensive']
        if not metrics[MetricCons.Me_interface_number]['total']:
            metrics[MetricCons.Me_interface_number]['total'] = len(self.src_relation[entity_id][Constant.define])
            for rel in self.src_relation[entity_id][Constant.define]:
                dest_entity = self.entity_extensive[rel.dest]
                metrics[MetricCons.Me_interface_number][ownership[dest_entity.not_aosp]] += 1
                # metrics[MetricCons.Me_interface_number][dest_entity.category] += 1
                metrics[MetricCons.Me_interface_number][dest_entity.accessible] += 1
                if dest_entity.final:
                    metrics[MetricCons.Me_interface_number]['final'] += 1

    def handle_metrics_statistics_interface_number(self, metrics: dict, metrics_statistics: dict):
        metrics_statistics[MetricCons.Me_interface_number] = {}

    def handle_metrics_add_param(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        metrics[MetricCons.Me_add_param]['count'] += 1
        temp_info = {'param_name': self.entity_extensive[entity_id].name,
                     'param_type': self.entity_extensive[entity_id].raw_type,
                     'used_times': len(self.dest_relation[entity_id][Constant.use])
                     }
        complex_flag = True
        for var_type in MetricCons.Type_complex:
            if var_type in self.entity_extensive[entity_id].raw_type:
                complex_flag = False
                break
        if complex_flag:
            metrics[MetricCons.Me_add_param]['complex_count'] += 1
        metrics[MetricCons.Me_add_param]['detail'].append(temp_info)

    def handle_metrics_filter_add_param(self, metrics: dict, indicate: list):
        if metrics[MetricCons.Me_add_param]['count'] > 1 or metrics[MetricCons.Me_add_param]['complex_count'] > 0:
            return True
        return False

    def handle_metrics_statistics_add_param(self, metrics: dict, metrics_statistics: dict):
        if metrics[MetricCons.Me_add_param]['count'] == 1:
            if metrics[MetricCons.Me_add_param]['complex_count'] == 0:
                metrics_statistics[MetricCons.Me_add_param]['single_simple_param'] += 1
            else:
                metrics_statistics[MetricCons.Me_add_param]['single_complex_param'] += 1
        else:
            if metrics[MetricCons.Me_add_param]['complex_count'] == 0:
                metrics_statistics[MetricCons.Me_add_param]['multi_simple_param'] += 1
            else:
                metrics_statistics[MetricCons.Me_add_param]['multi_complex_param'] += 1

    def handle_metrics_anonymous_class(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        if not metrics[MetricCons.Me_anonymous_class]:
            metrics[MetricCons.Me_anonymous_class] = {
                'is_anonymous_class': self.entity_extensive[entity_id].is_anonymous_class
            }

    def handle_metrics_filter_anonymous_class(self, metrics: dict, indicate: list):
        return not metrics[MetricCons.Me_anonymous_class]['is_anonymous_class']

    def handle_metrics_statistics_anonymous_class(self, metrics: dict, metrics_statistics: dict):
        if metrics[MetricCons.Me_anonymous_class]['is_anonymous_class']:
            metrics_statistics[MetricCons.Me_anonymous_class]['is_anonymous_class'] += 1
        else:
            metrics_statistics[MetricCons.Me_anonymous_class]['is_not_anonymous_class'] += 1

    def handle_metrics_open_in_sdk(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        if len(self.sdk_apis[self.entity_extensive[entity_id].qualifiedName]) == 1:
            metrics[MetricCons.Me_open_in_sdk]['in_sdk'].append(self.entity_extensive[entity_id].to_string())
        elif len(self.sdk_apis[self.entity_extensive[entity_id].qualifiedName]) > 1:
            for api in self.sdk_apis[self.entity_extensive[entity_id].qualifiedName]:
                if api['params'] == self.entity_extensive[entity_id].parameter_types:
                    metrics[MetricCons.Me_open_in_sdk]['in_sdk'].append(self.entity_extensive[entity_id].to_string())
                    break
            metrics[MetricCons.Me_open_in_sdk]['not_in_sdk'].append(self.entity_extensive[entity_id].to_string())
        else:
            metrics[MetricCons.Me_open_in_sdk]['not_in_sdk'].append(self.entity_extensive[entity_id].to_string())

    def handle_metrics_filter_open_in_sdk(self, metrics: dict, indicate: list):
        return len(metrics[MetricCons.Me_open_in_sdk]['in_sdk']) > 0

    def handle_metrics_statistics_open_in_sdk(self, metrics: dict, metrics_statistics: dict):
        if len(metrics[MetricCons.Me_open_in_sdk]['in_sdk']) == 0:
            metrics_statistics[MetricCons.Me_open_in_sdk]['all_not_in_sdk'] += 1
        elif len(metrics[MetricCons.Me_open_in_sdk]['not_in_sdk']) == 0:
            metrics_statistics[MetricCons.Me_open_in_sdk]['all_in_sdk'] += 1
        else:
            metrics_statistics[MetricCons.Me_open_in_sdk]['mix_in_sdk'] += 1
