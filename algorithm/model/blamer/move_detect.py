import json
from dataclasses import dataclass
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Set, Dict, List, Union, Tuple, overload, TextIO

from algorithm.model.blamer.entity_tracer import BaseState, MethodState, ParamState
from algorithm.model.blamer.refactor_format import MoveMethodPatterns, SpecialMoveMethodGetters, MoveClassPatterns
from algorithm.model.blamer.refactoring_analysis import RefactorData

MoveMethodRefactorings = [
    "Move And Rename Method",
    "Move Method",
    "Rename Method",
    "Extract Method",
    "Extract And Move Method"
]

MoveParamRefactorings = [
    "Rename Parameter",
    "Add Parameter",
    "Remove Parameter",
]

MoveClassRefactoring = [
    "Rename Class",
    "Move Class",
    "Move And Rename Class"
]


@dataclass(frozen=True)
class Entity:
    kind: str
    ent_id: int
    parent_id: int
    qualified_name: str
    short_name: str
    signature: str
    file_path: str


@dataclass(frozen=True)
class Dependency:
    dep_kind: str
    tar_ent: Entity


@dataclass(frozen=True)
class Contain:
    dep_kind: str
    tar_ent: Entity


FilePath = str

ContainLikeDependencies = ["Contain", "Define"]


@dataclass(frozen=True)
class DepData:
    ent_list: List[Entity]
    ent_dict: Dict[int, Entity]
    dep_dict: Dict[int, List[Dependency]]
    qualified_name_dict: Dict[Tuple[str, FilePath], Entity]
    contain_dict: Dict[int, List[Contain]]

    def get_children(self, ent_id: int) -> Set[Contain]:
        ret = set()
        for d in self.contain_dict[ent_id]:
            ret.add(d)
        return ret

    @overload
    def __getitem__(self, item: Tuple[str, FilePath]) -> Entity:
        ...

    @overload
    def __getitem__(self, item: BaseState) -> Entity:
        ...

    @overload
    def __getitem__(self, item: int) -> Entity:
        ...

    def __getitem__(self, item) -> Entity:
        if isinstance(item, int):
            return self.ent_dict[item]
        elif isinstance(item, tuple):
            return self.qualified_name_dict[item]
        elif isinstance(item, BaseState):
            file_path = item.file_path
            qualified_name = item.longname()
            return self.qualified_name_dict[qualified_name, file_path]


def get_signature(var) -> str:
    return var["rawType"] if "rawType" in var.keys() else ""


def load_dep_data(dep_file: Path) -> DepData:
    ent_list: List[Entity] = []
    ent_dict: Dict[int, Entity] = dict()
    dep_dict: Dict[int, List[Dependency]] = defaultdict(list)
    qualified_name_dict: Dict[Tuple[str, FilePath], Entity] = dict()
    dep_obj = json.loads(dep_file.read_text())
    contain_dict: Dict[int, List[Contain]] = defaultdict(list)

    for var in dep_obj["variables"]:
        try:
            qualified_name = var["qualifiedName"]
            short_name = var["name"]
            ent_id = var["id"]
            ent_kind = var["category"]
            parent_id = var["parentId"]
            file_path = var["File"] if "File" in var else ""
            signature = get_signature(var)
            ent = Entity(ent_kind, ent_id, parent_id, qualified_name, short_name, signature, file_path)
            ent_list.append(ent)
            ent_dict[ent_id] = ent
            qualified_name_dict[qualified_name, file_path] = ent
        except KeyError:
            continue
    for dep in dep_obj["cells"]:
        src_id = dep["src"]
        dest_id = dep["dest"]
        dest_ent = ent_dict[dest_id]
        dep_kind = list(dep["values"].keys())[0]
        if src_id in ent_dict and dest_id in ent_dict:
            dep_dict[src_id].append(Dependency(dep_kind, dest_ent))
            if dep_kind in ContainLikeDependencies:
                contain_dict[src_id].append((Contain(dep_kind, dest_ent)))

    return DepData(ent_list, ent_dict, dep_dict, qualified_name_dict, contain_dict)


