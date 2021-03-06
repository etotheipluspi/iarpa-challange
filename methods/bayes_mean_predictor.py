from __future__ import division
import numpy as np
import utils.submission as sbm
from server.database import Predictions
from methods.random_predictor import RandomPredictor


class BayesMeanPredictor:
    """
    Submits bayes mean of all predictions.
    """

    def __init__(self):
        self.name = 'bayes_mean'

    def get_bayes_mean_prediction(self, session, answer_id, use_rationale):
        if use_rationale:
            preds = list(session.query(Predictions.forecasted_probability)
                                .filter(Predictions.answer_id == answer_id)
                                .filter(Predictions.rationale != ''))
        else:
            preds = list(session.query(Predictions.forecasted_probability)
                                .filter(Predictions.answer_id == answer_id))
        return 4*(np.mean(preds)*(0.25 - np.var(preds)) + np.var(preds)*0.5)

    def predict(self, session, question_id, answer_ids, cache, use_rationale=False):
        try:
            pred = [{'answer_id': a,
                     'value': self.get_bayes_mean_prediction(session, a, use_rationale)}
                    for a in answer_ids]
            if len(pred) != 1:
                sbm.normalize_pred(pred)
        except:  # if there are no preds or this method fails submit random
            pred = RandomPredictor().predict(session, question_id)
        return pred
