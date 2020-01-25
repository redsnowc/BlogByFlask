from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user

from app.web import web
from app.models import Post, Admin, Category, Comment
from app.forms.comment import CommentForm
from app.libs.extensions import db
from app.libs.helpers import get_form_error_items, is_safe_url
from app.libs.email import send_mail


@web.route('/')
def index():
    """首页视图"""
    admin = Admin.query.first()
    per_page = admin.post_per_page
    pagination = Post.query.filter_by(trash=False, published=True).order_by(
        Post.create_time.desc()).paginate(per_page=per_page)
    return render_template('blog/index.html', pagination=pagination)


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
    per_page = admin.post_per_page
    pagination = Post.query.with_parent(category).filter_by(trash=False, published=True).order_by(
        Post.create_time.desc()).paginate(per_page=per_page)
    return render_template('blog/category.html', category=category, pagination=pagination)


@web.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    """
    文章详情视图，该视图处理发表评论功能
    :param post_id: 文章 id
    """
    post = Post.query.filter_by(id=post_id, trash=False, published=True).first_or_404()
    reply_id = request.args.get('reply_id')
    admin = Admin.query.first()
    per_page = admin.comment_per_page
    admin_email = admin.email
    # 该文章下不在回收站中、已审核且不是回复其它评论的评论 Pagination 对象
    comment_pagination = Comment.query.with_parent(
        post).filter_by(trash=False, reviewed=True, replied_id=None).order_by(
        Comment.create_time.desc()).paginate(per_page=per_page)

    form = CommentForm(request.form)
    # 根据用户登录状态设置不同的字段数据
    if current_user.is_authenticated:
        form.author.data = admin.nickname
        from_admin = True
        reviewed = True
        flash_message = '评论已发布。'
    else:
        from_admin = False
        reviewed = False
        flash_message = '您的评论会尽快被审核。'

    if form.validate_on_submit():
        with db.auto_commit():
            comment = Comment()
            comment.set_attr(form.data)
            comment.from_admin = from_admin
            comment.reviewed = reviewed
            comment.post = post

            if reply_id:
                comment.replied = Comment.query.get_or_404(reply_id)

            db.session.add(comment)

        flash(flash_message)
        # 如果不是已登录用户，则发送邮件通知管理员审核
        if not current_user.is_authenticated:
            send_mail(
                [admin_email],
                '博客有新的评论需要审核',
                'email/new_comment.html',
                post=post
            )

        return redirect(url_for('web.post', post_id=post.id, _anchor="commentResponse"))

    fields_name, fields_errors = get_form_error_items(form)

    # 如果是回复评论且表单验证失败，则跳转至专门显示表单错误的页面
    if reply_id and form.errors:
        if is_safe_url(request.referrer):
            back_url = request.referrer
        else:
            back_url = url_for('web.post', post_id=post.id)
        return redirect(url_for('web.reply_error', fields_errors=','.join(fields_errors), back_url=back_url))

    return render_template('blog/post.html', post=post, comment_pagination=comment_pagination, form=form,
                           fields_errors=fields_errors, fields_name=fields_name)


@web.route('/reply-error/<fields_errors>/<path:back_url>')
def reply_error(fields_errors, back_url):
    """
    专门处理回复评论表单的错误显示
    :param fields_errors: 表单错误信息
    :param back_url: 返回 URL
    """
    return render_template('blog/reply_error.html', fields_errors=fields_errors.split(','), back_url=back_url)


@web.about('/about')
def about():
    pass
