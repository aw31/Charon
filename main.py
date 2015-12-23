"""Virtual judge server using Charon for submissions."""
import datetime
from flask import Flask, abort, flash, redirect, render_template, request
from flask.ext.login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length
from charon import Charon

app = Flask(__name__)
app.config.update(
    CSRF_ENABLED=True,
    SECRET_KEY='onlybessieknows',
    SQLALCHEMY_DATABASE_URI='sqlite:///data/charon.db',
)

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Table for many-to-many relationship between problems and users.
solves = db.Table('solves',
                  db.Column('problem_id', db.Integer, db.ForeignKey('problem.id')),
                  db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
                  )

class User(db.Model, UserMixin):
    """Model for online judge users."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    email = db.Column(db.String(255), nullable=False, unique=True)
    first_name = db.Column(db.String(100), nullable=False, server_default='')
    last_name = db.Column(db.String(100), nullable=False, server_default='')
    solves = db.relationship('Problem', secondary=solves, backref='users', lazy='dynamic')

    def __init__(self, username, password, email, first_name, last_name):
        self.username = username
        self.password = password
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

@login_manager.user_loader
def load_user(id):
    """Returns user for Flask-Login."""
    return User.query.get(int(id))

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

class ProblemForm(Form):
    """Form for adding new problems."""
    url = StringField('URL', validators=[DataRequired()])
    index = StringField('Index', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    statement = TextAreaField('Statement', validators=[DataRequired()])

class SubmitForm(Form):
    """Form for solution submission."""
    language = SelectField('Language', choices = [
        ('Python 3.5.1', 'Python 3.5.1'),
        ('GNU G++11 5.1.0', 'GNU G++11 5.1.0'),
        ('Java 1.8.0_66', 'Java 1.8.0_66')
    ])
    code = TextAreaField('Code', validators=[DataRequired()])

class LoginForm(Form):
    """Form for logging in."""
    username = StringField('Username', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        """Overrides validation to check password."""
        if not Form.validate(self):
            return False
        user = User.query.filter_by(
            username=self.username.data,
            password=self.password.data
        ).first()
        if not user:
            return False
        self.user = user
        return True

class RegistrationForm(Form):
    """Form for registration."""
    username = StringField('Username', [DataRequired(), Length(max=50)])
    password = PasswordField('Password', [DataRequired(), Length(max=255)])
    email = StringField('Email', [DataRequired(), Length(max=255)])
    first_name = StringField('First Name', [DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', [DataRequired(), Length(max=100)])

    def validate(self):
        """Overrides validation to check for uniqueness."""
        if not Form.validate(self):
            return False
        if User.query.filter_by(username=self.username.data).count():
            return False
        if User.query.filter_by(username=self.email.data).count():
            return False
        return True

def get_callback(submission_id, user_id):
    """Curries update with submission ID and user ID."""
    def update(cf_id, result):
        """Updates submission with judge results."""
        submission = Submission.query.get(submission_id)
        submission.cf_id = cf_id
        submission.verdict = result[0]
        submission.runtime = result[1]
        submission.memory = result[2]
        db.session.commit()
        if submission.verdict == 'OK':
            user = User.query.get(user_id)
            user.solves.append(submission.problem)
            db.session.commit()
    return update

@app.route('/')
def index():
    """Index page handler."""
    problems = Problem.query.all()
    solves = {}
    if not current_user.is_anonymous:
        solves = dict.fromkeys(current_user.solves.all())
    return render_template('index.html', problems=problems, solves=solves)

@app.route('/status')
def status():
    """Submission status page handler."""
    submissions = Submission.query.all()
    return render_template('status.html', submissions=submissions)

@app.route('/add', methods=['GET', 'POST'])
def add():
    """Handler for adding new problems."""
    form = ProblemForm()
    if form.validate_on_submit():
        url = form.url.data
        index = form.index.data
        title = form.title.data
        statement = form.statement.data
        db.session.add(Problem(url, index, title, statement))
        db.session.commit()
        return redirect('/')
    return render_template('add.html', form=form)

@app.route('/problem/<int:problem_id>')
def view(problem_id):
    """Handler for viewing problem statement."""
    problem = Problem.query.get(problem_id)
    if not problem:
        abort(404)
    return render_template('problem.html', problem=problem)

@app.route('/problem/<int:problem_id>/submit', methods=['GET', 'POST'])
@login_required
def submit(problem_id):
    """Handler for submitting to a given problem."""
    problem = Problem.query.get(problem_id)
    if not problem:
        abort(404)
    form = SubmitForm()
    if form.validate_on_submit():
        language = form.language.data
        code = form.code.data
        submission = Submission(language, code, problem, current_user)
        db.session.add(submission)
        db.session.commit()
        cf_data = (problem.url, problem.index, language, code)
        charon.submit(cf_data, get_callback(submission.id, current_user.id))
        return redirect('/status')
    return render_template('submit.html', problem=problem, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handler for logging in."""
    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user)
        return redirect('/')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handler for registration."""
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            form.username.data,
            form.password.data,
            form.email.data,
            form.first_name.data,
            form.last_name.data
        )
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    """Handler for logging out."""
    logout_user()
    return redirect('/')

if __name__ == "__main__":
    db.create_all()
    charon = Charon()
    app.run(debug=True)
