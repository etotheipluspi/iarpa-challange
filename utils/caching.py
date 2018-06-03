import cPickle as pkl


def save_predictors(predictors, scores, predictors_domains, method_scores):
    pkl.dump(predictors, open('saved/predictors.pkl', 'w'))
    pkl.dump(scores, open('saved/scores.pkl', 'w'))
    pkl.dump(predictors_domains, open('saved/predictors_domains.pkl', 'w'))
    pkl.dump(method_scores, open('saved/method_scores.pkl', 'w'))


def load_predictors():
    predictors = pkl.load(open('saved/predictors.pkl', 'r'))
    scores = pkl.load(open('saved/scores.pkl', 'r'))
    predictors_domains = pkl.load(open('saved/predictors_domains.pkl', 'r'))
    method_scores = pkl.load(open('saved/method_scores.pkl', 'r'))
    return predictors, scores, predictors_domains, method_scores
