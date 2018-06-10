from __future__ import division
from methods.bayes_mean_predictor import BayesMeanPredictor


class BayesMeanRationalePredictor:
    """
    Submits bayes mean of all predictions that have a non-empty 'rationale' field.
    """

    def __init__(self):
        self.name = 'bayes_mean_rationale'
        self.bayes_mean_predictor = BayesMeanPredictor()

    def predict(self, session, question_id, answer_ids, cache):
        return self.bayes_mean_predictor.predict(session,
                                                 question_id,
                                                 answer_ids,
                                                 cache,
                                                 use_rationale=True)
