from typing import List
from algorithm.utils import Constant
from algorithm.model.dependency.entity import Entity


class Relation:
    src: int
    dest: int
    rel: str
    bind_var: int
    setAccessible: int
    invoke: int
    not_aosp: int
    id: int

    def __init__(self, **kwargs):
        self.bind_var = -1
        self.setAccessible = -1
        self.invoke = -1
        self.src = kwargs['src']
        self.dest = kwargs['dest']
        self.not_aosp = 0
        self.id = -1
        self.src_file = ''
        self.dest_file = ''

        for key in kwargs['values']:
            if key == 'bindVar':
                self.bind_var = kwargs['values'][key]
            elif key == 'modifyAccessible':
                self.setAccessible = 1
            elif key == 'invoke':
                self.invoke = 1
            else:
                self.rel = key

    def toJson(self):
        relation = {self.rel: 1}
        if self.bind_var != -1:
            relation['bindVar'] = self.bind_var
        if self.rel == Constant.reflect:
            relation['modifyAccessible'] = True if self.setAccessible else False
            relation['invoke'] = True if self.invoke else False
        return {"src": self.src, "values": relation, "dest": self.dest}

    def __str__(self):
        return str(self.src) + self.rel + str(self.dest)

    def to_str(self, entities: List[Entity]):
        return entities[self.src].qualifiedName + self.rel + entities[self.dest].qualifiedName

    def to_detail_json(self, entities: List[Entity]):
        relation = {self.rel: 1}
        if self.bind_var != -1:
            relation['bindVar'] = self.bind_var
        if self.rel == Constant.reflect:
            relation['modifyAccessible'] = True if self.setAccessible else False
            relation['invoke'] = True if self.invoke else False
        return {"src": entities[self.src].toJson(), "values": relation,
                "dest": entities[self.dest].toJson()}

    def to_db_json(self):
        relation = {self.rel: 1}
        if self.bind_var != -1:
            relation['bindVar'] = self.bind_var
        if self.rel == Constant.reflect:
            relation['modifyAccessible'] = True if self.setAccessible else False
            relation['invoke'] = True if self.invoke else False
        return {
            "id": self.id,
            "src": self.src,
            "rel_type": self.rel,
            "dest": self.dest
        }

    def set_not_aosp(self, not_aosp):
        self.not_aosp = not_aosp

    def set_id(self, rid):
        self.id = rid

    def is_core_rel(self):
        return self.rel in [Constant.define, Constant.call, Constant.inherit, Constant.implement]

    def set_files(self, entities: List[Entity]):
        self.src_file = entities[self.src].file_path
        self.dest_file = entities[self.dest].file_path

    def get_files(self):
        return {self.src_file, self.dest_file}
