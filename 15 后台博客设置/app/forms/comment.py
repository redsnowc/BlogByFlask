from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, URL, Length, Email, Optional


class CommentForm(FlaskForm):
    author = StringField(validators=[DataRequired('昵称不能为空'),
                                     Length(max=16, message='昵称最长不能超过 16 个字符')])
    email = StringField(validators=[Optional(), Email(message='邮箱格式有误'),
                                    Length(max=64, message='邮箱最长不能超过 64 个字符')])
    site = StringField(validators=[Optional(), URL(message='链接格式有误'),
                                   Length(max=256, message='链接最长不能超过 256 个字符')])
    content = TextAreaField(validators=[DataRequired('评论内容不能为空')])


