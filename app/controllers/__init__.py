from flask import Flask
from app.controllers.ping import ping
from app.controllers.ctr_file import ctr_file
from app.controllers.ctr_scan import ctr_scan
from app.controllers.ctr_anti import ctr_anti
from app.controllers.ctr_entity import ctr_entity


def register_router(app: Flask):
    # ping
    app.register_blueprint(ping)
    # project
    app.register_blueprint(ctr_file)

    #
    app.register_blueprint(ctr_scan)

    #
    app.register_blueprint(ctr_anti)

    app.register_blueprint(ctr_entity)
