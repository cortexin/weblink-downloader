from fastapi import APIRouter, Form, Cookie
from starlette.responses import RedirectResponse
from starlette.requests import Request

from link_downloader.exceptions import UsernameExists
from link_downloader.services import auth
from .templates import templates

router = APIRouter()


@router.get('/register')
async def register_form(request: Request):
    return templates.TemplateResponse(
        'register.html', {'request': request}
    )


@router.get('/login')
async def login_form(request: Request):
    return templates.TemplateResponse(
        'login.html', {'request': request}
    )


@router.post('/register')
async def register(
        *,
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
):
    try:
        user_id = await auth.register(username, password)
    except UsernameExists as e:
        return templates.TemplateResponse(
            'register.html',
            {'request': request, 'error': str(e)}
        )

    response = RedirectResponse('/links', status_code=302)
    auth.log_user_in(user_id, response)
    return response


@router.post('/login')
async def login(
        *,
        username: str = Form(...),
        password: str = Form(...),
):
    user_id = await auth.login(username, password)
    if not user_id:
        return templates.TemplateResponse(
            'login.html',
            {'request': request, 'error': 'Invalid username or password'}
        )

    response = RedirectResponse('/links', status_code=302)
    auth.log_user_in(user_id, response)
    return response


@router.post('/logout')
async def logout(
        *,
        delete_user: bool = Form(...),
        fastapi_auth: str = Cookie(''),
):
    response = RedirectResponse('/auth/login', status_code=302)
    await auth.logout(
        fastapi_auth,
        response=response,
        delete_user=delete_user,
    )
    return response
