from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, Email, NumberRange, ValidationError


class AdminForm(FlaskForm):
    """博客设置表单类"""
    blog_title = StringField('博客名称', validators=[DataRequired('博客名不能为空'),
                                                 Length(max=128, message='博客名长度不能超过 128 个字符')])
    blog_subtitle = StringField('博客副标题', validators=[DataRequired('博客副标题不能为空'),
                                                     Length(max=256, message='博客副标题长度不能超过 256 个字符')])
    nickname = StringField('管理员昵称', validators=[DataRequired('管理员昵称不能为空'),
                                                Length(max=30, message='管理员昵称长度不能超过 30 个字符')])
    email = StringField('管理员邮箱', validators=[DataRequired('管理员邮箱不能为空'), Email(message='邮箱格式不正确'),
                                             Length(max=64, message='管理员邮箱长度不能超过 64 个字符')])
    post_per_page = IntegerField('文章每页显示数量', validators=[DataRequired('文章每页显示数量不能为空'),
                                                         NumberRange(min=1, message='文章每页显示数量不能小于 1')])
    comment_per_page = IntegerField('评论每页显示数量', validators=[DataRequired('评论每页显示数量不能为空'),
                                                            NumberRange(min=1, message='评论每页显示数量不能小于 1')])
    blog_about = TextAreaField()
    blog_about_markdown = TextAreaField()
    submit = SubmitField('提交')

    def validate_blog_about_markdown(self, filed):
        if not filed.data:
            raise ValidationError('博客关于内容不能为空')
