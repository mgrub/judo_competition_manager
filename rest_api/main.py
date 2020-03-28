from flask import Flask, render_template, request

from judo_competition_manager.models import Group, Fight, Competitor, GroupCompetitorAssociation
from judo_competition_manager.database import init_db, db_session, and_

import json

app = Flask(__name__)

@app.route('/')
def index():
    groups = Group.query.all()
    return render_template("index.html", groups=groups)

@app.route('/group/<int:group_id>', methods=["GET", "POST"])
def group_overview(group_id):

    g = Group.query.filter(Group.id == group_id).first()

    if request.method == "GET":
        return render_template("group_overview.html", g=g)

    else:
        if "action" in request.form:
            action = request.form.get("action")

            if "competitor_id" in request.form:
                c_id = request.form.get("competitor_id")
                c = Competitor.query.filter(Competitor.id == c_id).first()

                # query the corresponing gca-object
                gca = GroupCompetitorAssociation.query.filter(and_(GroupCompetitorAssociation.competitor == c, GroupCompetitorAssociation.group == g)).first()

                if action == "remove" and gca != None:
                    db_session.delete(gca)
                    db_session.commit()
                elif action == "add" and gca == None:
                    gca = GroupCompetitorAssociation(group=g, competitor=c)
                    db_session.add(gca)
                    db_session.commit()
            
            elif action == "list_competitors":
                return render_template("competitor_list.html", g=g)

        else:
            print("No valid/supported group action. Check your arguments")

        return '', 204  # no page

@app.route('/fight/<int:fight_id>/dropdown')
def fight_dropdown(fight_id):
    f = Fight.query.filter(Fight.id == fight_id).first()

    return render_template("fight_dropdown.html", fight=f)

@app.route('/fight/<int:fight_id>/set_winner', methods=["POST"])
def fight_set_winner(fight_id):
    
    f = Fight.query.filter(Fight.id == fight_id).first()
    g = f.group

    # TODO: make consistency/plausability checks
    winner_id = request.form.get("winner_id")
    points = request.form.get("points")
    subpoints = request.form.get("subpoints")

    # set winner
    g.load_mode_class(g.mode, db_session)
    g.mode_class.set_winner(fight_id, winner_id, points, subpoints, local_ids=False)
    
    return '', 204  # no page

@app.route("/competitor/<int:competitor_id>", methods=["POST"])
def competitor(competitor_id):

    if "action" in request.form:
        action = request.form.get("action")

        if action == "add_new":
            name = request.form.get("name")
            firstname = request.form.get("firstname")
            year_of_birth = request.form.get("year_of_birth")
            club_id = request.form.get("club_id")
            gender_id = request.form.get("gender_id")

            c = Competitor(name=name, firstname=firstname, year_of_birth=year_of_birth, club_id=club_id, gender_id=gender_id)
            db_session.add(c)
            db_session.commit()

        elif action == "change":
            c = Competitor.query.filter(Competitor.id == competitor_id).first()

            for key in request.form.keys():
                val = request.form.get(key)
                print(key, val)
                if key in ["name", "firstname", "year_of_birth", "club_id", "gender_id"]:
                    setattr(c, key, val)
            
            db_session.commit()





@app.route('/query', methods=["POST"])
def query():

    if "competitors_matching" in request.form:
        # match all names and firstnames starting with the request search term (ilike -> case insensitive)
        search = request.form.get("competitors_matching") + "%"
        matches_by_name = Competitor.query.filter(Competitor.name.ilike(search)).limit(5).all()
        matches_by_firstname = Competitor.query.filter(Competitor.firstname.ilike(search)).limit(5).all()

        result = {}
        for c in matches_by_name:
            result[c.id] = (c.name, c.firstname, c.club.name, "name_match")

        for c in matches_by_firstname:
            result[c.id] = (c.name, c.firstname, c.club.name, "firstname_match")
        
        return json.dumps(result)
    else:
        return ""

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
