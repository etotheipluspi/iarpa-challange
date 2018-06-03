from server.updatedb import updatedb
from server.submit import submit
from server.notify import notify_success, notify_almost_success, notify_error


def main():
    try:
        updatedb()
        try:
            methods_submitted = submit()
            notify_success(methods_submitted)
        except:
            methods_submitted = submit(use_cache=True)
            notify_almost_success(methods_submitted)
    except:
        notify_error()


if __name__ == '__main__':
    main()
