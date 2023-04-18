import os
import csv
from typing import List
from algorithm.utils import FileCSV, Constant


class IntrusiveCompare:
    dimension: List[str]
    file_name: str
    out_path: str

    def __init__(self):
        self.file_name = 'final_ownership_file_count.csv'
        self.dimension = ['native', 'obsoletely native', 'intrusive', 'extensive']
        self.out_path = "D:\\Honor\\match_res\\intrusive_analysis"

    def get_top_files(self, projects: List[tuple[str, str]], dim: int, top: float):

        def fetch_all(file_list: List[dict]) -> List[dict]:
            temp = []
            for file in file_list:
                if file[self.dimension[dim]] == '':
                    return temp
                temp.append(file)
            return temp

        def fetch_top(file_list: List[dict], scope: int) -> List[dict]:
            temp = []
            for index in range(scope):
                temp.append(file_list[index])
            return temp

        p_top_files: List[set] = []
        p_top_files_data = []
        for project in projects:
            v_ins = FileCSV.read_dict_from_csv(os.path.join(project[1], self.file_name))
            sorted_files = sorted(v_ins, key=lambda x: get_num(x[self.dimension[dim]]), reverse=True)
            all_files = fetch_all(sorted_files)
            top_files = fetch_top(all_files, int(len(all_files) * top))
            p_top_files_data.append(top_files)
            p_top_files.append(set([file['file'] for file in top_files]))
        return p_top_files, p_top_files_data

    def write_res(self, keys: str, projects: List[tuple[str, str]], top_files: List[set],
                  top_files_data: List[List[dict]],
                  top: float):
        for data, project in zip(top_files_data, projects):
            FileCSV.write_dict_to_csv(self.out_path, project[0] + '-' + str(top), data, 'w')

        union_file = top_files[0]
        inter_file = top_files[0]
        for p_top in top_files:
            inter_file = inter_file & p_top
            union_file = inter_file | p_top

        FileCSV.base_write_to_csv(self.out_path, f'{keys}inter_top_files_{str(top)}', list(inter_file))
        FileCSV.base_write_to_csv(self.out_path, f'{keys}union_top_files_{str(top)}', list(union_file))
        FileCSV.write_dict_to_csv(self.out_path, f'inter_union_top_files',
                                  [{f'{keys}inter_union_{str(top)}': float(len(inter_file) / len(union_file))}], 'a')

    def start_analysis(self, dim: int, top: float, **projects):
        keys = ""
        vals = []
        for k, v in projects.items():
            keys += f'{str(k)}_'
            vals.extend(v)
        p_top_files, p_top_files_data = self.get_top_files(vals, dim, top)
        self.write_res(keys, vals, p_top_files, p_top_files_data, top)

    def get_intrusive_commit(self, projects: List[tuple[str, str]]):
        final_res = []
        final_res_total = []
        for project in projects:
            res = {}
            for cat in [Constant.E_class, Constant.E_interface, Constant.E_annotation, 'Enum', 'Enum Constant',
                        Constant.E_method,
                        Constant.E_variable]:
                res[cat] = {'1': 0, '2': 0, '3': 0, '>3': 0}
            res_total = {'project': project[0], '1': 0, '2': 0, '3': 0, '>3': 0}
            commits_data = FileCSV.read_dict_from_csv(os.path.join(project[1], 'mixed_entities.csv'))
            for commit_data in commits_data:
                category = commit_data['category']
                commits: str = commit_data['accompany commits']
                commit_count = commits.count(',') + 1
                field = str(commit_count)
                if commit_count > 3:
                    field = '>3'
                res[category][field] += 1
                res_total[field] += 1
            for cat, val in res.items():
                print(cat, val)
                dic = {'project': project[0], 'category': cat}
                dic.update(val)
                final_res.append(dic)

            final_res_total.append(res_total)
            FileCSV.write_dict_to_csv(self.out_path, 'commit_count', final_res, 'w')
            FileCSV.write_dict_to_csv(self.out_path, 'commit_count_total', final_res_total, 'w')


def get_num(str_num: str):
    if str_num == '' or str_num == 'null':
        return 0
    else:
        return int(str_num)

def get(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        info = [line[0] for line in reader]
        info.sort()
        tt = set(info)
        files = list(tt)
        files.sort()
        str_files = ';'.join(files)
        print(len(files))
        print(str_files)

        pkgs = list(set([file.rsplit('/', 1)[0] for file in files]))
        pkgs.sort()
        str_pkgs = ';'.join(pkgs)
        print(len(pkgs))
        print(str_pkgs)


if __name__ == '__main__':
    ins_a = IntrusiveCompare()
    projects = [('lineage_lineage18.1-16.0', 'D:\\Honor\\match_res\\LineageOS\\base\\lineage_lineage18.1-16.0'),
                ('lineage_lineage18.1-17.1', 'D:\\Honor\\match_res\\LineageOS\\base\\lineage_lineage18.1-17.1'),
                ('lineage_lineage18.1-18.1', 'D:\\Honor\\match_res\\LineageOS\\base\\lineage_lineage18.1-18.1'),
                ('lineage_lineage18.1-19.1', 'D:\\Honor\\match_res\\LineageOS\\base\\lineage_lineage18.1-19.1')]
