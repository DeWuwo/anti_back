import csv
import sys
import json
import time
from collections import defaultdict
from pathlib import Path
from typing import List, Optional, Dict
import argparse
import git
from concurrent.futures import as_completed

from algorithm.model.blamer.move_detect import distill_move_edit_list, MoveEdit
from algorithm.utils import MyThread

refactor_move_cache: Dict[str, Dict[str, List[MoveEdit]]] = {}


def search_refactoring(category: str, longname: str, unsure_params: str, unsure_filepath: str,
                       refactor_data: List[dict], commit: str) -> List[MoveEdit]:
    try:
        move_edits = refactor_move_cache[commit]
    except KeyError:
        move_edits = distill_move_edit_list(refactor_data)
        refactor_move_cache[commit] = move_edits
    ret = []

    try:
        for move in move_edits[category + longname]:
            to_state = move.to_state
            if unsure_params == "null" or to_state.get_param() == unsure_params:
                ret.append(move)
    except KeyError:
        return ret
    return ret


def search_refactoring_by_id(category: str, longname: str, unsure_params: str, unsure_filepath: str,
                             refactor_data: List[dict]) -> List[MoveEdit]:
    move_edits = distill_move_edit_list(refactor_data)
    ret = []
    try:
        for move in move_edits[category + longname]:
            to_state = move.to_state
            if unsure_params == "null" or to_state.get_param() == unsure_params:
                ret.append(move)
    except KeyError:
        return ret
    return ret


OwnerShipData = Dict[str, str]


def resolve_unsure(repo_path: Path, not_sure_line: OwnerShipData, sorted_commits: Dict[str, int],
                   refactor_data: Dict[str, List[dict]], flag: bool):
    unsure_longname = not_sure_line["Entity"]
    unsure_filepath = not_sure_line["file path"]
    unsure_param = not_sure_line["param_names"]
    unsure_category = not_sure_line["category"]
    related_moves = []
    if flag:
        unsure_id = not_sure_line['id']
        related_moves = search_refactoring_by_id(unsure_category, unsure_longname, unsure_param,
                                                 unsure_filepath, refactor_data[unsure_id])
    else:
        repo = git.Repo(repo_path)
        third_party_commits = json.loads(not_sure_line["accompany commits"])
        # if unsure_category == 'Variable' and unsure_longname.rsplit('.', 1)[1] not in unsure_param:
        #     return None
        third_sorted_commits = sorted(third_party_commits, key=lambda k: sorted_commits[k], reverse=False)
        # commit = repo.commit(third_sorted_commits[0])
        commit = third_sorted_commits[0]
        try:
            refactor_info = refactor_data[str(commit)]
        except KeyError:
            refactor_info = {}
        if refactor_info:
            related_moves = search_refactoring(unsure_category, unsure_longname, unsure_param, unsure_filepath,
                                               refactor_info, str(commit))
        else:
            related_moves = []
    if not related_moves:
        return None
    return related_moves


RefactorData = Dict[str, List[dict]]


def load_refactor_data(file_path: Path, ref_data) -> RefactorData:
    ret = defaultdict(list)
    if ref_data:
        for r in ref_data:
            ret[r["sha1"]] = r["refactorings"]
        return ret
    refactor_obj = json.loads(file_path.read_text())
    for r in refactor_obj["commits"]:
        ret[r["sha1"]] = r["refactorings"]
    return ret
    # todo: tojson
    # if ref_data:
    #     return ref_data
    # refactor_obj = json.loads(file_path.read_text())
    # return refactor_obj["commits"]


def load_refactor_data_id(file_path: Path) -> RefactorData:
    refactor_obj: dict = json.loads(file_path.read_text())
    ret = defaultdict(list)
    for k, v in refactor_obj.items():
        ret[k] = v['Moves']
    return ret


def load_not_sure_lines(file_path: Path) -> List[OwnerShipData]:
    head = ["Entity", "category", "id", "param_names", "file path", "commits", "base commits", "third party commits"]
    ret = []
    with open(file_path) as file:
        reader = csv.DictReader(file, head)
        reader.__next__()
        for row in reader:
            ret.append(dict(row))

    return ret


def resolution_entry():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refactor_path", dest="refactor_path", action="store")
    parser.add_argument("--repo", dest="repo_path", action="store")
    parser.add_argument("--unsure_ownership", dest="unsure_ownership", action="store")
    parser.add_argument("-o", dest="output", action="store")
    args = parser.parse_args()

    refactor_path = Path(args.refactor_path)
    repo_path = Path(args.repo_path)
    unsure_ownership = args.unsure_ownership

    refactor_data = load_refactor_data(refactor_path)
    not_sure_rows = load_not_sure_lines(Path(unsure_ownership))

    move_list = list()

    for row in not_sure_rows:
        moves = resolve_unsure(repo_path, row, refactor_data)
        if moves:
            row_dict = dict()
            for k, v in row.items():
                try:
                    row_dict[k] = json.loads(v)
                except json.JSONDecodeError:
                    row_dict[k] = v
            row_dict["Moves"] = [m.refactor_obj for m in moves]
            move_list.append(row_dict)

    out_name = args.output if args.output else "unsure_resolution.json"
    with open(out_name, "w") as file:
        json.dump(move_list, file, indent=4)


def load_entity_refactor(repo_path: str, refactor_path: str, sorted_extensive_commits: list,
                         ref_data: List, unsure_refactor: str,
                         not_sure_rows: List[dict], out_path: str):
    refactor_path = Path(refactor_path)
    repo_path = Path(repo_path)
    unsure_path = Path(unsure_refactor)
    # unsure_ownership = unsure_ownership
    refactor_cache = False
    if unsure_path.exists():
        refactor_data = load_refactor_data_id(unsure_path)
        refactor_cache = True
    else:
        refactor_data = load_refactor_data(refactor_path, ref_data)
    # not_sure_rows = load_not_sure_lines(Path(unsure_ownership))

    ref_ent_write: Dict[int, dict] = {}
    ref_ent: Dict[int, list] = {}

    def resolve_refactor_to_entity(entities: List[dict], *index):
        move_list_write: Dict[int, dict] = {}
        move_list: Dict[int, list] = {}
        sorted_commits: Dict[str, int] = {}
        for index, cmt in enumerate(sorted_extensive_commits):
            sorted_commits[cmt] = index

        total = len(entities)
        i = 0
        for row in entities:
            i += 1
            print("\r", end="")
            print(f"       Refactor detect: {i}/{total}", end="")
            sys.stdout.flush()
            moves = resolve_unsure(repo_path, row, sorted_commits, refactor_data, refactor_cache)
            if moves:
                row_dict = dict()
                for k, v in row.items():
                    try:
                        row_dict[k] = json.loads(v)
                    except json.JSONDecodeError:
                        row_dict[k] = v
                row_dict["Moves"] = [m.refactor_obj for m in moves]
                move_list_write[int(row_dict['id'])] = row_dict
                move_list[int(row_dict['id'])] = [row_dict,
                                                  [[m.refactor_obj['type'], m.src_state, m.to_state] for m in moves]]
        return move_list_write, move_list

    ref_ent_write, ref_ent = resolve_refactor_to_entity(not_sure_rows)
    with open(f"{out_path}/unsure_resolution.json", "w") as file:
        json.dump(ref_ent_write, file, indent=4)
    return ref_ent


if __name__ == '__main__':
    resolution_entry()
