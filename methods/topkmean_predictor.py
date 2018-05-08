from __future__ import division
import utils.queries as qry
import utils.submission as sbm


class TopKMeanPredictor:
    """
    Submits mean of the predictions of the top k predictors.
    """

    def __init__(self, k, sorted_predictors):
        self.name = 'top' + str(k) + 'mean'
        self.sorted_predictors = sorted_predictors
        self.k = k

    def predict(self, session, question_id):
        answer_ids = qry.get_answer_ids(session, question_id)
        user_preds, n_preds = [], 0
        for user_id in self.sorted_predictors:
            if n_preds == self.k:
                break
            user_pred = qry.get_preds(session, user_id, question_id, predict=True)
            if None in [p[1] for p in user_pred]:
                continue
            n_preds += 1
            user_preds.append(user_pred)
        pred = sbm.get_pred_dict(user_preds, answer_ids)
        return pred
