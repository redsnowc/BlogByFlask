from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Length, ValidationError

from app.models import Category


class NewCategoryForm(FlaskForm):
    """新增分类表单类"""
    name = StringField(validators=[DataRequired("分类名不能为空"),
                                   Length(max=12, message='分类名最长不能超过 12 个字符')])
    alias = StringField(validators=[Length(max=24, message='别名最长不能超过 24 个字符')])
    show = BooleanField()

    def validate_name(self, filed):
        if Category.query.filter_by(name=filed.data).first():
            raise ValidationError('分类名已存在')

    def validate_alias(self, filed):
        if Category.query.filter_by(alias=filed.data).first():
            raise ValidationError('别名已存在')


class EditCategoryForm(NewCategoryForm):
    """编辑分类表单类"""
    id = HiddenField()

    def _get_record_by_id(self):
        """通过隐藏的 ID 字段的值，查询分类记录"""
        return Category.query.get(self.id.data)

    def validate_name(self, filed):
        """验证分类的名称是否在其它分类中存在"""
        category_by_id = self._get_record_by_id()
        category_by_name = Category.query.filter_by(name=filed.data).first()
        if category_by_name and category_by_name.id != category_by_id.id:
            raise ValidationError('分类名已存在')

    def validate_alias(self, filed):
        """验证分类的别名是否在其它分类中存在"""
        category_by_id = self._get_record_by_id()
        category_by_alias = Category.query.filter_by(alias=filed.data).first()
        if category_by_alias and category_by_alias.id != category_by_id.id:
            raise ValidationError('别名已存在')

