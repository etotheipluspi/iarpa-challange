import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, REAL, DateTime

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

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, nullable=False)
    name = Column(String)
    ends_at = Column(DateTime)
    description = Column(String)
    topic = Column(String)
    domain = Column(String)
    country = Column(String)
    generation_method = Column(String)
    correct_answer_id = Column(Integer)


class Answers(Base):

    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, nullable=False)
    answer_id = Column(Integer, nullable=False)
    name = Column(String)


class Predictions(Base):

    __tablename__ = 'predictions'

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, nullable=False)
    answer_id = Column(Integer, nullable=False)
    predictor_id = Column(String, nullable=False)
    forecasted_probability = Column(REAL, nullable=False)
    rationale = Column(String)


class OurPredictions(Base):

    __tablename__ = 'our_predictions'

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, nullable=False)
    answer_id = Column(Integer, nullable=False)
    method_name = Column(String)
    forecasted_probability = Column(REAL)
