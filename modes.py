from database_definitions import Fight

class ko_full_repechage():

    def __init__(self, db_session):
        self.session = db_session

    def _fights(self):
        
        fights = []
        fights.append(Fight(local_id = 0, competitor_1 = 0, competitor_2 = 1))
        fights.append(Fight(local_id = 1, competitor_1 = 2, competitor_2 = 3))
        fights.append(Fight(local_id = 2, competitor_1 = None, competitor_2 = None))
        fights.append(Fight(local_id = 3, competitor_1 = None, competitor_2 = None))

        return fights

    def init_fights(self):
        self.fights = self.session.add_all(self._fights())
        print(self.fights)

    def draw_lots(self):
        pass

    def set_winner(self, local_fight_id, local_competitor_id):
        pass

    def update_fights(self):
        pass

    def evaluate_group_result(self):
        pass