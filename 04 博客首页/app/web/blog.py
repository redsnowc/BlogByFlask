from flask import render_template

from app.web import web
from app.models import Post, Admin


@web.route('/')
def index():
    """首页视图"""
    admin = Admin.query.first()
    per_page = admin.per_page
    pagination = Post.query.order_by(
        Post.create_time.desc()).paginate(per_page=per_page)
    return render_template('blog/index.html', pagination=pagination)


@web.route('/test')
def test():
    pagination = Post.query.order_by(
        Post.create_time.desc()).paginate(per_page=10)
    return render_template('1.html', pagination=pagination)
