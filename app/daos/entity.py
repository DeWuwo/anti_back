from flask import current_app
from arango.collection import StandardCollection
from typing import List

from app.daos.model import Entity


class DaoEntity:
    collection_entity: StandardCollection

    def __init__(self):
        db = current_app.config['db'].connect()
        if not db.has_collection(Entity.__collection__):
            db.create_collection(Entity)
        self.collection_entity = db[Entity.__collection__]

    def add_entity(self, entity: dict, scan_id: str):
        sc = entity
        sc.update({"_key": f"{scan_id}_{entity['id']}", "scan_id": scan_id})
        self.collection_entity.insert(sc)

    def add_entity_list(self, entities: List[dict], scan_id: str):
        for ent in entities:
            ent.update({"_key": f"{scan_id}_{ent['id']}", "scan_id": scan_id})
        self.collection_entity.insert_many(entities)

    def query_entity_by_id(self, scan_id: str, rid):
        cursor = self.collection_entity.find({"scan_id": scan_id, "id": rid})
        entity_list = [doc for doc in cursor]
        return entity_list

    def query_all_entity(self, scan_id: str, page: int, limit: int):
        cursor = self.collection_entity.find({"scan_id": scan_id}, skip=page * limit, limit=limit)
        entity_list = [doc for doc in cursor]
        return entity_list
