from flask import Flask, render_template, request

from judo_competition_manager.models import Group
from judo_competition_manager.database import init_db, db_session

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello, World!"

@app.route('/group/<int:group_id>', methods=["GET", "POST"])
def group_overview(group_id):
    g = Group.query.filter(Group.id == group_id).first()

    # change the winner
    if request.method == "POST":
        tmp = request.form["winner_select"]
        fight_id, winner_id = tmp.split(".")
        g.load_mode_class(g.mode, db_session)
        g.mode_class.set_winner(fight_id, winner_id, 1, 10, local_ids=False)

    # always return the group overview
    return render_template("group_overview.html", g=g)
    

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
