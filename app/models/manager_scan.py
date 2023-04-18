from app.daos.scan import DaoScan


class ScanListRes:
    def __init__(self, res, count):
        self.res = res
        self.count = count


class IManagerScan:
    _page: int
    _limit: int
    _dao: DaoScan

    def __init__(self, page=0, limit=10):
        self._page = page
        self._limit = limit
        self._dao = DaoScan()

    def add_scan(self, native, extensive, native_node, extensive_node, extensive_url) -> None:
        raise NotImplementedError()

    def get_all_scan(self):
        raise NotImplementedError()


class ManagerScan(IManagerScan):
    def add_scan(self, native, extensive, native_node, extensive_node, extensive_url) -> str:
        scan_id = self._dao.add_scan(native, extensive, native_node, extensive_node, extensive_url)
        return scan_id

    def get_all_scan(self):
        res, count = self._dao.query_all_scan(self._page, self._limit)
        return ScanListRes(res, count)

    def get_scan(self, scan_id):
        scans = self._dao.query_scan_by_id(scan_id)
        if not scans:
            raise
        return scans[0]