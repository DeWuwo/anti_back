from flask import current_app, Blueprint, request
from flask.views import MethodView
from arango import ArangoError
from app.models.errors import ProjectNotFound, ProjectHasExist
from app.utils import Warp
from app.models.manager_entity import ManagerEntity

ctr_entity = Blueprint('ctr_entity', __name__)


class CtrEntity(MethodView):
    def get(self, entity_id):
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
        data = request.json
        scan_id = data.get('scan_id')

        try:
            res = ManagerEntity(scan_id=scan_id, page=page, limit=limit).get_entity_by_id(entity_id)
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
            ManagerEntity().add_entity(native, extensive)
            return Warp.success_warp('项目上传成功')
        except ArangoError as e:
            current_app.logger.error(e)
            return Warp.fail_warp(501)
        except ProjectHasExist as e:
            current_app.logger.error(e)
            return Warp.fail_warp(206)


entity_view = CtrEntity.as_view('ctr_entity')
ctr_entity.add_url_rule('/entity', view_func=entity_view, methods=['GET'])
ctr_entity.add_url_rule('/entity', view_func=entity_view, methods=['POST'])
ctr_entity.add_url_rule('/entity/<int:entity_id>', view_func=entity_view, methods=['GET'])
