from app.web import web


@web.route('/')
def index():
    """首页视图"""

    return '博客首页'

