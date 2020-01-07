from flask import Blueprint

# 蓝图实例，单蓝图多模块
web = Blueprint('web', __name__)

# 执行蓝图的模块文件，确保视图被识别
import app.web.blog
import app.web.blog_front
