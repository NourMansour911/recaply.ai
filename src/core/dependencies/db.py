from fastapi import Request

def get_db_client(request: Request):
        return request.app.db_client