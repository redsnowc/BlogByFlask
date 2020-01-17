from app.models.base import Base
from app.libs.extensions import db


class Link(Base):
    """
    链接数据表模型
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    tag = db.Column(db.String(10))
    url = db.Column(db.String(256))
