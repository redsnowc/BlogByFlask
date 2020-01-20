from app.libs.extensions import db

# Post 表和 Category 表多对多关系中间表
post_category_middle = db.Table(
    'post_category_middle',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

