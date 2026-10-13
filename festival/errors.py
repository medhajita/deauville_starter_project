
class FestivalError(Exception):
    pass

class ValidationError(FestivalError):
    pass

class NotFoundError(FestivalError):
    pass

class ConflictError(FestivalError):
    pass

class StorageError(FestivalError):
    pass