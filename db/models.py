from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Table
from .database import Base, Serializer
import importlib

class GroupCompetitorAssociation(Base, Serializer):
    __tablename__ = "group_competitor_associations"
    
    group_id = Column(Integer, ForeignKey('groups.id'), primary_key=True)
    group = relationship("Group", back_populates="competitors")
    
    competitor_id = Column(Integer, ForeignKey('competitors.id'), primary_key=True)
    competitor = relationship("Competitor", back_populates="groups")

    local_lot = Column(Integer)

class Club(Base, Serializer):
    __tablename__ = "clubs"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    name_long = Column(String)
    country = Column(String)

class Competitor(Base, Serializer):
    __tablename__ = "competitors"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    firstname = Column(String)

    club_id = Column(Integer, ForeignKey("clubs.id"))
    club = relationship("Club")

    year_of_birth = Column(Integer)
    
    gender_id = Column(Integer, ForeignKey("genders.id"))
    gender = relationship("Gender")

    weight = Column(Float)
    nationality = Column(String)
    comment = Column(String)

    groups = relationship("GroupCompetitorAssociation", back_populates="competitor")

    def __repr__(self):
        return "Competitor: {0} {1} ({2})".format(self.firstname, self.name, self.club.name)

class Age(Base, Serializer):
    __tablename__ = "ages"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age_min = Column(Integer)
    age_max = Column(Integer)

    def __repr__(self):
        return "Age: {0}".format(self.name)

class Gender(Base, Serializer):
    __tablename__ = "genders"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    name_long = Column(String)

    def __repr__(self):
        return "Gender: {0}".format(self.name)
    
class Weight(Base, Serializer):
    __tablename__ = "weights"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    weight_min = Column(Float)
    weight_max = Column(Float)
    tolerance = Column(Float)
    weight_collection = Column(Integer, ForeignKey("weight_collections.id"))

    def __repr__(self):
        return "Weight: {0}".format(self.name)

class WeightCollection(Base, Serializer):
    __tablename__ = "weight_collections"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    weights = relationship("Weight")

    def __repr__(self):
        return "WeightCollection: {0} ({1})".format(self.name, "|".join([w.name for w in self.weights]))

class Mode(Base, Serializer):
    __tablename__ = "modes"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    name_long = Column(String)
    competitors_min = Column(Integer)
    competitors_max = Column(Integer)
    template = Column(String)

    mode_collection = Column(Integer, ForeignKey("mode_collections.id"))

    def __repr__(self):
        return "Mode: {0}".format(self.name)

class ModeCollection(Base, Serializer):
    __tablename__ = "mode_collections"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    modes = relationship("Mode")

    def __repr__(self):
        return "ModeCollection: {0} ({1})".format(self.name, "|".join([m.name for m in self.modes]))

class Group(Base, Serializer):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True)

    weight_id = Column(Integer, ForeignKey("weights.id"))
    weight = relationship("Weight")

    gender_id = Column(Integer, ForeignKey("genders.id"))
    gender = relationship("Gender")
    
    age_id = Column(Integer, ForeignKey("ages.id"))
    age = relationship("Age")
    
    mode_id = Column(Integer, ForeignKey("modes.id"))
    mode = relationship("Mode")

    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    tournament = relationship("Tournament")

    competitors = relationship("GroupCompetitorAssociation", back_populates="group")
    fights = relationship("Fight")
    results = relationship("Result")

    def __repr__(self):
        return "Group {0}: {1} | {2} | {3} | {4}".format(self.id, self.gender, self.age, self.weight, self.mode)

    def set_mode(self, mode_collection, session):
        n_comp = len(self.competitors)
        for mode in mode_collection.modes:
            if mode.competitors_min <= n_comp and n_comp <= mode.competitors_max:
                self.mode = mode
                session.commit()
    
    def load_mode_class(self, mode, session):
        module = importlib.import_module("judo_competition_manager.modes")
        self.mode_class = getattr(module, mode.name)(session, self)

class Fight(Base, Serializer):
    __tablename__ = "fights"
    
    id = Column(Integer, primary_key=True)
    local_id = Column(Integer)

    competitor_1_id = Column(Integer, ForeignKey('competitors.id'))
    competitor_1 = relationship("Competitor", foreign_keys=[competitor_1_id])

    competitor_2_id = Column(Integer, ForeignKey('competitors.id'))
    competitor_2 = relationship("Competitor", foreign_keys=[competitor_2_id])

    winner_id = Column(Integer, ForeignKey('competitors.id'))
    winner = relationship("Competitor", foreign_keys=[winner_id])

    winner_points = Column(Integer)
    winner_subpoints = Column(Integer)

    group_id = Column(Integer, ForeignKey("groups.id"))
    group = relationship("Group")

    def __repr__(self):
        return "Fight('{0}' vs. '{1}', winner: '{2}')".format(self.competitor_1, self.competitor_2, self.winner)

class Result(Base, Serializer):
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True)
    place = Column(Integer)

    competitor_id = Column(Integer, ForeignKey('competitors.id'))
    competitor = relationship("Competitor")

    group_id = Column(Integer, ForeignKey("groups.id"))
    group = relationship("Group")

    def __repr__(self):
        return "Result('{0}' has place '{1}' in '{2}')".format(self.competitor, self.place, self.group)

class Tournament(Base, Serializer):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    name_long = Column(String)
    host = Column(String)
    date = Column(String)
    location = Column(String)
    tatami_count = Column(Integer)
    
    groups = relationship("Group")
    mode_collection = Column(Integer, ForeignKey("mode_collections.id"))
