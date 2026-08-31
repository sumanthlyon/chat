from sqlalchemy.orm import Session

from app.database.models import User
from app.core.security import hash_password, verify_password




def create_user(
        db: Session,
        username,
        email,
        password
):

#hasing the password
    hashed_password = hash_password(password)

#builds an ORM object mapping to a row in the users table
    user = User(
        username=username,
        email=email,
        password_hash=hashed_password
    )

#adding user to database
    db.add(user)

    db.commit()

    db.refresh(user)


    return user


#authenticating the user
def authenticate_user(
        db: Session,
        email,
        password
):

    user = db.query(User).filter(
        User.email == email
    ).first()


    if not user:
        return None


    if not verify_password(
        password,
        user.password_hash
    ):
        return None


    return user