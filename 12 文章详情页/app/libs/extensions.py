from contextlib import contextmanager

from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_mail import Mail


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
csrf_protect = CSRFProtect()
mail = Mail()


def get_login_manager() -> LoginManager:
    """
    配置并返回 LoginManager 实例
    :return: LoginManager 实例
    """
    login_manager = LoginManager()

    @login_manager.user_loader
    def get_user(uid):
        """处理访问控制"""
        from app.models.admin import Admin
        return Admin.query.get(int(uid))

    login_manager.login_view = 'web.login'                # 登录视图的 endpoint
    login_manager.login_message = '无权访问此页面，请先登录'   # 重新向 Flash 信息
    login_manager.login_message_category = 'error'        # 重定向 Flask 信息分类

    return login_manager
