from database_definitions import Fight
from sqlalchemy import and_

class ModeTemplate():

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
        fight = self.session.query(Fight).filter(and_(Fight.group==self.group, Fight.local_id==local_fight_id)).first()
        fight.winner = local_competitor_id
        fight.winner_points = points
        fight.winner_subpoints = subpoints
        self.session.commit()

    def _fights(self):
        raise NotImplementedError()

    def evaluate_group_result(self):
        raise NotImplementedError()


class ko_full_repechage(ModeTemplate):

    def _fights(self):
        
        fights = []
        fights.append(Fight(local_id = 0, competitor_1 = 0, competitor_2 = 1, group = self.group))
        fights.append(Fight(local_id = 1, competitor_1 = 2, competitor_2 = 3, group = self.group))
        fights.append(Fight(local_id = 2, competitor_1 = None, competitor_2 = None, group = self.group))
        fights.append(Fight(local_id = 3, competitor_1 = None, competitor_2 = None, group = self.group))

        return fights

    def evaluate_group_result(self):
        pass