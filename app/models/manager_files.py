import os
from typing import List
from app.utils import DealFile
from app.models.errors import ProjectNotFound, NetWorkError, FileReadError


class ProjectListRes:
    def __init__(self, res, count):
        self.res = res
        self.count = count


class IManagerFile:
    _project_id: int
    _project_path: str

    def __init__(self):
        self._project_path = "/assets/projects/"

    def get_project_path(self, path) -> List:
        raise NotImplementedError()

    def fetch_from_git(self, git_mirror, path):
        raise NotImplementedError()

    def get_file_text(self, project_id, file_path):
        raise NotImplementedError()


class ManagerFile(IManagerFile):

    def get_project_path(self, path) -> List:
        return DealFile().get_dirs(path)

    def fetch_from_git(self, git_source, path):
        project = self._manager.query_project_by_repository(git_source + path)
        if project is None:
            project_path, project_name, encode_name = DealFile().git_fetch(git_source + path)
            self._manager.add_project(name=project_name, encode_name=encode_name, code_url=git_source + path)
            project = self._manager.query_project_by_encode_name(encode_name)
        elif project.encode_name is None or project.encode_name == '':
            _, _, encode_name = DealFile().git_fetch(git_source + path)
        else:
            if os.path.exists('./assets/projects/' + project.encode_name) is not True:
                _, _, encode_name = DealFile().git_fetch(git_source + path)
            else:
                pass
        return project

    def get_file_text(self, project, file_path):
        if not os.path.exists(os.getcwd() + os.path.join(self._project_path, project)):
            raise ProjectNotFound('Project Not Found')
        project_path = os.getcwd() + os.path.join(self._project_path, project, file_path)
        try:
            with open(project_path, 'r', encoding='utf-8') as f:
                to_front_file = f.read()
        except Exception:
            raise FileReadError('File Read Error')
        return str(to_front_file)
