from app.daos.scan import DaoScan
from app.daos.entity import DaoEntity
from app.daos.relation import DaoRelation
from app.daos.anti import DaoAnti
from algorithm.utils import FileJson, FileCSV, Constant
from algorithm.model.build_model import BuildModel
from algorithm.model.patterns.coupling_patterns import CouplingPattern
from algorithm.model.match import Match
from algorithm.model.git_history import GitHistory
from algorithm.model.mc.mc import MC
from algorithm.script.open_os import OpenOS


class AntiRes:
    def __init__(self, res):
        self.antis = res


class AntiFileRes:
    def __init__(self, fileset, res):
        self.file_set = fileset
        self.antis = res


class IManagerAnti:
    _page: int
    _limit: int
    _scan_id: int
    _scan: DaoScan
    _entity: DaoEntity
    _relation: DaoRelation
    _anti: DaoAnti

    def __init__(self, page=0, limit=10):
        self._page = page
        self._limit = limit
        self._scan = DaoScan()
        self._entity = DaoEntity()
        self._relation = DaoRelation()
        self._anti = DaoAnti()

    def get_anti(self, scan_id, aid):
        raise NotImplementedError()

    def get_antis_by_style(self, scan_id):
        raise NotImplementedError()

    def get_all_anti(self, scan_id):
        raise NotImplementedError()

    def start_new_scan(self, native, extensive, native_node, extensive_node, extensive_url) -> None:
        raise NotImplementedError()


class ManagerAnti(IManagerAnti):
    def get_anti_by_id(self, scan_id, aid):
        results = self._anti.query_anti_by_id(scan_id, aid)
        if not results:
            raise Exception
        res = results[0]
        rels = []
        for rel_id in res['rels']:
            rel = self._relation.query_relation_by_id(scan_id, rel_id)[0]
            rel['src'] = self._entity.query_entity_by_id(scan_id, rel['src'])
            rel['dest'] = self._entity.query_entity_by_id(scan_id, rel['dest'])
            rels.append(rel)
        res['rels'] = rels
        return AntiRes(res)

    def get_antis_by_style(self, scan_id):
        res = self._anti.query_antis_by_style(scan_id)
        return AntiRes(res)

    def get_antis_by_file(self, scan_id, file):
        res = self._anti.query_antis_by_file(scan_id, file)
        return AntiRes(res)

    def group_antis_by_file(self, scan_id):
        file_set = set()
        res = {}
        antis = self.get_all_anti(scan_id)
        for anti in antis:
            file_set = file_set | set(anti['files'])
        for file in file_set:
            res.update({file: self._anti.query_antis_by_file(scan_id, file)})
        return AntiFileRes(list(file_set), res)

    def get_all_anti(self, scan_id):
        res = self._anti.query_all_anti(scan_id)
        return res

    def start_new_scan(self, native, extensive, native_node, extensive_node, extensive_url):
        scan_id = self._scan.add_scan(native, extensive, native_node, extensive_node, extensive_url)
        oss = OpenOS()
        aosp_code_path, assi_code_path, aosp_dep_path, assi_dep_path, base_aosp_dep_path, aosp_commit, assi_commit, aosp_base_commit, out_path, aosp_hidden, assi_hidden = oss.get_path(
            *['aospa', 'sapphire', 'base', '15d9159eb00fb7fd92f9dc249af588f655fd8f66', '898ad0236f79d81514806e4f4ca3a2fe401e0705', 'null', 'null', 'android-12'])
        entities_honor, cells_honor, entities_stat_honor, entities_aosp, cells_aosp, entities_stat_aosp = \
            FileJson.read_from_json(aosp_dep_path, assi_dep_path)
        # 读取模块责任田
        module_blame = out_path

        # build base model
        git_history = GitHistory(aosp_code_path, assi_code_path, assi_dep_path, 'D:\\Honor\\source_code\\utils\\bin',
                                 out_path)

        base_model = BuildModel(entities_honor, cells_honor, entities_stat_honor, entities_aosp, cells_aosp,
                                entities_stat_aosp, git_history, out_path)
        # 存入实体
        self._entity.add_entity_list([ent.handle_to_db() for ent in base_model.entity_extensive], scan_id)
        # 存入依赖
        self._relation.add_relation_list([rel.to_db_json() for rel in base_model.relation_extensive], scan_id)

        mc = MC(out_path, assi_code_path, list(base_model.file_set_extension), aosp_code_path,
                list(base_model.file_set_android))
        mc.get_mc()

        pattern_match = Match(base_model, out_path, module_blame, assi_code_path)
        # match coupling pattern
        coupling_pattern = CouplingPattern()
        anti_res = pattern_match.start_match_pattern(coupling_pattern)
        self._anti.add_anti_list(anti_res, scan_id)
