from flask import Flask, render_template
from flask import make_response, request, abort
from flask import jsonify

from ..db.models import Tournament, Club, Competitor, Age, Gender, Weight
from ..db.models import Group, Fight, GroupCompetitorAssociation, Mode, Result
from ..db.database import init_db, db_session, and_

import json

app = Flask(__name__)

# utility function to change the name of a function to something that is unique to flask
def rename(newname):
    def decorator(f):
        f.__name__ = newname
        return f
    return decorator

# define some common actions (show, show_all, add, remove, change)
def define_showall(cls):
    @app.route("/api/" + cls.__name__.lower(), methods=["GET"])
    @rename(cls.__name__.lower() + "_showall")
    def func():
        members = cls.query.all()
        members_dict = {m.id: m.serialize() for m in members}
        return jsonify({cls.__name__.lower() + 's': members_dict})
    return func

def define_show(cls):
    @app.route("/api/" + cls.__name__.lower() + "/<int:cls_id>", methods=["GET"])
    @rename(cls.__name__.lower() + "_show")
    def func(cls_id):
        member = cls.query.filter(cls.id == cls_id).first()
        try:
            member_dict = member.serialize()
            return jsonify(member_dict)
        except AttributeError:
            abort(404)
    return func

def define_add(cls):
    @app.route("/api/" + cls.__name__.lower(), methods=["POST"])
    @rename(cls.__name__.lower() + "_add")
    def func():
        props = {key: request.form.get(key) for key in request.form}
        new_member = cls(*props)
        db_session.add(new_member)
        db_session.commit()
    return func

def define_remove(cls):
    @app.route("/api/" + cls.__name__.lower() + "/<int:cls_id>", methods=["DELETE"])
    @rename(cls.__name__.lower() + "_remove")
    def func(cls_id):
        member = cls.query.filter(cls.id == cls_id).first()
        db_session.delete(member)
        db_session.commit()
    return func

def define_change(cls):
    @app.route("/api/" + cls.__name__.lower() + "/<int:cls_id>", methods=["PUT"])
    @rename(cls.__name__.lower() + "_change")
    def func(cls_id):
        member = cls.query.filter(cls.id == cls_id).first()
        props = {key: request.form.get(key) for key in request.form}
        for key, val in props:
            setattr(member, key, val)
        db_session.commit()
    return func

# register these actions for most of the db-models
funcs = []
for cls in [Tournament, Club, Competitor, Age, Gender, Weight, Group, Fight, Mode, Result]:
    funcs.append(define_show(cls))
    funcs.append(define_showall(cls))
    funcs.append(define_add(cls))
    funcs.append(define_remove(cls))
    funcs.append(define_change(cls))

# add some more specific actions 
@app.route('/api/tournament/<int:tournament_id>/groups', methods=["GET"])
def tournamenet_show_groups(tournament_id):
    # get all groups belonging to tournament and jsonify
    groups = Group.query.filter(Group.tournament_id == tournament_id).all()
    result = {"groups": [g.id for g in groups]}
    return jsonify(result)

def group_add_competitor():
    pass

def group_remove_competitor():
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

@app.route('/api/query', methods=["POST"])
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


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
