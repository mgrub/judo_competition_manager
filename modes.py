from database_definitions import Fight, Competitor, GroupCompetitorAssociation
from sqlalchemy import and_

class ModeTemplate():

    # general functions, valid for all modes
    def __init__(self, session, group):
        self.session = session
        self.group = group

    def init_fights(self):
        self.session.add_all(self._fights())
        self.session.commit()

    def delete_fights(self):
        for fight in self.group.fights:
            self.session.delete(fight)
        self.session.commit()

    def reset_fights(self):
        self.delete_fights()
        self.init_fights()

    def draw_lots(self):
        pass

    def set_winner(self, local_fight_id, local_competitor_id, points, subpoints):

        # resolve local ids
        fight = self._get_fight_from(local_fight_id)
        competitor = self._get_competitor_from(local_competitor_id)

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

    def _get_fight_from(self, local_fight_id):
        return self.session.query(Fight).filter(and_(Fight.group==self.group, Fight.local_id==local_fight_id)).first()

    def _get_competitor_from(self, local_competitor_id):
        gca = self.session.query(GroupCompetitorAssociation).filter(and_(GroupCompetitorAssociation.group==self.group, GroupCompetitorAssociation.local_lot==local_competitor_id)).first()
        return gca.competitor

    # functions that need to be implemented by the specific modes
    def propagate_fight_outcome(self, local_fight_id):
        raise NotImplementedError()

    def _fights(self):
        raise NotImplementedError()

    def evaluate_group_result(self):
        raise NotImplementedError()


class KoModeTemplate(ModeTemplate):

    # dictionaries defining the different possible K.O. modes
    # need to be set
    fight_topology = {}  # {local_fight_id : (winner_next_fight , loser_next_fight)}   and   winner_next_fight = (<local_id>, <as_competitor>)
    fight_evaluation = {}  # {local_fight_id : winner_has_place}

    def propagate_fight_outcome(self, local_fight_id):
        
        # get fight, winner and loser
        fight = self._get_fight_from(local_fight_id)
        winner = fight.winner
        if winner == fight.competitor_1:
            loser = fight.competitor_2
        else:
            loser = fight.competitor_1

        # look up which fight comes next for winner and loser from dict
        next_fight_winner, next_fight_loser = self.fight_topology[local_fight_id]

        # if there is a next fight for the winner, set as competitor there
        if next_fight_winner:
            next_fight = self._get_fight_from(next_fight_winner["local_id"])
            if next_fight_winner["as_competitor"] == 1:
                next_fight.competitor_1 = winner
            else:
                next_fight.competitor_2 = winner

        # if there is a next fight for the loser, set as competitor there
        if next_fight_loser:
            next_fight = self._get_fight_from(next_fight_loser[0])
            if next_fight_loser[1] == 1:
                next_fight.competitor_1 = loser
            else:
                next_fight.competitor_2 = loser

        # write changes 
        self.session.commit()
    
    def evaluate_group_result(self):
        pass


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

    def _fights(self):
        
        fights = []
        fights.append(Fight(local_id =  0, competitor_1 = 0, competitor_2 = 1, group = self.group))
        fights.append(Fight(local_id =  1, competitor_1 = 2, competitor_2 = 3, group = self.group))
        fights.append(Fight(local_id =  2, competitor_1 = 4, competitor_2 = 5, group = self.group))
        fights.append(Fight(local_id =  3, competitor_1 = 6, competitor_2 = 7, group = self.group))
        fights.append(Fight(local_id =  4, competitor_1 = None, competitor_2 = None, group = self.group))
        fights.append(Fight(local_id =  5, competitor_1 = None, competitor_2 = None, group = self.group))
        fights.append(Fight(local_id =  6, competitor_1 = None, competitor_2 = None, group = self.group))
        fights.append(Fight(local_id =  7, competitor_1 = None, competitor_2 = None, group = self.group))
        fights.append(Fight(local_id =  8, competitor_1 = None, competitor_2 = None, group = self.group))
        fights.append(Fight(local_id =  9, competitor_1 = None, competitor_2 = None, group = self.group))
        fights.append(Fight(local_id = 10, competitor_1 = None, competitor_2 = None, group = self.group))

        return fights
