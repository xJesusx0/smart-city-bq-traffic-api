import bcrypt

def encrypt(data: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(data.encode("utf-8"), salt).decode("utf-8")

def verify(raw: str, encrypted: str) -> bool:
    return bcrypt.checkpw(raw.encode('utf-8'), encrypted.encode('utf-8'))