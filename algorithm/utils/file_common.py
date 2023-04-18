import os
import re
from typing import List
from algorithm.utils import FileCSV


class FileCommon:
    @classmethod
    def read_from_file_by_line(cls, file_path: str) -> List[str]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                res = []
                for line in f.readlines():
                    line = line.strip('\n')
                    if "\"" in line:
                        print(line)
                        res.append(re.findall(r"\"(.+?)\"", line)[0])
                return res
        except Exception as e:
            raise e


if __name__ == '__main__':
    FileCSV.base_write_to_csv('D:\\Honor\\match_res\\LineageOS\\base\\lineage-18.1', 'sdk_api',
                              FileCommon.read_from_file_by_line(
                                  'D:\\Honor\\source_code\\LineageOS\\base\\api\\current.txt'))
