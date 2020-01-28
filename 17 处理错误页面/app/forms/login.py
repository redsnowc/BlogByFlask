from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    """登录表单类"""
    username = StringField(validators=[DataRequired('用户名不能为空'), Length(5, 30, message='用户名应为在 5 到 30 个字符之间')])
    password = PasswordField(validators=[DataRequired('密码不能为空'), Length(8, 24, message='密码应在 8 到 24 个字符之间')])
    remember = BooleanField()
