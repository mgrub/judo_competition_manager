from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import *

import random
import string
import os

def load_or_create_database(db_name="configuration.db"):

    db_already_existing = os.path.exists(db_name)

    # define connectors
    engine = create_engine("sqlite:///configuration.db", echo=False)
    Base.metadata.create_all(engine)

    # create session
    Session = sessionmaker(bind=engine)
    session = Session()

    if db_already_existing:
        groups = session.query(Group).all()

        for g in groups:
            g.load_mode_class(g.mode, session)

    else:  # populate tables
        # add and update objects
        male = Gender(name="m", name_long="male")
        female = Gender(name="f", name_long="female")

        u18 = Age(name="u18", age_min=14, age_max=17)
        adults = Age(name="open", age_min=16, age_max=None)
        adults30 = Age(name="+30", age_min=30, age_max=None)

        ijf_weights_male = WeightCollection(name="IJF male")
        ijf_weights_female = WeightCollection(name="IJF female")

        session.add_all([male, female])
        session.add_all([u18, adults, adults30])
        session.add_all([ijf_weights_male, ijf_weights_female])
        session.commit()

        weights = []
        weights.append(Weight(name="- 60 kg",  weight_min=None,  weight_max=60.0,  tolerance=0.1, weight_collection=ijf_weights_male.id))
        weights.append(Weight(name="- 66 kg",  weight_min=60.0,  weight_max=66.0,  tolerance=0.1, weight_collection=ijf_weights_male.id))
        weights.append(Weight(name="- 73 kg",  weight_min=66.0,  weight_max=73.0,  tolerance=0.1, weight_collection=ijf_weights_male.id))
        weights.append(Weight(name="- 81 kg",  weight_min=73.0,  weight_max=81.0,  tolerance=0.1, weight_collection=ijf_weights_male.id))
        weights.append(Weight(name="- 90 kg",  weight_min=81.0,  weight_max=90.0,  tolerance=0.1, weight_collection=ijf_weights_male.id))
        weights.append(Weight(name="- 100 kg", weight_min=90.0,  weight_max=100.0, tolerance=0.1, weight_collection=ijf_weights_male.id))
        weights.append(Weight(name="+ 100 kg", weight_min=100.0, weight_max=None,  tolerance=0.1, weight_collection=ijf_weights_male.id))

        weights.append(Weight(name="- 48 kg", weight_min=None, weight_max=48.0, tolerance=0.1, weight_collection=ijf_weights_female.id))
        weights.append(Weight(name="- 52 kg", weight_min=48.0, weight_max=52.0, tolerance=0.1, weight_collection=ijf_weights_female.id))
        weights.append(Weight(name="- 57 kg", weight_min=52.0, weight_max=57.0, tolerance=0.1, weight_collection=ijf_weights_female.id))
        weights.append(Weight(name="- 63 kg", weight_min=57.0, weight_max=63.0, tolerance=0.1, weight_collection=ijf_weights_female.id))
        weights.append(Weight(name="- 70 kg", weight_min=63.0, weight_max=70.0, tolerance=0.1, weight_collection=ijf_weights_female.id))
        weights.append(Weight(name="- 78 kg", weight_min=70.0, weight_max=78.0, tolerance=0.1, weight_collection=ijf_weights_female.id))
        weights.append(Weight(name="+ 78 kg", weight_min=78.0, weight_max=None, tolerance=0.1, weight_collection=ijf_weights_female.id))

        session.add_all(weights)
        session.commit()

        mc = ModeCollection()
        session.add(mc)
        session.commit()

        modes = []
        modes.append(Mode(name="pool_5", name_long="KO Full Repechage", competitors_min=1, competitors_max=5, mode_collection=mc.id))
        modes.append(Mode(name="ko_full_repechage_8", name_long="KO Full Repechage", competitors_min=6, competitors_max=8, mode_collection=mc.id))
        modes.append(Mode(name="ko_full_repechage_16", name_long="KO Full Repechage", competitors_min=9, competitors_max=16, mode_collection=mc.id))
        session.add_all(modes)
        session.commit()

        # make tournament
        masters2020 = Tournament(name="Luftfahrt Masters", name_long="International Luftfahrt Masters 2020", location="Merlitzhalle", date="28th November 2020", host="SV Luftfahrt Berlin e.V.")
        session.add(masters2020)
        session.commit()

        # make groups
        groups = []
        _groups = [[u18,      female, ijf_weights_female],
                [adults,   female, ijf_weights_female],
                [adults,   male,   ijf_weights_male],
                [adults30, male,   ijf_weights_male]]

        for age, gender, weight_collection in _groups:
            print(age, gender, weight_collection)
            for weight in weight_collection.weights:
                groups.append(Group(age=age, weight=weight, gender=gender, tournament=masters2020))

        session.add_all(groups)
        session.commit()

        def random_string(length, charset = string.ascii_uppercase):
            return ''.join(random.choices(charset, k=length))

        # generate some random clubs
        clubs = []
        for n in range(10):
            clubname = random_string(9)
            clubs.append(Club(name=clubname))
        session.add_all(clubs)
        session.commit()

        # generate some random fighters
        competitors = []
        for n in range(200):
            name = random_string(6)
            firstname = random_string(3)
            club = random.choice(clubs)
            competitors.append(Competitor(name=name, firstname=firstname, club=club))
        session.add_all(competitors)
        session.commit()

        # add those fighters to random groups
        for c in competitors:
            g = random.choice(groups)
            gcr = GroupCompetitorAssociation(group=g, competitor=c)
            c.groups.append(gcr)
        session.commit()

        # draw and mode assignment
        for g in groups:
            g.set_mode(mc, session)
            g.load_mode_class(g.mode, session)
            g.mode_class.draw_lots()
            g.mode_class.init_fights()

    return session, groups

session, groups = load_or_create_database()


set_random_winner = False
calc_results = True

for g in groups:
    for f in g.fights:
        if set_random_winner:
            competitors = [f.competitor_1, f.competitor_2]
            if isinstance(competitors[0], Competitor) and isinstance(competitors[1], Competitor):
                winner = random.choice(competitors)
            elif competitors[0] == None:
                winner = competitors[1]
            else:
                winner = competitors[0]

            f.winner = winner
            f.winner_points = 1
            f.winner_subpoints = random.choice([1,7,7,10,10,10])
            session.commit()

            g.mode_class.propagate_fight_outcome(f.local_id)

    if calc_results:
        g.mode_class.evaluate_group_result()