from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique=True, nullable=False)
    age = db.Column(db.SMALLINT, nullable=False)
    email = db.Column(db.String(56), unique=True, nullable=False)
    _password_hash = db.Column('password', db.String(256), nullable=False)

    # 将实例方法 password 转换成属性来操作私有变量 _password_hash
    @property
    def password(self):
        return self._password_hash

    @password.setter
    def password(self, raw):
        self._password_hash = generate_password_hash(raw)


if __name__ == "__main__":
    db.create_all()
