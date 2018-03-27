from __future__ import division
from methods.topkmean_predictor import TopKMeanPredictor
from utils.extremize import extremize


class TopKMeanExtremePredictor:
    """
    Submits extremized predictions from top k mean predictor.
    """

    def __init__(self, k):
        self.topk_predictor = TopKMeanPredictor(k)
        self.name = self.topk_predictor.name + '_extreme'

    def predict(self, session, question_id):
        pred = self.topk_predictor.predict(session, question_id)
        extremize(pred)
        return pred
