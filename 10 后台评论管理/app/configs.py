import os

from datetime import timedelta

from app.models import Admin, Category, Comment, Link, Post


class BaseConfig:
    """
    配置基类，公用配置写在这里
    """
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    REMEMBER_COOKIE_DURATION = timedelta(days=31)
    PERMANENT_SESSION_LIFETIME = timedelta(days=3)

    # AJAX 请求校验查询模型名称使用
    MODELS = {'Admin': Admin, 'Category': Category, 'Comment': Comment, 'Link': Link, 'Post': Post}
    ADMIN_PER_PAGE = 20


class DevelopmentConfig(BaseConfig):
    """
    开发环境配置类
    """
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(seconds=1)


class TestConfig(BaseConfig):
    """
    测试环境配置类
    """
    pass


class ProductionConfig(BaseConfig):
    """
    生产环境配置类
    """
    pass


# 配置类字典，根据传递的 key 选择不同的配置类
configs = {
    'development': DevelopmentConfig,
    'test': TestConfig,
    'production': ProductionConfig
}
