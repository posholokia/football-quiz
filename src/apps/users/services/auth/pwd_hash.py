import bcrypt


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    pwd_hash = bcrypt.hashpw(password.encode(), salt)
    return pwd_hash.decode()


def check_password(password: str, hashed_password: str) -> bool:
    b_password: bytes = password.encode()
    b_hashed_password: bytes = hashed_password.encode()
    return bcrypt.checkpw(b_password, b_hashed_password)


p = "g+d7HsQJVzJhiE2rZDys+pBGvt51bYaloQRZZRxo5Bo"

print(hash_password(p))
