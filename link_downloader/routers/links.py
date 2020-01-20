import tempfile

from fastapi import APIRouter, Cookie, Form, HTTPException
from starlette.requests import Request
from starlette.responses import FileResponse, RedirectResponse

from link_downloader.exceptions import UrlInvalid
from link_downloader.models import database, links
from link_downloader.services import auth, download_links
from link_downloader.services.links import get_links_for_user
from link_downloader.validation import validate_url
from .templates import templates

router = APIRouter()


@router.get('/')
async def list_links(request: Request, fastapi_auth: str = Cookie('')):
    user_id = auth.get_user_id_from_cookie(fastapi_auth)
    if not user_id:
        raise HTTPException(status_code=401, detail='Unauthorized')

    link_list = await get_links_for_user(user_id)

    return templates.TemplateResponse(
        'links.html',
        {'request': request, 'links': link_list}
    )


@router.post('/create')
async def create_link(
        *,
        request: Request,
        url: str = Form(...),
        fastapi_auth: str = Cookie(''),
):
    user_id = auth.get_user_id_from_cookie(fastapi_auth)
    if not user_id:
        raise HTTPException(status_code=401, detail='Unauthorized')

    try:
        await validate_url(url)
    except UrlInvalid as e:
        link_list = await get_links_for_user(user_id)
        return templates.TemplateResponse(
            'links.html',
            {
                'request': request,
                'url': url,
                'error': e.__doc__,
                'links': link_list,
            }
        )

    query = links.insert().values(url=url, user_id=user_id)
    await database.execute(query)
    return RedirectResponse('/links', status_code=302)


@router.post('/{link_id}/delete')
async def delete_link(link_id: int, fastapi_auth: str = Cookie('')):
    user_id = auth.get_user_id_from_cookie(fastapi_auth)
    if not user_id:
        raise HTTPException(status_code=401, detail='Unauthorized')

    query = links.delete().where(
        (links.c.id == link_id) &
        (links.c.user_id == user_id)
    )
    await database.execute(query)
    return RedirectResponse('/links', status_code=302)


@router.get('/download')
async def download_files():
    query = links.select().column(links.c.url)
    urls = [
        rec['url'] for rec in await database.fetch_all(query)
    ]
    archived_files = await download_links.main(urls)

    # TODO: figure out a way to stream ZIP on the fly without waiting
    # for all urls to be downloaded and archived
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as f:
        f.write(archived_files.getvalue())
        return FileResponse(f.name, media_type='application/zip')
