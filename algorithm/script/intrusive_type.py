import os
import json
from typing import List
from algorithm.utils import FileCSV


class IntrusiveType:
    dimension: List[str]
    file_name: str
    out_path: str

    def __init__(self):
        self.file_name = 'intrusive_file_count.csv'
        self.out_path = "D:\\Honor\\match_res\\intrusive_analysis"

        # import_extension

    def get_filter(self, project: str, dim: str, file_set: set):
        file_intrusive = FileCSV.read_dict_from_csv(os.path.join(project, self.file_name))
        count = 0
        total = 0
        for file_res in file_intrusive:
            if file_res[dim]:
                total += int(file_res[dim])
                if file_res['file'] in file_set:
                    count += int(file_res[dim])
        print(count)
        print(total)

    def start_filter(self, project, file_android: str):
        file_set_android = set()
        with open(file_android) as a:
            android = json.load(a, strict=False)
            entities_aosp = android['variables']
        for item in entities_aosp:
            if not item['external']:
                if item['category'] == 'File':
                    file_set_android.add(item['File'])

        self.get_filter(project, 'import_extension', file_set_android)

    def run_filter(self, projects: List[tuple[str, str]]):
        for proj in projects:
            self.start_filter(proj[0], proj[1])
