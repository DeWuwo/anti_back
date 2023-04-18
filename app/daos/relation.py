from flask import current_app
from arango.collection import StandardCollection
from typing import List

from app.daos.model import Relation


class DaoRelation:
    collection_relation: StandardCollection

    def __init__(self):
        db = current_app.config['db'].connect()
        if not db.has_collection(Relation.__collection__):
            db.create_collection(Relation)
        self.collection_relation = db[Relation.__collection__]

    def add_relation(self, relation: dict, scan_id: str):
        relation.update({"_key": f"{scan_id}_{relation['id']}", "scan_id": scan_id})
        self.collection_relation.insert(relation)

    def add_relation_list(self, relations: List[dict], scan_id: str):
        for rel in relations:
            rel.update({"_key": f"{scan_id}_{rel['id']}", "scan_id": scan_id})
        self.collection_relation.insert_many(relations)

    def query_relation_by_id(self, scan_id: str, rid):
        cursor = self.collection_relation.find({"scan_id": scan_id, "id": rid})
        relation_list = [doc for doc in cursor]
        return relation_list

    def query_all_relation(self):
        cursor = self.collection_relation.all()
        relation_list = [doc for doc in cursor]
        return relation_list
