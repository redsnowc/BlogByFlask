from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

from demo.blueprints.home.home import home
from demo.blueprints.admin.admin import admin
from forms import RegisterForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "1234"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost:3306/fortest?charset=UTF8MB4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


app.register_blueprint(home)
app.register_blueprint(admin)


@app.route("/", methods=["POST", "GET"])
def index():
    form = RegisterForm()
    print(request.method)
    if form.validate_on_submit():
        from models import User
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.age = form.age.data
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
    return render_template("form.html", form=form)


if __name__ == "__main__":
    app.run()
