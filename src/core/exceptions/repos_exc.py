from .app_exc import AppException

class NotFoundException(AppException):
    def __init__(self, object_type : str = None , id = None ,message = None, status_code = 400):
        
        if message is None: 
            if id and object_type:
                message = f"{object_type} with id {id} not found"
            elif object_type is not None:
                message = f"{object_type} not found"
            
        super().__init__(message, status_code)
