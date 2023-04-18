import os
from typing import List
from algorithm.utils import FileCSV


class IntrusiveFilter:
    file_name: str
    out_path: str

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.out_path = 'D:\\Honor\\match_res\\intrusive_api'

    def facade_top_file_api(self, project, file_set: List[str]):
        intrusive_res = []
        intrusive_info = FileCSV.read_dict_from_csv(os.path.join(project, self.file_name))
        for exa in intrusive_info:
            if exa['isIntrusive'] == '1' and exa['file_path'] in file_set:
                intrusive_res.append(exa['qualifiedName'])
        FileCSV.base_write_to_csv(project, f'top_files_intrusive_api', intrusive_res)
        return intrusive_res

    def get_inter_api(self, projects: list, file_set):
        inter_api = set()
        files = set()
        for proj in projects:
            files.add(proj[0])
            apis = self.facade_top_file_api(proj[1], file_set)
            if projects.index(proj) == 0:
                inter_api = set(apis)
            else:
                inter_api = inter_api & set(apis)
        file_inter = '_'.join(list(files))
        FileCSV.base_write_to_csv(self.out_path, f'{file_inter}_top_files_intrusive_api_inter', list(inter_api))
