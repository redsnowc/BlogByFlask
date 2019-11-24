from flask import Flask, render_template

app = Flask(__name__)


app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 


class User:
    def __init__(self, permission, username):
        self.permission = permission
        self.username = username


def hidden_tel(tel):
    new_tel = tel.replace(tel[3:7], "*" * 4)
    return new_tel


app.add_template_filter(hidden_tel)


@app.route('/')
def index():
    username = "redsnow"
    languages = ["python", "javascript", "php", "java", "c", "c++"]
    user = User('admin', 'redsnow')
    tel = "13956781234"
    return render_template("index.html", username=username, languages=languages, user=user, tel=tel)


@app.route("/hi/<username>")
def hi(username):
    return "Hi %s" % username


# @app.route("/go_home")
# def go_home():
#     return redirect(url_for('index'))

