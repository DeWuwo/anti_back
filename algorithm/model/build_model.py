import json
import os.path
from typing import List, Dict
from collections import defaultdict
from functools import partial
from algorithm.model.dependency.entity import Entity, set_package, set_parameters
from algorithm.model.dependency.relation import Relation
from algorithm.model.git_history import GitHistory
from algorithm.model.blamer.entity_tracer import BaseState
from algorithm.utils import Constant, FileCSV, FileJson, Compare

MoveMethodRefactorings = [
    "Move And Rename Method",
    "Move Method",
    "Rename Method",
]

ExtractMethodRefactorings = [
    "Extract Method",
    "Extract And Move Method"
]

MoveMethodParamRefactorings = [
    "Rename Parameter",
    "Add Parameter",
    "Remove Parameter",
]

MoveClassRefactoring = [
    "Rename Class",
    "Move Class",
    "Move And Rename Class"
]


class BuildModel:
    # blame data
    git_history: GitHistory
    # base info
    entity_android: List[Entity]
    entity_extensive: List[Entity]
    relation_android: List[Relation]
    relation_extensive: List[Relation]
    statistics_android: Dict
    statistics_extensive: Dict
    file_set_android : set
    file_set_extension: set

    out_path: str
    # more info
    hidden_entities: List[int]
    params_modify_entities: List[int]
    hidden_modify_entities: List[int]
    access_modify_entities: List[int]
    final_modify_entities: List[int]
    annotation_modify_entities: List[int]
    return_type_modify_entities: List[int]

    parent_class_modify_entities: List[int]
    parent_interface_modify_entities: List[int]

    class_body_modify_entities: List[int]
    inner_extensive_class_entities: List[int]
    class_var_extensive_entities: List[int]
    class_var_modify_entities: List[int]

    method_extensive_entities: List[int]
    method_body_modify_entities: List[int]
    method_var_extensive_entities: List[int]
    method_var_modify_entities: List[int]

    import_extensive_relation: List[Relation]

    refactor_entities: Dict[str, List[int]]
    agg_relations: List[Relation]
    facade_relations: List[Relation]
    facade_entities: List[Entity]
    diff_relations: List[Relation]
    define_relations: List[Relation]
    reflect_relation: List[Relation]
    # query set
    query_map: defaultdict

    owner_proc: List[Dict]
    owner_proc_count: dict

    def __init__(self, entities_extensive, cells_extensive, statistics_extensive: Dict, entities_android, cells_android,
                 statistics_android: Dict, git_history: GitHistory, out_path: str):
        # first init
        self.git_history = git_history
        self.out_path = out_path
        self.entity_android = []
        self.entity_extensive = []
        self.relation_android = []
        self.relation_extensive = []
        self.statistics_android = statistics_android
        self.statistics_extensive = statistics_extensive
        self.file_set_android = set()
        self.file_set_extension = set()
        # self.hidden_entities = []
        self.params_modify_entities = []
        self.hidden_modify_entities = []
        self.access_modify_entities = []
        self.final_modify_entities = []
        self.annotation_modify_entities: List[int] = []
        self.return_type_modify_entities: List[int] = []

        self.parent_class_modify_entities: List[int] = []
        self.parent_interface_modify_entities: List[int] = []

        self.class_body_modify_entities = []
        self.inner_extensive_class_entities = []
        self.class_var_extensive_entities = []
        self.class_var_modify_entities = []

        self.method_extensive_entities = []
        self.method_body_modify_entities = []
        self.method_var_extensive_entities = []
        self.method_var_modify_entities = []
        self.import_extensive_relation = []
        self.refactor_entities = {
            "Move And Rename Method": [],
            "Move Method": [],
            "Rename Method": [],
            "Extract Method": [],
            "Extract And Move Method": [],
            "Rename Parameter": [],
            "Add Parameter": [],
            "Remove Parameter": [],
            "Rename Class": [],
            "Move Class": [],
            "Move And Rename Class": []
        }
        self.agg_relations = []
        self.facade_relations = []
        self.facade_entities = []
        self.diff_relations = []
        self.define_relations = []
        self.reflect_relation = []
        self.owner_proc = []
        self.owner_proc_count = {}

        # init entity
        print("start init model entities")
        aosp_entity_set = defaultdict(partial(defaultdict, partial(defaultdict, list)))
        extensive_entity_set = defaultdict(partial(defaultdict, partial(defaultdict, list)))
        # aosp entities
        print('     get aosp entities')
        for item in entities_android:
            if not item['external']:
                entity = Entity(**item)
                set_parameters(entity, self.entity_android)
                self.entity_android.append(entity)
                aosp_entity_set[entity.category][entity.qualifiedName][entity.file_path].append(entity.id)
                if entity.category == Constant.E_file:
                    self.file_set_android.add(entity.file_path)
                elif entity.category == Constant.E_class and entity.name == Constant.anonymous_class:
                    entity.set_anonymous_class(True)
        # assi entities
        print('     get assi entities')
        for item in entities_extensive:
            if not item['external']:
                entity = Entity(**item)
                # get entity package
                set_package(entity, self.entity_extensive)
                set_parameters(entity, self.entity_extensive)
                self.entity_extensive.append(entity)
                extensive_entity_set[entity.category][entity.qualifiedName][entity.file_path].append(entity.id)
                self.owner_proc.append(entity.to_csv())
                if entity.category == Constant.E_file:
                    self.file_set_extension.add(entity.file_path)
                elif entity.category == Constant.E_class and entity.name == Constant.anonymous_class:
                    entity.set_anonymous_class(True)
        # init dep
        print("start init model deps")
        import_relation_set = defaultdict(int)
        print("     get aosp dep")
        for index, item in enumerate(cells_android):
            relation = Relation(**item)
            relation.set_id(index)
            relation.set_files(self.entity_android)
            self.relation_android.append(relation)
            if relation.rel == Constant.R_import:
                import_relation_set[relation.to_str(self.entity_android)] = 1
            elif relation.rel == Constant.typed:
                self.entity_android[relation.src].set_typed(relation.dest)
            elif relation.rel == Constant.R_annotate:
                self.entity_android[relation.dest].set_annotations(self.entity_android[relation.src].qualifiedName)
            elif relation.rel == Constant.inherit:
                self.entity_android[relation.src].set_parent_class(self.entity_android[relation.dest].qualifiedName)
            elif relation.rel == Constant.implement:
                self.entity_android[relation.src].set_parent_interface(self.entity_android[relation.dest].qualifiedName)

        print("     get assi dep")
        temp_param = defaultdict(list)
        temp_define = defaultdict(list)
        for index, item in enumerate(cells_extensive):
            relation = Relation(**item)
            relation.set_id(index)
            relation.set_files(self.entity_extensive)
            self.relation_extensive.append(relation)
            if relation.rel == Constant.param:
                temp_param[relation.src].append(self.entity_extensive[relation.dest])
                self.entity_extensive[relation.dest].set_is_param(1)
            elif relation.rel == Constant.define:
                temp_define[relation.src].append(self.entity_extensive[relation.dest])
            elif relation.rel == Constant.R_import:
                if import_relation_set[relation.to_str(self.entity_extensive)] != 1 and \
                        self.entity_extensive[relation.src].file_path in self.file_set_android:
                    self.import_extensive_relation.append(relation)
            elif relation.rel == Constant.typed:
                self.entity_extensive[relation.src].set_typed(relation.dest)
            elif relation.rel == Constant.R_annotate:
                self.entity_extensive[relation.dest].set_annotations(self.entity_extensive[relation.src].qualifiedName)
            elif relation.rel == Constant.inherit:
                self.entity_extensive[relation.src].set_parent_class(self.entity_extensive[relation.dest].qualifiedName)
            elif relation.rel == Constant.implement:
                self.entity_extensive[relation.src].set_parent_interface(
                    self.entity_extensive[relation.dest].qualifiedName)
            elif relation.rel == Constant.call:
                self.entity_extensive[relation.dest].set_called_count()
        # data get -- blame
        print('start init owner from blame')
        all_entities, all_native_entities, old_native_entities, old_update_entities, intrusive_entities, old_intrusive_entities, pure_accompany_entities, refactor_list = self.get_blame_data()

        #
        for ent_id, ent in all_entities.items():
            self.entity_extensive[int(ent_id)].set_commits_count(
                {'actively_native': len(json.loads(ent['base commits'])),
                 'obsolotely_native': len(json.loads(ent['old base commits'])),
                 'extensive': len(json.loads(ent['accompany commits']))})

        print('get ownership')
        # first get entity owner
        print('     get entity owner')
        self.get_entity_ownership(aosp_entity_set, extensive_entity_set, all_entities, all_native_entities,
                                  old_native_entities, old_update_entities, intrusive_entities,
                                  old_intrusive_entities, pure_accompany_entities, refactor_list,
                                  temp_define, temp_param)
        print('     get relation owner')
        self.get_relation_ownership()

        print('get filter relation set')
        self.detect_facade()

        # query set build
        print('get relation search dictionary')
        self.query_map_build(self.diff_relations, self.define_relations)

        print('  output entities owner and intrusive info')
        self.out_intrusive_info()

        # output facade info
        self.out_facade_info()

    # Get data of blame
    def get_blame_data(self):
        all_entities, all_native_entities, old_native_entities, old_update_entities, intrusive_entities, old_intrusive_entities, pure_accompany_entities = self.git_history.divide_owner()

        print('get possible refactor entity')
        possible_refactor_entities = []
        possible_refactor_entities.extend(intrusive_entities.values())
        possible_refactor_entities.extend(old_intrusive_entities.values())
        # possible_refactor_entities.extend(pure_accompany_entities.values())
        refactor_list = self.git_history.load_refactor_entity(possible_refactor_entities)
        return all_entities, all_native_entities, old_native_entities, old_update_entities, intrusive_entities, old_intrusive_entities, pure_accompany_entities, refactor_list

    # get owner string '01', '10', '11' or '00'
    def get_direction(self, relation: Relation):
        def get_owner(ent: Entity):
            # if ent.is_intrusive:
            #     return '0'
            # else:
            return str(ent.not_aosp)

        return get_owner(self.entity_extensive[relation.src]) + get_owner(self.entity_extensive[relation.dest])

    # Construction of query map
    def query_map_build(self, diff: List[Relation], android_define_set: List[Relation]):
        self.query_map = defaultdict(partial(defaultdict, partial(defaultdict, partial(defaultdict, list))))
        for item in diff:
            self.query_map[item.rel][self.get_direction(item)][self.entity_extensive[item.src].category][
                self.entity_extensive[item.dest].category].append(item)

            self.query_map[item.rel][self.get_direction(item)][self.entity_extensive[item.src].category][
                item.dest].append(item)

            self.query_map[item.rel][self.get_direction(item)][item.src][
                self.entity_extensive[item.dest].category].append(item)

            self.query_map[item.rel][self.get_direction(item)][item.src][item.dest].append(item)
        for item in android_define_set:
            self.query_map[item.rel]['00'][self.entity_extensive[item.src].category][
                self.entity_extensive[item.dest].category].append(item)

            self.query_map[item.rel]['00'][self.entity_extensive[item.src].category][item.dest].append(item)

            self.query_map[item.rel]['00'][item.src][self.entity_extensive[item.dest].category].append(item)
            self.query_map[item.rel]['00'][item.src][item.dest].append(item)

    # query method
    def query_relation(self, rel: str, not_aosp: str, src, dest) -> List[Relation]:
        return self.query_map[rel][not_aosp][src][dest]

    # diff & blame
    def get_entity_ownership(self, aosp_entity_map, extensive_entity_map, all_entities: dict, all_native_entities: dict,
                             old_native_entities: dict, old_update_entities: dict, intrusive_entities: dict,
                             old_intrusive_entities: dict, pure_accompany_entities: dict,
                             refactor_list: Dict[int, list],
                             child_define: Dict[int, List[Entity]], child_param: dict):
        keys_all_entities = all_entities.keys()
        keys_intrusive_entities = intrusive_entities.keys()
        keys_old_intrusive_entities = old_intrusive_entities.keys()
        keys_pure_accompany_entities = pure_accompany_entities.keys()
        keys_old_native_entities = old_native_entities.keys()
        keys_old_update_entities = old_update_entities.keys()
        keys_all_native_entities = all_native_entities.keys()
        self.owner_proc_count = {
            'ignore': 0,
            'dep_coupling': 0,
            'dep_native': 0,
            'dep_extension': 0,
            'dep_any': 0,
            'git_pure_native': 0,
            'git_native': 0,
            'git_old_native': 0,
            'git_old_update': 0,
            'git_intrusive': 0,
            'git_old_intrusive': 0,
            'git_extension': 0,
            'git_any': 0,
            'refactor': 0,
            'dep_native2git_pure_native': 0,
            'dep_native2git_pure_native_c': [0, 0, 0, 0],
            'dep_native2git_native': 0,
            'dep_native2git_native_c': [0, 0, 0, 0],
            'dep_native2git_old_native': 0,
            'dep_native2git_old_native_c': [0, 0, 0, 0],
            'dep_native2git_old_update': 0,
            'dep_native2git_old_update_c': [0, 0, 0, 0],
            'dep_native2git_intrusive': 0,
            'dep_native2git_intrusive_c': [0, 0, 0, 0],
            'dep_native2git_old_intrusive': 0,
            'dep_native2git_old_intrusive_c': [0, 0, 0, 0],
            'dep_native2git_extension': 0,
            'dep_native2git_extension_c': [0, 0, 0, 0],
            'dep_extension2git_extension': 0,
            'dep_extension2git_extension_c': [0, 0, 0, 0],
            'dep_extension2git_native': 0,
            'dep_extension2git_native_c': [0, 0, 0, 0],
            'dep_extension2git_pure_native': 0,
            'dep_extension2git_pure_native_c': [0, 0, 0, 0],
            'dep_extension2git_old_native': 0,
            'dep_extension2git_old_native_c': [0, 0, 0, 0],
            'dep_extension2git_old_update': 0,
            'dep_extension2git_old_update_c': [0, 0, 0, 0],
            'dep_extension2git_intrusive': 0,
            'dep_extension2git_intrusive_c': [0, 0, 0, 0],
            'dep_extension2git_old_intrusive': 0,
            'dep_extension2git_old_intrusive_c': [0, 0, 0, 0],
            'parent_ref': 0,
            "Move And Rename Method": 0,
            "Move Method": 0,
            "Rename Method": 0,
            "Extract Method": 0,
            "Extract And Move Method": 0,
            "Rename Parameter": 0,
            "Add Parameter": 0,
            "Remove Parameter": 0,
            "Rename Class": 0,
            "Move Class": 0,
            "Move And Rename Class": 0
        }

        def get_index(category: str) -> int:
            if category == Constant.E_class or category == Constant.E_interface:
                return 0
            elif category == Constant.E_method:
                return 1
            elif category == Constant.E_variable:
                return 2
            else:
                return 3

        def get_git_dep2git(ent: Entity):
            if ent.id in keys_old_native_entities:
                return '_0', "git_old_native"
            elif ent.id in keys_old_update_entities:
                return '_0 0', "git_old_update"
            elif ent.id in keys_intrusive_entities:
                return '0 1', "git_intrusive"
            elif ent.id in keys_old_intrusive_entities:
                return '_0 1', "git_old_intrusive"
            elif ent.id in keys_pure_accompany_entities:
                return '1', "git_extension"
            elif ent.id in keys_all_native_entities:
                return '0', "git_native"
            else:
                return '000', "git_pure_native"

        def detect_count(ent: Entity, dep_res):
            if dep_res == -1:
                dep_count = 'dep_extension'
                self.owner_proc[ent.id]['dep_diff'] = '1'
            else:
                dep_count = 'dep_native'
                self.owner_proc[ent.id]['dep_diff'] = '0'
            self.owner_proc_count[dep_count] += 1

            owner, owner_str = get_git_dep2git(ent)
            self.owner_proc[ent.id]['git_blame'] = owner
            self.owner_proc_count[owner_str] += 1

            if not ent.refactor:
                self.owner_proc_count[dep_count + '2' + owner_str] += 1
                self.owner_proc_count[dep_count + '2' + owner_str + '_c'][get_index(ent.category)] += 1

        def detect_ownership(ent: Entity, all_refactor_info: Dict[int, list], src_name: str, src_param: str,
                             src_file: str):
            if all_refactor_info is None:
                detect_un_refactor_entities(ent, src_name, src_param, src_file)
                return
            try:
                ent_refactor_info = all_refactor_info[ent.id][1]
                detect_refactor_entities(ent, ent_refactor_info, all_refactor_info)
            except KeyError:
                detect_un_refactor_entities(ent, src_name, src_param, src_file)

        def detect_git_must_native(ent: Entity):
            if ent.id not in keys_all_entities:
                return 1

        def detect_refactor_entities(ent: Entity, ent_refactor_info: list, all_refactor_info: Dict[int, list]):
            def detect_refactor_entities_son(child_entity_set: List[Entity], outer_ref_name: str, outer_ref_param: str,
                                             outer_ref_file_path: str):
                for child_ent in child_entity_set:
                    child_ent.set_refactor({'type': 'parent_ref'})
                    self.owner_proc[child_ent.id]['refactor'] = 'parent_ref'
                    child_source_qualified_name = outer_ref_name + '.' + child_ent.name
                    if child_ent.category == Constant.E_method:
                        child_source_param = child_ent.parameter_names
                    else:
                        child_source_param = outer_ref_param
                    detect_ownership(child_ent, all_refactor_info, child_source_qualified_name, child_source_param,
                                     outer_ref_file_path)
                    detect_refactor_entities_son(child_define[child_ent.id] + child_param[child_ent.id],
                                                 child_source_qualified_name, child_source_param, outer_ref_file_path)

            move_list = set()
            self.owner_proc_count['refactor'] += 1
            for move in ent_refactor_info:
                move_type: str = move[0]
                source_state: BaseState = move[1]
                dest_state: BaseState = move[2]
                # print(len(ent_refactor_info), ent.category, ent.id, move_type, source_state.longname(),
                #       dest_state.longname())

                # 对扩展重构
                dep_diff_res = self.graph_differ(ent, source_state.longname(), source_state.get_param(),
                                                 source_state.file_path,
                                                 aosp_entity_map, extensive_entity_map)
                if dep_diff_res == -1 and ent.id in keys_pure_accompany_entities:
                    ent.set_honor(1)
                    self.owner_proc[ent.id]['dep_diff'] = '1'
                    self.owner_proc[ent.id]['git_blame'] = 'extension refactor'
                    continue
                ent.set_refactor(
                    {'type': move_type, 'source_name': source_state.longname(),
                     'source_param': source_state.get_param()})
                move_list.add(move_type)
                if move_type in MoveClassRefactoring:
                    ent.set_honor(0)
                    ent.set_intrusive(1)
                    detect_refactor_entities_son(child_define[ent.id], source_state.longname(),
                                                 source_state.get_param(), source_state.file_path)
                elif move_type in MoveMethodRefactorings:
                    ent.set_honor(0)
                    ent.set_intrusive(1)
                    detect_refactor_entities_son(child_define[ent.id] + child_param[ent.id], source_state.longname(),
                                                 source_state.get_param(), source_state.file_path)
                elif move_type in ExtractMethodRefactorings:
                    ent.set_honor(1)
                    ent.set_intrusive(1)
                    for ent in child_param[ent.id]:
                        ent.set_honor(1)
                    detect_refactor_entities_son(child_define[ent.id], source_state.longname(),
                                                 source_state.get_param(), source_state.file_path)
                elif move_type in MoveMethodParamRefactorings:
                    if ent.category == Constant.E_method:
                        ent.set_honor(0)
                        ent.set_intrusive(1)
                        detect_refactor_entities_son(child_define[ent.id] + child_param[ent.id],
                                                     source_state.longname(),
                                                     source_state.get_param(), source_state.file_path)
                    else:
                        if move_type == MoveMethodParamRefactorings[0]:
                            ent.set_honor(0)
                            ent.set_intrusive(1)
                        elif move_type == MoveMethodParamRefactorings[1]:
                            ent.set_honor(1)
                else:
                    ent.set_honor(0)
                    ent.set_intrusive(1)
                    self.owner_proc[ent.id]['dep_diff'] = 'null'
                    self.owner_proc[ent.id]['git_blame'] = 'other refactor'

            self.owner_proc[ent.id]['refactor'] = ent.refactor
            for move in move_list:
                self.owner_proc_count[move] += 1
                self.refactor_entities[move].append(ent.id)

        def detect_un_refactor_entities(ent: Entity, source_name: str, source_param: str, source_file: str):
            if ent.not_aosp != -2:
                self.owner_proc_count['parent_ref'] += 1
                return

            dep_diff_res = self.graph_differ(ent, source_name, source_param, source_file, aosp_entity_map,
                                             extensive_entity_map)
            detect_count(ent, dep_diff_res)
            if ent.id in keys_old_native_entities or ent.id in keys_old_update_entities:
                ent.set_honor(0)
                ent.set_old_aosp(1)
            elif ent.id in keys_old_intrusive_entities:
                ent.set_honor(0)
                ent.set_old_aosp(1)
                ent.set_intrusive(1)
            elif ent.id in keys_all_native_entities:
                ent.set_honor(0)
            elif ent.id in keys_intrusive_entities or ent.id in keys_pure_accompany_entities:
                if dep_diff_res > -1:
                    ent.set_honor(0)
                    if ent.is_param != 1:
                        ent.set_intrusive(1)
                else:
                    ent.set_honor(1)

        # start detect ownership
        for entity in self.entity_extensive:
            self.owner_proc[entity.id]['refactor'] = 'null'
            if entity.above_file_level():
                owner = 0 if self.graph_differ(entity, entity.qualifiedName, entity.parameter_names, entity.file_path,
                                               aosp_entity_map, extensive_entity_map) >= 0 else 1
                entity.set_honor(owner)
                self.owner_proc[entity.id]['dep_diff'] = 'ignore'
                self.owner_proc[entity.id]['git_blame'] = 'ignore'
                self.owner_proc_count['ignore'] += 1
            # 解耦仓实体
            elif entity.is_decoupling > 1:
                entity.set_honor(1)
                self.owner_proc[entity.id]['dep_diff'] = '1-coupling'
                self.owner_proc[entity.id]['git_blame'] = 'any'
                self.owner_proc_count['dep_coupling'] += 1
                self.owner_proc_count['git_any'] += 1
            elif detect_git_must_native(entity):
                entity.set_honor(0)
                if entity.category == Constant.E_method and not entity.hidden:
                    entity.set_hidden(['hidden'])
                self.graph_differ(entity, entity.qualifiedName, entity.parameter_names, entity.file_path,
                                  aosp_entity_map, extensive_entity_map)
                self.owner_proc[entity.id]['dep_diff'] = 'any'
                self.owner_proc[entity.id]['git_blame'] = '000'
                self.owner_proc_count['dep_any'] += 1
                self.owner_proc_count['git_pure_native'] += 1
            else:
                detect_ownership(entity, refactor_list, entity.qualifiedName, entity.parameter_names, entity.file_path)

    def load_entity_ownership_from_catch(self):
        owners = FileCSV.read_from_file_csv(os.path.join(self.out_path, 'final_ownership.csv'), True)
        for owner in owners:
            self.entity_extensive[int(owner[0])].set_honor(int(owner[1]))
            self.entity_extensive[int(owner[0])].set_old_aosp(int(owner[2]))
            self.entity_extensive[int(owner[0])].set_intrusive(int(owner[3]))
            if int(owner[3]) == 1:
                self.entity_extensive[int(owner[0])].set_entity_mapping(int(owner[7]))
                self.get_entity_map(self.entity_extensive[int(owner[0])], self.entity_android[int(owner[7])])

    # graph differ
    def graph_differ(self, entity: Entity, search_name: str, search_param: str, search_file: str,
                     aosp_entity_set: defaultdict, extensive_entity_set: defaultdict):
        aosp_list: List[int] = aosp_entity_set[entity.category][search_name][search_file]
        extensive_list: List[int] = extensive_entity_set[entity.category][entity.qualifiedName][entity.file_path]
        if not aosp_list:
            return -1
        elif len(aosp_list) == 1 and len(extensive_list) == 1:
            self.get_entity_map(entity, self.entity_android[aosp_list[0]])
            return aosp_list[0]
        else:
            if entity.category == Constant.E_class and entity.anonymous != -1:
                for item_id in aosp_list:
                    if self.entity_android[item_id].raw_type == entity.raw_type and \
                            self.entity_android[self.entity_android[item_id].anonymous].name == \
                            self.entity_extensive[entity.anonymous].name:
                        self.get_entity_map(entity, self.entity_android[item_id])
                        return item_id
            elif entity.category == Constant.E_class or entity.category == Constant.E_interface:
                for item_id in aosp_list:
                    if self.entity_android[item_id].abstract == entity.abstract:
                        self.get_entity_map(entity, self.entity_android[item_id])
                        return item_id
            elif Constant.anonymous_class in entity.qualifiedName:
                map_parent_anonymous_class = get_parent_anonymous_class(entity.id, self.entity_extensive).id
                for item_id in aosp_list:
                    aosp_parent_anonymous_class = get_parent_anonymous_class(item_id,
                                                                             self.entity_android).entity_mapping
                    if aosp_parent_anonymous_class == map_parent_anonymous_class:
                        self.get_entity_map(entity, self.entity_android[item_id])
                        return item_id
            elif entity.category == Constant.E_method or entity.category == Constant.E_variable:
                for item_id in aosp_list:
                    if self.entity_android[item_id].parameter_names == search_param and \
                            (not (entity.not_aosp == 0 and entity.is_intrusive == 0) or
                             (self.entity_android[item_id].parameter_types == entity.parameter_types)):
                        self.get_entity_map(entity, self.entity_android[item_id])
                        return item_id
            else:
                return aosp_list[0]
            return -1

    # get entity mapping
    def get_entity_mapping(self, entity: Entity, search_name: str, search_param_name: str, search_file: str,
                           aosp_entity_set: defaultdict, extensive_entity_set: defaultdict):
        if entity.get_ownership() == Constant.Owner_actively_native:
            pass

    # Get entity mapping relationship
    def get_entity_map(self, extensive_entity: Entity, native_entity: Entity):
        extensive_entity.set_entity_mapping(native_entity.id)
        native_entity.set_entity_mapping(extensive_entity.id)

    # get relation ownership
    def get_relation_ownership(self):
        print('get relation ownership')
        temp_aosp_relation_map = {}
        for relation in self.relation_android:
            temp_aosp_relation_map[str(relation.src) + relation.rel + str(relation.dest)] = relation

        for relation in self.relation_extensive:
            src = self.entity_extensive[relation.src]
            dest = self.entity_extensive[relation.dest]
            if src.not_aosp == 1 or dest.not_aosp == 1:
                relation.set_not_aosp(1)
            else:
                is_intrusive = dest.is_intrusive if relation.rel == Constant.R_annotate else src.is_intrusive
                if is_intrusive and src.entity_mapping > -1 and dest.entity_mapping > -1:
                    # if src.entity_mapping > -1 and dest.entity_mapping > -1:
                    try:
                        if temp_aosp_relation_map[str(src.entity_mapping) + relation.rel + str(dest.entity_mapping)]:
                            relation.set_not_aosp(0)
                    except KeyError:
                        relation.set_not_aosp(1)
                else:
                    relation.set_not_aosp(0)

    # get diff and extra useful aosp 'define' dep
    def detect_facade(self):
        facade_entities = set()
        for relation in self.relation_extensive:
            src = self.entity_extensive[relation.src]
            dest = self.entity_extensive[relation.dest]
            if src.not_aosp + dest.not_aosp == 1:
                self.facade_relations.append(relation)
                self.diff_relations.append(relation)
                facade_entities.add(src.id)
                facade_entities.add(dest.id)
                if relation.rel == Constant.define and dest.not_aosp == 1:
                    if dest.category == Constant.E_class:
                        if dest.name != Constant.anonymous_class and src.category != Constant.E_file:
                            self.inner_extensive_class_entities.append(dest.id)
                    elif dest.category == Constant.E_method:
                        self.method_extensive_entities.append(dest.id)
                    elif dest.category == Constant.E_variable:
                        if src.category != Constant.E_method:
                            self.class_var_extensive_entities.append(dest.id)
                        else:
                            self.method_var_extensive_entities.append(dest.id)
            elif src.not_aosp + dest.not_aosp == 2:
                self.diff_relations.append(relation)
            # 依赖切面扩充
            elif src.not_aosp == 0 and dest.not_aosp == 0:
                if relation.not_aosp == 1:
                    self.diff_relations.append(relation)
                    self.facade_relations.append(relation)
                    # facade_entities.add(src.id)
                    # facade_entities.add(dest.id)
                elif relation.rel == Constant.define or relation.rel == Constant.contain:
                    self.define_relations.append(relation)
            # 临时增加聚合依赖
            if relation.rel == Constant.define:
                if src.category == Constant.E_class and dest.category == Constant.E_variable:
                    type_entity_id = dest.typed
                    if type_entity_id != -1 and \
                            self.entity_extensive[type_entity_id].not_aosp != src.not_aosp:
                        self.agg_relations.append(relation)

        for e_id in facade_entities:
            self.facade_entities.append(self.entity_extensive[e_id])

    # out intrusive entities info
    def out_intrusive_info(self):
        def get_count_ownership():
            total_count = {'total': 0, 'native': 0, 'obsoletely native': 0, 'intrusive': 0, 'extensive': 0, 'unsure': 0}
            file_total_count = defaultdict(partial(defaultdict, int))
            for entity in self.entity_extensive:
                if entity.is_core_entity():
                    total_count['total'] += 1
                    file_total_count[entity.file_path]['total'] += 1
                    if entity.is_intrusive == 1:
                        total_count['intrusive'] += 1
                        file_total_count[entity.file_path]['intrusive'] += 1
                    elif entity.not_aosp == 0:
                        if entity.old_aosp <= 0:
                            total_count['native'] += 1
                            file_total_count[entity.file_path]['native'] += 1
                        elif entity.old_aosp >= 1:
                            total_count['obsoletely native'] += 1
                            file_total_count[entity.file_path]['obsoletely native'] += 1
                        else:
                            total_count['unsure'] += 1
                            file_total_count[entity.file_path]['unsure'] += 1
                    elif entity.not_aosp == 1:
                        total_count['extensive'] += 1
                        file_total_count[entity.file_path]['extensive'] += 1
            return total_count, file_total_count, ['total', 'native', 'obsoletely native', 'intrusive', 'extensive',
                                                   'unsure']

        def get_intrusive_count():
            total_count = {}
            header = ['access_modify', 'final_modify', 'annotation_modify', 'param_modify', 'import_extensive',
                      'parent_class_modify', 'parent_interface_modify',
                      'class_body_modify', 'inner_extensive_class', 'class_var_extensive', 'class_var_modify',
                      'method_body_modify', 'method_extensive', 'method_var_extensive', 'method_var_modify',
                      'Move Class', 'Rename Class',
                      'Move And Rename Class', 'Move Method', 'Rename Method',
                      'Move And Rename Method', 'Extract Method', 'Extract And Move Method', 'Rename Parameter',
                      'Add Parameter', 'Remove Parameter']
            for int_type in header:
                total_count.update({int_type: 0})

            file_total_count = defaultdict(partial(defaultdict, int))
            for extensive_entity in self.entity_extensive:
                if extensive_entity.is_intrusive and extensive_entity.entity_mapping != -1 and extensive_entity.not_aosp == 0:
                    native_entity = self.entity_android[extensive_entity.entity_mapping]
                    if extensive_entity.hidden:
                        source_hd = Constant.hidden_map(native_entity.hidden)
                        update_hd = Constant.hidden_map(extensive_entity.hidden)
                        if source_hd and update_hd and source_hd != update_hd:
                            self.hidden_modify_entities.append(extensive_entity.id)
                            extensive_entity.set_intrusive_modify('hidden_modify', source_hd + '-' + update_hd)
                    if extensive_entity.accessible != native_entity.accessible:
                        self.access_modify_entities.append(extensive_entity.id)
                        extensive_entity.set_intrusive_modify('access_modify',
                                                              native_entity.accessible + '-' + extensive_entity.accessible)
                        total_count['access_modify'] += 1
                        file_total_count[extensive_entity.file_path]['access_modify'] += 1

                    if extensive_entity.final != native_entity.final:
                        self.final_modify_entities.append(extensive_entity.id)
                        extensive_entity.set_intrusive_modify('final_modify',
                                                              get_final(native_entity.final) + '-' + get_final(
                                                                  extensive_entity.final))
                        total_count['final_modify'] += 1
                        file_total_count[extensive_entity.file_path]['final_modify'] += 1
                    if not Compare.compare_list(extensive_entity.annotations, native_entity.annotations):
                        self.annotation_modify_entities.append(extensive_entity.id)
                        extensive_entity.set_intrusive_modify('annotation_modify',
                                                              f'{native_entity.annotations}-{extensive_entity.annotations}')
                        total_count['annotation_modify'] += 1
                        file_total_count[extensive_entity.file_path]['annotation_modify'] += 1

                    if extensive_entity.category == Constant.E_method and extensive_entity.raw_type != native_entity.raw_type:
                        self.return_type_modify_entities.append(extensive_entity.id)
                        extensive_entity.set_intrusive_modify('return_type_modify',
                                                              native_entity.raw_type + '-' + extensive_entity.raw_type)

                    if extensive_entity.parent_class != native_entity.parent_class:
                        self.parent_class_modify_entities.append(extensive_entity.id)
                        extensive_entity.set_intrusive_modify('parent_class_modify',
                                                              f'{native_entity.parent_class}-{extensive_entity.parent_class}')
                        total_count['parent_class_modify'] += 1
                        file_total_count[extensive_entity.file_path]['parent_class_modify'] += 1
                    if not Compare.compare_list(native_entity.parent_interface, extensive_entity.parent_interface):
                        self.parent_interface_modify_entities.append(extensive_entity.id)
                        extensive_entity.set_intrusive_modify('parent_interface_modify',
                                                              f'{native_entity.parent_interface}-{extensive_entity.parent_interface}')
                        total_count['parent_interface_modify'] += 1
                        file_total_count[extensive_entity.file_path]['parent_interface_modify'] += 1
                    if extensive_entity.category in [Constant.E_class, Constant.E_interface]:
                        self.class_body_modify_entities.append(extensive_entity.id)
                        extensive_entity.set_intrusive_modify('class_body_modify', '-')
                        total_count['class_body_modify'] += 1
                        file_total_count[extensive_entity.file_path]['class_body_modify'] += 1
                    if extensive_entity.category == Constant.E_method:
                        self.method_body_modify_entities.append(extensive_entity.id)
                        extensive_entity.set_intrusive_modify('method_body_modify', '-')
                        total_count['method_body_modify'] += 1
                        file_total_count[extensive_entity.file_path]['method_body_modify'] += 1
                        if extensive_entity.parameter_names != native_entity.parameter_names:
                            self.params_modify_entities.append(extensive_entity.id)
                            extensive_entity.set_intrusive_modify('param_modify',
                                                                  native_entity.parameter_names + '-' + extensive_entity.parameter_names)
                            total_count['param_modify'] += 1
                            file_total_count[extensive_entity.file_path]['param_modify'] += 1
                    if extensive_entity.category == Constant.E_variable:
                        if self.entity_extensive[extensive_entity.parentId].category == Constant.E_method:
                            self.method_var_modify_entities.append(extensive_entity.id)
                            extensive_entity.set_intrusive_modify('method_var_modify', '-')
                            total_count['method_var_modify'] += 1
                            file_total_count[extensive_entity.file_path]['method_var_modify'] += 1
                        else:
                            self.class_var_modify_entities.append(extensive_entity.id)
                            extensive_entity.set_intrusive_modify('class_var_modify', '-')
                            total_count['class_var_modify'] += 1
                            file_total_count[extensive_entity.file_path]['class_var_modify'] += 1

            for rel in self.import_extensive_relation:
                total_count['import_extensive'] += 1
                file_total_count[self.entity_extensive[rel.src].file_path]['import_extensive'] += 1

            for entity_id in self.inner_extensive_class_entities:
                total_count['inner_extensive_class'] += 1
                file_total_count[self.entity_extensive[entity_id].file_path]['inner_extensive_class'] += 1

            for entity_id in self.class_var_extensive_entities:
                total_count['class_var_extensive'] += 1
                file_total_count[self.entity_extensive[entity_id].file_path]['class_var_extensive'] += 1

            for entity_id in self.method_extensive_entities:
                total_count['method_extensive'] += 1
                file_total_count[self.entity_extensive[entity_id].file_path]['method_extensive'] += 1

            for entity_id in self.method_var_extensive_entities:
                total_count['method_var_extensive'] += 1
                file_total_count[self.entity_extensive[entity_id].file_path]['method_var_extensive'] += 1

            for move_type, move_entity_list in self.refactor_entities.items():
                for entity_id in move_entity_list:
                    total_count[move_type] += 1
                    file_total_count[self.entity_extensive[entity_id].file_path][move_type] += 1
            return total_count, file_total_count, header

        ownership_count, file_owner_count, owner_keys = get_count_ownership()
        intrusive_count, file_intrusive_count, intrusive_keys = get_intrusive_count()

        FileCSV.write_owner_to_csv(self.out_path, 'final_ownership', self.entity_extensive)
        FileCSV.write_dict_to_csv(self.out_path, 'final_ownership_count', [ownership_count], 'w')
        FileCSV.write_file_to_csv(self.out_path, 'final_ownership_file_count', file_owner_count, 'file',
                                  owner_keys)
        FileCSV.write_dict_to_csv(self.out_path, 'intrusive_count', [intrusive_count], 'w')
        FileCSV.write_file_to_csv(self.out_path, 'intrusive_file_count', file_intrusive_count, 'file',
                                  intrusive_keys)
        FileCSV.write_dict_to_csv(self.out_path, 'owner_proc', self.owner_proc, 'w')
        FileCSV.write_dict_to_csv(self.out_path, 'owner_proc_count', [self.owner_proc_count], 'w')
        FileCSV.write_entity_to_csv(self.out_path, 'param_modify_entities',
                                    [self.entity_extensive[entity_id] for entity_id in self.params_modify_entities],
                                    'modify')
        FileCSV.write_entity_to_csv(self.out_path, 'access_modify_entities',
                                    [self.entity_extensive[entity_id] for entity_id in self.access_modify_entities],
                                    'modify')
        FileCSV.write_entity_to_csv(self.out_path, 'final_modify_entities',
                                    [self.entity_extensive[entity_id] for entity_id in self.final_modify_entities],
                                    'modify')
        FileCSV.write_entity_to_csv(self.out_path, 'class_var_modify_entities',
                                    [self.entity_extensive[entity_id] for entity_id in self.class_var_modify_entities],
                                    'modify')
        FileCSV.write_entity_to_csv(self.out_path, 'method_var_modify_entities',
                                    [self.entity_extensive[entity_id] for entity_id in self.method_var_modify_entities],
                                    'modify')
        FileCSV.write_entity_to_csv(self.out_path, 'class_var_extensive_entities',
                                    [self.entity_extensive[entity_id] for entity_id in
                                     self.class_var_extensive_entities],
                                    'modify')
        FileCSV.write_entity_to_csv(self.out_path, 'annotation_modify_entities',
                                    [self.entity_extensive[entity_id] for entity_id in self.annotation_modify_entities],
                                    'modify')

        FileCSV.write_entity_to_csv(self.out_path, 'parent_class_modify_entities',
                                    [self.entity_extensive[entity_id] for entity_id in
                                     self.parent_class_modify_entities],
                                    'modify')

        FileCSV.write_entity_to_csv(self.out_path, 'parent_interface_modify_entities',
                                    [self.entity_extensive[entity_id] for entity_id in
                                     self.parent_interface_modify_entities],
                                    'modify')
        FileCSV.write_entity_to_csv(self.out_path, 'return_type_modify_entities',
                                    [self.entity_extensive[entity_id] for entity_id in
                                     self.return_type_modify_entities],
                                    'modify')
        FileJson.write_data_to_json(self.out_path,
                                    [rel.to_detail_json(self.entity_extensive) for rel in
                                     self.import_extensive_relation],
                                    'add_import.json')
        FileCSV.write_entity_to_csv(self.out_path, 'inner_extensive_class_entities',
                                    [self.entity_extensive[entity_id] for entity_id in
                                     self.inner_extensive_class_entities],
                                    'modify')

        temp_ref = set()
        for _, v in self.refactor_entities.items():
            temp_ref.update(v)
        FileCSV.write_entity_to_csv(self.out_path, 'refactor_entities',
                                    [self.entity_extensive[entity_id] for entity_id in temp_ref],
                                    'modify')

    def out_facade_info(self):
        print('output facade info')

        def info_init():
            base_info: dict = {'total_relations': len(self.relation_extensive),
                               'total_entities': len(self.entity_extensive),
                               'facade_relation': len(self.facade_relations),
                               'facade_entities': len(self.facade_entities),
                               'facade_e2n': 0, 'facade_n2e': 0,
                               'facade_n2n': 0,
                               'facade_n2n(intrusive2actively)': 0,
                               'facade_n2n(intrusive2obsolotely)': 0,
                               'facade_n2n(intrusive2intrusive)': 0,
                               }
            relation_info = {
                'all_e2n': 0, 'all_n2e': 0, 'all_n2n': 0,
            }
            rel_src = defaultdict(partial(defaultdict, int))
            for rel_type in Constant.Relations:
                relation_info[rel_type + '_e2n'] = 0
                relation_info[rel_type + '_n2e'] = 0
                relation_info[rel_type + '_n2n'] = 0
            relation_info.update({'Define_e': 0, 'Parameter_e': 0})
            entity_info = {
                'Method': [0, 0], 'Interface': [0, 0], 'Class': [0, 0], 'Variable': [0, 0], 'Annotation': [0, 0],
                'File': [0, 0], 'Package': [0, 0], 'Enum': [0, 0], 'Enum Constant': [0, 0],
            }

            for relation in self.relation_extensive:
                rel_src[relation.rel][relation.src] += 1

            return base_info, relation_info, entity_info, rel_src

        def get_index(relation: Relation, is_agg: bool) -> str:
            src_owner = self.entity_extensive[relation.src].not_aosp
            dest_owner = self.entity_extensive[relation.dest].not_aosp

            def get_index_str(index: int):
                if index:
                    return 'e'
                else:
                    return 'n'

            if is_agg:
                return get_index_str(src_owner) + '2' + get_index_str(
                    self.entity_extensive[self.entity_extensive[relation.dest].typed].not_aosp)
            if relation.rel == Constant.R_annotate:
                return get_index_str(dest_owner) + '2' + get_index_str(src_owner)
            elif relation.rel == Constant.define:
                if self.entity_extensive[relation.src].not_aosp:
                    if self.entity_extensive[relation.src].refactor:
                        return get_index_str(src_owner) + '2' + get_index_str(dest_owner)
                    else:
                        return 'e'
            elif relation.rel == Constant.param and self.entity_extensive[relation.src].not_aosp:
                return 'e'
            return get_index_str(src_owner) + '2' + get_index_str(dest_owner)

        # 临时添加 聚合 依赖
        def get_key(relation: Relation, is_agg: bool) -> str:
            rel_type = relation.rel
            if is_agg:
                rel_type = 'Aggregate'
            return rel_type + '_' + get_index(relation, is_agg)

        # start output
        facade_relations_divide_ownership = {'e2n': [], 'n2e': [], 'n2n': [], 'e': []}
        source_facade_relation: Dict[str, List[Relation]] = {'e2n': [], 'n2e': [], 'n2n': [], 'e': []}
        facade_base_info, facade_relation_info, facade_entity_info, rel_src_map = info_init()

        for rel in self.facade_relations:
            facade_relation_info[get_key(rel, False)] += 1
            facade_relations_divide_ownership[get_index(rel, False)].append(rel.to_detail_json(self.entity_extensive))
            source_facade_relation[get_index(rel, False)].append(rel)
        for rel in self.agg_relations:
            facade_relation_info[get_key(rel, True)] += 1
            # 聚合重复计数了 define依赖
            # facade_relations_divide_ownership[get_index(rel, True)].append(rel.to_detail_json(self.entity_extensive))
            # source_facade_relation[get_index(rel, True)].append(rel)

        facade_base_info['facade_n2e'] = len(facade_relations_divide_ownership['n2e'])
        facade_base_info['facade_e2n'] = len(facade_relations_divide_ownership['e2n'])
        facade_base_info['facade_n2n'] = len(facade_relations_divide_ownership['n2n'])

        # 侵入式调用原生(intrusive obsoletely actively)的情况
        for rel in facade_relations_divide_ownership['n2n']:
            if rel['dest']['ownership'] == 'actively native':
                facade_base_info['facade_n2n(intrusive2actively)'] += 1
            elif rel['dest']['ownership'] == 'intrusive native':
                facade_base_info['facade_n2n(intrusive2intrusive)'] += 1
            else:
                facade_base_info['facade_n2n(intrusive2obsolotely)'] += 1

        # 侵入式调用原生中 属于原生以及属于扩展的情况
        facade_i2n = defaultdict(partial(defaultdict, partial(defaultdict, int)))
        for ent in self.entity_extensive:
            if ent.is_intrusive == 1:
                for rel_type in Constant.Relations:
                    facade_i2n[ent.id][rel_type]['n2a'] = rel_src_map[rel_type][ent.id]
        for rel in source_facade_relation['n2n']:
            facade_i2n[rel.src][rel.rel]['e_n2n'] += 1
        entities = facade_i2n.keys()
        for rel in source_facade_relation['n2e']:
            if rel.src in entities:
                facade_i2n[rel.src][rel.rel]['n2e'] += 1

        res_n2n = []
        res_n2n_source = []
        for ent_id, rel_info in facade_i2n.items():
            temp_n2n = {'entity_id': ent_id, 'total_nat_n2n': 0, 'total_ext_n2n': 0}
            temp_n2n_source = {'entity_id': ent_id, 'total_nat_n2n': 0, 'total_ext_n2n': 0}
            temp_total_n_n2n = 0
            temp_total_e_n2n = 0
            for rel_type in Constant.Relations:
                n2a = rel_src_map[rel_type][ent_id]
                n2e = facade_i2n[ent_id][rel_type]['n2e']
                e_n2n = facade_i2n[ent_id][rel_type]['e_n2n']
                n_n2n = n2a - n2e - e_n2n

                temp_total_n_n2n += n_n2n
                temp_total_e_n2n += e_n2n

                temp_n2n.update(
                    {f'nat_n2n_{rel_type}': n_n2n,
                     f'ext_n2n_{rel_type}': e_n2n})
                temp_n2n_source.update(
                    {f'n2a_{rel_type}': n2a,
                     f'n2e_{rel_type}': n2e,
                     f'nat_n2n_{rel_type}': n_n2n,
                     f'ext_n2n_{rel_type}': e_n2n})
            temp_n2n['total_nat_n2n'] = temp_total_n_n2n
            temp_n2n['total_ext_n2n'] = temp_total_e_n2n
            temp_n2n_source['total_nat_n2n'] = temp_total_n_n2n
            temp_n2n_source['total_ext_n2n'] = temp_total_e_n2n
            res_n2n.append(temp_n2n)
            res_n2n_source.append(temp_n2n_source)
        res_n2n_stat = {'total_intrusive': len(res_n2n), 'e_0': 0, 'e_1-5': 0, 'e_6-10': 0, 'e_11-': 0}
        count_n_n2n = 0
        count_e_n2n = 0
        for info in res_n2n:
            n_n2n = info['total_nat_n2n']
            e_n2n = info['total_ext_n2n']
            count_n_n2n += n_n2n
            count_e_n2n += e_n2n
            if e_n2n == 0:
                res_n2n_stat['e_0'] += 1
            elif 1 <= e_n2n <= 5:
                res_n2n_stat['e_1-5'] += 1
            elif 6 <= e_n2n <= 10:
                res_n2n_stat['e_6-10'] += 1
            else:
                res_n2n_stat['e_11-'] += 1
        res_n2n_rel_stat = {'total_intrusive': len(res_n2n),
                            'count_n_n2n': float(count_n_n2n / (count_e_n2n + count_n_n2n)),
                            'count_e_n2n': float(count_e_n2n / (count_e_n2n + count_n_n2n))}
        res_n2n_stat_per = {'total_intrusive': len(res_n2n), 'e_0': 0, 'e_1%': 0, 'e_2%': 0, 'e_3%': 0}
        for info in res_n2n:
            n_n2n = info['total_nat_n2n']
            e_n2n = info['total_ext_n2n']
            if e_n2n == 0:
                res_n2n_stat_per['e_0'] += 1
            elif float(e_n2n / (e_n2n + n_n2n)) < 0.1:
                res_n2n_stat_per['e_1%'] += 1
            elif float(e_n2n / (e_n2n + n_n2n)) < 0.2:
                res_n2n_stat_per['e_2%'] += 1
            else:
                res_n2n_stat_per['e_3%'] += 1

        facade_base_info['facade_relation'] = facade_base_info['facade_n2e'] + facade_base_info['facade_e2n'] + \
                                              facade_base_info['facade_n2n']
        facade_relation_info['all_e2n'] = facade_base_info['facade_e2n']
        facade_relation_info['all_n2e'] = facade_base_info['facade_n2e']
        facade_relation_info['all_n2n'] = facade_base_info['facade_n2n']

        for ent in self.facade_entities:
            facade_entity_info[ent.category][ent.not_aosp] += 1
        FileCSV.write_dict_to_csv(self.out_path, 'facade_base_info_count', [facade_base_info], 'w')
        FileCSV.write_dict_to_csv(self.out_path, 'facade_relation_info_count', [facade_relation_info], 'w')
        FileCSV.write_dict_to_csv(self.out_path, 'facade_entity_info_count', [facade_entity_info], 'w')
        FileCSV.write_entity_to_csv(self.out_path, 'facade_info_entities',
                                    self.facade_entities, 'modify')
        facade_relations_divide_ownership.pop('e')
        FileJson.write_to_json(self.out_path, facade_relations_divide_ownership, 'facade')

        FileCSV.write_dict_to_csv(self.out_path, 'facade_n2n_count', res_n2n, 'w')
        FileCSV.write_dict_to_csv(self.out_path, 'facade_n2n_stat', [res_n2n_stat], 'w')

        project = {'project': self.out_path.rsplit('\\')[-1]}
        temp_base = project.copy()
        temp_base.update(facade_base_info)
        temp_rel = project.copy()
        temp_rel.update(facade_relation_info)
        temp_n2n_stat = project.copy()
        temp_n2n_stat.update(res_n2n_stat)
        temp_n2n_rel_stat = project.copy()
        temp_n2n_rel_stat.update(res_n2n_rel_stat)
        FileCSV.write_dict_to_csv('D:\\Honor\\match_res', 'facade_base_info_count', [temp_base], 'a')
        FileCSV.write_dict_to_csv('D:\\Honor\\match_res', 'facade_relation_info_count', [temp_rel], 'a')
        FileCSV.write_dict_to_csv('D:\\Honor\\match_res', 'facade_n2n_stat', [temp_n2n_stat], 'a')
        FileCSV.write_dict_to_csv('D:\\Honor\\match_res', 'facade_n2n_rel_stat', [temp_n2n_rel_stat], 'a')


# valid entity map
def valid_entity_mapping(entity: Entity, search_name: str, search_param: str):
    return entity.qualifiedName == search_name and entity.parameter_names == search_param


# get parent
def get_parent_entity(entity: int, entity_set: List[Entity]):
    return entity_set[entity_set[entity].parentId]


# get parent Anonymous_class
def get_parent_anonymous_class(entity: int, entity_set: List[Entity]):
    temp = entity
    while entity_set[temp].name != Constant.anonymous_class:
        temp = get_parent_entity(temp, entity_set).id
    return entity_set[temp]


def get_final(is_final: bool):
    if is_final:
        return 'final'
    return ''
