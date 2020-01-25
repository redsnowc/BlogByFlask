from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, URL, ValidationError

from app.models import Link


class NewLinkForm(FlaskForm):
    """新增链接表单"""
    name = StringField(validators=[DataRequired('链接名称不能为空'),
                                   Length(max=60, message='链接名称最大不能超过 60 个字符')])
    url = StringField(validators=[DataRequired('链接地址不能为空'),
                                  URL(message='链接格式不正确'),
                                  Length(6, 255, message='链接地址长度应在 6 - 255 个字符之间')])
    tag = SelectField(
        label='标签',
        validators=[DataRequired('必须选择一个标签')],
        render_kw={
            'class': 'custom-select my-1 mr-sm-2'
        },
        choices=[
            ('weixin', '微信'),
            ('weibo', '微博'),
            ('douban', '豆瓣'),
            ('zhihu', '知乎'),
            ('google', '谷歌'),
            ('linkedin', '领英'),
            ('twitter', '推特'),
            ('facebook', '脸书'),
            ('github', 'Github'),
            ('telegram', 'Telegram'),
            ('other', '其它'),
            ('friendLink', '友情链接')
        ],
        default='other',
        coerce=str
    )

    def validate_name(self, filed):
        if Link.query.filter_by(name=filed.data).first():
            raise ValidationError('链接名称已存在')

    def validate_url(self, filed):
        if Link.query.filter_by(url=filed.data).first():
            raise ValidationError('链接已存在')


class EditLinkForm(NewLinkForm):
    """编辑链接表单"""
    id = HiddenField()

    def _get_record_by_id(self):
        """通过隐藏的 ID 字段的值，查询分类记录"""
        return Link.query.get(self.id.data)

    def validate_name(self, filed):
        """验证链接的名称否已存在"""
        link_by_id = self._get_record_by_id()
        link_by_name = Link.query.filter_by(name=filed.data).first()
        if link_by_name and link_by_name.id != link_by_id.id:
            raise ValidationError('链接名称已存在')

    def validate_url(self, filed):
        """验证链接的 URL 是否已存"""
        link_by_id = self._get_record_by_id()
        link_by_url = Link.query.filter_by(url=filed.data).first()
        if link_by_url and link_by_url.id != link_by_id.id:
            raise ValidationError('链接已存在')
