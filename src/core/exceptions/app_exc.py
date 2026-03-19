class AppException(Exception):
    def __init__(self, message: str = "Something went wrong", status_code: int = 400,details=None):
        self.message = message
        self.status_code = status_code
        self.details = details
