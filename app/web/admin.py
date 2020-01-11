from flask import render_template
from flask_login import login_required

from app.web import web


@web.route('/admin')
@login_required
def admin():
    return render_template('admin/admin.html')
