import numpy as np


class RandomPredictor:

    def __init__(self):
        self.name = 'random'

    def predict(self, session, question_id, answer_ids, cache):
        if len(answer_ids) == 1:
            return [{'answer_id': answer_ids[0],
                     'value': float(np.random.randint(2))}]
        else:
            ipred = np.random.randint(len(answer_ids))
            return [{'answer_id': a,
                     'value': float(i == ipred)}
                    for i, a in enumerate(answer_ids)]
