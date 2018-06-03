from server.submit import score
from server.notify import notify


def main():
    try:
        score()
        notify('score_success')
    except:
        notify('score_fail')


if __name__ == '__main__':
    main()
