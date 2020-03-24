from flask import Flask, render_template, request

from judo_competition_manager.models import Group, Fight, Competitor, GroupCompetitorAssociation
from judo_competition_manager.database import init_db, db_session, and_

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
                    print("123")
                elif action == "add" and gca == None:
                    gca = GroupCompetitorAssociation(group=g, competitor=c)
                    g.competitors.append(gca)
                    db_session.commit()
            
            elif action == "list_competitors":
                print("ABC")
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

@app.route('/query', methods=["POST"])
def query():
    matching_competitors = []

    if "competitors_matching" in request.form:
        # match all names and firstnames starting with the request search term (ilike -> case insensitive)
        search = request.form.get("competitors_matching") + "%"
        matches_by_name = Competitor.query.filter(Competitor.name.ilike(search)).limit(5).all()
        matches_by_firstname = Competitor.query.filter(Competitor.firstname.ilike(search)).limit(5).all()

        matching_competitors = matches_by_name + matches_by_firstname

        return render_template("competitor_autocomplete.html", list_of_competitors=matching_competitors)
    else:
        return ""

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
