from arango_orm import Collection
from arango_orm.fields import String, Integer, List, DateTime


class Scan(Collection):
    __collection__ = 'scan'
    _key = String(required=True)  # registration number
    native = String(required=True)
    native_node = String(required=True)
    extensive = String(required=True)
    extensive_node = String(required=True)
    extensive_url = String(required=True)
    scan_time = DateTime()
    state = String(required=True)


class Entity(Collection):
    __collection__ = 'entity'
    _key = String(required=True)  # registration number
    name = String(required=True, allow_none=False)
    category = String(required=True, allow_none=False)
    file_path = String(required=True, allow_none=False)
    id = Integer(required=True, allow_none=False)


class Relation(Collection):
    __collection__ = 'relation'
    _key = String(required=True)  # registration number
    src = Integer(required=True, allow_none=False)
    dest = Integer(required=True, allow_none=False)
    rel_type = String(required=True, allow_none=False)
    id = Integer(required=True, allow_none=False)


class Anti(Collection):
    __collection__ = 'anti'
    _key = String(required=True)  # registration number
    category = String(required=True, allow_none=False)
    style = String(required=True, allow_none=False)
    rels = List(cls_or_instance=String)
    id = Integer(required=True, allow_none=False)