@dataclass(frozen=True)
class MoveEdit:
    src_state: BaseState
    to_state: BaseState
    refactor_obj: dict


def extract_related_code_elements(kind: str, code_elements: List[dict]) -> List[Tuple[str, FilePath]]:
    ret = []
    for ele in code_elements:
        if ele["codeElementType"] == kind:
            ret.append((ele["codeElement"], ele["filePath"]))

    return ret


def extract_methods(code_elements: List[dict]) -> List[Tuple[str, FilePath]]:
    return extract_related_code_elements("METHOD_DECLARATION", code_elements)


def extract_classes(code_elements: List[dict]) -> List[Tuple[str, FilePath]]:
    return extract_related_code_elements("TYPE_DECLARATION", code_elements)


def extract_method_move(description: str,
                        left_side: List[dict],
                        right_side: List[dict]) -> List[Tuple[BaseState, BaseState]]:
    for pattern in MoveMethodPatterns:
        matched = pattern[0].match(description)
        if matched:
            from_class_index = pattern[2]
            to_class_index = pattern[4]
            src_class = matched.group(from_class_index)
            to_class = matched.group(to_class_index)
            src_method, src_path = extract_methods(left_side)[0]
            to_method, to_path = extract_methods(right_side)[0]
            # return {MethodState(src_class, src_path, src_method)}, {MethodState(to_class, to_path, to_method)}
            return [(MethodState(src_class, src_path, src_method), MethodState(to_class, to_path, to_method))]

    # for getter in SpecialMoveMethodGetters:
    #     if matched := getter({
    #         "description": description,
    #         "leftSideLocations": left_side,
    #         "rightSideLocations": right_side,
    #     }):
    #         _, src_class, _, to_class = matched
    #         src_method, src_path = extract_methods(left_side)[0]
    #         to_method, to_path = extract_methods(right_side)[0]
    #         return {MethodState(src_class, src_path, src_method)}, {MethodState(to_class, to_path, to_method)}
    return []


def extract_param_move(description: str,
                       left_side: List[dict],
                       right_side: List[dict]) -> List[Tuple[BaseState, BaseState]]:
    for getter in SpecialMoveMethodGetters:
        if matched := getter({
            "description": description,
            "leftSideLocations": left_side,
            "rightSideLocations": right_side,
        }):
            from_param, from_method, src_class, to_param, to_method, to_class = matched
            src_method, src_path = extract_methods(left_side)[0]
            to_method, to_path = extract_methods(right_side)[0]
            return [
                (ParamState(src_class, src_path, src_method, from_param),
                 ParamState(to_class, to_path, to_method, to_param)),
                (MethodState(src_class, src_path, src_method),
                 MethodState(to_class, to_path, to_method))
            ]
    return []


# def extract_class_move(description: str,
#                        left_side: List[dict],
#                        right_side: List[dict]) -> Tuple[Set[BaseState], Set[BaseState]]:
#     src_classes = extract_classes(left_side)
#     to_classes = extract_classes(right_side)
#     src_states = {BaseState(longname, path) for longname, path in src_classes}
#     to_classes = {BaseState(longname, path) for longname, path in to_classes}
#     return src_states, to_classes

def extract_class_move(description: str,
                       left_side: List[dict],
                       right_side: List[dict]) -> List[Tuple[BaseState, BaseState]]:
    src_class = extract_classes(left_side)[0]
    to_class = extract_classes(right_side)[0]
    src_state = BaseState(src_class[0], src_class[1])
    to_state = BaseState(to_class[0], to_class[1])
    return [(src_state, to_state)]


