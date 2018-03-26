from __future__ import division
from datetime import datetime
import server.database as db
import scoring.brier as brier

MAX_BRIER_SCORE = 2


class TopKMeanPredictor:
    """
    Submits mean of the predictions of the top k predictors.
    """

    def __init__(self, k):
        self.name = 'top' + str(k) + 'mean'
        self.session = db.create_session()
        self.topk = self.get_topk_userids(self.session, k)
        self.session.close()

    def get_ended_question_ids(self, session):
        query = (session.query(db.Questions.question_id)
                        .filter(db.Questions.ends_at < datetime.utcnow()))
        return [x[0] for x in query]

    def get_resolved_question_ids(self, session):
        query = (session.query(db.Answers.question_id)
                        .filter(db.Answers.is_correct is not None))
        return [x[0] for x in query]

    def get_question_ids(self, session):
        ended = set(self.get_ended_question_ids(session))
        resolved = set(self.get_resolved_question_ids(session))
        return list(ended & resolved)

    def get_answer_ids(self, session, question_id):
        query = (session.query(db.Answers.answer_id)
                        .filter(db.Answers.question_id == question_id)
                        .order_by(db.Answers.sort_order))
        return [x[0] for x in query]

    def get_correct_answer_id(self, session, question_id):
        query = (session.query(db.Answers.answer_id)
                        .filter(db.Answers.question_id == question_id)
                        .filter(db.Answers.is_correct is True)).first()
        return query[0] if query is not None else False

    def get_user_ids(self, session):
        query = session.query(db.Predictions.user_id).distinct()
        return [x[0] for x in query]

    def get_ends_at(self, session, question_id):
        query = (session.query(db.Questions.ends_at)
                        .filter(db.Questions.question_id == question_id)).first()
        return query[0]

    def get_pred(self, session, user_id, question_id, answer_id, predict):
        if predict:
            ends_at = datetime.utcnow()
        else:
            ends_at = self.get_ends_at(session, question_id)
        query = (session.query(db.Predictions.forecasted_probability)
                        .filter(db.Predictions.user_id == user_id)
                        .filter(db.Predictions.question_id == question_id)
                        .filter(db.Predictions.answer_id == answer_id)
                        .filter(db.Predictions.submitted_at < ends_at)
                        .order_by(db.Predictions.submitted_at.desc())).first()
        return query[0] if query is not None else None

    def get_preds(self, session, user_id, question_id, predict=False):
        preds = []
        answer_ids = self.get_answer_ids(session, question_id)
        for answer_id in answer_ids:
            pred = self.get_pred(session, user_id, question_id, answer_id, predict)
            preds.append((answer_id, pred))
        return preds

    def get_use_ordinal_scoring(self, session, question_id):
        query = (session.query(db.Questions.use_ordinal_scoring)
                        .filter(db.Questions.question_id == question_id)).first()
        return query[0]

    def get_score(self, session, user_id, question_id):
        preds = self.get_preds(session, user_id, question_id)
        if None in [p[1] for p in preds]:
            return MAX_BRIER_SCORE
        correct_answer_id = self.get_correct_answer_id(session, question_id)
        use_ordinal_scoring = self.get_use_ordinal_scoring(session, question_id)
        if use_ordinal_scoring:
            return brier.get_ordinal_score(preds, correct_answer_id)
        else:
            return brier.get_score(preds, correct_answer_id)

    def get_user_score(self, session, user_id):
        score = 0
        question_ids = self.get_question_ids(session)
        for question_id in question_ids:
            score += self.get_score(session, user_id, question_id)
        return score / len(question_ids)

    def get_topk_userids(self, session, k):
        user_ids = self.get_user_ids(session)
        topk = []
        for user_id in user_ids:
            score = self.get_user_score(session, user_id)
            topk.append((user_id, score))
        topk_sorted = sorted(topk, key=lambda x: x[1])
        return [x[0] for x in topk_sorted][:k]

    def add_pred(self, pred, user_pred):
        for idx, (_, prob) in enumerate(user_pred):
            pred[idx]['value'] += prob

    def normalize(self, pred, n):
        for p in pred:
            p['value'] /= n

    def get_pred_dict(self, user_preds, answer_ids):
        pred = [{'answer_id': aid, 'value': 0} for aid in answer_ids]
        n_preds = 0
        for user_pred in user_preds:
            if None in [p[1] for p in user_pred]:
                continue
            n_preds += 1
            self.add_pred(pred, user_pred)
        self.normalize(pred, n_preds)
        return pred

    def predict(self, session, question_id):
        answer_ids = self.get_answer_ids(session, question_id)
        user_preds = []
        for user_id in self.topk:
            user_pred = self.get_preds(session, user_id, question_id, predict=True)
            user_preds.append(user_pred)
        pred = self.get_pred_dict(user_preds, answer_ids)
        return pred
