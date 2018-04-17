from __future__ import division
from datetime import datetime
import server.database as db
import scoring.brier as brier

MAX_BRIER_SCORE = 2


class InvScorePredictor:
    """
    Submits predictions weighted by inverse score of the experts
    (when no score, take max brier score of 2, so weight is 0.5).
    """

    def __init__(self, squared=False):
        if squared:
            self.name = 'invscore_sq'
        else:
            self.name = 'invscore'
        self.squared = squared
        self.session = db.create_session()
        self.all_u = self.get_all_userids(self.session)
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
            preds.append([answer_id, pred])
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

    def get_all_userids(self, session):
        user_ids = self.get_user_ids(session)
        all_u = []
        for user_id in user_ids:
            score = self.get_user_score(session, user_id)
            all_u.append([user_id, score])
        all_u = sorted(all_u, key=lambda x: x[1])
        return all_u

    def add_pred(self, pred, user_pred):
        for idx, (_, prob) in enumerate(user_pred):
            pred[idx]['value'] += prob

    def normalize(self, pred, norm_factor):
        if len(pred) == 1:
            pred[0]['value'] /= norm_factor
        else:
            s = 0
            for p in pred:
                s += p['value']
            if s:
                for p in pred:
                    p['value'] /= s

    def get_pred_dict(self, user_preds, answer_ids, norm_factor=None):
        pred = [{'answer_id': aid, 'value': 0} for aid in answer_ids]
        for user_pred in user_preds:
            if None in [p[1] for p in user_pred]:
                continue
            self.add_pred(pred, user_pred)
        self.normalize(pred, norm_factor)
        return pred

    def predict(self, session, question_id):
        answer_ids = self.get_answer_ids(session, question_id)
        user_preds = []
        if len(answer_ids) == 1:
            is_binary = True
            norm_factor = 0.
        else:
            is_binary = False
        for user_inf in self.all_u:
            # user_inf contains (user_id, score)
            user_pred = self.get_preds(session,
                                       user_inf[0],
                                       question_id,
                                       predict=True)
            for p in user_pred:
                if p[1] is not None:
                    if self.squared:
                        factor = 1.0 / (user_inf[1] + 0.001) ** 2
                    else:
                        factor = 1.0 / (user_inf[1] + 0.001)
                    p[1] *= factor
                    if is_binary:
                        norm_factor += factor
            user_preds.append(user_pred)
        if is_binary:
            pred = self.get_pred_dict(user_preds,
                                      answer_ids,
                                      norm_factor=norm_factor)
        else:
            pred = self.get_pred_dict(user_preds, answer_ids)
        return pred
