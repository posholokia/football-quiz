from pydantic import BaseModel


class AuthCredentialsSchema(BaseModel):
    username: str
    password: str


class AccessTokenSchema(BaseModel):
    access: str


class RefreshTokenSchema(BaseModel):
    refresh: str


class TokenObtainPairSchemaSchema(AccessTokenSchema, RefreshTokenSchema):
    pass
