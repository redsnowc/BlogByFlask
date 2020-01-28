import click
import os

from flask import Flask, render_template, url_for, request
from datetime import datetime

from sqlalchemy import func
from flask_wtf.csrf import CSRFError

from app.configs import configs
from app.libs.extensions import db, migrate, get_login_manager, csrf_protect, mail, whooshee
from app.models import Post, Category, post_category_middle, Comment, Admin, Link
from app.libs.fake_data import FakeData
from app.libs.custom_filters import switch_link_tag, get_search_part
from app.libs.helpers import is_safe_url


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
    register_error_templates(app)
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
        unreviewed_comment_count = Comment.query.filter_by(reviewed=False, trash=False).count()
        admin_url_info = [
            {'总览': 'web.admin_index'},
            {'文章管理': 'web.manage_post'},
            {'评论管理': 'web.manage_comment'},
            {'分类管理': 'web.manage_category'},
            {'链接管理': 'web.manage_link'},
            {'博客设置': 'web.blog_setting'}
        ]
        return {"admin": admin, "categories": categories, "links": links, "current_year": current_year,
                "unreviewed_comment_count": unreviewed_comment_count, "admin_url_info": admin_url_info}


def add_template_filters(app: Flask):
    """
    注册自定义模板验证器
    :param app: Flask 核心对象
    :return: None
    """
    app.add_template_filter(switch_link_tag)
    app.add_template_filter(get_search_part)


def register_error_templates(app: Flask):
    """
    注册 HTTP 请求错误时页面显示模板
    :param app: Flask 核心对象
    :return: None
    """
    @app.errorhandler(404)
    def not_found(e):
        """处理 404 错误"""
        error_info = {
            'head_title': '找不到您要访问的页面',
            'page_title': '找不到您要访问的页面...',
            'description': f'抱歉，您要访问的页面不存在，您可以<a href="{url_for("web.index")}">返回首页</a>，或者查看以下内容：'
        }
        posts = Post.query.filter_by(published=True, trash=False).order_by(func.rand()).limit(5)
        return render_template('error/error.html', posts=posts, error_info=error_info), 404

    @app.errorhandler(500)
    def server_error(e):
        """处理 500 错误"""
        error_info = {
            'head_title': '似乎有什么意外出现了',
            'page_title': '似乎有什么意外出现了...',
            'description': f'抱歉，有不可名状的错误突然出现，您可以<a href="{url_for("web.index")}">返回首页</a>，或者查看以下内容：'
        }
        posts = Post.query.filter_by(published=True, trash=False).order_by(func.rand()).limit(5)
        return render_template('error/error.html', posts=posts, error_info=error_info), 500

    @app.errorhandler(CSRFError)
    def csrf_error(e):
        """处理 csrf_token 失效错误"""
        # 因为 csrf 的错误普遍出现在填写表单中，所以为了引导用户回到上一页，这里有必要进行判断
        if is_safe_url(request.referrer):
            back_url = request.referrer
        else:
            back_url = url_for('web.index')
        error_info = {
            'head_title': '您的页面会话已过期',
            'page_title': '您的页面会话已过期',
            'description': f'抱歉，可能您在页面停留过久，导致会话已过期，您可以<a href="{back_url}">返回上一页</a>重新执行操作，或者查看以下内容：'
        }
        posts = Post.query.filter_by(published=True, trash=False).order_by(func.rand()).limit(5)
        return render_template('error/error.html', posts=posts, error_info=error_info), 500
