from __future__ import division
from methods.topkmean_predictor import TopKMeanPredictor
from utils.extremize import extremize


class TopKMeanExtremePredictor:
    """
    Submits extremized predictions from top k mean predictor.
    """

    def __init__(self, k, sorted_predictors):
        self.topk_predictor = TopKMeanPredictor(k, sorted_predictors)
        self.name = self.topk_predictor.name + '_extreme'

    def predict(self, session, question_id, answer_ids, cache):
        pred = self.topk_predictor.predict(session,
                                           question_id,
                                           answer_ids,
                                           cache)
        extremize(pred)
        return pred
