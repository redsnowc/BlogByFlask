from threading import Thread

from flask import current_app, render_template, Flask
from flask_mail import Message

from app.libs.extensions import mail
from app.models import Admin


def _send_async_email(app: Flask, message: Message):
    """
    执行 mail.send 发送电子邮件，异步调用
    :param app: Flask 核心对象
    :param message: flask_mail.Message 实例
    """
    with app.app_context():
        try:
            mail.send(message)
        except Exception as e:
            print(e)


def send_mail(to: list, subject: str, template: str, **kwargs):
    """
    发送电子邮件，内部开启一个新线程执行异步发送，避免页面阻塞
    :param to: 目标电子邮件列表
    :param subject: 电子邮件标题
    :param template: 邮件模板路径
    """
    admin = Admin.query.first()
    message = Message(
        f'{subject} - {admin.blog_title}',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=to
    )
    message.html = render_template(template, **kwargs)
    # current_app 无法跨线程使用，必须获得真正的 Flask 核心对象
    app = current_app._get_current_object()
    thread = Thread(target=_send_async_email, args=[app, message])
    thread.start()
