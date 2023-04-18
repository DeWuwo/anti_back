from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Set, Optional, Tuple, Sequence, Dict, Iterable

import git

from algorithm.model.blamer.commit_dag import CommitDAG, SHA, commit_dag_generator, CommitNode
from algorithm.model.blamer.refactor_format import MoveAttributePattern, MoveMethodPatterns, SpecialMoveMethodGetters, \
    MoveClassPatterns, get_name_from_sig, get_param_from_sig, get_param_from_param_sig
from algorithm.model.blamer.refactoring_analysis import RefactorData


@dataclass(frozen=True)
class BaseState:
    class_state: str
    file_path: str

    def longname(self):
        return self.class_state

    def get_param(self):
        return 'null'

    def get_category(self):
        return 'Class'


@dataclass(frozen=True)
class MethodState(BaseState):
    method_state: str

    def __str__(self) -> str:
        return f"(\n {self.method_state},\n {self.class_state}, \n{self.file_path})"

    def longname(self):
        return self.class_state + "." + get_name_from_sig(self.method_state)

    def get_param(self):
        return get_param_from_sig(self.method_state)[1]

    def get_category(self):
        return 'Method'


@dataclass(frozen=True)
class ParamState(BaseState):
    method_state: str
    param_state: str

    def __str__(self) -> str:
        return f"(\n {self.param_state},\n {self.method_state},\n {self.class_state}, \n{self.file_path})"

    def longname(self):
        param = get_param_from_param_sig(self.param_state)[1]
        if param == '':
            longname = self.class_state + "." + get_name_from_sig(self.method_state)
        else:
            longname = self.class_state + "." + get_name_from_sig(self.method_state) + "." + get_param_from_param_sig(
                self.param_state)[1]
        return longname

    def get_param(self):
        return get_param_from_sig(self.method_state)[1]

    def get_category(self):
        return 'Variable'


@dataclass(frozen=True)
class AttributeState(BaseState):
    attribute_state: str

    def __str__(self) -> str:
        return f"({self.attribute_state},\n {self.class_state})"

    def longname(self):
        return self.class_state + "." + self.attribute_state

    def get_param(self):
        return 'null'


def get_move_method(refactor_obj):
    description = refactor_obj["description"]
    for pattern in MoveMethodPatterns:
        matched = pattern[0].match(description)
        if matched:
            from_method_index = pattern[1]
            from_class_index = pattern[2]
            to_method_index = pattern[3]
            to_class_index = pattern[4]
            from_method = matched.group(from_method_index)
            from_class = matched.group(from_class_index)
            to_method = matched.group(to_method_index)
            to_class = matched.group(to_class_index)
            return from_method, from_class, to_method, to_class
    for getter in SpecialMoveMethodGetters:
        if matched := getter(refactor_obj):
            return matched
    return None


def get_move_class(refactor_obj):
    description = refactor_obj["description"]
    for pattern in MoveClassPatterns:
        matched = pattern.match(description)
        if matched:
            from_class_index = 1
            to_class_index = 2
            from_class = matched.group(from_class_index)
            to_class = matched.group(to_class_index)
            return from_class, to_class
    return None


def resolve_method_refactor(state: MethodState, refactor_obj) -> List[MethodState]:
    ret = []
    if mv_method := get_move_method(refactor_obj):
        from_method, from_class, to_method, to_class = mv_method
        if from_method == state.method_state and from_class == state.class_state:
            ret.append(MethodState(to_method, to_class))
    elif move_class := get_move_class(refactor_obj):
        from_class, to_class = move_class
        if state.class_state.startswith(from_class):
            ret.append(MethodState(state.method_state, state.class_state.replace(from_class, to_class)))
    return ret


def get_move_attribute(refactor_obj):
    description = refactor_obj["description"]
    for pattern in MoveAttributePattern:
        matched = pattern[0].match(description)
        if matched:
            from_attribute_index = pattern[1]
            from_class_index = pattern[2]
            to_attribute_index = pattern[3]
            to_class_index = pattern[4]
            from_attribute = matched.group(from_attribute_index)
            from_class = matched.group(from_class_index)
            to_attribute = matched.group(to_attribute_index)
            to_class = matched.group(to_class_index)
            return from_attribute, from_class, to_attribute, to_class
    for getter in SpecialMoveMethodGetters:
        if matched := getter(refactor_obj):
            return matched
    return None


