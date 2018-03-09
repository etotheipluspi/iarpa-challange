import numpy as np
from server.database import Answers


class RandomPredictor:

    def __init__(self):
        self.name = 'random'

    def get_answer_ids(self, session, question_id):
        query = (session.query(Answers.answer_id)
                        .filter(Answers.question_id == question_id)
                        .distinct())
        return [x[0] for x in list(query)]

    def predict(self, session, question_id):
        answer_ids = self.get_answer_ids(session, question_id)
        if len(answer_ids) == 1:
            return [{'answer_id': answer_ids[0],
                     'value': float(np.random.randint(2))}]
        else:
            ipred = np.random.randint(len(answer_ids))
            return [{'answer_id': a,
                     'value': float(i == ipred)}
                    for i, a in enumerate(answer_ids)]
