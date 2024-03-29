from .models import Fight, Competitor, GroupCompetitorAssociation, Result
from sqlalchemy import and_, func
import random

class ModeTemplate():

    initial_known_fights = {}  # {<local_fight_id> : (competitor_1_local_id, competitor_2_local_id)}

    # general functions, valid for all modes
    def __init__(self, session, group):
        self.session = session
        self.group = group

    def init_fights(self):
        # create fights
        n_fights = self.get_total_number_of_fights()
        fights = []

        # populate fight with competitors, if it is one of the initial known fights
        for local_fight_id in range(n_fights):
            if local_fight_id in self.initial_known_fights:
                c1 = self.get_competitor_from(self.initial_known_fights[local_fight_id][0])
                c2 = self.get_competitor_from(self.initial_known_fights[local_fight_id][1])
                fight = Fight(local_id = local_fight_id, competitor_1 = c1, competitor_2 = c2, group = self.group)
            else:
                fight = Fight(local_id = local_fight_id, competitor_1 = None, competitor_2 = None, group = self.group)
            fights.append(fight)

        # write to session
        self.session.add_all(fights)
        self.session.commit()

    def delete_fights(self):
        for fight in self.group.fights:
            self.session.delete(fight)
        self.session.commit()

    def delete_results(self):
        for result in self.group.results:
            self.session.delete(result)
        self.session.commit()

    def reset_fights(self):
        self.delete_fights()
        self.init_fights()

    def draw_lots(self, manual_draw=None):

        if manual_draw:
            draw = manual_draw
        else:
            k = self.get_number_of_competitors()
            draw = random.sample(range(k), k)
        
        gca = self.session.query(GroupCompetitorAssociation).filter(and_(GroupCompetitorAssociation.group==self.group)).all()

        for entry, local_lot in zip(gca, draw):
            entry.local_lot = local_lot
        
        self.session.commit()

    def set_winner(self, fight_id, competitor_id, points, subpoints, local_ids=True):

        # resolve local/global ids
        fight = self.get_fight_from(fight_id, local_id=local_ids)
        competitor = self.get_competitor_from(competitor_id, local_id=local_ids)

        # set winner
        fight.winner = competitor
        fight.winner_points = points
        fight.winner_subpoints = subpoints

        # write changes
        self.session.commit()

    def update_fights(self):
        fights = self.session.query(Fight).filter(Fight.group==self.group).all()

        for fight in fights:
            if fight.winner != None:
                self.propagate_fight_outcome(fight.local_id)

    def get_fight_from(self, fight_id, local_id=True):
        if local_id:
            return self.session.query(Fight).filter(and_(Fight.group==self.group, Fight.local_id==fight_id)).first()
        else:
            return self.session.query(Fight).filter(Fight.id==fight_id).first()

    def get_winner_of(self, fight):
        return fight.winner
    
    def get_loser_of(self, fight):
        winner = fight.winner
        if winner == fight.competitor_1:
            loser = fight.competitor_2
        else:
            loser = fight.competitor_1
        return loser

    def get_competitor_from(self, competitor_id, local_id=True):
        if local_id:
            gca = self.session.query(GroupCompetitorAssociation).filter(and_(GroupCompetitorAssociation.group==self.group, GroupCompetitorAssociation.local_lot==competitor_id)).first()
            if gca == None:
                return None
            else:
                return gca.competitor
        else:
            return self.session.query(Competitor).filter(Competitor.id==competitor_id).first()

    def get_number_of_competitors(self):
        return len(self.group.competitors)

    def get_total_number_of_fights(self):
        raise NotImplementedError()

    def propagate_fight_outcome(self, local_fight_id):
        raise NotImplementedError()

    def evaluate_group_result(self):
        raise NotImplementedError()

class PoolModeTemplate(ModeTemplate):

    def get_total_number_of_fights(self):
        return len(self.initial_known_fights)

    def propagate_fight_outcome(self, local_fight_id):
        # Because all fights are determined in advance there is no need for propagation of fight outcome.
        # However to avoid the "NotImplementedError" it is necessary to create an empty function.
        pass
    
    def evaluate_group_result(self):
        self.delete_results()

        # check total number of points+subpoints of every fighter 
        competitor_scores = {}

        for gca in self.group.competitors:
            total_points = self.session.query(func.sum(Fight.winner_points)).filter(and_(Fight.group==self.group, Fight.winner==gca.competitor)).first()
            total_subpoints = self.session.query(func.sum(Fight.winner_subpoints)).filter(and_(Fight.group==self.group, Fight.winner==gca.competitor)).first()

            if total_points[0] == None:
                points = 0
            else:
                points = total_points[0]

            if total_subpoints[0] == None:
                subpoints = 0
            else:
                subpoints = total_subpoints[0]

            competitor_scores[gca.competitor] = (points, subpoints)

        # sort by (points, subpoints)
        # competitors with same (total_points, total_subpoints) should have the same place
        scores_sorted = sorted(competitor_scores.values(), key= lambda x: (x[0], x[1]), reverse=True)

        # assign every competitor a place (by the position in the sorted unique scores)
        for competitor, score in competitor_scores.items():
            place = scores_sorted.index(score) + 1
            result = Result(competitor=competitor, place=place, group=self.group)
            self.session.add(result)

        self.session.commit()

