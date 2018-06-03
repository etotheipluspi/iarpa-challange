import os
import requests


def message(msg_type, methods_submitted):
    if msg_type == 'db_success':
        return 'Updated database successfully.'
    elif msg_type == 'db_fail':
        return 'Updating database failed.'
    elif msg_type == 'score_success':
        return 'Scoring predictors and methods successfully.'
    elif msg_type == 'score_fail':
        return 'Scoring predictors and methods failed.'
    elif msg_type == 'submit_success':
        msg = 'Submission succeeded.'
        msg += ' Successully submitted responses for methods'
        for m in methods_submitted:
            msg += ' ' + m + ','
        return msg[:-1] + '.'
    elif msg_type == 'submit_fail':
        return 'Submission failed.'


def notify(msg_type, methods_submitted=None):
    requests.post(os.environ['SLACK_URL'],
                  json={'text': message(msg_type, methods_submitted)})
