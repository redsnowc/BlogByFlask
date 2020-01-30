from flask import url_for

from test.base import BaseTest
from app.libs.extensions import db
from app.models import Category, Post, Comment


class BlogFrontTest(BaseTest):

    def test_index_page(self) -> None:
        """测试首页"""
        data = self.get_response_text_data('web.index', 'get')
        self.assertIn('临时博客名', data)
        self.assertIn('临时博客副标题', data)
        self.assertEqual(1, data.count('nav-item'))
        self.assertEqual(1, data.count('<div class="col-10 post-container">'))
        self.assertEqual(0, data.count('<a class="icon"'))
        self.assertEqual(2, data.count('<svg'))

        self.fake_data.fake_links()
        self.fake_data.fake_comments(20)
        self.login()
        data = self.get_response_text_data('web.index', 'get')
        self.assertIn('后台首页', data)
        self.assertIn('新建文章', data)
        self.assertIn('待审核评论', data)
        self.assertEqual(10, data.count('<a class="icon"'))

    def test_index_pagination(self) -> None:
        """测试首页分页器"""
        self.fake_data.fake_posts(20)
        data = self.get_response_text_data('web.index', 'get', page=2)
        self.assertEqual(10, data.count('<div class="col-10 post-container">'))

    def test_category_page(self) -> None:
        """测试分类页面"""
        category = Category.query.get(2)
        data = self.get_response_text_data('web.category', 'get', name_or_alias='testCategory')
        self.assertIn('<h1 class="display-4 col-12">分类 · testCategory</h1>', data)
        self.assertEqual(len(category.posts), data.count('<div class="col-10 post-container">'))

    def test_post_page(self) -> None:
        """测试文章详情页"""
        data = self.get_response_text_data('web.post', 'get', post_id=1)
        self.assertIn('testTitle', data)
        self.assertIn('testContent', data)
        self.assertIn('testAuthor', data)
        self.assertIn('testCommentContent', data)

    def test_visitor_post_comment(self) -> None:
        """测试访客发布评论功能"""
        data = self.get_response_text_data('web.post', 'post', data={
            'author': 'newAuthor',
            'content': 'newContent'
        }, follow_redirects=True, post_id=1)
        self.assertIn('您的评论会尽快被审核，感谢您的评论。', data)
        self.assertNotIn('newContent', data)

    def test_admin_post_comment(self) -> None:
        """测试管理员发布评论功能"""
        self.login()
        data = self.get_response_text_data('web.post', 'post', data={
            'content': 'adminContent'
        }, follow_redirects=True, post_id=1)
        self.assertIn('评论已发布', data)
        self.assertIn('adminContent', data)

    def test_visitor_reply_comment(self) -> None:
        """测试访客回复评论功能"""
        data = self.get_response_text_data('web.post', 'post', data={
            'author': 'replyAuthor',
            'content': 'replyContent'
        }, follow_redirects=True, post_id=1, reply_id=1)
        self.assertIn('您的评论会尽快被审核，感谢您的评论。', data)
        self.assertNotIn('replyContent', data)

    def test_admin_reply_comment(self) -> None:
        """测试管理员回复评论功能"""
        self.login()
        data = self.get_response_text_data('web.post', 'post', data={
            'content': 'AdminReplyContent'
        }, follow_redirects=True, post_id=1, reply_id=1)
        self.assertIn('评论已发布', data)
        self.assertIn('AdminReplyContent', data)

    def test_invalid_comment(self) -> None:
        """测试无效的评论"""
        post = Post.query.get(1)
        with db.auto_commit():
            post.trash = True
            db.session.add(post)

        data = self.get_response_text_data('web.post', 'post', data={
            'author': 'replyAuthor',
            'content': 'replyContent'
        }, follow_redirects=True, post_id=1)
        self.assertIn('找不到您要访问的页面', data)

        with db.auto_commit():
            post.trash = False
            post.published = False
            db.session.add(post)

        data = self.get_response_text_data('web.post', 'post', data={
            'author': 'replyAuthor',
            'content': 'replyContent'
        }, follow_redirects=True, post_id=1)
        self.assertIn('找不到您要访问的页面', data)

        with db.auto_commit():
            post.trash = False
            post.published = True
            post.can_comment = False

        data = self.get_response_text_data('web.post', 'post', data={
            'author': 'replyAuthor',
            'content': 'replyContent'
        }, follow_redirects=True, post_id=1)
        self.assertIn('评论已关闭', data)
        self.assertNotIn('test content', data)

    def test_invalid_reply(self) -> None:
        """测试无效的回复"""
        data = self.get_response_text_data('web.post', 'post', data={
            'author': 'replyAuthor',
            'content': 'replyContent'
        }, follow_redirects=True, post_id=1, reply_id=2)
        self.assertIn('找不到您要访问的页面', data)

        comment = Comment.query.get(1)
        with db.auto_commit():
            comment.trash = True
            db.session.add(comment)

        data = self.get_response_text_data('web.post', 'post', data={
            'author': 'replyAuthor',
            'content': 'replyContent'
        }, follow_redirects=True, post_id=1, reply_id=1)
        self.assertIn('找不到您要访问的页面', data)

        with db.auto_commit():
            comment.trash = False
            comment.reviewed = False
            db.session.add(comment)

        data = self.get_response_text_data('web.post', 'post', data={
            'author': 'replyAuthor',
            'content': 'replyContent'
        }, follow_redirects=True, post_id=1, reply_id=1)
        self.assertIn('找不到您要访问的页面', data)

        self.fake_data.fake_posts(1)
        with db.auto_commit():
            comment.trash = False
            comment.reviewed = True
            comment.post_id = 2
            db.session.add(comment)

        data = self.get_response_text_data('web.post', 'post', data={
            'author': 'replyAuthor',
            'content': 'replyContent'
        }, follow_redirects=True, post_id=1, reply_id=1)
        self.assertIn('找不到您要访问的页面', data)

    def test_reply_form_error_page(self) -> None:
        """测试回复表单验证失败页面"""
        data = self.get_response_text_data('web.post', 'post', follow_redirects=True, post_id=1, reply_id=1)
        self.assertIn('回复提交失败', data)
        self.assertIn('评论内容不能为空', data)
        self.assertIn('昵称不能为空', data)

    def test_comment_form_error(self) -> None:
        """测试主评论表单错误"""
        data = self.get_response_text_data('web.post', 'post', follow_redirects=True, post_id=1)
        self.assertIn('评论表单填写有误', data)
        self.assertIn('评论内容不能为空', data)
        self.assertIn('昵称不能为空', data)

    def test_search_page(self) -> None:
        """测试搜索页面"""
        data = self.get_response_text_data('web.search', 'get', follow_redirects=True, search='test')
        self.assertIn("'test' 的搜索结果", data)
        self.assertEqual(1, data.count('post-container'))
        self.assertEqual(2, data.count('#ff3366'))

        # data = self.get_response_text_data('web.search', 'get', follow_redirects=True, search='')
        # self.assertIn('搜索内容不能为空', data)
        #
        # data = self.get_response_text_data('web.search', 'get', follow_redirects=True, search='1')
        # self.assertIn('搜索内容不能少于两个字符', data)
        #
        # data = self.get_response_text_data('web.search', 'get', follow_redirects=True, search='nothing')
        # self.assertIn('没有搜索到任何包含 nothing 的结果', data)

    def test_about_page(self) -> None:
        """测试关于页面"""
        data = self.get_response_text_data('web.about', 'get')
        self.assertIn('关于我和我的博客', data)
        self.assertIn('相关链接', data)
