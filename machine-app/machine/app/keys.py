import logging
from fastapi import status
import jwt
from datetime import datetime
from app.routers.router_utils import raise_and_log_error

logger = logging.getLogger(__name__)

public_key = None


class RsaKeys(object):

    @staticmethod
    def publish_public_key():
        logger.debug("TO DO PUBLISH PUBLIC KEY")

    @staticmethod
    def get_public_key():
        return public_key

    @staticmethod
    def set_public_key(new_public_key):
        global public_key
        public_key = new_public_key

    @staticmethod
    def verify_jwt(token):
        try:
            payload = jwt.decode(token, public_key, algorithms='RS256')
            if payload['exp'] < datetime.timestamp(datetime.utcnow()):
                raise_and_log_error(logger, status.HTTP_403_FORBIDDEN, "JWT Token expired")
        except jwt.exceptions.ExpiredSignatureError as exc:
            raise_and_log_error(logger, status.HTTP_403_FORBIDDEN, f"JWT Token expired: {exc}")
        except jwt.exceptions.InvalidSignatureError as exc:
            raise_and_log_error(logger, status.HTTP_401_UNAUTHORIZED, f"JWT signature verification failed: {exc}")
        except Exception as e:
            raise_and_log_error(logger, status.HTTP_401_UNAUTHORIZED, f"JWT error: {e}")

    @staticmethod
    def verify_admin_jwt(token):

        try:
            payload = jwt.decode(token, public_key, algorithms='RS256')
            if payload['exp'] < datetime.timestamp(datetime.utcnow()):
                raise_and_log_error(logger, status.HTTP_403_FORBIDDEN, "JWT Token expired")

            if 1 not in payload['roles']:
                raise_and_log_error(logger, status.HTTP_401_UNAUTHORIZED, "JWT signature verification failed")

        except jwt.exceptions.ExpiredSignatureError as exc:
            raise_and_log_error(logger, status.HTTP_403_FORBIDDEN, f"JWT Token expired {exc}")
        except jwt.exceptions.InvalidSignatureError as exc:
            raise_and_log_error(logger, status.HTTP_401_UNAUTHORIZED, f"JWT signature verification failed {exc}")
        except Exception as e:
            raise_and_log_error(logger, status.HTTP_401_UNAUTHORIZED, f"JWT error {e}")


