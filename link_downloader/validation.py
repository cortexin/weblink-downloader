import httpx
from httpx.exceptions import NetworkError, ConnectTimeout
from link_downloader.exceptions import UrlInvalid


async def validate_url(url: str) -> None:
    '''
    Probe the url with a HEAD request.
    Raise an error if resource is unavailable or response status is not OK.
    '''
    async with httpx.AsyncClient() as client:
        try:
            res = await client.head(url)
        except (NetworkError, ConnectTimeout):
            raise UrlInvalid

        if res.status_code != 200:
            raise UrlInvalid
