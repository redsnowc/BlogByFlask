from contextlib import contextmanager

from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy
from flask_migrate import Migrate


class SQLALCHEMY(_SQLAlchemy):
    """
    复写 SQLAlchemy 增加一个方法，专门处理数据库的写入出错的回滚操作
    """
    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e


db = SQLALCHEMY()
migrate = Migrate()
