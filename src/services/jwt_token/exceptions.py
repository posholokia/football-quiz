class TokenTypeUndefined(Exception):
    pass


class InvalidTokenType(Exception):
    pass


class DecodeJWTError(Exception):
    pass


class TokenInBlacklistError(Exception):
    pass
