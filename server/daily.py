from server.updatedb import updatedb
from server.submit import submit
from server.notify import notify


def main():
    try:
        updatedb()
        notify('db_success')
    except:
        notify('db_fail')
    try:
        methods_submitted = submit()
        notify('submit_success',
               methods_submitted=methods_submitted)
    except:
        notify('submit_fail')


if __name__ == '__main__':
    main()
