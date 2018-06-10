from __future__ import division
import numpy as np
import utils.queries as qry


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

    def normalize(self, scores):
        total = np.sum(scores.values())
        for name in scores.keys():
            scores[name] /= total

    def average_brier_to_weights(self, scores):
        new_scores = {}
        for name, s in scores.items():
            # shift the scores
            if not np.isnan(s):
                new_scores[name] = 1 / (s + 0.001)
        self.normalize(new_scores)
        return new_scores

    def squared_brier_to_weights(self, scores):
        new_scores = {}
        for name, s in scores.items():
            # shift the scores
            if not np.isnan(s):
                new_scores[name] = 1 / (s + 0.001) ** 2
        self.normalize(new_scores)
        return new_scores

    def cbrt_brier_to_weights(self, scores):
        new_scores = {}
        for name, s in scores.items():
            # shift the scores
            if not np.isnan(s):
                new_scores[name] = 1 / (s + 0.001) ** 3
        self.normalize(new_scores)
        return new_scores

    def add_pred(self, final_pred, pred):
        for p in final_pred:
            idx = [x['answer_id'] for x in pred].index(p['answer_id'])
            p['value'] += pred[idx]['value']

    def get_method_pred(self, session, method_name, question_id, answer_ids, cache):
        pred = qry.get_our_preds(session,
                                 method_name,
                                 question_id,
                                 answer_ids,
                                 cache=cache)
        return [{'answer_id': aid, 'value': p} for (aid, p) in pred]

    def predict(self, session, question_id, answer_ids, cache):
        final_pred = [{'answer_id': aid, 'value': 0} for aid in answer_ids]
        total = 0.
        for name, weight in self.method_scores.items():
            pred = self.get_method_pred(session,
                                        name,
                                        question_id,
                                        answer_ids,
                                        cache)
            for p in pred:
                p['value'] *= weight
            if len(answer_ids) < 1:
                    total += p['value']
            else:
                total += weight
            self.add_pred(final_pred, pred)
        for p in final_pred:
            p['value'] /= total
        return final_pred
