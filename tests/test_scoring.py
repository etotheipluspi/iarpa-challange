from scoring.brier import get_score
from scoring.brier import get_ordinal_score

# Test cases taken from the IARPA challenge rules handbook

PREDS1 = [('A', 0.25), ('B', 0.25), ('C', 0.5), ('D', 0)]
PREDS2 = [('A', 0.25), ('B', 0.25), ('C', 0.3), ('D', 0.2)]
CORRECT_ANSWER = 'B'
BRIER1 = 0.22
BRIER2 = 0.19
ORDINAL1 = 0.21
ORDINAL2 = 0.24


def isapprox(x, y, tol=1e-2):
        return abs(x - y) < tol


def test_brier_score():
    score1 = get_score(PREDS1, CORRECT_ANSWER)
    assert isapprox(score1, BRIER1)
    score2 = get_score(PREDS2, CORRECT_ANSWER)
    assert isapprox(score2, BRIER2)


def test_ordinal_brier_score():
    score1 = get_ordinal_score(PREDS1, CORRECT_ANSWER)
    print score1
    assert isapprox(score1, ORDINAL1)
    score2 = get_ordinal_score(PREDS2, CORRECT_ANSWER)
    assert isapprox(score2, ORDINAL2)
