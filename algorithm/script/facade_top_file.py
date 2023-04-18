import os
from typing import List
from algorithm.utils import FileCSV


class FileTop:
    dimension: List[str]
    file_name: str
    out_path: str

    def __init__(self, file_name: str, dimension: List[str], out_path: str):
        self.file_name = file_name
        self.dimension = dimension
        self.out_path = out_path

    def get_top_files(self, projects: List[tuple[str, str]], dim: str, top: float):

        def fetch_all(file_list: List[dict]) -> List[dict]:
            temp = []
            for file in file_list:
                if file[dim] == '':
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
            sorted_files = sorted(v_ins, key=lambda x: get_num(x[dim]), reverse=True)
            all_files = fetch_all(sorted_files)
            top_files = fetch_top(all_files, int(len(all_files) * top))
            p_top_files_data.append(top_files)
            p_top_files.append(set([file['file'] for file in top_files]))
        return p_top_files, p_top_files_data

    def write_res(self, keys: str, projects: List[tuple[str, str]], top_files: List[set],
                  top_files_data: List[List[dict]], top: float, dim: str):
        for data, project in zip(top_files_data, projects):
            FileCSV.write_dict_to_csv(self.out_path, f'{project[0]}_{dim}_{str(top)}', data, 'w')

        union_file = top_files[0]
        inter_file = top_files[0]
        for p_top in top_files:
            inter_file = inter_file & p_top
            union_file = inter_file | p_top

        FileCSV.base_write_to_csv(self.out_path, f'{keys}inter_top_files_{dim}_{str(top)}', list(inter_file))
        FileCSV.base_write_to_csv(self.out_path, f'{keys}union_top_files_{dim}_{str(top)}', list(union_file))
        FileCSV.write_dict_to_csv(self.out_path, f'inter_union_top_files',
                                  [{f'{keys}inter_union_{dim}_{str(top)}': float(len(inter_file) / len(union_file))}], 'a')

    def start_analysis(self, dims: List[str], top: float, **projects):
        keys = ""
        vals = []
        for k, v in projects.items():
            keys += f'{str(k)}_'
            vals.extend(v)
        for dim in dims:
            p_top_files, p_top_files_data = self.get_top_files(vals, dim, top)
            self.write_res(keys, vals, p_top_files, p_top_files_data, top, dim)


def get_num(str_num: str):
    if str_num == '' or str_num == 'null':
        return 0
    else:
        return int(str_num)
