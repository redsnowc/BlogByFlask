import unittest
import os
import shutil

from flask import url_for, Response
from typing import Union

from app import create_app
from app.libs.extensions import db
from app.models import Comment, Category, Post, Link
from app.libs.fake_data import FakeData
from app.configs import basedir


class BaseTest(unittest.TestCase):

    def setUp(self) -> None:
        """启动测试前执行"""
        app = create_app(config='test')
        self.context = app.test_request_context()
        self.context.push()
        self.client = app.test_client()
        self.runner = app.test_cli_runner()

        self.runner.invoke(args=['initdb', '--_init'])
        self.fake_data = FakeData()
        self.fake_data.fake_admin()

        # 测试前生成一些少部分测试数据以供使用
        category = Category(
            name='testCategory',
            alias='test-alias',
        )
        link = Link(
            name='testLink',
            url='https://www.test.com',
        )
        post = Post(
            title='testTitle',
            content='<p>testContent<p>',
            content_markdown='testContent',
            description='testDescription',
            categories=[category]
        )
        comment = Comment(
            author='testAuthor',
            content='testCommentContent',
            post=post,
            reviewed=True
        )
        with db.auto_commit():
            db.session.add_all([category, link, post, comment])

    def tearDown(self) -> None:
        """测试结束后执行"""
        db.drop_all()
        self.context.pop()
        shutil.rmtree(os.path.join(basedir, 'test/whooshee'))

    def login(self) -> Response:
        """登录"""
        return self.client.post(url_for('web.login'), data={
            'username': 'admin',
            'password': '12345678'
        }, follow_redirects=True)

    def logout(self) -> Response:
        """登出"""
        return self.client.get(url_for('web.logout'), follow_redirects=True)

    def get_response_text_data(self, endpoint: str, method: str, data: dict = None, json: Union[dict, str] = None,
                               follow_redirects: bool = False, **kwargs) -> str:
        """获取 response 对象的文本数据"""
        if json is None:
            json = {}
        if data is None:
            data = {}

        if method == 'get':
            response = self.client.get(url_for(endpoint, **kwargs), follow_redirects=follow_redirects)
        elif method == 'post':
            if data:
                response = self.client.post(url_for(endpoint, **kwargs), data=data, follow_redirects=follow_redirects)
            elif json:
                response = self.client.post(url_for(endpoint, **kwargs), json=json, follow_redirects=follow_redirects)
            else:
                response = self.client.post(url_for(endpoint, **kwargs), follow_redirects=follow_redirects)
        else:
            raise ValueError('`method` must be `get` or `post`.')
        return response.get_data(as_text=True)