def extract_state(refactor_kind: str,
                  description: str,
                  left_side: List[dict],
                  right_side: List[dict]) -> List[Tuple[BaseState, BaseState]]:
    # if refactor_kind in MoveMethodRefactorings:
    #     src_methods, to_methods = extract_method_move(description, left_side, right_side)
    #     return src_methods, to_methods
    # elif refactor_kind in MoveClassRefactoring:
    #     src_classes, to_classes = extract_class_move(description, left_side, right_side)
    #     return src_classes, to_classes
    if refactor_kind in MoveMethodRefactorings:
        return extract_method_move(description, left_side, right_side)
    elif refactor_kind in MoveParamRefactorings:
        return extract_param_move(description, left_side, right_side)
    elif refactor_kind in MoveClassRefactoring:
        return extract_class_move(description, left_side, right_side)


def distill_move_edit(refactor_obj: dict) -> List[MoveEdit]:
    refactor_kind = refactor_obj["type"]
    description = refactor_obj["description"]
    if refactor_kind not in MoveMethodRefactorings + MoveClassRefactoring + MoveParamRefactorings:
        return []
    states = extract_state(refactor_kind,
                           description,
                           refactor_obj["leftSideLocations"],
                           refactor_obj["rightSideLocations"])
    ret = []
    for state in states:
        ret.append(MoveEdit(state[0], state[1], refactor_obj))
    # for src in src_states:
    #     for to in to_states:
    #         ret.append(MoveEdit(src, to, refactor_obj))

    return ret


def distill_move_edit_list(refactor_objs: List[dict]) -> Dict[str, List[MoveEdit]]:
    # ret = []
    # for refactor_obj in refactor_objs:
    #     ret.extend(distill_move_edit((refactor_obj)))
    # return ret
    ret = {}
    for refactor_obj in refactor_objs:
        moves = distill_move_edit(refactor_obj)
        for move in moves:
            try:
                ret[move.to_state.get_category() + move.to_state.longname()].append(move)
            except KeyError:
                ret[move.to_state.get_category() + move.to_state.longname()] = []
                ret[move.to_state.get_category() + move.to_state.longname()].append(move)
    return ret


def distill_move_edit_diction(refactor_data: RefactorData) -> Dict[str, Set[MoveEdit]]:
    ...


class MappingKind(Enum):
    DirectMapping = "Direct"
    RefactorMapping = "Refactor"
    RefactorChildMapping = "Child"


@dataclass(frozen=True)
class MappingValue:
    ent_id: int
    kind: MappingKind


class EntityMapping:
    src_dep_data: DepData
    to_dep_data: DepData
    mapping: Dict[int, Set[MappingValue]]
    move_mapping: Dict[int, List[Tuple[MoveEdit, int]]]

    def __init__(self, src_dep_data: DepData, to_dep_data: DepData):
        self.src_dep_data: DepData = src_dep_data
        self.to_dep_data: DepData = to_dep_data
        self.mapping: Dict[int, Set[MappingValue]] = defaultdict(set)
        self.move_mapping: Dict[int, List[Tuple[MoveEdit, int]]] = defaultdict(list)

    def unmatched_ent_ids(self) -> Set[int]:
        matched_ids: Set[int] = set()
        for i, values in self.mapping.items():
            matched_ids.update(v.ent_id for v in values)
        return matched_ids.difference(self.to_dep_data.dep_dict.keys())

    def __getitem__(self, item: int) -> Set[MappingValue]:
        return self.mapping[item]


def same_entity_under_ctx(src_parent_ent: Entity, src_child_ent: Entity,
                          to_parent_ent: Entity, to_child_ent: Entity) -> bool:
    # todo: use more accurate under parent entity comparing
    return src_child_ent.short_name == to_child_ent.short_name


