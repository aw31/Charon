"""Runs Charon and Flask server."""
from charon import Charon
from app import app, db, login_manager
from app.models import User
import app.views as views

@login_manager.user_loader
def load_user(user_id):
    """Returns user for Flask-Login."""
    return User.query.get(int(user_id))

views.charon = Charon(
    app.config['CF_HANDLE'],
    app.config['CF_PASSWORD']
)

db.create_all()

app.register_blueprint(views.views)
app.run()
