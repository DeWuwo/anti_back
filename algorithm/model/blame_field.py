import os
from typing import Dict
from algorithm.utils.file_csv import FileCSV


class BlameField:
    file_path: str
    module_blame: Dict

    def __init__(self, file_path):
        self.file_path = os.path.join(file_path, 'blame_field.csv')
        self.module_blame = {}

    def read_blame_field(self):
        try:
            reader_res = FileCSV.read_from_file_csv(self.file_path, True)
        except Exception as e:
            reader_res = {}
        for blame in reader_res:
            for file in blame[2].split(';'):
                if file == "*":
                    file = ""
                self.module_blame[blame[1] + file] = blame[3]
        return self.module_blame
