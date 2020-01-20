import json

from flask import render_template, request, url_for, abort, flash, current_app
from flask_login import login_required

from app.web import web
from app.forms.category import NewCategoryForm, EditCategoryForm
from app.forms.link import NewLinkForm, EditLinkForm
from app.models import Category, Link, Comment
from app.libs.extensions import db
from app.libs.helpers import get_form_error_items, check_ajax_request_data, redirect_back


@web.route('/admin')
@login_required
def admin_index():
    """后台首页视图"""
    return render_template('admin/admin_index.html')


@web.route('/admin/category', methods=['POST', 'GET'])
@login_required
def manage_category():
    """后台分类管理视图"""
    form = NewCategoryForm(request.form)

    if form.validate_on_submit():
        with db.auto_commit():
            category = Category()
            category.set_attr(form.data)
            db.session.add(category)
        return redirect_back()

    fields_names, fields_errors = get_form_error_items(form)
    return render_template('admin/manage_category.html', form=form,
                           fields_errors=fields_errors,
                           fields_names=fields_names)


@web.route('/admin/get-category', methods=['POST'])
@login_required
def get_category():
    """
        ajax 获取分类记录视图
        该视图仅能接受固定格式的 ajax 请求数据
        js object example {model: 'Category', id: 1}
        :return 依据实际情况返回对应的 json 字符串
    """

    data = request.get_json()

    result = check_ajax_request_data(data)
    if isinstance(result, str):
        return result

    if result.__class__.__name__ != 'Category':
        return json.dumps({'code': 0, 'msg': '指定查询模型与该查询不符'})

    successful_data = {'code': 1, 'data': {}}
    successful_data['data']['id'] = result.id
    successful_data['data']['name'] = result.name
    successful_data['data']['alias'] = result.alias
    successful_data['data']['show'] = result.show
    successful_data['data']['posts_count'] = len(result.posts)

    return json.dumps(successful_data)


@web.route('/admin/update-category', methods=['POST'])
@login_required
def update_category():
    """
        ajax 更新分类记录视图
        该视图接收前端表单数据的序列化字符串
        :return 依据实际情况返回对应的 json 字符串
    """
    form = EditCategoryForm()
    form_data = request.form

    result = check_ajax_request_data(form_data)

    if isinstance(result, str):
        return result

    if result.__class__.__name__ != 'Category':
        return json.dumps({'code': 0, 'msg': '指定查询模型与该查询不符'})

    if form.validate_on_submit():
        with db.auto_commit():
            result.set_attr(form.data)
            db.session.add(result)
        return json.dumps({'code': 1})

    return json.dumps({'code': 2, 'msg': form.errors})