class pool_5(PoolModeTemplate):

    initial_known_fights = {
        0 : (3, 4),
        1 : (0, 1),
        2 : (2, 3),
        3 : (4, 0),
        4 : (1, 2),
        5 : (3, 0),
        6 : (2, 4),
        7 : (1, 3),
        8 : (0, 2),
        9 : (4, 1),
    }

class KoModeTemplate(ModeTemplate):

    # dictionaries defining the different possible K.O. modes
    # need to be set
    fight_topology = {}  # {local_fight_id : (winner_next_fight , loser_next_fight)}   and   winner_next_fight = (<local_id>, <as_competitor>)
    fight_evaluation = {}  # {local_fight_id : (winner_has_place, loser_has_place)}
    
    def get_total_number_of_fights(self):
        return len(self.fight_topology)

    def propagate_fight_outcome(self, local_fight_id):
        
        # get fight, winner and loser
        fight = self.get_fight_from(local_fight_id)
        winner = self.get_winner_of(fight)
        loser = self.get_loser_of(fight)

        # look up which fight comes next for winner and loser from dict
        next_fight_winner, next_fight_loser = self.fight_topology[local_fight_id]

        # if there is a next fight for the winner, set as competitor there
        if next_fight_winner:
            next_fight = self.get_fight_from(next_fight_winner[0])
            if next_fight_winner[1] == 1:
                next_fight.competitor_1 = winner
            else:
                next_fight.competitor_2 = winner

        # if there is a next fight for the loser, set as competitor there
        if next_fight_loser:
            next_fight = self.get_fight_from(next_fight_loser[0])
            if next_fight_loser[1] == 1:
                next_fight.competitor_1 = loser
            else:
                next_fight.competitor_2 = loser

        # write changes 
        self.session.commit()
    
    def evaluate_group_result(self):
        
        # delete existing results
        self.delete_results()

        # get results from fight_evaluation-dictionary
        for local_fight_id, (place_winner, place_loser)  in self.fight_evaluation.items():
            # get fight, winner and loser
            fight = self.get_fight_from(local_fight_id)
            winner = self.get_winner_of(fight)
            loser = self.get_loser_of(fight)

            if isinstance(winner, Competitor) and place_winner:
                result = Result(competitor=winner, place=place_winner, group=self.group)
                self.session.add(result)

            if isinstance(loser, Competitor) and place_loser:
                result = Result(competitor=loser, place=place_loser, group=self.group)
                self.session.add(result)
        self.session.commit()

class ko_full_repechage_8(KoModeTemplate):

    fight_topology = {
        # round 1
        0  : (( 6, 1), ( 4, 1)),
        1  : (( 6, 2), ( 4, 2)),
        2  : (( 7, 1), ( 5, 1)),
        3  : (( 7, 2), ( 5, 2)),
        # repechage 1
        4  : (( 8, 1), None),
        5  : (( 9, 1), None),
        # semi finals
        6  : ((10, 1), ( 9, 2)),
        7  : ((10, 2), ( 8, 2)),
        # bronze medal
        8  : (None, None),
        9  : (None, None),
        # final
        10 : (None, None),
    }

    initial_known_fights = {
        0: (0, 1),
        1: (2, 3),
        2: (4, 5),
        3: (6, 7),
    }

    fight_evaluation = {
        8  : (3, 5), 
        9  : (3, 5),
        10 : (1, 2),
    }

class ko_full_repechage_16(KoModeTemplate):

    fight_topology = {
        # round 1
        0  : (( 8, 1), (12, 1)),
        1  : (( 8, 2), (12, 2)),
        2  : (( 9, 1), (13, 1)),
        3  : (( 9, 2), (13, 2)),
        4  : ((10, 1), (14, 1)),
        5  : ((10, 2), (14, 2)),
        6  : ((11, 1), (15, 1)),
        7  : ((11, 2), (15, 2)),
        # round 2
        8  : ((20, 1), (18, 2)),
        9  : ((20, 2), (19, 2)),
        10 : ((21, 1), (16, 2)),
        11 : ((21, 2), (17, 2)),
        # repechage 1
        12 : ((16, 1), None),
        13 : ((17, 1), None),
        14 : ((18, 1), None),
        15 : ((19, 1), None),
        16 : ((22, 1), None),
        17 : ((22, 2), None),
        18 : ((23, 1), None),
        19 : ((23, 2), None),
        # semi finals
        20 : ((26, 1), ( 9, 2)),
        21 : ((26, 2), ( 8, 2)),
        # repechage 2
        22 : ((24, 1), None),
        23 : ((25, 1), None),
        # bronze medal
        24 : (None, None),
        25 : (None, None),
        # final
        26 : (None, None),
    }

    initial_known_fights = {
        0: (0, 1),
        1: (2, 3),
        2: (4, 5),
        3: (6, 7),
        4: (8, 9),
        5: (10, 11),
        6: (12, 13),
        7: (14, 15),
    }

    fight_evaluation = {
        24 : (3, 5), 
        25 : (3, 5),
        26 : (1, 2),
    }