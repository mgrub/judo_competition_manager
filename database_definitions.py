from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Table

# define connectors
engine = create_engine("sqlite:///:memory:", echo=True)
Base = declarative_base()

association_competitor_groups = Table('association', Base.metadata,
    Column('competitor', Integer, ForeignKey('competitors.id')),
    Column('group', Integer, ForeignKey('groups.id')))

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

    groups = relationship("Group", secondary=association_competitor_groups, back_populates="competitors")

class Age(Base):
    __tablename__ = "age_categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age_min = Column(Integer)
    age_max = Column(Integer)

class Gender(Base):
    __tablename__ = "gender_categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    name_long = Column(String)
    
class Weight(Base):
    __tablename__ = "weight_categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    weight_min = Column(Float)
    weight_max = Column(Float)
    tolerance = Column(Float)

class Mode(Base):
    __tablename__ = "modes"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    name_long = Column(String)
    competitors_min = Column(Integer)
    competitors_max = Column(Integer)
    template = Column(String)

class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True)
    weight = Column(Integer, ForeignKey("weight_categories.id"))
    gender = Column(Integer, ForeignKey("gender_categories.id"))
    age = Column(Integer, ForeignKey("age_categories.id"))
    mode = Column(Integer, ForeignKey("modes.id"))

    competitors = relationship("Competitor", secondary=association_competitor_groups, back_populates="groups")
    fights = relationship("Fight")
    results = relationship("Result")

class Fight(Base):
    __tablename__ = "fights"
    
    id = Column(Integer, primary_key=True)
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

w60   = Weight(name="- 60 kg",  weight_min=None,  weight_max=60.0,  tolerance=0.1)
w66   = Weight(name="- 66 kg",  weight_min=60.0,  weight_max=66.0,  tolerance=0.1)
w73   = Weight(name="- 73 kg",  weight_min=66.0,  weight_max=73.0,  tolerance=0.1)
w81   = Weight(name="- 81 kg",  weight_min=73.0,  weight_max=81.0,  tolerance=0.1)
w90   = Weight(name="- 90 kg",  weight_min=81.0,  weight_max=90.0,  tolerance=0.1)
w100  = Weight(name="- 100 kg", weight_min=90.0,  weight_max=100.0, tolerance=0.1)
wp100 = Weight(name="+ 100 kg", weight_min=100.0, weight_max=None,  tolerance=0.1)
w_male = [w60, w66, w73, w81, w90, w100, wp100]

w48  = Weight(name="- 48 kg", weight_min=None, weight_max=48.0, tolerance=0.1)
w52  = Weight(name="- 52 kg", weight_min=48.0, weight_max=52.0, tolerance=0.1)
w57  = Weight(name="- 57 kg", weight_min=52.0, weight_max=57.0, tolerance=0.1)
w63  = Weight(name="- 63 kg", weight_min=57.0, weight_max=63.0, tolerance=0.1)
w70  = Weight(name="- 70 kg", weight_min=63.0, weight_max=70.0, tolerance=0.1)
w78  = Weight(name="- 78 kg", weight_min=70.0, weight_max=78.0, tolerance=0.1)
wp78 = Weight(name="+ 78 kg", weight_min=78.0, weight_max=None, tolerance=0.1)
w_female = [w48, w52, w57, w63, w70, w78, wp78]

# make groups
groups = []
_groups = [[w_female, u18, female],
           [w_female, adults, female],
           [w_male, adults, male],
           [w_male, adults30, male]]

for weight_classes, age, gender in _groups:
    for weight in weight_classes:
        groups.append(Group(age=age, weight=weight, gender=gender, mode=None))

session.add_all([male, female])
session.add_all([u18, adults, adults30])
session.add_all([*w_male, *w_female])
session.add_all(groups)

session.commit()