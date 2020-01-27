from datetime import datetime

from app.models.base import Base
from app.libs.extensions import db, whooshee


@whooshee.register_model('title', 'content')
class Post(Base):
    """
    博客文章数据表模型类
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    content_markdown = db.Column(db.Text)      # 储存 markdown 格式的正文，用以编辑时传递给 markdown 编辑器
    content = db.Column(db.Text)               # 储存 HTML 格式正文，用来展示
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    categories = db.relationship('Category', secondary='post_category_middle')
    comments = db.relationship(
        'Comment', cascade='all, delete-orphan'
    )
    can_comment = db.Column(db.Boolean, default=True)
    description = db.Column(db.String(150))    # SEO 相关，写在 <meta> 标签内
    trash = db.Column(db.Boolean, default=False)
    published = db.Column(db.Boolean, default=True)
