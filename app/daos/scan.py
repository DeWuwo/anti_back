from datetime import datetime
from flask import current_app
from arango.collection import StandardCollection
from app.utils import FormatTime
from app.daos.model import Scan


class DaoScan:
    collection_scan: StandardCollection

    def __init__(self):
        db = current_app.config['db'].connect()
        if not db.has_collection(Scan.__collection__):
            db.create_collection(Scan)
        self.collection_scan = db[Scan.__collection__]

    def add_scan(self, native, extensive, native_node, extensive_node, extensive_url):
        sc = {
            'native': native,
            'native_node': native_node,
            'extensive': extensive,
            'extensive_node': extensive_node,
            'extensive_url': extensive_url,
            'scan_time': FormatTime.format_time(datetime.now()),
            'state': 'running'
        }

        return self.collection_scan.insert(sc)['_key']

    def query_all_scan(self, page: int, limit: int):
        cursor = self.collection_scan.all(skip=page * limit, limit=limit)
        scan_list = [doc for doc in cursor]
        return scan_list, len(scan_list)

    def query_scan_by_id(self, scan_id: str):
        cursor = self.collection_scan.find({"_key": scan_id})
        scan_list = [doc for doc in cursor]
        return scan_list
