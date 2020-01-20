import asyncio
import cgi
import io
from typing import Dict, List, Optional
from zipfile import ZipFile

import httpx
from httpx.exceptions import ConnectTimeout, NetworkError, HTTPError


async def main(urls: List[str]):
    buffer = io.BytesIO()

    with ZipFile(buffer, 'a') as f:
        async for filename, content in download_files(urls):
            f.writestr(filename, content)
    return buffer


async def download_files(urls: List[str]):
    async with httpx.AsyncClient(timeout=10) as client:
        futures = [
            client.get(url)
            for url in urls
        ]

        for future in asyncio.as_completed(futures):
            try:
                response = await future
                response.raise_for_status()
            except (NetworkError, ConnectTimeout, HTTPError):
                continue  # TODO: return an error message to the client

            filename = get_filename(response)
            yield (filename, response.content)


def get_filename(response) -> str:
    return (
        get_filename_from_headers(response.headers) or
        get_filename_from_url(response.url) or
        f'file_from_{response.url}'
    )


def get_filename_from_headers(headers: Dict[str, str]) -> Optional[str]:
    disposition = headers.get('Content-Disposition')

    if disposition:
        value, params = cgi.parse_header(disposition)
        return (value == 'attachment') and params.get('file')


def get_filename_from_url(url: httpx.URL) -> str:
    return url.path.split('/')[-1]
