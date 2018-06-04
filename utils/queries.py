from __future__ import division
import numpy as np
from datetime import datetime
import server.database as db
import scoring.brier as brier

MAX_BRIER_SCORE = 2


def get_domains(session):
    query = session.query(db.Questions.domain).distinct()
    return [x[0] for x in query]


def get_question_domain(session, question_id):
    query = (session.query(db.Questions.domain)
                    .filter(db.Questions.question_id == question_id)
                    .first())
    return query[0]


def get_resolved_question_ids(session, domain=None):
    if domain is None:
        query = (session.query(db.Answers.question_id)
                        .filter(db.Answers.is_correct)
                        .distinct())
    else:
        query = (session.query(db.Answers.question_id)
                        .filter(db.Answers.is_correct)
                        .filter(db.Questions.domain == domain)
                        .distinct())
    return [x[0] for x in query]


def get_active_question_ids(session):
    query = (session.query(db.Questions.question_id)
                    .filter(db.Questions.ends_at > datetime.utcnow())
                    .distinct())
    return [x[0] for x in list(query)]


def get_answer_ids(session, question_id):
    query = (session.query(db.Answers.answer_id)
                    .filter(db.Answers.question_id == question_id)
                    .order_by(db.Answers.sort_order)
                    .distinct())
    return [x[0] for x in query]


def get_correct_answer_id(session, question_id):
    query = (session.query(db.Answers.answer_id)
                    .filter(db.Answers.question_id == question_id)
                    .filter(db.Answers.is_correct is True)).first()
    return query[0] if query is not None else False


def get_user_ids(session):
    query = session.query(db.Predictions.user_id).distinct()
    return [x[0] for x in query]


def get_ends_at(session, question_id):
    query = (session.query(db.Questions.ends_at)
                    .filter(db.Questions.question_id == question_id)).first()
    return query[0]


def get_our_pred(session, method_name, question_id, answer_id):
    ends_at = get_ends_at(session, question_id)
    query = (session.query(db.OurPredictions.forecasted_probability)
                    .filter(db.OurPredictions.method_name == method_name)
                    .filter(db.OurPredictions.question_id == question_id)
                    .filter(db.OurPredictions.answer_id == answer_id)
                    .filter(db.OurPredictions.submitted_at < ends_at)
                    .order_by(db.OurPredictions.submitted_at.desc())).first()
    return query[0] if query is not None else None


def get_our_preds(session, method_name, question_id, answer_ids):
    preds = []
    answer_ids = get_answer_ids(session, question_id)
    for answer_id in answer_ids:
        pred = get_our_pred(session, method_name, question_id, answer_id)
        preds.append((answer_id, pred))
    return preds


def get_pred(session, user_id, question_id, answer_id, predict):
    if predict:
        ends_at = datetime.utcnow()
    else:
        ends_at = get_ends_at(session, question_id)
    query = (session.query(db.Predictions.forecasted_probability)
                    .filter(db.Predictions.user_id == user_id)
                    .filter(db.Predictions.question_id == question_id)
                    .filter(db.Predictions.answer_id == answer_id)
                    .filter(db.Predictions.submitted_at < ends_at)
                    .order_by(db.Predictions.submitted_at.desc())).first()
    return query[0] if query is not None else None


def get_preds(session, user_id, question_id, predict=False):
    preds = []
    answer_ids = get_answer_ids(session, question_id)
    for answer_id in answer_ids:
        pred = get_pred(session, user_id, question_id, answer_id, predict)
        preds.append((answer_id, pred))
    return preds


def get_use_ordinal_scoring(session, question_id):
    query = (session.query(db.Questions.use_ordinal_scoring)
                    .filter(db.Questions.question_id == question_id)).first()
    return query[0]


def get_method_names(session):
    query = (session.query(db.OurPredictions.method_name).distinct())
    return [x[0] for x in query if 'sisl' not in x[0] and x[0] != 'random']


def get_method_score(session, method_name, question_ids):
    scores = []
    for question_id in question_ids:
            score = get_score(session, method_name, question_id, is_method=True)
            scores.append(score)
    return np.mean([x for x in scores if x != MAX_BRIER_SCORE])


def get_score(session, predictor_id, question_id, is_method=False):
    if is_method:
        answer_ids = get_answer_ids(session, question_id)
        preds = get_our_preds(session, predictor_id, question_id, answer_ids)
    else:
        preds = get_preds(session, predictor_id, question_id)
    if None in [p[1] for p in preds]:
        return MAX_BRIER_SCORE
    correct_answer_id = get_correct_answer_id(session, question_id)
    use_ordinal_scoring = get_use_ordinal_scoring(session, question_id)
    if use_ordinal_scoring:
        return brier.get_ordinal_score(preds, correct_answer_id)
    else:
        return brier.get_score(preds, correct_answer_id)


def get_user_score(session, user_id, question_ids):
    score = 0
    if not question_ids:  # no questions in that domain
        question_ids = get_resolved_question_ids(session)
    for question_id in question_ids:
        score += get_score(session, user_id, question_id)
    return score / len(question_ids)


def get_sorted_predictors_helper(session, user_ids, question_ids):
    print 'Scoring predictors...'
    predictors = []
    for idx, user_id in enumerate(user_ids):
        print 'Scoring predictor', idx + 1, 'of', len(user_ids)
        score = get_user_score(session, user_id, question_ids)
        predictors.append((user_id, score))
    sorted_predictors = sorted(predictors, key=lambda x: x[1])
    print 'Scoring predictors complete.'
    return zip(*sorted_predictors)


def get_sorted_predictors(session, user_ids):
    question_ids = get_resolved_question_ids(session)
    return get_sorted_predictors_helper(session, user_ids, question_ids)


def get_sorted_predictors_domain(session, user_ids, domain):
    question_ids = get_resolved_question_ids(session, domain=domain)
    return get_sorted_predictors_helper(session, user_ids, question_ids)[0]


def get_sorted_predictors_domains(session, user_ids):
    print 'Scoring predictors on each domain...'
    domains = get_domains(session)
    predictors_domains = {}
    for idx, d in enumerate(domains):
        print 'Scoring domain', idx + 1, 'of', len(domains)
        predictors_domains[d] = get_sorted_predictors_domain(session, user_ids, d)
    print 'Domain scoring complete.'
    return predictors_domains


def get_method_scores(session):
    print 'Scoring our methods...'
    method_names = get_method_names(session)
    method_scores = {}
    question_ids = get_resolved_question_ids(session)
    for idx, name in enumerate(method_names):
        print 'Scoring method', idx + 1, 'of', len(method_names), name
        method_score = get_method_score(session, name, question_ids)
        method_scores[name] = method_score
    print 'Scoring our methods complete.'
    return method_scores
