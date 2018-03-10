import os
import requests


def message(methods_submitted):
    msg = 'Successully updated tables and submitted responses for methods'
    for m in methods_submitted:
        msg += ' ' + m + ','
    return msg[:-1] + '.'


def notify_success(methods_submitted):
    requests.post(os.environ['SLACK_URL'],
                  json={'text': message(methods_submitted)})


def notify_error():
    requests.post(os.environ['SLACK_URL'],
                  json={'text': 'Job failed. Check server logs for error.'})
