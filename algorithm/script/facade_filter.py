import os
from typing import List
from collections import defaultdict
from functools import partial
from algorithm.utils import FileCSV, FileJson, Constant


class FacadeFilter:
    file_path: str
    file_name: str
    relation_types: List[str]

    def __init__(self, file_path: str, file_name: str, relation_types: List[str]):
        self.file_path = file_path
        self.file_name = os.path.join(file_path, file_name)
        self.relation_types = relation_types

    def facade_filter(self):
        res = {}
        file_res = defaultdict(partial(defaultdict, int))
        facade_info = FileJson.read_base_json(self.file_name)
        n2e: List[dict] = facade_info['res']['n2e']
        e2n: List[dict] = facade_info['res']['e2n']
        for rel_type in self.relation_types:
            res[rel_type + '_e2n'] = 0
            res[rel_type + '_n2e'] = 0
        for rel in e2n:
            src_e = rel['src']
            dest_e = rel['dest']
            rel_type: str = ''
            for k in rel['values'].keys():
                rel_type = str(k)
                break
            if rel_type in self.relation_types:
                if rel_type == Constant.R_annotate:
                    if dest_e['category'] == Constant.E_variable:
                        continue
                    file_res[dest_e['File']]['e2n_e'] += 1
                    file_res[src_e['File']]['e2n_n'] += 1
                res[rel_type + '_e2n'] += 1
                file_res[src_e['File']]['e2n_e'] += 1
                file_res[dest_e['File']]['e2n_n'] += 1
        for rel in n2e:
            src_e = rel['src']
            dest_e = rel['dest']
            rel_type: str = ''
            for k in rel['values'].keys():
                rel_type = str(k)
                break
            if rel_type in self.relation_types:
                if rel_type == Constant.R_annotate:
                    if dest_e['category'] == Constant.E_variable:
                        continue
                    if src_e['qualifiedName'] in ["com.android.internal.annotations.GuardedBy",
                                                  "android.telephony.data.ApnSetting.ApnType"]:
                        continue
                    file_res[dest_e['File']]['n2e_n'] += 1
                    file_res[src_e['File']]['n2e_e'] += 1
                res[rel_type + '_n2e'] += 1
                file_res[src_e['File']]['n2e_n'] += 1
                file_res[dest_e['File']]['n2e_e'] += 1
        FileCSV.write_dict_to_csv(self.file_path, 'facade_filter', [res], 'w')
        FileCSV.write_file_to_csv(self.file_path, 'facade_file_filter', file_res, 'file',
                                  ['e2n_e', 'e2n_n', 'n2e_n', 'n2e_e'])

    def filter_hidden(self):
        res = defaultdict(partial(defaultdict, int))
        intrusive_res = {}
        hidden_json = defaultdict(list)
        rel_json = defaultdict(list)
        facade_info = FileJson.read_base_json(self.file_name)
        n2e: List[dict] = facade_info['res']['n2e']
        e2n: List[dict] = facade_info['res']['e2n']
        heads_hd_rel = []
        heads_hd_intrusive = []
        hidden_level = [Constant.HD_blacklist, Constant.HD_greylist,
                        Constant.HD_whitelist] + Constant.HD_greylist_max_list
        for label in hidden_level:
            for rel in Constant.Relations:
                heads_hd_rel.append(f'{label}_{rel}')
        for label in hidden_level:
            heads_hd_intrusive.append(f'{label}_1')
            intrusive_res.update({f'{label}_1': 0, f'{label}_0': 0})
            heads_hd_intrusive.append(f'{label}_0')

        for rel in e2n:
            src_e = rel['src']
            dest_e = rel['dest']
            rel_type: str = ''
            for k in rel['values'].keys():
                rel_type = str(k)
                if rel_type == 'Typed':
                    qualifiedName: str = src_e['qualifiedName']
                    temp = qualifiedName.rsplit('.', 2)
                    if temp[1][0].isupper() and temp[1] not in temp[0]:
                        rel_type = 'Aggregate'
                break
            try:
                if rel_type == Constant.R_annotate:
                    hidden_flag = Constant.hidden_map(src_e['hidden'])
                    is_intrusive = src_e['isIntrusive']
                else:
                    hidden_flag = Constant.hidden_map(dest_e['hidden'])
                    is_intrusive = dest_e['isIntrusive']
                if src_e['not_aosp'] != dest_e['not_aosp'] and \
                        hidden_flag in [Constant.HD_blacklist,
                                        Constant.HD_greylist, Constant.HD_whitelist] + Constant.HD_greylist_max_list:
                    res[dest_e['qualifiedName']][hidden_flag + '_' + rel_type] += 1
                    if rel_type == Constant.call:
                        intrusive_res[f'{hidden_flag}_{is_intrusive}'] += 1
                    hidden_json[hidden_flag + '_' + rel_type + '_e2n'].append(rel)
            except KeyError:
                pass
        for rel in n2e:
            src_e = rel['src']
            dest_e = rel['dest']
            rel_type: str = ''
            for k in rel['values'].keys():
                rel_type = str(k)
                break
            try:
                if rel_type == Constant.R_annotate:
                    hidden_flag = Constant.hidden_map(dest_e['hidden'])
                else:
                    hidden_flag = Constant.hidden_map(src_e['hidden'])
                if src_e['not_aosp'] != dest_e['not_aosp'] and \
                        hidden_flag in [Constant.HD_blacklist,
                                        Constant.HD_greylist, Constant.HD_whitelist] + Constant.HD_greylist_max_list:
                    # res[src_e['qualifiedName']][hidden_flag + '_' + rel_type + '_n2e'] += 1
                    hidden_json[hidden_flag + '_' + rel_type + '_n2e'].append(rel)
            except KeyError:
                pass
        FileCSV.write_file_to_csv(self.file_path, 'facade_hidden_filter', res, 'name', heads_hd_rel)
        FileCSV.write_dict_to_csv(self.file_path, 'facade_hidden_intrusive_count', [intrusive_res], 'w')
        FileJson.write_data_to_json(self.file_path, hidden_json, 'facade_hidden_hidden.json')
        # FileJson.write_data_to_json(self.file_path, rel_json, 'facade_hidden_rel.json')

    def get_facade_files(self):
        e2n, n2e = self.load_facade()
        file_set = set()
        for rel in e2n + n2e:
            src_e = rel['src']
            dest_e = rel['dest']
            file_set.add(src_e['File'])
            file_set.add(dest_e['File'])
        return file_set

    def load_facade(self):
        facade_info = FileJson.read_base_json(self.file_name)
        n2e: List[dict] = facade_info['res']['n2e']
        e2n: List[dict] = facade_info['res']['e2n']
        return e2n, n2e

    def get_facade_conf(self, project: str):
        conf_file_set = []
        inter_set = []
        conf_info = FileCSV.read_from_file_csv(os.path.join(self.file_path, 'conf_files.csv'), False)
        for line in conf_info:
            for file_name in line:
                conf_file_set.append(file_name)
        facade_file_set = self.get_facade_files()
        for conf in conf_file_set:
            if conf in facade_file_set:
                inter_set.append(conf)
        # inter_set = facade_file_set & conf_file_set
        return {'project': project, 'conf_files': len(conf_file_set), 'facade_files': len(facade_file_set),
                'inter_set': len(inter_set), 'rate': float(len(inter_set)/len(conf_file_set)),'files': list(inter_set)}
