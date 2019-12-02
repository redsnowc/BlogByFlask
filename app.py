from flask import Flask


from demo.blueprints.home.home import home
from demo.blueprints.admin.admin import admin

app = Flask(__name__)


app.register_blueprint(home)
app.register_blueprint(admin)


# if __name__ == "__main__":
#     app.run()
