import os
import server.database as db
from datetime import datetime
from forecast.tools.api import GfcApi
from methods.random_predictor import RandomPredictor
from methods.median_predictor import MedianPredictor
from methods.median_rationale_predictor import MedianRationalePredictor

gfc_creds = dict(
    token=os.environ['GFC_TOKEN'],
    server='https://api.iarpagfchallenge.com'
)

if 'staging' not in gfc_creds['server']:
    raise Exception('''Are you sure you want to submit to the production server? If so, comment these lines and re-run the submission script.''')

api = GfcApi(gfc_creds['token'], gfc_creds['server'])

methods = [RandomPredictor(),
           MedianPredictor(),
           MedianRationalePredictor()]


def get_active_question_ids(session):
    query = (session.query(db.Questions.question_id)
                    .filter(db.Questions.ends_at > datetime.utcnow())
                    .distinct())
    return [x[0] for x in list(query)]


def log(session, question_id, method_name, preds):
    session.add_all([db.OurPredictions(
        question_id=question_id,
        answer_id=p['answer_id'],
        method_name=method_name,
        forecasted_probability=p['value'],
        submitted_at=datetime.utcnow()
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
    return [m.name for m in methods]


def submit():
    session = db.create_session()
    question_ids = get_active_question_ids(session)
    method_names = submit_all(session, question_ids)
    session.close()
    return method_names
