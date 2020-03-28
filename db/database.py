from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import and_, or_

import json

# define connectors
engine = create_engine("sqlite:///configuration.db", echo=False)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

# use this class to add JSON-export functionality
class Serializer(object):

    def serialize(self):
        # init dict to store values
        d = {}

        # loop over all table-columns
        for col in self.__table__.columns:
            key = col.name
            val = getattr(self, key)
            d[key] = val
        
        return d

    def to_json(self):
        return json.dumps(self.serialize())


def init_db():
    import db.models
    Base.metadata.create_all(bind=engine)
