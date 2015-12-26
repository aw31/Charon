"""Module for Flask handlers."""
from functools import wraps
from flask import Blueprint, abort, redirect, render_template, request
from flask.ext.login import login_required, login_user, logout_user, current_user
from app import db
from app.forms import ProblemForm, SubmitForm, LoginForm, RegistrationForm
from app.models import User, Problem, Submission

views = Blueprint('views', __name__)

def admin_required(f):
    """Decorator for views that require admin privileges."""
    @wraps(f)
    def inner(*args, **kwargs):
        if not current_user.is_admin:
            return redirect('/login')
        return f(*args, **kwargs)
    return inner

def get_callback(submission_id, user_id):
    """Curries update with submission ID and user ID."""
    def update(cf_id, result):
        """Updates submission with views results."""
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

@views.route('/')
def index():
    """Index page handler."""
    problems = Problem.query.all()
    solves = {}
    if not current_user.is_anonymous:
        solves = dict.fromkeys(current_user.solves.all())
    return render_template('index.html', problems=problems, solves=solves)

@views.route('/status')
@login_required
def status():
    """Submission status page handler."""
    submissions = reversed(Submission.query.all())
    return render_template('status.html', submissions=submissions)

@views.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
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

@views.route('/problem/<int:problem_id>')
def view(problem_id):
    """Handler for viewing problem statement."""
    problem = Problem.query.get(problem_id)
    if not problem:
        abort(404)
    return render_template('problem.html', problem=problem)

@views.route('/problem/<int:problem_id>/submit', methods=['GET', 'POST'])
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

@views.route('/problem/<int:problem_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(problem_id):
    """Handler for editing existing problems."""
    problem = Problem.query.get(problem_id)
    if not problem:
        abort(404)
    form = ProblemForm()
    if request.method == 'GET':
        form.url.data = problem.url
        form.index.data = problem.index
        form.title.data = problem.title
        form.statement.data = problem.statement
    if form.validate_on_submit():
        problem.url = form.url.data
        problem.index = form.index.data
        problem.title = form.title.data
        problem.statement = form.statement.data
        db.session.commit()
        return redirect('/')
    return render_template('add.html', form=form)

@views.route('/login', methods=['GET', 'POST'])
def login():
    """Handler for logging in."""
    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user)
        return redirect('/')
    return render_template('login.html', form=form)

@views.route('/register', methods=['GET', 'POST'])
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
        # make first user an admin
        if not User.query.count():
            user.is_admin = True
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    return render_template('register.html', form=form)

@views.route('/logout')
def logout():
    """Handler for logging out."""
    logout_user()
    return redirect('/')
