from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    surname = db.Column(db.String)
    name = db.Column(db.String)
    second_name = db.Column(db.String)
    age = db.Column(db.Integer)
    sex = db.Column(db.String)
    education = db.Column(db.Text)
    background = db.Column(db.Text)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def __repr__(self):
        return f'User {self.id} - {self.username}'
