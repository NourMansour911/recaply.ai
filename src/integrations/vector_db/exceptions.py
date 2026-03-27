
class VectorDBException(Exception):
    """Base exception for all vector DB errors."""
    pass

class ConnectionError(VectorDBException):
    """Raised when the DB connection fails."""
    pass

class CollectionNotFoundError(VectorDBException):
    """Raised when a requested collection does not exist."""
    pass

class InsertError(VectorDBException):
    """Raised when inserting points fails."""
    pass

class BatchInsertError(VectorDBException):
    """Raised when inserting a batch of points fails."""
    pass

class FetchError(VectorDBException):
    """Raised when fetching points/chunks fails."""
    pass

class SearchError(VectorDBException):
    """Raised when search (vector or keyword) fails."""
    pass