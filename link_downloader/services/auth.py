import base64
import hmac
from hashlib import sha256
from typing import Optional

from asyncpg.exceptions import UniqueViolationError
from passlib.hash import sha256_crypt
from starlette.responses import Response

from link_downloader.models import users, database
from link_downloader.config import APP_SECRET, AUTH_COOKIE_TTL
from link_downloader.exceptions import UsernameExists


async def register(username: str, password: str) -> int:
    hashed_password = sha256_crypt.encrypt(password)
    query = users.insert().values(
        username=username,
        password=hashed_password,
    )
    try:
        return await database.execute(query)
    except UniqueViolationError:
        raise UsernameExists


async def login(username: str, password: str) -> Optional[int]:
    query = users.select(users.c.username == username)

    user = await database.fetch_one(query)

    if user:
        passwords_match = sha256_crypt.verify(password, user['password'])
        return passwords_match and user['id']


def log_user_in(user_id: int, response: Response) -> None:
    signature = _encode_signature(_make_signature(user_id))

    cookie = ':'.join((str(user_id), signature))

    response.set_cookie(
        key='fastapi_auth',
        value=cookie,
        httponly=True,
        expires=AUTH_COOKIE_TTL
    )


def get_user_id_from_cookie(cookie: str) -> Optional[int]:
    values = cookie.split(':')
    if len(values) != 2:
        return

    user_id, request_signature = values

    true_signature = _make_signature(user_id)

    if hmac.compare_digest(
            true_signature,
            _decode_signature(request_signature)
    ):
        return int(user_id)


async def logout(
        cookie: str,
        response: Response,
        delete_user: Optional[bool] = False
) -> None:
    user_id = get_user_id_from_cookie(cookie)
    if not user_id:
        return

    if delete_user:
        await _delete_user(user_id)

    response.delete_cookie('fastapi_auth')


async def _delete_user(user_id: int) -> None:
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)


def _make_signature(msg) -> str:
    return hmac.new(APP_SECRET.encode(), str(msg).encode(), sha256).digest()


def _encode_signature(sign: bytes) -> str:
    return base64.urlsafe_b64encode(sign).decode()


def _decode_signature(digest: str) -> bytes:
    return base64.urlsafe_b64decode(digest.encode())
