import argparse
import csv
import json
import re
from pathlib import Path
from typing import List, Iterable

from algorithm.model.blamer.dep_blamer import load_commits


def load_authors(file_path: Path) -> List[str]:
    ret = []
    authors_obj = json.loads(file_path.read_text())
    for author in authors_obj:
        if isinstance(author, dict) and "name" in author:
            ret.append(author["name"])
    return ret


def only(commit_list: Iterable[str], accompany_authors: Iterable[str]):
    for commit in commit_list:
        if commit not in accompany_authors:
            return False
    return True


def entry():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_commits", dest="base_commits", action="store")
    parser.add_argument("--only_accompany_commits", dest="only_accompany_commits", action="store")
    parser.add_argument("--ownership", dest="ownership", action="store")
    parser.add_argument("-o", dest="name", action="store")
    args = parser.parse_args()
    base_commits = load_commits(Path(args.base_commits))
    accompany_commits = load_commits(Path(args.only_accompany_commits))

    break_changes = []
    accompany_changes = []
    all_changes = []

    with open(args.ownership, "r") as file:
        reader = csv.DictReader(file, ["Entity", "category", "id", "param_names", "file path", "commits"])
        reader.__next__()
        for row in reader:
            ent_commits = set(json.loads(row["commits"]))
            ent_base_commits = ent_commits.intersection(base_commits)
            ent_accompany_commits = ent_commits.intersection(accompany_commits)
            row["base commits"] = json.dumps(list(ent_base_commits))
            row["accompany commits"] = json.dumps(list(ent_accompany_commits))
            all_changes.append(row)
            if len(ent_accompany_commits) != 0 and len(ent_base_commits) == 0:
                accompany_changes.append(row)
            elif len(ent_accompany_commits) != 0 and len(ent_base_commits) != 0:
                break_changes.append(row)
    matches = re.match("(.*)_(.*)_ownership_lineageos\\.csv", args.ownership)
    if args.name:
        name = args.name
    else:
        project_name = matches[1]
        sha = matches[2]
        name = f"{project_name}_{sha}"
    dump_ent_commit_infos(break_changes, f"{name}_mixed_entities.csv")
    dump_ent_commit_infos(accompany_changes, f"{name}_pure_accompany_entities.csv")
    dump_ent_commit_infos(all_changes, f"{name}_all_entities.csv")


def dump_ent_commit_infos(ent_commit_infos, file_name: str):
    with open(file_name, "w", newline="") as file:
        writer = csv.DictWriter(file, ["Entity", "category", "id", "param_names", "file path", "commits",
                                       "base commits", "old base commits", "accompany commits"])
        writer.writeheader()
        for row in ent_commit_infos:
            writer.writerow(row)


def get_entity_owner(base_commit: str, old_base_commits: str, only_accompany_commits: str, ownership: str,
                     out_path: str):
    print('blame get entity owner')
    base_commits = load_commits(Path(base_commit))
    old_base_commits = load_commits(Path(old_base_commits))
    accompany_commits = load_commits(Path(only_accompany_commits))

    all_changes = []
    all_native_changes = []
    old_native_changes = []
    old_update_changes = []
    intrusive_changes = []
    old_intrusive_changes = []
    pure_accompany_changes = []

    all_entities = {}
    all_native_entities = {}
    old_native_entities = {}
    old_update_entities = {}
    intrusive_entities = {}
    old_intrusive_entities = {}
    pure_accompany_entities = {}

    with open(ownership, "r") as file:
        reader = csv.DictReader(file, ["Entity", "category", "id", "param_names", "file path", "commits"])
        reader.__next__()
        for row in reader:
            ent_commits = set(json.loads(row["commits"]))
            ent_base_commits = ent_commits.intersection(base_commits)
            ent_old_base_commits = ent_commits.intersection(old_base_commits)
            ent_accompany_commits = ent_commits.intersection(accompany_commits)
            row["base commits"] = json.dumps(list(ent_base_commits))
            row["old base commits"] = json.dumps(list(ent_old_base_commits))
            row["accompany commits"] = json.dumps(list(ent_accompany_commits))
            all_changes.append(row)
            all_entities[int(row['id'])] = row
            if len(ent_accompany_commits) != 0:
                if len(ent_base_commits) == 0 and len(ent_old_base_commits) == 0:
                    pure_accompany_changes.append(row)
                    pure_accompany_entities[int(row['id'])] = row
                elif len(ent_base_commits) != 0 and len(ent_old_base_commits) == 0:
                    intrusive_changes.append(row)
                    intrusive_entities[int(row['id'])] = row
                elif len(ent_old_base_commits) != 0:
                    old_intrusive_changes.append(row)
                    old_intrusive_entities[int(row['id'])] = row
            elif len(ent_accompany_commits) == 0:
                if len(ent_base_commits) == 0 and len(ent_old_base_commits) != 0:
                    old_native_changes.append(row)
                    old_native_entities[int(row['id'])] = row
                elif len(ent_base_commits) != 0 and len(ent_old_base_commits) == 0:
                    all_native_changes.append(row)
                    all_native_entities[int(row['id'])] = row
                elif len(ent_old_base_commits) != 0 and len(ent_old_base_commits) != 0:
                    old_update_changes.append(row)
                    old_update_entities[int(row['id'])] = row

    dump_ent_commit_infos(all_changes, f"{out_path}/all_entities.csv")
    dump_ent_commit_infos(all_native_changes, f"{out_path}/all_native_entities.csv")
    dump_ent_commit_infos(old_native_changes, f"{out_path}/old_native_entities.csv")
    dump_ent_commit_infos(old_update_changes, f"{out_path}/old_update_entities.csv")
    dump_ent_commit_infos(intrusive_changes, f"{out_path}/mixed_entities.csv")
    dump_ent_commit_infos(old_intrusive_changes, f"{out_path}/old_mixed_entities.csv")
    dump_ent_commit_infos(pure_accompany_changes, f"{out_path}/pure_accompany_entities.csv")
    return all_entities, all_native_entities, old_native_entities, old_update_entities, intrusive_entities, old_intrusive_entities, pure_accompany_entities


if __name__ == "__main__":
    entry()
