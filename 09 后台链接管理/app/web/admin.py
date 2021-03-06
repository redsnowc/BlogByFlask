import json

from flask import render_template, url_for, redirect, request, abort
from flask_login import login_required

from app.web import web
from app.forms.category import NewCategoryForm, EditCategoryForm
from app.forms.link import NewLinkForm, EditLinkForm
from app.models import Category, Link
from app.libs.extensions import db
from app.libs.helpers import get_form_error_items, check_ajax_request_data


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
        return redirect(url_for('web.manage_category'))

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
        js object example {modelName: 'Category', id: 1}
        :return 依据实际情况返回对应的 json 字符串
    """

    data = request.get_json()

    result = check_ajax_request_data(data, Category.__name__)
    if isinstance(result, str):
        return result

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

    result = check_ajax_request_data(form_data, Category.__name__)
    if isinstance(result, str):
        return result

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
    return redirect(url_for('web.manage_category'))


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
        return redirect(url_for('web.manage_link'))

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
        js object example {modelName: 'Link', id: 1}
        :return 依据实际情况返回对应的 json 字符串
    """

    data = request.get_json()

    result = check_ajax_request_data(data, Link.__name__)
    if isinstance(result, str):
        return result

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

    result = check_ajax_request_data(form_data, Link.__name__)
    if isinstance(result, str):
        return result

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
    return redirect(url_for('web.manage_link'))
