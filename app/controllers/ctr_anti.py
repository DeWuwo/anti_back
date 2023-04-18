from flask import current_app, Blueprint, request
from flask.views import MethodView
from arango import ArangoError
from app.models.errors import ProjectNotFound, ProjectHasExist
from app.utils import Warp
from app.models.manager_anti import ManagerAnti

ctr_anti = Blueprint('ctr_anti', __name__)


class CtrAnti(MethodView):
    def get(self, anti_id):
        args = request.args
        try:
            current_app.logger.debug(args.get('limit'))
            limit = int(args.get('limit'))
            current_app.logger.debug(args.get('page'))
            page = int(args.get('page'))
        except (TypeError, ValueError):
            limit = 10
            page = 0
        data = request.json
        scan_id = data.get('scan_id')
        module = data.get('module')
        file_path = data.get('file_path')
        if anti_id is not None:
            try:
                res = ManagerAnti(page=page, limit=limit).get_anti_by_id(scan_id, anti_id)
                return Warp.success_warp(res.__dict__)
            except ArangoError as e:
                current_app.logger.error(e)
                return Warp.fail_warp(501)
            except ProjectNotFound as e:
                current_app.logger.error(e)
                return Warp.fail_warp(403, '项目不存在')
        elif file_path != '':
            try:
                res = ManagerAnti(page=page, limit=limit).get_antis_by_file(scan_id, file_path)
                return Warp.success_warp(res.__dict__)
            except ArangoError as e:
                current_app.logger.error(e)
                return Warp.fail_warp(501)
            except ProjectNotFound as e:
                current_app.logger.error(e)
                return Warp.fail_warp(403, '项目不存在')
        elif module == "true":
            try:
                res = ManagerAnti(page=page, limit=limit).group_antis_by_file(scan_id)
                return Warp.success_warp(res.__dict__)
            except ArangoError as e:
                current_app.logger.error(e)
                return Warp.fail_warp(501)
            except ProjectNotFound as e:
                current_app.logger.error(e)
                return Warp.fail_warp(403, '项目不存在')
        else:
            try:
                res = ManagerAnti(page=page, limit=limit).get_antis_by_style(scan_id)
                return Warp.success_warp(res.__dict__)
            except ArangoError as e:
                current_app.logger.error(e)
                return Warp.fail_warp(501)
            except ProjectNotFound as e:
                current_app.logger.error(e)
                return Warp.fail_warp(403, '项目不存在')

    def post(self):
        data = request.json
        native = data.get('native')
        native_node = data.get('native_node')
        extensive = data.get('extensive')
        extensive_node = data.get('extensive_node')
        extensive_url = data.get('extensive_url')
        if native is None or native == '' or extensive is None or extensive is None:
            current_app.logger.error('原生版本不能为空', str({'native': native}))
            return Warp.fail_warp(301, '原生版本不能为空')
        try:
            ManagerAnti().start_new_scan(native, extensive, native_node, extensive_node, extensive_url)
            return Warp.success_warp('项目上传成功')
        except ArangoError as e:
            current_app.logger.error(e)
            return Warp.fail_warp(501)
        except ProjectHasExist as e:
            current_app.logger.error(e)
            return Warp.fail_warp(206)


anti_view = CtrAnti.as_view('ctr_anti')
ctr_anti.add_url_rule('/anti', defaults={'anti_id': None}, view_func=anti_view, methods=['GET'])
ctr_anti.add_url_rule('/anti/<int:anti_id>', view_func=anti_view, methods=['GET'])
ctr_anti.add_url_rule('/anti', view_func=anti_view, methods=['POST'])
