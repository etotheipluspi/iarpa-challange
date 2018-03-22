def get_score(preds, correct_answer_id):
    # Note: this score is normalized, whereas the score in the
    #       IARPA challenge rules handbook is not
    score = 0
    for answer_id, pred in preds:
        score += (int(answer_id == correct_answer_id) - pred) ** 2
    score /= len(preds)
    return score


def get_ordinal_score(preds, correct_answer_id):
    # Note: assumes answers are in sorted order
    score = 0
    for i in range(1, len(preds)):
        left, right = preds[:i], preds[i:]
        sum_left, sum_right = sum(x[1] for x in left), sum(x[1] for x in right)
        if correct_answer_id in [x[0] for x in left]:
            correct, incorrect = sum_left, sum_right
        else:
            correct, incorrect = sum_right, sum_left
        score += (1 - correct) ** 2 + incorrect ** 2
    score /= len(preds) - 1
    return score
