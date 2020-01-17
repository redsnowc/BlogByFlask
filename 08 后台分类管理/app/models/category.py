from app.libs.extensions import db
from app.models.base import Base


class Category(Base):
    """
    文章分类数据表模型
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(12), nullable=False, unique=True)
    posts = db.relationship("Post", secondary='post_category_middle')
    alias = db.Column(db.String(24), unique=True, nullable=True)
    show = db.Column(db.Boolean, default=True)

    def delete(self):
        """
            执行删除分类操作
        """
        if self.posts:
            for post in self.posts:
                # 如果要删除的分类文章没有其它分类则将其移动至默认分类下
                if len(post.categories) == 1:
                    with db.auto_commit():
                        post.categories = [Category.query.get(1)]
                        db.session.add(post)

        with db.auto_commit():
            db.session.delete(self)
