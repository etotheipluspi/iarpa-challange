from __future__ import division
import numpy as np
import utils.queries as qry
from methods.median_predictor import MedianPredictor
from methods.median_rationale_predictor import MedianRationalePredictor
from methods.topkmean_predictor import TopKMeanPredictor
from methods.topkmean_extreme_predictor import TopKMeanExtremePredictor
from methods.domain_predictor import DomainPredictor
from methods.inverse_score_predictor import InvScorePredictor


class WeightedMethodsPredictor:
    """
    Submits a prediction based on weighted sum of all the current methods -
    weight is determined by Brier score
    """

    def __init__(self,
                 predictors,
                 scores,
                 predictors_domains,
                 method_scores,
                 weighting_function='squared'):

        self.weighting_function = weighting_function
        self.name = 'sisl_weight_' + weighting_function
        if weighting_function == 'squared':
            self.method_scores = self.squared_brier_to_weights(method_scores)
        elif weighting_function == 'average':
            self.method_scores = self.average_brier_to_weights(method_scores)
        elif weighting_function == 'cbrt':
            self.method_scores = self.cbrt_brier_to_weights(method_scores)
        self.methods = [MedianPredictor(),
                        MedianRationalePredictor(),
                        TopKMeanPredictor(2, predictors),
                        TopKMeanPredictor(5, predictors),
                        TopKMeanPredictor(10, predictors),
                        TopKMeanPredictor(20, predictors),
                        TopKMeanPredictor(50, predictors),
                        TopKMeanExtremePredictor(10, predictors),
                        DomainPredictor(2, predictors_domains),
                        DomainPredictor(5, predictors_domains),
                        DomainPredictor(10, predictors_domains),
                        DomainPredictor(20, predictors_domains),
                        DomainPredictor(50, predictors_domains),
                        InvScorePredictor(predictors, scores),
                        InvScorePredictor(predictors, scores, squared=True)]

    def normalize(self, scores):
        total = np.sum(scores.values())
        for name in scores.keys():
            scores[name] /= total

    def average_brier_to_weights(self, scores):
        hi = np.max([x for x in scores.values() if not np.isnan(x)])
        new_scores = {}
        for name, s in scores.items():
            # shift the scores
            if not np.isnan(s):
                new_scores[name] = hi - s
        self.normalize(new_scores)
        return new_scores

    def squared_brier_to_weights(self, scores):
        hi = np.max([x for x in scores.values() if not np.isnan(x)])
        new_scores = {}
        for name, s in scores.items():
            # shift the scores
            if not np.isnan(s):
                new_scores[name] = np.sqrt(hi) - np.sqrt(s)
        self.normalize(new_scores)
        return new_scores

    def cbrt_brier_to_weights(self, scores):
        hi = np.max([x for x in scores.values() if not np.isnan(x)])
        new_scores = {}
        for name, s in scores.items():
            # shift the scores
            if not np.isnan(s):
                new_scores[name] = np.cbrt(hi) - np.cbrt(s)
        self.normalize(new_scores)
        return new_scores

    def get_method(self, name):
        for method in self.methods:
            if method.name == name:
                return method

    def add_pred(self, final_pred, pred):
        for p in final_pred:
            idx = [x['answer_id'] for x in pred].index(p['answer_id'])
            p['value'] += pred[idx]['value']

    def predict(self, session, question_id):
        answer_ids = qry.get_answer_ids(session, question_id)
        final_pred = [{'answer_id': aid, 'value': 0} for aid in answer_ids]
        total = 0.
        for name, weight in self.method_scores.items():
            method = self.get_method(name)
            pred = method.predict(session, question_id)
            for i, prob in enumerate(pred):
                prob['value'] *= weight
                total += prob['value']
            self.add_pred(final_pred, pred)
        for p in final_pred:
            p['value'] /= total
        return final_pred
