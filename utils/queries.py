from __future__ import division
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


def get_ended_question_ids(session, domain=None):
    if domain is None:
        query = (session.query(db.Questions.question_id)
                        .filter(db.Questions.ends_at < datetime.utcnow()))
    else:
        query = (session.query(db.Questions.question_id)
                        .filter(db.Questions.ends_at < datetime.utcnow())
                        .filter(db.Questions.domain == domain))
    return [x[0] for x in query]


def get_resolved_question_ids(session, domain=None):
    if domain is None:
        query = (session.query(db.Answers.question_id)
                        .filter(db.Answers.is_correct is not None))
    else:
        query = (session.query(db.Answers.question_id)
                        .filter(db.Answers.is_correct is not None)
                        .filter(db.Questions.domain == domain))
    return [x[0] for x in query]


def get_active_question_ids(session):
    query = (session.query(db.Questions.question_id)
                    .filter(db.Questions.ends_at > datetime.utcnow())
                    .distinct())
    return [x[0] for x in list(query)]


def get_question_ids(session, domain=None):
    ended = set(get_ended_question_ids(session, domain=domain))
    resolved = set(get_resolved_question_ids(session, domain=domain))
    return list(ended & resolved)


def get_answer_ids(session, question_id):
    query = (session.query(db.Answers.answer_id)
                    .filter(db.Answers.question_id == question_id)
                    .order_by(db.Answers.sort_order))
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


def get_score(session, user_id, question_id):
    preds = get_preds(session, user_id, question_id)
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
    if not question_ids:  # in case no questions in that domain
        question_ids = get_question_ids(session)
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
    question_ids = get_question_ids(session)
    return get_sorted_predictors_helper(session, user_ids, question_ids)


def get_sorted_predictors_domain(session, user_ids, domain):
    question_ids = get_question_ids(session, domain=domain)
    return get_sorted_predictors_helper(session, user_ids, question_ids)[0]


def get_sorted_predictors_domains(session, user_ids):
    print 'Scoring predictors on each domain.'
    domains = get_domains(session)
    predictors_domains = {}
    for idx, d in enumerate(domains):
        print 'Scoring domain', idx + 1, 'of', len(domains)
        predictors_domains[d] = get_sorted_predictors_domain(session, user_ids, d)
    print 'Domain scoring complete.'
    return predictors_domains
