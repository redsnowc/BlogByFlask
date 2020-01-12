from flask import render_template

from app.web import web
from app.models import Post, Admin, Category


@web.route('/')
def index():
    """首页视图"""
    admin = Admin.query.first()
    per_page = admin.per_page
    pagination = Post.query.order_by(
        Post.create_time.desc()).paginate(per_page=per_page)
    return render_template('blog/_index.html', pagination=pagination)


@web.route('/category/<name_or_alias>')
def category(name_or_alias):
    """
    分类视图
    :param name_or_alias: 分类的别名或者名称
    """
    # 将 name_or_alias 的值作为别名去查询分类记录
    category = Category.query.filter(Category.alias == name_or_alias).first()

    # 如果别名找不到，则将 name_or_alias 作为分类名称去查询分类记录
    # 如果还是没有则直接抛出 404 错误
    if not category:
        category = Category.query.filter(Category.name == name_or_alias).first_or_404()

    admin = Admin.query.first()
    per_page = admin.per_page
    pagination = Post.query.with_parent(category).order_by(
        Post.create_time.desc()).paginate(per_page=per_page)
    return render_template('blog/_category.html', category=category, pagination=pagination)
