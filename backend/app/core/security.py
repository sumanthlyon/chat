import bcrypt

#hashing the password
def hash_password(password: str):

    password_bytes = password.encode("utf-8")

    salt = bcrypt.gensalt()

    hashed_password = bcrypt.hashpw(
        password_bytes,
        salt
    )

    return hashed_password.decode("utf-8")


#veriying the password
def verify_password(
        plain_password: str,
        hashed_password: str
):

    password_bytes = plain_password.encode("utf-8")

    hashed_bytes = hashed_password.encode("utf-8")

    return bcrypt.checkpw(
        password_bytes,
        hashed_bytes
    )