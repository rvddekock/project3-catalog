import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


# store user information
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    image = Column(String(250))
    provider = Column(String(25))


# movies Database
class MovieDB(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    movieName = Column(String(250), nullable=False)
    directorName = Column(String(250), nullable=False)
    coverUrl = Column(String(450), nullable=False)
    description = Column(String(), nullable=False)
    category = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # return movie data
        return {
            'id': self.id,
            'name': self.movieName,
            'director': self.directorName,
            'genre': self.category,
            'coverUrl': self.coverUrl,
            'description': self.description
        }

engine = create_engine('sqlite:///MovieCatalog.db')
Base.metadata.create_all(engine)
