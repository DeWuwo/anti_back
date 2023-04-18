from app.daos.entity import DaoEntity
from app.models.manager_scan import ManagerScan
from app.models.manager_files import ManagerFile


class EntityListRes:
    def __init__(self, res, count):
        self.res = res
        self.count = count


class EntityRes:
    def __init__(self, entity, file):
        self.entity = entity
        self.file = file


class IManagerEntity:
    _page: int
    _limit: int
    _scan_id: str
    _dao: DaoEntity

    def __init__(self, scan_id, page=0, limit=10):
        self._page = page
        self._limit = limit
        self._scan_id = scan_id
        self._dao = DaoEntity()

    def add_entity(self, entity) -> None:
        raise NotImplementedError()

    def get_all_entity(self):
        raise NotImplementedError()

    def get_entity_by_id(self, eid):
        raise NotImplementedError()


class ManagerEntity(IManagerEntity):
    def add_entity(self, entity) -> str:
        entity_id = self._dao.add_entity(entity, self._scan_id)
        return entity_id

    def get_all_entity(self):
        res, count = self._dao.query_all_entity(self._scan_id, self._page, self._limit)
        return EntityListRes(res, count)

    def get_entity_by_id(self, eid):
        res = self._dao.query_entity_by_id(self._scan_id, eid)
        if not res:
            raise Exception
        scan_info = ManagerScan().get_scan(self._scan_id)
        project = f"{scan_info['extensive']}_{scan_info['extensive_node']}"
        entity_file = ManagerFile().get_file_text(project, res[0]['file_path'])
        return EntityRes(res[0], entity_file)
