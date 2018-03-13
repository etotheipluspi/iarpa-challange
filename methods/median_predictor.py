from __future__ import division
import numpy as np
from server.database import Answers, Predictions
from methods.random_predictor import RandomPredictor


class MedianPredictor:
    """
    Submits median of all predictions.
    """

    def __init__(self):
        self.name = 'median'

    def get_answer_ids(self, session, question_id):
        query = (session.query(Answers.answer_id)
                        .filter(Answers.question_id == question_id)
                        .distinct())
        return [x[0] for x in list(query)]

    def get_median_prediction(self, session, answer_id, use_rationale):
        if use_rationale:
            preds = list(session.query(Predictions.forecasted_probability)
                                .filter(Predictions.answer_id == answer_id)
                                .filter(Predictions.rationale != ''))
        else:
            preds = list(session.query(Predictions.forecasted_probability)
                                .filter(Predictions.answer_id == answer_id))
        return np.median(preds)

    def normalize(self, prediction):
        total = sum(p['value'] for p in prediction)
        for p in prediction:
            p['value'] /= total

    def predict(self, session, question_id, use_rationale=False):
        answer_ids = self.get_answer_ids(session, question_id)
        try:
            pred = [{'answer_id': a,
                     'value': self.get_median_prediction(session, a, use_rationale)}
                    for a in answer_ids]
            if len(pred) != 1:
                self.normalize(pred)
        except:  # if there are no preds or this method fails submit random
            pred = RandomPredictor().predict(session, question_id)
        return pred
