import os
import json

from flask import render_template, request, url_for, redirect, abort, flash, current_app, send_from_directory
from flask_login import login_required

from app.web import web
from app.forms.category import NewCategoryForm, EditCategoryForm
from app.forms.link import NewLinkForm, EditLinkForm
from app.forms.post import PostForm
from app.models import Category, Link, Comment, Post
from app.libs.extensions import db, csrf_protect
from app.libs.helpers import get_form_error_items, check_ajax_request_data, redirect_back, allowed_file, \
    avoided_file_duplication, remove_html_tag


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
    return redirect_back()


@web.route('/admin/trash-record/<any(Comment, Post):model_name>/<int:record_id>/<any(do, undo):action>',
           methods=['POST'])
@login_required
def trash_record(model_name, record_id, action):
    """
    移动评论或文章至回收站视图，软删除
    :param model_name: 数据表模型名称，model_name = Comment or Post
    :param record_id: 记录 id
    :param action: 执行方式 action = do or undo
    """
    model = current_app.config['MODELS'].get(model_name)
    record = model.query.get_or_404(record_id)

    if action == 'do':
        record.trash = True
        flash_message = '评论已被移入回收站' if model_name == 'Comment' else '文章已被移入回收站'
    else:
        record.trash = False
        flash_message = '评论已被移出回收站' if model_name == 'Comment' else '文章已被移出回收站'

    with db.auto_commit():
        db.session.add(record)
    flash(flash_message, 'success')
    return redirect_back()


@web.route('/admin/delete-record/<any(Comment, Post):model_name>/<int:record_id>', defaults={'action': 'one'},
           methods=['POST'])
@web.route('/admin/delete-record/<any(Comment, Post):model_name>/<any(all, one):action>', defaults={'record_id': None},
           methods=['POST'])
@login_required
def delete_record(model_name, record_id, action):
    """
    删除文章或评论视图
    :param model_name: 数据表模型名称，model_name = Comment or Post
    :param record_id: 记录 id
    :param action: 执行操作 action = all 删除全部回收站评论
    """
    model = current_app.config['MODELS'].get(model_name)
    if action == 'all':
        with db.auto_commit():
            for record in model.query.filter_by(trash=True).all():
                db.session.delete(record)
        flash('回收站已清空', 'success')
        return redirect_back(default_endpoint='web.manage_comment')

    record = model.query.get_or_404(record_id)
    with db.auto_commit():
        db.session.delete(record)
    flash_message = '评论已删除' if model_name == 'Comment' else '文章已删除'
    flash(flash_message, 'success')
    return redirect_back()


@web.route('/admin/post/<any(all, draft, trash):status>')
@web.route('/admin/post', defaults={'status': 'all'})
@login_required
def manage_post(status):
    """
    后台文章管理视图
    后台直接访问 /admin/post 显示全部文章
    :param status: status 筛选文章 status = all or draft or trash
    """
    per_page = current_app.config['ADMIN_PER_PAGE']

    # 三种不同文章状态的 query 对象
    posts_query_dict = {
        'all': Post.query.filter_by(trash=False),
        'draft': Post.query.filter_by(published=False),
        'trash': Post.query.filter_by(trash=True)
    }
    pagination = posts_query_dict.get(status).order_by(Post.create_time.desc()).paginate(per_page=per_page)

    # 三种类型文章对应的 URL 以及总数
    posts_info_dict = {
        '全部': [url_for('web.manage_post', status='all'), posts_query_dict.get('all').count()],
        '草稿': [url_for('web.manage_post', status='draft'), posts_query_dict.get('draft').count()],
        '回收站': [url_for('web.manage_post', status='trash'), posts_query_dict.get('trash').count()],
    }

    return render_template('admin/manage_post.html', pagination=pagination,
                           posts_info_dict=posts_info_dict, status=status)


@web.route('/admin/close-comment/<int:post_id>/<any(do, undo):action>', methods=['POST'])
@login_required
def close_comment(post_id, action):
    """
    关闭文章评论视图
    :param post_id: 文章 id
    :param action: 执行操作，action = do or undo
    """
    post = Post.query.get_or_404(post_id)
    if action == 'do':
        post.can_comment = False
        flash_message = f'文章 "{post.title}" 评论功能已关闭'
    else:
        post.can_comment = True
        flash_message = f'文章 "{post.title}" 评论功能已开启'

    with db.auto_commit():
        db.session.add(post)
        flash(flash_message, 'success')
    return redirect_back()


@web.route('/admin/new-post', methods=['POST', 'GET'])
@login_required
def new_post():
    """新建文章视图"""
    form = PostForm(request.form)
    if form.validate_on_submit():

        form.content.data = request.form['markdownEditor-html-code']
        form.categories.data = [Category.query.get(category_id) for category_id in form.categories.data]

        if not form.description.data:
            form.description.data = remove_html_tag(form.content.data)[0:150]

        if form.publish.data:
            with db.auto_commit():
                post = Post()
                post.set_attr(form.data)
                db.session.add(post)
            flash('文章已发布', 'success')

        if form.save.data:
            with db.auto_commit():
                post = Post()
                post.set_attr(form.data)
                post.published = False
                db.session.add(post)
            flash('文章已保存为草稿', 'success')

        return redirect(url_for('web.manage_post'))

    return render_template('admin/post_editor.html', form=form)


@web.route('/admin/edit-post/<int:post_id>', methods=['POST', 'GET'])
@login_required
def edit_post(post_id):
    """
    编辑文章视图
    :param post_id: 文章 id
    """
    post = Post.query.get_or_404(post_id)
    form = PostForm(request.form)

    if form.validate_on_submit():
        form.content.data = request.form['markdownEditor-html-code']
        form.categories.data = [Category.query.get(category_id) for category_id in form.categories.data]

        if not form.description.data:
            form.description.data = remove_html_tag(form.content.data)[0:150]

        if form.publish.data:
            with db.auto_commit():
                post.set_attr(form.data)
                post.published = True
                db.session.add(post)
            flash('文章已更新', 'success')

        if form.save.data:
            with db.auto_commit():
                post.set_attr(form.data)
                post.published = False
                db.session.add(post)
            flash('文章已保存为草稿', 'success')

        return redirect(url_for('web.manage_post'))

    if not form.errors:
        form.title.data = post.title
        form.categories.data = [category.id for category in post.categories]
        form.content_markdown.data = post.content_markdown
        form.description.data = post.description
        form.can_comment.data = post.can_comment

    return render_template('admin/post_editor.html', form=form, post=post)


@web.route('/admin/uploaded-image/<filename>')
@login_required
def uploaded_image(filename):
    """
    获取上传图片的 Response
    :param filename: 文件名
    """
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@web.route('/admin/upload-image', methods=['POST'])
@csrf_protect.exempt
@login_required
def upload_image():
    """上传图片视图"""
    file = request.files.get('editormd-image-file')
    base_info = {
        'success': 0,
        'message': '图片上传失败'
    }
    if not file:
        return json.dumps(base_info)

    # 判断文件格式是否被允许
    if not allowed_file(file.filename):
        base_info['message'] = '图片格式不被允许'
        return json.dumps(base_info)

    # 避免文件名重复
    filename = avoided_file_duplication(file.filename)
    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    base_info['success'] = 1
    base_info['message'] = '图片上传成功'
    base_info['url'] = url_for('web.uploaded_image', filename=filename)
    return json.dumps(base_info)
