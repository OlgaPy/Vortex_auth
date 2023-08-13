from hashlib import md5


def password_hash(password: str | bytes, solt: str | bytes | None) -> str:
    if isinstance(password, str):
        password = password.encode("utf-8")

    if isinstance(solt, str):
        solt = solt.encode("utf-8")

    pass_hash = md5(solt + password).hexdigest()
    return pass_hash
