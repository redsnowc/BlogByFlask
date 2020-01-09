from app.libs.extensions import db
from app.models.base import Base


class Category(Base):
    """
    文章分类数据表模型
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(12), nullable=False, unique=True)
    posts = db.relationship("Post", secondary='post_category_middle')
    alias = db.Column(db.String(24), unique=True)
    show = db.Column(db.Boolean, default=True)
