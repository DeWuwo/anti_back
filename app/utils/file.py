import os
import stat
import shutil
import git
from app.utils import MD5
import subprocess
from subprocess import CalledProcessError
from app.models.errors import DirAnalyzeError, GitFetchError, ProjectNotFound, GitRepoNotExist, CommandRunError, \
    GitFetchingError


class DealFile:
    base_path = "./assets/projects/"

    @classmethod
    def allowed_file(cls, filename: str):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'py'}

    @classmethod
    def rename(cls, filename: str) -> str:
        return MD5.encode_file(filename) + '.jpg'

    @classmethod
    def save_file(cls, path, py_f):
        paths = path.rsplit('/', 1)
        file_message = py_f.filename.rsplit('/', 1)
        file_name = file_message[1] if len(file_message) == 2 else file_message[0]
        if len(paths) == 2:
            if paths[1] == file_name:
                file_path = paths[0] + '/'
            else:
                file_path = path
        else:
            if paths[0] == file_name:
                file_path = ''
            else:
                file_path = path
        proj_path = cls.base_path + file_path
        if os.path.exists(proj_path) is not True:
            os.makedirs(proj_path)
        py_f.save(proj_path + file_name)

    @classmethod
    def get_dirs(cls, file_path):
        proj_path = cls.base_path + file_path
        if os.path.exists(os.path.join(proj_path)) is not True:
            raise ProjectNotFound('Project Not Found')
        try:
            for _, dirs, files in os.walk(proj_path, topdown=True):
                return dirs, files
        except Exception:
            raise DirAnalyzeError('DirAnalyzeError')
        # dir_list = []
        # file_list = []
        # for item in dirs:
        #     temp = os.path.join(proj_path, item)
        #     if os.path.isdir(temp):
        #         dir_list.append(item)
        #     else:
        #         file_list.append(item)

    @classmethod
    def git_fetch(cls, repo_url):
        git_target, git_url = cls.git_url_deal(repo_url)
        project_repo = git_url.strip('/').split('/', 1)
        project_master = project_repo[0]
        project_name = project_repo[1]
        encode_project_name = project_master + '-' + project_name
        fetch_command = 'cd ' + cls.base_path + ' && git clone ' + git_target + git_url + ' ' + encode_project_name
        project_path = cls.base_path + encode_project_name
        if os.path.exists(project_path):
            dirs, files = cls.get_dirs(encode_project_name)
            if len(dirs) + len(files) > 1:
                return project_path, project_name, encode_project_name
            else:
                shutil.rmtree(project_path, onerror=cls.rm_read_only)
        try:
            res = cls.command_run(fetch_command)
        except Exception:
            raise GitFetchError('获取项目失败')
        if res:
            return project_path, project_name, encode_project_name
        else:
            shutil.rmtree(project_path)
            raise GitFetchError('获取项目失败')

    @classmethod
    def clone_project_from_git(cls, repo_url, local_url, node):
        new_repo = git.Repo.clone_from(repo_url, os.path.join(cls.base_path, local_url))
        new_repo.git.checkout(node)

    @classmethod
    def git_url_deal(cls, git_url: str):
        # "https://github.com.cnpmjs.org/"
        if git_url.find("github.com/") != -1:
            return "https://github.com.cnpmjs.org/", git_url.split("github.com/", 1)[1]
        elif git_url.find("gitee.com") != -1:
            return "https://gitee.com/", git_url.split("gitee.com/", 1)[1]
        else:
            raise GitRepoNotExist('Repo not Exist')

    @classmethod
    def command_run(cls, command: str):
        try:
            ret = subprocess.run(command, shell=True, check=True, encoding="utf-8")
            return ret.returncode == 0
        except CalledProcessError:
            raise CommandRunError

    @classmethod
    def rm_read_only(cls, fn, tmp, info):
        try:
            os.chmod(tmp, stat.S_IWRITE)
            fn(tmp)
        except PermissionError:
            raise GitFetchingError
