from socket import gaierror

import httpx
from httpx.exceptions import NetworkError, ConnectTimeout, HTTPError

from link_downloader.exceptions import UrlInvalid


async def validate_url(url: str) -> None:
    '''
    Probe the url with a HEAD request.
    Raise an error if resource is unavailable or response status is not OK.
    '''
    async with httpx.AsyncClient() as client:
        try:
            res = await client.head(url)
            res.raise_for_status()
        except (NetworkError, ConnectTimeout, HTTPError, gaierror):
            raise UrlInvalid
