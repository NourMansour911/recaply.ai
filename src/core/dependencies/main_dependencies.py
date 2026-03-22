from fastapi import Header, Request, Depends


def get_tenant_id(x_tenant_id: str = Header(...)):
    return x_tenant_id

def get_db_client(request: Request) :
        return request.app.state.db_client
    
def get_whisper(request: Request) :
        return request.app.state.whisper



