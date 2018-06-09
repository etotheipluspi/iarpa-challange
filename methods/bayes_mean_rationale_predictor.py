from __future__ import division
from methods.bayes_mean_predictor import BayesMeanPredictor


class BayesMeanRationalePredictor:
    """
    Submits bayes mean of all predictions that have a non-empty 'rationale' field.
    """

    def __init__(self):
        self.name = 'bayes_mean_rationale'
        self.bayes_mean_rationale = BayesMeanPredictor()

    def predict(self, session, question_id):
        return self.bayes_mean_rationale.predict(session,
                                                 question_id,
                                                 use_rationale=True)
