import pytest

from link_downloader.config import AUTH_COOKIE_TTL
from link_downloader.services import auth

from tests.utils import future


def test_log_user_in(mocker):
    # arrange
    m_encode_signature = mocker.patch.object(auth, '_encode_signature', return_value='encoded')
    m_make_signature = mocker.patch.object(auth, '_make_signature', return_value='signature')
    m_response = mocker.Mock()
    m_response.set_cookie = mocker.Mock()

    # act
    auth.log_user_in(user_id=10, response=m_response)

    # assert
    m_response.set_cookie.assert_called_once_with(
        key='fastapi_auth',
        value='10:encoded',
        httponly=True,
        expires=AUTH_COOKIE_TTL,
    )


@pytest.mark.parametrize('cookie', ['random', 'random:hash'])
def test_get_user_id_from_cookie__cookie_malformed__returns_none(cookie):
    # act
    result = auth.get_user_id_from_cookie(cookie)

    # assert
    assert result is None


def test_get_user_id_from_cookie__signature_valid__returns_user_id(mocker):
    # arrange
    m_make_signature = mocker.patch.object(auth, '_make_signature', return_value='signature')
    m_decode_signature = mocker.patch.object(auth, '_decode_signature', return_value='decoded')
    m_compare_digest = mocker.patch.object(auth.hmac, 'compare_digest', return_value=True)

    # act
    result = auth.get_user_id_from_cookie('10:hashed-signature')

    # assert
    assert result == 10
    m_make_signature.assert_called_once_with('10')
    m_compare_digest.assert_called_once_with('signature', 'decoded')


@pytest.mark.asyncio
async def test_logout__delete_user__deletes_user_and_logs_out(mocker):
    # arrange
    m_get_user = mocker.patch.object(auth, 'get_user_id_from_cookie', return_value=1)
    m_delete_user = mocker.patch.object(auth, '_delete_user', return_value=future())
    m_response = mocker.Mock()
    m_response.delete_cookie = mocker.Mock()

    # act
    await auth.logout(cookie='test', response=m_response, delete_user=True)

    # assert
    m_get_user.assert_called_once_with('test')
    m_delete_user.assert_called_once_with(1)
    m_response.delete_cookie.assert_called_once_with('fastapi_auth')
