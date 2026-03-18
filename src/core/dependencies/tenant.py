from fastapi import Header

def get_tenant_id(x_tenant_id: str = Header(...)):
    return x_tenant_id
