"""Module for Flask-SQLAlchemy models."""
import datetime
from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

solves = db.Table(
    'solves',
    db.Column('problem_id', db.Integer, db.ForeignKey('problem.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model, UserMixin):
    """Model for online judge users."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    solves = db.relationship('Problem', secondary=solves, backref='users', lazy='dynamic')

    def __init__(self, username, password, email, first_name, last_name):
        self.username = username
        self.set_password(password)
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Problem(db.Model):
    """Model for coding problems."""
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String)
    index = db.Column(db.String)
    title = db.Column(db.String)
    statement = db.Column(db.String)

    def __init__(self, url, index, title, statement):
        self.url = url
        self.index = index
        self.title = title
        self.statement = statement

class Submission(db.Model):
    """Model for user submissions."""
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String)
    code = db.Column(db.String)
    date = db.Column(db.DateTime)
    verdict = db.Column(db.String)
    runtime = db.Column(db.String)
    memory = db.Column(db.String)
    cf_id = db.Column(db.String)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'))
    problem = db.relationship('Problem', backref=db.backref('submissions', lazy='dynamic'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('users', lazy='dynamic'))

    def __init__(self, language, code, problem, user):
        self.language = language
        self.code = code
        self.date = datetime.datetime.now()
        self.verdict = 'JUDGING'
        self.problem = problem
        self.user = user
