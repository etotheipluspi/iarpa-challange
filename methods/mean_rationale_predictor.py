from __future__ import division
from methods.mean_predictor import MeanPredictor


class MeanRationalePredictor:
    """
    Submits mean of all predictions that have a non-empty 'rationale' field.
    """

    def __init__(self):
        self.name = 'mean_rationale'
        self.mean_predictor = MeanPredictor()

    def predict(self, session, question_id, answer_ids, cache):
        return self.mean_predictor.predict(session,
                                           question_id,
                                           answer_ids,
                                           cache,
                                           use_rationale=True)
