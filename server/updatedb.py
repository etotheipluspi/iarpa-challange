import os
import dateutil.parser
from datetime import datetime, timedelta
import server.database as db
from forecast.tools.api import GfcApi

COMPETITION_START = datetime(2018, 3, 6)

gfc_creds = dict(
    token=os.environ['GFC_TOKEN'],
    server='https://api.iarpagfchallenge.com'
)

api = GfcApi(gfc_creds['token'], gfc_creds['server'])


def get_time(time_str):
    aware = dateutil.parser.parse(time_str)
    return aware.replace(tzinfo=None)


def get_topic(question):
    metadata = question.get('metadata', None)
    if metadata is None:
        return None
    return metadata.get('Topic', None)


def get_domain(question):
    metadata = question.get('metadata', None)
    if metadata is None:
        return None
    return metadata.get('Domain', None)


def get_country(question):
    metadata = question.get('metadata', None)
    if metadata is None:
        return None
    return metadata.get('Country - Primary', None)


def get_generation_method(question):
    metadata = question.get('metadata', None)
    if metadata is None:
        return None
    return metadata.get('IFP Generation Method', None)


def get_iscorrect(prob):
    return prob if prob in (0, 1) else None


def get_questions(after_time):
    questions = api.get_questions(status='all',
                                  created_after=COMPETITION_START,
                                  updated_after=after_time)
    return questions


def create_questions_table(session, after_time):
    questions = get_questions(after_time)
    for q in questions:
        session.merge(db.Questions(
            question_id=q['id'],
            name=q.get('name', None),
            ends_at=get_time(q['ends_at']),
            description=q.get('description', None),
            topic=get_topic(q),
            domain=get_domain(q),
            country=get_country(q),
            generation_method=get_generation_method(q)))
    session.commit()


def create_answers_table(session, after_time):
    questions = get_questions(after_time)
    for q in questions:
        for a in q['answers']:
            session.merge(db.Answers(
                answer_id=a['id'],
                question_id=q['id'],
                name=a.get('name', None),
                is_correct=get_iscorrect(a['probability'])))
    session.commit()


def create_predictions_table(session, after_time):
    predictions = api.get_human_forecasts(updated_after=after_time)
    for p in predictions:
        for a in p['predictions']:
            session.merge(db.Predictions(
                prediction_id=a['id'],
                question_id=p['question_id'],
                answer_id=a['answer_id'],
                user_id=a['membership_guid'],
                forecasted_probability=a['forecasted_probability'],
                rationale=p.get('rationale', None),
                submitted_at=get_time(p['updated_at'])))
    session.commit()


def updatedb():
    session = db.create_session()
    after_time = datetime.utcnow() - timedelta(days=2)
    create_questions_table(session, after_time)
    create_answers_table(session, after_time)
    create_predictions_table(session, after_time)
    session.close()
