import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Boolean, REAL, DateTime

db_args = dict(
    user=os.environ['GFC_USER'],
    password=os.environ['GFC_PASSWORD'],
    host=os.environ['GFC_HOST'],
    db=os.environ['GFC_DB'],
    port=os.environ['GFC_PORT']
)

engine = create_engine(
    'postgresql://%(user)s:%(password)s@%(host)s:%(port)s/%(db)s' % db_args)

Base = declarative_base()


def create_session():
    Session = sessionmaker(bind=engine)
    return Session()


class Questions(Base):

    __tablename__ = 'questions'

    question_id = Column(Integer, primary_key=True)
    name = Column(String)
    ends_at = Column(DateTime)
    description = Column(String)
    topic = Column(String)
    domain = Column(String)
    country = Column(String)
    generation_method = Column(String)


class Answers(Base):

    __tablename__ = 'answers'

    answer_id = Column(Integer, primary_key=True)
    question_id = Column(Integer, nullable=False)
    name = Column(String)
    is_correct = Column(Boolean)


class Predictions(Base):

    __tablename__ = 'predictions'

    prediction_id = Column(Integer, primary_key=True)
    question_id = Column(Integer, nullable=False)
    answer_id = Column(Integer, nullable=False)
    user_id = Column(String, nullable=False)
    forecasted_probability = Column(REAL, nullable=False)
    rationale = Column(String)
    submitted_at = Column(DateTime)


class OurPredictions(Base):

    __tablename__ = 'our_predictions'

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, nullable=False)
    answer_id = Column(Integer, nullable=False)
    method_name = Column(String)
    forecasted_probability = Column(REAL)
    submitted_at = Column(DateTime)
