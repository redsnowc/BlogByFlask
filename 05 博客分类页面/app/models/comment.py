from datetime import datetime

from app.models.base import Base
from app.libs.extensions import db


class Comment(Base):
    """
    文章评论数据表模型类
    """
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(16))
    email = db.Column(db.String(64))
    site = db.Column(db.String(256))
    content = db.Column(db.Text)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    from_admin = db.Column(db.Boolean, default=False)
    reviewed = db.Column(db.Boolean, default=False)
    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    replied = db.relationship('Comment', remote_side=[id], uselist=False)
    replies = db.relationship('Comment', cascade='all')
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', uselist=False)
