"""
SQLAlchemy models matching the schema sketched in README.md:
Users, Artists, Tracks, ListeningHistory, Snapshots.
"""

from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship, declarative_base, sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    spotify_id = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String)
    email = Column(String)

    listening_history = relationship("ListeningHistory", back_populates="user")
    snapshots = relationship("Snapshot", back_populates="user")


class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True)
    spotify_id = Column(String, unique=True, nullable=False, index=True)
    followers = Column(Integer)
    genres = Column(String)  # stored as comma-separated string; consider a join table if you need real filtering

    tracks = relationship("Track", back_populates="artist")


class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True)
    spotify_id = Column(String, unique=True, nullable=False, index=True)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)
    danceability = Column(Float)
    energy = Column(Float)
    tempo = Column(Float)

    artist = relationship("Artist", back_populates="tracks")
    listening_history = relationship("ListeningHistory", back_populates="track")


class ListeningHistory(Base):
    __tablename__ = "listening_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    played_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="listening_history")
    track = relationship("Track", back_populates="listening_history")


class Snapshot(Base):
    """A monthly rollup of a user's listening stats (obscurity/diversity/discovery)."""
    __tablename__ = "snapshots"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    month = Column(String, nullable=False)  # e.g. "2026-07"
    obscurity_score = Column(Float)
    diversity_score = Column(Float)
    discovery_score = Column(Float)

    user = relationship("User", back_populates="snapshots")


def get_engine(db_url="sqlite:///soundscape.db"):
    return create_engine(db_url)


def init_db(engine):
    Base.metadata.create_all(engine)


def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


if __name__ == "__main__":
    # Quick way to create the local sqlite DB file for development.
    engine = get_engine()
    init_db(engine)
    print("Database initialized at soundscape.db")
