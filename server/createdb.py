import os
import dateutil.parser
import server.database as db
from forecast.tools.api import GfcApi

gfc_creds = dict(
    token=os.environ['GFC_TOKEN'],
    server='https://api.iarpagfchallenge.com'
)

api = GfcApi(gfc_creds['token'], gfc_creds['server'])


def clear_table(session, table):
    session.query(table).delete()
    session.commit()


def get_time(time_str):
    return dateutil.parser.parse(time_str)


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


def create_questions_table(session):
    clear_table(session, db.Questions)
    questions = api.get_questions()
    session.add_all([db.Questions(
        question_id=q['id'],
        name=q.get('name', None),
        ends_at=get_time(q['ends_at']),
        description=q.get('description', None),
        topic=get_topic(q),
        domain=get_domain(q),
        country=get_country(q),
        generation_method=get_generation_method(q)
    ) for q in questions])
    session.commit()


def create_answers_table(session):
    clear_table(session, db.Answers)
    questions = api.get_questions()
    for q in questions:
        session.add_all([db.Answers(
            answer_id=a['id'],
            question_id=q['id'],
            name=a.get('name', None)
        ) for a in q['answers']])
    session.commit()


def create_predictions_table(session):
    clear_table(session, db.Predictions)
    predictions = api.get_human_forecasts()
    for p in predictions:
        session.add_all([db.Predictions(
            prediction_id=a['id'],
            question_id=p['question_id'],
            answer_id=a['answer_id'],
            user_id=a['membership_guid'],
            forecasted_probability=a['forecasted_probability'],
            rationale=p.get('rationale', None),
            submitted_at=dateutil.parser.parse(p['updated_at'])
        ) for a in p['predictions']])
    session.commit()


def main():
    session = db.create_session()
    create_questions_table(session)
    create_answers_table(session)
    create_predictions_table(session)
    session.close()


if __name__ == '__main__':
    main()