class EntityMappingBuilder:
    def __init__(self, move_edits: List[MoveEdit], src_deps: DepData, to_deps: DepData):
        self.move_edits = move_edits
        self.src_deps = src_deps
        self.to_deps = to_deps
        self.mapping = EntityMapping(src_deps, to_deps)

    def build_ent_mapping(self):
        self.build_direct_mapping()
        self.build_move_mapping()
        self.build_further_mapping()

    def build_direct_mapping(self):
        for ent in self.src_deps.ent_list:
            if (ent.qualified_name, ent.file_path) in self.to_deps.qualified_name_dict:
                to_candidate_ent = self.to_deps.qualified_name_dict[ent.qualified_name, ent.file_path]
                if to_candidate_ent.file_path == ent.file_path:
                    self.mapping[ent.ent_id].add(MappingValue(to_candidate_ent.ent_id, MappingKind.DirectMapping))

    def build_move_mapping(self):
        for move_edit in self.move_edits:
            src_state = move_edit.src_state
            to_state = move_edit.to_state
            src_entity = self.src_deps[src_state]
            to_entity = self.to_deps[to_state]
            self.mapping[src_entity.ent_id].add(MappingValue(to_entity.ent_id, MappingKind.RefactorMapping))
            self.mapping.move_mapping[src_entity.ent_id].append((move_edit, to_entity.ent_id))

    def find_matched_ancestor(self, src_ent: Entity, deps: DepData) -> Tuple[Entity, Set[Entity]]:
        while len(self.mapping[src_ent.ent_id]) == 0:
            src_ent = deps[src_ent.parent_id]
        ent_ids = {v.ent_id for v in self.mapping[src_ent.ent_id]}
        return src_ent, set(map(self.to_deps.__getitem__, ent_ids))

    def build_further_mapping(self):
        for src_ent_id in self.mapping.unmatched_ent_ids():
            if src_ent_id not in self.src_deps.dep_dict:
                continue
            src_ancestor, to_ancestors = self.find_matched_ancestor(self.src_deps[src_ent_id], self.src_deps)
            for to_ancestor in to_ancestors:
                self.build_children_mapping_under_parent_ctx(src_ancestor, to_ancestor)

    def build_children_mapping_under_parent_ctx(self, src_parent_ent: Entity, to_parent_ent: Entity):
        for src_child_dep in self.src_deps.get_children(src_parent_ent.ent_id):
            for to_child_dep in self.src_deps.get_children(to_parent_ent.ent_id):
                if same_entity_under_ctx(src_parent_ent, src_child_dep.tar_ent,
                                         to_parent_ent, to_child_dep.tar_ent):
                    self.mapping[src_child_dep.tar_ent.ent_id]. \
                        add(MappingValue(to_child_dep.tar_ent.ent_id, MappingKind.RefactorChildMapping))
                    self.build_children_mapping_under_parent_ctx(src_child_dep.tar_ent, to_child_dep.tar_ent)


def build_mapping(refactor_data: Path, dep_file1: Path, dep_file2) -> EntityMapping:
    refactor_obj = json.loads(refactor_data.read_text())
    move_edits = distill_move_edit_list(refactor_obj["refactorings"])
    dep_obj1 = load_dep_data(dep_file1)
    dep_obj2 = load_dep_data(dep_file2)
    builder = EntityMappingBuilder(move_edits, dep_obj1, dep_obj2)
    builder.build_ent_mapping()
    return builder.mapping


def dump_entity_mapping(mapping: EntityMapping, fp: TextIO):
    mapping_obj = []
    for src_id, to_ids in mapping.mapping.items():
        mapping_obj.append({
            "src": src_id,
            "dests": [{"dest": v.ent_id, "type": v.kind.value} for v in to_ids]
        })
    move_mapping_obj = []
    for src_id, to_moves in mapping.move_mapping.items():
        move_mapping_obj.append({
            "src": src_id,
            "dests": [{"refactoring": move[0].refactor_obj, "dest_id": move[1]} for move in to_moves]
        })

    json.dump({
        "normal_mapping": mapping_obj,
        "refactor_mapping": move_mapping_obj
    }, fp, indent=4)


def entry():
    refactor_path = Path("rename_refactor.json")
    before_dep_path = Path("android_frameworks_base-out-before-renamed.json")
    renamed_dep_path = Path("android_frameworks_base-out-renamed.json")
    mapping = build_mapping(refactor_path, before_dep_path, renamed_dep_path)
    with open("mapping.json", "w") as file:
        dump_entity_mapping(mapping, file)


if __name__ == '__main__':
    entry()
