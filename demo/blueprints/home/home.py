from flask import Blueprint, render_template


home = Blueprint("home", __name__, url_prefix="/home",
                 template_folder="templates",
                 static_folder="static")


@home.route('/')
def index():
    return render_template("home/index.html")
