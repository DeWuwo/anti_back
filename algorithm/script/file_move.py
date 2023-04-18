import os

from algorithm.utils import Command
from typing import List


class FileMove:
    @classmethod
    def file_move(cls, src_path: str, dest_path: str, file_set: List[str]):
        for file in file_set:
            src_file = os.path.join(src_path, file)
            dest_file = os.path.join(dest_path)
            if not os.path.exists(dest_file):
                os.makedirs(dest_file)
            print(src_file, dest_file)
            Command.command_run(f'copy /Y {src_file} {dest_file}')