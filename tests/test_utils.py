from copy import deepcopy
from utils.extremize import extremize

BINARY_PRED1 = [{'answer_id': 1950, 'value': 0.1}]
BINARY_PRED2 = [{'answer_id': 1950, 'value': 0.8}]
MULTIANSWER_PRED1 = [{'answer_id': 1976, 'value': 0.1},
                     {'answer_id': 1977, 'value': 0.1},
                     {'answer_id': 1978, 'value': 0.6},
                     {'answer_id': 1979, 'value': 0.1},
                     {'answer_id': 1980, 'value': 0.1}]
MULTIANSWER_PRED2 = [{'answer_id': 1976, 'value': 0.2},
                     {'answer_id': 1977, 'value': 0.2},
                     {'answer_id': 1978, 'value': 0.2},
                     {'answer_id': 1979, 'value': 0.25},
                     {'answer_id': 1980, 'value': 0.15}]

EXTREME_BINARY_PRED1 = [{'answer_id': 1950, 'value': 0}]
EXTREME_BINARY_PRED2 = [{'answer_id': 1950, 'value': 1}]
EXTREME_MULTIANSWER_PRED1 = [{'answer_id': 1976, 'value': 0},
                             {'answer_id': 1977, 'value': 0},
                             {'answer_id': 1978, 'value': 1},
                             {'answer_id': 1979, 'value': 0},
                             {'answer_id': 1980, 'value': 0}]
EXTREME_MULTIANSWER_PRED2 = [{'answer_id': 1976, 'value': 0},
                             {'answer_id': 1977, 'value': 0},
                             {'answer_id': 1978, 'value': 0},
                             {'answer_id': 1979, 'value': 1},
                             {'answer_id': 1980, 'value': 0}]


def is_same_pred(pred1, pred2):
    if len(pred1) == 1:
        return pred1[0].items() == pred2[0].items()
    else:
        p1_tups = sorted([sorted(p.items()) for p in pred1])
        p2_tups = sorted([sorted(p.items()) for p in pred2])
        return p1_tups == p2_tups


def test_extremize_binary():
    pred1 = deepcopy(BINARY_PRED1)
    extremize(pred1)
    assert is_same_pred(pred1, EXTREME_BINARY_PRED1)
    pred2 = deepcopy(BINARY_PRED2)
    extremize(pred2)
    assert is_same_pred(pred2, EXTREME_BINARY_PRED2)


def test_extremize_multianswer():
    pred1 = deepcopy(MULTIANSWER_PRED1)
    extremize(pred1)
    assert is_same_pred(pred1, EXTREME_MULTIANSWER_PRED1)
    pred2 = deepcopy(MULTIANSWER_PRED2)
    extremize(pred2)
    assert is_same_pred(pred2, EXTREME_MULTIANSWER_PRED2)
