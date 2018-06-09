from __future__ import division


def add_pred(pred, user_pred):
    for idx, (_, prob) in enumerate(user_pred):
        pred[idx]['value'] += prob


# Normalize by dividing by number of predictors
def normalize(pred, n):
    if not n:
        return
    for p in pred:
        p['value'] /= n


# Normalize to ensure sum of probs equals 1
def normalize_pred(pred):
    total = sum(p['value'] for p in pred)
    if total:
        for p in pred:
            p['value'] /= total


def get_pred_dict(user_preds, answer_ids):
    pred = [{'answer_id': aid, 'value': 0} for aid in answer_ids]
    for user_pred in user_preds:
        add_pred(pred, user_pred)
    normalize(pred, len(user_preds))
    return pred
