import csv
import json as J
import sys
from collections import defaultdict
from pathlib import Path
from typing import Set, Dict, IO, Optional, List, TypedDict


def get_files(refactor_obj):
    file_set = set()
    for code_element in refactor_obj["leftSideLocations"] + refactor_obj["rightSideLocations"]:
        file_set.add(code_element["filePath"])
    return list(file_set)


def add_file_refactor_statistic(file_refactor_dict, file_list, ty):
    for file in file_list:
        file_refactor_dict[file][ty] += 1


class RefactorObj(TypedDict):
    type: str
    description: str
    leftSideLocations: list
    rightSideLocations: list


class RefactorData:
    refactor_type: Set[str]
    refactor_statistic: Dict[str, int]
    file_refactor_mapping: Dict[str, Dict[str, int]]
    commit_len: int

    def __init__(self, file_path: Path):
        self.refactor_type = set()
        self.refactor_statistic = defaultdict(int)
        self.commit_len = -1
        self.commit_list = []
        self.refactor_data = dict()
        self.refactor_dict = dict()
        self.file_refactor_mapping = defaultdict(lambda: defaultdict(int))
        self.load_refactoring_data(file_path)

    def load_refactoring_data(self, file_path: Path):
        with open(file_path) as file:
            refactor_data = J.load(file)
            self.refactor_data = refactor_data
            all_refactors = refactor_data["commits"]
            self.commit_len = len(all_refactors)
            for commit_refactor in all_refactors:
                sha = commit_refactor["sha1"]
                self.commit_list.append(sha)
                self.refactor_dict[sha] = commit_refactor["refactorings"]
                for refactor_obj in commit_refactor["refactorings"]:
                    ty = refactor_obj["type"]
                    self.refactor_type.add(ty)
                    self.refactor_statistic[ty] += 1
                    file_list = get_files(refactor_obj)
                    add_file_refactor_statistic(self.file_refactor_mapping, file_list, ty)

    def dump_statistic(self, fp: IO):
        import csv as C
        writer = C.writer(fp)
        writer.writerow(["type", "number"])
        content = []
        for ty, count in self.refactor_statistic.items():
            content.append([ty, count])
        content.sort(key=lambda t: -t[1])
        writer.writerows(content)

    def dump_type(self, fp: IO):
        J.dump(list(self.refactor_type), fp, indent=4)

    def dump_least(self, fp: IO, ty_name):
        all_refactors = self.refactor_data["commits"]
        self.commit_len = len(all_refactors)
        cur_max = 9999
        cur_obj = None
        for commit_refactor in all_refactors:
            for refactor_obj in commit_refactor["refactorings"]:
                ty = refactor_obj["type"]
                if ty == ty_name:
                    code_element_len = len(refactor_obj["leftSideLocations"]) + len(refactor_obj["rightSideLocations"])
                    if code_element_len < cur_max:
                        cur_max = code_element_len
                        cur_obj = commit_refactor
        J.dump(cur_obj, fp)

    def get_refactor(self, sha) -> list:
        return self.refactor_dict[sha]

    def get_next(self, sha) -> Optional[str]:
        next_index = self.commit_list.index(sha) + 1
        return None if next_index == len(self.commit_list) else self.commit_list[next_index]

    def get(self, sha: str) -> List[dict]:
        return self.refactor_dict[sha]

    def dump_file_refactor(self, file: IO, file_list):
        writer = csv.writer(file)
        refactor_list = list(self.refactor_type)
        head = ["file"] + refactor_list
        rows = []
        for file_name in file_list:
            row = [file_name]
            for refactor_type in refactor_list:
                row.append(self.file_refactor_mapping[file_name][refactor_type])
            rows.append(row)
        writer.writerows([head] + rows)


def entry():
    data_path = Path(sys.argv[1])
    root_dir = Path(sys.argv[2])
    file_list = [str(p.relative_to(root_dir)).replace("\\", "/") for p in root_dir.glob("**/*.java")]
    refactor_data = RefactorData(data_path)
    # with open("refactor_type.json", "w") as file:
    #     refactor_data.dump_type(file)
    #
    # with open("refactor_statistic.csv", "w", newline="") as file:
    #     refactor_data.dump_statistic(file)

    with open("minimal_add_annotation.json", "w") as file:
        refactor_data.dump_least(file, "Add Method Annotation")

    with open("file_level_refactoring.csv", "w", newline="") as file:
        refactor_data.dump_file_refactor(file, file_list)

    print(refactor_data.commit_len)


if __name__ == "__main__":
    entry()
