import random

from faker import Faker
from pypinyin import lazy_pinyin

from app.models import Admin, Category, Comment, Post, Link
from app.libs.extensions import db


class FakeData:
    """
    虚拟数据生成类
    """
    FAKER = Faker('zh_cn')

    @classmethod
    def fake_admin(cls):
        """
        生成 admin 表虚拟数据
        :return: None
        """
        with db.auto_commit():
            admin = Admin()
            admin.username = 'admin'
            admin.password = '12345678'
            admin.nickname = '临时管理员昵称'
            admin.blog_title = '临时博客名'
            admin.blog_subtitle = '临时博客副标题'
            admin.blog_about = FakeData.FAKER.text(1000)
            # 请务必执行完 `flask fake` 之后，执行 `flask admin` 重设管理员账户，并填入你的真实邮箱
            # 否则你将无法收到新评论邮件
            admin.email = 'admin@admin.com'
            db.session.add(admin)

    @classmethod
    def fake_categories(cls, count: int = 9):
        """
        生成博客分类虚拟数据
        :param count: default=9，包括我们初始数据库生成的默认分类，默认一共有 10 个分类
        :return: None
        """
        while Category.query.count() < count + 1:
            category_name = FakeData.FAKER.word()
            # 分类不能同名，为了避免这个情况，这里要做一定的判断
            if Category.query.filter_by(name=category_name).first():
                continue

            with db.auto_commit():
                category = Category()
                category.name = category_name
                category.alias = ''.join(lazy_pinyin(category_name))
                db.session.add(category)

    @classmethod
    def fake_posts(cls, count: int = 50):
        """
        生成博客文章虚拟数据
        :param count: default=50，生成 50 条文章记录
        :return: None
        """
        for i in range(count):
            with db.auto_commit():
                post = Post()
                post.title = FakeData.FAKER.sentence()
                post.content = FakeData.FAKER.text(4000)
                # description 字段是为了 SEO 准备的，最大不超过 150 字符，默认取文章开头前 150 个字符
                post.description = post.content[0: 149]
                category_id_one = random.randint(1, Category.query.count())
                category_id_two = random.randint(1, Category.query.count())
                # 分类 id 为 1 是默认分类，如果出现，则只给文章默认分类
                if category_id_one == 1 or category_id_two == 1:
                    post.categories = [Category.query.get(1)]
                # 如果分类 id 相同那么只取其中一个
                elif category_id_one == category_id_two:
                    post.categories = [Category.query.get(category_id_one)]
                else:
                    post.categories = [
                        Category.query.get(category_id_one),
                        Category.query.get(category_id_two)
                    ]
                db.session.add(post)

    @classmethod
    def fake_comments(cls, count: int = 1000):
        """
        生成博客文章评论
        :param count: default=1000，默认生成 1000 条评论
        :return: None
        """
        # 50% 已审核评论
        # 5% 未审核评论
        # 10% 管理员评论
        # 35% 回复的评论
        reviewed_comments_count = int(count * 0.5)
        unreviewed_comments_count = int(count * 0.05)
        admin_comments_count = int(count * 0.1)
        replied_comments_count = int(count * 0.35)

        def _generate_comments(
                _count: int,
                reviewed: bool = True,
                from_admin: bool = False,
                is_replied: bool = False
        ):
            """
            生成评论数据，内部调用
            :param _count: 生成的评论数量
            :param reviewed: default=True，默认是已审核评论
            :param from_admin: default=False，默认不是管理员评论
            :param is_replied: default=False，默认不是回复评论
            :return: None
            """
            comments_count = Comment.query.count()
            posts_count = Post.query.count()
            for i in range(_count):
                with db.auto_commit():
                    comment = Comment()
                    if not from_admin:
                        comment.author = cls.FAKER.name()
                        comment.email = cls.FAKER.email()
                        comment.site = cls.FAKER.url()
                    else:
                        comment.author = Admin.query.get(1).nickname
                        comment.email = "admin@email.com"
                        comment.site = "localhost:5000"
                    comment.content = cls.FAKER.text(random.randint(40, 200))
                    comment.from_admin = from_admin
                    comment.reviewed = reviewed
                    if is_replied:
                        comment.replied = Comment.query.get(random.randint(1, comments_count))
                    comment.post = Post.query.get(random.randint(1, posts_count))
                    db.session.add(comment)

        # 生成已审核的评论
        _generate_comments(reviewed_comments_count)
        # 生成未审核评论
        _generate_comments(unreviewed_comments_count, reviewed=False)
        # 生成管理员评论
        _generate_comments(admin_comments_count, from_admin=True)
        # 生成回复的评论
        _generate_comments(replied_comments_count, is_replied=True)

    @classmethod
    def fake_links(cls):
        """
        生成博客链接虚拟数据
        :return: None
        """
        with db.auto_commit():
            weibo = Link(name='Weibo', url='#', tag='weibo')
            weixin = Link(name='Weixin', url='#', tag='weixin')
            douban = Link(name='Douban', url='#', tag='douban')
            zhihu = Link(name='Zhihu', url='#', tag='zhihu')
            github = Link(name='Github', url='#', tag='github')
            twitter = Link(name='Twitter', url='#', tag='twitter')
            facebook = Link(name='FaceBook', url='#', tag='facebook')
            google = Link(name='Google', url='#', tag='google')
            linkedin = Link(name='LinkedIn', url='#', tag='linkedin')
            other = Link(name='Other', url='#', tag='other')
            telegram = Link(name='Telegram', url='#', tag='telegram')
            frendlink = Link(name='FriendLink', url='#', tag='friendLink')
            db.session.add_all([twitter, facebook, google, linkedin, weibo, weixin,
                                douban, zhihu, github, other, telegram, frendlink])
