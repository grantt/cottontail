"""Cottontial Error classes and functions."""


class CottontailBaseError(Exception):
    """
    Base exception class for Cottontail errors in Python.
    """
    pass


class CottontailError(CottontailBaseError):
    """
    A generic error for the Cottontail client

    Args:
        message (str): Name of the error message to pass
        code (int): Numeric code of the error to display
    """

    def __init__(self, message, code):
        if not code:
            code = UNKNOWN
        self.err_code = code

        if not message:
            message = u'An unknown error occurred'

        self.err_message = message

    def __repr__(self):
        return unicode(self).encode('utf-8')

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return u"CottontailError('{}', code={})".format(self.err_message, self.err_code)

UNKNOWN = 0
INVALID = 1

__all__ = [
     u'CottontailBaseError',
     u'CottontailError'
]