from flask_login import UserMixin
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import func
from typing import Optional

from cotacol.extensions import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))
    date_joined = db.Column(db.DateTime(timezone=True), default=func.now())
    extra_data = db.Column(db.JSON)

    social_accounts = db.relationship("SocialAccount", back_populates="user", lazy="joined")

    def __str__(self) -> str:
        return self.username

    @property
    def name(self) -> str:
        athlete = self.social_accounts[0].extra_data["athlete"]
        return f'{athlete["firstname"]} {athlete["lastname"]}'

    @property
    def profile_picture(self) -> str:
        return self.social_accounts[0].extra_data["athlete"]["profile"]

    def is_active(self) -> bool:
        return True

    def as_dict(self) -> dict:
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return d


class SocialAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    provider = db.Column(db.String(32))
    uid = db.Column(db.String(191))
    extra_data = db.Column(db.JSON)
    last_login = db.Column(db.DateTime(timezone=True), default=func.now())

    user = db.relationship("User", back_populates="social_accounts")


def user_from_token(token: dict, provider: str = "strava") -> Optional[User]:
    if provider == "strava":
        uid, username = str(token["athlete"]["id"]), str(token["athlete"]["username"])
    else:
        return None

    try:
        account = SocialAccount.query.filter(SocialAccount.provider == provider, SocialAccount.uid == uid).one()
        account.last_login = func.now()
        account.user.username = username
    except NoResultFound:
        account = None
        db.session.add(
            SocialAccount(
                user=User(username=username), provider=provider, uid=uid, extra_data=token, last_login=func.now(),
            )
        )

    db.session.flush()
    db.session.commit()

    if not account:
        account = SocialAccount.query.filter(SocialAccount.provider == provider, SocialAccount.uid == uid).one()

    return account.user
