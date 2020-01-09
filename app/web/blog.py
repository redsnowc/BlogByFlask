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
    return render_template('blog/index.html', pagination=pagination)


@web.route('/category/<name_or_alias>')
def category(name_or_alias):
    category = Category.query.filter(Category.alias == name_or_alias).first()

    if not category:
        category = Category.query.filter(Category.name == name_or_alias).first_or_404()

    admin = Admin.query.first()
    per_page = admin.per_page
    pagination = Post.query.with_parent(category).order_by(
        Post.create_time.desc()).paginate(per_page=per_page)
    return render_template('blog/category.html', category=category, pagination=pagination)