@web.route('/admin/delete-category/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    """删除分类视图"""
    if category_id == 1:
        abort(404)

    category = Category.query.get_or_404(category_id)
    category.delete()
    return redirect_back()


@web.route('/admin/link', methods=['POST', 'GET'])
@login_required
def manage_link():
    """后台链接管理管理视图"""
    form = NewLinkForm(request.form)

    if form.validate_on_submit():
        with db.auto_commit():
            link = Link()
            link.set_attr(form.data)
            db.session.add(link)
        return redirect_back()

    fields_names, fields_errors = get_form_error_items(form)
    return render_template('admin/manage_link.html', form=form,
                           fields_errors=fields_errors,
                           fields_names=fields_names)


@web.route('/admin/get-link', methods=['POST'])
@login_required
def get_link():
    """
        ajax 获取链接记录视图
        该视图仅能接受固定格式的 ajax 请求数据
        js object example {model: 'Link', id: 1}
        :return 依据实际情况返回对应的 json 字符串
    """

    data = request.get_json()

    result = check_ajax_request_data(data)
    if isinstance(result, str):
        return result

    if result.__class__.__name__ != 'Link':
        return json.dumps({'code': 0, 'msg': '指定查询模型与该查询不符'})

    successful_data = {'code': 1, 'data': {}}
    successful_data['data']['id'] = result.id
    successful_data['data']['name'] = result.name
    successful_data['data']['url'] = result.url
    successful_data['data']['tag'] = result.tag

    return json.dumps(successful_data)


@web.route('/admin/update-link', methods=['POST'])
@login_required
def update_link():
    """
        ajax 更新链接记录视图
        该视图接收前端表单数据的序列化字符串
        :return 依据实际情况返回对应的 json 字符串
    """
    form = EditLinkForm()
    form_data = request.form
    print(form_data)

    result = check_ajax_request_data(form_data)

    if isinstance(result, str):
        return result

    if result.__class__.__name__ != 'Link':
        return json.dumps({'code': 0, 'msg': '指定查询模型与该查询不符'})

    if form.validate_on_submit():
        with db.auto_commit():
            result.set_attr(form.data)
            db.session.add(result)
        return json.dumps({'code': 1})

    return json.dumps({'code': 2, 'msg': form.errors})


@web.route('/admin/delete-link/<int:link_id>', methods=['POST'])
@login_required
def delete_link(link_id):
    """删除链接视图"""
    link = Link.query.get_or_404(link_id)
    with db.auto_commit():
        db.session.delete(link)
    return redirect_back()


@web.route('/admin/comment/<any(all, unreviewed, reviewed, trash, mine):status>')
@web.route('/admin/comment', defaults={'status': 'all'})
@login_required
def manage_comment(status):
    """
    后台评论管理视图
    直接访问 /admin/comment 显示全部评论
    :param status: 筛选评论 status = all or unreviewed or reviewed or trash or mine
    """
    per_page = current_app.config['ADMIN_PER_PAGE']

    # 评论的五种不同 query 对象字典
    comments_query_dict = {
        'all': Comment.query.filter_by(trash=False),
        'unreviewed': Comment.query.filter_by(reviewed=False, trash=False),
        'reviewed': Comment.query.filter_by(reviewed=True, trash=False, from_admin=False),
        'trash': Comment.query.filter_by(trash=True),
        'mine': Comment.query.filter_by(from_admin=True)
    }
    pagination = comments_query_dict.get(status).order_by(Comment.create_time.desc()).paginate(per_page=per_page)

    # 五种评论所对应的 URL 以及总数
    comments_info_dict = {
        '全部': [url_for('web.manage_comment', status='all'), comments_query_dict.get('all').count()],
        '我的': [url_for('web.manage_comment', status='mine'), comments_query_dict.get('mine').count()],
        '待审核': [url_for('web.manage_comment', status='unreviewed'), comments_query_dict.get('unreviewed').count()],
        '已审核': [url_for('web.manage_comment', status='reviewed'), comments_query_dict.get('reviewed').count()],
        '回收站': [url_for('web.manage_comment', status='trash'), comments_query_dict.get('trash').count()]
    }

    return render_template('admin/manage_comment.html', pagination=pagination,
                           comments_info_dict=comments_info_dict, status=status)


@web.route('/admin/review-comment/<int:comment_id>/<any(do, undo):action>', methods=['POST'])
@login_required
def review_comment(comment_id, action):
    """
    审核评论视图，可执行审核以及撤销审核操作
    :param comment_id: 评论 id
    :param action: 执行方式 action = do or undo
    """
    comment = Comment.query.get_or_404(comment_id)

    if action == 'do':
        comment.reviewed = True
        flash_message = '评论审核成功'
    else:
        comment.reviewed = False
        flash_message = '撤销评论审核成功'

    with db.auto_commit():
        db.session.add(comment)
    flash(flash_message, 'success')
    return redirect_back(default_endpoint='web.manage_comment')


@web.route('/admin/trash-comment/<int:comment_id>/<any(do, undo):action>', methods=['POST'])
@login_required
def trash_comment(comment_id, action):
    """
    移动评论至回收站视图，软删除
    :param comment_id: 评论 id
    :param action: 执行方式 action = do or undo
    """
    comment = Comment.query.get_or_404(comment_id)

    if action == 'do':
        comment.trash = True
        flash_message = '评论已被移入回收站'
    else:
        comment.trash = False
        flash_message = '评论已被移出回收站'

    with db.auto_commit():
        db.session.add(comment)
    flash(flash_message, 'success')
    return redirect_back(default_endpoint='web.manage_comment')


@web.route('/admin/delete-comment/<int:comment_id>', defaults={'action': 'one'}, methods=['POST'])
@web.route('/admin/delete-comment/<any(all, one):action>', defaults={'comment_id': None}, methods=['POST'])
@login_required
def delete_comment(comment_id, action):
    """
    删除评论视图
    :param comment_id: 评论 id
    :param action: 执行操作 action = all 删除全部回收站评论
    """
    if action == 'all':
        with db.auto_commit():
            for comment in Comment.query.filter_by(trash=True).all():
                db.session.delete(comment)
        return redirect_back(default_endpoint='web.manage_comment')

    comment = Comment.query.get_or_404(comment_id)
    with db.auto_commit():
        db.session.delete(comment)
    flash('评论已被删除', 'success')
    return redirect_back(default_endpoint='web.manage_comment')
