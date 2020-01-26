import click
import os

from flask import Flask
from datetime import datetime

from app.configs import configs
from app.libs.extensions import db, migrate, get_login_manager, csrf_protect, mail, whooshee
from app.models import Post, Category, post_category_middle, Comment, Admin, Link
from app.libs.fake_data import FakeData
from app.libs.custom_filters import switch_link_tag, get_search_part


def create_app(config: str = 'development') -> Flask:
    """
    工厂函数
    :param config: 默认是 development 开发环境，可选的值有 test、production
    :return: Flask 核心对象 app
    """
    app = Flask(__name__)
    app.config.from_object(configs[config])
    register_extensions(app)
    register_blueprints(app)
    register_cli(app)
    register_template_context(app)
    add_template_filters(app)
    return app


def register_extensions(app: Flask):
    """
    注册第三方插件
    :param app: Flask 核心对象
    :return: None
    """
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager = get_login_manager()
    login_manager.init_app(app)
    csrf_protect.init_app(app)
    mail.init_app(app)
    whooshee.init_app(app)


def register_blueprints(app: Flask):
    """
    注册蓝图
    :param app: Flask 核心对象
    :return: None
    """
    from app.web import web
    app.register_blueprint(web)


def register_cli(app: Flask):
    """
    注册命令行命令
    :param app: Flask 核心对象
    :return: None
    """
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='删除数据表并重建')
    @click.option('--_init', is_flag=True, help='删除并重建数据表 (内部调用)')
    def initdb(drop, _init):
        """初始化数据库"""
        if drop:
            click.confirm('确定要删除所有数据表？', abort=True)
            db.drop_all()
            click.echo('数据表删除成功')

        if _init:
            db.drop_all()
            click.echo('数据表删除成功')

        db.create_all()
        # 初始化数据后在分类表中添加一条记录作为默认默认分类
        with db.auto_commit():
            category = Category()
            category.name = '未分类'
            category.alias = 'default'
            category.show = False
            db.session.add(category)
        click.echo('数据表已成功创建')

    @app.cli.command()
    @click.option('--category', type=int, help='要生成的博客分类数量，默认 9')
    @click.option('--post', type=int, help='要生成的博客文章数量，默认 50')
    @click.option('--comment', type=int, help='要生成的评论数量，默认 1000')
    def fake(category, post, comment):
        """生成虚拟数据"""
        click.confirm('该操作会删除现有数据表并重建，确定吗？', abort=True)
        os.system('flask initdb --_init')
        click.echo('数据表已重建，开始生成虚拟数据...')

        click.echo('生成管理员与博客设置数据中...')
        FakeData.fake_admin()
        click.echo('Done!')

        click.echo('生成博客分类数据中...')
        FakeData.fake_categories(category) if category else FakeData.fake_categories()
        click.echo('Done!')

        click.echo('生成博客文章数据中...')
        FakeData.fake_posts(post) if post else FakeData.fake_posts()
        click.echo('Done!')

        click.echo('生成博客评论数据中...')
        FakeData.fake_comments(comment) if comment else FakeData.fake_comments()
        click.echo('Done!')

        click.echo('生成博客链接数据中...')
        FakeData.fake_links()
        click.echo('Done!')

        click.echo('数据已全部生成完毕！')

    @app.cli.command()
    @click.option('--username', prompt='请输入管理员用户名', help='管理员用户名')
    @click.password_option(prompt='请输入管理员密码', help='管理员密码')
    @click.option('--email', prompt='请输入管理员邮箱', help='管理员邮箱')
    def admin(username, password, email):
        """设置管理员用户名、密码以及邮箱"""

        # 处理 MySQL 错误
        try:
            admin = Admin.query.first()
        except Exception as e:
            if '1146' in str(e.orig):
                click.echo('数据表不存在，请执行 `flask initdb` 创建数据表')
            else:
                print(e)
                click.echo('请检查错误信息')
            return

        with db.auto_commit():
            if admin:
                click.echo('更新管理员账户信息...')
                admin.username = username
                admin.password = password
                admin.email = email
            else:
                click.echo('创建管理员账户中...')
                admin = Admin()
                admin.username = username
                admin.password = password
                admin.email = email
                admin.blog_title = '临时博客名'
                admin.blog_subtitle = '临时博客副标题'
                admin.blog_about = '临时博客关于'
                admin.nickname = '临时昵称'
            db.session.add(admin)
            click.echo('Done.')


def register_template_context(app: Flask):
    """
    注册模板全局变量
    :param app: Flask 核心对象
    :return dict: 传递给全局模板的数据
    """
    @app.context_processor
    def generate_template_context():
        admin = Admin.query.first()
        categories = Category.query.all()
        links = Link.query.all()
        current_year = datetime.now().year
        return {"admin": admin, "categories": categories, "links": links, "current_year": current_year}


def add_template_filters(app: Flask):
    """
    注册自定义模板验证器
    :param app: Flask 核心对象
    :return: None
    """
    app.add_template_filter(switch_link_tag)
    app.add_template_filter(get_search_part)
