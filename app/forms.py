"""Module for Flask-WTF forms."""
from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length
from app.models import User

class ProblemForm(Form):
    """Form for adding new problems."""
    url = StringField('URL', validators=[DataRequired()])
    index = StringField('Index', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    statement = TextAreaField('Statement', validators=[DataRequired()])

class SubmitForm(Form):
    """Form for solution submission."""
    language = SelectField('Language', choices=[
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
        username = self.username.data
        password = self.password.data
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return False
        self.user = user
        return True

class RegistrationForm(Form):
    """Form for registration."""
    username = StringField('Username', [DataRequired(), Length(max=50)])
    password = PasswordField('Password', [DataRequired(), Length(max=50)])
    email = StringField('Email', [DataRequired(), Length(max=50)])
    first_name = StringField('First Name', [DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', [DataRequired(), Length(max=50)])

    def validate(self):
        """Overrides validation to check for uniqueness."""
        if not Form.validate(self):
            return False
        username = self.username.data
        email = self.email.data
        if User.query.filter_by(username=username).count():
            return False
        if User.query.filter_by(email=email).count():
            return False
        return True
