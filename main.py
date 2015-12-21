import datetime
from flask import *
from flask_sqlalchemy import SQLAlchemy
from charon import Charon

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/charon.db'
db = SQLAlchemy(app)

class Problem(db.Model):
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
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String)
    code = db.Column(db.String)
    date = db.Column(db.DateTime)
    verdict = db.Column(db.String)
    time = db.Column(db.String)
    memory = db.Column(db.String)
    cf_id = db.Column(db.String)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'))
    problem = db.relationship(
        'Problem', backref=db.backref('submissions', lazy='dynamic'))

    def __init__(self, language, code, problem):
        self.language = language
        self.code = code
        self.date = datetime.datetime.now()
        self.verdict = 'WAITING'
        self.problem = problem

def update(submission_id, cf_id, result):
    submission = Submission.query.get(submission_id)
    submission.cf_id = cf_id
    submission.verdict = result[0]
    submission.time = result[1]
    submission.memory = result[2]
    db.session.commit()

def curry_update(submission_id):
    def curried(cf_id, result):
        return update(submission_id, cf_id, result)
    return curried

@app.route('/')
def index():
    problems = Problem.query.all()
    return render_template('index.html', problems=problems)

@app.route('/status')
def status():
    submissions = Submission.query.all()
    return render_template('status.html', submissions=submissions)

@app.route('/problem/<int:problem_id>')
def view(problem_id):
    problem = Problem.query.get(problem_id)
    return render_template('problem.html', problem=problem)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        return render_template('add.html')
    else:
        url = request.form['url']
        index = request.form['index']
        title = request.form['title']
        statement = request.form['statement']
        db.session.add(Problem(url, index, title, statement))
        db.session.commit()
        return redirect('/')

@app.route('/problem/<int:problem_id>/submit', methods=['GET', 'POST'])
def submit(problem_id):
    global charon
    if request.method == 'GET':
        problem = Problem.query.get(problem_id)
        return render_template('submit.html', problem=problem)
    else:
        language = request.form['language']
        code = request.form['code']
        problem = Problem.query.get(problem_id)
        submission = Submission(language, code, problem)
        db.session.add(submission)
        db.session.commit()
        callback = curry_update(submission.id)
        charon.submit(problem.url, problem.index, language, code, callback)
        return redirect('/status')

if __name__ == "__main__":
    charon = Charon()
    app.run()
