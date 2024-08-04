from pydantic import BaseModel


class AuthCredentialsSchema(BaseModel):
    username: str
    password: str


class AccessTokenSchema(BaseModel):
    access: str


class TokenObtainPairSchema(AccessTokenSchema):
    refresh: str
