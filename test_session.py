import random
from database_connector import DatabaseConnector
from models import Competitor

dbc = DatabaseConnector()
session, groups = dbc.load_or_create_database()

set_random_winner = True
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