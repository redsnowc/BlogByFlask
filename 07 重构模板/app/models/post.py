from datetime import datetime

from app.models.base import Base
from app.libs.extensions import db


class Post(Base):
    """
    博客文章数据表模型类
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    content = db.Column(db.Text)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    categories = db.relationship('Category', secondary='post_category_middle')
    comments = db.relationship(
        'Comment', cascade='all, delete-orphan'
    )
    can_comment = db.Column(db.Boolean, default=True)
    # SEO 相关，写在 <meta> 标签内
    description = db.Column(db.String(150))
