from test.base import BaseTest


class AuthTest(BaseTest):

    def test_login_page(self) -> None:
        """测试登录页面"""
        data = self.get_response_text_data('web.login', 'get')
        self.assertIn('用户名', data)
        self.assertIn('密码', data)
        self.assertIn('记住我', data)
        self.assertIn('返回首页', data)
        self.assertIn('登录', data)

    def test_login(self) -> None:
        """测试登录功能"""
        self.login()
        data = self.get_response_text_data('web.login', 'get', follow_redirects=True)
        self.assertNotIn('登录', data)
        self.assertIn('testTitle', data)
        self.assertIn('后台首页', data)

    def test_login_form_error(self) -> None:
        """测试登录表单验证失败"""
        data = self.get_response_text_data('web.login', 'post', data={
            'username': 'admin',
            'password': 'wrongPassword'
        }, follow_redirects=True)
        self.assertIn('登录失败！请检查用户名或密码', data)

        data = self.get_response_text_data('web.login', 'post', data={
            'username': 'wrong',
            'password': 'wrongPassword'
        }, follow_redirects=True)
        self.assertIn('登录失败！请检查用户名或密码', data)

        data = self.get_response_text_data('web.login', 'post', data={
            'username': 'wrong',
            'password': 'wrong'
        }, follow_redirects=True)
        self.assertIn('密码应在 8 到 24 个字符之间', data)

    def test_logout(self) -> None:
        """测试登出功能"""
        response = self.logout()
        data = response.get_data(as_text=True)
        self.assertIn('找不到您要访问的页面', data)

        self.login()
        self.logout()
        data = self.get_response_text_data('web.index', 'get')
        self.assertNotIn('后台首页', data)


