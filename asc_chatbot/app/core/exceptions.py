class ASCException(Exception):
    pass

class PatternNotFoundError(ASCException):
    pass

class MediaUploadError(ASCException):
    pass

class UnauthorizedError(ASCException):
    pass