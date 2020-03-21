from flask import Flask, render_template, request

from judo_competition_manager.models import Group, Fight
from judo_competition_manager.database import init_db, db_session

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello, World!"

@app.route('/group/<int:group_id>', methods=["GET", "POST"])
def group_overview(group_id):
    g = Group.query.filter(Group.id == group_id).first()

    return render_template("group_overview.html", g=g)

@app.route('/fight/<int:fight_id>/dropdown')
def fight_dropdown(fight_id):
    f = Fight.query.filter(Fight.id == fight_id).first()

    return render_template("fight_dropdown.html", fight=f)

@app.route('/fight/<int:fight_id>/set_winner', methods=["POST"])
def fight_set_winner(fight_id):
    
    f = Fight.query.filter(Fight.id == fight_id).first()
    g = f.group

    for key, val in request.form.items():
        print(key, val)

    # TODO: make consistency/plausability checks
    winner_id = request.form.get("winner_id")
    points = request.form.get("points")
    subpoints = request.form.get("subpoints")

    # set winner
    g.load_mode_class(g.mode, db_session)
    g.mode_class.set_winner(fight_id, winner_id, points, subpoints, local_ids=False)
    
    return '', 204  # no page

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
