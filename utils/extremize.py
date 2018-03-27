def extremize_binary(pred):
        if pred[0]['value'] > 0.5:
            pred[0]['value'] = 1
        else:
            pred[0]['value'] = 0


def get_max_prob(pred):
    max_prob = 0
    for p in pred:
        if p['value'] > max_prob:
            max_prob = p['value']
    return max_prob


def extremize_multianswer(pred):
    max_prob = get_max_prob(pred)
    for p in pred:
        if p['value'] == max_prob:
            p['value'] = 1
        else:
            p['value'] = 0


def extremize(pred):
    if len(pred) == 1:
        extremize_binary(pred)
    else:
        extremize_multianswer(pred)
