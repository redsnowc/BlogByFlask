import click

from flask import Flask

from app.configs import configs
from app.libs.extensions import db, migrate
from app.models import Post, Category, post_category_middle, Comment, Admin, Link


def create_app(config: str = "development") -> Flask:
    """
    工厂函数
    :param config: 默认是 development 开发环境，可选的值有 test、production
    :return: Flask 核心对象 app
    """
    app = Flask(__name__)
    app.config.from_object(configs[config])
    register_extensions(app)
    register_cli(app)
    return app


def register_extensions(app: Flask):
    """
    注册第三方插件
    :param app: Flask 核心对象
    :return: None
    """
    db.init_app(app)
    migrate.init_app(app, db)


def register_cli(app: Flask):
    """
    注册命令行命令
    :param app:
    :return: None
    """
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='删除数据表并重建')
    def initdb(drop):
        """初始化数据库"""
        if drop:
            click.confirm('确定要删除所有数据表?', abort=True)
            db.drop_all()
            click.echo('数据表删除成功')
        db.create_all()
        # 初始化数据后在分类表中添加一条记录作为默认默认分类
        with db.auto_commit():
            category = Category()
            category.name = "未分类"
            category.show = False
            db.session.add(category)
        click.echo('数据表已成功创建')
