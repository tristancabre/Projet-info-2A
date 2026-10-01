from pydantic import BaseModel


class ConnectionRequest(BaseModel):
    username: str
    password: str


class ConnectionResponse(BaseModel):
    id_user: int
    username: str
    email: str
    is_admin: bool  # display only (Streamlit), never used to secure anything
    access_token: str
    token_type: str = "bearer"
