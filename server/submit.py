import os
import server.database as db
import utils.caching as cache
import utils.queries as qry
from datetime import datetime
from forecast.tools.api import GfcApi
from methods.random_predictor import RandomPredictor
from methods.median_predictor import MedianPredictor
from methods.median_rationale_predictor import MedianRationalePredictor
from methods.topkmean_predictor import TopKMeanPredictor
from methods.topkmean_extreme_predictor import TopKMeanExtremePredictor
from methods.domain_predictor import DomainPredictor
from methods.inverse_score_predictor import InvScorePredictor
from methods.weighted_methods_predictor import WeightedMethodsPredictor

gfc_creds = dict(
    token=os.environ['GFC_TOKEN'],
    server='https://api.iarpagfchallenge.com'
)

if 'staging' not in gfc_creds['server']:
    raise Exception('''Are you sure you want to submit to the production server? If so, comment these lines and re-run the submission script.''')

api = GfcApi(gfc_creds['token'], gfc_creds['server'])


def get_methods(predictors, scores, predictors_domains, method_scores):
    methods = [RandomPredictor(),
               MedianPredictor(),
               MedianRationalePredictor(),
               TopKMeanPredictor(2, predictors),
               TopKMeanPredictor(5, predictors),
               TopKMeanPredictor(10, predictors),
               TopKMeanPredictor(20, predictors),
               TopKMeanPredictor(50, predictors),
               TopKMeanExtremePredictor(10, predictors),
               DomainPredictor(2, predictors_domains),
               DomainPredictor(5, predictors_domains),
               DomainPredictor(10, predictors_domains),
               DomainPredictor(20, predictors_domains),
               DomainPredictor(50, predictors_domains),
               InvScorePredictor(predictors, scores),
               InvScorePredictor(predictors, scores, squared=True),
               WeightedMethodsPredictor(predictors,
                                        scores,
                                        predictors_domains,
                                        method_scores,
                                        weighting_function='average'),
               WeightedMethodsPredictor(predictors,
                                        scores,
                                        predictors_domains,
                                        method_scores,
                                        weighting_function='squared'),
               WeightedMethodsPredictor(predictors,
                                        scores,
                                        predictors_domains,
                                        method_scores,
                                        weighting_function='cbrt')]
    return methods


def log(session, question_id, method_name, preds):
    session.add_all([db.OurPredictions(
        question_id=question_id,
        answer_id=p['answer_id'],
        method_name=method_name,
        forecasted_probability=p['value'],
        submitted_at=datetime.utcnow()
    ) for p in preds])
    session.commit()


def submit_all(session, methods, question_ids):
    print 'Submitting to questions...'
    for idx, qid in enumerate(question_ids):
        print 'Submitting to question number', idx + 1, 'of', len(question_ids)
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
    print 'Submission complete.'
    return [m.name for m in methods]


def get_predictors(session, user_ids, use_cache):
    if use_cache:
        cached = cache.load_predictors()
        predictors, scores, predictors_domains, method_scores = cached
    else:
        predictors, scores = qry.get_sorted_predictors(session, user_ids)
        predictors_domains = qry.get_sorted_predictors_domains(session, user_ids)
        method_scores = qry.get_method_scores(session)
        cache.save_predictors(predictors,
                              scores,
                              predictors_domains,
                              method_scores)
    return predictors, scores, predictors_domains, method_scores


def submit(use_cache=False):
    session = db.create_session()
    user_ids = qry.get_user_ids(session)
    out = get_predictors(session, user_ids, use_cache)
    predictors, scores, predictors_domains, method_scores = out
    methods = get_methods(predictors, scores, predictors_domains, method_scores)
    question_ids = qry.get_active_question_ids(session)
    method_names = submit_all(session, methods, question_ids)
    session.close()
    return method_names
