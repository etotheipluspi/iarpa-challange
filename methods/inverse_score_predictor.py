from __future__ import division
import utils.queries as qry
import utils.submission as sbm


class InvScorePredictor:
    """
    Submits predictions weighted by inverse score of the top 10
    experts (when no score, take max brier score of 2, so weight is 0.5).
    """

    def __init__(self, sorted_predictors, scores, squared=False):
        if squared:
            self.name = 'invscore_sq'
        else:
            self.name = 'invscore'
        self.squared = squared
        self.sorted_predictors = sorted_predictors
        self.scores = scores

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
            sbm.add_pred(pred, user_pred)
        self.normalize(pred, norm_factor)
        return pred

    def to_list(self, user_pred):
        return [list(x) for x in user_pred]

    def predict(self, session, question_id):
        answer_ids = qry.get_answer_ids(session, question_id)
        user_preds = []
        if len(answer_ids) == 1:
            is_binary = True
            norm_factor = 0.
        else:
            is_binary = False
        for user_id, score in zip(self.sorted_predictors[:10], self.scores[:10]):
            user_pred = self.to_list(qry.get_preds(session,
                                                   user_id,
                                                   question_id,
                                                   predict=True))
            for p in user_pred:
                if p[1] is not None:
                    if self.squared:
                        factor = 1.0 / (score + 0.001) ** 2
                    else:
                        factor = 1.0 / (score + 0.001)
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
