import os
import server.database as db
from forecast.tools.api import GfcApi
from methods.random_predictor import RandomPredictor

gfc_creds = dict(
    token=os.environ['GFC_TOKEN'],
    server='https://api.iarpagfchallenge.com'
)

api = GfcApi(gfc_creds['token'], gfc_creds['server'])

methods = [RandomPredictor()]  # TODO: add more methods.


def get_question_ids(session):
    query = session.query(db.Questions.question_id).distinct()
    return [x[0] for x in list(query)]


def log(session, question_id, method_name, preds):
    session.add_all([db.OurPredictions(
        question_id=question_id,
        answer_id=p['answer_id'],
        method_name=method_name,
        forecasted_probability=p['value']
    ) for p in preds])
    session.commit()


def submit_all(session, question_ids):
    for qid in question_ids:
        for method in methods:
            print 'Submitting to question', qid, 'using method', method.name
            preds = method.predict(session, qid)
            response = api.submit_forecast(qid, method.name, preds)
            if 'errors' not in response:
                print 'Success'
                log(session, qid, method.name, preds)
            else:
                print response
            print


def main():
    session = db.create_session()
    question_ids = get_question_ids(session)
    submit_all(session, question_ids)
    session.close()


if __name__ == '__main__':
    main()
