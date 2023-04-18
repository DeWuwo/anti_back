import os
from pathlib import Path
from flask import Blueprint, request, current_app
from flask.views import MethodView
from app.utils import Warp, DealFile
from sqlalchemy.exc import SQLAlchemyError
from app.models.errors import NetWorkError, EnreRunError
from app.models.manager_files import ManagerFile
from app.models.manager_coverage import ManagerCoverage
from app.models.manager_usage import ManagerUsage
from app.models.manager_pattern import ManagerPattern
from algorithm.pratice import Tool, Recommend

git_fetch = Blueprint('git_fetch', __name__, url_prefix='/project')


class Fetch(MethodView):
    def post(self):
        git_source = request.json.get('git_source')
        git_url = request.json.get('git_url')
        features = request.json.get('features')
        top = request.json.get('top')
        if git_url is None or git_url == '':
            current_app.logger.error('项目url不能为空', str({'git_url': git_url}))
            return Warp.fail_warp(301, '项目名url不能为空')

        try:
            project = ManagerFile().fetch_from_git(git_source, git_url)
            coverage = ManagerCoverage().get_coverage(project, '')
            usage = ManagerUsage().get_usage(project, '')
            pattern_count, pattern_info = ManagerPattern().get_pattern(project, '')
            Tool().use_enre(project.encode_name)
            recommend_files = Recommend().handle_get_recommend(project_name=project.encode_name,
                                                               features=features, top=top)
            return Warp.success_warp(
                {'cov': coverage, 'usage': usage, 'pattern': pattern_count, 'pattern_info': pattern_info,
                 'recommend': recommend_files})
        except NetWorkError as e:
            current_app.logger.error(e)
            return Warp.fail_warp(503, '服务器网络错误')
        except EnreRunError as e:
            current_app.logger.error(e)
            return Warp.fail_warp(503, '依赖抽取错误')
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            return Warp.fail_warp(501)


fetch_view = Fetch.as_view('git_fetch')

git_fetch.add_url_rule('/fetch', view_func=fetch_view, methods=['POST'])
