from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Table

# define connectors
engine = create_engine("sqlite:///configuration.db", echo=False)
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
    nationality = Column(String)

    groups = relationship("GroupCompetitorAssociation", back_populates="competitor")

    def __repr__(self):
        return "<Competitor: {0} {1} ({2})>".format(self.firstname, self.name, self.club.name)

class Age(Base):
    __tablename__ = "age_categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age_min = Column(Integer)
    age_max = Column(Integer)

    def __repr__(self):
        return "<Age: {0}>".format(self.name)

class Gender(Base):
    __tablename__ = "gender_categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    name_long = Column(String)

    def __repr__(self):
        return "<Gender: {0}>".format(self.name)
    
class Weight(Base):
    __tablename__ = "weight_categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    weight_min = Column(Float)
    weight_max = Column(Float)
    tolerance = Column(Float)
    weight_collection_id = Column(Integer, ForeignKey("weight_collections.id"))
    weight_collection = relationship("WeightCollection", back_populates="weights")

    def __repr__(self):
        return "<Weight: {0}>".format(self.name)

class WeightCollection(Base):
    __tablename__ = "weight_collections"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    weights = relationship("Weight", back_populates="weight_collection")

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

    def __repr__(self):
        return "<Mode: {0}>".format(self.name)

class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True)
    weight = Column(Integer, ForeignKey("weight_categories.id"))
    gender = Column(Integer, ForeignKey("gender_categories.id"))
    age = Column(Integer, ForeignKey("age_categories.id"))
    mode = Column(Integer, ForeignKey("modes.id"))

    competitors = relationship("GroupCompetitorAssociation", back_populates="group")
    fights = relationship("Fight")
    results = relationship("Result")

    def __repr__(self):
        return "<Group {0}: {1} {2} {3}>".format(self.id, self.gender.name, self.age.name, self.weight.name)

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
    
### populate tables

# create the table
Base.metadata.create_all(engine)

# create session
Session = sessionmaker(bind=engine)
session = Session()

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

# make groups
groups = []
_groups = [[u18,      female, ijf_weights_female],
           [adults,   female, ijf_weights_female],
           [adults,   male,   ijf_weights_male],
           [adults30, male,   ijf_weights_male]]

for age, gender, weight_collection in _groups:
    print(age, gender, weight_collection)
    for weight_cat_id in weight_collection.weights:
        # HERE IS AN ERROR, no weights within weight_collection ??? 
        groups.append(Group(age=age.id, weight=weight_cat_id, gender=gender.id))
        print(groups)

session.add_all(groups)

session.commit()