from flask import Flask
from flask_arango_orm import ArangoORM
import os

arango = ArangoORM()


def connect_db(app: Flask):
    try:
        arango.init_app(app)
        app.config['db'] = arango
        app.logger.info('成功连接数据库')
    except BaseException as e:
        app.logger.error('连接数据库失败', e)


def session_commit():
    pass
    # try:
    #     db.session.commit()
    # except SQLAlchemyError as e:
    #     db.session.rollback()
    #     raise e


def export_db():
    try:
        path = 'E:\\dump'
        ip = "127.0.0.1"
        port = "8529"
        username = "root"
        passwd = "753951"
        database = "anti_pattern"

        cmd = "arangodump --server.endpoint tcp://%s:%s --server.username %s --server.password %s --server.database %s --output-directory \"%s\"" % (
            ip, port, username, passwd, database, path)

        os.system(cmd)
    except Exception as e:
        pass


if __name__ == '__main__':
    export_db()
