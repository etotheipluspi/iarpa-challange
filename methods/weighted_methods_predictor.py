from __future__ import division
import numpy as np

import utils.queries as qry
import utils.submission as sbm
from scoring.brier import get_score

from median_predictor import MedianPredictor
from median_rationale_predictor import MedianRationalePredictor
from topkmean_predictor import TopKMeanPredictor
from topkmean_extreme_predictor import TopKMeanExtremePredictor
from domain_predictor import DomainPredictor
from inverse_score_predictor import InvScorePredictor


MAX_BRIER_SCORE = 2.0

class WeightedMethodsPredictor:
    """
    Submits a prediction based on weighted sum of all the current methods - 
    weight is determined by Brier score
    """

    def __init__(self, sorted_predictors, scores, sorted_predictors_domains, weighting_function='squared'):

        self.name = 'sisl_weight_' + str(weighting_function)

        self.weighting_function = weighting_function
        self.methods = [MedianPredictor(),
                        MedianRationalePredictor(),
                        TopKMeanPredictor(2, sorted_predictors),
                        TopKMeanPredictor(5, sorted_predictors),
                        TopKMeanPredictor(10, sorted_predictors),
                        TopKMeanPredictor(20, sorted_predictors),
                        TopKMeanPredictor(50, sorted_predictors),
                        TopKMeanExtremePredictor(10, sorted_predictors),
                        DomainPredictor(2, sorted_predictors_domains),
                        DomainPredictor(5, sorted_predictors_domains),
                        DomainPredictor(10, sorted_predictors_domains),
                        DomainPredictor(20, sorted_predictors_domains),
                        DomainPredictor(50, sorted_predictors_domains),
                        InvScorePredictor(sorted_predictors, scores),
                        InvScorePredictor(sorted_predictors, scores, squared=True)]


    def get_average_brier_score(self, session, method):
        questions = qry.get_resolved_question_ids(session)
        scores = []
        for qid in questions[:5]:
            correct_answer = qry.get_correct_answer_id(session, qid)
            prediction = method.predict(session, qid)
            pred_tuple = []
            for p in prediction:
                pred_tuple.append((p['answer_id'], p['value']))
            s = get_score(pred_tuple, correct_answer)
            scores.append(s)
        return np.mean(scores)

    def get_predictor_weights(self, session):
        scores = []
        for m in self.methods:
            try:
                s = self.get_average_brier_score(session, m)
            except:
                s = MAX_BRIER_SCORE
            scores.append(s)
        if self.weighting_function == 'squared':
            return self.squared_brier_to_weights(scores)
        elif self.weighting_function == 'average':
            return self.average_brier_to_weights(scores)
        elif self.weighting_function == 'cbrt':
            return self.cbrt_brier_to_weights(scores)
        else:
            return self.squared_brier_to_weights(scores)

    def average_brier_to_weights(self, scores):
        hi = np.max(scores)
        lo = np.min(scores)
        delta = hi - lo
        new_scores = []
        for s in scores:
            # shift the scores
            sp = s - hi
            sp *= -1.0
            sp += hi
            new_scores.append(sp)
        new_scores = np.array(new_scores) / np.sum(new_scores)
        return new_scores

    def squared_brier_to_weights(self, scores):
        hi = np.max(scores)
        lo = np.min(scores)
        delta = hi - lo
        new_scores = []
        for s in scores:
            # shift the scores
            sp = s - np.sqrt(hi)
            sp *= -1.0
            sp += np.sqrt(hi)
            new_scores.append(sp)
        new_scores = np.array(new_scores) / np.sum(new_scores)
        return new_scores

    def cbrt_brier_to_weights(self, scores):
        hi = np.max(scores)
        lo = np.min(scores)
        delta = hi - lo
        new_scores = []
        for s in scores:
            # shift the scores
            sp = s - np.cbrt(hi)
            sp *= -1.0
            sp += np.cbrt(hi)
            new_scores.append(sp)
        new_scores = np.array(new_scores) / np.sum(new_scores)
        return new_scores
         
    def predict(self, session, question_id):
        weights = self.get_predictor_weights(session)
        final_prediction = []
        total = 0.0
        for w, m in zip(weights, self.methods):
            # array of answer_ids and vals
            try: 
                prediction = m.predict(session, question_id)
            except:
                continue
            for i, p in enumerate(prediction):
                p['value'] *= w
                total += p['value']
                if not final_prediction:
                    final_prediction.append(np.copy(p))
                else:
                    final_prediction[i]['value'] += p['value']
        for p in final_prediction:
            p['value'] /= total
        return final_prediction




    

