from flask import render_template, request, redirect, flash, url_for, session, abort
from flask_login import login_user, current_user, logout_user

from app.web import web
from app.forms.login import LoginForm
from app.models import Admin


@web.route('/login', methods=['POST', 'GET'])
def login():
    """登录视图"""
    # 如果用户已登录则跳转回首页
    if current_user.is_authenticated:
        return redirect(url_for('web.index'))

    form = LoginForm(request.form)

    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and admin.check_password(form.password.data):
            # 使 PERMANENT_SESSION_LIFETIME 配置项生效
            session.permanent = True
            login_user(admin, remember=form.remember.data)
            # 登录后重定向，预防重定向攻击
            next_url = request.args.get('next')
            if not next_url or not next_url.startswith('/'):
                next_url = url_for('web.index')
            return redirect(next_url)
        else:
            flash('登录失败！请检查用户名或密码', 'error')
    return render_template('login/login.html', form=form)


@web.route('/logout')
def logout():
    """登出视图"""
    # 如果是未登录用户访问，直接抛出 404 错误
    if not current_user.is_authenticated:
        abort(404)
    logout_user()
    flash('已登出', 'info')
    return redirect(url_for('web.login'))

