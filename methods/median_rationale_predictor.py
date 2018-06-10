from __future__ import division
from methods.median_predictor import MedianPredictor


class MedianRationalePredictor:
    """
    Submits median of all predictions that have a non-empty 'rationale' field.
    """

    def __init__(self):
        self.name = 'median_rationale'
        self.median_predictor = MedianPredictor()

    def predict(self, session, question_id, answer_ids, cache):
        return self.median_predictor.predict(session,
                                             question_id,
                                             answer_ids,
                                             cache,
                                             use_rationale=True)
