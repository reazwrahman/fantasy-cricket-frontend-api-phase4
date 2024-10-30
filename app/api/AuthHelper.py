import datetime
import decouple
import jwt
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature,
    BadTimeSignature,
)


class AuthHelper(object):
    def __init__(self):
        self.secret_key = decouple.config("SECRET_KEY")

    def decode_confirmation_token(self, token: str) -> str:
        secret_key = self.secret_key
        expiration = 3600
        s = Serializer(secret_key, expiration)
        data = s.loads(token)
        return data["confirm"]

    def generate_jwt(self, email: str) -> str:
        token = jwt.encode(
            {
                "sub": email,  # Subject of the token (user's email)
                "iat": datetime.datetime.now(datetime.timezone.utc),  # Issued at time
                "exp": datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(hours=1),  # Token expiration time (1 hour)
            },
            self.secret_key,
            algorithm="HS256",
        )
        return token

    def decode_jwt(self, token: str) -> str:
        """returns decoded email"""
        try:
            data = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            decoded_email = data["sub"]
            return data["sub"]
        except:  ## invalid jwt
            return None

    def validate_jwt(self, token: str, user_email: str) -> bool:
        decoded_email = self.decode_jwt(token)
        return decoded_email is not None and decoded_email == user_email
