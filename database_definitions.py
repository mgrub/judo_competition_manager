from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Table
from sqlalchemy.ext.declarative import declarative_base
import importlib

Base = declarative_base()

class GroupCompetitorAssociation(Base):
    __tablename__ = "group_competitor_associations"
    group_id = Column(Integer, ForeignKey('groups.id'), primary_key=True)
    competitor_id = Column(Integer, ForeignKey('competitors.id'), primary_key=True)
    local_lot = Column(Integer)
    group = relationship("Group", back_populates="competitors")
    competitor = relationship("Competitor", back_populates="groups")

class Club(Base):
    __tablename__ = "clubs"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    name_long = Column(String)
    country = Column(String)

class Competitor(Base):
    __tablename__ = "competitors"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    firstname = Column(String)
    club = Column(Integer, ForeignKey("clubs.id"))
    year_of_birth = Column(Integer)
    gender = Column(Integer, ForeignKey("genders.id"))
    weight = Column(Float)
    nationality = Column(String)
    comment = Column(String)

    groups = relationship("GroupCompetitorAssociation", back_populates="competitor")

    def __repr__(self):
        return "<Competitor: {0} {1} ({2})>".format(self.firstname, self.name, self.club.name)

class Age(Base):
    __tablename__ = "ages"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age_min = Column(Integer)
    age_max = Column(Integer)

    def __repr__(self):
        return "<Age: {0}>".format(self.name)

class Gender(Base):
    __tablename__ = "genders"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    name_long = Column(String)

    def __repr__(self):
        return "<Gender: {0}>".format(self.name)
    
class Weight(Base):
    __tablename__ = "weights"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    weight_min = Column(Float)
    weight_max = Column(Float)
    tolerance = Column(Float)
    weight_collection = Column(Integer, ForeignKey("weight_collections.id"))

    def __repr__(self):
        return "<Weight: {0}>".format(self.name)

class WeightCollection(Base):
    __tablename__ = "weight_collections"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    weights = relationship("Weight")

    def __repr__(self):
        return "<WeightCollection: {0} ({1})>".format(self.name, "|".join([w.name for w in self.weights]))

class Mode(Base):
    __tablename__ = "modes"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    name_long = Column(String)
    competitors_min = Column(Integer)
    competitors_max = Column(Integer)
    template = Column(String)

    mode_collection = Column(Integer, ForeignKey("mode_collections.id"))

    def __repr__(self):
        return "<Mode: {0}>".format(self.name)

class ModeCollection(Base):
    __tablename__ = "mode_collections"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    modes = relationship("Mode")

    def __repr__(self):
        return "<ModeCollection: {0} ({1})>".format(self.name, "|".join([m.name for m in self.modes]))

class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True)
    weight = Column(Integer, ForeignKey("weights.id"))
    gender = Column(Integer, ForeignKey("genders.id"))
    age = Column(Integer, ForeignKey("ages.id"))
    mode = Column(Integer, ForeignKey("modes.id"))

    tournament = Column(Integer, ForeignKey("tournaments.id"))
    competitors = relationship("GroupCompetitorAssociation", back_populates="group")
    fights = relationship("Fight")
    results = relationship("Result")

    def __repr__(self):
        return "<Group {0}: {1} {2} {3}>".format(self.id, self.gender.name, self.age.name, self.weight.name, self.mode.name)

    def set_mode(self, mode_collection):
        n_comp = len(self.competitors)
        for mode in mode_collection:
            if mode.competitors_min <= n_comp and n_comp <= mode.competitors_max:
                module = importlib.import_module("modes")
                self.mode_class = getattr(module, mode)()

class Fight(Base):
    __tablename__ = "fights"
    
    id = Column(Integer, primary_key=True)
    local_id = Column(Integer)
    competitor_1 = Column(Integer, ForeignKey('competitors.id'))
    competitor_2 = Column(Integer, ForeignKey('competitors.id'))
    winner = Column(Integer, ForeignKey('competitors.id'))
    winner_points = Column(Integer)
    winner_subpoints = Column(Integer)
    group = Column(Integer, ForeignKey("groups.id"))
    
    def __repr__(self):
        return "<Fight('{0}' vs. '{1}', winner: '{2}')>".format(self.competitor_1, self.competitor_2, self.winner)
    
class Result(Base):
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True)
    place = Column(Integer)
    fighter = Column(Integer, ForeignKey('competitors.id'))
    group = Column(Integer, ForeignKey("groups.id"))

class Tournament(Base):
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
