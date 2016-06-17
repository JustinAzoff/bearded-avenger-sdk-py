
class CIFException(Exception):
    def __init__(self, msg):
        self.msg = "{}".format(msg)

    def __str__(self):
        return self.msg


class CIFConnectionError(CIFException):
    pass


class StoreSubmissionFailed(CIFException):
    pass


class AuthError(CIFException):
    pass


class TimeoutError(CIFException):
    pass