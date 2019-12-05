from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange
from wtforms.validators import ValidationError


class RegisterForm(FlaskForm):
    username = StringField(
        "用户名",
        validators=[
            DataRequired(message="用户名是必填项"),
            Length(6, 12, message="用户名长度应在 6 - 12 个字符之间")
        ],
        render_kw={
            "placeholder": "请输入用户名",
            "class": "form-control"
        }
    )
    age = IntegerField(
        "年龄",
        validators=[NumberRange(0, 150)],
        render_kw={
            "class": "form-control",
            "type": "number"
        }
    )
    email = StringField(
        "邮箱",
        validators=[
            DataRequired(message="邮箱是必填项"),
            Email(message="邮箱格式不正确")
        ],
        render_kw={
            "class": "form-control",
            "type": "email"
        }
    )
    password = PasswordField(
        "密码",
        validators=[
            DataRequired(message="密码是必填项"),
            Length(3, 24, message="密码长度应在 3 - 24 个字符之间")
        ],
        render_kw={
            "class": "form-control",
        }
    )
    confirm_password = PasswordField(
        "确认密码",
        validators=[EqualTo('password', message="两次输入的密码不一致")],
        render_kw={
            "class": "form-control",
        }

    )
    submit = SubmitField("注册", render_kw={"class": "btn btn-primary"})

    def validate_username(self, field):
        # 避免循环引入
        from models import User
        if User.query.filter(User.username == field.data).first():
            raise ValidationError("用户名已存在")

    def validate_email(self, field):
        # 避免循环引入
        from models import User
        if User.query.filter(User.email == field.data).first():
            raise ValidationError("邮箱已存在")


