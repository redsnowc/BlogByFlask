from flask import Flask

from app.configs import configs
from app.libs.extensions import db, migrate
from app.models import Post, Category, post_category_middle, Comment, Admin, Link


def create_app(config="development"):
    """
    工厂函数
    :param config: 默认是 development 开发环境，可选的值有 test、production
    :return: Flask 核心对象 app
    """
    app = Flask(__name__)
    app.config.from_object(configs[config])
    register_extensions(app)
    return app


def register_extensions(app):
    """
    注册第三方插件
    :param app: Flask 核心对象
    :return: None
    """
    db.init_app(app)
    migrate.init_app(app, db)

