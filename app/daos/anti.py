from flask import current_app
from arango.collection import StandardCollection
from typing import List

from app.daos.model import Anti


class DaoAnti:
    collection_anti: StandardCollection

    def __init__(self):
        db = current_app.config['db'].connect()
        if not db.has_collection(Anti.__collection__):
            db.create_collection(Anti)
        self.collection_anti = db[Anti.__collection__]
        self.db = db

    def add_anti(self, anti: dict, scan_id: str):
        anti.update({"_key": f"{scan_id}_{anti['id']}", "_scan_id": scan_id})
        self.collection_anti.insert(anti)

    def add_anti_list(self, antis: List[dict], scan_id: str):
        anti_res_db = []
        for item in antis:
            for mode, mode_res in item.items():
                for style_name, style in mode_res.items():
                    anti_index = 0
                    for exa in style['res']:
                        exa_db = {'scan_id': scan_id, 'id': anti_index, 'category': mode, 'style': style_name,
                                  'rels': [], 'files': []}
                        exa_files = set()
                        for rel in exa['value']:
                            exa_db['rels'].append(rel.id)
                            exa_files = exa_files | rel.get_files()
                        exa_db['files'] = list(exa_files)
                        anti_res_db.append(exa_db)
                        anti_index += 1
        self.collection_anti.insert_many(anti_res_db)

    def query_all_anti(self, scan_id):
        cursor = self.collection_anti.find({"scan_id": scan_id})
        anti_list = [doc for doc in cursor]
        return anti_list

    def query_anti_by_id(self, scan_id: str, aid):
        cursor = self.collection_anti.find({"scan_id": scan_id, 'id': aid})
        res = [doc for doc in cursor]
        return res

    def query_antis_by_file(self, scan_id: str, file):
        aql = f"FOR a IN anti FILTER a.scan_id == '{scan_id}' && '{file}' IN a.files COLLECT style = a.style INTO antis " + \
              "RETURN {style, count: LENGTH(antis[*]), antis: antis[*].a.id}"
        cursor = self.db.aql.execute(aql)
        res = [doc for doc in cursor]
        return res

    def query_antis_by_style(self, scan_id: str):
        aql = f"FOR a IN anti FILTER a.scan_id == '{scan_id}' COLLECT style = a.style INTO antis" + \
              " RETURN {style, count: LENGTH(antis[*]), antis: antis[*].a.id} "
        cursor = self.db.aql.execute(aql)
        res = [doc for doc in cursor]
        return res

    def group_anti_by_style(self, scan_id: str, style):
        cursor = self.collection_anti.find({"scan_id": scan_id, 'style': style})
        res = [doc for doc in cursor]
        return res
