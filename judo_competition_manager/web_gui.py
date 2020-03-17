from flask import Flask

from judo_competition_manager.models import Group
from judo_competition_manager.database import init_db, db_session

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello, World!"

@app.route('/group/<int:group_id>')
def group_overview(group_id):
    g = Group.query.filter(Group.id == group_id).first()
    print(g)
    return str(g)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
