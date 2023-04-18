from flask import current_app, Blueprint, request
from flask.views import MethodView
from arango import ArangoError
from app.models.errors import ProjectNotFound, ProjectHasExist
from app.utils import Warp
from app.models.manager_scan import ManagerScan

ctr_scan = Blueprint('ctr_scan', __name__)


class CtrScan(MethodView):
    def get(self):
        args = request.args
        try:
            current_app.logger.debug(args.get('limit'))
            limit = int(args.get('limit'))
        except (TypeError, ValueError):
            limit = 10
        try:
            current_app.logger.debug(args.get('page'))
            page = int(args.get('page'))
        except (TypeError, ValueError):
            page = 0
        try:
            res = ManagerScan(page=page, limit=limit).get_all_scan()
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
        extensive = data.get('extensive')
        if native is None or native == '' or extensive is None or extensive is None:
            current_app.logger.error('原生版本不能为空', str({'native': native}))
            return Warp.fail_warp(301, '原生版本不能为空')
        try:
            ManagerScan().add_scan(native, extensive)
            return Warp.success_warp('项目上传成功')
        except ArangoError as e:
            current_app.logger.error(e)
            return Warp.fail_warp(501)
        except ProjectHasExist as e:
            current_app.logger.error(e)
            return Warp.fail_warp(206)


scan_view = CtrScan.as_view('ctr_scan')
ctr_scan.add_url_rule('/scan', view_func=scan_view, methods=['GET'])
ctr_scan.add_url_rule('/scan', view_func=scan_view, methods=['POST'])
ctr_scan.add_url_rule('/scan/<int:project_id>', view_func=scan_view, methods=['DELETE'])
