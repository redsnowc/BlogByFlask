import json
import io
import os

from flask import url_for, current_app

from test.base import BaseTest
from app.models import Admin, Post, Comment
from app.libs.extensions import db


class AdminTest(BaseTest):

    def setUp(self) -> None:
        super().setUp()
        self.login()

    def check_login_required(self, endpoint: str, method: str, **kwargs) -> None:
        """检查请求登录控制"""
        self.logout()
        if method == 'get':
            response = self.client.get(url_for(endpoint, **kwargs), follow_redirects=True)
        elif method == 'post':
            response = self.client.post(url_for(endpoint, **kwargs), follow_redirects=True)
        else:
            raise ValueError('`method` must be `get` or `post`.')
        data = response.get_data(as_text=True)
        self.assertIn('无权访问此页面，请先登录', data)

    def test_admin_index(self) -> None:
        """测试后台首页"""
        data = self.get_response_text_data('web.admin_index', 'get')
        self.assertEqual(6, data.count('nav-item'))
        self.assertIn('回到博客', data)
        self.assertIn('登出', data)
        self.assertIn('相关操作', data)
        self.assertIn('概览', data)
        self.assertIn('近期文章', data)
        self.assertIn('近期评论', data)
        self.check_login_required('web.admin_index', 'get')

    def test_manage_category_page(self) -> None:
        """测试分类管理页面"""
        data = self.get_response_text_data('web.manage_category', 'get')
        self.assertIn('分类管理', data)
        self.assertIn('添加分类', data)
        self.assertEqual(2, data.count('修改</button>'))
        self.assertEqual(1, data.count('删除</button>'))
        self.assertEqual(2, data.count('<tr data-id='))

        self.check_login_required('web.manage_category', 'get')

    def test_new_category(self) -> None:
        """测试新增分类"""
        self.client.post(url_for('web.manage_category'), data={
            'name': 'newCategory',
            'alias': 'new-alias',
            'show': True
        })

        data = self.get_response_text_data('web.manage_category', 'get')
        self.assertIn('newCategory', data)
        self.assertIn('new-alias', data)

        data = self.get_response_text_data('web.index', 'get')
        self.assertIn('newCategory', data)

    def test_new_category_form_error(self) -> None:
        """测试新增分类表单验证错误"""
        data = self.get_response_text_data('web.manage_category', 'post', follow_redirects=True)
        self.assertIn('分类名不能为空', data)

        data = self.get_response_text_data('web.manage_category', 'post', data={
            'name': '未分类',
            'alias': 'default'
        }, follow_redirects=True)
        self.assertIn('分类名已存在', data)
        self.assertIn('别名已存在', data)

    def test_delete_category(self) -> None:
        """测试删除分类功能"""
        self.client.post(url_for('web.delete_category', category_id=2), follow_redirects=True)

        data = self.get_response_text_data('web.manage_category', 'get')
        self.assertNotIn('testCategory', data)

        data = self.get_response_text_data('web.delete_category', 'post', follow_redirects=True, category_id=2)
        self.assertIn('找不到您要访问的页面', data)

        data = self.get_response_text_data('web.delete_category', 'post', follow_redirects=True, category_id=1)
        self.assertIn('找不到您要访问的页面', data)

        self.check_login_required('web.delete_category', 'post', category_id=2)

    def test_get_category_ajax(self) -> None:
        """测试 AJAX 获取分类记录功能，并检查对 AJAX 请求数据的通用校验是否正常"""
        json_data = json.loads(self.get_response_text_data('web.get_category', 'post', json={
            'modelName': 'Category',
            'id': '1'
        }))
        self.assertEqual(1, json_data['code'])
        self.assertEqual(1, json_data['data']['id'])
        self.assertEqual('未分类', json_data['data']['name'])

        json_data = json.loads(self.get_response_text_data('web.get_category', 'post', json='wrong'))
        self.assertEqual(0, json_data['code'])
        self.assertEqual('AJAX 请求数据格式不正确', json_data['msg'])

        json_data = json.loads(self.get_response_text_data('web.get_category', 'post', json={'id': 1}))
        self.assertEqual(0, json_data['code'])
        self.assertEqual('未指定查询模型', json_data['msg'])

        json_data = json.loads(self.get_response_text_data('web.get_category', 'post', json={'modelName': 'Category'}))
        self.assertEqual(0, json_data['code'])
        self.assertEqual('未指定查询 id', json_data['msg'])

        json_data = json.loads(self.get_response_text_data('web.get_category', 'post', json={
            'modelName': 'Category',
            'id': 'wrong'
        }))
        self.assertEqual(0, json_data['code'])
        self.assertEqual('查询 id 不是数字', json_data['msg'])

        json_data = json.loads(self.get_response_text_data('web.get_category', 'post', json={
            'modelName': 'Wrong',
            'id': '1'
        }))
        self.assertEqual(0, json_data['code'])
        self.assertEqual('指定查询模型不存在', json_data['msg'])

        json_data = json.loads(self.get_response_text_data('web.get_category', 'post', json={
            'modelName': 'Category',
            'id': '100'
        }))
        self.assertEqual(0, json_data['code'])
        self.assertEqual('未查找到任何记录', json_data['msg'])

        json_data = json.loads(self.get_response_text_data('web.get_category', 'post', json={
            'modelName': 'Admin',
            'id': '1'
        }))
        self.assertEqual(0, json_data['code'])
        self.assertEqual('指定查询模型与该查询不符', json_data['msg'])

        self.check_login_required('web.get_category', 'post')

    def test_update_category_ajax(self) -> None:
        """校验 AJAX 更新分类记录功能"""
        json_data = json.loads(self.get_response_text_data('web.update_category', 'post', data={
            'id': 1,
            'name': '修改默认分类',
            'show': True,
            'modelName': 'Category'
        }))
        self.assertEqual(1, json_data['code'])

        data = self.get_response_text_data('web.index', 'get')
        self.assertIn('修改默认分类', data)

        data = self.get_response_text_data('web.manage_category', 'get')
        self.assertIn('修改默认分类', data)
        self.assertNotIn('未分类', data)

        self.check_login_required('web.update_category', 'post')

    def test_update_category_form_error_ajax(self) -> None:
        """测试更新分类表单验证错误"""
        json_data = json.loads(self.get_response_text_data('web.update_category', 'post', data={
            'id': 2,
            'name': '未分类',
            'alias': 'default',
            'show': True,
            'modelName': 'Category'
        }))
        self.assertEqual(2, json_data['code'])
        self.assertEqual(['分类名已存在'], json_data['msg']['name'])
        self.assertEqual(['别名已存在'], json_data['msg']['alias'])

        json_data = json.loads(self.get_response_text_data('web.update_category', 'post', data={
            'id': 2,
            'modelName': 'Category'
        }))
        self.assertEqual(2, json_data['code'])
        self.assertEqual(['分类名不能为空'], json_data['msg']['name'])

        json_data = json.loads(self.get_response_text_data('web.update_category', 'post', data={
            'id': 1,
            'modelName': 'Admin'
        }))
        self.assertEqual(0, json_data['code'])
        self.assertEqual('指定查询模型与该查询不符', json_data['msg'])

    def test_manage_link_page(self) -> None:
        """测试链接管理页面"""
        data = self.get_response_text_data('web.manage_link', 'get')
        self.assertIn('链接管理', data)
        self.assertIn('添加链接', data)
        self.assertEqual(1, data.count('修改</button>'))
        self.assertEqual(1, data.count('删除</button>'))
        self.assertEqual(1, data.count('<tr data-id='))

        self.check_login_required('web.manage_link', 'get')

    def test_new_link(self) -> None:
        """测试新增链接功能"""
        self.client.post(url_for('web.manage_link'), data={
            'name': 'newLink',
            'url': 'https://www.new.com',
            'tag': 'other'
        })

        data = self.get_response_text_data('web.manage_link', 'get')
        self.assertIn('newLink', data)
        self.assertIn('https://www.new.com', data)

    def test_new_link_form_error(self) -> None:
        """测试新增链接功能表单错误"""
        data = self.get_response_text_data('web.manage_link', 'post', data={'url': 'wrong'})
        self.assertIn('链接名称不能为空', data)
        self.assertIn('链接格式不正确', data)

        data = self.get_response_text_data('web.manage_link', 'post', data={
            'name': 'testLink',
            'url': 'https://www.test.com',
            'tag': 'other'
        }, follow_redirects=True)
        self.assertIn('链接名称已存在', data)
        self.assertIn('链接已存在', data)

    def test_delete_link(self) -> None:
        """测试删除链接功能"""
        self.client.post(url_for('web.delete_link', link_id=1))
        data = self.get_response_text_data('web.manage_link', 'get')
        self.assertNotIn('testLink', data)
        self.assertNotIn('https://www.test.com', data)

        data = self.get_response_text_data('web.delete_link', 'post', follow_redirects=True, link_id=1)
        self.assertIn('找不到您要访问的页面', data)

        self.check_login_required('web.delete_link', 'post', link_id=1)

    def test_get_link_ajax(self) -> None:
        """测试 AJAX 获取链接记录功能"""
        json_data = json.loads(self.get_response_text_data('web.get_link', 'post', json={
            'modelName': 'Link',
            'id': '1'
        }))
        self.assertEqual(1, json_data['code'])
        self.assertEqual(1, json_data['data']['id'])
        self.assertEqual('testLink', json_data['data']['name'])

        json_data = json.loads(self.get_response_text_data('web.get_link', 'post', json={
            'modelName': 'Link',
            'id': '2'
        }))
        self.assertEqual(0, json_data['code'])
        self.assertEqual('未查找到任何记录', json_data['msg'])

        json_data = json.loads(self.get_response_text_data('web.get_link', 'post', json={
            'modelName': 'Admin',
            'id': '1'
        }))
        self.assertEqual(0, json_data['code'])
        self.assertEqual('指定查询模型与该查询不符', json_data['msg'])

    def test_update_link_ajax(self) -> None:
        """测试 AJAX 更新链接"""
        json_data = json.loads(self.get_response_text_data('web.update_link', 'post', data={
            'id': 1,
            'name': 'editLink',
            'url': 'https://www.edit.com',
            'tag': 'other',
            'modelName': 'Link'
        }))
        self.assertEqual(1, json_data['code'])

        data = self.get_response_text_data('web.manage_link', 'get')
        self.assertIn('editLink', data)
        self.assertIn('https://www.edit.com', data)

        self.check_login_required('web.update_link', 'post')

    def test_update_link_form_error_ajax(self) -> None:
        """测试 AJAX 更新链接表单验证错误"""
        self.fake_data.fake_links()
        json_data = json.loads(self.get_response_text_data('web.update_link', 'post', data={
            'id': 2,
            'name': 'testLink',
            'url': 'https://www.test.com',
            'tag': 'other',
            'modelName': 'Link'
        }))
        self.assertEqual(2, json_data['code'])
        self.assertEqual(['链接名称已存在'], json_data['msg']['name'])
        self.assertEqual(['链接已存在'], json_data['msg']['url'])

        json_data = json.loads(self.get_response_text_data('web.update_link', 'post', data={
            'id': 2,
            'modelName': 'Link'
        }))
        self.assertEqual(['链接名称不能为空'], json_data['msg']['name'])
        self.assertEqual(['链接地址不能为空'], json_data['msg']['url'])

    def test_manage_comment_page(self) -> None:
        """测试评论管理页面"""
        self.fake_data.fake_comments(100)
        with db.auto_commit():
            admin = Admin.query.first()
            admin.comment_per_page = 100
            db.session.add(admin)

        data = self.get_response_text_data('web.manage_comment', 'get')
        self.assertIn('评论管理', data)
        self.assertNotIn('移出回收站', data)

        data = self.get_response_text_data('web.manage_comment', 'get', status='mine')
        self.assertNotIn('通过审核', data)

        data = self.get_response_text_data('web.manage_comment', 'get', status='unreviewed')
        self.assertNotIn('撤销审核', data)

        data = self.get_response_text_data('web.manage_comment', 'get', status='reviewed')
        self.assertNotIn('通过审核', data)

        data = self.get_response_text_data('web.manage_comment', 'get', status='trash')
        self.assertIn('暂无评论', data)

    def test_review_comment(self) -> None:
        """测试审核评论审核"""
        self.client.post(url_for('web.review_comment', comment_id=1, action='undo'))
        data = self.get_response_text_data('web.manage_comment', 'get', status='unreviewed')
        self.assertIn('testAuthor', data)

        self.client.post(url_for('web.review_comment', comment_id=1, action='do'))
        data = self.get_response_text_data('web.manage_comment', 'get', status='reviewed')
        self.assertIn('testAuthor', data)

        data = self.get_response_text_data('web.review_comment', 'post', follow_redirects=True, comment_id=2, action='undo')
        self.assertIn('找不到您要访问的页面', data)

        self.check_login_required('web.review_comment', 'post', comment_id=1, action='undo')

    def test_trash_comment(self) -> None:
        """测试移动评论至回收站功能"""
        self.client.post(url_for('web.trash_record', record_id=1, action='do', model_name='Comment'))
        data = self.get_response_text_data('web.manage_comment', 'get')
        self.assertNotIn('testAuthor', data)

        data = self.get_response_text_data('web.manage_comment', 'get', status='trash')
        self.assertIn('testAuthor', data)

        data = self.get_response_text_data('web.trash_record', 'post', follow_redirects=True, record_id=2,
                                           action='undo', model_name='Comment')
        self.assertIn('找不到您要访问的页面', data)

        self.check_login_required('web.trash_record', 'post', record_id=1, action='undo', model_name='Comment')

    def test_delete_comment(self) -> None:
        """测试删除评论功能"""
        self.client.post(url_for('web.delete_record', record_id=1, action='one', model_name='Comment'))
        data = self.get_response_text_data('web.manage_comment', 'get')
        self.assertIn('暂无评论', data)

        self.fake_data.fake_comments(10)
        comments = Comment.query.all()
        for comment in comments:
            with db.auto_commit():
                comment.trash = True
                db.session.add(comment)

        self.client.post(url_for('web.delete_record', action='all', model_name='Comment'))
        data = self.get_response_text_data('web.manage_comment', 'get')
        self.assertIn('暂无评论', data)

        data = self.get_response_text_data('web.delete_record', 'post', follow_redirects=True, record_id=1,
                                           action='one', model_name='Comment')
        self.assertIn('找不到您要访问的页面', data)

        self.check_login_required('web.delete_record', 'post', record_id=1, action='one', model_name='Comment')

    def test_manage_post_page(self) -> None:
        """测试文章管理页面"""
        data = self.get_response_text_data('web.manage_post', 'get')
        self.assertIn('testTitle', data)

        data = self.get_response_text_data('web.manage_post', 'get', status='draft')
        self.assertIn('暂无文章', data)

        data = self.get_response_text_data('web.manage_post', 'get', status='trash')
        self.assertIn('暂无文章', data)

        self.check_login_required('web.manage_post', 'get')

    def test_close_comment(self) -> None:
        """测试文章关闭评论功能"""
        self.client.post(url_for('web.close_comment', post_id=1, action='do'))
        data = self.get_response_text_data('web.post', 'get', post_id=1)
        self.assertNotIn('添加评论', data)
        self.assertNotIn('提交评论', data)
        self.assertNotIn('reply-link', data)

        self.client.post(url_for('web.close_comment', post_id=1, action='undo'))
        data = self.get_response_text_data('web.post', 'get', post_id=1)
        self.assertIn('添加评论', data)
        self.assertIn('提交评论', data)
        self.assertIn('reply-link', data)

        data = self.get_response_text_data('web.close_comment', 'post', follow_redirects=True, post_id=2, action='do')
        self.assertIn('找不到您要访问的页面', data)

        self.check_login_required('web.close_comment', 'post', post_id=1, action='undo')

    def test_trash_post(self) -> None:
        """测试移动文章至回收站功能"""
        self.client.post(url_for('web.trash_record', record_id=1, action='do', model_name='Post'))
        data = self.get_response_text_data('web.post', 'get', follow_redirects=True, post_id=1)
        self.assertIn('找不到您要访问的页面', data)

        data = self.get_response_text_data('web.manage_post', 'get', status='trash')
        self.assertIn('testTitle', data)

        self.client.post(url_for('web.trash_record', record_id=1, action='undo', model_name='Post'))
        data = self.get_response_text_data('web.post', 'get', post_id=1)
        self.assertIn('testTitle', data)

    def test_delete_post(self) -> None:
        """测试删除文章功能"""
        self.client.post(url_for('web.delete_record', record_id=1, action='one', model_name='Post'))
        data = self.get_response_text_data('web.post', 'get', follow_redirects=True, post_id=1)
        self.assertIn('找不到您要访问的页面', data)

        data = self.get_response_text_data('web.manage_post', 'get')
        self.assertIn('暂无文章', data)

        self.fake_data.fake_posts(3)
        posts = Post.query.all()
        for post in posts:
            with db.auto_commit():
                post.trash = True
                db.session.add(post)

        self.client.post(url_for('web.delete_record', action='all', model_name='Post'))
        data = self.get_response_text_data('web.manage_post', 'get')
        self.assertIn('暂无文章', data)

    def test_new_post_page(self) -> None:
        """测试新建文章页面"""
        data = self.get_response_text_data('web.new_post', 'get')
        self.assertIn('发布', data)
        self.assertIn('保存为草稿', data)

        self.check_login_required('web.new_post', 'get')

    def test_new_post(self) -> None:
        """测试新建文件功能"""
        self.client.post(url_for('web.new_post'), data={
            'title': 'newTitle',
            'categories': 1,
            'content_markdown': 'newContent',
            'markdownEditor-html-code': '<p>newContent</p>',
            'publish': '发布'
        })

        data = self.get_response_text_data('web.post', 'get', post_id=2)
        self.assertIn('newTitle', data)
        self.assertIn('newContent', data)

        self.client.post(url_for('web.new_post'), data={
            'title': 'draftTitle',
            'categories': 1,
            'content_markdown': 'draftContent',
            'markdownEditor-html-code': '<p>draftContent</p>',
            'save': '保存为草稿'
        })
        data = self.get_response_text_data('web.post', 'get', follow_redirects=True, post_id=3)
        self.assertIn('找不到您要访问的页面', data)

        data = self.get_response_text_data('web.manage_post', 'get', status='draft')
        self.assertIn('draftTitle', data)

    def test_new_post_form_error(self) -> None:
        """测试新建文章表单校验错误"""
        data = self.get_response_text_data('web.new_post', 'post', data={
            'title': 'draftTitle',
            'categories': 1,
            'save': '保存为草稿'
        }, follow_redirects=True)
        self.assertIn('文章内容不能为空', data)

    def test_edit_post_page(self) -> None:
        """测试编辑文章页面"""
        data = self.get_response_text_data('web.edit_post', 'get', post_id=1)
        self.assertIn('testTitle', data)
        self.assertIn('testContent', data)
        self.assertIn('testCategory', data)

        self.check_login_required('web.edit_post', 'get', post_id=1)

    def test_edit_post(self) -> None:
        """测试编辑文章功能"""
        self.client.post(url_for('web.edit_post', post_id=1), data={
            'title': 'editTitle',
            'categories': 1,
            'content_markdown': 'editContent',
            'markdownEditor-html-code': '<p>editContent</p>',
            'publish': '发布'
        })

        data = self.get_response_text_data('web.post', 'get', post_id=1)
        self.assertIn('editTitle', data)
        self.assertIn('editContent', data)

        self.client.post(url_for('web.edit_post', post_id=1), data={
            'title': 'editTitle',
            'categories': 1,
            'content_markdown': 'editContent',
            'markdownEditor-html-code': '<p>editContent</p>',
            'save': '保存为草稿'
        })
        data = self.get_response_text_data('web.post', 'get', follow_redirects=True, post_id=1)
        self.assertIn('找不到您要访问的页面', data)

        data = self.get_response_text_data('web.manage_post', 'get', status='draft')
        self.assertIn('editTitle', data)

    def test_upload_image(self) -> None:
        """测试图片上传"""
        json_data = json.loads(self.get_response_text_data('web.upload_image', 'post', data={
            'editormd-image-file': (io.BytesIO(b'test'), 'test.jpg')
        }))
        self.assertEqual(1, json_data['success'])
        filename = json_data['url'].split('/')[-1]
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        self.assertEqual(True, os.path.exists(file_path))
        os.remove(file_path)

        json_data = json.loads(self.get_response_text_data('web.upload_image', 'post', data={
            'editormd-image-file': 'wrong'
        }))
        self.assertEqual(0, json_data['success'])
        self.assertEqual('图片上传失败', json_data['message'])

        json_data = json.loads(self.get_response_text_data('web.upload_image', 'post', data={
            'editormd-image-file': (io.BytesIO(b'test'), 'test.wrong')
        }))
        self.assertEqual(0, json_data['success'])
        self.assertEqual('图片格式不被允许', json_data['message'])

        self.check_login_required('web.upload_image', 'post')

    def test_blog_setting_page(self) -> None:
        """测试博客设置页面"""
        data = self.get_response_text_data('web.blog_setting', 'get')
        self.assertIn('admin@admin.com', data)

        self.check_login_required('web.blog_setting', 'get')

    def test_edit_blog_setting(self) -> None:
        """测试修改博客设置"""
        self.client.post(url_for('web.blog_setting'), data={
            'blog_title': 'editBlogTitle',
            'blog_subtitle': 'editBlogSubtitle',
            'nickname': 'editNickName',
            'email': 'admin@admin.com',
            'post_per_page': 10,
            'comment_per_page': 10,
            'blog_about_markdown': 'editAbout',
            'markdownEditor-html-code': '<p>editAbout</p>'
        })
        data = self.get_response_text_data('web.index', 'get')
        self.assertIn('editBlogTitle', data)
        self.assertIn('editBlogSubtitle', data)
        self.assertIn('editNickName', data)

        data = self.get_response_text_data('web.about', 'get')
        self.assertIn('editAbout', data)

    def test_edit_blog_setting_form_error(self) -> None:
        """测试修改博客设置表单验证失败"""
        data = self.get_response_text_data('web.blog_setting', 'post', follow_redirects=True)
        self.assertIn('博客名不能为空', data)
        self.assertIn('博客副标题不能为空', data)
        self.assertIn('博客关于内容不能为空', data)