def resolve_attribute_refactor(state: AttributeState, refactor_obj) -> List[AttributeState]:
    ret = []
    if mv_attribute := get_move_attribute(refactor_obj):
        from_method, from_class, to_method, to_class = mv_attribute
        if from_method == state.attribute_state and from_class == state.class_state:
            ret.append(AttributeState(to_method, to_class))
    elif move_class := get_move_class(refactor_obj):
        from_class, to_class = move_class
        if state.class_state.startswith(from_class):
            ret.append(AttributeState(state.attribute_state, state.class_state.replace(from_class, to_class)))
    return ret


def resolve_class_refactor(state: BaseState, refactor_obj) -> List[BaseState]:
    ret = []
    move_class = get_move_class(refactor_obj)
    if move_class:
        from_class, to_class = move_class
        if state.class_state.startswith(from_class):
            ret.append(BaseState(to_class))
    return ret


def resolve_refactor(state: BaseState, refactor_obj) -> Sequence[BaseState]:
    if isinstance(state, MethodState):
        return resolve_method_refactor(state, refactor_obj)
    elif isinstance(state, AttributeState):
        return resolve_attribute_refactor(state, refactor_obj)
    elif isinstance(state, BaseState):
        return resolve_class_refactor(state, refactor_obj)
    else:
        raise NotImplementedError()


def transfer_state(s: BaseState, commit_refactors) -> List[BaseState]:
    new_states_of_s = list()
    for refactor_obj in commit_refactors:
        new_states_of_s.extend(resolve_refactor(s, refactor_obj))
    return new_states_of_s


def transfer_all_states(states: Iterable[BaseState], sha: str, refactor_data: RefactorData) -> Set[BaseState]:
    if sha not in refactor_data.refactor_dict:
        # if it's not a commit contain any refactoring detected
        return set(states)
    commit_refactors = refactor_data.get(sha)
    if not commit_refactors:
        return set(states)
    ret = set()
    for state in states:
        new_states = transfer_state(state, commit_refactors)
        if new_states:
            ret.update(new_states)
        else:
            ret.add(state)
    return ret


class EntityTracer:

    def __init__(self, data_path: Path, repo_path: Path):
        self.repo = git.Repo(repo_path)
        self.refactor_data = RefactorData(data_path)
        self.commit_dag = CommitDAG(self.repo)
        self.state_dict: Dict[SHA, Set[BaseState]] = defaultdict(set)

    def trace_entity(self, state: BaseState, sha: str):
        self.state_dict[sha] = {state}
        generator = commit_dag_generator(self.commit_dag, sha)
        for commit_node in generator:
            all_parent_states = self.take_parent_states(commit_node)
            self.state_dict[commit_node.sha].update(transfer_all_states(all_parent_states,
                                                                        commit_node.sha,
                                                                        self.refactor_data))
            assert len(self.state_dict[commit_node.sha]) != 0

    def take_parent_states(self, commit_node: CommitNode) -> Set[BaseState]:
        ret = set()
        for parent_sha in commit_node.parent_commits:
            ret.update(self.state_dict[parent_sha])
        return ret


def entry():
    base_repo_path = Path("D:\\Master\\CodeSmell\\Refactor\\frameworks\\base")
    tracer = EntityTracer(Path("refactoring_android.json"), base_repo_path)
    commit = "87a6cc1e28eff0109c9a176c03ea798d85c97815"
    method_sig = "private commitApkSession(apkSession PackageInstallerSession, originalSession " \
                 "PackageInstallerSession, preReboot boolean) : void"
    class_path = "com.android.server.pm.StagingManager"
    tracer.trace_entity(MethodState(method_sig, class_path), commit)
    with open("mapping", "w") as file:
        for sha, states in tracer.state_dict.items():
            file.write(f"{sha} -> {states}\n")


if __name__ == "__main__":
    entry()
