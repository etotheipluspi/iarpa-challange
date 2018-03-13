from server.database import create_session
from methods.random_predictor import RandomPredictor
from methods.median_predictor import MedianPredictor
from methods.median_rationale_predictor import MedianRationalePredictor

BINARY_QID = 655
BINARY_AID = 1950
MULTIANSWER_QID = 665
MULTIANSWER_AIDS = [1976, 1977, 1978, 1979, 1980]


def test_random_predictor():
    predictor = RandomPredictor()
    validate_predictor(predictor)


def test_median_predictor():
    predictor = MedianPredictor()
    validate_predictor(predictor)


def test_median_rationale_predictor():
    predictor = MedianRationalePredictor()
    validate_predictor(predictor)


def check_method_name(predictor):
    assert predictor.name


def isapprox(x, y, tol=1e-3):
    return abs(x - y) < tol


def check_keys(pred):
    for p in pred:
        assert 'answer_id' in p
        assert 'value' in p


def check_binary_prediction(session, predict):
    pred = predict(session, BINARY_QID)
    assert len(pred) == 1
    check_keys(pred)
    assert pred[0]['answer_id'] == BINARY_AID
    assert 0 <= pred[0]['value'] <= 1


def check_multianswer_prediction(session, predict):
    pred = predict(session, MULTIANSWER_QID)
    assert len(pred) == len(MULTIANSWER_AIDS)
    check_keys(pred)
    assert sorted(p['answer_id'] for p in pred) == MULTIANSWER_AIDS
    assert all(p['value'] >= 0 for p in pred)  # all positive
    assert isapprox(sum(p['value'] for p in pred), 1)  # sum to 1


def validate_predictor(predictor):
    session = create_session()
    check_method_name(predictor)
    check_binary_prediction(session, predictor.predict)
    check_multianswer_prediction(session, predictor.predict)
    session.close()
